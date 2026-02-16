"""
Cloudflare Radar API Client.

Cloudflare Radar provides internet traffic insights, domain rankings, and traffic anomalies.

API Documentation: https://developers.cloudflare.com/radar/
Rate limit: Requires API Token (Bearer authentication)
"""

import logging
from typing import Optional, Dict

import httpx


logger = logging.getLogger(__name__)

# Constants
CLOUDFLARE_RADAR_BASE_URL = "https://api.cloudflare.com/client/v4/radar"
DEFAULT_TIMEOUT = 30  # seconds


class CloudflareRadarClient:
    """
    Client for Cloudflare Radar API.

    Provides domain rankings, traffic anomalies, and DNS statistics.
    """

    def __init__(self, api_token: Optional[str], timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize Cloudflare Radar client.

        Args:
            api_token: API token for authentication (required).
            timeout: Request timeout in seconds.

        Raises:
            ValueError: If api_token is None or empty.
        """
        if not api_token:
            raise ValueError("API token is required for Cloudflare Radar API")

        self.api_token = api_token
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def get_domain_ranking(self, domain: str) -> Optional[Dict]:
        """
        Fetch domain ranking from Cloudflare Radar.

        Args:
            domain: The domain to look up (e.g., "google.com").

        Returns:
            Dict with domain ranking data on success, None on failure.
            Dict structure:
            {
                "rank": int,
                "domain": str,
                "categories": list,
                "bucket": str
            }
        """
        url = f"{CLOUDFLARE_RADAR_BASE_URL}/ranking/domain/{domain}"

        try:
            response = await self.client.get(url, headers=self._get_headers())

            # Handle rate limiting
            if response.status_code == 429:
                logger.warning(f"Cloudflare Radar rate limit exceeded for domain {domain}")
                return None

            # Handle other errors
            if response.status_code != 200:
                logger.error(f"Cloudflare Radar API error for domain {domain}: {response.status_code}")
                return None

            data = response.json()

            # Check for API success
            if not data.get("success", False):
                errors = data.get("errors", [])
                logger.error(f"Cloudflare Radar API unsuccessful for domain {domain}: {errors}")
                return None

            return data.get("result")

        except httpx.TimeoutException:
            logger.error(f"HTTP timeout fetching Cloudflare Radar data for domain {domain}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching Cloudflare Radar data for domain {domain}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching Cloudflare Radar data for domain {domain}: {e}")
            return None

    async def get_traffic_anomalies(self, location: str) -> Optional[Dict]:
        """
        Fetch traffic anomalies for a location from Cloudflare Radar.

        Args:
            location: The location code (e.g., "US", "GB").

        Returns:
            Dict with traffic anomaly data on success, None on failure.
            Dict structure:
            {
                "anomalies": [
                    {
                        "location": str,
                        "timestamp": str,
                        "type": str,
                        "severity": str,
                        "description": str
                    }
                ]
            }
        """
        url = f"{CLOUDFLARE_RADAR_BASE_URL}/traffic_anomalies"
        params = {"location": location}

        try:
            response = await self.client.get(url, headers=self._get_headers(), params=params)

            # Handle rate limiting
            if response.status_code == 429:
                logger.warning(f"Cloudflare Radar rate limit exceeded for location {location}")
                return None

            # Handle other errors
            if response.status_code != 200:
                logger.error(f"Cloudflare Radar API error for location {location}: {response.status_code}")
                return None

            data = response.json()

            # Check for API success
            if not data.get("success", False):
                errors = data.get("errors", [])
                logger.error(f"Cloudflare Radar API unsuccessful for location {location}: {errors}")
                return None

            return data.get("result")

        except httpx.TimeoutException:
            logger.error(f"HTTP timeout fetching Cloudflare Radar anomalies for location {location}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching Cloudflare Radar anomalies for location {location}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching Cloudflare Radar anomalies for location {location}: {e}")
            return None

    async def get_dns_stats(self, domain: str) -> Optional[Dict]:
        """
        Fetch DNS query statistics for a domain from Cloudflare Radar.

        Args:
            domain: The domain to look up (e.g., "example.com").

        Returns:
            Dict with DNS statistics on success, None on failure.
            Dict structure:
            {
                "domain": str,
                "query_count": int,
                "response_time_avg_ms": float,
                "error_rate": float,
                "record_types": dict
            }
        """
        url = f"{CLOUDFLARE_RADAR_BASE_URL}/dns/summary"
        params = {"domain": domain}

        try:
            response = await self.client.get(url, headers=self._get_headers(), params=params)

            # Handle rate limiting
            if response.status_code == 429:
                logger.warning(f"Cloudflare Radar rate limit exceeded for DNS stats: {domain}")
                return None

            # Handle other errors
            if response.status_code != 200:
                logger.error(f"Cloudflare Radar API error for DNS stats: {domain}: {response.status_code}")
                return None

            data = response.json()

            # Check for API success
            if not data.get("success", False):
                errors = data.get("errors", [])
                logger.error(f"Cloudflare Radar API unsuccessful for DNS stats: {domain}: {errors}")
                return None

            return data.get("result")

        except httpx.TimeoutException:
            logger.error(f"HTTP timeout fetching Cloudflare Radar DNS stats for domain {domain}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching Cloudflare Radar DNS stats for domain {domain}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching Cloudflare Radar DNS stats for domain {domain}: {e}")
            return None
