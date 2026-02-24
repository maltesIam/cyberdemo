"""
Unit tests for backward compatibility when no scenario is active.

Task: T-025
Requirement: REQ-002-004-002
Test ID: UT-031

Tests that all tool handlers return their existing static/mock data
unchanged when no scenario is active (BR-012).
"""

import pytest


class TestBackwardCompatibility:
    """Tests for backward compatibility with no active scenario."""

    @pytest.fixture(autouse=True)
    def setup_no_scenario(self):
        """Ensure no scenario is active."""
        from src.scenarios.scenario_state_manager import reset_scenario_manager
        reset_scenario_manager()
        yield
        reset_scenario_manager()

    @pytest.mark.asyncio
    async def test_siem_list_incidents_returns_static_data(self):
        """siem_list_incidents returns existing static data when no scenario."""
        from src.mcp.tools.siem import handle_siem_list_incidents
        result = await handle_siem_list_incidents({})
        # Should return the original static mock data
        ids = {inc["id"] for inc in result["data"]}
        assert "INC-ANCHOR-001" in ids

    @pytest.mark.asyncio
    async def test_siem_get_incident_returns_static_data(self):
        """siem_get_incident returns static data when no scenario."""
        from src.mcp.tools.siem import handle_siem_get_incident
        result = await handle_siem_get_incident({"incident_id": "INC-ANCHOR-001"})
        assert result["id"] == "INC-ANCHOR-001"
        assert "Suspicious PowerShell" in result["title"]

    @pytest.mark.asyncio
    async def test_edr_list_detections_returns_static_data(self):
        """edr_list_detections returns static data when no scenario."""
        from src.mcp.tools.edr import handle_edr_list_detections
        result = await handle_edr_list_detections({})
        ids = {det["id"] for det in result["data"]}
        assert "DET-001" in ids

    @pytest.mark.asyncio
    async def test_edr_get_detection_returns_static_data(self):
        """edr_get_detection returns static data when no scenario."""
        from src.mcp.tools.edr import handle_edr_get_detection
        result = await handle_edr_get_detection({"detection_id": "DET-001"})
        assert result["id"] == "DET-001"
        assert result["technique_id"] == "T1059.001"

    @pytest.mark.asyncio
    async def test_intel_returns_static_data(self):
        """intel_get_indicator returns static behavior when no scenario."""
        from src.mcp.tools.intel import handle_intel_get_indicator
        result = await handle_intel_get_indicator({
            "indicator_type": "ip",
            "value": "1.2.3.4"
        })
        # Static behavior: non-malicious for unknown IPs
        assert result["verdict"] == "benign"

    @pytest.mark.asyncio
    async def test_edr_contain_host_returns_static_response(self):
        """edr_contain_host works normally when no scenario."""
        from src.mcp.tools.edr import handle_edr_contain_host
        result = await handle_edr_contain_host({
            "device_id": "DEV-001",
            "reason": "Test"
        })
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_siem_close_incident_returns_static_response(self):
        """siem_close_incident works normally when no scenario."""
        from src.mcp.tools.siem import handle_siem_close_incident
        result = await handle_siem_close_incident({
            "incident_id": "INC-ANCHOR-001",
            "resolution": "true_positive"
        })
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_siem_add_comment_returns_static_response(self):
        """siem_add_comment works normally when no scenario."""
        from src.mcp.tools.siem import handle_siem_add_comment
        result = await handle_siem_add_comment({
            "incident_id": "INC-ANCHOR-001",
            "comment": "Test comment"
        })
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_tickets_list_returns_static_data(self):
        """tickets_list returns static data when no scenario."""
        from src.mcp.tools.tickets import handle_tickets_list
        result = await handle_tickets_list({})
        assert len(result["data"]) >= 1

    @pytest.mark.asyncio
    async def test_tickets_create_returns_static_response(self):
        """tickets_create works normally when no scenario."""
        from src.mcp.tools.tickets import handle_tickets_create
        result = await handle_tickets_create({
            "title": "Test",
            "description": "Test",
            "incident_id": "INC-001"
        })
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_ctem_returns_static_data(self):
        """ctem_get_asset_risk returns static data when no scenario."""
        from src.mcp.tools.ctem import handle_ctem_get_asset_risk
        result = await handle_ctem_get_asset_risk({"asset_id": "SRV-WEB-01"})
        assert "risk_score" in result

    @pytest.mark.asyncio
    async def test_approvals_returns_static_data(self):
        """approvals_get returns static data when no scenario."""
        from src.mcp.tools.approvals import handle_approvals_get
        result = await handle_approvals_get({"incident_id": "INC-ANCHOR-001"})
        assert "status" in result

    @pytest.mark.asyncio
    async def test_reports_returns_static_data(self):
        """reports_get_postmortem returns static data when no scenario."""
        from src.mcp.tools.reports import handle_reports_get_postmortem
        result = await handle_reports_get_postmortem({"incident_id": "INC-001"})
        assert "postmortem_id" in result

    @pytest.mark.asyncio
    async def test_edr_process_tree_returns_static_data(self):
        """edr_get_process_tree returns static data when no scenario."""
        from src.mcp.tools.edr import handle_edr_get_process_tree
        result = await handle_edr_get_process_tree({"detection_id": "DET-001"})
        assert "process_tree" in result

    @pytest.mark.asyncio
    async def test_edr_hunt_hash_returns_static_data(self):
        """edr_hunt_hash returns static data when no scenario."""
        from src.mcp.tools.edr import handle_edr_hunt_hash
        result = await handle_edr_hunt_hash({"hash": "abc123"})
        assert result["total_hosts_found"] >= 1
