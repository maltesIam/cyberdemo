"""Unit tests for Recorded Future Vulnerability mock generator.

Tests follow TDD RED-GREEN-REFACTOR cycle.
These tests should FAIL initially (RED phase) as the implementation doesn't exist yet.
"""
import pytest
from datetime import datetime


class TestRecordedFutureVulnMock:
    """Tests for RecordedFutureVulnMock vulnerability risk score generator."""

    def test_high_risk_cve_gets_high_score(self):
        """
        RED: Test that high CVSS + high EPSS + exploit = high risk score (>=90).

        Expected behavior:
        - CVSS 9.8 -> 39.2 points (40% weight)
        - EPSS 0.95 -> 28.5 points (30% weight)
        - Known exploited -> 20 points
        - Age 15 days -> 10 points (recent)
        - Total: ~98 points -> Risk Category: Critical
        """
        from src.generators.enrichment.recorded_future_vuln_mock import RecordedFutureVulnMock

        mock = RecordedFutureVulnMock()

        result = mock.calculate_risk_score(
            cve_id="CVE-2024-0001",
            cvss_score=9.8,
            epss_score=0.95,
            known_exploited=True,
            age_days=15
        )

        # High risk score expected
        assert result["risk_score"] >= 90, f"Expected risk score >=90, got {result['risk_score']}"
        assert result["risk_category"] == "Critical"

    def test_low_risk_cve_gets_low_score(self):
        """
        RED: Test that low CVSS + low EPSS + no exploit = low risk score (<=40).

        Expected behavior:
        - CVSS 3.2 -> 12.8 points (40% weight)
        - EPSS 0.01 -> 0.3 points (30% weight)
        - Not exploited -> 0 points
        - Age 400 days -> 2 points (old)
        - Total: ~15 points -> Risk Category: Low
        """
        from src.generators.enrichment.recorded_future_vuln_mock import RecordedFutureVulnMock

        mock = RecordedFutureVulnMock()

        result = mock.calculate_risk_score(
            cve_id="CVE-2024-9999",
            cvss_score=3.2,
            epss_score=0.01,
            known_exploited=False,
            age_days=400
        )

        # Low risk score expected
        assert result["risk_score"] <= 40, f"Expected risk score <=40, got {result['risk_score']}"
        assert result["risk_category"] == "Low"

    def test_score_clamped_to_valid_range(self):
        """
        RED: Test that risk scores are always in range [0, 100].
        """
        from src.generators.enrichment.recorded_future_vuln_mock import RecordedFutureVulnMock

        mock = RecordedFutureVulnMock()

        # Extreme high values
        result_high = mock.calculate_risk_score(
            cve_id="CVE-2024-MAX",
            cvss_score=10.0,
            epss_score=1.0,
            known_exploited=True,
            age_days=1
        )
        assert 0 <= result_high["risk_score"] <= 100, f"Score {result_high['risk_score']} out of range"

        # Extreme low values
        result_low = mock.calculate_risk_score(
            cve_id="CVE-2024-MIN",
            cvss_score=0.0,
            epss_score=0.0,
            known_exploited=False,
            age_days=1000
        )
        assert 0 <= result_low["risk_score"] <= 100, f"Score {result_low['risk_score']} out of range"

    def test_known_exploited_increases_score(self):
        """
        RED: Test that known_exploited=True increases score by 20 points.
        """
        from src.generators.enrichment.recorded_future_vuln_mock import RecordedFutureVulnMock

        mock = RecordedFutureVulnMock()

        base_params = {
            "cve_id": "CVE-2024-TEST",
            "cvss_score": 7.0,
            "epss_score": 0.5,
            "age_days": 60
        }

        result_without_exploit = mock.calculate_risk_score(**base_params, known_exploited=False)
        result_with_exploit = mock.calculate_risk_score(**base_params, known_exploited=True)

        # Exploited should be exactly 20 points higher
        score_diff = result_with_exploit["risk_score"] - result_without_exploit["risk_score"]
        assert score_diff == 20, f"Expected 20 point difference, got {score_diff}"

        # Verify exploit component in risk vector
        assert result_with_exploit["risk_vector"]["exploit_component"] == 20
        assert result_without_exploit["risk_vector"]["exploit_component"] == 0

    def test_recent_cve_higher_score(self):
        """
        RED: Test that recent CVEs (<=30 days) get higher age component (10 points).
        """
        from src.generators.enrichment.recorded_future_vuln_mock import RecordedFutureVulnMock

        mock = RecordedFutureVulnMock()

        base_params = {
            "cve_id": "CVE-2024-AGE",
            "cvss_score": 7.0,
            "epss_score": 0.5,
            "known_exploited": False,
        }

        result_recent = mock.calculate_risk_score(**base_params, age_days=15)
        result_old = mock.calculate_risk_score(**base_params, age_days=500)

        # Recent should have higher score
        assert result_recent["risk_score"] > result_old["risk_score"]
        # Recent should have 10 point age component
        assert result_recent["risk_vector"]["age_component"] == 10

    def test_old_cve_lower_score(self):
        """
        RED: Test that old CVEs (>365 days) get lowest age component (2 points).
        """
        from src.generators.enrichment.recorded_future_vuln_mock import RecordedFutureVulnMock

        mock = RecordedFutureVulnMock()

        result = mock.calculate_risk_score(
            cve_id="CVE-2020-OLD",
            cvss_score=7.0,
            epss_score=0.5,
            known_exploited=False,
            age_days=500
        )

        # Old CVE should have 2 point age component
        assert result["risk_vector"]["age_component"] == 2

    def test_threat_actors_generated_for_high_risk(self):
        """
        RED: Test that threat actors are generated for high-risk CVEs (score >=80, known_exploited=True).
        """
        from src.generators.enrichment.recorded_future_vuln_mock import RecordedFutureVulnMock

        mock = RecordedFutureVulnMock()

        # High risk with exploit -> should have threat actors
        result = mock.calculate_risk_score(
            cve_id="CVE-2024-CRITICAL",
            cvss_score=9.5,
            epss_score=0.85,
            known_exploited=True,
            age_days=20
        )

        assert result["risk_score"] >= 80, f"Score {result['risk_score']} should be >=80 for this test"
        assert len(result["threat_actors"]) >= 1, "High-risk exploited CVE should have threat actors"

    def test_no_threat_actors_for_low_risk(self):
        """
        RED: Test that threat actors are NOT generated for low-risk CVEs.
        """
        from src.generators.enrichment.recorded_future_vuln_mock import RecordedFutureVulnMock

        mock = RecordedFutureVulnMock()

        # Low risk without exploit -> should NOT have threat actors
        result = mock.calculate_risk_score(
            cve_id="CVE-2024-LOW",
            cvss_score=3.0,
            epss_score=0.05,
            known_exploited=False,
            age_days=200
        )

        assert len(result["threat_actors"]) == 0, "Low-risk CVE should not have threat actors"

    def test_campaigns_generated_for_recent_high_risk(self):
        """
        RED: Test that campaigns are generated for recent (<=90 days) high-risk (>=70) CVEs.
        """
        from src.generators.enrichment.recorded_future_vuln_mock import RecordedFutureVulnMock

        mock = RecordedFutureVulnMock()

        # Recent + high risk -> should have campaigns
        result = mock.calculate_risk_score(
            cve_id="CVE-2024-CAMPAIGN",
            cvss_score=8.5,
            epss_score=0.75,
            known_exploited=True,
            age_days=30
        )

        assert result["risk_score"] >= 70, f"Score {result['risk_score']} should be >=70 for this test"
        assert len(result["campaigns"]) >= 1, "Recent high-risk CVE should have campaigns"

    def test_no_campaigns_for_old_cve(self):
        """
        RED: Test that campaigns are NOT generated for old CVEs (>90 days) even if high-risk.
        """
        from src.generators.enrichment.recorded_future_vuln_mock import RecordedFutureVulnMock

        mock = RecordedFutureVulnMock()

        # Old CVE - should NOT have campaigns
        result = mock.calculate_risk_score(
            cve_id="CVE-2023-OLD",
            cvss_score=9.0,
            epss_score=0.8,
            known_exploited=True,
            age_days=200
        )

        assert len(result["campaigns"]) == 0, "Old CVE should not have active campaigns"

    def test_return_format_correct(self):
        """
        RED: Test that return format contains all required fields.
        """
        from src.generators.enrichment.recorded_future_vuln_mock import RecordedFutureVulnMock

        mock = RecordedFutureVulnMock()

        result = mock.calculate_risk_score(
            cve_id="CVE-2024-FORMAT",
            cvss_score=7.0,
            epss_score=0.5,
            known_exploited=False,
            age_days=60
        )

        # Required top-level fields
        assert "risk_score" in result
        assert "risk_category" in result
        assert "threat_actors" in result
        assert "campaigns" in result
        assert "risk_vector" in result
        assert "enrichment_source" in result
        assert "generated_at" in result

        # Required risk_vector fields
        assert "cvss_component" in result["risk_vector"]
        assert "epss_component" in result["risk_vector"]
        assert "exploit_component" in result["risk_vector"]
        assert "age_component" in result["risk_vector"]

    def test_enrichment_source_field(self):
        """
        RED: Test that enrichment_source field is correctly set.
        """
        from src.generators.enrichment.recorded_future_vuln_mock import RecordedFutureVulnMock

        mock = RecordedFutureVulnMock()

        result = mock.calculate_risk_score(
            cve_id="CVE-2024-SOURCE",
            cvss_score=7.0,
            epss_score=0.5,
            known_exploited=False,
            age_days=60
        )

        assert result["enrichment_source"] == "synthetic_recorded_future_vuln"

    def test_age_component_weights_correctly(self):
        """
        RED: Test that age component follows correct weighting:
        - 0-30 days: 10 points
        - 31-90 days: 7 points
        - 91-365 days: 4 points
        - >365 days: 2 points
        """
        from src.generators.enrichment.recorded_future_vuln_mock import RecordedFutureVulnMock

        mock = RecordedFutureVulnMock()

        base_params = {
            "cve_id": "CVE-2024-AGETEST",
            "cvss_score": 7.0,
            "epss_score": 0.5,
            "known_exploited": False,
        }

        result_0_30 = mock.calculate_risk_score(**base_params, age_days=15)
        result_31_90 = mock.calculate_risk_score(**base_params, age_days=60)
        result_91_365 = mock.calculate_risk_score(**base_params, age_days=180)
        result_365_plus = mock.calculate_risk_score(**base_params, age_days=500)

        # Extract age components
        assert result_0_30["risk_vector"]["age_component"] == 10
        assert result_31_90["risk_vector"]["age_component"] == 7
        assert result_91_365["risk_vector"]["age_component"] == 4
        assert result_365_plus["risk_vector"]["age_component"] == 2

    def test_risk_category_boundaries(self):
        """
        RED: Test risk category boundaries:
        - Critical: >=90
        - High: >=70
        - Medium: >=50
        - Low: <50
        """
        from src.generators.enrichment.recorded_future_vuln_mock import RecordedFutureVulnMock

        mock = RecordedFutureVulnMock()

        # Test Critical (>=90)
        result_critical = mock.calculate_risk_score(
            cve_id="CVE-CRITICAL",
            cvss_score=10.0,
            epss_score=1.0,
            known_exploited=True,
            age_days=1
        )
        assert result_critical["risk_category"] == "Critical"

        # Test Low (<50)
        result_low = mock.calculate_risk_score(
            cve_id="CVE-LOW",
            cvss_score=2.0,
            epss_score=0.1,
            known_exploited=False,
            age_days=400
        )
        assert result_low["risk_category"] == "Low"
