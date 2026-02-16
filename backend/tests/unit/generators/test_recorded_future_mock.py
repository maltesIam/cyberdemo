"""Unit tests for Recorded Future mock generator.

Tests follow TDD RED-GREEN-REFACTOR cycle.
These tests should FAIL initially (RED phase).
"""
import pytest
from datetime import datetime


class TestRecordedFutureMock:
    """Tests for RecordedFutureMock risk score generator."""

    def test_risk_score_calculation_high_cvss_high_epss(self):
        """
        RED: Test that high CVSS + high EPSS + exploit = high risk score (≥90).

        Expected behavior:
        - CVSS 9.8 → 39.2 points (40% weight)
        - EPSS 0.95 → 28.5 points (30% weight)
        - Known exploited → 20 points
        - Age 15 days → 10 points (recent)
        - Total: ~98 points → Risk Category: Critical
        """
        from src.generators.enrichment.recorded_future_mock import RecordedFutureMock

        mock = RecordedFutureMock()

        result = mock.calculate_risk_score(
            cve_id="CVE-2024-0001",
            cvss_score=9.8,
            epss_score=0.95,
            known_exploited=True,
            age_days=15
        )

        # High risk score expected
        assert result["risk_score"] >= 90, f"Expected risk score ≥90, got {result['risk_score']}"
        assert result["risk_category"] == "Critical"

        # Risk vector components should be present
        assert "risk_vector" in result
        assert "cvss_component" in result["risk_vector"]
        assert "epss_component" in result["risk_vector"]
        assert "exploit_component" in result["risk_vector"]
        assert "age_component" in result["risk_vector"]

        # Should assign threat actors to high-risk CVEs
        assert len(result["threat_actors"]) >= 1, "High-risk CVE should have threat actors assigned"

        # Metadata
        assert result["enrichment_source"] == "synthetic_recorded_future"
        assert "generated_at" in result

    def test_risk_score_calculation_low_cvss_low_epss(self):
        """
        RED: Test that low CVSS + low EPSS + no exploit = low risk score (≤40).

        Expected behavior:
        - CVSS 3.2 → 12.8 points (40% weight)
        - EPSS 0.01 → 0.3 points (30% weight)
        - Not exploited → 0 points
        - Age 400 days → 2 points (old)
        - Total: ~15 points → Risk Category: Low
        """
        from src.generators.enrichment.recorded_future_mock import RecordedFutureMock

        mock = RecordedFutureMock()

        result = mock.calculate_risk_score(
            cve_id="CVE-2024-9999",
            cvss_score=3.2,
            epss_score=0.01,
            known_exploited=False,
            age_days=400
        )

        # Low risk score expected
        assert result["risk_score"] <= 40, f"Expected risk score ≤40, got {result['risk_score']}"
        assert result["risk_category"] in ["Low", "Medium"]

        # No threat actors for low-risk CVEs
        assert len(result["threat_actors"]) == 0, "Low-risk CVE should not have threat actors"

    def test_threat_actors_assigned_to_high_risk_only(self):
        """
        RED: Test that threat actors are only assigned to high-risk CVEs (score ≥80, known_exploited=True).

        This ensures realistic synthetic data where APT groups target critical vulnerabilities.
        """
        from src.generators.enrichment.recorded_future_mock import RecordedFutureMock

        mock = RecordedFutureMock()

        # High risk with exploit → should have APTs
        high_risk = mock.calculate_risk_score(
            cve_id="CVE-2024-0002",
            cvss_score=9.5,
            epss_score=0.85,
            known_exploited=True,
            age_days=20
        )
        assert high_risk["risk_score"] >= 80
        assert len(high_risk["threat_actors"]) >= 1, "High-risk exploited CVE should have threat actors"

        # Medium risk without exploit → should NOT have APTs
        medium_risk = mock.calculate_risk_score(
            cve_id="CVE-2024-0003",
            cvss_score=6.5,
            epss_score=0.5,
            known_exploited=False,
            age_days=100
        )
        assert medium_risk["risk_score"] < 80
        assert len(medium_risk["threat_actors"]) == 0, "Medium-risk non-exploited CVE should not have threat actors"

    def test_campaigns_generated_for_recent_high_risk(self):
        """
        RED: Test that campaigns are only generated for recent (≤90 days) high-risk (≥70) CVEs.
        """
        from src.generators.enrichment.recorded_future_mock import RecordedFutureMock

        mock = RecordedFutureMock()

        # Recent + high risk → should have campaigns
        recent_high = mock.calculate_risk_score(
            cve_id="CVE-2024-0004",
            cvss_score=8.5,
            epss_score=0.75,
            known_exploited=True,
            age_days=30
        )
        assert recent_high["risk_score"] >= 70
        assert len(recent_high["campaigns"]) >= 1, "Recent high-risk CVE should have campaigns"

        # Old + high risk → should NOT have campaigns
        old_high = mock.calculate_risk_score(
            cve_id="CVE-2024-0005",
            cvss_score=8.5,
            epss_score=0.75,
            known_exploited=True,
            age_days=200
        )
        assert old_high["risk_score"] >= 70
        assert len(old_high["campaigns"]) == 0, "Old CVE should not have active campaigns"

    def test_risk_score_correlation_with_cvss_epss(self):
        """
        RED: Test that risk scores correlate highly with CVSS + EPSS (correlation ≥0.8).

        This ensures synthetic data is realistic.
        """
        from src.generators.enrichment.recorded_future_mock import RecordedFutureMock
        import statistics

        mock = RecordedFutureMock()

        # Generate multiple risk scores
        test_cases = [
            {"cvss": 9.8, "epss": 0.95, "exploit": True, "age": 15},
            {"cvss": 9.0, "epss": 0.80, "exploit": True, "age": 30},
            {"cvss": 7.5, "epss": 0.60, "exploit": False, "age": 60},
            {"cvss": 5.0, "epss": 0.30, "exploit": False, "age": 120},
            {"cvss": 3.0, "epss": 0.05, "exploit": False, "age": 300},
        ]

        risk_scores = []
        combined_scores = []  # CVSS + EPSS normalized

        for tc in test_cases:
            result = mock.calculate_risk_score(
                cve_id=f"CVE-2024-TEST",
                cvss_score=tc["cvss"],
                epss_score=tc["epss"],
                known_exploited=tc["exploit"],
                age_days=tc["age"]
            )
            risk_scores.append(result["risk_score"])
            # Normalize CVSS (0-10) + EPSS (0-1) to 0-100 scale
            combined = (tc["cvss"] / 10.0) * 50 + tc["epss"] * 50
            combined_scores.append(combined)

        # Calculate Pearson correlation
        def pearson_correlation(x, y):
            n = len(x)
            mean_x = statistics.mean(x)
            mean_y = statistics.mean(y)
            numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
            denominator = (sum((x[i] - mean_x) ** 2 for i in range(n)) *
                          sum((y[i] - mean_y) ** 2 for i in range(n))) ** 0.5
            return numerator / denominator if denominator != 0 else 0

        correlation = pearson_correlation(risk_scores, combined_scores)
        assert correlation >= 0.8, f"Correlation {correlation:.2f} below required 0.8"

    def test_risk_score_clamped_to_0_100(self):
        """
        RED: Test that risk scores are always in range [0, 100].
        """
        from src.generators.enrichment.recorded_future_mock import RecordedFutureMock

        mock = RecordedFutureMock()

        # Extreme high values
        result_high = mock.calculate_risk_score(
            cve_id="CVE-2024-MAX",
            cvss_score=10.0,
            epss_score=1.0,
            known_exploited=True,
            age_days=1
        )
        assert 0 <= result_high["risk_score"] <= 100

        # Extreme low values
        result_low = mock.calculate_risk_score(
            cve_id="CVE-2024-MIN",
            cvss_score=0.0,
            epss_score=0.0,
            known_exploited=False,
            age_days=1000
        )
        assert 0 <= result_low["risk_score"] <= 100

    def test_age_component_weights_correctly(self):
        """
        RED: Test that age component follows correct weighting:
        - 0-30 days: 10 points
        - 31-90 days: 7 points
        - 91-365 days: 4 points
        - >365 days: 2 points
        """
        from src.generators.enrichment.recorded_future_mock import RecordedFutureMock

        mock = RecordedFutureMock()

        # Same CVSS/EPSS/exploit, different ages
        base_params = {
            "cve_id": "CVE-2024-AGE",
            "cvss_score": 7.0,
            "epss_score": 0.5,
            "known_exploited": False,
        }

        result_0_30 = mock.calculate_risk_score(**base_params, age_days=15)
        result_31_90 = mock.calculate_risk_score(**base_params, age_days=60)
        result_91_365 = mock.calculate_risk_score(**base_params, age_days=180)
        result_365_plus = mock.calculate_risk_score(**base_params, age_days=500)

        # Extract age components
        age_0_30 = result_0_30["risk_vector"]["age_component"]
        age_31_90 = result_31_90["risk_vector"]["age_component"]
        age_91_365 = result_91_365["risk_vector"]["age_component"]
        age_365_plus = result_365_plus["risk_vector"]["age_component"]

        assert age_0_30 == 10, f"Expected 10 for 0-30 days, got {age_0_30}"
        assert age_31_90 == 7, f"Expected 7 for 31-90 days, got {age_31_90}"
        assert age_91_365 == 4, f"Expected 4 for 91-365 days, got {age_91_365}"
        assert age_365_plus == 2, f"Expected 2 for >365 days, got {age_365_plus}"
