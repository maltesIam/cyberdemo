"""
OpenCTI API Client (Synthetic/Mock).

OpenCTI (Open Cyber Threat Intelligence) is an open-source platform
for managing cyber threat intelligence. It uses STIX 2.1 format and
provides a GraphQL API.

This implementation is a synthetic/mock client for demo purposes,
as OpenCTI is typically self-hosted. It returns realistic STIX 2.1
formatted threat intelligence data for demonstration and testing.

API Documentation: https://docs.opencti.io/latest/deployment/connectors/
GraphQL API: https://docs.opencti.io/latest/development/api-usage/
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

import httpx


logger = logging.getLogger(__name__)

# Constants
DEFAULT_TIMEOUT = 30  # seconds


# =============================================================================
# Embedded Synthetic STIX 2.1 Data
# =============================================================================

# STIX Indicators - Malicious IP, domain, file hash patterns
SYNTHETIC_INDICATORS = [
    {
        "id": "indicator--abc123",
        "type": "indicator",
        "spec_version": "2.1",
        "name": "Cobalt Strike Beacon IP",
        "description": "Known Cobalt Strike C2 server IP address",
        "pattern": "[ipv4-addr:value = '185.174.137.70']",
        "pattern_type": "stix",
        "pattern_version": "2.1",
        "valid_from": "2024-01-15T00:00:00Z",
        "valid_until": "2025-01-15T00:00:00Z",
        "labels": ["malicious-activity", "c2", "cobalt-strike"],
        "confidence": 85,
        "kill_chain_phases": [
            {"kill_chain_name": "mitre-attack", "phase_name": "command-and-control"}
        ]
    },
    {
        "id": "indicator--def456",
        "type": "indicator",
        "spec_version": "2.1",
        "name": "APT28 Domain Indicator",
        "description": "Domain associated with APT28 phishing campaigns",
        "pattern": "[domain-name:value = 'mail-security-update.com']",
        "pattern_type": "stix",
        "pattern_version": "2.1",
        "valid_from": "2024-02-01T00:00:00Z",
        "valid_until": "2025-02-01T00:00:00Z",
        "labels": ["apt28", "phishing", "spearphishing"],
        "confidence": 90,
        "kill_chain_phases": [
            {"kill_chain_name": "mitre-attack", "phase_name": "initial-access"}
        ]
    },
    {
        "id": "indicator--ghi789",
        "type": "indicator",
        "spec_version": "2.1",
        "name": "Emotet Malware Hash",
        "description": "SHA256 hash of Emotet dropper variant",
        "pattern": "[file:hashes.'SHA-256' = '3a2b1c4d5e6f7890abcdef1234567890abcdef1234567890abcdef12345678']",
        "pattern_type": "stix",
        "pattern_version": "2.1",
        "valid_from": "2024-01-20T00:00:00Z",
        "valid_until": "2025-01-20T00:00:00Z",
        "labels": ["emotet", "malware", "trojan", "dropper"],
        "confidence": 95,
        "kill_chain_phases": [
            {"kill_chain_name": "mitre-attack", "phase_name": "execution"}
        ]
    },
    {
        "id": "indicator--jkl012",
        "type": "indicator",
        "spec_version": "2.1",
        "name": "Ransomware C2 IP",
        "description": "IP address associated with ransomware command and control",
        "pattern": "[ipv4-addr:value = '45.33.32.156']",
        "pattern_type": "stix",
        "pattern_version": "2.1",
        "valid_from": "2024-03-01T00:00:00Z",
        "valid_until": "2025-03-01T00:00:00Z",
        "labels": ["ransomware", "c2", "malicious-activity"],
        "confidence": 80,
        "kill_chain_phases": [
            {"kill_chain_name": "mitre-attack", "phase_name": "command-and-control"}
        ]
    },
    {
        "id": "indicator--mno345",
        "type": "indicator",
        "spec_version": "2.1",
        "name": "YARA Rule - Suspicious PowerShell",
        "description": "YARA rule detecting suspicious PowerShell execution patterns",
        "pattern": "rule SuspiciousPowershell { strings: $a = \"-encodedcommand\" nocase condition: $a }",
        "pattern_type": "yara",
        "pattern_version": "4.0",
        "valid_from": "2024-01-10T00:00:00Z",
        "valid_until": "2025-01-10T00:00:00Z",
        "labels": ["powershell", "execution", "suspicious"],
        "confidence": 70,
        "kill_chain_phases": [
            {"kill_chain_name": "mitre-attack", "phase_name": "execution"}
        ]
    },
    {
        "id": "indicator--pqr678",
        "type": "indicator",
        "spec_version": "2.1",
        "name": "Sigma Rule - Mimikatz Detection",
        "description": "Sigma rule for detecting Mimikatz credential dumping",
        "pattern": "title: Mimikatz Detection\nlogsource:\n  product: windows\n  service: security\ndetection:\n  selection:\n    CommandLine|contains: 'sekurlsa'",
        "pattern_type": "sigma",
        "pattern_version": "1.0",
        "valid_from": "2024-02-15T00:00:00Z",
        "valid_until": "2025-02-15T00:00:00Z",
        "labels": ["mimikatz", "credential-access", "detection"],
        "confidence": 85,
        "kill_chain_phases": [
            {"kill_chain_name": "mitre-attack", "phase_name": "credential-access"}
        ]
    },
    {
        "id": "indicator--stu901",
        "type": "indicator",
        "spec_version": "2.1",
        "name": "Snort Rule - SSH Brute Force",
        "description": "Snort rule detecting SSH brute force attempts",
        "pattern": "alert tcp any any -> any 22 (msg:\"SSH Brute Force Attempt\"; threshold: type both, track by_src, count 5, seconds 60; sid:1000001;)",
        "pattern_type": "snort",
        "pattern_version": "3.0",
        "valid_from": "2024-01-25T00:00:00Z",
        "valid_until": "2025-01-25T00:00:00Z",
        "labels": ["ssh", "brute-force", "network"],
        "confidence": 75,
        "kill_chain_phases": [
            {"kill_chain_name": "mitre-attack", "phase_name": "credential-access"}
        ]
    },
]

# STIX Threat Actors - APT Groups
SYNTHETIC_THREAT_ACTORS = [
    {
        "id": "threat-actor--apt28",
        "type": "threat-actor",
        "spec_version": "2.1",
        "name": "APT28",
        "description": "APT28 (also known as Fancy Bear, Sofacy, Pawn Storm, STRONTIUM) is a Russian cyber espionage group attributed to Russian military intelligence (GRU).",
        "aliases": ["Fancy Bear", "Sofacy", "Pawn Storm", "STRONTIUM", "Sednit", "Tsar Team"],
        "threat_actor_types": ["nation-state"],
        "sophistication": "advanced",
        "resource_level": "government",
        "primary_motivation": "organizational-gain",
        "goals": ["espionage", "data-theft", "disruption"],
        "roles": ["agent", "infrastructure-operator"],
        "first_seen": "2008-01-01T00:00:00Z",
        "last_seen": "2024-01-01T00:00:00Z",
        "labels": ["russia", "gru", "apt"]
    },
    {
        "id": "threat-actor--apt29",
        "type": "threat-actor",
        "spec_version": "2.1",
        "name": "APT29",
        "description": "APT29 (also known as Cozy Bear, The Dukes, NOBELIUM) is a Russian threat group attributed to Russian Foreign Intelligence Service (SVR).",
        "aliases": ["Cozy Bear", "The Dukes", "NOBELIUM", "Dark Halo", "YTTRIUM"],
        "threat_actor_types": ["nation-state"],
        "sophistication": "expert",
        "resource_level": "government",
        "primary_motivation": "organizational-gain",
        "goals": ["espionage", "intelligence-collection"],
        "roles": ["agent", "infrastructure-operator"],
        "first_seen": "2008-01-01T00:00:00Z",
        "last_seen": "2024-01-01T00:00:00Z",
        "labels": ["russia", "svr", "apt"]
    },
    {
        "id": "threat-actor--lazarus",
        "type": "threat-actor",
        "spec_version": "2.1",
        "name": "Lazarus Group",
        "description": "Lazarus Group (also known as Hidden Cobra, ZINC, Labyrinth Chollima) is a North Korean state-sponsored threat group.",
        "aliases": ["Hidden Cobra", "ZINC", "Labyrinth Chollima", "Guardians of Peace", "NICKEL ACADEMY"],
        "threat_actor_types": ["nation-state", "criminal"],
        "sophistication": "advanced",
        "resource_level": "government",
        "primary_motivation": "personal-gain",
        "goals": ["financial-theft", "espionage", "disruption"],
        "roles": ["agent", "malware-author"],
        "first_seen": "2009-01-01T00:00:00Z",
        "last_seen": "2024-01-01T00:00:00Z",
        "labels": ["north-korea", "dprk", "apt"]
    },
    {
        "id": "threat-actor--apt41",
        "type": "threat-actor",
        "spec_version": "2.1",
        "name": "APT41",
        "description": "APT41 (also known as Wicked Panda, BARIUM, Winnti) is a Chinese state-sponsored espionage group conducting financially motivated operations.",
        "aliases": ["Wicked Panda", "BARIUM", "Winnti", "Double Dragon"],
        "threat_actor_types": ["nation-state", "criminal"],
        "sophistication": "advanced",
        "resource_level": "government",
        "primary_motivation": "organizational-gain",
        "goals": ["espionage", "financial-theft", "intellectual-property-theft"],
        "roles": ["agent", "infrastructure-operator", "malware-author"],
        "first_seen": "2012-01-01T00:00:00Z",
        "last_seen": "2024-01-01T00:00:00Z",
        "labels": ["china", "apt"]
    },
    {
        "id": "threat-actor--fin7",
        "type": "threat-actor",
        "spec_version": "2.1",
        "name": "FIN7",
        "description": "FIN7 (also known as Carbanak, Carbon Spider) is a financially motivated threat group targeting the financial services sector.",
        "aliases": ["Carbanak", "Carbon Spider", "GOLD NIAGARA"],
        "threat_actor_types": ["criminal"],
        "sophistication": "advanced",
        "resource_level": "organization",
        "primary_motivation": "personal-gain",
        "goals": ["financial-theft", "data-theft"],
        "roles": ["agent", "infrastructure-operator", "malware-author"],
        "first_seen": "2013-01-01T00:00:00Z",
        "last_seen": "2024-01-01T00:00:00Z",
        "labels": ["financial", "cybercrime"]
    },
]

# STIX Relationships - Links between indicators and threat actors
SYNTHETIC_RELATIONSHIPS = [
    {
        "id": "relationship--001",
        "type": "relationship",
        "spec_version": "2.1",
        "relationship_type": "indicates",
        "source_ref": "indicator--abc123",
        "target_ref": "malware--cobalt-strike",
        "description": "This indicator detects Cobalt Strike C2 traffic",
        "start_time": "2024-01-15T00:00:00Z"
    },
    {
        "id": "relationship--002",
        "type": "relationship",
        "spec_version": "2.1",
        "relationship_type": "indicates",
        "source_ref": "indicator--def456",
        "target_ref": "threat-actor--apt28",
        "description": "This domain indicator is attributed to APT28",
        "start_time": "2024-02-01T00:00:00Z"
    },
    {
        "id": "relationship--003",
        "type": "relationship",
        "spec_version": "2.1",
        "relationship_type": "uses",
        "source_ref": "threat-actor--apt28",
        "target_ref": "malware--sofacy",
        "description": "APT28 uses Sofacy malware family",
        "start_time": "2015-01-01T00:00:00Z"
    },
    {
        "id": "relationship--004",
        "type": "relationship",
        "spec_version": "2.1",
        "relationship_type": "indicates",
        "source_ref": "indicator--ghi789",
        "target_ref": "malware--emotet",
        "description": "This hash indicates Emotet malware",
        "start_time": "2024-01-20T00:00:00Z"
    },
    {
        "id": "relationship--005",
        "type": "relationship",
        "spec_version": "2.1",
        "relationship_type": "attributed-to",
        "source_ref": "intrusion-set--apt28-campaign",
        "target_ref": "threat-actor--apt28",
        "description": "This campaign is attributed to APT28",
        "start_time": "2023-06-01T00:00:00Z"
    },
]


class OpenCTIClient:
    """
    Client for OpenCTI API (Synthetic/Mock).

    Provides access to STIX 2.1 threat intelligence data including
    indicators, threat actors, and relationships. Uses embedded
    synthetic data for demo purposes.

    In production, OpenCTI uses a GraphQL API with Bearer token authentication.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = DEFAULT_TIMEOUT
    ):
        """
        Initialize OpenCTI client.

        Args:
            base_url: OpenCTI instance URL (e.g., https://opencti.example.com).
            api_key: API key for authentication.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

        # Build lookup indexes for synthetic data
        self._indicators = {i["id"]: i for i in SYNTHETIC_INDICATORS}
        self._threat_actors = {a["id"]: a for a in SYNTHETIC_THREAT_ACTORS}
        self._relationships = SYNTHETIC_RELATIONSHIPS

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
        """Get authorization headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def _make_request(
        self,
        query: str,
        variables: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make GraphQL request to OpenCTI API.

        Args:
            query: GraphQL query string.
            variables: Optional query variables.

        Returns:
            Dict with response data on success, None on failure.
        """
        url = f"{self.base_url}/graphql"

        try:
            response = await self.client.post(
                url,
                headers=self._get_headers(),
                json={
                    "query": query,
                    "variables": variables or {}
                }
            )

            # Handle authentication errors
            if response.status_code == 401:
                logger.error("OpenCTI authentication failed - invalid API key")
                return None

            # Handle forbidden access
            if response.status_code == 403:
                logger.error("OpenCTI access forbidden")
                return None

            # Handle server errors
            if response.status_code >= 500:
                logger.error(f"OpenCTI server error: {response.status_code}")
                return None

            if response.status_code != 200:
                logger.error(f"OpenCTI API error: {response.status_code}")
                return None

            data = response.json()

            # Check for GraphQL errors
            if "errors" in data:
                logger.error(f"OpenCTI GraphQL errors: {data['errors']}")
                return None

            return data.get("data")

        except httpx.TimeoutException:
            logger.error(f"OpenCTI request timeout for {url}")
            return None

        except httpx.ConnectError as e:
            logger.error(f"OpenCTI connection error: {e}")
            return None

        except httpx.RequestError as e:
            logger.error(f"OpenCTI request error: {e}")
            return None

        except ValueError as e:
            logger.error(f"OpenCTI JSON parse error: {e}")
            return None

        except Exception as e:
            logger.error(f"OpenCTI unexpected error: {e}")
            return None

    async def search_indicators(
        self,
        query: str,
        pattern_type: Optional[str] = None,
        limit: int = 25
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Search for STIX indicators.

        This is a synthetic implementation that searches embedded demo data.
        In production, this would query the OpenCTI GraphQL API.

        Args:
            query: Search query string (searches name, description, pattern).
            pattern_type: Optional filter by pattern type (stix, yara, sigma, snort).
            limit: Maximum number of results to return.

        Returns:
            List of STIX indicator objects on success, None on API error.
        """
        query_lower = query.lower()

        # Filter indicators by query
        results = []
        for indicator in SYNTHETIC_INDICATORS:
            # Check if query matches name, description, or pattern
            name_match = query_lower in indicator["name"].lower()
            desc_match = query_lower in indicator.get("description", "").lower()
            pattern_match = query_lower in indicator.get("pattern", "").lower()
            label_match = any(query_lower in label for label in indicator.get("labels", []))

            if name_match or desc_match or pattern_match or label_match:
                # Filter by pattern_type if specified
                if pattern_type:
                    if indicator.get("pattern_type") != pattern_type:
                        continue

                results.append(indicator.copy())

        # Apply limit
        return results[:limit]

    async def get_indicator(
        self,
        indicator_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific STIX indicator.

        Args:
            indicator_id: STIX indicator ID (e.g., "indicator--abc123").

        Returns:
            STIX indicator object on success, None if not found.
        """
        return self._indicators.get(indicator_id)

    async def search_threat_actors(
        self,
        query: str,
        sophistication: Optional[str] = None,
        limit: int = 25
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Search for STIX threat actors.

        This is a synthetic implementation that searches embedded demo data.
        In production, this would query the OpenCTI GraphQL API.

        Args:
            query: Search query string (searches name, description, aliases).
            sophistication: Optional filter by sophistication level
                           (none, minimal, intermediate, advanced, expert).
            limit: Maximum number of results to return.

        Returns:
            List of STIX threat-actor objects on success.
        """
        query_lower = query.lower()

        results = []
        for actor in SYNTHETIC_THREAT_ACTORS:
            # Check if query matches name, description, or aliases
            name_match = query_lower in actor["name"].lower()
            desc_match = query_lower in actor.get("description", "").lower()
            alias_match = any(
                query_lower in alias.lower()
                for alias in actor.get("aliases", [])
            )
            label_match = any(
                query_lower in label
                for label in actor.get("labels", [])
            )

            # Empty query matches all
            if query == "" or name_match or desc_match or alias_match or label_match:
                # Filter by sophistication if specified
                if sophistication:
                    if actor.get("sophistication") != sophistication:
                        continue

                results.append(actor.copy())

        return results[:limit]

    async def get_threat_actor(
        self,
        threat_actor_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific STIX threat actor.

        Args:
            threat_actor_id: STIX threat-actor ID (e.g., "threat-actor--apt28").

        Returns:
            STIX threat-actor object on success, None if not found.
        """
        return self._threat_actors.get(threat_actor_id)

    async def get_relationships(
        self,
        entity_id: str,
        relationship_type: Optional[str] = None,
        limit: int = 50
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get STIX relationships for an entity.

        Args:
            entity_id: STIX entity ID to find relationships for.
            relationship_type: Optional filter by relationship type
                              (indicates, uses, attributed-to, etc.).
            limit: Maximum number of results to return.

        Returns:
            List of STIX relationship objects.
        """
        results = []

        for rel in self._relationships:
            # Check if entity is source or target of relationship
            if rel["source_ref"] == entity_id or rel["target_ref"] == entity_id:
                # Filter by relationship_type if specified
                if relationship_type:
                    if rel.get("relationship_type") != relationship_type:
                        continue

                results.append(rel.copy())

        return results[:limit]
