"""
GreyNoise API Client.

GreyNoise classifies IPs as benign, malicious, or unknown based on
internet-wide scanning and activity data.

API Documentation: https://docs.greynoise.io/
Community tier: Limited free access
"""

import logging
from typing import Optional, Dict

import httpx


logger = logging.getLogger(__name__)

# Constants
GREYNOISE_API_BASE_URL = "https://api.greynoise.io/v3"
GREYNOISE_COMMUNITY_URL = "https://api.greynoise.io/v3/community"
MAX_ITEMS_PER_SOURCE = 100
DEFAULT_TIMEOUT = 30  # seconds


class GreyNoiseClient:
    """
    Client for GreyNoise API.

    Classifies IPs and provides tags for benign vs malicious activity.
    """

    def __init__(self, api_key: str, timeout: int = DEFAULT_TIMEOUT):
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def fetch_ip_classification(self, ip: str) -> Optional[Dict]:
        """
        Fetch IP classification from GreyNoise.

        Returns:
            Dict with IP classification data on success, None on failure.
            Dict structure:
            {
                "indicator_value": str,
                "indicator_type": "ip",
                "classification": str,  # "benign" | "malicious" | "unknown"
                "tags": List[str],
                "first_seen": str,
                "last_seen": str
            }
        """
        # Try community endpoint first (free tier)
        url = f"{GREYNOISE_COMMUNITY_URL}/{ip}"
        headers = {"key": self.api_key}

        try:
            response = await self.client.get(url, headers=headers)

            # Handle rate limiting
            if response.status_code == 429:
                logger.warning(f"GreyNoise rate limit exceeded for IP {ip}")
                return None

            # Handle auth errors
            if response.status_code == 401:
                logger.error("GreyNoise API authentication failed")
                return None

            # Handle not found (unknown IP)
            if response.status_code == 404:
                return {
                    "indicator_value": ip,
                    "indicator_type": "ip",
                    "classification": "unknown",
                    "tags": [],
                    "first_seen": None,
                    "last_seen": None
                }

            if response.status_code != 200:
                logger.error(f"GreyNoise API error for IP {ip}: {response.status_code}")
                return None

            data = response.json()

            return self._parse_response(data, ip)

        except TimeoutError:
            logger.error(f"Timeout fetching GreyNoise data for IP {ip}")
            return None

        except httpx.TimeoutException:
            logger.error(f"HTTP timeout fetching GreyNoise data for IP {ip}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching GreyNoise data for IP {ip}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching GreyNoise data for IP {ip}: {e}")
            return None

    def _parse_response(self, data: Dict, ip: str) -> Optional[Dict]:
        """Parse GreyNoise response into internal format."""
        try:
            # GreyNoise Community API response structure:
            # {
            #   "ip": "1.2.3.4",
            #   "noise": true,
            #   "riot": false,
            #   "classification": "malicious",
            #   "name": "VPN Proxy",
            #   "link": "https://viz.greynoise.io/ip/1.2.3.4",
            #   "last_seen": "2024-02-13",
            #   "message": "Success"
            # }

            if not data:
                logger.warning(f"Empty response for IP {ip}")
                return None

            # Determine classification
            classification = data.get("classification", "unknown")

            # If "riot" flag is true, it's benign (known good actors)
            if data.get("riot", False):
                classification = "benign"
            # If "noise" flag is true but not riot, it's likely malicious
            elif data.get("noise", False):
                if classification not in ["benign", "malicious"]:
                    classification = "malicious"

            # Extract tags
            tags = []
            if data.get("name"):
                tags.append(data.get("name"))

            return {
                "indicator_value": ip,
                "indicator_type": "ip",
                "classification": classification,
                "tags": tags,
                "first_seen": None,  # Community API doesn't provide this
                "last_seen": data.get("last_seen")
            }

        except Exception as e:
            logger.error(f"Error parsing GreyNoise response for IP {ip}: {e}")
            return None

    async def fetch_ips(self, ips: list[str]) -> Dict[str, Optional[Dict]]:
        """
        Fetch classification for multiple IPs.

        Respects MAX_ITEMS_PER_SOURCE limit (100).

        Returns:
            Dict mapping IP to classification data (or None if fetch failed)
        """
        # Limit to MAX_ITEMS_PER_SOURCE
        if len(ips) > MAX_ITEMS_PER_SOURCE:
            logger.warning(
                f"Limiting GreyNoise fetch from {len(ips)} to {MAX_ITEMS_PER_SOURCE}"
            )
            ips = ips[:MAX_ITEMS_PER_SOURCE]

        results = {}

        # Fetch sequentially to respect rate limits
        for ip in ips:
            result = await self.fetch_ip_classification(ip)
            results[ip] = result

        return results
