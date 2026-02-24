"""
Unit tests for APT29 EDR detections.

Task: T-019
Requirement: REQ-002-002-003
Test ID: UT-027

Tests that APT29 scenario defines 15 cumulative EDR detections
across 8 phases with correct structure and cumulative behavior.
"""

import pytest


class TestAPT29EDRDetections:
    """Tests for 15 cumulative EDR detections across 8 phases."""

    def test_total_unique_edr_detections_is_15(self):
        """Total unique EDR detections across all phases must be 15."""
        from src.scenarios.apt29 import APT29_PHASES
        all_detection_ids = set()
        for phase in APT29_PHASES.values():
            for det in phase["edr_detections"]:
                all_detection_ids.add(det["id"])
        assert len(all_detection_ids) == 15

    def test_edr_detection_required_fields(self):
        """Each EDR detection must have all required fields."""
        from src.scenarios.apt29 import APT29_PHASES
        required = ["id", "rule_name", "severity", "process_name",
                     "host", "pid", "mitre_technique", "action_taken"]
        for phase_num, phase in APT29_PHASES.items():
            for det in phase["edr_detections"]:
                for field in required:
                    assert field in det, (
                        f"Phase {phase_num}, detection {det.get('id', '?')} "
                        f"missing field: {field}"
                    )

    def test_edr_severity_values(self):
        """EDR detection severity must be a valid level."""
        from src.scenarios.apt29 import APT29_PHASES
        valid_severities = {"low", "medium", "high", "critical"}
        for phase_num, phase in APT29_PHASES.items():
            for det in phase["edr_detections"]:
                assert det["severity"] in valid_severities, (
                    f"Phase {phase_num}, detection {det['id']}: "
                    f"invalid severity '{det['severity']}'"
                )

    def test_edr_detections_have_unique_ids(self):
        """All EDR detection IDs across all phases must be unique."""
        from src.scenarios.apt29 import APT29_PHASES
        all_ids = []
        for phase in APT29_PHASES.values():
            for det in phase["edr_detections"]:
                all_ids.append(det["id"])
        assert len(all_ids) == len(set(all_ids)), "Duplicate EDR detection IDs found"

    def test_cumulative_edr_phase_3(self):
        """Cumulative EDR detections for phase 3 includes phases 1+2+3."""
        from src.scenarios.apt29 import get_cumulative_detections
        cumulative = get_cumulative_detections(3)
        # Collect IDs from phases 1, 2, 3
        from src.scenarios.apt29 import APT29_PHASES
        expected_ids = set()
        for p in [1, 2, 3]:
            for det in APT29_PHASES[p]["edr_detections"]:
                expected_ids.add(det["id"])
        cumulative_ids = {d["id"] for d in cumulative}
        assert cumulative_ids == expected_ids

    def test_cumulative_edr_phase_8_includes_all_15(self):
        """Cumulative EDR detections for phase 8 must include all 15."""
        from src.scenarios.apt29 import get_cumulative_detections
        cumulative = get_cumulative_detections(8)
        assert len(cumulative) == 15

    def test_edr_action_taken_valid(self):
        """action_taken must be a recognized EDR action."""
        from src.scenarios.apt29 import APT29_PHASES
        valid_actions = {"alerted", "blocked", "quarantined", "logged", "killed_process"}
        for phase_num, phase in APT29_PHASES.items():
            for det in phase["edr_detections"]:
                assert det["action_taken"] in valid_actions, (
                    f"Phase {phase_num}, detection {det['id']}: "
                    f"invalid action_taken '{det['action_taken']}'"
                )

    def test_edr_detections_have_mitre_techniques(self):
        """Each detection must reference a MITRE technique."""
        from src.scenarios.apt29 import APT29_PHASES
        for phase in APT29_PHASES.values():
            for det in phase["edr_detections"]:
                assert det["mitre_technique"].startswith("T"), (
                    f"Detection {det['id']} has invalid technique: {det['mitre_technique']}"
                )

    def test_phase_2_has_execution_detections(self):
        """Phase 2 EDR detections must relate to execution (PowerShell)."""
        from src.scenarios.apt29 import APT29_PHASES
        phase2_detections = APT29_PHASES[2]["edr_detections"]
        assert len(phase2_detections) >= 1
        has_execution = any(
            "powershell" in det["process_name"].lower() or
            "T1059" in det["mitre_technique"]
            for det in phase2_detections
        )
        assert has_execution

    def test_each_phase_introduces_new_detections(self):
        """Each phase must introduce at least one new EDR detection."""
        from src.scenarios.apt29 import APT29_PHASES
        for phase_num, phase in APT29_PHASES.items():
            assert len(phase["edr_detections"]) >= 1, (
                f"Phase {phase_num} has no EDR detections"
            )
