"""
IPinfo API Client.

IPinfo provides IP geolocation, ASN, and basic metadata for IP addresses.

API Documentation: https://ipinfo.io/developers
Rate limit: 50,000 requests/month (free tier, no API key needed for basic)
"""

import logging
import re
from typing import Optional, Dict

import httpx


logger = logging.getLogger(__name__)

# Constants
IPINFO_API_BASE_URL = "https://ipinfo.io"
DEFAULT_TIMEOUT = 30  # seconds

# Regex to parse ASN from org field (e.g., "AS15169 Google LLC")
ASN_PATTERN = re.compile(r'^(AS\d+)\s+(.+)$')


class IPinfoClient:
    """
    Client for IPinfo API.

    Provides IP geolocation, ASN, and metadata lookup.
    """

    def __init__(self, api_key: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize IPinfo client.

        Args:
            api_key: Optional API key for higher rate limits. Not required for basic usage.
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_ip_info(self, ip: str) -> Optional[Dict]:
        """
        Fetch IP information from IPinfo.

        Args:
            ip: The IP address to look up.

        Returns:
            Dict with IP info on success, None on failure.
            Dict structure:
            {
                "ip": str,
                "hostname": str,
                "city": str,
                "region": str,
                "country": str,
                "loc": str,  # "lat,lng"
                "org": str,  # "AS##### Org Name"
                "postal": str,
                "timezone": str,
                "asn": str,  # Parsed ASN (e.g., "AS15169")
                "org_name": str,  # Parsed org name (e.g., "Google LLC")
                "bogon": bool  # True if private/reserved IP
            }
        """
        url = f"{IPINFO_API_BASE_URL}/{ip}/json"
        headers = {"Accept": "application/json"}

        # Add API key if provided
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = await self.client.get(url, headers=headers)

            # Handle rate limiting
            if response.status_code == 429:
                logger.warning(f"IPinfo rate limit exceeded for IP {ip}")
                return None

            # Handle other errors
            if response.status_code != 200:
                logger.error(f"IPinfo API error for IP {ip}: {response.status_code}")
                return None

            data = response.json()

            return self._parse_response(data)

        except httpx.TimeoutException:
            logger.error(f"HTTP timeout fetching IPinfo data for IP {ip}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching IPinfo data for IP {ip}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching IPinfo data for IP {ip}: {e}")
            return None

    async def get_geolocation(self, ip: str) -> Optional[Dict]:
        """
        Fetch geolocation data for an IP address.

        Args:
            ip: The IP address to look up.

        Returns:
            Dict with geolocation data on success, None on failure.
            Dict structure:
            {
                "latitude": float,
                "longitude": float,
                "city": str,
                "region": str,
                "country": str,
                "postal": str,
                "timezone": str
            }
        """
        ip_info = await self.get_ip_info(ip)

        if ip_info is None:
            return None

        return self._extract_geolocation(ip_info)

    def _parse_response(self, data: Dict) -> Dict:
        """Parse IPinfo response and enrich with parsed fields."""
        result = {
            "ip": data.get("ip", ""),
            "hostname": data.get("hostname", ""),
            "city": data.get("city", ""),
            "region": data.get("region", ""),
            "country": data.get("country", ""),
            "loc": data.get("loc", ""),
            "org": data.get("org", ""),
            "postal": data.get("postal", ""),
            "timezone": data.get("timezone", ""),
            "bogon": data.get("bogon", False)
        }

        # Parse ASN and org name from org field
        asn, org_name = self._parse_org(data.get("org", ""))
        result["asn"] = asn
        result["org_name"] = org_name

        return result

    def _parse_org(self, org: str) -> tuple[Optional[str], str]:
        """
        Parse ASN and organization name from org field.

        Args:
            org: The org field value (e.g., "AS15169 Google LLC")

        Returns:
            Tuple of (asn, org_name). ASN may be None if not in standard format.
        """
        if not org:
            return None, ""

        match = ASN_PATTERN.match(org)
        if match:
            return match.group(1), match.group(2)

        # Org doesn't have ASN format
        return None, org

    def _extract_geolocation(self, ip_info: Dict) -> Dict:
        """
        Extract geolocation data from full IP info.

        Args:
            ip_info: The full IP info dict.

        Returns:
            Dict with geolocation fields only.
        """
        latitude = None
        longitude = None

        # Parse loc field (format: "lat,lng")
        loc = ip_info.get("loc", "")
        if loc and "," in loc:
            try:
                lat_str, lng_str = loc.split(",")
                latitude = float(lat_str)
                longitude = float(lng_str)
            except (ValueError, TypeError):
                logger.warning(f"Failed to parse location: {loc}")

        return {
            "latitude": latitude,
            "longitude": longitude,
            "city": ip_info.get("city", ""),
            "region": ip_info.get("region", ""),
            "country": ip_info.get("country", ""),
            "postal": ip_info.get("postal", ""),
            "timezone": ip_info.get("timezone", "")
        }
