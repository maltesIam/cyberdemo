"""
AbuseIPDB API Client.

AbuseIPDB provides IP reputation data including abuse confidence scores
and report counts.

API Documentation: https://www.abuseipdb.com/api.html
Rate limit: 1000 requests/day (free tier)
"""

import logging
from typing import Optional, Dict

import httpx


logger = logging.getLogger(__name__)

# Constants
ABUSEIPDB_API_BASE_URL = "https://api.abuseipdb.com/api/v2"
MAX_ITEMS_PER_SOURCE = 100
DEFAULT_TIMEOUT = 30  # seconds


class AbuseIPDBClient:
    """
    Client for AbuseIPDB API.

    Provides IP abuse confidence scores and report data.
    """

    def __init__(self, api_key: str, timeout: int = DEFAULT_TIMEOUT):
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def fetch_ip_reputation(self, ip: str) -> Optional[Dict]:
        """
        Fetch IP reputation from AbuseIPDB.

        Returns:
            Dict with IP reputation data on success, None on failure.
            Dict structure:
            {
                "indicator_value": str,
                "indicator_type": "ip",
                "abuse_confidence_score": int,  # 0-100
                "total_reports": int,
                "country": str,
                "is_whitelisted": bool
            }
        """
        url = f"{ABUSEIPDB_API_BASE_URL}/check"
        headers = {
            "Key": self.api_key,
            "Accept": "application/json"
        }
        params = {
            "ipAddress": ip,
            "maxAgeInDays": 90  # Look back 90 days
        }

        try:
            response = await self.client.get(url, headers=headers, params=params)

            # Handle rate limiting
            if response.status_code == 429:
                logger.warning(f"AbuseIPDB rate limit exceeded for IP {ip}")
                return None

            # Handle auth errors
            if response.status_code == 401:
                logger.error("AbuseIPDB API authentication failed")
                return None

            if response.status_code != 200:
                logger.error(f"AbuseIPDB API error for IP {ip}: {response.status_code}")
                return None

            data = response.json()

            return self._parse_response(data, ip)

        except TimeoutError:
            logger.error(f"Timeout fetching AbuseIPDB data for IP {ip}")
            return None

        except httpx.TimeoutException:
            logger.error(f"HTTP timeout fetching AbuseIPDB data for IP {ip}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching AbuseIPDB data for IP {ip}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching AbuseIPDB data for IP {ip}: {e}")
            return None

    def _parse_response(self, data: Dict, ip: str) -> Optional[Dict]:
        """Parse AbuseIPDB response into internal format."""
        try:
            # AbuseIPDB response structure:
            # {
            #   "data": {
            #     "ipAddress": "1.2.3.4",
            #     "isWhitelisted": false,
            #     "abuseConfidenceScore": 100,
            #     "countryCode": "CN",
            #     "usageType": "Data Center/Web Hosting/Transit",
            #     "totalReports": 50,
            #     "numDistinctUsers": 10,
            #     "lastReportedAt": "2024-02-13T10:00:00+00:00"
            #   }
            # }

            ip_data = data.get("data", {})

            if not ip_data:
                logger.warning(f"No data returned for IP {ip}")
                return None

            return {
                "indicator_value": ip,
                "indicator_type": "ip",
                "abuse_confidence_score": ip_data.get("abuseConfidenceScore", 0),
                "total_reports": ip_data.get("totalReports", 0),
                "country": ip_data.get("countryCode", ""),
                "is_whitelisted": ip_data.get("isWhitelisted", False)
            }

        except Exception as e:
            logger.error(f"Error parsing AbuseIPDB response for IP {ip}: {e}")
            return None

    async def fetch_ips(self, ips: list[str]) -> Dict[str, Optional[Dict]]:
        """
        Fetch reputation for multiple IPs.

        Respects MAX_ITEMS_PER_SOURCE limit (100).

        Returns:
            Dict mapping IP to reputation data (or None if fetch failed)
        """
        # Limit to MAX_ITEMS_PER_SOURCE
        if len(ips) > MAX_ITEMS_PER_SOURCE:
            logger.warning(
                f"Limiting AbuseIPDB fetch from {len(ips)} to {MAX_ITEMS_PER_SOURCE}"
            )
            ips = ips[:MAX_ITEMS_PER_SOURCE]

        results = {}

        # Fetch sequentially to respect rate limits
        for ip in ips:
            result = await self.fetch_ip_reputation(ip)
            results[ip] = result

        return results
