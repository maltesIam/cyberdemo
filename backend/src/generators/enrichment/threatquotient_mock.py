"""ThreatQuotient threat context generator (synthetic).

Simulates ThreatQuotient API responses for threat scoring and context including:
- Threat score (0-100)
- Confidence level (high/medium/low)
- Associated campaigns
- Related indicators
- Context description
- Priority (critical/high/medium)
"""

import random
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional


class ThreatQuotientMock:
    """Simulates ThreatQuotient API for threat scoring and context."""

    # Campaign name components
    ADJECTIVES = [
        "Shadow", "Silent", "Iron", "Golden", "Dark", "Crimson", "Silver",
        "Phantom", "Midnight", "Electric", "Frozen", "Burning", "Hidden"
    ]

    NOUNS = [
        "Storm", "Dragon", "Phoenix", "Wolf", "Eagle", "Serpent", "Tiger",
        "Falcon", "Raven", "Thunder", "Viper", "Hawk", "Lotus"
    ]

    ANIMALS = [
        "Bear", "Panda", "Spider", "Scorpion", "Cobra", "Leopard",
        "Jackal", "Lynx", "Buffalo", "Crane", "Owl", "Mantis"
    ]

    def __init__(self, seed: int = None):
        """Initialize the mock generator.

        Args:
            seed: Random seed for reproducibility
        """
        self._seed = seed
        if seed is not None:
            random.seed(seed)

    def generate_threat_context(
        self,
        indicator_type: str,
        indicator_value: str,
        reputation_score: int,
        malware_families: List[str]
    ) -> Dict[str, Any]:
        """Generate synthetic threat context in ThreatQuotient style.

        Args:
            indicator_type: Type of IOC (ip, domain, url, hash, email)
            indicator_value: The actual indicator value
            reputation_score: Base reputation score (0-100)
            malware_families: List of associated malware families

        Returns:
            Dictionary with threat context including:
            - threat_score (0-100)
            - confidence level (high/medium/low)
            - associated campaigns
            - related indicators
            - context description
            - priority (critical/high/medium)
        """
        # Reset seed for reproducibility if provided
        if self._seed is not None:
            random.seed(self._seed)

        # Clamp threat score to valid range
        threat_score = min(100, max(0, reputation_score))

        # Determine confidence based on score
        confidence = self._calculate_confidence(threat_score)

        # Generate associated campaigns (only for high scores)
        campaigns = self._generate_campaigns(threat_score, malware_families)

        # Generate related indicators
        related_indicators = self._generate_related_indicators(
            indicator_type, threat_score
        )

        # Generate context description
        context_description = self._generate_context_description(
            indicator_type, indicator_value, threat_score, malware_families
        )

        # Determine priority
        priority = self._calculate_priority(threat_score)

        return {
            "threat_score": threat_score,
            "confidence": confidence,
            "campaigns": campaigns,
            "related_indicators": related_indicators,
            "context_description": context_description,
            "priority": priority,
            "enrichment_source": "synthetic_threatquotient",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    def _calculate_confidence(self, threat_score: int) -> str:
        """Calculate confidence level based on threat score.

        Args:
            threat_score: Threat score (0-100)

        Returns:
            Confidence level: high, medium, or low
        """
        if threat_score > 80:
            return "high"
        elif threat_score > 50:
            return "medium"
        else:
            return "low"

    def _calculate_priority(self, threat_score: int) -> str:
        """Calculate priority level based on threat score.

        Args:
            threat_score: Threat score (0-100)

        Returns:
            Priority level: critical, high, or medium
        """
        if threat_score > 90:
            return "critical"
        elif threat_score > 70:
            return "high"
        else:
            return "medium"

    def _generate_campaigns(
        self,
        threat_score: int,
        malware_families: List[str]
    ) -> List[Dict[str, str]]:
        """Generate associated campaigns based on score and malware families.

        Args:
            threat_score: Threat score (0-100)
            malware_families: List of associated malware families

        Returns:
            List of campaign dictionaries with name and status
        """
        # Only generate campaigns for high-threat indicators
        if threat_score < 60:
            return []

        campaigns = []
        num_campaigns = 1 if threat_score < 80 else random.randint(1, 3)

        for _ in range(num_campaigns):
            campaign_type = random.choice([0, 1])

            if campaign_type == 0:
                # Operation style: "Operation Shadow Dragon"
                name = f"Operation {random.choice(self.ADJECTIVES)} {random.choice(self.NOUNS)}"
            else:
                # Animal campaign style: "Silent Bear Campaign"
                name = f"{random.choice(self.ADJECTIVES)} {random.choice(self.ANIMALS)} Campaign"

            status = random.choice(["active", "monitoring", "historical"])
            campaigns.append({"name": name, "status": status})

        return campaigns

    def _generate_related_indicators(
        self,
        indicator_type: str,
        threat_score: int
    ) -> List[Dict[str, str]]:
        """Generate related indicators for the IOC.

        Args:
            indicator_type: Type of the original IOC
            threat_score: Threat score (0-100)

        Returns:
            List of related indicator dictionaries
        """
        if threat_score < 50:
            return []

        related = []
        num_related = random.randint(1, 4) if threat_score >= 70 else random.randint(1, 2)

        # Generate different types of related indicators
        indicator_generators = {
            "ip": self._generate_random_ip,
            "domain": self._generate_random_domain,
            "url": self._generate_random_url,
            "hash": self._generate_random_hash
        }

        # Pick related indicator types (exclude the original type sometimes)
        available_types = list(indicator_generators.keys())

        for _ in range(num_related):
            rel_type = random.choice(available_types)
            rel_value = indicator_generators[rel_type]()
            related.append({"type": rel_type, "value": rel_value})

        return related

    def _generate_random_ip(self) -> str:
        """Generate a random IP address."""
        return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"

    def _generate_random_domain(self) -> str:
        """Generate a random malicious-looking domain."""
        prefixes = ["secure", "update", "cdn", "api", "mail", "login", "auth"]
        suffixes = ["service", "cloud", "net", "sys", "core", "hub"]
        tlds = ["com", "net", "org", "io", "xyz"]
        return f"{random.choice(prefixes)}-{random.choice(suffixes)}{random.randint(1, 99)}.{random.choice(tlds)}"

    def _generate_random_url(self) -> str:
        """Generate a random suspicious URL."""
        domain = self._generate_random_domain()
        paths = ["download", "update", "api/v1/data", "files", "cdn/resource"]
        return f"https://{domain}/{random.choice(paths)}"

    def _generate_random_hash(self) -> str:
        """Generate a random file hash (MD5-style)."""
        return ''.join(random.choices('0123456789abcdef', k=32))

    def _generate_context_description(
        self,
        indicator_type: str,
        indicator_value: str,
        threat_score: int,
        malware_families: List[str]
    ) -> str:
        """Generate a human-readable context description.

        Args:
            indicator_type: Type of IOC
            indicator_value: The indicator value
            threat_score: Threat score (0-100)
            malware_families: List of associated malware families

        Returns:
            Human-readable context description
        """
        # Determine severity word
        if threat_score > 90:
            severity = "critical"
        elif threat_score > 70:
            severity = "high"
        elif threat_score > 50:
            severity = "moderate"
        else:
            severity = "low"

        # Format malware families
        if malware_families and len(malware_families) > 0:
            if len(malware_families) == 1:
                family_str = malware_families[0]
            elif len(malware_families) == 2:
                family_str = f"{malware_families[0]} and {malware_families[1]}"
            else:
                family_str = f"{', '.join(malware_families[:2])}, and others"
        else:
            family_str = "unknown malware"

        # Build description based on threat level
        if threat_score >= 70:
            description = (
                f"This {indicator_type} indicator ({indicator_value}) has been associated with {severity} "
                f"threat activity involving {family_str}. Analysis suggests ongoing "
                f"malicious operations with confidence level based on {threat_score}% reputation score."
            )
        elif threat_score >= 40:
            description = (
                f"This {indicator_type} indicator ({indicator_value}) shows {severity} "
                f"threat indicators associated with {family_str}. Monitoring is recommended "
                f"based on the current {threat_score}% reputation score."
            )
        else:
            description = (
                f"This {indicator_type} indicator ({indicator_value}) has a {severity} "
                f"threat profile with limited evidence of malicious activity related to {family_str}. "
                f"Current reputation score is {threat_score}%."
            )

        return description
