"""
URLhaus API Client.

URLhaus (abuse.ch) provides URL and payload threat intelligence data
including malware URLs, hosts, and file hashes.

API Documentation: https://urlhaus-api.abuse.ch/v1/
Rate limit: Unlimited (free API)
"""

import logging
from typing import Optional, Dict

import httpx


logger = logging.getLogger(__name__)

# Constants
URLHAUS_API_BASE_URL = "https://urlhaus-api.abuse.ch/v1"
DEFAULT_TIMEOUT = 30  # seconds


class URLhausClient:
    """
    Client for URLhaus API (abuse.ch).

    Provides threat intelligence for URLs, hosts, and file hashes.
    """

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize URLhaus client.

        Args:
            timeout: Request timeout in seconds (default: 30)
        """
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def lookup_url(self, url: str) -> Optional[Dict]:
        """
        Lookup a URL in URLhaus database.

        Args:
            url: The URL to lookup (e.g., http://malicious.com/malware.exe)

        Returns:
            Dict with URL threat data on success, None on failure.
            Dict structure when found:
            {
                "query_status": "ok",
                "url": str,
                "url_status": str,  # "online" or "offline"
                "host": str,
                "threat": str,
                "tags": list,
                "payloads": list
            }
        """
        endpoint = f"{URLHAUS_API_BASE_URL}/url/"
        data = {"url": url}

        return await self._post_request(endpoint, data, f"URL {url}")

    async def lookup_host(self, host: str) -> Optional[Dict]:
        """
        Lookup a host (IP or domain) in URLhaus database.

        Args:
            host: The host to lookup (IP address or domain name)

        Returns:
            Dict with host threat data on success, None on failure.
            Dict structure when found:
            {
                "query_status": "ok",
                "host": str,
                "url_count": int,
                "blacklists": dict,
                "urls": list
            }
        """
        endpoint = f"{URLHAUS_API_BASE_URL}/host/"
        data = {"host": host}

        return await self._post_request(endpoint, data, f"host {host}")

    async def lookup_payload(
        self, file_hash: str, hash_type: str = "sha256"
    ) -> Optional[Dict]:
        """
        Lookup a file payload by hash in URLhaus database.

        Args:
            file_hash: The file hash to lookup
            hash_type: Type of hash ("sha256" or "md5", default: "sha256")

        Returns:
            Dict with payload threat data on success, None on failure.
            Dict structure when found:
            {
                "query_status": "ok",
                "md5_hash": str,
                "sha256_hash": str,
                "file_type": str,
                "signature": str,
                "virustotal": dict,
                "urls": list
            }

        Raises:
            ValueError: If hash_type is not "sha256" or "md5"
        """
        if hash_type not in ("sha256", "md5"):
            raise ValueError("hash_type must be 'sha256' or 'md5'")

        endpoint = f"{URLHAUS_API_BASE_URL}/payload/"

        if hash_type == "sha256":
            data = {"sha256_hash": file_hash}
        else:
            data = {"md5_hash": file_hash}

        return await self._post_request(endpoint, data, f"hash {file_hash}")

    async def _post_request(
        self, endpoint: str, data: Dict, description: str
    ) -> Optional[Dict]:
        """
        Make a POST request to URLhaus API.

        Args:
            endpoint: Full API endpoint URL
            data: Form data to POST
            description: Description for logging

        Returns:
            Dict with response data on success, None on failure.
        """
        try:
            response = await self.client.post(
                endpoint,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            # Handle HTTP errors
            if response.status_code != 200:
                logger.error(
                    f"URLhaus API error for {description}: {response.status_code}"
                )
                return None

            return response.json()

        except httpx.TimeoutException:
            logger.error(f"Timeout fetching URLhaus data for {description}")
            return None

        except httpx.ConnectError as e:
            logger.error(f"Connection error fetching URLhaus data for {description}: {e}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching URLhaus data for {description}: {e}")
            return None

        except ValueError as e:
            logger.error(f"JSON decode error for URLhaus {description}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching URLhaus data for {description}: {e}")
            return None
