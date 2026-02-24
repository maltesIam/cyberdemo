"""
Unit Tests for Phase Sync Initialization (UT-034).

Requirement: REQ-002-006-001
Task: T-033

When attack_start_scenario is called, BOTH SimulationStateManager (existing)
and ScenarioStateManager (new) must be initialized together.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


def _reset_all():
    """Reset both managers to clean state."""
    from src.mcp.tools.attack_simulation import reset_simulation_manager
    from src.services.scenario_state_manager import ScenarioStateManager

    reset_simulation_manager()
    # Reset ScenarioStateManager singleton internal state synchronously
    mgr = ScenarioStateManager.get_instance()
    mgr._state = None
    mgr._phases = {}


class TestPhaseSyncInitialization:
    """Tests that both managers sync on scenario start."""

    def setup_method(self):
        """Reset all managers before each test."""
        _reset_all()

    @pytest.mark.asyncio
    async def test_start_scenario_initializes_simulation_state_manager(self):
        """SimulationStateManager must be initialized when scenario starts."""
        from src.services.phase_sync import PhaseSyncCoordinator

        coordinator = PhaseSyncCoordinator()
        result = await coordinator.start_scenario("apt29")

        assert result["status"] == "started"
        assert result["scenario"] == "apt29"

    @pytest.mark.asyncio
    async def test_start_scenario_initializes_scenario_state_manager(self):
        """ScenarioStateManager must be initialized when scenario starts."""
        from src.services.phase_sync import PhaseSyncCoordinator
        from src.services.scenario_state_manager import ScenarioStateManager

        coordinator = PhaseSyncCoordinator()
        result = await coordinator.start_scenario("apt29")

        mgr = ScenarioStateManager.get_instance()
        state = await mgr.get_current_state()
        assert state is not None
        assert state.scenario_id == "apt29"

    @pytest.mark.asyncio
    async def test_both_managers_are_in_sync_after_start(self):
        """Both managers must be initialized to the same scenario."""
        from src.services.phase_sync import PhaseSyncCoordinator
        from src.services.scenario_state_manager import ScenarioStateManager
        from src.mcp.tools.attack_simulation import get_simulation_manager

        coordinator = PhaseSyncCoordinator()
        result = await coordinator.start_scenario("apt29")

        # SimulationStateManager should have apt29
        sim_state = await get_simulation_manager().get_state()
        assert sim_state["scenario"] == "apt29"

        # ScenarioStateManager should also have apt29
        mgr = ScenarioStateManager.get_instance()
        scenario_state = await mgr.get_current_state()
        assert scenario_state.scenario_id == "apt29"

    @pytest.mark.asyncio
    async def test_start_scenario_returns_combined_status(self):
        """Start must return combined status from both managers."""
        from src.services.phase_sync import PhaseSyncCoordinator

        coordinator = PhaseSyncCoordinator()
        result = await coordinator.start_scenario("apt29")

        assert "simulation_id" in result
        assert "scenario" in result
        assert result["sync_status"] == "both_initialized"

    @pytest.mark.asyncio
    async def test_start_unknown_scenario_returns_error(self):
        """Starting an unknown scenario must return error without side effects."""
        from src.services.phase_sync import PhaseSyncCoordinator

        coordinator = PhaseSyncCoordinator()
        result = await coordinator.start_scenario("nonexistent")

        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_start_while_running_returns_error(self):
        """Starting while already running must return error."""
        from src.services.phase_sync import PhaseSyncCoordinator

        coordinator = PhaseSyncCoordinator()

        await coordinator.start_scenario("apt29")
        result = await coordinator.start_scenario("fin7")

        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_scenario_state_gets_phase_data_on_start(self):
        """ScenarioStateManager must receive phase event data on start."""
        from src.services.phase_sync import PhaseSyncCoordinator
        from src.services.scenario_state_manager import ScenarioStateManager

        coordinator = PhaseSyncCoordinator()
        await coordinator.start_scenario("apt29")

        mgr = ScenarioStateManager.get_instance()
        state = await mgr.get_current_state()
        assert state is not None
        assert state.total_phases == 8  # APT29 has 8 phases
        assert state.current_phase == 0  # Not yet advanced
