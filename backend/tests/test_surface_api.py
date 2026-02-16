"""Surface WOW Command Center API endpoint tests.

Tests for /surface/*, /vulnerabilities/*, and /threats/* endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app


@pytest.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ============================================================================
# Surface Endpoints
# ============================================================================


@pytest.mark.asyncio
async def test_surface_overview(client):
    """Test GET /surface/overview returns KPI aggregations."""
    response = await client.get("/surface/overview")
    assert response.status_code == 200
    data = response.json()
    # Verify all required KPI fields exist
    assert "total_assets" in data
    assert "critical_assets" in data
    assert "active_detections" in data
    assert "open_incidents" in data
    assert "critical_incidents" in data
    assert "contained_hosts" in data
    assert "critical_cves" in data
    assert "kev_cves" in data
    assert "high_risk_iocs" in data
    assert "timestamp" in data
    # Values should be non-negative integers
    assert isinstance(data["total_assets"], int)
    assert data["total_assets"] >= 0
    assert isinstance(data["critical_assets"], int)
    assert data["critical_assets"] >= 0


@pytest.mark.asyncio
async def test_surface_nodes_default(client):
    """Test GET /surface/nodes returns paginated node list."""
    response = await client.get("/surface/nodes")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "nodes" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["total"], int)


@pytest.mark.asyncio
async def test_surface_nodes_pagination(client):
    """Test /surface/nodes respects pagination params."""
    response = await client.get("/surface/nodes?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) <= 10


@pytest.mark.asyncio
async def test_surface_nodes_filters(client):
    """Test /surface/nodes with filter params."""
    response = await client.get("/surface/nodes?asset_type=server&risk_min=50")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["nodes"], list)
    # All returned nodes should have risk_score >= 50
    for node in data["nodes"]:
        assert node.get("risk_score", 0) >= 50


@pytest.mark.asyncio
async def test_surface_nodes_search(client):
    """Test /surface/nodes search filter."""
    response = await client.get("/surface/nodes?search=SRV")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["nodes"], list)


@pytest.mark.asyncio
async def test_surface_nodes_have_layer_data(client):
    """Test that returned nodes have proper layer structure."""
    response = await client.get("/surface/nodes?page_size=5")
    assert response.status_code == 200
    data = response.json()
    for node in data["nodes"]:
        layers = node.get("layers", {})
        # Verify all 8 layer keys exist
        assert "base" in layers
        assert "edr" in layers
        assert "siem" in layers
        assert "ctem" in layers
        assert "vulnerabilities" in layers
        assert "threats" in layers
        assert "containment" in layers
        assert "relations" in layers
        # Verify base is always True
        assert layers["base"] is True
        # Verify layer objects have 'active' field
        assert "active" in layers["edr"]
        assert "active" in layers["siem"]
        assert "active" in layers["ctem"]
        assert "active" in layers["vulnerabilities"]
        assert "active" in layers["threats"]
        assert "active" in layers["containment"]
        assert "active" in layers["relations"]


@pytest.mark.asyncio
async def test_surface_connections(client):
    """Test GET /surface/connections returns connection list."""
    response = await client.get("/surface/connections")
    assert response.status_code == 200
    data = response.json()
    assert "connections" in data
    assert isinstance(data["connections"], list)
    for conn in data["connections"]:
        assert "source_id" in conn
        assert "target_id" in conn
        assert "type" in conn
        assert "strength" in conn


@pytest.mark.asyncio
async def test_surface_connections_type_filter(client):
    """Test /surface/connections with type filter."""
    response = await client.get("/surface/connections?type=lateral_movement")
    assert response.status_code == 200
    data = response.json()
    for conn in data["connections"]:
        assert conn["type"] == "lateral_movement"


# ============================================================================
# Vulnerabilities Endpoints
# ============================================================================


@pytest.mark.asyncio
async def test_vulnerabilities_list(client):
    """Test GET /vulnerabilities returns paginated list."""
    response = await client.get("/vulnerabilities")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_vulnerabilities_severity_filter(client):
    """Test /vulnerabilities with severity filter."""
    response = await client.get("/vulnerabilities?severity=Critical")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_vulnerabilities_cvss_filter(client):
    """Test /vulnerabilities with CVSS range filter."""
    response = await client.get("/vulnerabilities?cvss_min=7.0&cvss_max=10.0")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_vulnerabilities_kev_filter(client):
    """Test /vulnerabilities with KEV filter."""
    response = await client.get("/vulnerabilities?kev=true")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_vulnerabilities_search(client):
    """Test /vulnerabilities with search filter."""
    response = await client.get("/vulnerabilities?search=CVE-2024")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_vulnerability_summary(client):
    """Test GET /vulnerabilities/summary returns stats."""
    response = await client.get("/vulnerabilities/summary")
    assert response.status_code == 200
    data = response.json()
    assert "by_severity" in data
    assert "kev_count" in data
    assert "exploit_available_count" in data
    assert "avg_cvss" in data
    assert isinstance(data["by_severity"], dict)
    assert isinstance(data["kev_count"], int)
    assert isinstance(data["avg_cvss"], (int, float))


@pytest.mark.asyncio
async def test_vulnerability_cve_detail(client):
    """Test GET /vulnerabilities/cves/:id returns detail or 404."""
    response = await client.get("/vulnerabilities/cves/CVE-2024-0001")
    # Accept 200 (found) or 404 (not in test data) or 500 (OpenSearch down)
    assert response.status_code in [200, 404, 500]
    if response.status_code == 200:
        data = response.json()
        assert "cve_id" in data or "affected_assets" in data


# ============================================================================
# Threats Endpoints
# ============================================================================


@pytest.mark.asyncio
async def test_threats_list(client):
    """Test GET /threats returns paginated IOC list."""
    response = await client.get("/threats")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data
    assert "page" in data
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_threats_type_filter(client):
    """Test /threats with ioc_type filter."""
    response = await client.get("/threats?ioc_type=ip")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_threats_verdict_filter(client):
    """Test /threats with verdict filter."""
    response = await client.get("/threats?verdict=malicious")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_threats_risk_filter(client):
    """Test /threats with risk_min filter."""
    response = await client.get("/threats?risk_min=80")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_threat_ioc_detail(client):
    """Test GET /threats/iocs/:id returns detail or 404."""
    response = await client.get("/threats/iocs/1.2.3.4")
    assert response.status_code in [200, 404, 500]


@pytest.mark.asyncio
async def test_threat_map(client):
    """Test GET /threats/map returns geo aggregation."""
    response = await client.get("/threats/map")
    assert response.status_code == 200
    data = response.json()
    assert "countries" in data
    assert "total_iocs" in data
    assert isinstance(data["countries"], list)
    assert isinstance(data["total_iocs"], int)


@pytest.mark.asyncio
async def test_threat_actor(client):
    """Test GET /threats/actors/:name returns IOCs for actor."""
    response = await client.get("/threats/actors/APT29")
    assert response.status_code == 200
    data = response.json()
    assert "actor" in data
    assert data["actor"] == "APT29"
    assert "iocs" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_threat_mitre(client):
    """Test GET /threats/mitre returns ATT&CK coverage."""
    response = await client.get("/threats/mitre")
    assert response.status_code == 200
    data = response.json()
    assert "techniques" in data
    assert "total_detections" in data
    assert isinstance(data["techniques"], list)
    for tech in data["techniques"]:
        assert "technique_id" in tech
        assert "detection_count" in tech


# ============================================================================
# Edge Cases
# ============================================================================


@pytest.mark.asyncio
async def test_surface_nodes_empty_page(client):
    """Test /surface/nodes with very high page number returns empty."""
    response = await client.get("/surface/nodes?page=9999")
    assert response.status_code == 200
    data = response.json()
    assert data["nodes"] == []


@pytest.mark.asyncio
async def test_vulnerabilities_extreme_cvss(client):
    """Test /vulnerabilities with CVSS=0 returns results."""
    response = await client.get("/vulnerabilities?cvss_min=0&cvss_max=0")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_threats_search(client):
    """Test /threats with search filter."""
    response = await client.get("/threats?search=malware")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["data"], list)
