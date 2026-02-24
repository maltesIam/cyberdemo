"""
Unit Tests for Phase Advance Sync (UT-035).

Requirement: REQ-002-006-002
Task: T-034

When simulation advances to the next phase or jumps to a specific stage,
ScenarioStateManager must sync its cumulative events accordingly.
"""

import pytest


def _reset_all():
    """Reset both managers to clean state."""
    from src.mcp.tools.attack_simulation import reset_simulation_manager
    from src.services.scenario_state_manager import ScenarioStateManager

    reset_simulation_manager()
    mgr = ScenarioStateManager.get_instance()
    mgr._state = None
    mgr._phases = {}


class TestPhaseAdvanceSync:
    """Tests that phase advances sync both managers."""

    def setup_method(self):
        """Reset all state before each test."""
        _reset_all()

    @pytest.mark.asyncio
    async def test_advance_phase_syncs_simulation_manager(self):
        """Advancing a phase must update SimulationStateManager's current_stage."""
        from src.services.phase_sync import PhaseSyncCoordinator
        from src.mcp.tools.attack_simulation import get_simulation_manager

        coordinator = PhaseSyncCoordinator()
        await coordinator.start_scenario("apt29")

        result = await coordinator.advance_phase(3)

        sim_state = await get_simulation_manager().get_state()
        assert sim_state["current_stage"] == 3
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_advance_phase_syncs_scenario_manager(self):
        """Advancing a phase must update ScenarioStateManager's current_phase."""
        from src.services.phase_sync import PhaseSyncCoordinator
        from src.services.scenario_state_manager import ScenarioStateManager

        coordinator = PhaseSyncCoordinator()
        await coordinator.start_scenario("apt29")

        await coordinator.advance_phase(2)

        mgr = ScenarioStateManager.get_instance()
        state = await mgr.get_current_state()
        assert state is not None
        assert state.current_phase == 2

    @pytest.mark.asyncio
    async def test_advance_returns_sync_status(self):
        """Advance must return sync_status='both_advanced'."""
        from src.services.phase_sync import PhaseSyncCoordinator

        coordinator = PhaseSyncCoordinator()
        await coordinator.start_scenario("apt29")

        result = await coordinator.advance_phase(1)

        assert result["sync_status"] == "both_advanced"

    @pytest.mark.asyncio
    async def test_advance_to_invalid_stage_returns_error(self):
        """Advancing to an out-of-range stage must return error."""
        from src.services.phase_sync import PhaseSyncCoordinator

        coordinator = PhaseSyncCoordinator()
        await coordinator.start_scenario("apt29")

        result = await coordinator.advance_phase(99)

        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_advance_without_scenario_returns_error(self):
        """Advancing without an active scenario must return error."""
        from src.services.phase_sync import PhaseSyncCoordinator

        coordinator = PhaseSyncCoordinator()
        result = await coordinator.advance_phase(1)

        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_jump_forward_accumulates_events(self):
        """Jumping from phase 1 to phase 3 must accumulate events for 1, 2, 3."""
        from src.services.phase_sync import PhaseSyncCoordinator
        from src.services.scenario_state_manager import ScenarioStateManager
        from src.models.scenario_types import SiemIncident

        coordinator = PhaseSyncCoordinator()
        await coordinator.start_scenario("apt29")

        # Manually inject events into the scenario manager's phases for testing
        mgr = ScenarioStateManager.get_instance()
        phases = mgr._phases  # Access internal phases for test setup

        # Add test incidents to phases
        for phase_num in [1, 2, 3]:
            if phase_num in phases:
                phases[phase_num].incidents.append(
                    SiemIncident(
                        id=f"INC-{phase_num}",
                        title=f"Phase {phase_num} Incident",
                        severity="high",
                        source="test",
                        mitre_tactic="test",
                        mitre_technique="T0000",
                    )
                )

        # Advance to phase 3 (should accumulate 1+2+3)
        await coordinator.advance_phase(3)

        state = await mgr.get_current_state()
        assert state is not None
        assert state.current_phase == 3
        assert len(state.incidents) == 3

    @pytest.mark.asyncio
    async def test_sequential_advance_accumulates(self):
        """Advancing 1->2->3 must be equivalent to jumping to 3."""
        from src.services.phase_sync import PhaseSyncCoordinator
        from src.services.scenario_state_manager import ScenarioStateManager

        coordinator = PhaseSyncCoordinator()
        await coordinator.start_scenario("apt29")

        await coordinator.advance_phase(1)
        await coordinator.advance_phase(2)
        await coordinator.advance_phase(3)

        mgr = ScenarioStateManager.get_instance()
        state = await mgr.get_current_state()
        assert state is not None
        assert state.current_phase == 3

    @pytest.mark.asyncio
    async def test_both_managers_agree_on_stage(self):
        """After advance, both managers must report the same stage."""
        from src.services.phase_sync import PhaseSyncCoordinator
        from src.services.scenario_state_manager import ScenarioStateManager
        from src.mcp.tools.attack_simulation import get_simulation_manager

        coordinator = PhaseSyncCoordinator()
        await coordinator.start_scenario("apt29")

        await coordinator.advance_phase(5)

        sim_state = await get_simulation_manager().get_state()
        scenario_state = await ScenarioStateManager.get_instance().get_current_state()

        assert sim_state["current_stage"] == 5
        assert scenario_state.current_phase == 5
