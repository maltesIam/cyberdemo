"""Unit tests for ThreatQuotient mock generator.

Tests follow TDD RED-GREEN-REFACTOR cycle.
These tests should FAIL initially (RED phase).
"""
import pytest
import json


class TestThreatQuotientMock:
    """Tests for ThreatQuotientMock threat context generator."""

    def test_threatquotient_generates_context_for_malicious_ip(self):
        """
        RED: Test generation of threat context for a malicious IP indicator.

        Expected: Complete threat context with score, confidence, campaigns,
        related indicators, description, and priority.
        """
        from src.generators.enrichment.threatquotient_mock import ThreatQuotientMock

        mock = ThreatQuotientMock()

        result = mock.generate_threat_context(
            indicator_type="ip",
            indicator_value="192.168.1.100",
            reputation_score=85,
            malware_families=["Emotet", "TrickBot"]
        )

        # Required fields must be present
        assert "threat_score" in result
        assert "confidence" in result
        assert "campaigns" in result
        assert "related_indicators" in result
        assert "context_description" in result
        assert "priority" in result
        assert "enrichment_source" in result
        assert "generated_at" in result

        # Threat score should be based on reputation
        assert 0 <= result["threat_score"] <= 100
        assert result["threat_score"] == 85  # Should match reputation_score

        # Confidence should be a valid level
        assert result["confidence"] in ["high", "medium", "low"]

        # High score should have high confidence
        assert result["confidence"] == "high"

        # Priority should be based on threat score
        assert result["priority"] in ["critical", "high", "medium"]

        # Source identifier
        assert result["enrichment_source"] == "synthetic_threatquotient"

    def test_threatquotient_high_score_generates_campaigns(self):
        """
        RED: Test that high threat scores (>=60) generate associated campaigns.

        Expected: At least one campaign with name and status fields.
        """
        from src.generators.enrichment.threatquotient_mock import ThreatQuotientMock

        mock = ThreatQuotientMock()

        # High score should generate campaigns
        result_high = mock.generate_threat_context(
            indicator_type="domain",
            indicator_value="malicious-domain.com",
            reputation_score=80,
            malware_families=["Cobalt Strike"]
        )

        assert len(result_high["campaigns"]) >= 1, "High score should generate campaigns"

        # Each campaign should have required fields
        for campaign in result_high["campaigns"]:
            assert "name" in campaign
            assert "status" in campaign
            assert campaign["status"] in ["active", "monitoring", "historical"]

        # Low score should NOT generate campaigns
        result_low = mock.generate_threat_context(
            indicator_type="domain",
            indicator_value="benign-domain.com",
            reputation_score=30,
            malware_families=[]
        )

        assert len(result_low["campaigns"]) == 0, "Low score should not generate campaigns"

    def test_threatquotient_description_is_readable(self):
        """
        RED: Test that context description is human-readable and meaningful.

        Expected: Description should contain indicator type, value, severity,
        and malware family information in readable English.
        """
        from src.generators.enrichment.threatquotient_mock import ThreatQuotientMock

        mock = ThreatQuotientMock()

        result = mock.generate_threat_context(
            indicator_type="hash",
            indicator_value="abc123def456",
            reputation_score=90,
            malware_families=["Ryuk", "Conti"]
        )

        description = result["context_description"]

        # Description should be a non-empty string
        assert isinstance(description, str)
        assert len(description) > 50, "Description should be meaningful, not a stub"

        # Description should mention the indicator type
        assert "hash" in description.lower()

        # Description should mention severity level
        assert any(sev in description.lower() for sev in ["critical", "high", "moderate", "severe"])

        # Description should mention malware if provided
        assert "Ryuk" in description or "Conti" in description or "malware" in description.lower()

        # Description should read like English (basic check)
        assert description[0].isupper(), "Should start with capital letter"
        assert description[-1] == ".", "Should end with period"

    def test_threatquotient_returns_valid_json(self):
        """
        RED: Test that the result can be serialized to valid JSON.

        Expected: All fields should be JSON-serializable.
        """
        from src.generators.enrichment.threatquotient_mock import ThreatQuotientMock

        mock = ThreatQuotientMock()

        result = mock.generate_threat_context(
            indicator_type="url",
            indicator_value="https://evil.com/malware.exe",
            reputation_score=95,
            malware_families=["AgentTesla"]
        )

        # Should be JSON serializable without errors
        try:
            json_str = json.dumps(result)
            parsed = json.loads(json_str)
            assert parsed == result
        except (TypeError, ValueError) as e:
            pytest.fail(f"Result is not JSON serializable: {e}")

        # All values should be primitive types or lists/dicts of primitives
        assert isinstance(result["threat_score"], int)
        assert isinstance(result["confidence"], str)
        assert isinstance(result["campaigns"], list)
        assert isinstance(result["related_indicators"], list)
        assert isinstance(result["context_description"], str)
        assert isinstance(result["priority"], str)
        assert isinstance(result["generated_at"], str)

    def test_threatquotient_related_indicators_generated(self):
        """
        RED: Test that related indicators are generated for high-threat IOCs.
        """
        from src.generators.enrichment.threatquotient_mock import ThreatQuotientMock

        mock = ThreatQuotientMock()

        # High threat score should generate related indicators
        result = mock.generate_threat_context(
            indicator_type="ip",
            indicator_value="45.33.32.156",
            reputation_score=75,
            malware_families=["Emotet"]
        )

        assert "related_indicators" in result
        assert isinstance(result["related_indicators"], list)

        # Should have at least some related indicators for high score
        if result["threat_score"] >= 50:
            assert len(result["related_indicators"]) >= 1, "High-threat IOC should have related indicators"

            # Each related indicator should have type and value
            for indicator in result["related_indicators"]:
                assert "type" in indicator
                assert "value" in indicator
                assert indicator["type"] in ["ip", "domain", "url", "hash"]

    def test_threatquotient_confidence_levels(self):
        """
        RED: Test confidence level assignment based on threat score.

        Expected:
        - score > 80: confidence = "high"
        - 50 < score <= 80: confidence = "medium"
        - score <= 50: confidence = "low"
        """
        from src.generators.enrichment.threatquotient_mock import ThreatQuotientMock

        mock = ThreatQuotientMock()

        # High score → high confidence
        result_high = mock.generate_threat_context(
            indicator_type="ip",
            indicator_value="1.2.3.4",
            reputation_score=85,
            malware_families=[]
        )
        assert result_high["confidence"] == "high"

        # Medium score → medium confidence
        result_medium = mock.generate_threat_context(
            indicator_type="ip",
            indicator_value="1.2.3.5",
            reputation_score=65,
            malware_families=[]
        )
        assert result_medium["confidence"] == "medium"

        # Low score → low confidence
        result_low = mock.generate_threat_context(
            indicator_type="ip",
            indicator_value="1.2.3.6",
            reputation_score=40,
            malware_families=[]
        )
        assert result_low["confidence"] == "low"

    def test_threatquotient_priority_levels(self):
        """
        RED: Test priority level assignment based on threat score.

        Expected:
        - score > 90: priority = "critical"
        - 70 < score <= 90: priority = "high"
        - score <= 70: priority = "medium"
        """
        from src.generators.enrichment.threatquotient_mock import ThreatQuotientMock

        mock = ThreatQuotientMock()

        # Critical priority
        result_critical = mock.generate_threat_context(
            indicator_type="ip",
            indicator_value="1.2.3.7",
            reputation_score=95,
            malware_families=["Ryuk"]
        )
        assert result_critical["priority"] == "critical"

        # High priority
        result_high = mock.generate_threat_context(
            indicator_type="ip",
            indicator_value="1.2.3.8",
            reputation_score=80,
            malware_families=[]
        )
        assert result_high["priority"] == "high"

        # Medium priority
        result_medium = mock.generate_threat_context(
            indicator_type="ip",
            indicator_value="1.2.3.9",
            reputation_score=50,
            malware_families=[]
        )
        assert result_medium["priority"] == "medium"

    def test_threatquotient_threat_score_clamped(self):
        """
        RED: Test that threat score is always clamped to [0, 100].
        """
        from src.generators.enrichment.threatquotient_mock import ThreatQuotientMock

        mock = ThreatQuotientMock()

        # Test with out-of-range inputs
        result_high = mock.generate_threat_context(
            indicator_type="ip",
            indicator_value="1.2.3.10",
            reputation_score=150,  # Over 100
            malware_families=[]
        )
        assert result_high["threat_score"] <= 100

        result_low = mock.generate_threat_context(
            indicator_type="ip",
            indicator_value="1.2.3.11",
            reputation_score=-10,  # Negative
            malware_families=[]
        )
        assert result_low["threat_score"] >= 0

    def test_threatquotient_campaign_names_are_creative(self):
        """
        RED: Test that generated campaign names are realistic operation names.
        """
        from src.generators.enrichment.threatquotient_mock import ThreatQuotientMock

        mock = ThreatQuotientMock()

        # Generate multiple contexts to see campaign variety
        campaigns_seen = set()
        for i in range(10):
            result = mock.generate_threat_context(
                indicator_type="domain",
                indicator_value=f"malware{i}.com",
                reputation_score=85,
                malware_families=["Emotet"]
            )
            for campaign in result["campaigns"]:
                campaigns_seen.add(campaign["name"])

        # Should have variety in campaign names
        assert len(campaigns_seen) >= 2, "Campaign names should have variety"

        # Campaign names should look like operation names (contain space or capitalized words)
        for name in campaigns_seen:
            assert len(name) > 3, f"Campaign name too short: {name}"

    def test_threatquotient_seed_reproducibility(self):
        """
        RED: Test that providing a seed makes results reproducible.
        """
        from src.generators.enrichment.threatquotient_mock import ThreatQuotientMock

        mock1 = ThreatQuotientMock(seed=12345)
        mock2 = ThreatQuotientMock(seed=12345)

        result1 = mock1.generate_threat_context(
            indicator_type="ip",
            indicator_value="1.2.3.12",
            reputation_score=75,
            malware_families=["TrickBot"]
        )

        result2 = mock2.generate_threat_context(
            indicator_type="ip",
            indicator_value="1.2.3.12",
            reputation_score=75,
            malware_families=["TrickBot"]
        )

        # Same seed should produce same campaigns
        assert result1["campaigns"] == result2["campaigns"]
        # Same seed should produce same related indicators
        assert result1["related_indicators"] == result2["related_indicators"]

    def test_threatquotient_empty_malware_families(self):
        """
        RED: Test behavior when malware_families is empty.
        """
        from src.generators.enrichment.threatquotient_mock import ThreatQuotientMock

        mock = ThreatQuotientMock()

        result = mock.generate_threat_context(
            indicator_type="ip",
            indicator_value="10.0.0.1",
            reputation_score=70,
            malware_families=[]
        )

        # Should still generate valid context
        assert result["threat_score"] == 70
        assert "context_description" in result
        assert len(result["context_description"]) > 0

        # Description should handle empty malware gracefully
        assert "unknown" in result["context_description"].lower() or "malware" in result["context_description"].lower()

    def test_threatquotient_all_indicator_types(self):
        """
        RED: Test that all indicator types are handled.
        """
        from src.generators.enrichment.threatquotient_mock import ThreatQuotientMock

        mock = ThreatQuotientMock()

        indicator_types = ["ip", "domain", "url", "hash", "email"]

        for ioc_type in indicator_types:
            result = mock.generate_threat_context(
                indicator_type=ioc_type,
                indicator_value=f"test-{ioc_type}-value",
                reputation_score=60,
                malware_families=["TestMalware"]
            )

            assert result["threat_score"] == 60
            assert result["confidence"] == "medium"
            assert ioc_type in result["context_description"].lower()
