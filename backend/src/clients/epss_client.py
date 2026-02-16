"""
EPSS (Exploit Prediction Scoring System) API Client.

EPSS provides probability scores indicating the likelihood that a CVE
will be exploited in the wild.

API Documentation: https://www.first.org/epss/api
No rate limits or API key required.
"""

import logging
from typing import Any, Optional, Dict, List

import httpx


logger = logging.getLogger(__name__)

# Constants
EPSS_API_BASE_URL = "https://api.first.org/data/v1/epss"
MAX_ITEMS_PER_SOURCE = 100
DEFAULT_TIMEOUT = 30  # seconds


class EPSSClient:
    """
    Client for EPSS API.

    Returns exploit prediction scores for CVEs.
    No rate limiting required (free tier has no limits).
    """

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def fetch_score(self, cve_id: str) -> Optional[Dict]:
        """
        Fetch EPSS score for a single CVE.

        Returns:
            Dict with EPSS data on success, None on failure.
            Dict structure:
            {
                "cve_id": str,
                "epss_score": float,  # 0.0 to 1.0
                "epss_percentile": float  # 0.0 to 1.0
            }
        """
        url = f"{EPSS_API_BASE_URL}"
        params = {"cve": cve_id}

        try:
            response = await self.client.get(url, params=params)

            if response.status_code != 200:
                logger.error(f"EPSS API error for {cve_id}: {response.status_code}")
                return None

            data = response.json()

            # Parse response
            return self._parse_epss_response(data, cve_id)

        except TimeoutError:
            logger.error(f"Timeout fetching EPSS score for {cve_id}")
            return None

        except httpx.TimeoutException:
            logger.error(f"HTTP timeout fetching EPSS score for {cve_id}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching EPSS score for {cve_id}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching EPSS score for {cve_id}: {e}")
            return None

    def _parse_epss_response(self, data: Dict, cve_id: str) -> Optional[Dict]:
        """
        Parse EPSS API response.

        Handles malformed responses gracefully.
        """
        try:
            # EPSS API returns data in format:
            # {
            #   "status": "OK",
            #   "data": [
            #     {
            #       "cve": "CVE-2024-0001",
            #       "epss": "0.00123",
            #       "percentile": "0.45678"
            #     }
            #   ]
            # }

            epss_data_list = data.get("data", [])

            if not epss_data_list:
                logger.warning(f"No EPSS data found for {cve_id}")
                return None

            epss_data = epss_data_list[0]

            epss_score = float(epss_data.get("epss", 0.0))
            epss_percentile = float(epss_data.get("percentile", 0.0))

            return {
                "cve_id": cve_id,
                "epss_score": epss_score,
                "epss_percentile": epss_percentile
            }

        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing EPSS response for {cve_id}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error parsing EPSS response for {cve_id}: {e}")
            return None

    async def fetch_scores(self, cve_ids: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Fetch EPSS scores for multiple CVEs.

        Respects MAX_ITEMS_PER_SOURCE limit (100).

        EPSS API supports batch queries with comma-separated CVE IDs,
        but we'll implement sequential fetching for consistency with other clients.

        Returns:
            Dict mapping CVE ID to EPSS data (or None if fetch failed)
        """
        # Limit to MAX_ITEMS_PER_SOURCE
        if len(cve_ids) > MAX_ITEMS_PER_SOURCE:
            logger.warning(
                f"Limiting EPSS fetch from {len(cve_ids)} to {MAX_ITEMS_PER_SOURCE}"
            )
            cve_ids = cve_ids[:MAX_ITEMS_PER_SOURCE]

        results = {}

        # Fetch sequentially
        for cve_id in cve_ids:
            result = await self.fetch_score(cve_id)
            results[cve_id] = result

        return results

    async def enrich(self, cve_ids: List[str]) -> Dict[str, Any]:
        """
        Enrich multiple CVEs with EPSS scores and return standard result format.

        Returns:
            {"count": int, "failed": int, "processed": List[str]}
        """
        results = await self.fetch_scores(cve_ids)
        processed = [cve_id for cve_id, data in results.items() if data is not None]
        failed = len(results) - len(processed)
        return {
            "count": len(processed),
            "failed": failed,
            "processed": processed,
        }
