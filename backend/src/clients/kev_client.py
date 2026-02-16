"""
CISA KEV (Known Exploited Vulnerabilities) API Client.

CISA KEV provides a catalog of vulnerabilities that are known to be actively
exploited in the wild. This is critical for vulnerability prioritization.

API URL: https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
Rate limit: Free API, no authentication required.
"""

import logging
from typing import Optional, Dict, List

import httpx


logger = logging.getLogger(__name__)

# Constants
KEV_API_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
DEFAULT_TIMEOUT = 30  # seconds


class KEVClient:
    """
    Client for CISA KEV (Known Exploited Vulnerabilities) API.

    Provides methods to check if CVEs are in the KEV catalog, which indicates
    they are actively being exploited in the wild.
    """

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize KEV client.

        Args:
            timeout: HTTP request timeout in seconds (default: 30)
        """
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> "KEVClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def fetch_kev_catalog(self) -> Optional[Dict]:
        """
        Fetch the full CISA KEV catalog.

        Returns:
            Dict with KEV catalog data on success, None on failure.
            Dict structure:
            {
                "title": str,
                "catalogVersion": str,
                "dateReleased": str,
                "count": int,
                "vulnerabilities": [
                    {
                        "cveID": str,
                        "vendorProject": str,
                        "product": str,
                        "vulnerabilityName": str,
                        "dateAdded": str,
                        "shortDescription": str,
                        "requiredAction": str,
                        "dueDate": str,
                        "knownRansomwareCampaignUse": str  # "Known" or "Unknown"
                    }
                ]
            }
        """
        try:
            response = await self.client.get(KEV_API_URL)

            if response.status_code != 200:
                logger.error(f"KEV API error: HTTP {response.status_code}")
                return None

            data = response.json()
            return data

        except httpx.TimeoutException:
            logger.error("Timeout fetching KEV catalog")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching KEV catalog: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching KEV catalog: {e}")
            return None

    async def check_cve(self, cve_id: str) -> Optional[Dict]:
        """
        Check if a specific CVE is in the KEV catalog.

        Args:
            cve_id: The CVE ID to check (e.g., "CVE-2024-21351")

        Returns:
            Dict with KEV data if CVE is in catalog, None if not found or error.
            Dict structure:
            {
                "is_kev": True,
                "date_added": str,
                "due_date": str,
                "required_action": str,
                "ransomware_use": bool,  # "Known" -> True, "Unknown" -> False
                "vendor": str,
                "product": str,
                "vulnerability_name": str
            }
        """
        catalog = await self.fetch_kev_catalog()

        if catalog is None:
            return None

        vulnerabilities = catalog.get("vulnerabilities", [])

        # Normalize CVE ID for case-insensitive comparison
        cve_id_upper = cve_id.upper()

        for vuln in vulnerabilities:
            if vuln.get("cveID", "").upper() == cve_id_upper:
                return self._format_kev_entry(vuln)

        return None

    async def get_kev_for_cves(self, cve_ids: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Check multiple CVEs against the KEV catalog in a single API call.

        Args:
            cve_ids: List of CVE IDs to check

        Returns:
            Dict mapping CVE ID to KEV data (or None if not in catalog)
        """
        result = {cve_id: None for cve_id in cve_ids}

        catalog = await self.fetch_kev_catalog()

        if catalog is None:
            return result

        vulnerabilities = catalog.get("vulnerabilities", [])

        # Build a lookup dict for efficiency
        kev_lookup = {
            vuln.get("cveID", "").upper(): vuln
            for vuln in vulnerabilities
        }

        for cve_id in cve_ids:
            cve_id_upper = cve_id.upper()
            if cve_id_upper in kev_lookup:
                result[cve_id] = self._format_kev_entry(kev_lookup[cve_id_upper])

        return result

    def _format_kev_entry(self, vuln: Dict) -> Dict:
        """
        Format a raw KEV vulnerability entry into the standard response format.

        Args:
            vuln: Raw vulnerability dict from KEV API

        Returns:
            Formatted dict with standardized fields
        """
        ransomware_str = vuln.get("knownRansomwareCampaignUse", "Unknown")
        ransomware_use = ransomware_str == "Known"

        return {
            "is_kev": True,
            "date_added": vuln.get("dateAdded", ""),
            "due_date": vuln.get("dueDate", ""),
            "required_action": vuln.get("requiredAction", ""),
            "ransomware_use": ransomware_use,
            "vendor": vuln.get("vendorProject", ""),
            "product": vuln.get("product", ""),
            "vulnerability_name": vuln.get("vulnerabilityName", "")
        }
