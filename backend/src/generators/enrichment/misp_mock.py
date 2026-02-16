"""MISP (Malware Information Sharing Platform) mock generator.

Simulates MISP event and attribute data for threat intelligence integration:
- Event structures with threat levels
- TLP (Traffic Light Protocol) tags
- IOC attributes (IP, domain, hash, URL)
- Organization metadata
"""

import random
import uuid as uuid_lib
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional


class MISPMock:
    """Simulates MISP threat intelligence data."""

    def __init__(self, seed: int = None):
        """Initialize the mock generator.

        Args:
            seed: Random seed for reproducibility
        """
        self._seed = seed
        if seed is not None:
            random.seed(seed)

        # MISP threat levels: 1=High, 2=Medium, 3=Low, 4=Undefined
        self._threat_level_names = {
            1: "High",
            2: "Medium",
            3: "Low",
            4: "Undefined"
        }

        # TLP levels
        self._tlp_levels = ["tlp:white", "tlp:green", "tlp:amber", "tlp:red"]

        # Threat categories
        self._threat_categories = [
            "APT", "Ransomware", "Phishing", "Botnet", "C2",
            "Malware", "Exploit", "Data Breach", "Reconnaissance"
        ]

        # Organization names for mock data
        self._organizations = [
            "CIRCL", "CERT-EU", "MISP Community", "Threat Intel Hub",
            "SecOps Team", "SOC Analysis", "Incident Response",
            "Threat Research Lab", "CyberDefense Center"
        ]

        # Attribute categories mapping
        self._category_map = {
            "ip": "Network activity",
            "domain": "Network activity",
            "hash": "Payload delivery",
            "url": "External analysis"
        }

        # Attribute type mapping - first item is primary (always used for primary indicator)
        self._type_map = {
            "ip": ["ip-src", "ip-dst"],
            "domain": ["domain", "hostname"],
            "hash": ["md5", "sha1", "sha256"],
            "url": ["url", "link"]
        }

        # Primary type for each indicator type (deterministic for tests)
        self._primary_type_map = {
            "ip": "ip-src",
            "domain": "domain",
            "hash": "md5",
            "url": "url"
        }

    def generate_events(
        self,
        indicator_type: str,
        indicator_value: str,
        threat_level: int = 2
    ) -> List[Dict[str, Any]]:
        """Generate MISP-style events for an indicator.

        Args:
            indicator_type: Type of IOC (ip, domain, hash, url)
            indicator_value: The indicator value
            threat_level: MISP threat level (1=High, 2=Medium, 3=Low, 4=Undefined)

        Returns:
            List of MISP event dictionaries with:
            - event_id, uuid, info, threat_level_id
            - date, timestamp, published
            - orgc (organization creator)
            - tags (TLP, threat type)
            - attributes (the indicators)
        """
        # Validate threat level
        if threat_level < 1 or threat_level > 4:
            threat_level = 2  # Default to Medium

        # Generate 1-3 events
        num_events = random.randint(1, 3)
        events = []

        for i in range(num_events):
            event = self._generate_single_event(
                indicator_type=indicator_type,
                indicator_value=indicator_value,
                threat_level=threat_level,
                event_index=i
            )
            events.append(event)

        return events

    def generate_attributes(
        self,
        indicator_type: str,
        indicator_value: str
    ) -> List[Dict[str, Any]]:
        """Generate MISP attributes for an indicator.

        Args:
            indicator_type: Type of IOC (ip, domain, hash, url)
            indicator_value: The indicator value

        Returns:
            List of MISP attribute dictionaries
        """
        attributes = []

        # Primary attribute with the input indicator
        primary_attr = self._create_attribute(
            indicator_type=indicator_type,
            indicator_value=indicator_value,
            is_primary=True
        )
        attributes.append(primary_attr)

        # Add 0-2 related attributes
        num_related = random.randint(0, 2)
        for _ in range(num_related):
            related_type = random.choice(["ip", "domain", "hash", "url"])
            related_value = self._generate_related_indicator(related_type)
            related_attr = self._create_attribute(
                indicator_type=related_type,
                indicator_value=related_value,
                is_primary=False
            )
            attributes.append(related_attr)

        return attributes

    def _generate_single_event(
        self,
        indicator_type: str,
        indicator_value: str,
        threat_level: int,
        event_index: int
    ) -> Dict[str, Any]:
        """Generate a single MISP event.

        Args:
            indicator_type: Type of IOC
            indicator_value: The indicator value
            threat_level: MISP threat level
            event_index: Index for unique ID generation

        Returns:
            MISP event dictionary
        """
        # Generate event metadata
        event_uuid = str(uuid_lib.uuid4())
        event_id = random.randint(10000, 99999)

        # Generate timestamp and date
        days_ago = random.randint(0, 30)
        event_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
        timestamp = int(event_date.timestamp())

        # Generate event info (descriptive title)
        threat_category = random.choice(self._threat_categories)
        event_info = self._generate_event_info(
            indicator_type=indicator_type,
            indicator_value=indicator_value,
            threat_category=threat_category
        )

        # Generate organization
        orgc = self._generate_organization()

        # Generate tags
        tags = self._generate_tags(threat_level, threat_category)

        # Generate attributes
        attributes = self.generate_attributes(indicator_type, indicator_value)

        return {
            "event_id": event_id,
            "uuid": event_uuid,
            "info": event_info,
            "threat_level_id": threat_level,
            "date": event_date.strftime("%Y-%m-%d"),
            "timestamp": str(timestamp),
            "published": random.choice([True, True, True, False]),  # 75% published
            "orgc": orgc,
            "tags": tags,
            "attributes": attributes,
            "analysis": random.randint(0, 2),  # 0=Initial, 1=Ongoing, 2=Complete
            "distribution": random.randint(0, 3),
            "enrichment_source": "synthetic_misp",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    def _create_attribute(
        self,
        indicator_type: str,
        indicator_value: str,
        is_primary: bool
    ) -> Dict[str, Any]:
        """Create a MISP attribute.

        Args:
            indicator_type: Type of IOC
            indicator_value: The indicator value
            is_primary: Whether this is the primary indicator

        Returns:
            MISP attribute dictionary
        """
        # Get category and type
        category = self._category_map.get(indicator_type, "External analysis")

        # Primary indicators get deterministic type, related get random
        if is_primary:
            attr_type = self._primary_type_map.get(indicator_type, "other")
        else:
            attr_types = self._type_map.get(indicator_type, ["other"])
            attr_type = random.choice(attr_types)

        return {
            "uuid": str(uuid_lib.uuid4()),
            "type": attr_type,
            "category": category,
            "value": indicator_value,
            "to_ids": is_primary,  # Primary indicators used for detection
            "comment": f"{'Primary' if is_primary else 'Related'} indicator",
            "timestamp": str(int(datetime.now(timezone.utc).timestamp())),
            "distribution": random.randint(0, 3)
        }

    def _generate_organization(self) -> Dict[str, Any]:
        """Generate organization creator metadata.

        Returns:
            Organization dictionary
        """
        org_name = random.choice(self._organizations)
        org_id = random.randint(1, 100)

        return {
            "id": str(org_id),
            "name": org_name,
            "uuid": str(uuid_lib.uuid4()),
            "local": random.choice([True, False])
        }

    def _generate_tags(
        self,
        threat_level: int,
        threat_category: str
    ) -> List[Dict[str, Any]]:
        """Generate MISP tags including TLP.

        Args:
            threat_level: MISP threat level
            threat_category: Threat category string

        Returns:
            List of tag dictionaries
        """
        tags = []

        # Always include TLP tag
        tlp = self._select_tlp_for_threat_level(threat_level)
        tags.append({
            "id": random.randint(1, 1000),
            "name": tlp,
            "colour": self._get_tlp_colour(tlp),
            "exportable": True
        })

        # Add threat category tag
        tags.append({
            "id": random.randint(1, 1000),
            "name": f"misp-galaxy:threat-actor=\"{threat_category}\"",
            "colour": "#0088cc",
            "exportable": True
        })

        # Optionally add additional tags
        if random.random() > 0.5:
            confidence_tag = random.choice(["confidence:high", "confidence:medium", "confidence:low"])
            tags.append({
                "id": random.randint(1, 1000),
                "name": confidence_tag,
                "colour": "#3366cc",
                "exportable": True
            })

        return tags

    def _select_tlp_for_threat_level(self, threat_level: int) -> str:
        """Select appropriate TLP based on threat level.

        Args:
            threat_level: MISP threat level

        Returns:
            TLP string
        """
        # Higher threat level (lower number) -> more restricted TLP
        if threat_level == 1:  # High
            return random.choice(["tlp:red", "tlp:amber"])
        elif threat_level == 2:  # Medium
            return random.choice(["tlp:amber", "tlp:green"])
        elif threat_level == 3:  # Low
            return random.choice(["tlp:green", "tlp:white"])
        else:  # Undefined
            return random.choice(self._tlp_levels)

    def _get_tlp_colour(self, tlp: str) -> str:
        """Get colour code for TLP tag.

        Args:
            tlp: TLP string

        Returns:
            Hex colour code
        """
        colours = {
            "tlp:white": "#ffffff",
            "tlp:green": "#00ff00",
            "tlp:amber": "#ffc000",
            "tlp:red": "#ff0000"
        }
        return colours.get(tlp, "#cccccc")

    def _generate_event_info(
        self,
        indicator_type: str,
        indicator_value: str,
        threat_category: str
    ) -> str:
        """Generate descriptive event info.

        Args:
            indicator_type: Type of IOC
            indicator_value: The indicator value
            threat_category: Threat category

        Returns:
            Descriptive event info string
        """
        templates = [
            f"{threat_category} activity detected - {indicator_type.upper()} indicator",
            f"Malicious {indicator_type} associated with {threat_category} campaign",
            f"IOC Report: {threat_category} threat intelligence",
            f"Threat Intelligence: {threat_category} infrastructure indicators",
            f"{threat_category} Campaign - Network indicators collection"
        ]
        return random.choice(templates)

    def _generate_related_indicator(self, indicator_type: str) -> str:
        """Generate a random related indicator value.

        Args:
            indicator_type: Type of IOC to generate

        Returns:
            Generated indicator value
        """
        if indicator_type == "ip":
            return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        elif indicator_type == "domain":
            prefixes = ["evil", "bad", "malware", "c2", "phish"]
            tlds = ["com", "net", "org", "ru", "cn", "xyz"]
            return f"{random.choice(prefixes)}{random.randint(1,99)}.{random.choice(tlds)}"
        elif indicator_type == "hash":
            return ''.join(random.choices('0123456789abcdef', k=32))
        elif indicator_type == "url":
            domain = self._generate_related_indicator("domain")
            paths = ["payload.exe", "download.php", "update.bin", "script.js"]
            return f"http://{domain}/{random.choice(paths)}"
        else:
            return f"unknown-{random.randint(1000, 9999)}"
