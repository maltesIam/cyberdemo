"""
NVD (National Vulnerability Database) API 2.0 Client.

Rate limits:
- Without API key: 5 requests per 30 seconds
- With API key: 50 requests per 30 seconds

API Documentation: https://nvd.nist.gov/developers/vulnerabilities
"""

import asyncio
import logging
import time
from typing import Any, Optional, Dict, List
from datetime import datetime

import httpx


logger = logging.getLogger(__name__)

# Constants
NVD_API_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
MAX_ITEMS_PER_SOURCE = 100
DEFAULT_TIMEOUT = 30  # seconds

# Rate limiting constants
RATE_LIMIT_WITHOUT_KEY = 5  # requests per 30 seconds
RATE_LIMIT_WITH_KEY = 50  # requests per 30 seconds
RATE_LIMIT_WINDOW = 30  # seconds


class NVDRateLimitError(Exception):
    """Raised when NVD API rate limit is exceeded."""
    pass


class NVDTimeoutError(Exception):
    """Raised when NVD API request times out."""
    pass


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: List[float] = []

    async def acquire(self):
        """Wait until we can make a request within rate limit."""
        current_time = time.time()

        # Remove old requests outside the window
        self.requests = [
            req_time for req_time in self.requests
            if current_time - req_time < self.window_seconds
        ]

        # If we're at the limit, wait
        if len(self.requests) >= self.max_requests:
            oldest_request = min(self.requests)
            wait_time = self.window_seconds - (current_time - oldest_request)
            if wait_time > 0:
                logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                # Retry acquire after waiting
                return await self.acquire()

        # Record this request
        self.requests.append(current_time)


class NVDClient:
    """
    Client for NVD API 2.0.

    Handles rate limiting, timeouts, and error recovery gracefully.
    Returns None on errors instead of raising exceptions to prevent
    blocking the entire enrichment process.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT
    ):
        self.api_key = api_key
        self.timeout = timeout

        # Set up rate limiter based on API key availability
        max_requests = RATE_LIMIT_WITH_KEY if api_key else RATE_LIMIT_WITHOUT_KEY
        self.rate_limiter = RateLimiter(max_requests, RATE_LIMIT_WINDOW)

        # HTTP client
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def fetch_cve(self, cve_id: str) -> Optional[Dict]:
        """
        Fetch CVE data from NVD API.

        Returns:
            Dict with CVE data on success, None on failure.
            Dict structure:
            {
                "cve_id": str,
                "cvss_v3_score": float | None,
                "cvss_v3_vector": str | None,
                "cvss_v2_score": float | None,
                "cwe_ids": List[str],
                "cpe_uris": List[str],
                "references": List[Dict],
                "description": str,
                "published_date": str,
                "last_modified_date": str
            }
        """
        await self.rate_limiter.acquire()

        headers = {}
        if self.api_key:
            headers["apiKey"] = self.api_key

        url = f"{NVD_API_BASE_URL}"
        params = {"cveId": cve_id}

        try:
            response = await self.client.get(url, params=params, headers=headers)

            # Handle rate limiting
            if response.status_code == 429:
                logger.warning(f"Rate limit exceeded for CVE {cve_id}")
                return None

            # Handle other HTTP errors
            if response.status_code != 200:
                logger.error(f"NVD API error for {cve_id}: {response.status_code}")
                return None

            data = response.json()

            # Parse response
            return self._parse_cve_response(data, cve_id)

        except TimeoutError:
            logger.error(f"Timeout fetching CVE {cve_id} from NVD")
            return None

        except httpx.TimeoutException:
            logger.error(f"HTTP timeout fetching CVE {cve_id} from NVD")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching CVE {cve_id}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching CVE {cve_id}: {e}")
            return None

    def _parse_cve_response(self, data: Dict, cve_id: str) -> Optional[Dict]:
        """
        Parse NVD API response into our internal format.

        Handles malformed responses gracefully.
        """
        try:
            vulnerabilities = data.get("vulnerabilities", [])

            if not vulnerabilities:
                logger.warning(f"No vulnerability data found for {cve_id}")
                return None

            cve_data = vulnerabilities[0].get("cve", {})

            if not cve_data:
                logger.warning(f"Malformed response for {cve_id}")
                return None

            # Extract CVSS scores
            metrics = cve_data.get("metrics", {})
            cvss_v3_data = (
                metrics.get("cvssMetricV31", [{}])[0] if "cvssMetricV31" in metrics
                else metrics.get("cvssMetricV30", [{}])[0] if "cvssMetricV30" in metrics
                else {}
            )
            cvss_v2_data = metrics.get("cvssMetricV2", [{}])[0] if "cvssMetricV2" in metrics else {}

            cvss_v3 = cvss_v3_data.get("cvssData", {})
            cvss_v2 = cvss_v2_data.get("cvssData", {})

            # Extract CWE IDs
            weaknesses = cve_data.get("weaknesses", [])
            cwe_ids = []
            for weakness in weaknesses:
                descriptions = weakness.get("description", [])
                for desc in descriptions:
                    cwe_id = desc.get("value", "")
                    if cwe_id.startswith("CWE-"):
                        cwe_ids.append(cwe_id)

            # Extract CPE URIs
            configurations = cve_data.get("configurations", [])
            cpe_uris = []
            for config in configurations:
                nodes = config.get("nodes", [])
                for node in nodes:
                    cpe_matches = node.get("cpeMatch", [])
                    for match in cpe_matches:
                        cpe_uri = match.get("criteria", "")
                        if cpe_uri:
                            cpe_uris.append(cpe_uri)

            # Extract references
            references = []
            for ref in cve_data.get("references", []):
                references.append({
                    "url": ref.get("url", ""),
                    "source": ref.get("source", ""),
                    "tags": ref.get("tags", [])
                })

            # Extract descriptions
            descriptions = cve_data.get("descriptions", [])
            description = ""
            for desc in descriptions:
                if desc.get("lang") == "en":
                    description = desc.get("value", "")
                    break

            # Dates
            published_date = cve_data.get("published", "")
            last_modified_date = cve_data.get("lastModified", "")

            return {
                "cve_id": cve_id,
                "cvss_v3_score": cvss_v3.get("baseScore"),
                "cvss_v3_vector": cvss_v3.get("vectorString"),
                "cvss_v2_score": cvss_v2.get("baseScore"),
                "cwe_ids": cwe_ids,
                "cpe_uris": cpe_uris,
                "references": references,
                "description": description,
                "published_date": published_date,
                "last_modified_date": last_modified_date
            }

        except Exception as e:
            logger.error(f"Error parsing CVE response for {cve_id}: {e}")
            return None

    async def fetch_cves(self, cve_ids: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Fetch multiple CVEs from NVD API.

        Respects MAX_ITEMS_PER_SOURCE limit (100).

        Returns:
            Dict mapping CVE ID to data (or None if fetch failed)
        """
        # Limit to MAX_ITEMS_PER_SOURCE
        if len(cve_ids) > MAX_ITEMS_PER_SOURCE:
            logger.warning(
                f"Limiting CVE fetch from {len(cve_ids)} to {MAX_ITEMS_PER_SOURCE}"
            )
            cve_ids = cve_ids[:MAX_ITEMS_PER_SOURCE]

        results = {}

        # Fetch sequentially to respect rate limits
        for cve_id in cve_ids:
            result = await self.fetch_cve(cve_id)
            results[cve_id] = result

        return results

    async def enrich(self, cve_ids: List[str]) -> Dict[str, Any]:
        """
        Enrich multiple CVEs and return standard result format.

        Returns:
            {"count": int, "failed": int, "processed": List[str]}
        """
        results = await self.fetch_cves(cve_ids)
        processed = [cve_id for cve_id, data in results.items() if data is not None]
        failed = len(results) - len(processed)
        return {
            "count": len(processed),
            "failed": failed,
            "processed": processed,
        }
