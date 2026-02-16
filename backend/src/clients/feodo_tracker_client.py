"""
Feodo Tracker API Client.

Feodo Tracker (abuse.ch) provides C2 server intelligence including
botnet command-and-control server IPs and malware families.

API Documentation: https://feodotracker.abuse.ch/
Data Source: https://feodotracker.abuse.ch/downloads/ipblocklist.json
Rate limit: Unlimited (free API, no authentication required)
"""

import logging
from typing import Optional, List
import time

import httpx


logger = logging.getLogger(__name__)

# Constants
FEODO_TRACKER_BLOCKLIST_URL = "https://feodotracker.abuse.ch/downloads/ipblocklist.json"
DEFAULT_TIMEOUT = 30  # seconds
CACHE_TTL_SECONDS = 300  # 5 minutes cache


class FeodoTrackerClient:
    """
    Client for Feodo Tracker API.

    Provides access to C2 server blocklist data including:
    - IP addresses of known C2 servers
    - Associated malware families (Dridex, Emotet, QakBot, etc.)
    - Network information (AS number, country)
    - Status (online/offline)
    """

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self._cache: Optional[List[dict]] = None
        self._cache_timestamp: float = 0

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def clear_cache(self):
        """Clear the cached blocklist data."""
        self._cache = None
        self._cache_timestamp = 0

    def _is_cache_valid(self) -> bool:
        """Check if the cache is still valid."""
        if self._cache is None:
            return False
        return (time.time() - self._cache_timestamp) < CACHE_TTL_SECONDS

    async def get_blocklist(self) -> List[dict]:
        """
        Fetch the full IP blocklist from Feodo Tracker.

        Returns:
            List of dicts containing C2 server data. Empty list on error.
            Each dict structure:
            {
                "ip_address": str,
                "port": int,
                "status": str ("online" or "offline"),
                "hostname": str or None,
                "as_number": int,
                "as_name": str,
                "country": str,
                "first_seen": str,
                "last_online": str,
                "malware": str
            }
        """
        # Check cache first
        if self._is_cache_valid():
            return self._cache

        try:
            response = await self.client.get(FEODO_TRACKER_BLOCKLIST_URL)

            if response.status_code != 200:
                logger.error(
                    f"Feodo Tracker API error: {response.status_code}"
                )
                return []

            data = response.json()

            # Update cache
            self._cache = data
            self._cache_timestamp = time.time()

            return data

        except httpx.TimeoutException:
            logger.error("Timeout fetching Feodo Tracker blocklist")
            return []

        except httpx.ConnectError as e:
            logger.error(f"Connection error fetching Feodo Tracker blocklist: {e}")
            return []

        except httpx.RequestError as e:
            logger.error(f"Request error fetching Feodo Tracker blocklist: {e}")
            return []

        except ValueError as e:
            logger.error(f"JSON parse error from Feodo Tracker: {e}")
            return []

        except Exception as e:
            logger.error(f"Unexpected error fetching Feodo Tracker blocklist: {e}")
            return []

    async def check_ip(self, ip: str) -> Optional[dict]:
        """
        Check if an IP exists in the Feodo Tracker blocklist.

        Args:
            ip: The IP address to check.

        Returns:
            Dict with C2 server data if found, None if not found or on error.
        """
        blocklist = await self.get_blocklist()

        for entry in blocklist:
            if entry.get("ip_address") == ip:
                return entry

        return None

    async def get_by_malware(self, malware: str) -> List[dict]:
        """
        Get all C2 servers associated with a specific malware family.

        Args:
            malware: The malware family name (e.g., "Dridex", "Emotet").
                     Matching is case-insensitive.

        Returns:
            List of dicts containing C2 server data for the specified malware.
            Empty list if no matches or on error.
        """
        blocklist = await self.get_blocklist()

        malware_lower = malware.lower()
        matches = [
            entry for entry in blocklist
            if entry.get("malware", "").lower() == malware_lower
        ]

        return matches
