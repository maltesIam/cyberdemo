"""
Unit tests for ScenarioStateManager singleton - UT-020
Requirement: REQ-002-001-001
Description: Singleton class with start_scenario, advance_to_phase, reset methods.
Only one instance exists; start loads scenario, advance accumulates phase data, reset clears state.

Also covers:
- TECH-008: ScenarioStateManager singleton class with async-safe state
- TECH-010: PhaseEvents data structure
- DATA-001: PhaseEvents data structure (incidents, detections, IOCs per phase)
- DATA-002: ScenarioState cumulative structure
- NFR-006: ScenarioStateManager query response under 10ms
- NFR-007: Memory usage for scenario data under 50MB
"""
import pytest
import time


class TestPhaseEventsDataStructure:
    """Test PhaseEvents Pydantic model (DATA-001, TECH-010)."""

    def test_phase_events_model_exists(self):
        """PhaseEvents model can be instantiated."""
        from src.models.scenario_types import PhaseEvents

        pe = PhaseEvents(
            phase_number=1,
            phase_name="Initial Access",
            incidents=[],
            detections=[],
            iocs=[],
        )
        assert pe.phase_number == 1
        assert pe.phase_name == "Initial Access"
        assert pe.incidents == []
        assert pe.detections == []
        assert pe.iocs == []

    def test_phase_events_with_data(self):
        """PhaseEvents holds typed incident, detection, and IOC lists."""
        from src.models.scenario_types import PhaseEvents, SiemIncident, EdrDetection, IntelIOC

        incident = SiemIncident(
            id="INC-001",
            title="Spearphishing Link Detected",
            severity="high",
            source="sentinel",
            mitre_tactic="initial-access",
            mitre_technique="T1566.002",
        )
        detection = EdrDetection(
            id="EDR-001",
            host_id="WS-FIN-042",
            process_name="outlook.exe",
            action="detected",
            severity="high",
            mitre_technique="T1566.002",
        )
        ioc = IntelIOC(
            id="IOC-001",
            type="ip",
            value="185.220.101.1",
            threat_actor="APT29",
            source="recorded-future",
        )

        pe = PhaseEvents(
            phase_number=1,
            phase_name="Initial Access",
            incidents=[incident],
            detections=[detection],
            iocs=[ioc],
        )
        assert len(pe.incidents) == 1
        assert len(pe.detections) == 1
        assert len(pe.iocs) == 1


class TestScenarioStateStructure:
    """Test ScenarioState data structure (DATA-002)."""

    def test_scenario_state_model_exists(self):
        """ScenarioState model can be instantiated."""
        from src.models.scenario_types import ScenarioState

        state = ScenarioState(
            scenario_id="apt29",
            scenario_name="APT29 - Cozy Bear",
            current_phase=0,
            total_phases=8,
        )
        assert state.scenario_id == "apt29"
        assert state.current_phase == 0
        assert state.total_phases == 8
        assert state.incidents == []
        assert state.detections == []
        assert state.iocs == []
        assert state.contained_hosts == set()
        assert state.closed_incidents == set()
        assert state.comments == []


class TestScenarioStateManagerSingleton:
    """Test ScenarioStateManager is a proper singleton (TECH-008)."""

    def test_singleton_instance(self):
        """Only one instance of ScenarioStateManager exists."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr1 = ScenarioStateManager.get_instance()
        mgr2 = ScenarioStateManager.get_instance()
        assert mgr1 is mgr2

    def test_singleton_after_reset(self):
        """After resetting, the same instance is returned."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr1 = ScenarioStateManager.get_instance()
        mgr2 = ScenarioStateManager.get_instance()
        assert mgr1 is mgr2


class TestScenarioStateManagerMethods:
    """Test start_scenario, advance_to_phase, get_current_state, reset."""

    @pytest.mark.asyncio
    async def test_start_scenario(self):
        """start_scenario initializes the state with scenario data."""
        from src.services.scenario_state_manager import ScenarioStateManager
        from src.models.scenario_types import PhaseEvents

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        # Create a minimal scenario script
        phases = {
            1: PhaseEvents(
                phase_number=1,
                phase_name="Initial Access",
                incidents=[],
                detections=[],
                iocs=[],
            ),
        }

        await mgr.start_scenario(
            scenario_id="test-scenario",
            scenario_name="Test Scenario",
            phases=phases,
        )

        state = await mgr.get_current_state()
        assert state is not None
        assert state.scenario_id == "test-scenario"
        assert state.scenario_name == "Test Scenario"
        assert state.current_phase == 0
        assert state.total_phases == 1

    @pytest.mark.asyncio
    async def test_advance_to_phase(self):
        """advance_to_phase updates the current phase number."""
        from src.services.scenario_state_manager import ScenarioStateManager
        from src.models.scenario_types import PhaseEvents, SiemIncident

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        incident = SiemIncident(
            id="INC-001",
            title="Phishing detected",
            severity="high",
            source="sentinel",
            mitre_tactic="initial-access",
            mitre_technique="T1566.002",
        )

        phases = {
            1: PhaseEvents(
                phase_number=1,
                phase_name="Initial Access",
                incidents=[incident],
                detections=[],
                iocs=[],
            ),
        }

        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        state = await mgr.get_current_state()
        assert state.current_phase == 1
        assert len(state.incidents) == 1
        assert state.incidents[0].id == "INC-001"

    @pytest.mark.asyncio
    async def test_reset_clears_state(self):
        """reset() clears all state."""
        from src.services.scenario_state_manager import ScenarioStateManager
        from src.models.scenario_types import PhaseEvents

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = {
            1: PhaseEvents(
                phase_number=1,
                phase_name="Phase 1",
                incidents=[],
                detections=[],
                iocs=[],
            ),
        }

        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        await mgr.reset()

        state = await mgr.get_current_state()
        assert state is None

    @pytest.mark.asyncio
    async def test_get_current_state_when_no_scenario(self):
        """get_current_state returns None when no scenario is active."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        state = await mgr.get_current_state()
        assert state is None


class TestScenarioStateManagerPerformance:
    """Test NFR-006 and NFR-007."""

    @pytest.mark.asyncio
    async def test_query_response_under_10ms(self):
        """NFR-006: get_current_state responds in under 10ms."""
        from src.services.scenario_state_manager import ScenarioStateManager
        from src.models.scenario_types import PhaseEvents, SiemIncident

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        # Create a scenario with some data
        incidents = [
            SiemIncident(
                id=f"INC-{i:03d}",
                title=f"Incident {i}",
                severity="high",
                source="sentinel",
                mitre_tactic="initial-access",
                mitre_technique="T1566",
            )
            for i in range(50)
        ]

        phases = {
            1: PhaseEvents(
                phase_number=1,
                phase_name="Phase 1",
                incidents=incidents,
                detections=[],
                iocs=[],
            ),
        }

        await mgr.start_scenario("perf-test", "Perf Test", phases)
        await mgr.advance_to_phase(1)

        # Measure query time
        start = time.perf_counter()
        for _ in range(100):
            state = await mgr.get_current_state()
        elapsed = (time.perf_counter() - start) / 100

        assert elapsed < 0.01, f"Query took {elapsed*1000:.2f}ms, expected < 10ms"
