"""
OSV (Open Source Vulnerabilities) API Client.

Free API, no authentication required.
API Documentation: https://osv.dev/docs/

Endpoints:
- POST /query - Query vulnerabilities by package or commit
- GET /vulns/{id} - Get vulnerability by OSV ID
- POST /querybatch - Batch query multiple packages
"""

import logging
from typing import Optional, List, Dict, Any

import httpx


logger = logging.getLogger(__name__)

# Constants
OSV_API_BASE_URL = "https://api.osv.dev/v1"
DEFAULT_TIMEOUT = 30  # seconds


class OSVClient:
    """
    Client for OSV (Open Source Vulnerabilities) API.

    Provides access to open source vulnerability data for packages
    across multiple ecosystems (npm, PyPI, Maven, etc.).

    Returns None on errors instead of raising exceptions to prevent
    blocking the entire enrichment process.
    """

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize the OSV client.

        Args:
            timeout: Request timeout in seconds (default: 30)
        """
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> "OSVClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def fetch_vulnerability(self, osv_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch vulnerability data by OSV ID.

        Args:
            osv_id: The OSV vulnerability ID (e.g., "GHSA-jfh8-c2jp-5v3q")

        Returns:
            Dict with parsed vulnerability data, or None on failure.
            Structure:
            {
                "osv_id": str,
                "cve_id": str | None,
                "summary": str,
                "severity": str | None,
                "affected": List[Dict],
                "references": List[Dict]
            }
        """
        url = f"{OSV_API_BASE_URL}/vulns/{osv_id}"

        try:
            response = await self.client.get(url)

            if response.status_code == 404:
                logger.warning(f"OSV vulnerability not found: {osv_id}")
                return None

            if response.status_code != 200:
                logger.error(f"OSV API error for {osv_id}: {response.status_code}")
                return None

            data = response.json()
            return self._parse_vulnerability(data)

        except httpx.TimeoutException:
            logger.error(f"Timeout fetching OSV vulnerability {osv_id}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching OSV vulnerability {osv_id}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching OSV vulnerability {osv_id}: {e}")
            return None

    async def query_by_cve(self, cve_id: str) -> List[Dict[str, Any]]:
        """
        Query vulnerabilities by CVE ID.

        Args:
            cve_id: The CVE ID (e.g., "CVE-2021-44228")

        Returns:
            List of parsed vulnerability dicts, or empty list on failure.
        """
        url = f"{OSV_API_BASE_URL}/query"
        payload = {"query": cve_id}

        try:
            response = await self.client.post(url, json=payload)

            if response.status_code != 200:
                logger.error(f"OSV API error querying CVE {cve_id}: {response.status_code}")
                return []

            data = response.json()
            vulns = data.get("vulns", [])

            return [self._parse_vulnerability(v) for v in vulns if v]

        except httpx.TimeoutException:
            logger.error(f"Timeout querying OSV for CVE {cve_id}")
            return []

        except httpx.RequestError as e:
            logger.error(f"Request error querying OSV for CVE {cve_id}: {e}")
            return []

        except Exception as e:
            logger.error(f"Unexpected error querying OSV for CVE {cve_id}: {e}")
            return []

    async def query_by_package(
        self,
        ecosystem: str,
        name: str,
        version: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query vulnerabilities by package ecosystem and name.

        Args:
            ecosystem: Package ecosystem (e.g., "npm", "PyPI", "Maven")
            name: Package name
            version: Optional package version to check

        Returns:
            List of parsed vulnerability dicts, or empty list on failure.
        """
        url = f"{OSV_API_BASE_URL}/query"
        payload: Dict[str, Any] = {
            "package": {
                "ecosystem": ecosystem,
                "name": name
            }
        }

        if version:
            payload["version"] = version

        try:
            response = await self.client.post(url, json=payload)

            if response.status_code != 200:
                logger.error(
                    f"OSV API error querying package {ecosystem}/{name}: {response.status_code}"
                )
                return []

            data = response.json()
            vulns = data.get("vulns", [])

            return [self._parse_vulnerability(v) for v in vulns if v]

        except httpx.TimeoutException:
            logger.error(f"Timeout querying OSV for package {ecosystem}/{name}")
            return []

        except httpx.RequestError as e:
            logger.error(f"Request error querying OSV for package {ecosystem}/{name}: {e}")
            return []

        except Exception as e:
            logger.error(f"Unexpected error querying OSV for package {ecosystem}/{name}: {e}")
            return []

    async def batch_query(self, queries: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Batch query multiple packages at once.

        Args:
            queries: List of query dicts, each containing package info.
                     Example: [{"package": {"ecosystem": "npm", "name": "express"}}]

        Returns:
            List of lists, where each inner list contains parsed vulnerabilities
            for the corresponding query. Returns empty lists on failure.
        """
        url = f"{OSV_API_BASE_URL}/querybatch"
        payload = {"queries": queries}

        try:
            response = await self.client.post(url, json=payload)

            if response.status_code != 200:
                logger.error(f"OSV API error in batch query: {response.status_code}")
                return [[] for _ in queries]

            data = response.json()
            results = data.get("results", [])

            parsed_results = []
            for result in results:
                vulns = result.get("vulns", [])
                parsed_vulns = [self._parse_vulnerability(v) for v in vulns if v]
                parsed_results.append(parsed_vulns)

            return parsed_results

        except httpx.TimeoutException:
            logger.error("Timeout in OSV batch query")
            return [[] for _ in queries]

        except httpx.RequestError as e:
            logger.error(f"Request error in OSV batch query: {e}")
            return [[] for _ in queries]

        except Exception as e:
            logger.error(f"Unexpected error in OSV batch query: {e}")
            return [[] for _ in queries]

    def _parse_vulnerability(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse OSV API response into our internal format.

        Handles malformed responses gracefully.
        """
        try:
            osv_id = data.get("id")
            if not osv_id:
                logger.warning("OSV response missing 'id' field")
                return None

            # Extract CVE ID from aliases
            aliases = data.get("aliases", [])
            cve_id = None
            for alias in aliases:
                if alias.startswith("CVE-"):
                    cve_id = alias
                    break

            # Extract severity
            severity = self._extract_severity(data)

            # Parse affected packages
            affected = []
            for aff in data.get("affected", []):
                affected_entry = {
                    "package": aff.get("package", {}),
                    "ranges": aff.get("ranges", []),
                    "ecosystem_specific": aff.get("ecosystem_specific", {})
                }
                affected.append(affected_entry)

            # Parse references
            references = []
            for ref in data.get("references", []):
                references.append({
                    "type": ref.get("type", ""),
                    "url": ref.get("url", "")
                })

            return {
                "osv_id": osv_id,
                "cve_id": cve_id,
                "summary": data.get("summary", ""),
                "severity": severity,
                "affected": affected,
                "references": references
            }

        except Exception as e:
            logger.error(f"Error parsing OSV vulnerability: {e}")
            return None

    def _extract_severity(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Extract severity level from OSV vulnerability data.

        Checks both CVSS score and ecosystem_specific severity.
        """
        # First, check ecosystem_specific in affected packages
        for aff in data.get("affected", []):
            eco_specific = aff.get("ecosystem_specific", {})
            if "severity" in eco_specific:
                return eco_specific["severity"]

        # Then, try to extract from CVSS
        severity_list = data.get("severity", [])
        for sev in severity_list:
            score = sev.get("score", "")
            if "CVSS" in score:
                # Parse CVSS score to determine severity
                return self._cvss_to_severity(score)

        return None

    def _cvss_to_severity(self, cvss_vector: str) -> Optional[str]:
        """
        Convert CVSS vector string to severity level.

        This is a simplified conversion based on typical CVSS patterns.
        """
        # For CVSS v3, we look for high impact indicators
        if "/S:C/" in cvss_vector or "/S:U/" in cvss_vector:
            # Check impact metrics
            if "/C:H/I:H/A:H" in cvss_vector:
                return "CRITICAL"
            elif "/C:H/" in cvss_vector or "/I:H/" in cvss_vector or "/A:H/" in cvss_vector:
                return "HIGH"
            elif "/C:L/" in cvss_vector or "/I:L/" in cvss_vector or "/A:L/" in cvss_vector:
                return "MEDIUM"
            else:
                return "LOW"

        return None
