"""
Unit tests for agent mutation persistence - UT-022
Requirement: REQ-002-001-003
Description: When the agent performs mutations (contain host, close incident,
add comment), these persist in the ScenarioState and are reflected in
subsequent tool queries.

BR-010: Agent mutations are immediate and visible to subsequent tool calls.
BR-014: Contained hosts show status "contained" in all relevant tool responses.
BR-015: Closed incidents show status "closed" in all tool responses.
DATA-006: Agent mutation format.
"""
import pytest


def _make_scenario_phases():
    """Create a scenario for mutation testing."""
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
                    title="Spearphishing Detected",
                    severity="high",
                    source="sentinel",
                    mitre_tactic="initial-access",
                    mitre_technique="T1566.002",
                    host_id="WS-FIN-042",
                    status="new",
                ),
                SiemIncident(
                    id="INC-002",
                    title="Suspicious PowerShell",
                    severity="critical",
                    source="sentinel",
                    mitre_tactic="execution",
                    mitre_technique="T1059.001",
                    host_id="WS-FIN-042",
                    status="new",
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
                    id="INC-003",
                    title="Lateral Movement",
                    severity="critical",
                    source="sentinel",
                    mitre_tactic="lateral-movement",
                    mitre_technique="T1021.002",
                    host_id="SRV-DEV-03",
                    status="new",
                ),
            ],
            detections=[],
            iocs=[],
        ),
    }


class TestContainHostMutation:
    """Test contain_host agent mutation."""

    @pytest.mark.asyncio
    async def test_contain_host_adds_to_contained_set(self):
        """contain_host adds the host to contained_hosts."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_scenario_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        await mgr.contain_host("WS-FIN-042")

        state = await mgr.get_current_state()
        assert "WS-FIN-042" in state.contained_hosts

    @pytest.mark.asyncio
    async def test_contain_host_persists_across_queries(self):
        """Contained host is visible in subsequent queries."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_scenario_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        await mgr.contain_host("WS-FIN-042")

        # Query multiple times
        state1 = await mgr.get_current_state()
        state2 = await mgr.get_current_state()
        assert "WS-FIN-042" in state1.contained_hosts
        assert "WS-FIN-042" in state2.contained_hosts

    @pytest.mark.asyncio
    async def test_contain_host_persists_after_phase_advance(self):
        """Contained host persists when advancing to next phase."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_scenario_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        await mgr.contain_host("WS-FIN-042")
        await mgr.advance_to_phase(2)

        state = await mgr.get_current_state()
        assert "WS-FIN-042" in state.contained_hosts

    @pytest.mark.asyncio
    async def test_multiple_hosts_can_be_contained(self):
        """Multiple hosts can be contained independently."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_scenario_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        await mgr.contain_host("WS-FIN-042")
        await mgr.contain_host("SRV-DEV-03")

        state = await mgr.get_current_state()
        assert "WS-FIN-042" in state.contained_hosts
        assert "SRV-DEV-03" in state.contained_hosts
        assert len(state.contained_hosts) == 2


class TestCloseIncidentMutation:
    """Test close_incident agent mutation."""

    @pytest.mark.asyncio
    async def test_close_incident_adds_to_closed_set(self):
        """close_incident adds the incident to closed_incidents."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_scenario_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        await mgr.close_incident("INC-001")

        state = await mgr.get_current_state()
        assert "INC-001" in state.closed_incidents

    @pytest.mark.asyncio
    async def test_close_incident_updates_status_in_incidents_list(self):
        """BR-015: Closed incident status is 'closed' in the incidents list."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_scenario_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        await mgr.close_incident("INC-001")

        state = await mgr.get_current_state()
        inc = next(i for i in state.incidents if i.id == "INC-001")
        assert inc.status == "closed"

    @pytest.mark.asyncio
    async def test_closed_incident_persists_after_phase_advance(self):
        """Closed status persists when rebuilding cumulative data."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_scenario_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        await mgr.close_incident("INC-001")
        await mgr.advance_to_phase(2)

        state = await mgr.get_current_state()
        assert "INC-001" in state.closed_incidents
        inc = next(i for i in state.incidents if i.id == "INC-001")
        assert inc.status == "closed"

    @pytest.mark.asyncio
    async def test_non_closed_incidents_remain_new(self):
        """Closing one incident does not affect others."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_scenario_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        await mgr.close_incident("INC-001")

        state = await mgr.get_current_state()
        inc2 = next(i for i in state.incidents if i.id == "INC-002")
        assert inc2.status == "new"


class TestAddCommentMutation:
    """Test add_comment agent mutation."""

    @pytest.mark.asyncio
    async def test_add_comment_persists(self):
        """Added comments persist in state."""
        from src.services.scenario_state_manager import ScenarioStateManager
        from src.models.scenario_types import AgentComment

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_scenario_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        comment = AgentComment(
            id="CMT-001",
            incident_id="INC-001",
            content="Confirmed: this is a true positive phishing attempt",
        )
        await mgr.add_comment(comment)

        state = await mgr.get_current_state()
        assert len(state.comments) == 1
        assert state.comments[0].id == "CMT-001"
        assert state.comments[0].incident_id == "INC-001"
        assert "true positive" in state.comments[0].content

    @pytest.mark.asyncio
    async def test_multiple_comments_persist(self):
        """Multiple comments can be added to the same or different incidents."""
        from src.services.scenario_state_manager import ScenarioStateManager
        from src.models.scenario_types import AgentComment

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_scenario_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        await mgr.add_comment(AgentComment(
            id="CMT-001", incident_id="INC-001", content="Analysis in progress",
        ))
        await mgr.add_comment(AgentComment(
            id="CMT-002", incident_id="INC-001", content="True positive confirmed",
        ))
        await mgr.add_comment(AgentComment(
            id="CMT-003", incident_id="INC-002", content="Investigating PowerShell activity",
        ))

        state = await mgr.get_current_state()
        assert len(state.comments) == 3

    @pytest.mark.asyncio
    async def test_comments_persist_after_phase_advance(self):
        """Comments remain after advancing phases."""
        from src.services.scenario_state_manager import ScenarioStateManager
        from src.models.scenario_types import AgentComment

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        phases = _make_scenario_phases()
        await mgr.start_scenario("test", "Test", phases)
        await mgr.advance_to_phase(1)

        await mgr.add_comment(AgentComment(
            id="CMT-001", incident_id="INC-001", content="Phase 1 analysis",
        ))

        await mgr.advance_to_phase(2)

        state = await mgr.get_current_state()
        assert len(state.comments) == 1
        assert state.comments[0].id == "CMT-001"


class TestMutationsNoScenario:
    """Test mutations when no scenario is active."""

    @pytest.mark.asyncio
    async def test_contain_host_noop_when_no_scenario(self):
        """contain_host does nothing when no scenario is active."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        # Should not raise
        await mgr.contain_host("WS-FIN-042")
        state = await mgr.get_current_state()
        assert state is None

    @pytest.mark.asyncio
    async def test_close_incident_noop_when_no_scenario(self):
        """close_incident does nothing when no scenario is active."""
        from src.services.scenario_state_manager import ScenarioStateManager

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        await mgr.close_incident("INC-001")
        state = await mgr.get_current_state()
        assert state is None

    @pytest.mark.asyncio
    async def test_add_comment_noop_when_no_scenario(self):
        """add_comment does nothing when no scenario is active."""
        from src.services.scenario_state_manager import ScenarioStateManager
        from src.models.scenario_types import AgentComment

        mgr = ScenarioStateManager.get_instance()
        await mgr.reset()

        comment = AgentComment(
            id="CMT-001", incident_id="INC-001", content="Test",
        )
        await mgr.add_comment(comment)
        state = await mgr.get_current_state()
        assert state is None
