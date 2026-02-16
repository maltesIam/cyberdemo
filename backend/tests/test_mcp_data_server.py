"""
MCP Data Server Tests - TDD RED Phase

Tests the MCP Data Server that handles synthetic data generation operations.

Port: 8002
Endpoint: /data-mcp/messages

Tools:
- data_generate_assets
- data_generate_edr_detections
- data_generate_siem_incidents
- data_generate_threat_intel
- data_generate_ctem_findings
- data_generate_all
- data_reset
- data_get_health
"""

import pytest
from httpx import AsyncClient
import json


# =============================================================================
# TEST 1: MCP Data Server Health Check
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_data_server_health(client: AsyncClient):
    """
    GIVEN the MCP Data Server is running
    WHEN a health check is requested
    THEN it should return healthy status with data tools info
    """
    response = await client.get("/data-mcp/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["protocol"] == "MCP-Data"
    assert "tools_count" in data
    assert data["tools_count"] >= 8  # At least 8 data generation tools


# =============================================================================
# TEST 2: List Available Data Tools
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_data_server_lists_tools(client: AsyncClient):
    """
    GIVEN the MCP Data Server connection
    WHEN tools/list is requested
    THEN it should return all data generation tools
    """
    message = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }

    response = await client.post("/data-mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "tools" in data["result"]

    # Verify expected tools exist
    tool_names = {t["name"] for t in data["result"]["tools"]}
    expected_tools = {
        "data_generate_assets",
        "data_generate_edr_detections",
        "data_generate_siem_incidents",
        "data_generate_threat_intel",
        "data_generate_ctem_findings",
        "data_generate_all",
        "data_reset",
        "data_get_health",
    }

    for tool_name in expected_tools:
        assert tool_name in tool_names, f"Missing tool: {tool_name}"


# =============================================================================
# TEST 3: Generate Assets Tool
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_data_generate_assets(client: AsyncClient):
    """
    GIVEN the data_generate_assets tool
    WHEN invoked with count parameter
    THEN it should generate the specified number of assets
    """
    message = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "data_generate_assets",
            "arguments": {"count": 10, "seed": 42}
        }
    }

    response = await client.post("/data-mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "content" in data["result"]

    content = json.loads(data["result"]["content"][0]["text"])
    assert content["status"] == "success"
    assert content["count"] == 10
    assert "assets" in content


# =============================================================================
# TEST 4: Generate EDR Detections Tool
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_data_generate_edr_detections(client: AsyncClient):
    """
    GIVEN the data_generate_edr_detections tool
    WHEN invoked with count parameter
    THEN it should generate the specified number of detections
    """
    message = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "data_generate_edr_detections",
            "arguments": {"count": 5, "seed": 42}
        }
    }

    response = await client.post("/data-mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data

    content = json.loads(data["result"]["content"][0]["text"])
    assert content["status"] == "success"
    assert content["count"] == 5


# =============================================================================
# TEST 5: Generate SIEM Incidents Tool
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_data_generate_siem_incidents(client: AsyncClient):
    """
    GIVEN the data_generate_siem_incidents tool
    WHEN invoked
    THEN it should generate SIEM incidents
    """
    message = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "data_generate_siem_incidents",
            "arguments": {"seed": 42}
        }
    }

    response = await client.post("/data-mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data

    content = json.loads(data["result"]["content"][0]["text"])
    assert content["status"] == "success"
    assert "count" in content


# =============================================================================
# TEST 6: Generate Threat Intel Tool
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_data_generate_threat_intel(client: AsyncClient):
    """
    GIVEN the data_generate_threat_intel tool
    WHEN invoked with count parameter
    THEN it should generate threat intelligence IOCs
    """
    message = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "data_generate_threat_intel",
            "arguments": {"count": 20, "seed": 42}
        }
    }

    response = await client.post("/data-mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data

    content = json.loads(data["result"]["content"][0]["text"])
    assert content["status"] == "success"
    assert content["count"] == 20


# =============================================================================
# TEST 7: Generate CTEM Findings Tool
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_data_generate_ctem_findings(client: AsyncClient):
    """
    GIVEN the data_generate_ctem_findings tool
    WHEN invoked
    THEN it should generate CTEM vulnerability findings
    """
    message = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "data_generate_ctem_findings",
            "arguments": {"seed": 42}
        }
    }

    response = await client.post("/data-mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data

    content = json.loads(data["result"]["content"][0]["text"])
    assert content["status"] == "success"
    assert "findings_count" in content


# =============================================================================
# TEST 8: Generate All Data Tool
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_data_generate_all(client: AsyncClient):
    """
    GIVEN the data_generate_all tool
    WHEN invoked
    THEN it should generate all data types with proper cross-references
    """
    message = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "data_generate_all",
            "arguments": {
                "asset_count": 10,
                "detection_count": 5,
                "intel_count": 10,
                "seed": 42
            }
        }
    }

    response = await client.post("/data-mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data

    content = json.loads(data["result"]["content"][0]["text"])
    assert content["status"] == "success"
    assert "summary" in content
    summary = content["summary"]
    assert "assets" in summary
    assert "detections" in summary
    assert "incidents" in summary
    assert "intel" in summary


# =============================================================================
# TEST 9: Data Reset Tool
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_data_reset(client: AsyncClient):
    """
    GIVEN generated data exists
    WHEN data_reset is invoked
    THEN it should clear all generated data
    """
    message = {
        "jsonrpc": "2.0",
        "id": 8,
        "method": "tools/call",
        "params": {
            "name": "data_reset",
            "arguments": {}
        }
    }

    response = await client.post("/data-mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data

    content = json.loads(data["result"]["content"][0]["text"])
    assert content["status"] == "success"
    assert content["message"] == "All generated data has been cleared"


# =============================================================================
# TEST 10: Data Get Health Tool
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_data_get_health(client: AsyncClient):
    """
    GIVEN the data server is running
    WHEN data_get_health is invoked
    THEN it should return current data generation status
    """
    message = {
        "jsonrpc": "2.0",
        "id": 9,
        "method": "tools/call",
        "params": {
            "name": "data_get_health",
            "arguments": {}
        }
    }

    response = await client.post("/data-mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data

    content = json.loads(data["result"]["content"][0]["text"])
    assert "status" in content
    assert "data_counts" in content


# =============================================================================
# TEST 11: Unknown Tool Returns Error
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_data_unknown_tool_returns_error(client: AsyncClient):
    """
    GIVEN a non-existent tool name
    WHEN invoked
    THEN it should return a JSON-RPC error
    """
    message = {
        "jsonrpc": "2.0",
        "id": 10,
        "method": "tools/call",
        "params": {
            "name": "unknown_data_tool",
            "arguments": {}
        }
    }

    response = await client.post("/data-mcp/messages", json=message)

    data = response.json()
    assert "error" in data


# =============================================================================
# TEST 12: Invalid Method Returns Error
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_data_invalid_method_returns_error(client: AsyncClient):
    """
    GIVEN an invalid JSON-RPC method
    WHEN sent to the server
    THEN it should return a method not found error
    """
    message = {
        "jsonrpc": "2.0",
        "id": 11,
        "method": "invalid/method"
    }

    response = await client.post("/data-mcp/messages", json=message)

    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == -32601  # Method not found


# =============================================================================
# Unit Tests: Tool Schema Validation
# =============================================================================
class TestMCPDataToolSchemas:
    """Unit tests for MCP Data Server tool schemas."""

    def test_all_data_tools_have_required_fields(self):
        """Data tools must have name, description, and inputSchema."""
        from src.mcp.data_tools import get_all_data_tools

        tools = get_all_data_tools()

        for tool in tools:
            assert "name" in tool, f"Tool missing name: {tool}"
            assert "description" in tool, f"Tool {tool['name']} missing description"
            assert "inputSchema" in tool, f"Tool {tool['name']} missing inputSchema"

    def test_all_expected_data_tools_registered(self):
        """All expected data generation tools should be registered."""
        from src.mcp.data_tools import get_all_data_tools

        tools = get_all_data_tools()
        tool_names = {t["name"] for t in tools}

        expected_tools = {
            "data_generate_assets",
            "data_generate_edr_detections",
            "data_generate_siem_incidents",
            "data_generate_threat_intel",
            "data_generate_ctem_findings",
            "data_generate_all",
            "data_reset",
            "data_get_health",
        }

        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Missing data tool: {tool_name}"

    def test_data_handlers_exist_for_all_tools(self):
        """Each tool should have a corresponding handler."""
        from src.mcp.data_tools import get_all_data_tools, get_data_tool_handlers

        tools = get_all_data_tools()
        handlers = get_data_tool_handlers()

        for tool in tools:
            tool_name = tool["name"]
            assert tool_name in handlers, f"Missing handler for tool: {tool_name}"
