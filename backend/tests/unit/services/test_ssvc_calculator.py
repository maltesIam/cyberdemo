"""
SSVC (Stakeholder-Specific Vulnerability Categorization) Calculator Tests.

TDD RED PHASE: All tests written BEFORE implementation.

SSVC Decision Tree:
1. Exploitation Status: "active" | "poc" | "none"
2. Automatable: True | False
3. Technical Impact: "total" | "partial"
4. Decision: "Act" | "Attend" | "Track*" | "Track"
"""
import pytest

from src.services.ssvc_calculator import SSVCCalculator


class TestSSVCExploitationStatus:
    """Tests for _determine_exploitation_status method."""

    def setup_method(self):
        self.calculator = SSVCCalculator()

    def test_kev_cve_is_active_exploitation(self):
        """KEV (Known Exploited Vulnerability) should result in 'active' exploitation."""
        result = self.calculator._determine_exploitation_status(
            is_kev=True,
            epss_score=0.1,
            exploit_count=0
        )
        assert result == "active"

    def test_high_epss_is_active_exploitation(self):
        """EPSS score > 0.70 should result in 'active' exploitation."""
        result = self.calculator._determine_exploitation_status(
            is_kev=False,
            epss_score=0.75,
            exploit_count=0
        )
        assert result == "active"

    def test_epss_exactly_at_threshold_is_not_active(self):
        """EPSS score exactly at 0.70 should NOT be 'active' (need > 0.70)."""
        result = self.calculator._determine_exploitation_status(
            is_kev=False,
            epss_score=0.70,
            exploit_count=0
        )
        assert result != "active"

    def test_exploit_count_is_poc_exploitation(self):
        """Exploit count > 0 without KEV/high EPSS should be 'poc'."""
        result = self.calculator._determine_exploitation_status(
            is_kev=False,
            epss_score=0.3,
            exploit_count=5
        )
        assert result == "poc"

    def test_no_exploit_is_none_exploitation(self):
        """No KEV, low EPSS, no exploits should result in 'none'."""
        result = self.calculator._determine_exploitation_status(
            is_kev=False,
            epss_score=0.1,
            exploit_count=0
        )
        assert result == "none"

    def test_kev_takes_priority_over_exploit_count(self):
        """KEV should result in 'active' even with exploit count."""
        result = self.calculator._determine_exploitation_status(
            is_kev=True,
            epss_score=0.1,
            exploit_count=10
        )
        assert result == "active"


class TestSSVCAutomatable:
    """Tests for _is_automatable method."""

    def setup_method(self):
        self.calculator = SSVCCalculator()

    def test_network_low_none_is_automatable(self):
        """AV:N, AC:L, PR:N should be automatable."""
        vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        result = self.calculator._is_automatable(vector)
        assert result is True

    def test_local_is_not_automatable(self):
        """AV:L (Local) should NOT be automatable."""
        vector = "CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        result = self.calculator._is_automatable(vector)
        assert result is False

    def test_adjacent_network_is_not_automatable(self):
        """AV:A (Adjacent Network) should NOT be automatable."""
        vector = "CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        result = self.calculator._is_automatable(vector)
        assert result is False

    def test_physical_is_not_automatable(self):
        """AV:P (Physical) should NOT be automatable."""
        vector = "CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        result = self.calculator._is_automatable(vector)
        assert result is False

    def test_high_complexity_is_not_automatable(self):
        """AC:H (High complexity) should NOT be automatable."""
        vector = "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H"
        result = self.calculator._is_automatable(vector)
        assert result is False

    def test_requires_low_privileges_is_not_automatable(self):
        """PR:L (Low privileges required) should NOT be automatable."""
        vector = "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H"
        result = self.calculator._is_automatable(vector)
        assert result is False

    def test_requires_high_privileges_is_not_automatable(self):
        """PR:H (High privileges required) should NOT be automatable."""
        vector = "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H"
        result = self.calculator._is_automatable(vector)
        assert result is False


class TestSSVCTechnicalImpact:
    """Tests for _determine_technical_impact method."""

    def setup_method(self):
        self.calculator = SSVCCalculator()

    def test_high_cvss_is_total_impact(self):
        """CVSS score >= 9.0 should result in 'total' impact."""
        vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L"
        result = self.calculator._determine_technical_impact(
            cvss_v3_score=9.5,
            cvss_v3_vector=vector
        )
        assert result == "total"

    def test_cvss_exactly_at_9_is_total_impact(self):
        """CVSS score exactly 9.0 should result in 'total' impact."""
        vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L"
        result = self.calculator._determine_technical_impact(
            cvss_v3_score=9.0,
            cvss_v3_vector=vector
        )
        assert result == "total"

    def test_low_cvss_is_partial_impact(self):
        """CVSS score < 9.0 without C:H AND I:H should be 'partial'."""
        vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L"
        result = self.calculator._determine_technical_impact(
            cvss_v3_score=5.0,
            cvss_v3_vector=vector
        )
        assert result == "partial"

    def test_high_cia_is_total_impact(self):
        """C:H AND I:H in vector should result in 'total' even with lower CVSS."""
        vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L"
        result = self.calculator._determine_technical_impact(
            cvss_v3_score=7.0,
            cvss_v3_vector=vector
        )
        assert result == "total"

    def test_only_high_confidentiality_is_partial(self):
        """Only C:H (without I:H) should result in 'partial'."""
        vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L"
        result = self.calculator._determine_technical_impact(
            cvss_v3_score=6.0,
            cvss_v3_vector=vector
        )
        assert result == "partial"

    def test_only_high_integrity_is_partial(self):
        """Only I:H (without C:H) should result in 'partial'."""
        vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L"
        result = self.calculator._determine_technical_impact(
            cvss_v3_score=6.0,
            cvss_v3_vector=vector
        )
        assert result == "partial"


class TestSSVCParseCVSSVector:
    """Tests for _parse_cvss_vector method."""

    def setup_method(self):
        self.calculator = SSVCCalculator()

    def test_parse_cvss_vector_correctly(self):
        """Should correctly parse a CVSS 3.1 vector string."""
        vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        result = self.calculator._parse_cvss_vector(vector)

        assert result["AV"] == "N"
        assert result["AC"] == "L"
        assert result["PR"] == "N"
        assert result["UI"] == "N"
        assert result["S"] == "U"
        assert result["C"] == "H"
        assert result["I"] == "H"
        assert result["A"] == "H"

    def test_parse_cvss_vector_with_changed_scope(self):
        """Should correctly parse vector with S:C (Changed scope)."""
        vector = "CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N"
        result = self.calculator._parse_cvss_vector(vector)

        assert result["S"] == "C"
        assert result["PR"] == "L"
        assert result["UI"] == "R"

    def test_handles_missing_vector(self):
        """Should return empty dict for None or empty vector."""
        result_none = self.calculator._parse_cvss_vector(None)
        result_empty = self.calculator._parse_cvss_vector("")

        assert result_none == {}
        assert result_empty == {}

    def test_handles_invalid_vector(self):
        """Should return empty dict for invalid vector format."""
        result = self.calculator._parse_cvss_vector("not-a-valid-vector")
        assert result == {}

    def test_handles_partial_vector(self):
        """Should parse partial vectors, returning what's available."""
        vector = "CVSS:3.1/AV:N/AC:H"
        result = self.calculator._parse_cvss_vector(vector)

        assert result.get("AV") == "N"
        assert result.get("AC") == "H"
        # Missing fields should not be present
        assert "C" not in result or result.get("C") is None


class TestSSVCDecisionMatrix:
    """Tests for the full SSVC decision matrix."""

    def setup_method(self):
        self.calculator = SSVCCalculator()

    def test_decision_act_for_active_automatable(self):
        """Active exploitation + automatable = Act."""
        result = self.calculator.calculate_ssvc_decision(
            is_kev=True,
            epss_score=0.8,
            exploit_count=5,
            cvss_v3_score=9.8,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        )
        assert result["decision"] == "Act"
        assert result["exploitation"] == "active"
        assert result["automatable"] is True

    def test_decision_attend_for_active_not_automatable(self):
        """Active exploitation + not automatable = Attend."""
        result = self.calculator.calculate_ssvc_decision(
            is_kev=True,
            epss_score=0.8,
            exploit_count=5,
            cvss_v3_score=9.0,
            cvss_v3_vector="CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"  # AV:L = not automatable
        )
        assert result["decision"] == "Attend"
        assert result["exploitation"] == "active"
        assert result["automatable"] is False

    def test_decision_attend_for_poc_total_impact(self):
        """POC exploitation + total impact = Attend."""
        result = self.calculator.calculate_ssvc_decision(
            is_kev=False,
            epss_score=0.3,
            exploit_count=5,  # POC
            cvss_v3_score=9.5,  # Total impact
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        )
        assert result["decision"] == "Attend"
        assert result["exploitation"] == "poc"
        assert result["technical_impact"] == "total"

    def test_decision_track_star_for_poc_partial_impact(self):
        """POC exploitation + partial impact = Track*."""
        result = self.calculator.calculate_ssvc_decision(
            is_kev=False,
            epss_score=0.3,
            exploit_count=5,  # POC
            cvss_v3_score=6.0,  # Partial impact
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L"
        )
        assert result["decision"] == "Track*"
        assert result["exploitation"] == "poc"
        assert result["technical_impact"] == "partial"

    def test_decision_track_for_no_exploitation(self):
        """No exploitation = Track."""
        result = self.calculator.calculate_ssvc_decision(
            is_kev=False,
            epss_score=0.1,
            exploit_count=0,
            cvss_v3_score=5.0,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L"
        )
        assert result["decision"] == "Track"
        assert result["exploitation"] == "none"

    def test_decision_track_for_no_exploitation_high_impact(self):
        """No exploitation = Track even with high impact."""
        result = self.calculator.calculate_ssvc_decision(
            is_kev=False,
            epss_score=0.1,
            exploit_count=0,
            cvss_v3_score=9.8,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        )
        assert result["decision"] == "Track"
        assert result["exploitation"] == "none"


class TestSSVCFullCalculation:
    """Integration tests for full SSVC calculation."""

    def setup_method(self):
        self.calculator = SSVCCalculator()

    def test_full_ssvc_calculation_example(self):
        """Full example: CVE with KEV, high EPSS, network automatable."""
        result = self.calculator.calculate_ssvc_decision(
            is_kev=True,
            epss_score=0.85,
            exploit_count=10,
            cvss_v3_score=9.8,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        )

        # Check all fields are present
        assert "decision" in result
        assert "exploitation" in result
        assert "automatable" in result
        assert "technical_impact" in result
        assert "mission_prevalence" in result

        # Check expected values
        assert result["decision"] == "Act"
        assert result["exploitation"] == "active"
        assert result["automatable"] is True
        assert result["technical_impact"] == "total"
        # Mission prevalence is a placeholder for now
        assert result["mission_prevalence"] in ["essential", "supportive", "minimal"]

    def test_full_ssvc_with_missing_vector(self):
        """Should handle missing CVSS vector gracefully."""
        result = self.calculator.calculate_ssvc_decision(
            is_kev=True,
            epss_score=0.85,
            exploit_count=10,
            cvss_v3_score=9.8,
            cvss_v3_vector=None
        )

        # Should still produce a decision
        assert "decision" in result
        # Without vector, automatable should be False (can't confirm)
        assert result["automatable"] is False

    def test_full_ssvc_with_empty_vector(self):
        """Should handle empty CVSS vector gracefully."""
        result = self.calculator.calculate_ssvc_decision(
            is_kev=True,
            epss_score=0.85,
            exploit_count=10,
            cvss_v3_score=9.8,
            cvss_v3_vector=""
        )

        assert "decision" in result
        assert result["automatable"] is False

    def test_ssvc_log4shell_scenario(self):
        """Real-world scenario: Log4Shell-like CVE."""
        # Log4Shell: KEV, high EPSS, network automatable, critical score
        result = self.calculator.calculate_ssvc_decision(
            is_kev=True,
            epss_score=0.97,
            exploit_count=100,
            cvss_v3_score=10.0,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H"
        )

        assert result["decision"] == "Act"
        assert result["exploitation"] == "active"
        assert result["automatable"] is True
        assert result["technical_impact"] == "total"

    def test_ssvc_low_priority_cve_scenario(self):
        """Real-world scenario: Low priority CVE."""
        result = self.calculator.calculate_ssvc_decision(
            is_kev=False,
            epss_score=0.01,
            exploit_count=0,
            cvss_v3_score=4.0,
            cvss_v3_vector="CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:L/I:N/A:N"
        )

        assert result["decision"] == "Track"
        assert result["exploitation"] == "none"
        assert result["automatable"] is False
        assert result["technical_impact"] == "partial"


class TestSSVCEdgeCases:
    """Edge case tests for SSVC Calculator."""

    def setup_method(self):
        self.calculator = SSVCCalculator()

    def test_zero_epss_score(self):
        """EPSS score of 0 should not be active."""
        result = self.calculator._determine_exploitation_status(
            is_kev=False,
            epss_score=0.0,
            exploit_count=0
        )
        assert result == "none"

    def test_epss_score_one(self):
        """EPSS score of 1.0 (max) should be active."""
        result = self.calculator._determine_exploitation_status(
            is_kev=False,
            epss_score=1.0,
            exploit_count=0
        )
        assert result == "active"

    def test_cvss_score_zero(self):
        """CVSS score of 0 should be partial impact."""
        result = self.calculator._determine_technical_impact(
            cvss_v3_score=0.0,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N"
        )
        assert result == "partial"

    def test_cvss_score_ten(self):
        """CVSS score of 10.0 (max) should be total impact."""
        result = self.calculator._determine_technical_impact(
            cvss_v3_score=10.0,
            cvss_v3_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H"
        )
        assert result == "total"

    def test_negative_exploit_count_treated_as_zero(self):
        """Negative exploit count should be treated as no exploits."""
        result = self.calculator._determine_exploitation_status(
            is_kev=False,
            epss_score=0.1,
            exploit_count=-5
        )
        assert result == "none"
