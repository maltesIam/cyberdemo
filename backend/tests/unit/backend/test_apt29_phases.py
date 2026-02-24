"""
Unit tests for APT29 scenario script - 8 phase definitions.

Task: T-017
Requirement: REQ-002-002-001
Test ID: UT-025

Tests that APT29 scenario defines exactly 8 phases following
the MITRE ATT&CK kill chain for Cozy Bear (APT29).
"""

import pytest


class TestAPT29PhaseDefinitions:
    """Tests for the 8-phase APT29 attack scenario."""

    def test_scenario_has_exactly_8_phases(self):
        """APT29 scenario must define exactly 8 phases."""
        from src.scenarios.apt29 import APT29_PHASES
        assert len(APT29_PHASES) == 8

    def test_phase_1_initial_access(self):
        """Phase 1 must be Initial Access (Spear-phishing)."""
        from src.scenarios.apt29 import APT29_PHASES
        phase = APT29_PHASES[1]
        assert phase["name"] == "Initial Access"
        assert phase["mitre_tactic"] == "TA0001"
        assert "T1566.001" in phase["mitre_techniques"]

    def test_phase_2_execution(self):
        """Phase 2 must be Execution (PowerShell)."""
        from src.scenarios.apt29 import APT29_PHASES
        phase = APT29_PHASES[2]
        assert phase["name"] == "Execution"
        assert phase["mitre_tactic"] == "TA0002"
        assert "T1059.001" in phase["mitre_techniques"]

    def test_phase_3_persistence(self):
        """Phase 3 must be Persistence (Registry keys)."""
        from src.scenarios.apt29 import APT29_PHASES
        phase = APT29_PHASES[3]
        assert phase["name"] == "Persistence"
        assert phase["mitre_tactic"] == "TA0003"
        assert "T1547.001" in phase["mitre_techniques"]

    def test_phase_4_privilege_escalation(self):
        """Phase 4 must be Privilege Escalation (Token theft)."""
        from src.scenarios.apt29 import APT29_PHASES
        phase = APT29_PHASES[4]
        assert phase["name"] == "Privilege Escalation"
        assert phase["mitre_tactic"] == "TA0004"
        assert "T1134.001" in phase["mitre_techniques"]

    def test_phase_5_defense_evasion(self):
        """Phase 5 must be Defense Evasion (Process injection)."""
        from src.scenarios.apt29 import APT29_PHASES
        phase = APT29_PHASES[5]
        assert phase["name"] == "Defense Evasion"
        assert phase["mitre_tactic"] == "TA0005"
        assert "T1055.001" in phase["mitre_techniques"]

    def test_phase_6_credential_access(self):
        """Phase 6 must be Credential Access (LSASS dump)."""
        from src.scenarios.apt29 import APT29_PHASES
        phase = APT29_PHASES[6]
        assert phase["name"] == "Credential Access"
        assert phase["mitre_tactic"] == "TA0006"
        assert "T1003.001" in phase["mitre_techniques"]

    def test_phase_7_lateral_movement(self):
        """Phase 7 must be Lateral Movement (RDP, SMB)."""
        from src.scenarios.apt29 import APT29_PHASES
        phase = APT29_PHASES[7]
        assert phase["name"] == "Lateral Movement"
        assert phase["mitre_tactic"] == "TA0008"
        assert "T1021.001" in phase["mitre_techniques"]

    def test_phase_8_exfiltration(self):
        """Phase 8 must be Exfiltration (HTTPS C2)."""
        from src.scenarios.apt29 import APT29_PHASES
        phase = APT29_PHASES[8]
        assert phase["name"] == "Exfiltration"
        assert phase["mitre_tactic"] == "TA0010"
        assert "T1041" in phase["mitre_techniques"]

    def test_all_phases_have_required_fields(self):
        """Every phase must have name, mitre_tactic, mitre_techniques, description."""
        from src.scenarios.apt29 import APT29_PHASES
        required_fields = ["name", "mitre_tactic", "mitre_techniques", "description"]
        for phase_num, phase in APT29_PHASES.items():
            for field in required_fields:
                assert field in phase, f"Phase {phase_num} missing field: {field}"

    def test_phases_have_siem_incidents(self):
        """Every phase must have a siem_incidents list."""
        from src.scenarios.apt29 import APT29_PHASES
        for phase_num, phase in APT29_PHASES.items():
            assert "siem_incidents" in phase, f"Phase {phase_num} missing siem_incidents"
            assert isinstance(phase["siem_incidents"], list)

    def test_phases_have_edr_detections(self):
        """Every phase must have an edr_detections list."""
        from src.scenarios.apt29 import APT29_PHASES
        for phase_num, phase in APT29_PHASES.items():
            assert "edr_detections" in phase, f"Phase {phase_num} missing edr_detections"
            assert isinstance(phase["edr_detections"], list)

    def test_phases_have_intel_iocs(self):
        """Every phase must have an intel_iocs list."""
        from src.scenarios.apt29 import APT29_PHASES
        for phase_num, phase in APT29_PHASES.items():
            assert "intel_iocs" in phase, f"Phase {phase_num} missing intel_iocs"
            assert isinstance(phase["intel_iocs"], list)

    def test_scenario_metadata(self):
        """APT29 scenario must have proper metadata."""
        from src.scenarios.apt29 import APT29_METADATA
        assert APT29_METADATA["id"] == "apt29"
        assert "Cozy Bear" in APT29_METADATA["name"]
        assert APT29_METADATA["total_phases"] == 8

    def test_phase_keys_are_1_indexed(self):
        """Phase dictionary keys must be 1-indexed (1 through 8)."""
        from src.scenarios.apt29 import APT29_PHASES
        expected_keys = {1, 2, 3, 4, 5, 6, 7, 8}
        assert set(APT29_PHASES.keys()) == expected_keys
