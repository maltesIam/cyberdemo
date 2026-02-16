"""
VirusTotal API Client.

VirusTotal provides threat intelligence for files, URLs, domains, and IPs.

API Documentation: https://developers.virustotal.com/reference/overview
Rate limit: 500 requests/day (free tier), 4 requests/minute
"""

import base64
import logging
from typing import Optional, Dict, Literal

import httpx


logger = logging.getLogger(__name__)

# Constants
VIRUSTOTAL_API_BASE_URL = "https://www.virustotal.com/api/v3"
DEFAULT_TIMEOUT = 30  # seconds


class VirusTotalClient:
    """
    Client for VirusTotal API v3.

    Provides threat intelligence for files (hashes), URLs, domains, and IPs.
    Requires an API key for authentication.
    """

    def __init__(self, api_key: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize VirusTotal client.

        Args:
            api_key: VirusTotal API key (required).
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with API key."""
        return {
            "x-apikey": self.api_key,
            "Accept": "application/json"
        }

    async def _make_request(self, url: str) -> Optional[Dict]:
        """
        Make GET request to VirusTotal API.

        Args:
            url: Full URL to request.

        Returns:
            Dict with response data on success, None on failure.
        """
        try:
            response = await self.client.get(url, headers=self._get_headers())

            # Handle rate limiting (daily quota or per-minute)
            if response.status_code == 429:
                logger.warning(f"VirusTotal rate limit exceeded for {url}")
                return None

            # Handle authentication errors
            if response.status_code == 401:
                logger.error("VirusTotal API authentication failed - invalid API key")
                return None

            # Handle forbidden access
            if response.status_code == 403:
                logger.error("VirusTotal API access forbidden")
                return None

            # Handle not found
            if response.status_code == 404:
                logger.info(f"VirusTotal resource not found: {url}")
                return None

            # Handle server errors
            if response.status_code >= 500:
                logger.error(f"VirusTotal server error: {response.status_code}")
                return None

            if response.status_code != 200:
                logger.error(f"VirusTotal API error: {response.status_code}")
                return None

            data = response.json()

            # Validate response structure
            if "data" not in data:
                logger.warning(f"VirusTotal malformed response - missing 'data' key")
                return None

            return data["data"]

        except httpx.TimeoutException:
            logger.error(f"VirusTotal request timeout for {url}")
            return None

        except httpx.ConnectError as e:
            logger.error(f"VirusTotal connection error: {e}")
            return None

        except httpx.RequestError as e:
            logger.error(f"VirusTotal request error: {e}")
            return None

        except ValueError as e:
            logger.error(f"VirusTotal JSON parse error: {e}")
            return None

        except Exception as e:
            logger.error(f"VirusTotal unexpected error: {e}")
            return None

    async def check_ip(self, ip: str) -> Optional[Dict]:
        """
        Check an IP address for threat intelligence.

        Args:
            ip: IP address to check.

        Returns:
            Dict with IP analysis data on success, None on failure.
        """
        url = f"{VIRUSTOTAL_API_BASE_URL}/ip_addresses/{ip}"
        return await self._make_request(url)

    async def get_ip_report(self, ip: str) -> Optional[Dict]:
        """
        Get detailed IP report.

        Args:
            ip: IP address to get report for.

        Returns:
            Dict with detailed IP report on success, None on failure.
        """
        # Same endpoint, same data - this is an alias for consistency
        return await self.check_ip(ip)

    async def check_url(self, url_to_check: str) -> Optional[Dict]:
        """
        Check a URL for threat intelligence.

        Note: VirusTotal uses URL ID which is base64(url) without padding.

        Args:
            url_to_check: URL to check.

        Returns:
            Dict with URL analysis data on success, None on failure.
        """
        # VirusTotal URL ID is base64 encoded URL without padding
        url_id = base64.urlsafe_b64encode(url_to_check.encode()).decode().rstrip("=")
        url = f"{VIRUSTOTAL_API_BASE_URL}/urls/{url_id}"
        return await self._make_request(url)

    async def check_hash(self, file_hash: str) -> Optional[Dict]:
        """
        Check a file hash (MD5, SHA1, or SHA256) for threat intelligence.

        Args:
            file_hash: File hash to check (MD5, SHA1, or SHA256).

        Returns:
            Dict with file analysis data on success, None on failure.
        """
        url = f"{VIRUSTOTAL_API_BASE_URL}/files/{file_hash}"
        return await self._make_request(url)

    async def check_domain(self, domain: str) -> Optional[Dict]:
        """
        Check a domain for threat intelligence.

        Args:
            domain: Domain to check.

        Returns:
            Dict with domain analysis data on success, None on failure.
        """
        url = f"{VIRUSTOTAL_API_BASE_URL}/domains/{domain}"
        return await self._make_request(url)

    async def get_quota_status(self) -> Optional[Dict]:
        """
        Get current API quota status.

        Returns:
            Dict with quota information on success, None on failure.
        """
        url = f"{VIRUSTOTAL_API_BASE_URL}/users/me"
        result = await self._make_request(url)
        if result and "attributes" in result:
            return result["attributes"]
        return None

    async def get_enrichment_data(
        self,
        indicator_type: Literal["ip", "url", "hash", "domain"],
        indicator: str
    ) -> Optional[Dict]:
        """
        Get structured enrichment data for threat intelligence systems.

        Args:
            indicator_type: Type of indicator (ip, url, hash, domain).
            indicator: The indicator value to check.

        Returns:
            Dict with standardized enrichment data on success, None on failure.
            Structure:
            {
                "indicator": str,
                "indicator_type": str,
                "source": "virustotal",
                "malicious_count": int,
                "total_engines": int,
                "is_malicious": bool,
                "reputation": int,
                "country": str (for IPs),
                "threat_label": str (for files),
                "raw_data": dict
            }
        """
        # Fetch raw data based on indicator type
        if indicator_type == "ip":
            raw_data = await self.check_ip(indicator)
        elif indicator_type == "url":
            raw_data = await self.check_url(indicator)
        elif indicator_type == "hash":
            raw_data = await self.check_hash(indicator)
        elif indicator_type == "domain":
            raw_data = await self.check_domain(indicator)
        else:
            logger.error(f"Unknown indicator type: {indicator_type}")
            return None

        if raw_data is None:
            return None

        # Extract attributes safely
        attributes = raw_data.get("attributes", {})
        stats = attributes.get("last_analysis_stats", {})

        # Calculate totals
        malicious_count = stats.get("malicious", 0)
        suspicious_count = stats.get("suspicious", 0)
        harmless_count = stats.get("harmless", 0)
        undetected_count = stats.get("undetected", 0)
        timeout_count = stats.get("timeout", 0)

        total_engines = (
            malicious_count +
            suspicious_count +
            harmless_count +
            undetected_count +
            timeout_count
        )

        # Determine if malicious (threshold: any malicious detection)
        is_malicious = malicious_count > 0

        # Build enrichment response
        enrichment = {
            "indicator": indicator,
            "indicator_type": indicator_type,
            "source": "virustotal",
            "malicious_count": malicious_count,
            "suspicious_count": suspicious_count,
            "harmless_count": harmless_count,
            "total_engines": total_engines,
            "is_malicious": is_malicious,
            "reputation": attributes.get("reputation", 0),
            "raw_data": raw_data
        }

        # Add type-specific fields
        if indicator_type == "ip":
            enrichment["country"] = attributes.get("country")
            enrichment["as_owner"] = attributes.get("as_owner")
            enrichment["asn"] = attributes.get("asn")

        elif indicator_type == "hash":
            classification = attributes.get("popular_threat_classification", {})
            enrichment["threat_label"] = classification.get("suggested_threat_label")
            enrichment["file_name"] = attributes.get("meaningful_name")
            enrichment["file_type"] = attributes.get("type_description")

        elif indicator_type == "domain":
            enrichment["registrar"] = attributes.get("registrar")
            enrichment["categories"] = attributes.get("categories")

        elif indicator_type == "url":
            enrichment["final_url"] = attributes.get("last_final_url")
            enrichment["categories"] = attributes.get("categories")

        return enrichment
