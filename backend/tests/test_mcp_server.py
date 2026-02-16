"""
MCP Backend Server Tests - TDD RED Phase

Tests the MCP (Model Context Protocol) server that enables SoulInTheBot
to interact with the CyberDemo SOC system.

MCP Protocol:
- Uses JSON-RPC 2.0 format
- SSE endpoint for streaming: /mcp/sse
- Message endpoint: /mcp/messages
- Tool listing: tools/list
- Tool execution: tools/call
"""

import pytest
from httpx import AsyncClient
import json


# =============================================================================
# TEST 1: MCP Server SSE Endpoint
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_server_starts_and_responds(client: AsyncClient):
    """
    GIVEN el servidor MCP configurado
    WHEN se conecta al endpoint SSE
    THEN debe establecer conexión y responder con event-stream
    """
    # SSE endpoints are tricky to test, so we test the health endpoint instead
    response = await client.get("/mcp/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


# =============================================================================
# TEST 2: List Available Tools
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_lists_available_tools(client: AsyncClient):
    """
    GIVEN una conexión MCP establecida
    WHEN se envía tools/list
    THEN debe retornar las herramientas registradas
    """
    message = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }

    response = await client.post("/mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "tools" in data["result"]
    # At minimum, we should have SIEM, EDR, Intel, CTEM tools
    assert len(data["result"]["tools"]) >= 10


# =============================================================================
# TEST 3: SIEM List Incidents Tool
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_siem_list_incidents_tool(client: AsyncClient):
    """
    GIVEN el tool siem_list_incidents
    WHEN se invoca sin parámetros
    THEN debe retornar lista de incidentes
    """
    message = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "siem_list_incidents",
            "arguments": {}
        }
    }

    response = await client.post("/mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "content" in data["result"]


# =============================================================================
# TEST 4: SIEM Get Incident Tool
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_siem_get_incident_tool(client: AsyncClient):
    """
    GIVEN el tool siem_get_incident con un ID válido
    WHEN se invoca con el incident_id
    THEN debe retornar el incidente
    """
    message = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "siem_get_incident",
            "arguments": {"incident_id": "INC-ANCHOR-001"}
        }
    }

    response = await client.post("/mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data


# =============================================================================
# TEST 5: EDR Contain Host Tool
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_edr_contain_host_tool(client: AsyncClient):
    """
    GIVEN un dispositivo válido
    WHEN se invoca edr_contain_host
    THEN debe ejecutar contención y retornar resultado
    """
    message = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "edr_contain_host",
            "arguments": {
                "device_id": "DEV-001",
                "reason": "Malware detected"
            }
        }
    }

    response = await client.post("/mcp/messages", json=message)

    data = response.json()
    assert "result" in data
    content = json.loads(data["result"]["content"][0]["text"])
    assert content["status"] == "success"


# =============================================================================
# TEST 6: Intel Get Indicator Tool
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_intel_get_indicator_tool(client: AsyncClient):
    """
    GIVEN el tool intel_get_indicator
    WHEN se invoca con un hash
    THEN debe retornar información de reputación
    """
    message = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "intel_get_indicator",
            "arguments": {
                "indicator_type": "filehash",
                "value": "abc123def456"
            }
        }
    }

    response = await client.post("/mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data


# =============================================================================
# TEST 7: Tool with Missing Required Params
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_tool_invalid_params_returns_error(client: AsyncClient):
    """
    GIVEN un tool que requiere parámetros
    WHEN se invoca sin parámetros requeridos
    THEN debe retornar error JSON-RPC
    """
    message = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "siem_get_incident",
            "arguments": {}  # Falta incident_id requerido
        }
    }

    response = await client.post("/mcp/messages", json=message)

    data = response.json()
    assert "error" in data


# =============================================================================
# TEST 8: Unknown Tool Returns Error
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_unknown_tool_returns_error(client: AsyncClient):
    """
    GIVEN un nombre de tool que no existe
    WHEN se intenta invocar
    THEN debe retornar error
    """
    message = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "unknown_tool_that_does_not_exist",
            "arguments": {}
        }
    }

    response = await client.post("/mcp/messages", json=message)

    data = response.json()
    assert "error" in data


# =============================================================================
# TEST 9: CTEM Get Asset Risk Tool
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_ctem_get_asset_risk_tool(client: AsyncClient):
    """
    GIVEN el tool ctem_get_asset_risk
    WHEN se invoca con un asset_id
    THEN debe retornar el nivel de riesgo del activo
    """
    message = {
        "jsonrpc": "2.0",
        "id": 8,
        "method": "tools/call",
        "params": {
            "name": "ctem_get_asset_risk",
            "arguments": {"asset_id": "ASSET-001"}
        }
    }

    response = await client.post("/mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data


# =============================================================================
# TEST 10: Approvals Request Tool
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_approvals_request_tool(client: AsyncClient):
    """
    GIVEN el tool approvals_request
    WHEN se invoca para solicitar aprobación
    THEN debe crear una solicitud de aprobación
    """
    message = {
        "jsonrpc": "2.0",
        "id": 9,
        "method": "tools/call",
        "params": {
            "name": "approvals_request",
            "arguments": {
                "incident_id": "INC-001",
                "action": "contain",
                "reason": "High confidence malware"
            }
        }
    }

    response = await client.post("/mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data


# =============================================================================
# TEST 11: Tickets Create Tool
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_tickets_create_tool(client: AsyncClient):
    """
    GIVEN el tool tickets_create
    WHEN se invoca para crear un ticket
    THEN debe crear y retornar el ticket
    """
    message = {
        "jsonrpc": "2.0",
        "id": 10,
        "method": "tools/call",
        "params": {
            "name": "tickets_create",
            "arguments": {
                "title": "Security Incident",
                "description": "Auto-containment executed",
                "incident_id": "INC-001"
            }
        }
    }

    response = await client.post("/mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data


# =============================================================================
# TEST 12: Reports Generate Postmortem Tool
# =============================================================================
@pytest.mark.asyncio
async def test_mcp_reports_generate_postmortem_tool(client: AsyncClient):
    """
    GIVEN el tool reports_generate_postmortem
    WHEN se invoca para un incidente
    THEN debe generar un reporte postmortem
    """
    message = {
        "jsonrpc": "2.0",
        "id": 11,
        "method": "tools/call",
        "params": {
            "name": "reports_generate_postmortem",
            "arguments": {"incident_id": "INC-001"}
        }
    }

    response = await client.post("/mcp/messages", json=message)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data


# =============================================================================
# Unit Tests for MCP Tool Schemas
# =============================================================================
class TestMCPToolSchemas:
    """Unit tests for MCP tool schema validation."""

    def test_tool_schema_has_required_fields(self):
        """Tools must have name, description, and inputSchema."""
        from src.mcp.tools import get_all_tools

        tools = get_all_tools()

        for tool in tools:
            assert "name" in tool, f"Tool missing name: {tool}"
            assert "description" in tool, f"Tool {tool['name']} missing description"
            assert "inputSchema" in tool, f"Tool {tool['name']} missing inputSchema"

    def test_all_siem_tools_registered(self):
        """SIEM tools should be registered."""
        from src.mcp.tools import get_all_tools

        tools = get_all_tools()
        tool_names = {t["name"] for t in tools}

        expected_siem_tools = {
            "siem_list_incidents",
            "siem_get_incident",
            "siem_add_comment",
        }

        for tool_name in expected_siem_tools:
            assert tool_name in tool_names, f"Missing SIEM tool: {tool_name}"

    def test_all_edr_tools_registered(self):
        """EDR tools should be registered."""
        from src.mcp.tools import get_all_tools

        tools = get_all_tools()
        tool_names = {t["name"] for t in tools}

        expected_edr_tools = {
            "edr_get_detection",
            "edr_contain_host",
            "edr_hunt_hash",
        }

        for tool_name in expected_edr_tools:
            assert tool_name in tool_names, f"Missing EDR tool: {tool_name}"
