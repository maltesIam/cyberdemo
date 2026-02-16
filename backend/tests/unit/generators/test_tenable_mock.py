"""Unit tests for Tenable VPR mock generator.

Tests follow TDD RED-GREEN-REFACTOR cycle.
These tests should FAIL initially (RED phase).
"""
import pytest


class TestTenableVPRMock:
    """Tests for TenableVPRMock generator."""

    def test_vpr_score_calculation(self):
        """
        RED: Test VPR score calculation with all components.

        VPR formula:
        - CVSS (35%): 9.8 / 10 * 3.5 = 3.43
        - Threat (35%): EPSS (0.89 * 2.5) + exploit (1.0) = 2.225 + 1.0 = 3.225 (capped at 3.5)
        - Asset criticality (20%): critical = 2.0
        - Product coverage (10%): 0.8 * 1.0 = 0.8
        - Total: 3.43 + 3.225 + 2.0 + 0.8 = 9.455 → 9.5
        """
        from src.generators.enrichment.tenable_mock import TenableVPRMock

        mock = TenableVPRMock()

        result = mock.calculate_vpr(
            cvss_score=9.8,
            epss_score=0.89,
            asset_criticality="critical",
            known_exploited=True,
            age_days=20,
            product_coverage=0.8
        )

        # VPR score should be high (≥8.0)
        assert result["vpr_score"] >= 8.0, f"Expected VPR ≥8.0, got {result['vpr_score']}"
        assert result["vpr_score"] <= 10.0, f"VPR score {result['vpr_score']} exceeds maximum 10.0"

        # Components should be present
        assert "vpr_components" in result
        assert "cvss" in result["vpr_components"]
        assert "threat" in result["vpr_components"]
        assert "asset_criticality" in result["vpr_components"]
        assert "product_coverage" in result["vpr_components"]

        # Metadata
        assert result["enrichment_source"] == "synthetic_tenable"
        assert "generated_at" in result

    def test_vpr_components_weighted_correctly(self):
        """
        RED: Test that VPR components follow correct weights:
        - CVSS: 35% (max 3.5 points)
        - Threat: 35% (max 3.5 points)
        - Asset criticality: 20% (max 2.0 points)
        - Product coverage: 10% (max 1.0 points)
        """
        from src.generators.enrichment.tenable_mock import TenableVPRMock

        mock = TenableVPRMock()

        # Maximum values for all components
        result_max = mock.calculate_vpr(
            cvss_score=10.0,
            epss_score=1.0,
            asset_criticality="critical",
            known_exploited=True,
            age_days=1,
            product_coverage=1.0
        )

        components = result_max["vpr_components"]

        # Check component maximums
        assert components["cvss"] <= 3.5, f"CVSS component {components['cvss']} exceeds max 3.5"
        assert components["threat"] <= 3.5, f"Threat component {components['threat']} exceeds max 3.5"
        assert components["asset_criticality"] <= 2.0, f"Criticality component {components['asset_criticality']} exceeds max 2.0"
        assert components["product_coverage"] <= 1.0, f"Coverage component {components['product_coverage']} exceeds max 1.0"

        # Total should be ≤10.0
        total = sum(components.values())
        assert total <= 10.0, f"Total VPR components {total} exceeds 10.0"

    def test_asset_criticality_mapping(self):
        """
        RED: Test that asset criticality maps correctly:
        - critical: 2.0 points
        - high: 1.5 points
        - medium: 1.0 points
        - low: 0.5 points
        """
        from src.generators.enrichment.tenable_mock import TenableVPRMock

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

        # VPR scores should decrease as criticality decreases
        assert result_critical["vpr_score"] > result_high["vpr_score"]
        assert result_high["vpr_score"] > result_medium["vpr_score"]
        assert result_medium["vpr_score"] > result_low["vpr_score"]

    def test_threat_component_caps_at_3_5(self):
        """
        RED: Test that threat component (EPSS + exploit) is capped at 3.5 points.

        Even if EPSS is 1.0 and exploit is True, threat should not exceed 3.5.
        """
        from src.generators.enrichment.tenable_mock import TenableVPRMock

        mock = TenableVPRMock()

        # Maximum threat scenario
        result = mock.calculate_vpr(
            cvss_score=5.0,
            epss_score=1.0,  # Max EPSS
            asset_criticality="medium",
            known_exploited=True,  # +1.0 exploit bonus
            age_days=10,
            product_coverage=0.5
        )

        threat_component = result["vpr_components"]["threat"]
        assert threat_component <= 3.5, f"Threat component {threat_component} exceeds cap of 3.5"

    def test_vpr_score_range_0_to_10(self):
        """
        RED: Test that VPR scores are always in range [0.0, 10.0].
        """
        from src.generators.enrichment.tenable_mock import TenableVPRMock

        mock = TenableVPRMock()

        # Test minimum values
        result_min = mock.calculate_vpr(
            cvss_score=0.0,
            epss_score=0.0,
            asset_criticality="low",
            known_exploited=False,
            age_days=1000,
            product_coverage=0.0
        )
        assert 0.0 <= result_min["vpr_score"] <= 10.0

        # Test maximum values
        result_max = mock.calculate_vpr(
            cvss_score=10.0,
            epss_score=1.0,
            asset_criticality="critical",
            known_exploited=True,
            age_days=1,
            product_coverage=1.0
        )
        assert 0.0 <= result_max["vpr_score"] <= 10.0

    def test_vpr_correlation_with_cvss(self):
        """
        RED: Test that VPR scores correlate with CVSS (since CVSS is 35% of VPR).

        Higher CVSS should generally result in higher VPR.
        """
        from src.generators.enrichment.tenable_mock import TenableVPRMock

        mock = TenableVPRMock()

        # Fixed other parameters
        fixed_params = {
            "epss_score": 0.5,
            "asset_criticality": "medium",
            "known_exploited": False,
            "age_days": 100,
            "product_coverage": 0.5
        }

        # Different CVSS values
        result_low = mock.calculate_vpr(cvss_score=3.0, **fixed_params)
        result_med = mock.calculate_vpr(cvss_score=6.0, **fixed_params)
        result_high = mock.calculate_vpr(cvss_score=9.0, **fixed_params)

        # VPR should increase with CVSS
        assert result_low["vpr_score"] < result_med["vpr_score"]
        assert result_med["vpr_score"] < result_high["vpr_score"]

    def test_product_coverage_impact(self):
        """
        RED: Test that product coverage (0.0-1.0) impacts VPR score correctly.

        Higher coverage = more assets affected = higher VPR.
        """
        from src.generators.enrichment.tenable_mock import TenableVPRMock

        mock = TenableVPRMock()

        base_params = {
            "cvss_score": 7.0,
            "epss_score": 0.5,
            "asset_criticality": "high",
            "known_exploited": False,
            "age_days": 60
        }

        result_0_coverage = mock.calculate_vpr(**base_params, product_coverage=0.0)
        result_50_coverage = mock.calculate_vpr(**base_params, product_coverage=0.5)
        result_100_coverage = mock.calculate_vpr(**base_params, product_coverage=1.0)

        # VPR should increase with coverage
        assert result_0_coverage["vpr_score"] < result_50_coverage["vpr_score"]
        assert result_50_coverage["vpr_score"] < result_100_coverage["vpr_score"]

        # Coverage component should match expected values
        assert result_0_coverage["vpr_components"]["product_coverage"] == 0.0
        assert result_50_coverage["vpr_components"]["product_coverage"] == 0.5
        assert result_100_coverage["vpr_components"]["product_coverage"] == 1.0
