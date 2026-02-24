"""
Unit tests for APT29 SIEM incidents.

Task: T-018
Requirement: REQ-002-002-002
Test ID: UT-026

Tests that APT29 scenario defines 14 cumulative SIEM incidents
across 8 phases with correct structure and cumulative behavior.
"""

import pytest


class TestAPT29SIEMIncidents:
    """Tests for 14 cumulative SIEM incidents across 8 phases."""

    def test_total_unique_siem_incidents_is_14(self):
        """Total unique SIEM incidents across all phases must be 14."""
        from src.scenarios.apt29 import APT29_PHASES
        all_incident_ids = set()
        for phase in APT29_PHASES.values():
            for incident in phase["siem_incidents"]:
                all_incident_ids.add(incident["id"])
        assert len(all_incident_ids) == 14

    def test_siem_incident_required_fields(self):
        """Each SIEM incident must have all required fields."""
        from src.scenarios.apt29 import APT29_PHASES
        required = ["id", "title", "severity", "timestamp", "source",
                     "description", "mitre_tactic", "mitre_technique"]
        for phase_num, phase in APT29_PHASES.items():
            for inc in phase["siem_incidents"]:
                for field in required:
                    assert field in inc, (
                        f"Phase {phase_num}, incident {inc.get('id', '?')} "
                        f"missing field: {field}"
                    )

    def test_siem_severity_values(self):
        """SIEM incident severity must be one of the valid levels."""
        from src.scenarios.apt29 import APT29_PHASES
        valid_severities = {"low", "medium", "high", "critical"}
        for phase_num, phase in APT29_PHASES.items():
            for inc in phase["siem_incidents"]:
                assert inc["severity"] in valid_severities, (
                    f"Phase {phase_num}, incident {inc['id']}: "
                    f"invalid severity '{inc['severity']}'"
                )

    def test_siem_incidents_have_unique_ids(self):
        """All SIEM incident IDs across all phases must be unique."""
        from src.scenarios.apt29 import APT29_PHASES
        all_ids = []
        for phase in APT29_PHASES.values():
            for inc in phase["siem_incidents"]:
                all_ids.append(inc["id"])
        assert len(all_ids) == len(set(all_ids)), "Duplicate SIEM incident IDs found"

    def test_cumulative_phase_3_includes_phases_1_2_3(self):
        """Cumulative data retrieval for phase 3 should include
        incidents from phases 1, 2, and 3."""
        from src.scenarios.apt29 import get_cumulative_incidents
        cumulative = get_cumulative_incidents(3)
        # Must include phase 1, 2, and 3 incidents
        phase_1_ids = {i["id"] for i in _get_phase_incidents(1)}
        phase_2_ids = {i["id"] for i in _get_phase_incidents(2)}
        phase_3_ids = {i["id"] for i in _get_phase_incidents(3)}
        cumulative_ids = {i["id"] for i in cumulative}
        expected = phase_1_ids | phase_2_ids | phase_3_ids
        assert cumulative_ids == expected

    def test_cumulative_phase_8_includes_all_14(self):
        """Cumulative data for phase 8 must include all 14 incidents."""
        from src.scenarios.apt29 import get_cumulative_incidents
        cumulative = get_cumulative_incidents(8)
        assert len(cumulative) == 14

    def test_cumulative_phase_1_only_includes_phase_1(self):
        """Cumulative data for phase 1 must only include phase 1 incidents."""
        from src.scenarios.apt29 import get_cumulative_incidents
        cumulative = get_cumulative_incidents(1)
        phase_1_ids = {i["id"] for i in _get_phase_incidents(1)}
        cumulative_ids = {i["id"] for i in cumulative}
        assert cumulative_ids == phase_1_ids

    def test_siem_incidents_have_mitre_mapping(self):
        """Each incident must map to a valid MITRE technique."""
        from src.scenarios.apt29 import APT29_PHASES
        for phase in APT29_PHASES.values():
            for inc in phase["siem_incidents"]:
                assert inc["mitre_technique"].startswith("T"), (
                    f"Incident {inc['id']} has invalid technique: {inc['mitre_technique']}"
                )
                assert inc["mitre_tactic"].startswith("TA"), (
                    f"Incident {inc['id']} has invalid tactic: {inc['mitre_tactic']}"
                )

    def test_phase_1_has_initial_access_incidents(self):
        """Phase 1 SIEM incidents must relate to initial access."""
        from src.scenarios.apt29 import APT29_PHASES
        phase1_incidents = APT29_PHASES[1]["siem_incidents"]
        assert len(phase1_incidents) >= 1
        # At least one must be about spear-phishing or initial access
        has_initial_access = any(
            "TA0001" in inc["mitre_tactic"] for inc in phase1_incidents
        )
        assert has_initial_access

    def test_each_phase_introduces_new_incidents(self):
        """Each phase must introduce at least one new incident."""
        from src.scenarios.apt29 import APT29_PHASES
        for phase_num, phase in APT29_PHASES.items():
            assert len(phase["siem_incidents"]) >= 1, (
                f"Phase {phase_num} has no SIEM incidents"
            )


def _get_phase_incidents(phase_num):
    """Helper to get incidents from a specific phase."""
    from src.scenarios.apt29 import APT29_PHASES
    return APT29_PHASES[phase_num]["siem_incidents"]
