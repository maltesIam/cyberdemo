"""
HaveIBeenPwned (HIBP) API Client.

HIBP provides data breach and password exposure checking services.
Uses k-anonymity for password checks to avoid sending the full password hash.

API Documentation: https://haveibeenpwned.com/api/v3
Rate limit: 1500ms between requests for breach search API (requires API key)
Password API: No rate limit, uses k-anonymity (first 5 chars of SHA1 hash)
"""

import hashlib
import logging
from typing import Optional, List, Dict
from urllib.parse import quote

import httpx


logger = logging.getLogger(__name__)

# Constants
HIBP_PASSWORD_API_BASE_URL = "https://api.pwnedpasswords.com/range"
HIBP_BREACH_API_BASE_URL = "https://haveibeenpwned.com/api/v3"
DEFAULT_TIMEOUT = 30  # seconds
USER_AGENT = "CyberDemo-HIBP-Client/1.0"


class HIBPClient:
    """
    Client for HaveIBeenPwned API.

    Provides password exposure checking (using k-anonymity) and
    email breach checking services.
    """

    def __init__(self, api_key: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize HIBP client.

        Args:
            api_key: API key for breach searches (required for email checks).
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def check_password(self, password: str) -> int:
        """
        Check if a password has been exposed in data breaches.

        Uses k-anonymity model: only the first 5 characters of the SHA1 hash
        are sent to the API. The full hash is never transmitted.

        Args:
            password: The password to check.

        Returns:
            int: Number of times the password appears in breaches.
                 Returns 0 if not found or on error.
        """
        # Calculate SHA1 hash of the password
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]

        url = f"{HIBP_PASSWORD_API_BASE_URL}/{prefix}"
        headers = {
            "User-Agent": USER_AGENT
        }

        try:
            response = await self.client.get(url, headers=headers)

            if response.status_code != 200:
                logger.error(f"HIBP password API error: {response.status_code}")
                return 0

            # Parse the response - each line is SUFFIX:COUNT
            for line in response.text.splitlines():
                parts = line.strip().split(':')
                if len(parts) == 2:
                    response_suffix, count = parts
                    if response_suffix.upper() == suffix:
                        return int(count)

            # Suffix not found in response - password not pwned
            return 0

        except httpx.TimeoutException:
            logger.error("Timeout checking password against HIBP")
            return 0

        except httpx.RequestError as e:
            logger.error(f"Request error checking password against HIBP: {e}")
            return 0

        except Exception as e:
            logger.error(f"Unexpected error checking password against HIBP: {e}")
            return 0

    async def check_email_breaches(self, email: str) -> Optional[List[Dict]]:
        """
        Check if an email has been involved in any data breaches.

        Requires an API key.

        Args:
            email: The email address to check.

        Returns:
            List of breach dictionaries on success, empty list if not found,
            None on error or if API key is not provided.
        """
        # API key is required for breach searches
        if not self.api_key:
            logger.warning("HIBP API key required for email breach checks")
            return None

        # URL encode the email
        encoded_email = quote(email, safe='')
        url = f"{HIBP_BREACH_API_BASE_URL}/breachedaccount/{encoded_email}"

        headers = {
            "User-Agent": USER_AGENT,
            "hibp-api-key": self.api_key
        }

        try:
            response = await self.client.get(url, headers=headers)

            # Handle not found (email not in any breach)
            if response.status_code == 404:
                logger.info(f"Email not found in any breaches: {email}")
                return []

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = response.headers.get("retry-after", "unknown")
                logger.warning(f"HIBP rate limit exceeded, retry after: {retry_after}")
                return None

            # Handle authentication error
            if response.status_code == 401:
                logger.error("HIBP API authentication failed - invalid API key")
                return None

            # Handle server error
            if response.status_code >= 500:
                logger.error(f"HIBP API server error: {response.status_code}")
                return None

            # Handle other errors
            if response.status_code != 200:
                logger.error(f"HIBP API error for email {email}: {response.status_code}")
                return None

            return response.json()

        except httpx.TimeoutException:
            logger.error(f"Timeout checking email breaches for: {email}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error checking email breaches for {email}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error checking email breaches for {email}: {e}")
            return None
