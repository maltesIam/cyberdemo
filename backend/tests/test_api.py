"""API endpoint tests."""
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app


@pytest.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test /health endpoint returns 200."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


@pytest.mark.asyncio
async def test_list_incidents(client):
    """Test GET /siem/incidents returns list."""
    response = await client.get("/siem/incidents")
    assert response.status_code == 200
    data = response.json()
    assert "incidents" in data or "total" in data


@pytest.mark.asyncio
async def test_list_detections(client):
    """Test GET /edr/detections returns list."""
    response = await client.get("/edr/detections")
    assert response.status_code == 200
    data = response.json()
    assert "detections" in data or "total" in data


@pytest.mark.asyncio
async def test_list_assets(client):
    """Test GET /assets returns list."""
    response = await client.get("/assets")
    assert response.status_code == 200
    data = response.json()
    assert "assets" in data or "total" in data


@pytest.mark.asyncio
async def test_get_indicator_unknown(client):
    """Test GET /intel/indicators for unknown indicator."""
    response = await client.get("/intel/indicators/filehash/unknown_hash_123")
    # Accept 200 (OpenSearch available) or 500 (OpenSearch unavailable during tests)
    if response.status_code == 200:
        data = response.json()
        assert data["verdict"] == "unknown"
    else:
        # OpenSearch not available, skip validation
        assert response.status_code == 500


@pytest.mark.asyncio
async def test_gen_health(client):
    """Test GET /gen/health returns index counts."""
    response = await client.get("/gen/health")
    assert response.status_code == 200
    data = response.json()
    assert "indices" in data or "counts" in data or "status" in data
