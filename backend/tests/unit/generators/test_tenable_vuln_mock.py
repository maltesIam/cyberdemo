"""Unit tests for Tenable VPR vulnerability mock generator.

Tests follow TDD RED-GREEN-REFACTOR cycle.
These tests should FAIL initially (RED phase) as the implementation may not exist or match specs.
"""
import pytest
from datetime import datetime


class TestTenableVPRVulnMock:
    """Tests for TenableVPRMock vulnerability priority rating generator."""

    def test_high_risk_cve_gets_high_vpr(self):
        """
        RED: Test that high CVSS + high threat + critical assets = high VPR (>=8.0).

        VPR formula:
        - CVSS (35%): 9.8 / 10 * 3.5 = 3.43
        - Threat (35%): min(3.5, 0.9 * 2.5 + 1.0) = min(3.5, 3.25) = 3.25
        - Asset criticality (20%): critical = 2.0
        - Product coverage (10%): 0.8 * 1.0 = 0.8
        - Total: ~9.5
        """
        from src.generators.enrichment.tenable_vuln_mock import TenableVPRMock

        mock = TenableVPRMock()

        result = mock.calculate_vpr(
            cvss_score=9.8,
            epss_score=0.9,
            asset_criticality="critical",
            known_exploited=True,
            age_days=20,
            product_coverage=0.8
        )

        assert result["vpr_score"] >= 8.0, f"Expected VPR >=8.0, got {result['vpr_score']}"

    def test_low_risk_cve_gets_low_vpr(self):
        """
        RED: Test that low CVSS + low threat + low criticality = low VPR (<=4.0).

        VPR formula:
        - CVSS (35%): 3.0 / 10 * 3.5 = 1.05
        - Threat (35%): 0.05 * 2.5 + 0 = 0.125
        - Asset criticality (20%): low = 0.5
        - Product coverage (10%): 0.1 * 1.0 = 0.1
        - Total: ~1.78
        """
        from src.generators.enrichment.tenable_vuln_mock import TenableVPRMock

        mock = TenableVPRMock()

        result = mock.calculate_vpr(
            cvss_score=3.0,
            epss_score=0.05,
            asset_criticality="low",
            known_exploited=False,
            age_days=500,
            product_coverage=0.1
        )

        assert result["vpr_score"] <= 4.0, f"Expected VPR <=4.0, got {result['vpr_score']}"

    def test_score_clamped_to_valid_range(self):
        """
        RED: Test that VPR scores are always in range [0.0, 10.0].
        """
        from src.generators.enrichment.tenable_vuln_mock import TenableVPRMock

        mock = TenableVPRMock()

        # Maximum values
        result_max = mock.calculate_vpr(
            cvss_score=10.0,
            epss_score=1.0,
            asset_criticality="critical",
            known_exploited=True,
            age_days=1,
            product_coverage=1.0
        )
        assert 0.0 <= result_max["vpr_score"] <= 10.0

        # Minimum values
        result_min = mock.calculate_vpr(
            cvss_score=0.0,
            epss_score=0.0,
            asset_criticality="low",
            known_exploited=False,
            age_days=1000,
            product_coverage=0.0
        )
        assert 0.0 <= result_min["vpr_score"] <= 10.0

    def test_known_exploited_increases_vpr(self):
        """
        RED: Test that known_exploited=True increases VPR by adding to threat component.
        """
        from src.generators.enrichment.tenable_vuln_mock import TenableVPRMock

        mock = TenableVPRMock()

        base_params = {
            "cvss_score": 7.0,
            "epss_score": 0.5,
            "asset_criticality": "medium",
            "age_days": 60,
            "product_coverage": 0.5
        }

        result_without = mock.calculate_vpr(**base_params, known_exploited=False)
        result_with = mock.calculate_vpr(**base_params, known_exploited=True)

        # Exploited should increase VPR
        assert result_with["vpr_score"] > result_without["vpr_score"]
        # Threat component should be higher
        assert result_with["vpr_components"]["threat"] > result_without["vpr_components"]["threat"]

    def test_asset_criticality_mapping(self):
        """
        RED: Test that asset criticality maps correctly:
        - critical: 2.0 points
        - high: 1.5 points
        - medium: 1.0 points
        - low: 0.5 points
        """
        from src.generators.enrichment.tenable_vuln_mock import TenableVPRMock

        mock = TenableVPRMock()

        base_params = {
            "cvss_score": 7.0,
            "epss_score": 0.5,
            "known_exploited": False,
            "age_days": 100,
            "product_coverage": 0.5
        }

        result_critical = mock.calculate_vpr(**base_params, asset_criticality="critical")
        result_high = mock.calculate_vpr(**base_params, asset_criticality="high")
        result_medium = mock.calculate_vpr(**base_params, asset_criticality="medium")
        result_low = mock.calculate_vpr(**base_params, asset_criticality="low")

        assert result_critical["vpr_components"]["asset_criticality"] == 2.0
        assert result_high["vpr_components"]["asset_criticality"] == 1.5
        assert result_medium["vpr_components"]["asset_criticality"] == 1.0
        assert result_low["vpr_components"]["asset_criticality"] == 0.5

    def test_threat_component_capped_at_3_5(self):
        """
        RED: Test that threat component (EPSS * 2.5 + exploit bonus) is capped at 3.5.
        """
        from src.generators.enrichment.tenable_vuln_mock import TenableVPRMock

        mock = TenableVPRMock()

        # Maximum threat scenario: EPSS 1.0 * 2.5 + 1.0 = 3.5
        result = mock.calculate_vpr(
            cvss_score=5.0,
            epss_score=1.0,
            asset_criticality="medium",
            known_exploited=True,
            age_days=10,
            product_coverage=0.5
        )

        threat_component = result["vpr_components"]["threat"]
        assert threat_component <= 3.5, f"Threat component {threat_component} exceeds cap of 3.5"

    def test_product_coverage_impact(self):
        """
        RED: Test that product coverage (0.0-1.0) impacts VPR correctly.
        """
        from src.generators.enrichment.tenable_vuln_mock import TenableVPRMock

        mock = TenableVPRMock()

        base_params = {
            "cvss_score": 7.0,
            "epss_score": 0.5,
            "asset_criticality": "high",
            "known_exploited": False,
            "age_days": 60
        }

        result_0 = mock.calculate_vpr(**base_params, product_coverage=0.0)
        result_50 = mock.calculate_vpr(**base_params, product_coverage=0.5)
        result_100 = mock.calculate_vpr(**base_params, product_coverage=1.0)

        # VPR should increase with coverage
        assert result_0["vpr_score"] < result_50["vpr_score"]
        assert result_50["vpr_score"] < result_100["vpr_score"]

        # Coverage component should match expected values
        assert result_0["vpr_components"]["product_coverage"] == 0.0
        assert result_50["vpr_components"]["product_coverage"] == 0.5
        assert result_100["vpr_components"]["product_coverage"] == 1.0

    def test_cvss_component_weight(self):
        """
        RED: Test CVSS component is 35% weight (max 3.5 points).
        """
        from src.generators.enrichment.tenable_vuln_mock import TenableVPRMock

        mock = TenableVPRMock()

        # CVSS 10.0 should give max 3.5 points
        result = mock.calculate_vpr(
            cvss_score=10.0,
            epss_score=0.0,
            asset_criticality="low",
            known_exploited=False,
            age_days=1000,
            product_coverage=0.0
        )

        assert result["vpr_components"]["cvss"] == 3.5

    def test_return_format_correct(self):
        """
        RED: Test that return format contains all required fields.
        """
        from src.generators.enrichment.tenable_vuln_mock import TenableVPRMock

        mock = TenableVPRMock()

        result = mock.calculate_vpr(
            cvss_score=7.0,
            epss_score=0.5,
            asset_criticality="medium",
            known_exploited=False,
            age_days=60,
            product_coverage=0.5
        )

        # Required top-level fields
        assert "vpr_score" in result
        assert "vpr_components" in result
        assert "enrichment_source" in result
        assert "generated_at" in result

        # Required vpr_components fields
        assert "cvss" in result["vpr_components"]
        assert "threat" in result["vpr_components"]
        assert "asset_criticality" in result["vpr_components"]
        assert "product_coverage" in result["vpr_components"]

    def test_enrichment_source_field(self):
        """
        RED: Test that enrichment_source field is correctly set.
        """
        from src.generators.enrichment.tenable_vuln_mock import TenableVPRMock

        mock = TenableVPRMock()

        result = mock.calculate_vpr(
            cvss_score=7.0,
            epss_score=0.5,
            asset_criticality="medium",
            known_exploited=False,
            age_days=60,
            product_coverage=0.5
        )

        assert result["enrichment_source"] == "synthetic_tenable_vuln"

    def test_vpr_correlation_with_cvss(self):
        """
        RED: Test that VPR scores correlate with CVSS (since CVSS is 35% of VPR).
        """
        from src.generators.enrichment.tenable_vuln_mock import TenableVPRMock

        mock = TenableVPRMock()

        fixed_params = {
            "epss_score": 0.5,
            "asset_criticality": "medium",
            "known_exploited": False,
            "age_days": 100,
            "product_coverage": 0.5
        }

        result_low = mock.calculate_vpr(cvss_score=3.0, **fixed_params)
        result_med = mock.calculate_vpr(cvss_score=6.0, **fixed_params)
        result_high = mock.calculate_vpr(cvss_score=9.0, **fixed_params)

        # VPR should increase with CVSS
        assert result_low["vpr_score"] < result_med["vpr_score"]
        assert result_med["vpr_score"] < result_high["vpr_score"]

    def test_case_insensitive_criticality(self):
        """
        RED: Test that asset criticality is case-insensitive.
        """
        from src.generators.enrichment.tenable_vuln_mock import TenableVPRMock

        mock = TenableVPRMock()

        base_params = {
            "cvss_score": 7.0,
            "epss_score": 0.5,
            "known_exploited": False,
            "age_days": 100,
            "product_coverage": 0.5
        }

        result_lower = mock.calculate_vpr(**base_params, asset_criticality="critical")
        result_upper = mock.calculate_vpr(**base_params, asset_criticality="CRITICAL")
        result_mixed = mock.calculate_vpr(**base_params, asset_criticality="Critical")

        assert result_lower["vpr_components"]["asset_criticality"] == 2.0
        assert result_upper["vpr_components"]["asset_criticality"] == 2.0
        assert result_mixed["vpr_components"]["asset_criticality"] == 2.0
