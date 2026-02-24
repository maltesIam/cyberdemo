"""
Unit tests for mutation reflection in tool queries.

Task: T-026
Requirement: REQ-002-004-003
Test ID: UT-032

Tests that when the agent performs mutations (contain, close, comment),
subsequent tool queries reflect those changes immediately (BR-010).
"""

import pytest


class TestMutationReflection:
    """Tests that mutations are reflected in subsequent tool queries."""

    @pytest.fixture(autouse=True)
    def setup_active_scenario(self):
        """Set up an active APT29 scenario at phase 3."""
        from src.scenarios.scenario_state_manager import (
            get_scenario_manager, reset_scenario_manager
        )
        reset_scenario_manager()
        self.mgr = get_scenario_manager()
        yield
        reset_scenario_manager()

    async def _start_scenario_phase3(self):
        """Helper to start scenario at phase 3."""
        await self.mgr.start_scenario("apt29")
        await self.mgr.advance_to_phase(3)

    @pytest.mark.asyncio
    async def test_contained_host_reflected_in_siem_incidents(self):
        """After containing a host, SIEM incidents show the host as contained."""
        await self._start_scenario_phase3()
        from src.mcp.tools.edr import handle_edr_contain_host
        from src.mcp.tools.siem import handle_siem_list_incidents

        await handle_edr_contain_host({
            "device_id": "WS-EXEC-PC01",
            "reason": "Active compromise"
        })

        result = await handle_siem_list_incidents({})
        # Incidents related to WS-EXEC-PC01 should reflect containment
        for inc in result["data"]:
            if inc.get("asset") == "WS-EXEC-PC01":
                assert inc.get("containment_status") == "contained", (
                    f"Incident {inc['id']} on contained host should show contained status"
                )

    @pytest.mark.asyncio
    async def test_closed_incident_reflected_in_list(self):
        """After closing an incident, it shows as closed in list."""
        await self._start_scenario_phase3()
        from src.mcp.tools.siem import handle_siem_close_incident, handle_siem_list_incidents

        await handle_siem_close_incident({
            "incident_id": "INC-APT29-001",
            "resolution": "true_positive"
        })

        result = await handle_siem_list_incidents({})
        inc001 = next(
            (inc for inc in result["data"] if inc["id"] == "INC-APT29-001"), None
        )
        assert inc001 is not None
        assert inc001["status"] == "closed"

    @pytest.mark.asyncio
    async def test_closed_incident_reflected_in_get(self):
        """After closing an incident, get_incident shows it as closed."""
        await self._start_scenario_phase3()
        from src.mcp.tools.siem import handle_siem_close_incident, handle_siem_get_incident

        await handle_siem_close_incident({
            "incident_id": "INC-APT29-001",
            "resolution": "true_positive"
        })

        result = await handle_siem_get_incident({"incident_id": "INC-APT29-001"})
        assert result["status"] == "closed"

    @pytest.mark.asyncio
    async def test_comment_reflected_in_incident(self):
        """After adding a comment, the incident shows the comment."""
        await self._start_scenario_phase3()
        from src.mcp.tools.siem import handle_siem_add_comment, handle_siem_get_incident

        await handle_siem_add_comment({
            "incident_id": "INC-APT29-001",
            "comment": "Investigation started - checking lateral movement"
        })

        result = await handle_siem_get_incident({"incident_id": "INC-APT29-001"})
        comments = result.get("comments", [])
        assert len(comments) >= 1
        assert any("lateral movement" in c.get("text", "").lower() for c in comments)

    @pytest.mark.asyncio
    async def test_contained_host_reflected_in_edr_detections(self):
        """After containing a host, EDR detections show containment."""
        await self._start_scenario_phase3()
        from src.mcp.tools.edr import handle_edr_contain_host, handle_edr_list_detections

        await handle_edr_contain_host({
            "device_id": "WS-EXEC-PC01",
            "reason": "Active compromise"
        })

        result = await handle_edr_list_detections({})
        for det in result["data"]:
            if det.get("host") == "WS-EXEC-PC01":
                assert det.get("host_status") == "contained"

    @pytest.mark.asyncio
    async def test_lift_containment_reflected(self):
        """After lifting containment, host shows as active again."""
        await self._start_scenario_phase3()
        from src.mcp.tools.edr import (
            handle_edr_contain_host,
            handle_edr_lift_containment,
            handle_edr_list_detections,
        )

        # Contain then lift
        await handle_edr_contain_host({
            "device_id": "WS-EXEC-PC01",
            "reason": "Active compromise"
        })
        await handle_edr_lift_containment({
            "device_id": "WS-EXEC-PC01",
            "reason": "Remediated"
        })

        result = await handle_edr_list_detections({})
        for det in result["data"]:
            if det.get("host") == "WS-EXEC-PC01":
                assert det.get("host_status", "active") != "contained"

    @pytest.mark.asyncio
    async def test_ticket_creation_reflected(self):
        """After creating a ticket, tickets_list shows it."""
        await self._start_scenario_phase3()
        from src.mcp.tools.tickets import handle_tickets_create, handle_tickets_list

        await handle_tickets_create({
            "title": "Containment for INC-APT29-001",
            "description": "Network isolation required",
            "incident_id": "INC-APT29-001",
            "priority": "critical"
        })

        result = await handle_tickets_list({"incident_id": "INC-APT29-001"})
        assert len(result["data"]) >= 1
        ticket = result["data"][0]
        assert ticket["incident_id"] == "INC-APT29-001"
