"""
Unit tests for tool handler integration with ScenarioStateManager.

Task: T-024
Requirement: REQ-002-004-001
Test ID: UT-030

Tests that the 25 SOC tool handlers query ScenarioStateManager
when a scenario is active.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestToolHandlerIntegration:
    """Tests for 25 tool handler integration with ScenarioStateManager."""

    @pytest.fixture(autouse=True)
    def setup_scenario_manager(self):
        """Set up a fresh ScenarioStateManager for each test."""
        from src.scenarios.scenario_state_manager import (
            ScenarioStateManager, reset_scenario_manager
        )
        reset_scenario_manager()
        yield
        reset_scenario_manager()

    @pytest.mark.asyncio
    async def test_siem_list_incidents_uses_scenario_data(self):
        """siem_list_incidents returns scenario data when scenario active."""
        from src.scenarios.scenario_state_manager import get_scenario_manager
        from src.mcp.tools.siem import handle_siem_list_incidents
        mgr = get_scenario_manager()
        await mgr.start_scenario("apt29")
        await mgr.advance_to_phase(3)

        result = await handle_siem_list_incidents({})
        # Should contain APT29 phase 1-3 incidents
        incident_ids = {inc["id"] for inc in result["data"]}
        assert "INC-APT29-001" in incident_ids
        assert "INC-APT29-002" in incident_ids

    @pytest.mark.asyncio
    async def test_siem_get_incident_uses_scenario_data(self):
        """siem_get_incident returns scenario incident when active."""
        from src.scenarios.scenario_state_manager import get_scenario_manager
        from src.mcp.tools.siem import handle_siem_get_incident
        mgr = get_scenario_manager()
        await mgr.start_scenario("apt29")
        await mgr.advance_to_phase(1)

        result = await handle_siem_get_incident({"incident_id": "INC-APT29-001"})
        assert result["id"] == "INC-APT29-001"
        assert "Suspicious Email" in result["title"]

    @pytest.mark.asyncio
    async def test_edr_list_detections_uses_scenario_data(self):
        """edr_list_detections returns scenario data when active."""
        from src.scenarios.scenario_state_manager import get_scenario_manager
        from src.mcp.tools.edr import handle_edr_list_detections
        mgr = get_scenario_manager()
        await mgr.start_scenario("apt29")
        await mgr.advance_to_phase(2)

        result = await handle_edr_list_detections({})
        detection_ids = {det["id"] for det in result["data"]}
        assert "DET-APT29-001" in detection_ids

    @pytest.mark.asyncio
    async def test_edr_get_detection_uses_scenario_data(self):
        """edr_get_detection returns scenario detection when active."""
        from src.scenarios.scenario_state_manager import get_scenario_manager
        from src.mcp.tools.edr import handle_edr_get_detection
        mgr = get_scenario_manager()
        await mgr.start_scenario("apt29")
        await mgr.advance_to_phase(1)

        result = await handle_edr_get_detection({"detection_id": "DET-APT29-001"})
        assert result["id"] == "DET-APT29-001"

    @pytest.mark.asyncio
    async def test_intel_get_indicator_uses_scenario_data(self):
        """intel_get_indicator returns scenario IOC when active."""
        from src.scenarios.scenario_state_manager import get_scenario_manager
        from src.mcp.tools.intel import handle_intel_get_indicator
        mgr = get_scenario_manager()
        await mgr.start_scenario("apt29")
        await mgr.advance_to_phase(1)

        result = await handle_intel_get_indicator({
            "indicator_type": "ip",
            "value": "185.29.8.162"
        })
        assert result["verdict"] == "malicious"
        assert result["confidence"] >= 90

    @pytest.mark.asyncio
    async def test_edr_contain_host_registers_mutation(self):
        """edr_contain_host should register containment in ScenarioStateManager."""
        from src.scenarios.scenario_state_manager import get_scenario_manager
        from src.mcp.tools.edr import handle_edr_contain_host
        mgr = get_scenario_manager()
        await mgr.start_scenario("apt29")
        await mgr.advance_to_phase(1)

        await handle_edr_contain_host({
            "device_id": "WS-EXEC-PC01",
            "reason": "Malware detected"
        })

        # Verify containment is tracked
        state = mgr.get_current_state()
        assert "WS-EXEC-PC01" in state.get("contained_hosts", [])

    @pytest.mark.asyncio
    async def test_siem_close_incident_registers_mutation(self):
        """siem_close_incident should register closure in ScenarioStateManager."""
        from src.scenarios.scenario_state_manager import get_scenario_manager
        from src.mcp.tools.siem import handle_siem_close_incident
        mgr = get_scenario_manager()
        await mgr.start_scenario("apt29")
        await mgr.advance_to_phase(1)

        await handle_siem_close_incident({
            "incident_id": "INC-APT29-001",
            "resolution": "true_positive"
        })

        state = mgr.get_current_state()
        assert "INC-APT29-001" in state.get("closed_incidents", [])

    @pytest.mark.asyncio
    async def test_siem_add_comment_registers_mutation(self):
        """siem_add_comment should register comment in ScenarioStateManager."""
        from src.scenarios.scenario_state_manager import get_scenario_manager
        from src.mcp.tools.siem import handle_siem_add_comment
        mgr = get_scenario_manager()
        await mgr.start_scenario("apt29")
        await mgr.advance_to_phase(1)

        await handle_siem_add_comment({
            "incident_id": "INC-APT29-001",
            "comment": "Investigating lateral movement"
        })

        state = mgr.get_current_state()
        comments = state.get("comments", {})
        assert "INC-APT29-001" in comments

    @pytest.mark.asyncio
    async def test_tickets_create_registers_mutation(self):
        """tickets_create should register ticket in ScenarioStateManager."""
        from src.scenarios.scenario_state_manager import get_scenario_manager
        from src.mcp.tools.tickets import handle_tickets_create
        mgr = get_scenario_manager()
        await mgr.start_scenario("apt29")
        await mgr.advance_to_phase(1)

        result = await handle_tickets_create({
            "title": "Containment for INC-APT29-001",
            "description": "Isolate compromised host",
            "incident_id": "INC-APT29-001"
        })

        state = mgr.get_current_state()
        assert len(state.get("tickets", [])) >= 1
