"""
Censys API Client.

Censys provides internet-wide scanning data for hosts, certificates, and services.
It's similar to Shodan but with different data sources and scanning methodology.

API Documentation: https://search.censys.io/api
Rate limit: 250 requests/month (free tier)
"""

import logging
from typing import Optional, Dict

import httpx


logger = logging.getLogger(__name__)

# Constants
CENSYS_API_BASE_URL = "https://search.censys.io/api/v2"
DEFAULT_TIMEOUT = 30  # seconds


class CensysClient:
    """
    Client for Censys Search API v2.

    Provides internet-wide scanning data for hosts and services.
    Requires API ID and API Secret for HTTP Basic Authentication.
    """

    def __init__(
        self,
        api_id: str,
        api_secret: str,
        timeout: int = DEFAULT_TIMEOUT
    ):
        """
        Initialize Censys client.

        Args:
            api_id: Censys API ID (username for Basic Auth).
            api_secret: Censys API Secret (password for Basic Auth).
            timeout: Request timeout in seconds.
        """
        self.api_id = api_id
        self.api_secret = api_secret
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    def _get_auth(self) -> tuple:
        """Get Basic Auth credentials tuple."""
        return (self.api_id, self.api_secret)

    async def _make_request(
        self,
        url: str,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make GET request to Censys API.

        Args:
            url: Full URL to request.
            params: Optional query parameters.

        Returns:
            Dict with response data on success, None on failure.
        """
        try:
            response = await self.client.get(
                url,
                auth=self._get_auth(),
                params=params or {}
            )

            # Handle rate limiting (250 requests/month)
            if response.status_code == 429:
                logger.warning(f"Censys rate limit exceeded for {url}")
                return None

            # Handle authentication errors
            if response.status_code == 401:
                logger.error("Censys API authentication failed - invalid credentials")
                return None

            # Handle forbidden access
            if response.status_code == 403:
                logger.error("Censys API access forbidden")
                return None

            # Handle not found
            if response.status_code == 404:
                logger.info(f"Censys resource not found: {url}")
                return None

            # Handle bad request
            if response.status_code == 400:
                logger.error(f"Censys bad request: {url}")
                return None

            # Handle server errors
            if response.status_code >= 500:
                logger.error(f"Censys server error: {response.status_code}")
                return None

            if response.status_code != 200:
                logger.error(f"Censys API error: {response.status_code}")
                return None

            data = response.json()

            # Validate response structure
            if "result" not in data:
                logger.warning("Censys malformed response - missing 'result' key")
                return None

            return data["result"]

        except httpx.TimeoutException:
            logger.error(f"Censys request timeout for {url}")
            return None

        except httpx.ConnectError as e:
            logger.error(f"Censys connection error: {e}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Censys request error: {e}")
            return None

        except ValueError as e:
            logger.error(f"Censys JSON parse error: {e}")
            return None

        except Exception as e:
            logger.error(f"Censys unexpected error: {e}")
            return None

    async def search_hosts(
        self,
        query: str,
        cursor: Optional[str] = None,
        per_page: int = 25
    ) -> Optional[Dict]:
        """
        Search for hosts in Censys database.

        Args:
            query: Censys search query (e.g., "services.port: 22").
            cursor: Pagination cursor for next page.
            per_page: Number of results per page (default 25, max 100).

        Returns:
            Dict with search results on success:
            {
                "query": str,
                "total": int,
                "hits": List[Dict],
                "links": Dict (pagination cursors)
            }
            None on failure.
        """
        url = f"{CENSYS_API_BASE_URL}/hosts/search"

        params = {
            "q": query,
            "per_page": per_page
        }

        if cursor:
            params["cursor"] = cursor

        return await self._make_request(url, params)

    async def get_host(self, ip: str) -> Optional[Dict]:
        """
        Get detailed information for a specific host/IP.

        Args:
            ip: IP address to lookup.

        Returns:
            Dict with host details on success:
            {
                "ip": str,
                "services": List[Dict],
                "location": Dict,
                "autonomous_system": Dict,
                "operating_system": Dict,
                "last_updated_at": str,
                ...
            }
            None on failure or not found.
        """
        url = f"{CENSYS_API_BASE_URL}/hosts/{ip}"
        return await self._make_request(url)
