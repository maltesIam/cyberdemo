"""
Unit tests for cumulative phase data - UT-021
Requirement: REQ-002-001-002
Description: When at phase N, state includes ALL events from phases 1 through N.
Each phase adds its events to the cumulative state.

BR-009: Data is always cumulative (earlier phase events never disappear).
BR-013: Tools must not reveal future-phase data.
"""
import pytest


def _make_phases():
    """Create a 3-phase scenario for testing cumulative behavior."""
    from src.models.scenario_types import (
        PhaseEvents,
        SiemIncident,
        EdrDetection,
        IntelIOC,
    )

    return {
        1: PhaseEvents(
            phase_number=1,
            phase_name="Initial Access",
            incidents=[
                SiemIncident(
                    id="INC-001",
                    title="Spearphishing",
                    severity="high",
                    source="sentinel",
                    mitre_tactic="initial-access",
                    mitre_technique="T1566.002",
                ),
            ],
            detections=[
                EdrDetection(
                    id="EDR-001",
                    host_id="WS-FIN-042",
                    process_name="outlook.exe",
                    action="detected",
                    severity="high",
                    mitre_technique="T1566.002",
                ),
            ],
            iocs=[
                IntelIOC(
                    id="IOC-001",
                    type="ip",
                    value="185.220.101.1",
                    threat_actor="APT29",
                    source="recorded-future",
                ),
            ],
        ),
        2: PhaseEvents(
            phase_number=2,
            phase_name="Execution",
            incidents=[
                SiemIncident(
                    id="INC-002",
                    title="PowerShell Execution",
                    severity="critical",
                    source="sentinel",
                    mitre_tactic="execution",
                    mitre_technique="T1059.001",
                ),
            ],
            detections=[
                EdrDetection(
                    id="EDR-002",
                    host_id="WS-FIN-042",
                    process_name="powershell.exe",
                    action="detected",
                    severity="critical",
                    mitre_technique="T1059.001",
                ),
            ],
            iocs=[
                IntelIOC(
                    id="IOC-002",
                    type="domain",
                    value="evil-c2.example.com",
                    threat_actor="APT29",
                    source="mandiant",
                ),
            ],
        ),
        3: PhaseEvents(
            phase_number=3,
            phase_name="Persistence",
            incidents=[
                SiemIncident(
                    id="INC-003",
                    title="Registry Modification",
                    severity="high",
                    source="sentinel",
                    mitre_tactic="persistence",
                    mitre_technique="T1547.001",
                ),
            ],
            detections=[
                EdrDetection(
                    id="EDR-003",
                    host_id="WS-FIN-042",
                    process_name="reg.exe",
                    action="detected",
                    severity="high",
                    mitre_technique="T1547.001",
                ),
                EdrDetection(
                    id="EDR-004",
                    host_id="SRV-DEV-03",
                    process_name="schtasks.exe",
                    action="detected",
                    severity="medium",
                    mitre_technique="T1053.005",
                ),
            ],
            iocs=[],  # No new IOCs in phase 3
        ),
    }


class TestCumulativePhaseData:
    """Test that state is cumulative across phases."""

    @pytest.mark.asyncio
    async def test_phase_1_has_only_phase_1_data(self):
        """At phase 1, state has only phase 1 events."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        state = await mgr.get_current_state()
        assert len(state.incidents) == 1
        assert state.incidents[0].id == "INC-001"
        assert len(state.detections) == 1
        assert state.detections[0].id == "EDR-001"
        assert len(state.iocs) == 1
        assert state.iocs[0].id == "IOC-001"

    @pytest.mark.asyncio
    async def test_phase_2_includes_phase_1_data(self):
        """At phase 2, state has events from phases 1 AND 2."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(2)

        state = await mgr.get_current_state()
        # Phase 1 + Phase 2 incidents
        assert len(state.incidents) == 2
        incident_ids = {inc.id for inc in state.incidents}
        assert "INC-001" in incident_ids  # Phase 1
        assert "INC-002" in incident_ids  # Phase 2

        # Phase 1 + Phase 2 detections
        assert len(state.detections) == 2
        detection_ids = {d.id for d in state.detections}
        assert "EDR-001" in detection_ids
        assert "EDR-002" in detection_ids

        # Phase 1 + Phase 2 IOCs
        assert len(state.iocs) == 2
        ioc_ids = {ioc.id for ioc in state.iocs}
        assert "IOC-001" in ioc_ids
        assert "IOC-002" in ioc_ids

    @pytest.mark.asyncio
    async def test_phase_3_includes_all_previous_data(self):
        """At phase 3, state has events from phases 1, 2, AND 3."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(3)

        state = await mgr.get_current_state()
        # 3 incidents total (1 per phase)
        assert len(state.incidents) == 3

        # 4 detections total (1 + 1 + 2)
        assert len(state.detections) == 4
        detection_ids = {d.id for d in state.detections}
        assert "EDR-001" in detection_ids
        assert "EDR-002" in detection_ids
        assert "EDR-003" in detection_ids
        assert "EDR-004" in detection_ids

        # 2 IOCs total (phase 3 has none)
        assert len(state.iocs) == 2

    @pytest.mark.asyncio
    async def test_earlier_phase_events_never_disappear(self):
        """BR-009: Earlier phase events remain when advancing."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_phases()
        await mgr.start_scenario("test", "Test", phases)

        # Advance to phase 1
        await mgr.advance_to_phase(1)
        state1 = await mgr.get_current_state()
        phase1_incidents = [inc.id for inc in state1.incidents]

        # Advance to phase 3
        await mgr.advance_to_phase(3)
        state3 = await mgr.get_current_state()
        phase3_incidents = [inc.id for inc in state3.incidents]

        # All phase 1 incidents still present in phase 3
        for inc_id in phase1_incidents:
            assert inc_id in phase3_incidents, f"Incident {inc_id} from phase 1 disappeared"

    @pytest.mark.asyncio
    async def test_no_future_phase_data_leak(self):
        """BR-013: At phase 1, no data from phase 2 or 3 should be visible."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        state = await mgr.get_current_state()
        incident_ids = {inc.id for inc in state.incidents}
        detection_ids = {d.id for d in state.detections}
        ioc_ids = {ioc.id for ioc in state.iocs}

        # No phase 2 or 3 data should be present
        assert "INC-002" not in incident_ids
        assert "INC-003" not in incident_ids
        assert "EDR-002" not in detection_ids
        assert "EDR-003" not in detection_ids
        assert "EDR-004" not in detection_ids
        assert "IOC-002" not in ioc_ids

    @pytest.mark.asyncio
    async def test_jump_to_phase_rebuilds_cumulative_data(self):
        """Jumping directly to phase 3 (without visiting 1,2) still accumulates."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_phases()
        await mgr.start_scenario("test", "Test", phases)
        # Jump directly to phase 3
        await mgr.advance_to_phase(3)

        state = await mgr.get_current_state()
        assert len(state.incidents) == 3
        assert len(state.detections) == 4
        assert len(state.iocs) == 2
        assert state.current_phase == 3

    @pytest.mark.asyncio
    async def test_advance_backward_rebuilds_correctly(self):
        """Going from phase 3 back to phase 1 removes phase 2,3 data."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_phases()
        await mgr.start_scenario("test", "Test", phases)

        await mgr.advance_to_phase(3)
        state3 = await mgr.get_current_state()
        assert len(state3.incidents) == 3

        await mgr.advance_to_phase(1)
        state1 = await mgr.get_current_state()
        assert len(state1.incidents) == 1
        assert state1.incidents[0].id == "INC-001"
        assert len(state1.detections) == 1
        assert len(state1.iocs) == 1

    @pytest.mark.asyncio
    async def test_invalid_phase_number_raises(self):
        """Phase number out of range raises ValueError."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_phases()
        await mgr.start_scenario("test", "Test", phases)

        with pytest.raises(ValueError, match="out of range"):
            await mgr.advance_to_phase(0)

        with pytest.raises(ValueError, match="out of range"):
            await mgr.advance_to_phase(4)

    @pytest.mark.asyncio
    async def test_advance_without_scenario_raises(self):
        """Advancing without an active scenario raises ValueError."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        with pytest.raises(ValueError, match="No scenario is active"):
            await mgr.advance_to_phase(1)
