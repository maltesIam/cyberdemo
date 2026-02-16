"""Mandiant Threat Intelligence mock generator (synthetic).

Simulates Mandiant threat intelligence API for APT mapping including:
- Attribution of IOCs to known APT groups based on country and malware families
- Threat actor profile generation
- Confidence scoring for attribution
"""

import random
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional


class MandiantMock:
    """Simulates Mandiant Threat Intelligence API for APT mapping."""

    # APT groups known publicly, organized by nation-state
    APT_GROUPS = {
        "russia": ["APT28", "APT29", "Turla", "Sandworm", "Gamaredon"],
        "china": ["APT1", "APT10", "APT41", "Mustang Panda", "Winnti"],
        "north_korea": ["Lazarus Group", "Kimsuky", "APT38", "Andariel"],
        "iran": ["APT33", "APT34", "APT35", "Charming Kitten", "OilRig"],
        "unknown": ["FIN7", "FIN8", "Carbanak", "Cobalt Group", "TA505"]
    }

    # Country code to APT region mapping
    COUNTRY_MAPPING = {
        "RU": "russia",
        "CN": "china",
        "KP": "north_korea",
        "IR": "iran"
    }

    # Malware family to known operators mapping
    MALWARE_APT_MAP = {
        "Emotet": ["TA542"],
        "TrickBot": ["Wizard Spider"],
        "Cobalt Strike": ["APT29", "FIN7", "APT41"],
        "Ryuk": ["Wizard Spider"],
        "Conti": ["Wizard Spider"],
        "Dridex": ["Evil Corp"],
        "QakBot": ["TA570"],
        "IcedID": ["TA551"],
        "BazarLoader": ["Wizard Spider"],
        "SolarWinds": ["APT29"],
        "NotPetya": ["Sandworm"],
        "WannaCry": ["Lazarus Group"],
        "Shamoon": ["APT33"],
        "APT10_Malware": ["APT10"],
    }

    # Valid target sectors
    TARGET_SECTORS = [
        "government", "finance", "energy", "technology", "healthcare",
        "defense", "telecommunications", "manufacturing", "education",
        "retail", "media", "transportation"
    ]

    # Valid motivations
    MOTIVATIONS = ["espionage", "financial", "sabotage", "hacktivism"]

    def __init__(self, seed: int = None):
        """Initialize the mock generator.

        Args:
            seed: Random seed for reproducibility
        """
        # Use instance-level random generator for reproducibility
        self._rng = random.Random(seed)

    def map_indicator_to_actors(
        self,
        indicator_type: str,
        indicator_value: str,
        country: str,
        malware_families: List[str]
    ) -> Dict[str, Any]:
        """Map IOC to known APT groups based on country and malware families.

        Args:
            indicator_type: Type of indicator (ip, domain, hash, url)
            indicator_value: Value of the indicator
            country: ISO country code (e.g., RU, CN, KP, IR)
            malware_families: List of associated malware families

        Returns:
            Dictionary with attributed actors and profiles
        """
        apt_candidates = []

        # Map by country
        if country in self.COUNTRY_MAPPING:
            region = self.COUNTRY_MAPPING[country]
            available_apts = self.APT_GROUPS[region]
            # Pick 1-2 APTs from the country
            num_to_pick = min(2, len(available_apts))
            apt_candidates.extend(self._rng.sample(available_apts, num_to_pick))

        # Map by malware family
        for family in malware_families:
            if family in self.MALWARE_APT_MAP:
                apt_candidates.extend(self.MALWARE_APT_MAP[family])

        # Deduplicate while preserving order
        seen = set()
        unique_candidates = []
        for apt in apt_candidates:
            if apt not in seen:
                seen.add(apt)
                unique_candidates.append(apt)

        # Limit to 3 actors maximum
        attributed_actors = unique_candidates[:3]

        # Determine attribution confidence
        if len(attributed_actors) == 0:
            attribution_confidence = "low"
        elif len(apt_candidates) > len(attributed_actors):
            # Multiple sources confirm attribution
            attribution_confidence = "medium"
        else:
            attribution_confidence = "medium" if attributed_actors else "low"

        # Generate actor profiles for top 2 actors
        actor_profiles = [
            self._generate_actor_profile(apt)
            for apt in attributed_actors[:2]
        ]

        return {
            "attributed_actors": attributed_actors,
            "attribution_confidence": attribution_confidence,
            "actor_profiles": actor_profiles,
            "enrichment_source": "synthetic_mandiant",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    def _generate_actor_profile(self, apt_name: str) -> Dict[str, Any]:
        """Generate basic threat actor profile.

        Args:
            apt_name: Name of the APT group

        Returns:
            Dictionary with actor profile information
        """
        # Determine motivation based on APT type
        if apt_name.startswith("FIN") or apt_name in ["Carbanak", "Evil Corp", "Wizard Spider"]:
            motivation = "financial"
        elif apt_name in ["Sandworm"]:
            motivation = "sabotage"
        else:
            motivation = self._rng.choice(["espionage", "financial", "sabotage", "hacktivism"])

        # Generate target sectors (2-4 sectors)
        num_sectors = self._rng.randint(2, 4)
        target_sectors = self._rng.sample(self.TARGET_SECTORS, num_sectors)

        # Generate active since year (between 2005 and 2022)
        active_since = str(self._rng.randint(2005, 2022))

        # Generate aliases
        aliases = self._generate_aliases(apt_name)

        return {
            "name": apt_name,
            "aliases": aliases,
            "motivation": motivation,
            "target_sectors": target_sectors,
            "active_since": active_since
        }

    def _generate_aliases(self, apt_name: str) -> List[str]:
        """Generate aliases for an APT group.

        Args:
            apt_name: Name of the APT group

        Returns:
            List of aliases
        """
        # Known aliases for some APT groups
        known_aliases = {
            "APT28": ["Fancy Bear", "Sofacy", "Sednit", "Pawn Storm"],
            "APT29": ["Cozy Bear", "The Dukes", "CozyDuke"],
            "APT41": ["Winnti", "Barium", "Wicked Panda"],
            "Lazarus Group": ["Hidden Cobra", "Zinc", "Guardians of Peace"],
            "APT33": ["Elfin", "Magnallium", "Refined Kitten"],
            "APT34": ["OilRig", "Helix Kitten"],
            "Turla": ["Snake", "Venomous Bear", "Waterbug"],
            "Sandworm": ["Voodoo Bear", "IRIDIUM", "Telebots"],
            "FIN7": ["Carbanak", "Navigator Group"],
            "Wizard Spider": ["GRIM SPIDER", "UNC1878"],
        }

        if apt_name in known_aliases:
            # Return 1-2 known aliases
            num_aliases = min(2, len(known_aliases[apt_name]))
            return self._rng.sample(known_aliases[apt_name], num_aliases)

        # Generate generic alias for unknown APT
        return [f"{apt_name}_alias"]
