"""
Pulsedive API Client.

Pulsedive provides threat intelligence data including risk scores,
geo location, and threat attribution.

API Documentation: https://pulsedive.com/api/
Rate limit: 100 requests/day (free tier)
"""

import logging
from typing import Optional, Dict

import httpx


logger = logging.getLogger(__name__)

# Constants
PULSEDIVE_API_BASE_URL = "https://pulsedive.com/api"
DEFAULT_TIMEOUT = 30  # seconds


class PulsediveClient:
    """
    Client for Pulsedive API.

    Provides threat intelligence including risk scores, geo location,
    and threat attribution for IPs, domains, and URLs.
    """

    def __init__(self, api_key: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize Pulsedive client.

        Args:
            api_key: Optional API key for higher rate limits.
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_indicator_info(self, indicator: str) -> Optional[Dict]:
        """
        Fetch indicator information from Pulsedive.

        Args:
            indicator: The indicator value (IP, domain, URL, hash).

        Returns:
            Dict with indicator data on success, None on failure.
            Dict structure:
            {
                "indicator": str,
                "type": str,  # ip, domain, url, hash
                "risk": str,  # none, low, medium, high, critical
                "risk_recommended": str,
                "attributes": dict,
                "properties": dict,  # includes geo and whois
                "threats": list,
                "feeds": list
            }
        """
        url = f"{PULSEDIVE_API_BASE_URL}/info.php"
        params = {
            "indicator": indicator,
            "pretty": "1"
        }

        # Include API key if provided
        if self.api_key:
            params["key"] = self.api_key

        try:
            response = await self.client.get(url, params=params)

            # Handle rate limiting
            if response.status_code == 429:
                logger.warning(f"Pulsedive rate limit exceeded for indicator {indicator}")
                return None

            # Handle auth errors
            if response.status_code == 401:
                logger.error("Pulsedive API authentication failed")
                return None

            # Handle not found
            if response.status_code == 404:
                logger.info(f"Pulsedive indicator not found: {indicator}")
                return None

            if response.status_code != 200:
                logger.error(f"Pulsedive API error for indicator {indicator}: {response.status_code}")
                return None

            data = response.json()
            return data

        except TimeoutError:
            logger.error(f"Timeout fetching Pulsedive data for indicator {indicator}")
            return None

        except httpx.TimeoutException:
            logger.error(f"HTTP timeout fetching Pulsedive data for indicator {indicator}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching Pulsedive data for indicator {indicator}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching Pulsedive data for indicator {indicator}: {e}")
            return None

    async def get_indicator_links(self, indicator_id: int) -> Optional[Dict]:
        """
        Fetch linked indicators for a given indicator ID.

        Args:
            indicator_id: The Pulsedive indicator ID (iid).

        Returns:
            Dict with linked indicators on success, None on failure.
            Dict structure:
            {
                "results": [
                    {
                        "iid": int,
                        "indicator": str,
                        "type": str,
                        "risk": str
                    }
                ],
                "count": int
            }
        """
        url = f"{PULSEDIVE_API_BASE_URL}/info.php"
        params = {
            "iid": indicator_id,
            "get": "links",
            "pretty": "1"
        }

        if self.api_key:
            params["key"] = self.api_key

        try:
            response = await self.client.get(url, params=params)

            # Handle rate limiting
            if response.status_code == 429:
                logger.warning(f"Pulsedive rate limit exceeded for indicator ID {indicator_id}")
                return None

            # Handle auth errors
            if response.status_code == 401:
                logger.error("Pulsedive API authentication failed")
                return None

            # Handle not found
            if response.status_code == 404:
                logger.info(f"Pulsedive indicator ID not found: {indicator_id}")
                return None

            if response.status_code != 200:
                logger.error(f"Pulsedive API error for indicator ID {indicator_id}: {response.status_code}")
                return None

            data = response.json()
            return data

        except TimeoutError:
            logger.error(f"Timeout fetching Pulsedive links for indicator ID {indicator_id}")
            return None

        except httpx.TimeoutException:
            logger.error(f"HTTP timeout fetching Pulsedive links for indicator ID {indicator_id}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching Pulsedive links for indicator ID {indicator_id}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching Pulsedive links for indicator ID {indicator_id}: {e}")
            return None

    async def explore(self, query: str) -> Optional[Dict]:
        """
        Search/explore indicators using Pulsedive query syntax.

        Args:
            query: The search query (e.g., "risk:high type:ip").

        Returns:
            Dict with search results on success, None on failure.
            Dict structure:
            {
                "results": [
                    {
                        "iid": int,
                        "indicator": str,
                        "type": str,
                        "risk": str
                    }
                ],
                "count": int
            }
        """
        url = f"{PULSEDIVE_API_BASE_URL}/explore.php"
        params = {
            "q": query,
            "pretty": "1"
        }

        if self.api_key:
            params["key"] = self.api_key

        try:
            response = await self.client.get(url, params=params)

            # Handle rate limiting
            if response.status_code == 429:
                logger.warning(f"Pulsedive rate limit exceeded for explore query: {query}")
                return None

            # Handle auth errors
            if response.status_code == 401:
                logger.error("Pulsedive API authentication failed")
                return None

            if response.status_code != 200:
                logger.error(f"Pulsedive API error for explore query '{query}': {response.status_code}")
                return None

            data = response.json()
            return data

        except TimeoutError:
            logger.error(f"Timeout during Pulsedive explore query: {query}")
            return None

        except httpx.TimeoutException:
            logger.error(f"HTTP timeout during Pulsedive explore query: {query}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error during Pulsedive explore query '{query}': {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error during Pulsedive explore query '{query}': {e}")
            return None
