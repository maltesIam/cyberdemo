"""
Unit tests for VulnRiskScoreCalculator.

Following TDD: These tests are written FIRST, before implementation.
The calculator computes a vulnerability risk score (0-100) based on:

Component Weights (sum to 100):
  - CVSS Score (25%): (cvss_v3_score / 10.0) * 25
  - EPSS Score (25%): epss_score * 25
  - KEV Status (15%): 15 if is_kev else 0
  - Exploit Maturity (15%):
      "weaponized" -> 15
      "poc" -> 10
      "unproven" -> 5
      "none" -> 0
  - Asset Impact (10%): (affected_critical_assets / total_critical_assets) * 10, capped at 10
  - Exposure (10%): 10 if shodan_exposed_count > 0 else 0

Risk Levels:
  - >= 85: Critical
  - >= 70: High
  - >= 40: Medium
  - < 40: Low
"""
import pytest

from src.services.vuln_risk_score import VulnRiskScoreCalculator


class TestMaxAndMinRisk:
    """Tests for extreme risk score scenarios."""

    @pytest.fixture
    def calculator(self):
        return VulnRiskScoreCalculator()

    def test_max_risk_cve(self, calculator):
        """
        Maximum risk CVE: CVSS 10, EPSS 1.0, KEV, weaponized exploit, exposed.
        Expected: 25 + 25 + 15 + 15 + 10 + 10 = 100
        """
        result = calculator.calculate_risk_score(
            cvss_v3_score=10.0,
            epss_score=1.0,
            is_kev=True,
            exploit_maturity="weaponized",
            affected_critical_assets=10,
            total_critical_assets=10,
            shodan_exposed_count=100,
        )
        assert result["risk_score"] == 100.0
        assert result["risk_level"] == "Critical"
        # Verify all components at max
        assert result["components"]["cvss"] == 25.0
        assert result["components"]["epss"] == 25.0
        assert result["components"]["kev"] == 15.0
        assert result["components"]["exploit"] == 15.0
        assert result["components"]["asset"] == 10.0
        assert result["components"]["exposure"] == 10.0

    def test_min_risk_cve(self, calculator):
        """
        Minimum risk CVE: CVSS 0, EPSS 0, no KEV, no exploit, no exposure.
        Expected: 0 + 0 + 0 + 0 + 0 + 0 = 0
        """
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="none",
            affected_critical_assets=0,
            total_critical_assets=1,
            shodan_exposed_count=0,
        )
        assert result["risk_score"] == 0.0
        assert result["risk_level"] == "Low"
        # Verify all components at min
        assert result["components"]["cvss"] == 0.0
        assert result["components"]["epss"] == 0.0
        assert result["components"]["kev"] == 0.0
        assert result["components"]["exploit"] == 0.0
        assert result["components"]["asset"] == 0.0
        assert result["components"]["exposure"] == 0.0


class TestCVSSComponent:
    """Tests for CVSS score component (25% weight)."""

    @pytest.fixture
    def calculator(self):
        return VulnRiskScoreCalculator()

    def test_cvss_component_scales_correctly(self, calculator):
        """CVSS component = (cvss_v3_score / 10.0) * 25"""
        # CVSS 5.0 -> (5.0 / 10.0) * 25 = 12.5
        result = calculator.calculate_risk_score(
            cvss_v3_score=5.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="none",
            affected_critical_assets=0,
            total_critical_assets=1,
            shodan_exposed_count=0,
        )
        assert result["components"]["cvss"] == 12.5

    def test_cvss_max_gives_25_points(self, calculator):
        """CVSS 10.0 -> 25 points."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=10.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="none",
        )
        assert result["components"]["cvss"] == 25.0

    def test_cvss_9_8_critical(self, calculator):
        """CVSS 9.8 (common critical) -> 24.5 points."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=9.8,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="none",
        )
        assert result["components"]["cvss"] == pytest.approx(24.5)

    def test_cvss_7_5_high(self, calculator):
        """CVSS 7.5 (high) -> 18.75 points."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=7.5,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="none",
        )
        assert result["components"]["cvss"] == pytest.approx(18.75)


class TestEPSSComponent:
    """Tests for EPSS score component (25% weight)."""

    @pytest.fixture
    def calculator(self):
        return VulnRiskScoreCalculator()

    def test_epss_component_scales_correctly(self, calculator):
        """EPSS component = epss_score * 25"""
        # EPSS 0.5 -> 0.5 * 25 = 12.5
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.5,
            is_kev=False,
            exploit_maturity="none",
            affected_critical_assets=0,
            total_critical_assets=1,
            shodan_exposed_count=0,
        )
        assert result["components"]["epss"] == 12.5

    def test_epss_max_gives_25_points(self, calculator):
        """EPSS 1.0 -> 25 points."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=1.0,
            is_kev=False,
            exploit_maturity="none",
        )
        assert result["components"]["epss"] == 25.0

    def test_epss_zero_gives_0_points(self, calculator):
        """EPSS 0.0 -> 0 points."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="none",
        )
        assert result["components"]["epss"] == 0.0

    def test_epss_high_probability(self, calculator):
        """EPSS 0.972 (high probability) -> 24.3 points."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.972,
            is_kev=False,
            exploit_maturity="none",
        )
        assert result["components"]["epss"] == pytest.approx(24.3)


class TestKEVComponent:
    """Tests for CISA KEV status component (15% weight)."""

    @pytest.fixture
    def calculator(self):
        return VulnRiskScoreCalculator()

    def test_kev_adds_15_points(self, calculator):
        """KEV = True -> 15 points."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.0,
            is_kev=True,
            exploit_maturity="none",
            affected_critical_assets=0,
            total_critical_assets=1,
            shodan_exposed_count=0,
        )
        assert result["components"]["kev"] == 15.0

    def test_no_kev_adds_0_points(self, calculator):
        """KEV = False -> 0 points."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="none",
            affected_critical_assets=0,
            total_critical_assets=1,
            shodan_exposed_count=0,
        )
        assert result["components"]["kev"] == 0.0


class TestExploitMaturityComponent:
    """Tests for exploit maturity component (15% weight)."""

    @pytest.fixture
    def calculator(self):
        return VulnRiskScoreCalculator()

    def test_weaponized_exploit_adds_15(self, calculator):
        """Weaponized exploit -> 15 points (max)."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="weaponized",
            affected_critical_assets=0,
            total_critical_assets=1,
            shodan_exposed_count=0,
        )
        assert result["components"]["exploit"] == 15.0

    def test_poc_exploit_adds_10(self, calculator):
        """PoC exploit -> 10 points."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="poc",
            affected_critical_assets=0,
            total_critical_assets=1,
            shodan_exposed_count=0,
        )
        assert result["components"]["exploit"] == 10.0

    def test_unproven_exploit_adds_5(self, calculator):
        """Unproven exploit -> 5 points."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="unproven",
            affected_critical_assets=0,
            total_critical_assets=1,
            shodan_exposed_count=0,
        )
        assert result["components"]["exploit"] == 5.0

    def test_no_exploit_adds_0(self, calculator):
        """No exploit -> 0 points."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="none",
            affected_critical_assets=0,
            total_critical_assets=1,
            shodan_exposed_count=0,
        )
        assert result["components"]["exploit"] == 0.0

    def test_unknown_exploit_maturity_treated_as_none(self, calculator):
        """Unknown exploit maturity value -> 0 points (safe default)."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="unknown_value",
            affected_critical_assets=0,
            total_critical_assets=1,
            shodan_exposed_count=0,
        )
        assert result["components"]["exploit"] == 0.0


class TestAssetImpactComponent:
    """Tests for asset impact component (10% weight)."""

    @pytest.fixture
    def calculator(self):
        return VulnRiskScoreCalculator()

    def test_asset_impact_scales_correctly(self, calculator):
        """Asset impact = (affected / total) * 10"""
        # 5 of 10 critical assets -> (5/10) * 10 = 5
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="none",
            affected_critical_assets=5,
            total_critical_assets=10,
            shodan_exposed_count=0,
        )
        assert result["components"]["asset"] == 5.0

    def test_asset_impact_capped_at_10(self, calculator):
        """Asset impact capped at 10, even if affected > total."""
        # 15 of 10 (impossible but should cap) -> 10
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="none",
            affected_critical_assets=15,
            total_critical_assets=10,
            shodan_exposed_count=0,
        )
        assert result["components"]["asset"] == 10.0

    def test_asset_impact_zero_total_handled(self, calculator):
        """Zero total_critical_assets should not cause division by zero."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="none",
            affected_critical_assets=5,
            total_critical_assets=0,
            shodan_exposed_count=0,
        )
        # Should default to 0 when total is 0
        assert result["components"]["asset"] == 0.0

    def test_asset_impact_all_affected(self, calculator):
        """All critical assets affected -> 10 points."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="none",
            affected_critical_assets=100,
            total_critical_assets=100,
            shodan_exposed_count=0,
        )
        assert result["components"]["asset"] == 10.0

    def test_asset_impact_none_affected(self, calculator):
        """No critical assets affected -> 0 points."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="none",
            affected_critical_assets=0,
            total_critical_assets=100,
            shodan_exposed_count=0,
        )
        assert result["components"]["asset"] == 0.0


class TestExposureComponent:
    """Tests for internet exposure component (10% weight)."""

    @pytest.fixture
    def calculator(self):
        return VulnRiskScoreCalculator()

    def test_exposure_adds_10_when_exposed(self, calculator):
        """Shodan exposed count > 0 -> 10 points."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="none",
            affected_critical_assets=0,
            total_critical_assets=1,
            shodan_exposed_count=1,
        )
        assert result["components"]["exposure"] == 10.0

    def test_exposure_adds_0_when_not_exposed(self, calculator):
        """Shodan exposed count = 0 -> 0 points."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="none",
            affected_critical_assets=0,
            total_critical_assets=1,
            shodan_exposed_count=0,
        )
        assert result["components"]["exposure"] == 0.0

    def test_exposure_high_count_still_10(self, calculator):
        """High exposure count still gives exactly 10 (not more)."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=0.0,
            epss_score=0.0,
            is_kev=False,
            exploit_maturity="none",
            affected_critical_assets=0,
            total_critical_assets=1,
            shodan_exposed_count=10000,
        )
        assert result["components"]["exposure"] == 10.0


class TestTotalWeights:
    """Tests for weight validation."""

    @pytest.fixture
    def calculator(self):
        return VulnRiskScoreCalculator()

    def test_total_weights_sum_to_100(self, calculator):
        """All component weights must sum to 100."""
        # Max values for all components
        result = calculator.calculate_risk_score(
            cvss_v3_score=10.0,
            epss_score=1.0,
            is_kev=True,
            exploit_maturity="weaponized",
            affected_critical_assets=10,
            total_critical_assets=10,
            shodan_exposed_count=100,
        )
        components = result["components"]
        total_components = (
            components["cvss"]
            + components["epss"]
            + components["kev"]
            + components["exploit"]
            + components["asset"]
            + components["exposure"]
        )
        assert total_components == 100.0
        assert result["risk_score"] == 100.0


class TestRiskScoreClamping:
    """Tests for risk score clamping."""

    @pytest.fixture
    def calculator(self):
        return VulnRiskScoreCalculator()

    def test_risk_score_clamped_to_0_100(self, calculator):
        """Risk score is always between 0 and 100."""
        # Even with edge cases, score should be clamped
        result = calculator.calculate_risk_score(
            cvss_v3_score=10.0,
            epss_score=1.0,
            is_kev=True,
            exploit_maturity="weaponized",
            affected_critical_assets=100,
            total_critical_assets=10,  # Intentionally higher affected than total
            shodan_exposed_count=1000,
        )
        assert 0 <= result["risk_score"] <= 100

    def test_negative_values_handled(self, calculator):
        """Negative input values should result in non-negative score."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=-1.0,
            epss_score=-0.5,
            is_kev=False,
            exploit_maturity="none",
            affected_critical_assets=-5,
            total_critical_assets=10,
            shodan_exposed_count=-1,
        )
        assert result["risk_score"] >= 0


class TestRiskLevel:
    """Tests for risk level classification."""

    @pytest.fixture
    def calculator(self):
        return VulnRiskScoreCalculator()

    def test_risk_level_critical_above_85(self, calculator):
        """Score >= 85 -> Critical."""
        # Create a score of exactly 85
        result = calculator.calculate_risk_score(
            cvss_v3_score=10.0,  # 25
            epss_score=1.0,      # 25
            is_kev=True,         # 15
            exploit_maturity="weaponized",  # 15
            affected_critical_assets=5,
            total_critical_assets=10,  # 5 points asset
            shodan_exposed_count=0,    # 0 exposure
        )
        # 25 + 25 + 15 + 15 + 5 + 0 = 85
        assert result["risk_score"] == 85.0
        assert result["risk_level"] == "Critical"

    def test_risk_level_critical_at_100(self, calculator):
        """Score = 100 -> Critical."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=10.0,
            epss_score=1.0,
            is_kev=True,
            exploit_maturity="weaponized",
            affected_critical_assets=10,
            total_critical_assets=10,
            shodan_exposed_count=100,
        )
        assert result["risk_level"] == "Critical"

    def test_risk_level_high_70_to_84(self, calculator):
        """Score 70-84 -> High."""
        # Create a score of exactly 70
        result = calculator.calculate_risk_score(
            cvss_v3_score=10.0,  # 25
            epss_score=1.0,      # 25
            is_kev=False,        # 0
            exploit_maturity="weaponized",  # 15
            affected_critical_assets=5,
            total_critical_assets=10,  # 5 points asset
            shodan_exposed_count=0,    # 0 exposure
        )
        # 25 + 25 + 0 + 15 + 5 + 0 = 70
        assert result["risk_score"] == 70.0
        assert result["risk_level"] == "High"

    def test_risk_level_high_at_84(self, calculator):
        """Score = 84 -> High (not Critical)."""
        # CVSS 9.6 gives 24, plus other components to reach 84
        result = calculator.calculate_risk_score(
            cvss_v3_score=9.6,   # 24
            epss_score=1.0,      # 25
            is_kev=True,         # 15
            exploit_maturity="weaponized",  # 15
            affected_critical_assets=5,
            total_critical_assets=10,  # 5 points asset
            shodan_exposed_count=0,    # 0 exposure
        )
        # 24 + 25 + 15 + 15 + 5 + 0 = 84
        assert result["risk_score"] == 84.0
        assert result["risk_level"] == "High"

    def test_risk_level_medium_40_to_69(self, calculator):
        """Score 40-69 -> Medium."""
        # Create a score of exactly 40
        result = calculator.calculate_risk_score(
            cvss_v3_score=6.0,   # 15
            epss_score=0.4,      # 10
            is_kev=False,        # 0
            exploit_maturity="poc",  # 10
            affected_critical_assets=5,
            total_critical_assets=10,  # 5 points asset
            shodan_exposed_count=0,    # 0 exposure
        )
        # 15 + 10 + 0 + 10 + 5 + 0 = 40
        assert result["risk_score"] == 40.0
        assert result["risk_level"] == "Medium"

    def test_risk_level_low_below_40(self, calculator):
        """Score < 40 -> Low."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=4.0,   # 10
            epss_score=0.2,      # 5
            is_kev=False,        # 0
            exploit_maturity="none",  # 0
            affected_critical_assets=0,
            total_critical_assets=10,  # 0 points asset
            shodan_exposed_count=0,    # 0 exposure
        )
        # 10 + 5 + 0 + 0 + 0 + 0 = 15
        assert result["risk_score"] == 15.0
        assert result["risk_level"] == "Low"

    def test_risk_level_low_at_39(self, calculator):
        """Score = 39 -> Low (not Medium)."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=5.6,   # 14
            epss_score=0.4,      # 10
            is_kev=False,        # 0
            exploit_maturity="poc",  # 10
            affected_critical_assets=5,
            total_critical_assets=10,  # 5 points asset
            shodan_exposed_count=0,    # 0 exposure
        )
        # 14 + 10 + 0 + 10 + 5 + 0 = 39
        assert result["risk_score"] == 39.0
        assert result["risk_level"] == "Low"


class TestComponentsReturnedInResult:
    """Tests for result structure."""

    @pytest.fixture
    def calculator(self):
        return VulnRiskScoreCalculator()

    def test_components_returned_in_result(self, calculator):
        """Result includes components breakdown."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=7.5,
            epss_score=0.5,
            is_kev=True,
            exploit_maturity="poc",
            affected_critical_assets=3,
            total_critical_assets=10,
            shodan_exposed_count=5,
        )

        # Verify result structure
        assert "risk_score" in result
        assert "risk_level" in result
        assert "components" in result

        # Verify components structure
        components = result["components"]
        assert "cvss" in components
        assert "epss" in components
        assert "kev" in components
        assert "exploit" in components
        assert "asset" in components
        assert "exposure" in components

    def test_result_types(self, calculator):
        """Result values have correct types."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=7.5,
            epss_score=0.5,
            is_kev=True,
            exploit_maturity="poc",
            affected_critical_assets=3,
            total_critical_assets=10,
            shodan_exposed_count=5,
        )

        assert isinstance(result["risk_score"], float)
        assert isinstance(result["risk_level"], str)
        assert isinstance(result["components"], dict)

        for key in ["cvss", "epss", "kev", "exploit", "asset", "exposure"]:
            assert isinstance(result["components"][key], float)


class TestGetRiskLevel:
    """Tests for _get_risk_level helper method."""

    @pytest.fixture
    def calculator(self):
        return VulnRiskScoreCalculator()

    def test_get_risk_level_boundary_values(self, calculator):
        """Test boundary values for risk level classification."""
        assert calculator._get_risk_level(100.0) == "Critical"
        assert calculator._get_risk_level(85.0) == "Critical"
        assert calculator._get_risk_level(84.9) == "High"
        assert calculator._get_risk_level(70.0) == "High"
        assert calculator._get_risk_level(69.9) == "Medium"
        assert calculator._get_risk_level(40.0) == "Medium"
        assert calculator._get_risk_level(39.9) == "Low"
        assert calculator._get_risk_level(0.0) == "Low"


class TestDefaultParameters:
    """Tests for default parameter values."""

    @pytest.fixture
    def calculator(self):
        return VulnRiskScoreCalculator()

    def test_default_asset_parameters(self, calculator):
        """Default asset parameters work correctly."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=5.0,
            epss_score=0.5,
            is_kev=False,
            exploit_maturity="none",
            # Using defaults: affected_critical_assets=0, total_critical_assets=1
        )
        assert result["components"]["asset"] == 0.0
        assert result["components"]["exposure"] == 0.0

    def test_only_required_parameters(self, calculator):
        """Calculator works with only required parameters."""
        result = calculator.calculate_risk_score(
            cvss_v3_score=9.8,
            epss_score=0.972,
            is_kev=True,
            exploit_maturity="weaponized",
        )
        # Should work without optional parameters
        assert result["risk_score"] > 0
        assert result["risk_level"] in ["Critical", "High", "Medium", "Low"]


class TestRealWorldScenarios:
    """Tests for realistic CVE scenarios."""

    @pytest.fixture
    def calculator(self):
        return VulnRiskScoreCalculator()

    def test_log4j_scenario(self, calculator):
        """
        Log4Shell-like CVE: CVSS 10, high EPSS, KEV, weaponized, widely exposed.
        Expected: Critical risk.
        """
        result = calculator.calculate_risk_score(
            cvss_v3_score=10.0,
            epss_score=0.972,
            is_kev=True,
            exploit_maturity="weaponized",
            affected_critical_assets=50,
            total_critical_assets=100,
            shodan_exposed_count=1000000,
        )
        assert result["risk_level"] == "Critical"
        assert result["risk_score"] >= 90

    def test_medium_severity_no_exploit(self, calculator):
        """
        Medium severity CVE with no known exploits.
        Expected: Low to Medium risk.
        """
        result = calculator.calculate_risk_score(
            cvss_v3_score=5.3,
            epss_score=0.001,
            is_kev=False,
            exploit_maturity="none",
            affected_critical_assets=0,
            total_critical_assets=10,
            shodan_exposed_count=0,
        )
        assert result["risk_level"] in ["Low", "Medium"]
        assert result["risk_score"] < 40

    def test_high_cvss_no_exploitation(self, calculator):
        """
        High CVSS but no exploitation evidence.
        Expected: Medium risk (CVSS alone is not enough).
        """
        result = calculator.calculate_risk_score(
            cvss_v3_score=9.8,
            epss_score=0.05,
            is_kev=False,
            exploit_maturity="none",
            affected_critical_assets=0,
            total_critical_assets=10,
            shodan_exposed_count=0,
        )
        # 24.5 (CVSS) + 1.25 (EPSS) + 0 + 0 + 0 + 0 = 25.75
        assert result["risk_level"] == "Low"
        assert result["risk_score"] < 40

    def test_low_cvss_but_kev_and_weaponized(self, calculator):
        """
        Lower CVSS but actively exploited (KEV + weaponized).
        Expected: Higher risk due to exploitation.
        """
        result = calculator.calculate_risk_score(
            cvss_v3_score=6.5,
            epss_score=0.8,
            is_kev=True,
            exploit_maturity="weaponized",
            affected_critical_assets=5,
            total_critical_assets=10,
            shodan_exposed_count=100,
        )
        # 16.25 + 20 + 15 + 15 + 5 + 10 = 81.25
        assert result["risk_level"] == "High"
        assert result["risk_score"] >= 70
