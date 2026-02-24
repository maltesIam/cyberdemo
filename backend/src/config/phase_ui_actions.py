"""
Phase-to-UI-Action Mapping Configuration.

REQ-001-003-001 / DATA-007

Maps each attack scenario phase to specific UI actions that should be triggered
when the agent completes analysis for that phase. Each phase maps to a list of
actions, where each action has:
  - type: "navigate" | "highlight"
  - target (for navigate): the page/view to navigate to
  - element (for highlight): the UI element to highlight
  - description: human-readable description of what happens
"""

from typing import Any


# =============================================================================
# APT29 Phase-to-UI-Action Mapping
# =============================================================================

APT29_PHASE_ACTIONS: dict[int, list[dict[str, Any]]] = {
    1: [
        {
            "type": "navigate",
            "target": "incidents",
            "description": "Navigate to Incidents view to show initial access alert",
        },
        {
            "type": "highlight",
            "element": "source_ip",
            "description": "Highlight the source IP of the spearphishing email",
        },
    ],
    2: [
        {
            "type": "navigate",
            "target": "detections",
            "description": "Navigate to Detections view to show execution artifacts",
        },
        {
            "type": "highlight",
            "element": "process",
            "description": "Highlight the malicious process spawned by macro",
        },
    ],
    3: [
        {
            "type": "navigate",
            "target": "assets",
            "description": "Navigate to Assets view to show persistence indicators",
        },
        {
            "type": "highlight",
            "element": "registry_keys",
            "description": "Highlight registry keys modified for persistence",
        },
    ],
    4: [
        {
            "type": "navigate",
            "target": "incidents",
            "description": "Navigate to Incidents view to show privilege escalation",
        },
        {
            "type": "highlight",
            "element": "user",
            "description": "Highlight the escalated user account",
        },
    ],
    5: [
        {
            "type": "navigate",
            "target": "detections",
            "description": "Navigate to Detections view to show defense evasion techniques",
        },
        {
            "type": "highlight",
            "element": "technique",
            "description": "Highlight the MITRE technique used for evasion",
        },
    ],
    6: [
        {
            "type": "navigate",
            "target": "assets",
            "description": "Navigate to Assets view to show credential theft impact",
        },
        {
            "type": "highlight",
            "element": "compromised_host",
            "description": "Highlight the compromised host where credentials were stolen",
        },
    ],
    7: [
        {
            "type": "navigate",
            "target": "assets",
            "description": "Navigate to Assets view to show lateral movement path",
        },
        {
            "type": "highlight",
            "element": "network_path",
            "description": "Highlight the network path of lateral movement",
        },
    ],
    8: [
        {
            "type": "navigate",
            "target": "incidents",
            "description": "Navigate to Incidents view to show exfiltration alert",
        },
        {
            "type": "highlight",
            "element": "data_flow",
            "description": "Highlight the data flow path used for exfiltration",
        },
    ],
}


# =============================================================================
# Scenario Registry
# =============================================================================

_SCENARIO_MAPPINGS: dict[str, dict[int, list[dict[str, Any]]]] = {
    "apt29": APT29_PHASE_ACTIONS,
}


# =============================================================================
# Public API
# =============================================================================


def get_phase_ui_actions(scenario_id: str) -> dict[int, list[dict[str, Any]]]:
    """Get the full phase-to-UI-action mapping for a scenario.

    Args:
        scenario_id: The scenario identifier (e.g., "apt29").

    Returns:
        A dict mapping phase numbers to lists of UI action dicts.
        Returns empty dict for unknown scenarios.
    """
    return _SCENARIO_MAPPINGS.get(scenario_id, {})


def get_actions_for_phase(
    scenario_id: str, phase: int
) -> list[dict[str, Any]]:
    """Get UI actions for a specific phase of a scenario.

    Args:
        scenario_id: The scenario identifier.
        phase: The phase number (1-based).

    Returns:
        List of UI action dicts for the given phase.
        Returns empty list if scenario or phase not found.
    """
    mapping = _SCENARIO_MAPPINGS.get(scenario_id, {})
    return mapping.get(phase, [])
