"""
Shodan API Client.

Shodan is the search engine for internet-connected devices. It provides
information about exposed services, open ports, and vulnerabilities.

API Documentation: https://developer.shodan.io/api
Rate limit: 100 requests/month (free tier)
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any

import httpx


logger = logging.getLogger(__name__)

# Constants
SHODAN_API_BASE_URL = "https://api.shodan.io"
DEFAULT_TIMEOUT = 30  # seconds


@dataclass
class ServiceInfo:
    """Information about an exposed service."""
    port: int
    transport: str
    product: Optional[str] = None
    version: Optional[str] = None
    cpe: List[str] = field(default_factory=list)


@dataclass
class HostInfo:
    """Information about a host from Shodan."""
    ip: str
    org: Optional[str] = None
    isp: Optional[str] = None
    asn: Optional[str] = None
    hostnames: List[str] = field(default_factory=list)
    country_code: Optional[str] = None
    city: Optional[str] = None
    os: Optional[str] = None
    ports: List[int] = field(default_factory=list)
    services: List[ServiceInfo] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    last_update: Optional[str] = None


@dataclass
class VulnerabilityInfo:
    """Information about a vulnerability."""
    cve_id: str
    cvss: Optional[float] = None
    summary: Optional[str] = None
    references: List[str] = field(default_factory=list)
    verified: bool = False


class ShodanClient:
    """
    Client for Shodan API.

    Provides information about internet-connected devices, exposed services,
    and vulnerabilities.
    """

    def __init__(self, api_key: str, timeout: int = DEFAULT_TIMEOUT):
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self._remaining_requests: Optional[int] = None

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    def get_remaining_requests(self) -> Optional[int]:
        """Get the remaining API requests for the month."""
        return self._remaining_requests

    def _update_rate_limit(self, response: httpx.Response):
        """Update rate limit tracking from response headers."""
        remaining = response.headers.get("X-Rate-Limit-Remaining")
        if remaining is not None:
            try:
                self._remaining_requests = int(remaining)
            except ValueError:
                pass

    async def get_host(self, ip: str) -> Optional[HostInfo]:
        """
        Get information about a host.

        Args:
            ip: IP address to lookup

        Returns:
            HostInfo on success, None on failure or not found
        """
        url = f"{SHODAN_API_BASE_URL}/shodan/host/{ip}"
        params = {"key": self.api_key}

        try:
            response = await self.client.get(url, params=params)
            self._update_rate_limit(response)

            # Handle rate limiting
            if response.status_code == 429:
                logger.warning(f"Shodan rate limit exceeded for IP {ip}")
                return None

            # Handle auth errors
            if response.status_code == 401:
                logger.error("Shodan API authentication failed")
                return None

            # Handle not found
            if response.status_code == 404:
                logger.debug(f"No Shodan data for IP {ip}")
                return None

            # Handle server errors
            if response.status_code >= 500:
                logger.error(f"Shodan server error for IP {ip}: {response.status_code}")
                return None

            if response.status_code != 200:
                logger.error(f"Shodan API error for IP {ip}: {response.status_code}")
                return None

            data = response.json()
            return self._parse_host_response(data)

        except httpx.TimeoutException:
            logger.error(f"Timeout fetching Shodan data for IP {ip}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching Shodan data for IP {ip}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching Shodan data for IP {ip}: {e}")
            return None

    def _parse_host_response(self, data: Dict[str, Any]) -> Optional[HostInfo]:
        """Parse Shodan host response into HostInfo."""
        try:
            if not data or "ip_str" not in data:
                return None

            # Parse services from data array
            services = []
            for service_data in data.get("data", []):
                service = ServiceInfo(
                    port=service_data.get("port", 0),
                    transport=service_data.get("transport", "tcp"),
                    product=service_data.get("product"),
                    version=service_data.get("version"),
                    cpe=service_data.get("cpe", [])
                )
                services.append(service)

            return HostInfo(
                ip=data.get("ip_str", ""),
                org=data.get("org"),
                isp=data.get("isp"),
                asn=data.get("asn"),
                hostnames=data.get("hostnames", []),
                country_code=data.get("country_code"),
                city=data.get("city"),
                os=data.get("os"),
                ports=data.get("ports", []),
                services=services,
                tags=data.get("tags", []),
                last_update=data.get("last_update")
            )

        except Exception as e:
            logger.error(f"Error parsing Shodan host response: {e}")
            return None

    async def search(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """
        Search Shodan for hosts matching a query.

        Args:
            query: Shodan search query (e.g., "nginx country:US")
            page: Page number for pagination (default 1)

        Returns:
            List of matching hosts, empty list on error
        """
        url = f"{SHODAN_API_BASE_URL}/shodan/host/search"
        params = {
            "key": self.api_key,
            "query": query,
            "page": page
        }

        try:
            response = await self.client.get(url, params=params)
            self._update_rate_limit(response)

            # Handle rate limiting
            if response.status_code == 429:
                logger.warning(f"Shodan rate limit exceeded for search: {query}")
                return []

            # Handle auth errors
            if response.status_code == 401:
                logger.error("Shodan API authentication failed")
                return []

            # Handle server errors
            if response.status_code >= 500:
                logger.error(f"Shodan server error for search: {response.status_code}")
                return []

            if response.status_code != 200:
                logger.error(f"Shodan API error for search: {response.status_code}")
                return []

            data = response.json()
            return data.get("matches", [])

        except httpx.TimeoutException:
            logger.error(f"Timeout during Shodan search: {query}")
            return []

        except httpx.RequestError as e:
            logger.error(f"Request error during Shodan search: {e}")
            return []

        except Exception as e:
            logger.error(f"Unexpected error during Shodan search: {e}")
            return []

    async def get_services(self, ip: str) -> List[ServiceInfo]:
        """
        Get exposed services for an IP.

        Args:
            ip: IP address to lookup

        Returns:
            List of ServiceInfo, empty list if not found or error
        """
        host = await self.get_host(ip)
        if host is None:
            return []
        return host.services

    async def check_vulnerabilities(self, ip: str) -> List[VulnerabilityInfo]:
        """
        Check vulnerabilities for an IP.

        Args:
            ip: IP address to lookup

        Returns:
            List of VulnerabilityInfo, empty list if not found or no vulns
        """
        url = f"{SHODAN_API_BASE_URL}/shodan/host/{ip}"
        params = {"key": self.api_key}

        try:
            response = await self.client.get(url, params=params)
            self._update_rate_limit(response)

            # Handle errors
            if response.status_code != 200:
                return []

            data = response.json()
            return self._parse_vulnerabilities(data)

        except Exception as e:
            logger.error(f"Error checking vulnerabilities for IP {ip}: {e}")
            return []

    def _parse_vulnerabilities(self, data: Dict[str, Any]) -> List[VulnerabilityInfo]:
        """Parse vulnerabilities from Shodan host data."""
        vulns = []
        seen_cves = set()

        # Check each service for vulns
        for service_data in data.get("data", []):
            vulns_data = service_data.get("vulns", {})
            for cve_id, vuln_info in vulns_data.items():
                if cve_id in seen_cves:
                    continue
                seen_cves.add(cve_id)

                vuln = VulnerabilityInfo(
                    cve_id=cve_id,
                    cvss=vuln_info.get("cvss"),
                    summary=vuln_info.get("summary"),
                    references=vuln_info.get("references", []),
                    verified=vuln_info.get("verified", False)
                )
                vulns.append(vuln)

        return vulns
