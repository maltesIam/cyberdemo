"""
Unit Tests for Phase-to-UI-Action Mapping Configuration (UT-010).

Requirement: REQ-001-003-001
Task: T-028

Tests that each APT29 phase maps to specific UI actions:
- Phase 1 (Initial Access) -> navigate to Incidents + highlight source IP
- Phase 2 (Execution) -> navigate to Detections + highlight process
- Phase 3 (Persistence) -> navigate to Assets + highlight registry keys
- Phase 4 (Privilege Escalation) -> navigate to Incidents + highlight user
- Phase 5 (Defense Evasion) -> navigate to Detections + highlight technique
- Phase 6 (Credential Access) -> navigate to Assets + highlight compromised host
- Phase 7 (Lateral Movement) -> navigate to Assets + highlight network path
- Phase 8 (Exfiltration) -> navigate to Incidents + highlight data flow
"""

import pytest


class TestPhaseUIActionMapping:
    """Tests for the phase-to-UI-action mapping configuration."""

    def test_mapping_has_all_apt29_phases(self):
        """All 8 APT29 phases must have UI action mappings."""
        from src.config.phase_ui_actions import get_phase_ui_actions

        actions = get_phase_ui_actions("apt29")
        assert len(actions) == 8
        for i in range(1, 9):
            assert i in actions, f"Phase {i} missing from mapping"

    def test_each_phase_has_navigate_action(self):
        """Each phase mapping must include a 'navigate' action."""
        from src.config.phase_ui_actions import get_phase_ui_actions

        actions = get_phase_ui_actions("apt29")
        for phase_num, action_list in actions.items():
            nav_actions = [a for a in action_list if a["type"] == "navigate"]
            assert len(nav_actions) >= 1, (
                f"Phase {phase_num} must have at least one navigate action"
            )

    def test_each_phase_has_highlight_action(self):
        """Each phase mapping must include a 'highlight' action."""
        from src.config.phase_ui_actions import get_phase_ui_actions

        actions = get_phase_ui_actions("apt29")
        for phase_num, action_list in actions.items():
            highlight_actions = [a for a in action_list if a["type"] == "highlight"]
            assert len(highlight_actions) >= 1, (
                f"Phase {phase_num} must have at least one highlight action"
            )

    def test_phase_1_navigates_to_incidents(self):
        """Phase 1 (Initial Access) must navigate to Incidents view."""
        from src.config.phase_ui_actions import get_phase_ui_actions

        actions = get_phase_ui_actions("apt29")
        nav = [a for a in actions[1] if a["type"] == "navigate"][0]
        assert nav["target"] == "incidents"

    def test_phase_1_highlights_source_ip(self):
        """Phase 1 must highlight the source IP."""
        from src.config.phase_ui_actions import get_phase_ui_actions

        actions = get_phase_ui_actions("apt29")
        highlight = [a for a in actions[1] if a["type"] == "highlight"][0]
        assert highlight["element"] == "source_ip"

    def test_phase_5_navigates_to_detections(self):
        """Phase 5 (Defense Evasion) must navigate to Detections view."""
        from src.config.phase_ui_actions import get_phase_ui_actions

        actions = get_phase_ui_actions("apt29")
        nav = [a for a in actions[5] if a["type"] == "navigate"][0]
        assert nav["target"] == "detections"

    def test_phase_6_navigates_to_assets(self):
        """Phase 6 (Credential Access) must navigate to Assets view."""
        from src.config.phase_ui_actions import get_phase_ui_actions

        actions = get_phase_ui_actions("apt29")
        nav = [a for a in actions[6] if a["type"] == "navigate"][0]
        assert nav["target"] == "assets"

    def test_phase_6_highlights_compromised_host(self):
        """Phase 6 must highlight the compromised host."""
        from src.config.phase_ui_actions import get_phase_ui_actions

        actions = get_phase_ui_actions("apt29")
        highlight = [a for a in actions[6] if a["type"] == "highlight"][0]
        assert highlight["element"] == "compromised_host"

    def test_phase_8_navigates_to_incidents(self):
        """Phase 8 (Exfiltration) must navigate to Incidents view."""
        from src.config.phase_ui_actions import get_phase_ui_actions

        actions = get_phase_ui_actions("apt29")
        nav = [a for a in actions[8] if a["type"] == "navigate"][0]
        assert nav["target"] == "incidents"

    def test_action_has_required_fields(self):
        """Each action must have type, target/element, and description."""
        from src.config.phase_ui_actions import get_phase_ui_actions

        actions = get_phase_ui_actions("apt29")
        for phase_num, action_list in actions.items():
            for action in action_list:
                assert "type" in action, f"Action in phase {phase_num} missing 'type'"
                assert "description" in action, (
                    f"Action in phase {phase_num} missing 'description'"
                )
                if action["type"] == "navigate":
                    assert "target" in action
                elif action["type"] == "highlight":
                    assert "element" in action

    def test_unknown_scenario_returns_empty(self):
        """Unknown scenario IDs must return an empty mapping."""
        from src.config.phase_ui_actions import get_phase_ui_actions

        actions = get_phase_ui_actions("nonexistent_scenario")
        assert actions == {}

    def test_get_actions_for_phase_returns_list(self):
        """get_actions_for_phase returns the list for a single phase."""
        from src.config.phase_ui_actions import get_actions_for_phase

        result = get_actions_for_phase("apt29", 1)
        assert isinstance(result, list)
        assert len(result) >= 2  # navigate + highlight

    def test_get_actions_for_invalid_phase_returns_empty(self):
        """get_actions_for_phase returns empty list for invalid phase."""
        from src.config.phase_ui_actions import get_actions_for_phase

        result = get_actions_for_phase("apt29", 99)
        assert result == []

    def test_phase_mapping_is_serializable(self):
        """Phase mapping must be JSON-serializable for API transport."""
        import json
        from src.config.phase_ui_actions import get_phase_ui_actions

        actions = get_phase_ui_actions("apt29")
        # Convert int keys to string for JSON serialization
        serializable = {str(k): v for k, v in actions.items()}
        json_str = json.dumps(serializable)
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert len(parsed) == 8
