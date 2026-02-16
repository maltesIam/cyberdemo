"""
MISP API Client.

MISP (Malware Information Sharing Platform) is a threat intelligence sharing platform
that allows organizations to share, store, and correlate Indicators of Compromise (IOCs).

Since MISP is typically self-hosted, this client includes synthetic data generation
for demo mode when no real MISP instance is available.

API Documentation: https://www.misp-project.org/openapi/
Rate limit: Depends on instance configuration
"""

import logging
import random
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List

import httpx


logger = logging.getLogger(__name__)

# Constants
DEFAULT_TIMEOUT = 30  # seconds


class MISPClient:
    """
    Client for MISP API.

    Provides threat event search, attribute search, event details,
    and correlation lookups for threat intelligence sharing.

    Supports demo mode for synthetic data generation when no real
    MISP instance is available.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = DEFAULT_TIMEOUT,
        demo_mode: bool = False
    ):
        """
        Initialize MISP client.

        Args:
            base_url: Base URL of the MISP instance (e.g., "https://misp.example.org").
            api_key: MISP API key for authentication.
            timeout: Request timeout in seconds.
            demo_mode: If True, generate synthetic data instead of making API calls.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.demo_mode = demo_mode
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for MISP API requests."""
        return {
            "Authorization": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    async def search_events(self, query: str) -> Optional[Dict]:
        """
        Search for MISP events matching a query.

        Args:
            query: Search term to find in event info, tags, or attributes.

        Returns:
            Dict with event data on success, None on failure.
            Dict structure:
            {
                "response": [
                    {
                        "Event": {
                            "id": str,
                            "uuid": str,
                            "info": str,
                            "date": str,
                            "threat_level_id": str,
                            "analysis": str,
                            "distribution": str,
                            "published": bool,
                            "timestamp": str,
                            "attribute_count": str,
                            "Tag": [{"name": str}]
                        }
                    }
                ]
            }
        """
        if self.demo_mode:
            return self._generate_synthetic_events(query)

        url = f"{self.base_url}/events/restSearch"
        payload = {
            "returnFormat": "json",
            "value": query,
            "searchall": True
        }

        return await self._make_post_request(url, payload, f"search events for '{query}'")

    async def search_attributes(self, type: str, value: str) -> Optional[Dict]:
        """
        Search for MISP attributes by type and value.

        Args:
            type: Attribute type (e.g., "ip-dst", "domain", "md5", "sha256").
            value: Attribute value to search for.

        Returns:
            Dict with attribute data on success, None on failure.
            Dict structure:
            {
                "response": {
                    "Attribute": [
                        {
                            "id": str,
                            "event_id": str,
                            "category": str,
                            "type": str,
                            "value": str,
                            "to_ids": bool,
                            "timestamp": str,
                            "comment": str,
                            "Event": {
                                "id": str,
                                "info": str,
                                "org_id": str
                            }
                        }
                    ]
                }
            }
        """
        if self.demo_mode:
            return self._generate_synthetic_attributes(type, value)

        url = f"{self.base_url}/attributes/restSearch"
        payload = {
            "returnFormat": "json",
            "type": type,
            "value": value
        }

        return await self._make_post_request(url, payload, f"search attributes type={type} value={value}")

    async def get_event(self, event_id: str) -> Optional[Dict]:
        """
        Get detailed information for a specific MISP event.

        Args:
            event_id: The MISP event ID.

        Returns:
            Dict with full event data on success, None on failure.
            Dict structure:
            {
                "Event": {
                    "id": str,
                    "uuid": str,
                    "info": str,
                    "date": str,
                    "threat_level_id": str,
                    "analysis": str,
                    "distribution": str,
                    "published": bool,
                    "Org": {"id": str, "name": str},
                    "Orgc": {"id": str, "name": str},
                    "Attribute": [...],
                    "Tag": [...],
                    "Galaxy": [...]
                }
            }
        """
        if self.demo_mode:
            return self._generate_synthetic_event_detail(event_id)

        url = f"{self.base_url}/events/view/{event_id}"

        return await self._make_get_request(url, f"get event {event_id}")

    async def get_correlations(self, indicator: str) -> Optional[Dict]:
        """
        Get correlated indicators for a given indicator value.

        Args:
            indicator: The indicator value to find correlations for.

        Returns:
            Dict with correlation data on success, None on failure.
            Dict structure:
            {
                "response": [
                    {
                        "Attribute": {
                            "id": str,
                            "type": str,
                            "value": str,
                            "event_id": str
                        },
                        "RelatedAttribute": [
                            {
                                "id": str,
                                "type": str,
                                "value": str,
                                "event_id": str,
                                "Event": {"id": str, "info": str}
                            }
                        ]
                    }
                ]
            }
        """
        if self.demo_mode:
            return self._generate_synthetic_correlations(indicator)

        url = f"{self.base_url}/attributes/restSearch"
        payload = {
            "returnFormat": "json",
            "value": indicator,
            "includeCorrelations": True
        }

        return await self._make_post_request(url, payload, f"get correlations for '{indicator}'")

    async def _make_post_request(self, url: str, payload: Dict, context: str) -> Optional[Dict]:
        """
        Make a POST request to the MISP API.

        Args:
            url: The API endpoint URL.
            payload: The JSON payload to send.
            context: Context string for logging.

        Returns:
            Dict with API response on success, None on error.
        """
        try:
            response = await self.client.post(
                url,
                json=payload,
                headers=self._get_headers()
            )

            # Handle auth errors
            if response.status_code in (401, 403):
                logger.error(f"MISP API authentication error for {context}: HTTP {response.status_code}")
                return None

            # Handle not found
            if response.status_code == 404:
                logger.info(f"MISP resource not found for {context}")
                return None

            # Handle other non-200 status codes
            if response.status_code != 200:
                logger.error(f"MISP API error for {context}: HTTP {response.status_code}")
                return None

            return response.json()

        except httpx.TimeoutException:
            logger.error(f"Timeout fetching MISP data for {context}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching MISP data for {context}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching MISP data for {context}: {e}")
            return None

    async def _make_get_request(self, url: str, context: str) -> Optional[Dict]:
        """
        Make a GET request to the MISP API.

        Args:
            url: The API endpoint URL.
            context: Context string for logging.

        Returns:
            Dict with API response on success, None on error.
        """
        try:
            response = await self.client.get(
                url,
                headers=self._get_headers()
            )

            # Handle auth errors
            if response.status_code in (401, 403):
                logger.error(f"MISP API authentication error for {context}: HTTP {response.status_code}")
                return None

            # Handle not found
            if response.status_code == 404:
                logger.info(f"MISP resource not found for {context}")
                return None

            # Handle other non-200 status codes
            if response.status_code != 200:
                logger.error(f"MISP API error for {context}: HTTP {response.status_code}")
                return None

            return response.json()

        except httpx.TimeoutException:
            logger.error(f"Timeout fetching MISP data for {context}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error fetching MISP data for {context}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching MISP data for {context}: {e}")
            return None

    # Synthetic data generation methods for demo mode

    def _generate_synthetic_events(self, query: str) -> Dict:
        """Generate synthetic MISP events for demo mode."""
        threat_actors = [
            "APT29", "APT28", "Lazarus Group", "FIN7", "Sandworm",
            "Cozy Bear", "Fancy Bear", "Turla", "Carbanak", "MuddyWater"
        ]

        campaign_types = [
            "Phishing Campaign", "Ransomware Attack", "Supply Chain Compromise",
            "Credential Harvesting", "Data Exfiltration", "Espionage Operation",
            "DDoS Campaign", "Malware Distribution"
        ]

        tags = [
            "tlp:amber", "tlp:green", "tlp:red", "tlp:white",
            "apt", "ransomware", "phishing", "malware", "c2",
            "initial-access", "lateral-movement", "exfiltration"
        ]

        events = []
        num_events = random.randint(1, 5)

        for i in range(num_events):
            threat_actor = random.choice(threat_actors)
            campaign_type = random.choice(campaign_types)
            event_date = datetime.now() - timedelta(days=random.randint(1, 365))

            event_tags = random.sample(tags, random.randint(2, 5))
            if query.lower() in [t.lower() for t in threat_actors]:
                event_tags.append(query.lower())

            events.append({
                "Event": {
                    "id": str(10000 + i),
                    "uuid": str(uuid.uuid4()),
                    "info": f"{threat_actor} {campaign_type} - {query}",
                    "date": event_date.strftime("%Y-%m-%d"),
                    "threat_level_id": str(random.randint(1, 4)),
                    "analysis": str(random.randint(0, 2)),
                    "distribution": str(random.randint(0, 3)),
                    "org_id": "1",
                    "orgc_id": "1",
                    "published": random.choice([True, False]),
                    "timestamp": str(int(event_date.timestamp())),
                    "attribute_count": str(random.randint(5, 50)),
                    "Tag": [{"name": tag} for tag in event_tags]
                }
            })

        return {"response": events}

    def _generate_synthetic_attributes(self, type: str, value: str) -> Dict:
        """Generate synthetic MISP attributes for demo mode."""
        categories = {
            "ip-dst": "Network activity",
            "ip-src": "Network activity",
            "domain": "Network activity",
            "url": "Network activity",
            "md5": "Payload delivery",
            "sha256": "Payload delivery",
            "sha1": "Payload delivery",
            "filename": "Payload delivery",
            "email-src": "Payload delivery",
            "email-dst": "Payload delivery"
        }

        category = categories.get(type, "External analysis")

        attributes = []
        num_attrs = random.randint(1, 3)

        for i in range(num_attrs):
            event_id = str(10000 + random.randint(0, 100))
            attributes.append({
                "id": str(60000 + i),
                "event_id": event_id,
                "category": category,
                "type": type,
                "value": value,
                "to_ids": random.choice([True, False]),
                "timestamp": str(int(datetime.now().timestamp())),
                "comment": f"Detected in threat intelligence feed - {type}",
                "Event": {
                    "id": event_id,
                    "info": f"Malicious activity involving {type}",
                    "org_id": "1"
                }
            })

        return {"response": {"Attribute": attributes}}

    def _generate_synthetic_event_detail(self, event_id: str) -> Dict:
        """Generate synthetic MISP event details for demo mode."""
        threat_actors = ["APT29", "APT28", "Lazarus Group", "FIN7"]
        threat_actor = random.choice(threat_actors)

        event_date = datetime.now() - timedelta(days=random.randint(1, 180))

        attributes = [
            {
                "id": "67890",
                "type": "ip-dst",
                "category": "Network activity",
                "value": f"185.141.63.{random.randint(1, 255)}",
                "to_ids": True,
                "comment": "C2 server"
            },
            {
                "id": "67891",
                "type": "md5",
                "category": "Payload delivery",
                "value": f"{random.randbytes(16).hex()}",
                "to_ids": True,
                "comment": "Malware sample hash"
            },
            {
                "id": "67892",
                "type": "domain",
                "category": "Network activity",
                "value": f"malware{random.randint(1, 999)}.example.com",
                "to_ids": True,
                "comment": "Malicious domain"
            },
            {
                "id": "67893",
                "type": "sha256",
                "category": "Payload delivery",
                "value": f"{random.randbytes(32).hex()}",
                "to_ids": True,
                "comment": "Payload hash"
            }
        ]

        tags = [
            {"name": "tlp:amber"},
            {"name": threat_actor.lower().replace(" ", "-")},
            {"name": "misp-galaxy:mitre-attack-pattern=\"Spearphishing Attachment - T1566.001\""},
            {"name": "apt"},
            {"name": "malware"}
        ]

        galaxies = [
            {
                "name": "MITRE ATT&CK - Attack Pattern",
                "type": "mitre-attack-pattern",
                "GalaxyCluster": [
                    {
                        "value": "Spearphishing Attachment - T1566.001",
                        "description": "Adversaries may send spearphishing emails with a malicious attachment."
                    },
                    {
                        "value": "Command and Scripting Interpreter - T1059",
                        "description": "Adversaries may abuse command and script interpreters."
                    }
                ]
            },
            {
                "name": "Threat Actor",
                "type": "threat-actor",
                "GalaxyCluster": [
                    {
                        "value": threat_actor,
                        "description": f"Advanced persistent threat group known as {threat_actor}."
                    }
                ]
            }
        ]

        return {
            "Event": {
                "id": event_id,
                "uuid": str(uuid.uuid4()),
                "info": f"{threat_actor} Campaign - Targeting Critical Infrastructure",
                "date": event_date.strftime("%Y-%m-%d"),
                "threat_level_id": "1",
                "analysis": "2",
                "distribution": "1",
                "published": True,
                "timestamp": str(int(event_date.timestamp())),
                "Org": {
                    "id": "1",
                    "name": "CIRCL"
                },
                "Orgc": {
                    "id": "1",
                    "name": "CIRCL"
                },
                "Attribute": attributes,
                "Tag": tags,
                "Galaxy": galaxies
            }
        }

    def _generate_synthetic_correlations(self, indicator: str) -> Dict:
        """Generate synthetic MISP correlations for demo mode."""
        related_ips = [
            f"185.141.63.{random.randint(1, 255)}",
            f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            f"10.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        ]

        related_domains = [
            f"malware{random.randint(1, 999)}.example.com",
            f"c2-server{random.randint(1, 999)}.net",
            f"phishing{random.randint(1, 999)}.org"
        ]

        event_names = [
            "Related APT activity",
            "Malware distribution network",
            "Credential harvesting campaign",
            "C2 infrastructure"
        ]

        related_attributes = []

        # Add related IPs
        for ip in related_ips[:2]:
            event_id = str(10000 + random.randint(0, 100))
            related_attributes.append({
                "id": str(70000 + len(related_attributes)),
                "type": "ip-dst",
                "value": ip,
                "event_id": event_id,
                "Event": {
                    "id": event_id,
                    "info": random.choice(event_names)
                }
            })

        # Add related domains
        for domain in related_domains[:2]:
            event_id = str(10000 + random.randint(0, 100))
            related_attributes.append({
                "id": str(70000 + len(related_attributes)),
                "type": "domain",
                "value": domain,
                "event_id": event_id,
                "Event": {
                    "id": event_id,
                    "info": random.choice(event_names)
                }
            })

        return {
            "response": [
                {
                    "Attribute": {
                        "id": "67890",
                        "type": "ip-dst",
                        "value": indicator,
                        "event_id": "12345"
                    },
                    "RelatedAttribute": related_attributes
                }
            ]
        }
