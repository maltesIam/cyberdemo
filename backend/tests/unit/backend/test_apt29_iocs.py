"""
Unit tests for APT29 Intel IOCs.

Task: T-020
Requirement: REQ-002-002-004
Test ID: UT-028

Tests that APT29 scenario defines 7 cumulative threat intel IOCs
across 8 phases with correct structure and cumulative behavior.
"""

import pytest


class TestAPT29IntelIOCs:
    """Tests for 7 cumulative threat intel IOCs across 8 phases."""

    def test_total_unique_iocs_is_7(self):
        """Total unique IOCs across all phases must be 7."""
        from src.scenarios.apt29 import APT29_PHASES
        all_ioc_ids = set()
        for phase in APT29_PHASES.values():
            for ioc in phase["intel_iocs"]:
                all_ioc_ids.add(ioc["id"])
        assert len(all_ioc_ids) == 7

    def test_ioc_required_fields(self):
        """Each IOC must have all required fields."""
        from src.scenarios.apt29 import APT29_PHASES
        required = ["id", "type", "value", "confidence_score",
                     "source", "associated_threat"]
        for phase_num, phase in APT29_PHASES.items():
            for ioc in phase["intel_iocs"]:
                for field in required:
                    assert field in ioc, (
                        f"Phase {phase_num}, IOC {ioc.get('id', '?')} "
                        f"missing field: {field}"
                    )

    def test_ioc_type_values(self):
        """IOC type must be one of the valid indicator types."""
        from src.scenarios.apt29 import APT29_PHASES
        valid_types = {"ip", "domain", "hash", "email", "url"}
        for phase_num, phase in APT29_PHASES.items():
            for ioc in phase["intel_iocs"]:
                assert ioc["type"] in valid_types, (
                    f"Phase {phase_num}, IOC {ioc['id']}: "
                    f"invalid type '{ioc['type']}'"
                )

    def test_ioc_confidence_score_range(self):
        """IOC confidence_score must be between 0 and 100."""
        from src.scenarios.apt29 import APT29_PHASES
        for phase_num, phase in APT29_PHASES.items():
            for ioc in phase["intel_iocs"]:
                assert 0 <= ioc["confidence_score"] <= 100, (
                    f"Phase {phase_num}, IOC {ioc['id']}: "
                    f"confidence_score {ioc['confidence_score']} out of range"
                )

    def test_iocs_have_unique_ids(self):
        """All IOC IDs across all phases must be unique."""
        from src.scenarios.apt29 import APT29_PHASES
        all_ids = []
        for phase in APT29_PHASES.values():
            for ioc in phase["intel_iocs"]:
                all_ids.append(ioc["id"])
        assert len(all_ids) == len(set(all_ids)), "Duplicate IOC IDs found"

    def test_cumulative_iocs_phase_3(self):
        """Cumulative IOCs for phase 3 includes phases 1+2+3."""
        from src.scenarios.apt29 import get_cumulative_iocs
        cumulative = get_cumulative_iocs(3)
        from src.scenarios.apt29 import APT29_PHASES
        expected_ids = set()
        for p in [1, 2, 3]:
            for ioc in APT29_PHASES[p]["intel_iocs"]:
                expected_ids.add(ioc["id"])
        cumulative_ids = {i["id"] for i in cumulative}
        assert cumulative_ids == expected_ids

    def test_cumulative_iocs_phase_8_includes_all_7(self):
        """Cumulative IOCs for phase 8 must include all 7."""
        from src.scenarios.apt29 import get_cumulative_iocs
        cumulative = get_cumulative_iocs(8)
        assert len(cumulative) == 7

    def test_iocs_include_mixed_types(self):
        """IOCs should include at least IP, domain, and hash types."""
        from src.scenarios.apt29 import APT29_PHASES
        all_types = set()
        for phase in APT29_PHASES.values():
            for ioc in phase["intel_iocs"]:
                all_types.add(ioc["type"])
        assert "ip" in all_types, "No IP-type IOCs found"
        assert "domain" in all_types, "No domain-type IOCs found"
        assert "hash" in all_types, "No hash-type IOCs found"

    def test_ioc_associated_threat_references_apt29(self):
        """Each IOC associated_threat must reference APT29 / Cozy Bear."""
        from src.scenarios.apt29 import APT29_PHASES
        for phase in APT29_PHASES.values():
            for ioc in phase["intel_iocs"]:
                threat = ioc["associated_threat"].lower()
                assert "apt29" in threat or "cozy bear" in threat, (
                    f"IOC {ioc['id']} associated_threat '{ioc['associated_threat']}' "
                    f"does not reference APT29"
                )
