"""
ThreatFox API Client.

ThreatFox (abuse.ch) provides threat intelligence data including IOC information,
malware families, and threat types.

API Documentation: https://threatfox.abuse.ch/api/
Rate limit: Free, unlimited API
"""

import logging
from typing import Optional, Dict

import httpx


logger = logging.getLogger(__name__)

# Constants
THREATFOX_API_BASE_URL = "https://threatfox-api.abuse.ch/api/v1/"
DEFAULT_TIMEOUT = 30  # seconds


class ThreatFoxClient:
    """
    Client for ThreatFox API.

    Provides IOC search, malware family information, and threat intelligence.
    """

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def search_ioc(self, ioc: str) -> Optional[Dict]:
        """
        Search for an IOC (Indicator of Compromise) in ThreatFox.

        Args:
            ioc: The IOC to search for (IP, domain, hash, etc.)

        Returns:
            Dict with IOC data on success, None on failure.
            Dict structure:
            {
                "query_status": "ok" | "no_result" | "illegal_search_term",
                "data": [{
                    "ioc": str,
                    "threat_type": str,
                    "malware": str,
                    "confidence_level": int,
                    "first_seen": str,
                    "last_seen": str,
                    "tags": list
                }]
            }
        """
        payload = {
            "query": "search_ioc",
            "search_term": ioc
        }

        return await self._make_request(payload, f"IOC {ioc}")

    async def get_ioc_by_id(self, ioc_id: str) -> Optional[Dict]:
        """
        Get detailed information for a specific IOC by its ThreatFox ID.

        Args:
            ioc_id: The ThreatFox IOC ID

        Returns:
            Dict with detailed IOC data on success, None on failure.
        """
        payload = {
            "query": "ioc",
            "id": ioc_id
        }

        return await self._make_request(payload, f"IOC ID {ioc_id}")

    async def search_by_malware(self, malware: str) -> Optional[Dict]:
        """
        Search for all IOCs associated with a malware family.

        Args:
            malware: The malware family name (e.g., "Cobalt Strike")

        Returns:
            Dict with list of IOCs for the malware family.
        """
        payload = {
            "query": "malwareinfo",
            "malware": malware
        }

        return await self._make_request(payload, f"malware {malware}")

    async def _make_request(self, payload: Dict, context: str) -> Optional[Dict]:
        """
        Make a POST request to the ThreatFox API.

        Args:
            payload: The JSON payload to send
            context: Context string for logging

        Returns:
            Dict with API response on success, None on error.
        """
        try:
            response = await self.client.post(
                THREATFOX_API_BASE_URL,
                json=payload
            )

            # Handle non-200 status codes
            if response.status_code != 200:
                logger.error(f"ThreatFox API error for {context}: HTTP {response.status_code}")
                return None

            data = response.json()
            return data

        except httpx.TimeoutException:
            logger.error(f"Timeout fetching ThreatFox data for {context}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching ThreatFox data for {context}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching ThreatFox data for {context}: {e}")
            return None
