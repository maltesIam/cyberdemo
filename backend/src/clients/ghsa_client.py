"""
GitHub Security Advisories (GHSA) API Client.

GHSA provides vulnerability advisories via GitHub's GraphQL API.

API Documentation: https://docs.github.com/en/graphql/reference/objects#securityadvisory
Rate limit: 5000 points/hour (GraphQL)
"""

import logging
from typing import Optional, Dict, List

import httpx


logger = logging.getLogger(__name__)

# Constants
GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
DEFAULT_TIMEOUT = 30  # seconds


# GraphQL Queries
FETCH_ADVISORY_QUERY = """
query($ghsaId: String!) {
    securityAdvisory(ghsaId: $ghsaId) {
        ghsaId
        summary
        severity
        publishedAt
        identifiers {
            type
            value
        }
        vulnerabilities(first: 100) {
            nodes {
                package {
                    ecosystem
                    name
                }
                vulnerableVersionRange
                firstPatchedVersion {
                    identifier
                }
            }
        }
    }
}
"""

SEARCH_BY_CVE_QUERY = """
query($identifier: String!) {
    securityAdvisories(first: 100, identifier: {type: CVE, value: $identifier}) {
        nodes {
            ghsaId
            summary
            severity
            publishedAt
            identifiers {
                type
                value
            }
            vulnerabilities(first: 100) {
                nodes {
                    package {
                        ecosystem
                        name
                    }
                    vulnerableVersionRange
                    firstPatchedVersion {
                        identifier
                    }
                }
            }
        }
        pageInfo {
            hasNextPage
            endCursor
        }
    }
}
"""

SEARCH_BY_PACKAGE_QUERY = """
query($ecosystem: SecurityAdvisoryEcosystem!, $package: String!) {
    securityVulnerabilities(first: 100, ecosystem: $ecosystem, package: $package) {
        nodes {
            advisory {
                ghsaId
                summary
                severity
                publishedAt
                identifiers {
                    type
                    value
                }
            }
            package {
                ecosystem
                name
            }
            vulnerableVersionRange
            firstPatchedVersion {
                identifier
            }
        }
        pageInfo {
            hasNextPage
            endCursor
        }
    }
}
"""

# Ecosystem mapping (lowercase to GraphQL enum)
ECOSYSTEM_MAP = {
    "npm": "NPM",
    "pip": "PIP",
    "pypi": "PIP",
    "maven": "MAVEN",
    "nuget": "NUGET",
    "rubygems": "RUBYGEMS",
    "composer": "COMPOSER",
    "go": "GO",
    "rust": "RUST",
    "actions": "ACTIONS",
    "erlang": "ERLANG",
    "pub": "PUB",
    "swift": "SWIFT",
}

# Synthetic data for demo mode (no token)
SYNTHETIC_ADVISORIES = {
    "GHSA-jfhm-5ghh-2f97": {
        "ghsa_id": "GHSA-jfhm-5ghh-2f97",
        "cve_id": "CVE-2020-8203",
        "summary": "Prototype Pollution in lodash",
        "severity": "HIGH",
        "published_at": "2020-07-15T00:00:00Z",
        "affected_packages": [
            {
                "ecosystem": "npm",
                "package_name": "lodash",
                "vulnerable_versions": "< 4.17.20",
                "patched_version": "4.17.20"
            }
        ]
    },
    "GHSA-jf85-cpcp-j695": {
        "ghsa_id": "GHSA-jf85-cpcp-j695",
        "cve_id": "CVE-2021-44228",
        "summary": "Remote code injection in Log4j",
        "severity": "CRITICAL",
        "published_at": "2021-12-10T00:00:00Z",
        "affected_packages": [
            {
                "ecosystem": "maven",
                "package_name": "org.apache.logging.log4j:log4j-core",
                "vulnerable_versions": "< 2.17.0",
                "patched_version": "2.17.0"
            }
        ]
    },
    "GHSA-35jh-r3h4-6jhm": {
        "ghsa_id": "GHSA-35jh-r3h4-6jhm",
        "cve_id": "CVE-2019-10744",
        "summary": "Prototype Pollution in lodash",
        "severity": "CRITICAL",
        "published_at": "2019-07-10T00:00:00Z",
        "affected_packages": [
            {
                "ecosystem": "npm",
                "package_name": "lodash",
                "vulnerable_versions": "< 4.17.12",
                "patched_version": "4.17.12"
            }
        ]
    },
}

# CVE to GHSA mapping for synthetic data
CVE_TO_GHSA = {
    "CVE-2020-8203": ["GHSA-jfhm-5ghh-2f97"],
    "CVE-2021-44228": ["GHSA-jf85-cpcp-j695"],
    "CVE-2019-10744": ["GHSA-35jh-r3h4-6jhm"],
}


class GHSAClient:
    """
    Client for GitHub Security Advisories (GHSA) GraphQL API.

    Provides vulnerability advisory information for open-source packages.
    Requires a GitHub token for API access. Without a token, returns synthetic demo data.
    """

    def __init__(self, token: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize GHSA client.

        Args:
            token: GitHub personal access token (optional). If not provided, synthetic data is used.
            timeout: Request timeout in seconds.
        """
        self.token = token
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

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authorization."""
        headers = {
            "Content-Type": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def _make_graphql_request(self, query: str, variables: Dict) -> Optional[Dict]:
        """
        Make GraphQL request to GitHub API.

        Args:
            query: GraphQL query string.
            variables: Query variables.

        Returns:
            Dict with response data on success, None on failure.
        """
        try:
            response = await self.client.post(
                GITHUB_GRAPHQL_URL,
                headers=self._get_headers(),
                json={"query": query, "variables": variables}
            )

            # Handle authentication errors
            if response.status_code == 401:
                logger.error("GHSA API authentication failed - invalid token")
                return None

            # Handle rate limiting
            if response.status_code == 403:
                logger.warning("GHSA API rate limit exceeded or forbidden")
                return None

            # Handle server errors
            if response.status_code >= 500:
                logger.error(f"GHSA API server error: {response.status_code}")
                return None

            if response.status_code != 200:
                logger.error(f"GHSA API error: {response.status_code}")
                return None

            data = response.json()

            # Check for GraphQL errors
            if "errors" in data and data["errors"]:
                logger.warning(f"GHSA GraphQL errors: {data['errors']}")
                # Continue processing if data is present
                if "data" not in data or data["data"] is None:
                    return None

            return data.get("data")

        except httpx.TimeoutException:
            logger.error("GHSA request timeout")
            return None

        except httpx.ConnectError as e:
            logger.error(f"GHSA connection error: {e}")
            return None

        except httpx.RequestError as e:
            logger.error(f"GHSA request error: {e}")
            return None

        except ValueError as e:
            logger.error(f"GHSA JSON parse error: {e}")
            return None

        except Exception as e:
            logger.error(f"GHSA unexpected error: {e}")
            return None

    def _parse_advisory(self, advisory_data: Dict) -> Dict:
        """
        Parse advisory data into standardized format.

        Args:
            advisory_data: Raw advisory data from API.

        Returns:
            Standardized advisory dict.
        """
        # Extract CVE ID from identifiers
        cve_id = None
        identifiers = advisory_data.get("identifiers", [])
        for identifier in identifiers:
            if identifier.get("type") == "CVE":
                cve_id = identifier.get("value")
                break

        # Parse affected packages
        affected_packages = []
        vulnerabilities = advisory_data.get("vulnerabilities", {})
        nodes = vulnerabilities.get("nodes", []) if vulnerabilities else []

        for vuln in nodes:
            package = vuln.get("package", {})
            ecosystem = package.get("ecosystem", "").lower()
            package_name = package.get("name", "")
            vulnerable_versions = vuln.get("vulnerableVersionRange", "")
            first_patched = vuln.get("firstPatchedVersion")
            patched_version = first_patched.get("identifier") if first_patched else None

            affected_packages.append({
                "ecosystem": ecosystem,
                "package_name": package_name,
                "vulnerable_versions": vulnerable_versions,
                "patched_version": patched_version
            })

        return {
            "ghsa_id": advisory_data.get("ghsaId"),
            "cve_id": cve_id,
            "summary": advisory_data.get("summary"),
            "severity": advisory_data.get("severity"),
            "published_at": advisory_data.get("publishedAt"),
            "affected_packages": affected_packages
        }

    def _parse_vulnerability_node(self, vuln_node: Dict) -> Dict:
        """
        Parse a securityVulnerabilities node (from package search).

        Args:
            vuln_node: Vulnerability node from API.

        Returns:
            Standardized advisory dict with single affected package.
        """
        advisory = vuln_node.get("advisory", {})

        # Extract CVE ID
        cve_id = None
        identifiers = advisory.get("identifiers", [])
        for identifier in identifiers:
            if identifier.get("type") == "CVE":
                cve_id = identifier.get("value")
                break

        # Parse the single affected package
        package = vuln_node.get("package", {})
        ecosystem = package.get("ecosystem", "").lower()
        package_name = package.get("name", "")
        vulnerable_versions = vuln_node.get("vulnerableVersionRange", "")
        first_patched = vuln_node.get("firstPatchedVersion")
        patched_version = first_patched.get("identifier") if first_patched else None

        return {
            "ghsa_id": advisory.get("ghsaId"),
            "cve_id": cve_id,
            "summary": advisory.get("summary"),
            "severity": advisory.get("severity"),
            "published_at": advisory.get("publishedAt"),
            "affected_packages": [{
                "ecosystem": ecosystem,
                "package_name": package_name,
                "vulnerable_versions": vulnerable_versions,
                "patched_version": patched_version
            }]
        }

    async def fetch_advisory(self, ghsa_id: str) -> Optional[Dict]:
        """
        Fetch a specific advisory by GHSA ID.

        Args:
            ghsa_id: The GHSA identifier (e.g., "GHSA-jfhm-5ghh-2f97").

        Returns:
            Dict with advisory data on success, None if not found or error.
            Structure:
            {
                "ghsa_id": "GHSA-xxxx-yyyy-zzzz",
                "cve_id": "CVE-2024-0001" | None,
                "summary": "...",
                "severity": "CRITICAL" | "HIGH" | "MODERATE" | "LOW",
                "published_at": "2024-01-15T00:00:00Z",
                "affected_packages": [
                    {
                        "ecosystem": "npm",
                        "package_name": "lodash",
                        "vulnerable_versions": "<4.17.21",
                        "patched_version": "4.17.21" | None
                    }
                ]
            }
        """
        # Return synthetic data if no token
        if not self.token:
            return SYNTHETIC_ADVISORIES.get(ghsa_id)

        data = await self._make_graphql_request(
            FETCH_ADVISORY_QUERY,
            {"ghsaId": ghsa_id}
        )

        if not data:
            return None

        advisory = data.get("securityAdvisory")
        if not advisory:
            return None

        return self._parse_advisory(advisory)

    async def search_by_cve(self, cve_id: str) -> List[Dict]:
        """
        Search for advisories by CVE ID.

        Args:
            cve_id: The CVE identifier (e.g., "CVE-2021-44228").

        Returns:
            List of advisory dicts matching the CVE.
        """
        # Return synthetic data if no token
        if not self.token:
            ghsa_ids = CVE_TO_GHSA.get(cve_id, [])
            return [SYNTHETIC_ADVISORIES[ghsa_id] for ghsa_id in ghsa_ids if ghsa_id in SYNTHETIC_ADVISORIES]

        data = await self._make_graphql_request(
            SEARCH_BY_CVE_QUERY,
            {"identifier": cve_id}
        )

        if not data:
            return []

        advisories_data = data.get("securityAdvisories", {})
        nodes = advisories_data.get("nodes", []) if advisories_data else []

        return [self._parse_advisory(advisory) for advisory in nodes]

    async def search_by_package(self, ecosystem: str, package: str) -> List[Dict]:
        """
        Search for advisories affecting a specific package.

        Args:
            ecosystem: Package ecosystem (e.g., "npm", "pip", "maven").
            package: Package name.

        Returns:
            List of advisory dicts affecting the package.
        """
        # Return synthetic data if no token
        if not self.token:
            results = []
            for advisory in SYNTHETIC_ADVISORIES.values():
                for pkg in advisory.get("affected_packages", []):
                    if pkg["ecosystem"].lower() == ecosystem.lower() and pkg["package_name"].lower() == package.lower():
                        results.append(advisory)
                        break
            return results

        # Map ecosystem to GraphQL enum
        ecosystem_upper = ECOSYSTEM_MAP.get(ecosystem.lower(), ecosystem.upper())

        data = await self._make_graphql_request(
            SEARCH_BY_PACKAGE_QUERY,
            {"ecosystem": ecosystem_upper, "package": package}
        )

        if not data:
            return []

        vulnerabilities = data.get("securityVulnerabilities", {})
        nodes = vulnerabilities.get("nodes", []) if vulnerabilities else []

        return [self._parse_vulnerability_node(vuln) for vuln in nodes]
