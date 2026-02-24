"""
Unit tests for exclusive scenario lock - UT-024
Requirement: REQ-002-001-005
Description: Only one scenario can be active at a time.
Starting a new scenario must reset the previous one first.

BR-011: Only one scenario can be active at a time.
"""
import pytest


def _make_phases(prefix: str = ""):
    """Create minimal phases for exclusive scenario testing."""
    from src.models.scenario_types import PhaseEvents, SiemIncident

    return {
        1: PhaseEvents(
            phase_number=1,
            phase_name=f"{prefix}Phase 1",
            incidents=[
                SiemIncident(
                    id=f"{prefix}INC-001",
                    title=f"{prefix}Incident 1",
                    severity="high",
                    source="sentinel",
                    mitre_tactic="initial-access",
                    mitre_technique="T1566",
                ),
            ],
            detections=[],
            iocs=[],
        ),
    }


class TestExclusiveScenarioLock:
    """Test that only one scenario can be active at a time."""

    @pytest.mark.asyncio
    async def test_starting_new_scenario_resets_previous(self):
        """Starting a new scenario completely replaces the old one."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        # Start scenario A
        phases_a = _make_phases("A-")
        await mgr.start_scenario("apt29", "APT29", phases_a)
        await mgr.advance_to_phase(1)

        state_a = await mgr.get_current_state()
        assert state_a.scenario_id == "apt29"
        assert len(state_a.incidents) == 1
        assert state_a.incidents[0].id == "A-INC-001"

        # Start scenario B - should replace A
        phases_b = _make_phases("B-")
        await mgr.start_scenario("fin7", "FIN7", phases_b)

        state_b = await mgr.get_current_state()
        assert state_b.scenario_id == "fin7"
        assert state_b.scenario_name == "FIN7"
        # Should be at phase 0 (fresh start)
        assert state_b.current_phase == 0
        # No accumulated data yet (not advanced)
        assert len(state_b.incidents) == 0

    @pytest.mark.asyncio
    async def test_previous_mutations_cleared_on_new_scenario(self):
        """Mutations from previous scenario are cleared when starting new one."""
        from src.services.scenario_state_manager import ScenarioStateManager
        from src.models.scenario_types import AgentComment

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        # Start scenario A and add mutations
        phases_a = _make_phases("A-")
        await mgr.start_scenario("apt29", "APT29", phases_a)
        await mgr.advance_to_phase(1)
        await mgr.contain_host("WS-FIN-042")
        await mgr.close_incident("A-INC-001")
        await mgr.add_comment(AgentComment(
            id="CMT-001", incident_id="A-INC-001", content="Analysis done",
        ))

        state_a = await mgr.get_current_state()
        assert len(state_a.contained_hosts) == 1
        assert len(state_a.closed_incidents) == 1
        assert len(state_a.comments) == 1

        # Start scenario B
        phases_b = _make_phases("B-")
        await mgr.start_scenario("fin7", "FIN7", phases_b)

        state_b = await mgr.get_current_state()
        # All mutations from scenario A should be gone
        assert len(state_b.contained_hosts) == 0
        assert len(state_b.closed_incidents) == 0
        assert len(state_b.comments) == 0

    @pytest.mark.asyncio
    async def test_only_one_active_scenario_id(self):
        """get_active_scenario_id returns the latest scenario."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases_a = _make_phases("A-")
        await mgr.start_scenario("apt29", "APT29", phases_a)
        assert mgr.get_active_scenario_id() == "apt29"

        phases_b = _make_phases("B-")
        await mgr.start_scenario("fin7", "FIN7", phases_b)
        assert mgr.get_active_scenario_id() == "fin7"

    @pytest.mark.asyncio
    async def test_is_scenario_active(self):
        """is_scenario_active correctly reports active state."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        assert mgr.is_scenario_active() is False

        phases = _make_phases()
        await mgr.start_scenario("test", "Test", phases)
        assert mgr.is_scenario_active() is True

        await mgr.reset()
        assert mgr.is_scenario_active() is False

    @pytest.mark.asyncio
    async def test_new_scenario_has_correct_total_phases(self):
        """Each new scenario has its own total_phases count."""
        from src.services.scenario_state_manager import ScenarioStateManager
        from src.models.scenario_types import PhaseEvents

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        # Scenario with 3 phases
        phases_3 = {
            i: PhaseEvents(
                phase_number=i,
                phase_name=f"Phase {i}",
                incidents=[],
                detections=[],
                iocs=[],
            )
            for i in range(1, 4)
        }
        await mgr.start_scenario("three", "Three", phases_3)
        state = await mgr.get_current_state()
        assert state.total_phases == 3

        # Start scenario with 1 phase
        phases_1 = {
            1: PhaseEvents(
                phase_number=1,
                phase_name="Phase 1",
                incidents=[],
                detections=[],
                iocs=[],
            ),
        }
        await mgr.start_scenario("one", "One", phases_1)
        state = await mgr.get_current_state()
        assert state.total_phases == 1

    @pytest.mark.asyncio
    async def test_phase_data_isolated_between_scenarios(self):
        """Phase data from previous scenario cannot leak into new one."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        # Scenario A: advance to phase 1 to populate data
        phases_a = _make_phases("A-")
        await mgr.start_scenario("apt29", "APT29", phases_a)
        await mgr.advance_to_phase(1)

        state_a = await mgr.get_current_state()
        assert len(state_a.incidents) == 1

        # Scenario B: no advance, should have no incidents
        phases_b = _make_phases("B-")
        await mgr.start_scenario("fin7", "FIN7", phases_b)

        state_b = await mgr.get_current_state()
        assert len(state_b.incidents) == 0

        # Now advance B and verify it has B data, not A data
        await mgr.advance_to_phase(1)
        state_b2 = await mgr.get_current_state()
        assert len(state_b2.incidents) == 1
        assert state_b2.incidents[0].id == "B-INC-001"
