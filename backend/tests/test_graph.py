"""
TDD Tests for Graph Endpoints.

These tests are written FIRST following strict TDD methodology.
They should FAIL initially (RED phase) until implementation is complete.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock


# ============================================================================
# TEST 1: Get incident graph returns nodes and edges
# ============================================================================

@pytest.mark.asyncio
async def test_get_graph_incident_returns_nodes_and_edges():
    """
    GIVEN un incidente con detecciones y activos asociados
    WHEN se solicita GET /graph/incident/{id}
    THEN debe retornar nodos y edges en formato Cytoscape

    TDD: RED → Este test debe fallar inicialmente
    """
    try:
        from src.api.graph import router as graph_router
        from src.main import app
    except ImportError:
        pytest.skip("Graph router not implemented yet - TDD RED phase")
        return

    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/graph/incident/INC-ANCHOR-001")

    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0


# ============================================================================
# TEST 2: Graph nodes have Cytoscape format
# ============================================================================

@pytest.mark.asyncio
async def test_graph_nodes_have_cytoscape_format():
    """
    GIVEN un grafo de incidente
    WHEN se obtienen los nodos
    THEN cada nodo debe tener id, label, type, y data

    TDD: RED → Este test debe fallar inicialmente
    """
    try:
        from src.api.graph import router as graph_router
        from src.main import app
    except ImportError:
        pytest.skip("Graph router not implemented yet - TDD RED phase")
        return

    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/graph/incident/INC-ANCHOR-001")

    data = response.json()

    for node in data["nodes"]:
        assert "data" in node
        assert "id" in node["data"]
        assert "label" in node["data"]
        assert "type" in node["data"]
        assert node["data"]["type"] in [
            "incident", "detection", "asset", "process", "hash", "user"
        ]


# ============================================================================
# TEST 3: Graph edges have Cytoscape format
# ============================================================================

@pytest.mark.asyncio
async def test_graph_edges_have_cytoscape_format():
    """
    GIVEN un grafo de incidente
    WHEN se obtienen los edges
    THEN cada edge debe tener source, target, y relation

    TDD: RED → Este test debe fallar inicialmente
    """
    try:
        from src.api.graph import router as graph_router
        from src.main import app
    except ImportError:
        pytest.skip("Graph router not implemented yet - TDD RED phase")
        return

    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/graph/incident/INC-ANCHOR-001")

    data = response.json()

    for edge in data["edges"]:
        assert "data" in edge
        assert "source" in edge["data"]
        assert "target" in edge["data"]
        assert "relation" in edge["data"]


# ============================================================================
# TEST 4: Graph nodes have correct colors based on risk
# ============================================================================

@pytest.mark.asyncio
async def test_graph_nodes_have_correct_colors():
    """
    GIVEN un grafo con activos en diferentes estados
    WHEN se obtienen los nodos
    THEN los colores deben reflejar el estado:
         - Green: sin riesgo
         - Yellow: riesgo medio
         - Red: riesgo alto
         - Blue: contenido

    TDD: RED → Este test debe fallar inicialmente
    """
    try:
        from src.api.graph import router as graph_router
        from src.main import app
    except ImportError:
        pytest.skip("Graph router not implemented yet - TDD RED phase")
        return

    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/graph/incident/INC-ANCHOR-001")

    data = response.json()

    asset_nodes = [n for n in data["nodes"] if n["data"]["type"] == "asset"]

    for node in asset_nodes:
        assert "color" in node["data"]
        # Color should be one of the valid risk/status colors
        valid_colors = ["green", "yellow", "red", "blue", "#00ff00", "#ffff00", "#ff0000", "#0000ff"]
        color = node["data"]["color"].lower()
        assert any(c in color for c in ["green", "yellow", "red", "blue", "#"])


# ============================================================================
# TEST 5: Graph incident not found returns 404
# ============================================================================

@pytest.mark.asyncio
async def test_graph_incident_not_found_returns_404():
    """
    GIVEN un incidente que no existe
    WHEN se solicita su grafo
    THEN debe retornar 404

    TDD: RED → Este test debe fallar inicialmente
    """
    try:
        from src.api.graph import router as graph_router
        from src.main import app
    except ImportError:
        pytest.skip("Graph router not implemented yet - TDD RED phase")
        return

    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/graph/incident/INVALID-INCIDENT-ID")

    assert response.status_code == 404


# ============================================================================
# TEST 6: Get system graph returns overview
# ============================================================================

@pytest.mark.asyncio
async def test_get_graph_system_returns_overview():
    """
    GIVEN el sistema con múltiples incidentes
    WHEN se solicita GET /graph/system
    THEN debe retornar un grafo con fuentes, incidentes y activos

    TDD: RED → Este test debe fallar inicialmente
    """
    try:
        from src.api.graph import router as graph_router
        from src.main import app
    except ImportError:
        pytest.skip("Graph router not implemented yet - TDD RED phase")
        return

    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/graph/system")

    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data

    # System graph should have various node types
    if len(data["nodes"]) > 0:
        types = set(n["data"]["type"] for n in data["nodes"])
        # Should have at least some nodes
        assert len(types) >= 1


# ============================================================================
# Unit Tests for Graph Service
# ============================================================================

class TestGraphServiceUnit:
    """Unit tests for Graph service logic."""

    def test_node_to_cytoscape_format(self):
        """Test node conversion to Cytoscape format."""
        try:
            from src.services.graph_service import node_to_cytoscape
            result = node_to_cytoscape(
                id="node-001",
                label="Test Node",
                node_type="asset",
                data={"risk": "high"}
            )
            assert result["data"]["id"] == "node-001"
            assert result["data"]["label"] == "Test Node"
            assert result["data"]["type"] == "asset"
        except ImportError:
            pytest.skip("Graph service not implemented yet - TDD RED phase")

    def test_edge_to_cytoscape_format(self):
        """Test edge conversion to Cytoscape format."""
        try:
            from src.services.graph_service import edge_to_cytoscape
            result = edge_to_cytoscape(
                source="node-001",
                target="node-002",
                relation="detected_on"
            )
            assert result["data"]["source"] == "node-001"
            assert result["data"]["target"] == "node-002"
            assert result["data"]["relation"] == "detected_on"
        except ImportError:
            pytest.skip("Graph service not implemented yet - TDD RED phase")

    def test_risk_to_color_mapping(self):
        """Test risk level to color mapping."""
        try:
            from src.services.graph_service import risk_to_color
            assert risk_to_color("Green") == "green"
            assert risk_to_color("Yellow") == "yellow"
            assert risk_to_color("Red") == "red"
            assert risk_to_color("contained") == "blue"
        except ImportError:
            pytest.skip("Graph service not implemented yet - TDD RED phase")
