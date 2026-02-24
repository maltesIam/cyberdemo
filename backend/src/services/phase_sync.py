"""
Phase Sync Coordinator.

REQ-002-006-001 / INT-004 / T-033

Coordinates initialization and synchronization between SimulationStateManager
(existing) and ScenarioStateManager (new). When attack_start_scenario is called,
both managers are initialized together.
"""

from typing import Any

from src.mcp.tools.attack_simulation import (
    get_simulation_manager,
    SCENARIOS,
)
from src.services.scenario_state_manager import ScenarioStateManager
from src.models.scenario_types import PhaseEvents


def _build_phase_events_for_scenario(scenario_id: str) -> dict[int, PhaseEvents]:
    """Build PhaseEvents data for each phase of a scenario.

    Creates empty PhaseEvents structures for each phase/tactic in the scenario
    definition. Actual event data is populated during simulation runtime.

    Args:
        scenario_id: The scenario key (e.g., "apt29").

    Returns:
        Dict mapping 1-based phase numbers to PhaseEvents objects.
    """
    scenario = SCENARIOS.get(scenario_id)
    if not scenario:
        return {}

    phases: dict[int, PhaseEvents] = {}
    tactics = scenario.get("mitre_tactics", [])

    for i, tactic in enumerate(tactics, start=1):
        phases[i] = PhaseEvents(
            phase_number=i,
            phase_name=tactic["name"],
            mitre_tactic=tactic["id"],
            incidents=[],
            detections=[],
            iocs=[],
        )

    return phases


class PhaseSyncCoordinator:
    """Coordinates SimulationStateManager and ScenarioStateManager.

    Ensures both managers are initialized together when a scenario starts,
    and stay in sync when phases advance or jump.
    """

    async def start_scenario(
        self, scenario_id: str, seed: int | None = None
    ) -> dict[str, Any]:
        """Start a scenario in both managers simultaneously.

        Args:
            scenario_id: The scenario identifier (e.g., "apt29").
            seed: Optional reproducibility seed.

        Returns:
            Combined status dict from both managers.
        """
        if scenario_id not in SCENARIOS:
            return {"status": "error", "message": f"Unknown scenario: {scenario_id}"}

        # 1. Start SimulationStateManager
        sim_mgr = get_simulation_manager()
        sim_result = await sim_mgr.start_scenario(scenario_id, seed)

        if sim_result.get("status") == "error":
            return sim_result

        # 2. Build phase events and start ScenarioStateManager
        phases = _build_phase_events_for_scenario(scenario_id)
        scenario_mgr = ScenarioStateManager.get_instance()
        await scenario_mgr.start_scenario(
            scenario_id=scenario_id,
            scenario_name=SCENARIOS[scenario_id]["name"],
            phases=phases,
        )

        return {
            **sim_result,
            "sync_status": "both_initialized",
        }

    async def advance_phase(self, stage_number: int) -> dict[str, Any]:
        """Advance both managers to a specific stage.

        Args:
            stage_number: The stage number to advance to (1-based).

        Returns:
            Combined result from both managers.
        """
        # Advance SimulationStateManager
        sim_mgr = get_simulation_manager()
        sim_result = await sim_mgr.jump_to_stage(stage_number)

        if sim_result.get("status") == "error":
            return sim_result

        # Advance ScenarioStateManager
        scenario_mgr = ScenarioStateManager.get_instance()
        await scenario_mgr.advance_to_phase(stage_number)

        return {
            **sim_result,
            "sync_status": "both_advanced",
        }
