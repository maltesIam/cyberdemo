"""
MCP E2E Integration Tests

Tests the MCP integration from SoulInTheBot perspective:
- Frontend MCP server connectivity
- Backend MCP server connectivity
- Data MCP server connectivity
- Full investigation flow via MCP tools
- Demo scenario execution via MCP

These tests use mocked MCP responses to verify message format and tool invocations
without requiring actual MCP servers to be running.
"""

import pytest
import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone


# =============================================================================
# Mock MCP Client for Testing
# =============================================================================

class MockMCPClient:
    """Mock MCP client that simulates MCP server responses."""

    def __init__(self, server_type: str):
        self.server_type = server_type
        self.connected = False
        self.tools: dict[str, dict[str, Any]] = {}
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Setup mock tools based on server type."""
        if self.server_type == "frontend":
            self.tools = {
                "ui_show_alert": {
                    "name": "ui_show_alert",
                    "description": "Display alert in the SOC dashboard",
                    "inputSchema": {"type": "object", "properties": {"message": {"type": "string"}}}
                },
                "ui_update_status": {
                    "name": "ui_update_status",
                    "description": "Update investigation status in UI",
                    "inputSchema": {"type": "object", "properties": {"status": {"type": "string"}}}
                },
                "ui_show_timeline": {
                    "name": "ui_show_timeline",
                    "description": "Display investigation timeline",
                    "inputSchema": {"type": "object", "properties": {"events": {"type": "array"}}}
                },
            }
        elif self.server_type == "backend":
            self.tools = {
                "siem_list_incidents": {
                    "name": "siem_list_incidents",
                    "description": "List incidents from SIEM",
                    "inputSchema": {"type": "object", "properties": {}}
                },
                "siem_get_incident": {
                    "name": "siem_get_incident",
                    "description": "Get specific incident details",
                    "inputSchema": {"type": "object", "properties": {"incident_id": {"type": "string"}}, "required": ["incident_id"]}
                },
                "edr_contain_host": {
                    "name": "edr_contain_host",
                    "description": "Contain a host via EDR",
                    "inputSchema": {"type": "object", "properties": {"device_id": {"type": "string"}, "reason": {"type": "string"}}, "required": ["device_id"]}
                },
                "intel_get_indicator": {
                    "name": "intel_get_indicator",
                    "description": "Get threat intelligence for indicator",
                    "inputSchema": {"type": "object", "properties": {"indicator_type": {"type": "string"}, "value": {"type": "string"}}, "required": ["indicator_type", "value"]}
                },
                "ctem_get_asset_risk": {
                    "name": "ctem_get_asset_risk",
                    "description": "Get CTEM risk for asset",
                    "inputSchema": {"type": "object", "properties": {"asset_id": {"type": "string"}}, "required": ["asset_id"]}
                },
                "approvals_request": {
                    "name": "approvals_request",
                    "description": "Request approval for action",
                    "inputSchema": {"type": "object", "properties": {"incident_id": {"type": "string"}, "action": {"type": "string"}}, "required": ["incident_id", "action"]}
                },
                "tickets_create": {
                    "name": "tickets_create",
                    "description": "Create a ticket in ITSM",
                    "inputSchema": {"type": "object", "properties": {"title": {"type": "string"}, "description": {"type": "string"}}, "required": ["title"]}
                },
                "reports_generate_postmortem": {
                    "name": "reports_generate_postmortem",
                    "description": "Generate postmortem report",
                    "inputSchema": {"type": "object", "properties": {"incident_id": {"type": "string"}}, "required": ["incident_id"]}
                },
            }
        elif self.server_type == "data":
            self.tools = {
                "data_generate_assets": {
                    "name": "data_generate_assets",
                    "description": "Generate synthetic asset data",
                    "inputSchema": {"type": "object", "properties": {"count": {"type": "integer"}}}
                },
                "data_generate_edr_detections": {
                    "name": "data_generate_edr_detections",
                    "description": "Generate synthetic EDR detections",
                    "inputSchema": {"type": "object", "properties": {"count": {"type": "integer"}}}
                },
                "data_generate_siem_incidents": {
                    "name": "data_generate_siem_incidents",
                    "description": "Generate synthetic SIEM incidents",
                    "inputSchema": {"type": "object", "properties": {"count": {"type": "integer"}}}
                },
                "data_generate_all": {
                    "name": "data_generate_all",
                    "description": "Generate all synthetic data",
                    "inputSchema": {"type": "object", "properties": {}}
                },
                "data_reset": {
                    "name": "data_reset",
                    "description": "Reset all generated data",
                    "inputSchema": {"type": "object", "properties": {}}
                },
            }

    async def connect(self) -> bool:
        """Simulate connecting to MCP server."""
        self.connected = True
        return True

    async def disconnect(self) -> None:
        """Simulate disconnecting from MCP server."""
        self.connected = False

    async def send_message(self, message: dict[str, Any]) -> dict[str, Any]:
        """Simulate sending JSON-RPC message to MCP server."""
        if not self.connected:
            return {"jsonrpc": "2.0", "id": message.get("id"), "error": {"code": -32000, "message": "Not connected"}}

        method = message.get("method")
        msg_id = message.get("id", 1)

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": list(self.tools.values())}
            }
        elif method == "tools/call":
            params = message.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if tool_name not in self.tools:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                }

            # Simulate tool execution
            result = self._execute_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result)}]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }

    def _execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Simulate tool execution and return mock result."""
        # Frontend tools
        if tool_name == "ui_show_alert":
            return {"status": "success", "displayed": True, "message": arguments.get("message", "")}
        elif tool_name == "ui_update_status":
            return {"status": "success", "updated": True, "new_status": arguments.get("status", "")}
        elif tool_name == "ui_show_timeline":
            return {"status": "success", "rendered": True, "event_count": len(arguments.get("events", []))}

        # Backend tools
        elif tool_name == "siem_list_incidents":
            return {
                "status": "success",
                "incidents": [
                    {"id": "INC-001", "severity": "Critical", "status": "Open"},
                    {"id": "INC-002", "severity": "High", "status": "Investigating"},
                ]
            }
        elif tool_name == "siem_get_incident":
            incident_id = arguments.get("incident_id", "INC-001")
            return {
                "status": "success",
                "incident": {
                    "id": incident_id,
                    "severity": "Critical",
                    "status": "Open",
                    "alerts": [{"id": f"ALT-{incident_id}-001", "type": "malware"}],
                    "asset": {"device_id": "WS-FIN-042", "hostname": "WS-FIN-042.corp.acme.com"}
                }
            }
        elif tool_name == "edr_contain_host":
            return {
                "status": "success",
                "device_id": arguments.get("device_id"),
                "containment_status": "isolated",
                "action_id": f"ACT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            }
        elif tool_name == "intel_get_indicator":
            return {
                "status": "success",
                "indicator": {
                    "type": arguments.get("indicator_type"),
                    "value": arguments.get("value"),
                    "verdict": "malicious",
                    "vt_score": 58,
                    "vt_total": 72,
                    "confidence": 95
                }
            }
        elif tool_name == "ctem_get_asset_risk":
            return {
                "status": "success",
                "asset_id": arguments.get("asset_id"),
                "risk_color": "Red",
                "cve_count": 2,
                "cves": ["CVE-2024-1234", "CVE-2024-5678"]
            }
        elif tool_name == "approvals_request":
            return {
                "status": "success",
                "approval_id": f"APR-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                "incident_id": arguments.get("incident_id"),
                "action": arguments.get("action"),
                "state": "pending"
            }
        elif tool_name == "tickets_create":
            return {
                "status": "success",
                "ticket_id": f"TKT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                "title": arguments.get("title"),
                "state": "open"
            }
        elif tool_name == "reports_generate_postmortem":
            return {
                "status": "success",
                "postmortem_id": f"PM-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                "incident_id": arguments.get("incident_id"),
                "generated": True
            }

        # Data tools
        elif tool_name == "data_generate_assets":
            count = arguments.get("count", 10)
            return {"status": "success", "count": count, "assets": [f"ASSET-{i:03d}" for i in range(count)]}
        elif tool_name == "data_generate_edr_detections":
            count = arguments.get("count", 5)
            return {"status": "success", "count": count, "detections": [f"DET-{i:03d}" for i in range(count)]}
        elif tool_name == "data_generate_siem_incidents":
            count = arguments.get("count", 3)
            return {"status": "success", "count": count, "incidents": [f"INC-{i:03d}" for i in range(count)]}
        elif tool_name == "data_generate_all":
            return {
                "status": "success",
                "summary": {
                    "assets": 10,
                    "detections": 5,
                    "incidents": 3,
                    "intel": 20
                }
            }
        elif tool_name == "data_reset":
            return {"status": "success", "message": "All generated data has been cleared"}

        return {"status": "error", "message": f"Unknown tool: {tool_name}"}


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def frontend_mcp_client() -> MockMCPClient:
    """Mock MCP client for frontend server."""
    return MockMCPClient("frontend")


@pytest.fixture
def backend_mcp_client() -> MockMCPClient:
    """Mock MCP client for backend server."""
    return MockMCPClient("backend")


@pytest.fixture
def data_mcp_client() -> MockMCPClient:
    """Mock MCP client for data server."""
    return MockMCPClient("data")


# =============================================================================
# TEST 1: Frontend MCP Server Responds
# =============================================================================

class TestE2EMCPFrontendFromSoulInTheBot:
    """Test frontend MCP server connectivity and tools."""

    @pytest.mark.asyncio
    async def test_e2e_mcp_frontend_connects(self, frontend_mcp_client: MockMCPClient):
        """
        GIVEN SoulInTheBot wants to connect to Frontend MCP server
        WHEN connection is established
        THEN the client should be connected
        """
        result = await frontend_mcp_client.connect()
        assert result is True
        assert frontend_mcp_client.connected is True

    @pytest.mark.asyncio
    async def test_e2e_mcp_frontend_lists_tools(self, frontend_mcp_client: MockMCPClient):
        """
        GIVEN Frontend MCP server is connected
        WHEN tools/list is requested
        THEN it should return UI tools
        """
        await frontend_mcp_client.connect()

        response = await frontend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        })

        assert "result" in response
        tools = response["result"]["tools"]
        tool_names = {t["name"] for t in tools}

        assert "ui_show_alert" in tool_names
        assert "ui_update_status" in tool_names
        assert "ui_show_timeline" in tool_names

    @pytest.mark.asyncio
    async def test_e2e_mcp_frontend_show_alert(self, frontend_mcp_client: MockMCPClient):
        """
        GIVEN Frontend MCP server is connected
        WHEN ui_show_alert tool is invoked
        THEN alert should be displayed in UI
        """
        await frontend_mcp_client.connect()

        response = await frontend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "ui_show_alert",
                "arguments": {"message": "Critical incident detected: INC-001"}
            }
        })

        assert "result" in response
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["status"] == "success"
        assert content["displayed"] is True


# =============================================================================
# TEST 2: Backend MCP Server Responds
# =============================================================================

class TestE2EMCPBackendFromSoulInTheBot:
    """Test backend MCP server connectivity and tools."""

    @pytest.mark.asyncio
    async def test_e2e_mcp_backend_connects(self, backend_mcp_client: MockMCPClient):
        """
        GIVEN SoulInTheBot wants to connect to Backend MCP server
        WHEN connection is established
        THEN the client should be connected
        """
        result = await backend_mcp_client.connect()
        assert result is True
        assert backend_mcp_client.connected is True

    @pytest.mark.asyncio
    async def test_e2e_mcp_backend_lists_tools(self, backend_mcp_client: MockMCPClient):
        """
        GIVEN Backend MCP server is connected
        WHEN tools/list is requested
        THEN it should return SOC tools (SIEM, EDR, Intel, CTEM)
        """
        await backend_mcp_client.connect()

        response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        })

        assert "result" in response
        tools = response["result"]["tools"]
        tool_names = {t["name"] for t in tools}

        # SIEM tools
        assert "siem_list_incidents" in tool_names
        assert "siem_get_incident" in tool_names

        # EDR tools
        assert "edr_contain_host" in tool_names

        # Intel tools
        assert "intel_get_indicator" in tool_names

        # CTEM tools
        assert "ctem_get_asset_risk" in tool_names

    @pytest.mark.asyncio
    async def test_e2e_mcp_backend_siem_get_incident(self, backend_mcp_client: MockMCPClient):
        """
        GIVEN Backend MCP server is connected
        WHEN siem_get_incident tool is invoked
        THEN incident details should be returned
        """
        await backend_mcp_client.connect()

        response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "siem_get_incident",
                "arguments": {"incident_id": "INC-ANCHOR-001"}
            }
        })

        assert "result" in response
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["status"] == "success"
        assert "incident" in content
        assert content["incident"]["id"] == "INC-ANCHOR-001"

    @pytest.mark.asyncio
    async def test_e2e_mcp_backend_edr_contain(self, backend_mcp_client: MockMCPClient):
        """
        GIVEN Backend MCP server is connected
        WHEN edr_contain_host tool is invoked
        THEN host should be isolated
        """
        await backend_mcp_client.connect()

        response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "edr_contain_host",
                "arguments": {"device_id": "WS-FIN-042", "reason": "Malware detected"}
            }
        })

        assert "result" in response
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["status"] == "success"
        assert content["containment_status"] == "isolated"
        assert content["device_id"] == "WS-FIN-042"


# =============================================================================
# TEST 3: Data MCP Server Responds
# =============================================================================

class TestE2EMCPDataFromSoulInTheBot:
    """Test data MCP server connectivity and tools."""

    @pytest.mark.asyncio
    async def test_e2e_mcp_data_connects(self, data_mcp_client: MockMCPClient):
        """
        GIVEN SoulInTheBot wants to connect to Data MCP server
        WHEN connection is established
        THEN the client should be connected
        """
        result = await data_mcp_client.connect()
        assert result is True
        assert data_mcp_client.connected is True

    @pytest.mark.asyncio
    async def test_e2e_mcp_data_lists_tools(self, data_mcp_client: MockMCPClient):
        """
        GIVEN Data MCP server is connected
        WHEN tools/list is requested
        THEN it should return data generation tools
        """
        await data_mcp_client.connect()

        response = await data_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        })

        assert "result" in response
        tools = response["result"]["tools"]
        tool_names = {t["name"] for t in tools}

        assert "data_generate_assets" in tool_names
        assert "data_generate_edr_detections" in tool_names
        assert "data_generate_siem_incidents" in tool_names
        assert "data_generate_all" in tool_names
        assert "data_reset" in tool_names

    @pytest.mark.asyncio
    async def test_e2e_mcp_data_generate_all(self, data_mcp_client: MockMCPClient):
        """
        GIVEN Data MCP server is connected
        WHEN data_generate_all tool is invoked
        THEN all synthetic data should be generated
        """
        await data_mcp_client.connect()

        response = await data_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "data_generate_all",
                "arguments": {}
            }
        })

        assert "result" in response
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["status"] == "success"
        assert "summary" in content
        assert content["summary"]["assets"] > 0
        assert content["summary"]["detections"] > 0
        assert content["summary"]["incidents"] > 0


# =============================================================================
# TEST 4: Full Investigation Flow via MCP
# =============================================================================

class TestE2EFullInvestigationFlowViaMCP:
    """Test complete investigation workflow using MCP tools."""

    @pytest.mark.asyncio
    async def test_e2e_full_investigation_flow_via_mcp(self, backend_mcp_client: MockMCPClient):
        """
        GIVEN SoulInTheBot receives an incident alert
        WHEN it performs full investigation via MCP tools
        THEN investigation should complete with proper artifacts

        Investigation flow:
        1. Get incident from SIEM
        2. Get threat intel for file hash
        3. Get CTEM risk for asset
        4. Contain host via EDR
        5. Create ticket
        6. Generate postmortem
        """
        await backend_mcp_client.connect()

        # Step 1: Get incident from SIEM
        incident_response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "siem_get_incident",
                "arguments": {"incident_id": "INC-ANCHOR-001"}
            }
        })

        incident = json.loads(incident_response["result"]["content"][0]["text"])
        assert incident["status"] == "success"
        incident_id = incident["incident"]["id"]
        device_id = incident["incident"]["asset"]["device_id"]

        # Step 2: Get threat intel
        intel_response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "intel_get_indicator",
                "arguments": {
                    "indicator_type": "filehash",
                    "value": "a1b2c3d4e5f6789012345678901234567890abcdef"
                }
            }
        })

        intel = json.loads(intel_response["result"]["content"][0]["text"])
        assert intel["status"] == "success"
        assert intel["indicator"]["verdict"] == "malicious"

        # Step 3: Get CTEM risk
        ctem_response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "ctem_get_asset_risk",
                "arguments": {"asset_id": device_id}
            }
        })

        ctem = json.loads(ctem_response["result"]["content"][0]["text"])
        assert ctem["status"] == "success"

        # Step 4: Contain host
        contain_response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "edr_contain_host",
                "arguments": {
                    "device_id": device_id,
                    "reason": "Malicious file detected with high confidence"
                }
            }
        })

        contain = json.loads(contain_response["result"]["content"][0]["text"])
        assert contain["status"] == "success"
        assert contain["containment_status"] == "isolated"

        # Step 5: Create ticket
        ticket_response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "tickets_create",
                "arguments": {
                    "title": f"Security Incident: {incident_id}",
                    "description": "Auto-containment executed for malware detection"
                }
            }
        })

        ticket = json.loads(ticket_response["result"]["content"][0]["text"])
        assert ticket["status"] == "success"
        assert ticket["ticket_id"].startswith("TKT-")

        # Step 6: Generate postmortem
        postmortem_response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "reports_generate_postmortem",
                "arguments": {"incident_id": incident_id}
            }
        })

        postmortem = json.loads(postmortem_response["result"]["content"][0]["text"])
        assert postmortem["status"] == "success"
        assert postmortem["postmortem_id"].startswith("PM-")
        assert postmortem["generated"] is True


# =============================================================================
# TEST 5: Demo Scenario Execution via MCP
# =============================================================================

class TestE2EDemoScenarioViaMCP:
    """Test demo scenario execution using MCP tools."""

    @pytest.mark.asyncio
    async def test_e2e_demo_scenario_auto_containment_via_mcp(
        self,
        backend_mcp_client: MockMCPClient,
        data_mcp_client: MockMCPClient,
        frontend_mcp_client: MockMCPClient
    ):
        """
        GIVEN Demo Scenario 1: Auto-Containment
        WHEN executed via MCP tools from SoulInTheBot
        THEN standard workstation with malware should be auto-contained

        Scenario:
        - Asset: WS-FIN-042 (standard-user, finance)
        - Intel: Malicious QakBot hash with 58/72 VT detections
        - Expected: Auto-contain, create ticket, generate postmortem
        """
        # Connect all MCP servers
        await backend_mcp_client.connect()
        await data_mcp_client.connect()
        await frontend_mcp_client.connect()

        # Phase 1: Generate demo data
        data_response = await data_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "data_generate_all", "arguments": {}}
        })
        assert json.loads(data_response["result"]["content"][0]["text"])["status"] == "success"

        # Phase 2: Update UI with scenario start
        ui_response = await frontend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "ui_show_alert",
                "arguments": {"message": "Demo Scenario 1: Auto-Containment started"}
            }
        })
        assert json.loads(ui_response["result"]["content"][0]["text"])["displayed"] is True

        # Phase 3: Get incident and perform investigation
        incident_response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "siem_get_incident",
                "arguments": {"incident_id": "INC-ANCHOR-001"}
            }
        })
        incident = json.loads(incident_response["result"]["content"][0]["text"])
        assert incident["status"] == "success"

        # Phase 4: Get intel (high confidence malware)
        intel_response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "intel_get_indicator",
                "arguments": {
                    "indicator_type": "filehash",
                    "value": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
                }
            }
        })
        intel = json.loads(intel_response["result"]["content"][0]["text"])
        assert intel["indicator"]["verdict"] == "malicious"
        assert intel["indicator"]["confidence"] >= 90

        # Phase 5: Auto-contain (standard asset + high confidence = auto-contain)
        contain_response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "edr_contain_host",
                "arguments": {
                    "device_id": "WS-FIN-042",
                    "reason": "Auto-containment: QakBot malware detected (95% confidence)"
                }
            }
        })
        contain = json.loads(contain_response["result"]["content"][0]["text"])
        assert contain["status"] == "success"
        assert contain["containment_status"] == "isolated"

        # Phase 6: Create ticket
        ticket_response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "tickets_create",
                "arguments": {
                    "title": "Auto-Containment: INC-ANCHOR-001",
                    "description": "WS-FIN-042 isolated due to QakBot detection",
                    "incident_id": "INC-ANCHOR-001"
                }
            }
        })
        ticket = json.loads(ticket_response["result"]["content"][0]["text"])
        assert ticket["status"] == "success"

        # Phase 7: Generate postmortem
        postmortem_response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "reports_generate_postmortem",
                "arguments": {"incident_id": "INC-ANCHOR-001"}
            }
        })
        postmortem = json.loads(postmortem_response["result"]["content"][0]["text"])
        assert postmortem["status"] == "success"

        # Phase 8: Update UI with completion
        timeline_response = await frontend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "ui_show_timeline",
                "arguments": {
                    "events": [
                        {"action": "incident_received", "timestamp": "2024-01-15T10:00:00Z"},
                        {"action": "intel_enrichment", "timestamp": "2024-01-15T10:00:05Z"},
                        {"action": "ctem_enrichment", "timestamp": "2024-01-15T10:00:10Z"},
                        {"action": "auto_containment", "timestamp": "2024-01-15T10:00:15Z"},
                        {"action": "ticket_created", "timestamp": "2024-01-15T10:00:20Z"},
                        {"action": "postmortem_generated", "timestamp": "2024-01-15T10:00:25Z"},
                    ]
                }
            }
        })
        timeline = json.loads(timeline_response["result"]["content"][0]["text"])
        assert timeline["status"] == "success"
        assert timeline["event_count"] == 6

    @pytest.mark.asyncio
    async def test_e2e_demo_scenario_vip_approval_via_mcp(self, backend_mcp_client: MockMCPClient):
        """
        GIVEN Demo Scenario 2: VIP Human-in-the-Loop
        WHEN executed via MCP tools from SoulInTheBot
        THEN VIP device should request approval before containment

        Scenario:
        - Asset: LAPTOP-CFO-01 (VIP, executive)
        - Intel: Same malicious hash
        - Expected: Request approval (VIP override policy)
        """
        await backend_mcp_client.connect()

        # Get incident
        incident_response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "siem_get_incident",
                "arguments": {"incident_id": "INC-ANCHOR-002"}
            }
        })
        incident = json.loads(incident_response["result"]["content"][0]["text"])
        assert incident["status"] == "success"

        # For VIP device, request approval instead of auto-contain
        approval_response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "approvals_request",
                "arguments": {
                    "incident_id": "INC-ANCHOR-002",
                    "action": "contain",
                    "reason": "VIP device - requires human approval"
                }
            }
        })

        approval = json.loads(approval_response["result"]["content"][0]["text"])
        assert approval["status"] == "success"
        assert approval["approval_id"].startswith("APR-")
        assert approval["state"] == "pending"


# =============================================================================
# Test Error Handling
# =============================================================================

class TestE2EMCPErrorHandling:
    """Test MCP error handling scenarios."""

    @pytest.mark.asyncio
    async def test_e2e_mcp_unknown_tool_error(self, backend_mcp_client: MockMCPClient):
        """
        GIVEN Backend MCP server is connected
        WHEN unknown tool is invoked
        THEN error should be returned
        """
        await backend_mcp_client.connect()

        response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "unknown_tool",
                "arguments": {}
            }
        })

        assert "error" in response
        assert response["error"]["code"] == -32601

    @pytest.mark.asyncio
    async def test_e2e_mcp_not_connected_error(self, backend_mcp_client: MockMCPClient):
        """
        GIVEN Backend MCP server is NOT connected
        WHEN tool is invoked
        THEN connection error should be returned
        """
        # Don't connect

        response = await backend_mcp_client.send_message({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "siem_list_incidents",
                "arguments": {}
            }
        })

        assert "error" in response
        assert response["error"]["code"] == -32000
        assert "Not connected" in response["error"]["message"]
