"""Unit tests for Qualys QDS vulnerability mock generator.

Tests follow TDD RED-GREEN-REFACTOR cycle.
These tests should FAIL initially (RED phase) as the implementation doesn't exist yet.
"""
import pytest
from datetime import datetime


class TestQualysQDSMock:
    """Tests for QualysQDSMock vulnerability detection score generator."""

    def test_high_risk_cve_gets_high_qds(self):
        """
        RED: Test that high CVSS + high EPSS + exploit + threats = high QDS (>=90).

        QDS formula:
        - CVSS (40%): 9.8 / 10 * 40 = 39.2
        - EPSS (20%): 0.95 * 20 = 19.0
        - Exploit bonus (10%): 10
        - Threat indicators (30%): 15 (malware) + 15 (real-time) = 30
        - Total: ~98.2 -> QDS Severity: Critical
        """
        from src.generators.enrichment.qualys_vuln_mock import QualysQDSMock

        mock = QualysQDSMock()

        result = mock.calculate_qds(
            cvss_score=9.8,
            epss_score=0.95,
            known_exploited=True,
            malware_associated=True,
            real_time_threat=True
        )

        assert result["qds_score"] >= 90, f"Expected QDS >=90, got {result['qds_score']}"
        assert result["qds_severity"] == "Critical"

    def test_low_risk_cve_gets_low_qds(self):
        """
        RED: Test that low CVSS + low EPSS + no threats = low QDS (<=40).

        QDS formula:
        - CVSS (40%): 3.0 / 10 * 40 = 12.0
        - EPSS (20%): 0.05 * 20 = 1.0
        - Exploit bonus (10%): 0
        - Threat indicators (30%): 0
        - Total: 13.0 -> QDS Severity: Low
        """
        from src.generators.enrichment.qualys_vuln_mock import QualysQDSMock

        mock = QualysQDSMock()

        result = mock.calculate_qds(
            cvss_score=3.0,
            epss_score=0.05,
            known_exploited=False,
            malware_associated=False,
            real_time_threat=False
        )

        assert result["qds_score"] <= 40, f"Expected QDS <=40, got {result['qds_score']}"
        assert result["qds_severity"] == "Low"

    def test_score_clamped_to_valid_range(self):
        """
        RED: Test that QDS scores are always in range [0, 100].
        """
        from src.generators.enrichment.qualys_vuln_mock import QualysQDSMock

        mock = QualysQDSMock()

        # Maximum values
        result_max = mock.calculate_qds(
            cvss_score=10.0,
            epss_score=1.0,
            known_exploited=True,
            malware_associated=True,
            real_time_threat=True
        )
        assert 0 <= result_max["qds_score"] <= 100

        # Minimum values
        result_min = mock.calculate_qds(
            cvss_score=0.0,
            epss_score=0.0,
            known_exploited=False,
            malware_associated=False,
            real_time_threat=False
        )
        assert 0 <= result_min["qds_score"] <= 100

    def test_known_exploited_increases_qds(self):
        """
        RED: Test that known_exploited=True increases QDS by 10 points.
        """
        from src.generators.enrichment.qualys_vuln_mock import QualysQDSMock

        mock = QualysQDSMock()

        base_params = {
            "cvss_score": 7.0,
            "epss_score": 0.5,
            "malware_associated": False,
            "real_time_threat": False
        }

        result_without = mock.calculate_qds(**base_params, known_exploited=False)
        result_with = mock.calculate_qds(**base_params, known_exploited=True)

        # Exploited should be exactly 10 points higher
        score_diff = result_with["qds_score"] - result_without["qds_score"]
        assert score_diff == 10, f"Expected 10 point difference, got {score_diff}"

        # Verify exploit component
        assert result_with["qds_components"]["exploit_bonus"] == 10
        assert result_without["qds_components"]["exploit_bonus"] == 0

    def test_malware_associated_increases_qds(self):
        """
        RED: Test that malware_associated=True increases QDS by 15 points.
        """
        from src.generators.enrichment.qualys_vuln_mock import QualysQDSMock

        mock = QualysQDSMock()

        base_params = {
            "cvss_score": 7.0,
            "epss_score": 0.5,
            "known_exploited": False,
            "real_time_threat": False
        }

        result_without = mock.calculate_qds(**base_params, malware_associated=False)
        result_with = mock.calculate_qds(**base_params, malware_associated=True)

        # Malware should add 15 points
        score_diff = result_with["qds_score"] - result_without["qds_score"]
        assert score_diff == 15, f"Expected 15 point difference, got {score_diff}"

    def test_real_time_threat_increases_qds(self):
        """
        RED: Test that real_time_threat=True increases QDS by 15 points.
        """
        from src.generators.enrichment.qualys_vuln_mock import QualysQDSMock

        mock = QualysQDSMock()

        base_params = {
            "cvss_score": 7.0,
            "epss_score": 0.5,
            "known_exploited": False,
            "malware_associated": False
        }

        result_without = mock.calculate_qds(**base_params, real_time_threat=False)
        result_with = mock.calculate_qds(**base_params, real_time_threat=True)

        # Real-time threat should add 15 points
        score_diff = result_with["qds_score"] - result_without["qds_score"]
        assert score_diff == 15, f"Expected 15 point difference, got {score_diff}"

    def test_combined_threat_indicators(self):
        """
        RED: Test that both malware_associated and real_time_threat add up to 30 points total.
        """
        from src.generators.enrichment.qualys_vuln_mock import QualysQDSMock

        mock = QualysQDSMock()

        base_params = {
            "cvss_score": 5.0,
            "epss_score": 0.3,
            "known_exploited": False
        }

        result_none = mock.calculate_qds(**base_params, malware_associated=False, real_time_threat=False)
        result_both = mock.calculate_qds(**base_params, malware_associated=True, real_time_threat=True)

        # Both should add 30 points (15 + 15)
        score_diff = result_both["qds_score"] - result_none["qds_score"]
        assert score_diff == 30, f"Expected 30 point difference, got {score_diff}"

        # Verify threat indicators component
        assert result_both["qds_components"]["threat_indicators"] == 30

    def test_qds_severity_boundaries(self):
        """
        RED: Test QDS severity boundaries:
        - Critical: >=90
        - High: >=70
        - Medium: >=40
        - Low: <40
        """
        from src.generators.enrichment.qualys_vuln_mock import QualysQDSMock

        mock = QualysQDSMock()

        # Test Critical (>=90)
        result_critical = mock.calculate_qds(
            cvss_score=10.0,
            epss_score=1.0,
            known_exploited=True,
            malware_associated=True,
            real_time_threat=True
        )
        assert result_critical["qds_severity"] == "Critical"

        # Test Low (<40)
        result_low = mock.calculate_qds(
            cvss_score=2.0,
            epss_score=0.05,
            known_exploited=False,
            malware_associated=False,
            real_time_threat=False
        )
        assert result_low["qds_severity"] == "Low"

    def test_return_format_correct(self):
        """
        RED: Test that return format contains all required fields.
        """
        from src.generators.enrichment.qualys_vuln_mock import QualysQDSMock

        mock = QualysQDSMock()

        result = mock.calculate_qds(
            cvss_score=7.0,
            epss_score=0.5,
            known_exploited=False,
            malware_associated=False,
            real_time_threat=False
        )

        # Required top-level fields
        assert "qds_score" in result
        assert "qds_severity" in result
        assert "qds_components" in result
        assert "enrichment_source" in result
        assert "generated_at" in result

        # Required qds_components fields
        assert "cvss_component" in result["qds_components"]
        assert "epss_component" in result["qds_components"]
        assert "exploit_bonus" in result["qds_components"]
        assert "threat_indicators" in result["qds_components"]

    def test_enrichment_source_field(self):
        """
        RED: Test that enrichment_source field is correctly set.
        """
        from src.generators.enrichment.qualys_vuln_mock import QualysQDSMock

        mock = QualysQDSMock()

        result = mock.calculate_qds(
            cvss_score=7.0,
            epss_score=0.5,
            known_exploited=False,
            malware_associated=False,
            real_time_threat=False
        )

        assert result["enrichment_source"] == "synthetic_qualys_qds"

    def test_cvss_component_weight(self):
        """
        RED: Test CVSS component is 40% weight (max 40 points).
        """
        from src.generators.enrichment.qualys_vuln_mock import QualysQDSMock

        mock = QualysQDSMock()

        # CVSS 10.0 should give 40 points
        result = mock.calculate_qds(
            cvss_score=10.0,
            epss_score=0.0,
            known_exploited=False,
            malware_associated=False,
            real_time_threat=False
        )

        assert result["qds_components"]["cvss_component"] == 40

    def test_epss_component_weight(self):
        """
        RED: Test EPSS component is 20% weight (max 20 points).
        """
        from src.generators.enrichment.qualys_vuln_mock import QualysQDSMock

        mock = QualysQDSMock()

        # EPSS 1.0 should give 20 points
        result = mock.calculate_qds(
            cvss_score=0.0,
            epss_score=1.0,
            known_exploited=False,
            malware_associated=False,
            real_time_threat=False
        )

        assert result["qds_components"]["epss_component"] == 20

    def test_qds_correlation_with_cvss(self):
        """
        RED: Test that QDS scores correlate with CVSS (since CVSS is 40% of QDS).
        """
        from src.generators.enrichment.qualys_vuln_mock import QualysQDSMock

        mock = QualysQDSMock()

        fixed_params = {
            "epss_score": 0.5,
            "known_exploited": False,
            "malware_associated": False,
            "real_time_threat": False
        }

        result_low = mock.calculate_qds(cvss_score=3.0, **fixed_params)
        result_med = mock.calculate_qds(cvss_score=6.0, **fixed_params)
        result_high = mock.calculate_qds(cvss_score=9.0, **fixed_params)

        # QDS should increase with CVSS
        assert result_low["qds_score"] < result_med["qds_score"]
        assert result_med["qds_score"] < result_high["qds_score"]

    def test_generated_at_is_iso_timestamp(self):
        """
        RED: Test that generated_at is a valid ISO 8601 timestamp.
        """
        from src.generators.enrichment.qualys_vuln_mock import QualysQDSMock

        mock = QualysQDSMock()

        result = mock.calculate_qds(
            cvss_score=7.0,
            epss_score=0.5,
            known_exploited=False,
            malware_associated=False,
            real_time_threat=False
        )

        # Should be parseable as ISO timestamp
        generated_at = result["generated_at"]
        assert isinstance(generated_at, str)
        # Should not raise an error
        datetime.fromisoformat(generated_at.replace("Z", "+00:00") if generated_at.endswith("Z") else generated_at)
