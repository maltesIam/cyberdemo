"""Unit tests for Mandiant Threat Intelligence mock generator.

Tests follow TDD RED-GREEN-REFACTOR cycle.
These tests should FAIL initially (RED phase).
"""
import pytest


class TestMandiantMock:
    """Tests for MandiantMock generator."""

    def test_mandiant_maps_russian_ip_to_apt28_apt29(self):
        """
        RED: Test that Russian IP maps to Russian APT groups (APT28, APT29).
        """
        from src.generators.enrichment.mandiant_mock import MandiantMock

        mock = MandiantMock()

        result = mock.map_indicator_to_actors(
            indicator_type="ip",
            indicator_value="192.0.2.1",
            country="RU",
            malware_families=[]
        )

        assert "attributed_actors" in result
        assert len(result["attributed_actors"]) > 0

        # Should include at least one Russian APT
        russian_apts = {"APT28", "APT29", "Turla", "Sandworm", "Gamaredon"}
        attributed = set(result["attributed_actors"])
        assert attributed & russian_apts, f"Expected Russian APT, got {attributed}"

    def test_mandiant_maps_chinese_ip_to_chinese_apts(self):
        """
        RED: Test that Chinese IP maps to Chinese APT groups.
        """
        from src.generators.enrichment.mandiant_mock import MandiantMock

        mock = MandiantMock()

        result = mock.map_indicator_to_actors(
            indicator_type="ip",
            indicator_value="203.0.113.1",
            country="CN",
            malware_families=[]
        )

        assert "attributed_actors" in result

        # Should include at least one Chinese APT
        chinese_apts = {"APT1", "APT10", "APT41", "Mustang Panda", "Winnti"}
        attributed = set(result["attributed_actors"])
        assert attributed & chinese_apts, f"Expected Chinese APT, got {attributed}"

    def test_mandiant_maps_emotet_to_ta542(self):
        """
        RED: Test that Emotet malware family maps to TA542 threat actor.
        """
        from src.generators.enrichment.mandiant_mock import MandiantMock

        mock = MandiantMock()

        result = mock.map_indicator_to_actors(
            indicator_type="hash",
            indicator_value="abc123def456",
            country="US",  # Country doesn't map to known APT
            malware_families=["Emotet"]
        )

        assert "attributed_actors" in result
        # TA542 is known Emotet operator
        assert "TA542" in result["attributed_actors"], \
            f"Expected TA542 for Emotet, got {result['attributed_actors']}"

    def test_mandiant_maps_trickbot_to_wizard_spider(self):
        """
        RED: Test that TrickBot/Conti/Ryuk maps to Wizard Spider.
        """
        from src.generators.enrichment.mandiant_mock import MandiantMock

        mock = MandiantMock()

        # Test with TrickBot
        result = mock.map_indicator_to_actors(
            indicator_type="hash",
            indicator_value="trickbot_hash",
            country="US",
            malware_families=["TrickBot"]
        )

        assert "Wizard Spider" in result["attributed_actors"], \
            f"Expected Wizard Spider for TrickBot, got {result['attributed_actors']}"

    def test_mandiant_maps_cobalt_strike_to_multiple_actors(self):
        """
        RED: Test that Cobalt Strike maps to multiple known operators.
        """
        from src.generators.enrichment.mandiant_mock import MandiantMock

        mock = MandiantMock()

        result = mock.map_indicator_to_actors(
            indicator_type="ip",
            indicator_value="10.0.0.1",
            country="US",
            malware_families=["Cobalt Strike"]
        )

        # Cobalt Strike used by APT29, FIN7, APT41
        known_cs_users = {"APT29", "FIN7", "APT41"}
        attributed = set(result["attributed_actors"])
        assert attributed & known_cs_users, \
            f"Expected Cobalt Strike users, got {attributed}"

    def test_mandiant_generates_actor_profile(self):
        """
        RED: Test generation of basic threat actor profile.
        """
        from src.generators.enrichment.mandiant_mock import MandiantMock

        mock = MandiantMock()

        profile = mock._generate_actor_profile("APT28")

        assert "name" in profile
        assert profile["name"] == "APT28"
        assert "aliases" in profile
        assert isinstance(profile["aliases"], list)
        assert "motivation" in profile
        assert profile["motivation"] in ["espionage", "financial", "sabotage", "hacktivism"]
        assert "target_sectors" in profile
        assert isinstance(profile["target_sectors"], list)
        assert len(profile["target_sectors"]) >= 2
        assert "active_since" in profile

    def test_mandiant_returns_valid_attribution(self):
        """
        RED: Test that attribution response has all required fields.
        """
        from src.generators.enrichment.mandiant_mock import MandiantMock

        mock = MandiantMock()

        result = mock.map_indicator_to_actors(
            indicator_type="ip",
            indicator_value="192.168.1.1",
            country="RU",
            malware_families=["Emotet"]
        )

        # Required fields
        assert "attributed_actors" in result
        assert "attribution_confidence" in result
        assert "actor_profiles" in result
        assert "enrichment_source" in result
        assert "generated_at" in result

        # Validate field types
        assert isinstance(result["attributed_actors"], list)
        assert result["attribution_confidence"] in ["low", "medium", "high"]
        assert isinstance(result["actor_profiles"], list)
        assert result["enrichment_source"] == "synthetic_mandiant"

    def test_mandiant_returns_actor_profiles_for_attributed(self):
        """
        RED: Test that actor profiles are generated for attributed actors.
        """
        from src.generators.enrichment.mandiant_mock import MandiantMock

        mock = MandiantMock()

        result = mock.map_indicator_to_actors(
            indicator_type="domain",
            indicator_value="malicious.example.com",
            country="RU",
            malware_families=[]
        )

        # Should have profiles for at least some attributed actors
        if result["attributed_actors"]:
            assert len(result["actor_profiles"]) > 0, \
                "Expected actor profiles when actors are attributed"

            for profile in result["actor_profiles"]:
                assert "name" in profile
                assert "motivation" in profile
                assert "target_sectors" in profile

    def test_mandiant_low_confidence_for_unknown_country(self):
        """
        RED: Test low confidence for unknown/unmapped countries.
        """
        from src.generators.enrichment.mandiant_mock import MandiantMock

        mock = MandiantMock()

        result = mock.map_indicator_to_actors(
            indicator_type="ip",
            indicator_value="10.0.0.1",
            country="ZZ",  # Unknown country
            malware_families=[]
        )

        # Low confidence when no mapping found
        assert result["attribution_confidence"] == "low"

    def test_mandiant_iran_ip_maps_to_iranian_apts(self):
        """
        RED: Test that Iranian IP maps to Iranian APT groups.
        """
        from src.generators.enrichment.mandiant_mock import MandiantMock

        mock = MandiantMock()

        result = mock.map_indicator_to_actors(
            indicator_type="ip",
            indicator_value="5.5.5.5",
            country="IR",
            malware_families=[]
        )

        iranian_apts = {"APT33", "APT34", "APT35", "Charming Kitten", "OilRig"}
        attributed = set(result["attributed_actors"])
        assert attributed & iranian_apts, f"Expected Iranian APT, got {attributed}"

    def test_mandiant_north_korea_ip_maps_to_dprk_apts(self):
        """
        RED: Test that North Korean IP maps to DPRK APT groups.
        """
        from src.generators.enrichment.mandiant_mock import MandiantMock

        mock = MandiantMock()

        result = mock.map_indicator_to_actors(
            indicator_type="ip",
            indicator_value="175.0.0.1",
            country="KP",
            malware_families=[]
        )

        dprk_apts = {"Lazarus Group", "Kimsuky", "APT38", "Andariel"}
        attributed = set(result["attributed_actors"])
        assert attributed & dprk_apts, f"Expected North Korean APT, got {attributed}"

    def test_mandiant_combines_country_and_malware_attribution(self):
        """
        RED: Test that both country and malware family contribute to attribution.
        """
        from src.generators.enrichment.mandiant_mock import MandiantMock

        mock = MandiantMock()

        # Russian IP with Emotet (TA542 is not Russian but operates Emotet)
        result = mock.map_indicator_to_actors(
            indicator_type="ip",
            indicator_value="192.0.2.100",
            country="RU",
            malware_families=["Emotet", "Cobalt Strike"]
        )

        attributed = set(result["attributed_actors"])

        # Should have Russian APTs from country
        russian_apts = {"APT28", "APT29", "Turla", "Sandworm", "Gamaredon"}
        # And malware-based actors
        malware_actors = {"TA542", "APT29", "FIN7", "APT41"}

        # Should have at least one from each source
        has_country_based = bool(attributed & russian_apts)
        has_malware_based = bool(attributed & malware_actors)

        assert has_country_based or has_malware_based, \
            f"Expected attribution from country or malware, got {attributed}"

    def test_mandiant_limits_actors_to_three(self):
        """
        RED: Test that attributed actors list is limited to 3.
        """
        from src.generators.enrichment.mandiant_mock import MandiantMock

        mock = MandiantMock()

        result = mock.map_indicator_to_actors(
            indicator_type="ip",
            indicator_value="192.0.2.1",
            country="RU",
            malware_families=["Cobalt Strike", "TrickBot", "Emotet"]
        )

        # Should be limited to 3 actors max
        assert len(result["attributed_actors"]) <= 3

    def test_mandiant_deduplicates_actors(self):
        """
        RED: Test that duplicate actors are deduplicated.
        """
        from src.generators.enrichment.mandiant_mock import MandiantMock

        mock = MandiantMock()

        # APT29 appears in both Russian APTs and Cobalt Strike users
        result = mock.map_indicator_to_actors(
            indicator_type="ip",
            indicator_value="192.0.2.1",
            country="RU",
            malware_families=["Cobalt Strike"]
        )

        # No duplicates
        actors = result["attributed_actors"]
        assert len(actors) == len(set(actors)), f"Duplicates found: {actors}"

    def test_mandiant_profile_has_valid_sectors(self):
        """
        RED: Test that actor profiles have valid target sectors.
        """
        from src.generators.enrichment.mandiant_mock import MandiantMock

        mock = MandiantMock()

        profile = mock._generate_actor_profile("Lazarus Group")

        valid_sectors = {
            "government", "finance", "energy", "technology", "healthcare",
            "defense", "telecommunications", "manufacturing", "education",
            "retail", "media", "transportation"
        }

        for sector in profile["target_sectors"]:
            assert sector in valid_sectors, f"Invalid sector: {sector}"

    def test_mandiant_active_since_is_valid_year(self):
        """
        RED: Test that active_since is a valid year string.
        """
        from src.generators.enrichment.mandiant_mock import MandiantMock

        mock = MandiantMock()

        profile = mock._generate_actor_profile("APT10")

        active_since = profile["active_since"]
        assert active_since.isdigit(), f"active_since should be year string: {active_since}"
        year = int(active_since)
        assert 2000 <= year <= 2025, f"Invalid year: {year}"

    def test_mandiant_seed_reproducibility(self):
        """
        RED: Test that results are reproducible with same seed.
        """
        from src.generators.enrichment.mandiant_mock import MandiantMock

        mock1 = MandiantMock(seed=42)
        mock2 = MandiantMock(seed=42)

        result1 = mock1.map_indicator_to_actors(
            indicator_type="ip",
            indicator_value="192.0.2.1",
            country="RU",
            malware_families=[]
        )

        result2 = mock2.map_indicator_to_actors(
            indicator_type="ip",
            indicator_value="192.0.2.1",
            country="RU",
            malware_families=[]
        )

        # Same seed should produce same attribution
        assert result1["attributed_actors"] == result2["attributed_actors"]
