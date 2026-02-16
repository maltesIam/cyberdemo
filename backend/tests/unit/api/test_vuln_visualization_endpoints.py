"""
Unit tests for Vulnerability Visualization API endpoints.

Following TDD: Tests written FIRST for visualization endpoints.
Uses mocking for OpenSearch client to isolate API logic.

Endpoints covered:
- GET /api/vulnerabilities/overview - KPIs for Bottom Bar
- GET /api/vulnerabilities/terrain - Risk Terrain data
- GET /api/vulnerabilities/heatmap - Calendar Heatmap data
- GET /api/vulnerabilities/sunburst - CWE Sunburst data
- GET /api/vulnerabilities/bubbles - Priority Bubbles data
- GET /api/vulnerabilities/trends - Temporal trends
"""
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from src.main import app


# The path to patch - the module where get_opensearch_client is defined
OPENSEARCH_CLIENT_PATH = "src.opensearch.client.get_opensearch_client"


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def mock_opensearch_client():
    """Create a mock OpenSearch client."""
    client = AsyncMock()
    return client


@pytest.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_overview_aggregation_response():
    """Sample aggregation response for overview endpoint."""
    return {
        "hits": {"total": {"value": 150}},
        "aggregations": {
            "critical_count": {"doc_count": 25},
            "high_count": {"doc_count": 45},
            "kev_count": {"doc_count": 12},
            "avg_risk_score": {"value": 62.5},
            "act_count": {"doc_count": 10},
            "attend_count": {"doc_count": 35},
            "remediated_last_7d": {"doc_count": 8},
        }
    }


@pytest.fixture
def sample_terrain_aggregation_response():
    """Sample aggregation response for terrain endpoint."""
    return {
        "aggregations": {
            "by_severity": {
                "buckets": [
                    {
                        "key": "Critical",
                        "doc_count": 20,
                        "by_exploitation": {
                            "buckets": [
                                {"key": "active", "doc_count": 5, "avg_risk": {"value": 95.0}},
                                {"key": "poc", "doc_count": 10, "avg_risk": {"value": 80.0}},
                                {"key": "none", "doc_count": 5, "avg_risk": {"value": 60.0}},
                            ]
                        }
                    },
                    {
                        "key": "High",
                        "doc_count": 45,
                        "by_exploitation": {
                            "buckets": [
                                {"key": "active", "doc_count": 8, "avg_risk": {"value": 85.0}},
                                {"key": "poc", "doc_count": 20, "avg_risk": {"value": 70.0}},
                                {"key": "none", "doc_count": 17, "avg_risk": {"value": 50.0}},
                            ]
                        }
                    },
                ]
            }
        }
    }


@pytest.fixture
def sample_heatmap_aggregation_response():
    """Sample aggregation response for heatmap endpoint."""
    return {
        "aggregations": {
            "by_date": {
                "buckets": [
                    {
                        "key_as_string": "2024-01-15",
                        "doc_count": 12,
                        "max_severity": {"buckets": [{"key": "Critical", "doc_count": 3}]}
                    },
                    {
                        "key_as_string": "2024-01-16",
                        "doc_count": 8,
                        "max_severity": {"buckets": [{"key": "High", "doc_count": 5}]}
                    },
                    {
                        "key_as_string": "2024-01-17",
                        "doc_count": 5,
                        "max_severity": {"buckets": [{"key": "Medium", "doc_count": 4}]}
                    },
                ]
            }
        }
    }


@pytest.fixture
def sample_sunburst_aggregation_response():
    """Sample aggregation response for sunburst endpoint."""
    return {
        "aggregations": {
            "by_cwe_category": {
                "buckets": [
                    {
                        "key": "Injection",
                        "doc_count": 25,
                        "by_cwe": {
                            "buckets": [
                                {"key": "CWE-89", "doc_count": 15},
                                {"key": "CWE-78", "doc_count": 10},
                            ]
                        }
                    },
                    {
                        "key": "Buffer Errors",
                        "doc_count": 18,
                        "by_cwe": {
                            "buckets": [
                                {"key": "CWE-120", "doc_count": 12},
                                {"key": "CWE-119", "doc_count": 6},
                            ]
                        }
                    },
                ]
            }
        }
    }


@pytest.fixture
def sample_bubbles_response():
    """Sample search response for bubbles endpoint."""
    return {
        "hits": {
            "total": {"value": 50},
            "hits": [
                {
                    "_source": {
                        "cve_id": "CVE-2024-0001",
                        "risk_score": 95,
                        "severity": "Critical",
                        "title": "Critical RCE",
                    }
                },
                {
                    "_source": {
                        "cve_id": "CVE-2024-0002",
                        "risk_score": 85,
                        "severity": "High",
                        "title": "SQL Injection",
                    }
                },
                {
                    "_source": {
                        "cve_id": "CVE-2024-0003",
                        "risk_score": 60,
                        "severity": "Medium",
                        "title": "XSS Flaw",
                    }
                },
            ]
        }
    }


@pytest.fixture
def sample_trends_aggregation_response():
    """Sample aggregation response for trends endpoint."""
    return {
        "aggregations": {
            "by_date": {
                "buckets": [
                    {"key_as_string": "2024-01-01", "doc_count": 15},
                    {"key_as_string": "2024-01-08", "doc_count": 22},
                    {"key_as_string": "2024-01-15", "doc_count": 18},
                    {"key_as_string": "2024-01-22", "doc_count": 30},
                ]
            }
        }
    }


# ============================================================================
# Tests for GET /api/vulnerabilities/overview
# ============================================================================


class TestVulnerabilitiesOverview:
    """Tests for the vulnerabilities overview KPIs endpoint."""

    @pytest.mark.asyncio
    async def test_overview_returns_total_cves(
        self, client, mock_opensearch_client, sample_overview_aggregation_response
    ):
        """Test that overview returns total CVE count."""
        mock_opensearch_client.search.return_value = sample_overview_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/overview")

        assert response.status_code == 200
        data = response.json()
        assert "total_cves" in data
        assert data["total_cves"] == 150

    @pytest.mark.asyncio
    async def test_overview_returns_critical_count(
        self, client, mock_opensearch_client, sample_overview_aggregation_response
    ):
        """Test that overview returns critical severity count."""
        mock_opensearch_client.search.return_value = sample_overview_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/overview")

        assert response.status_code == 200
        data = response.json()
        assert "critical_count" in data
        assert data["critical_count"] == 25

    @pytest.mark.asyncio
    async def test_overview_returns_high_count(
        self, client, mock_opensearch_client, sample_overview_aggregation_response
    ):
        """Test that overview returns high severity count."""
        mock_opensearch_client.search.return_value = sample_overview_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/overview")

        assert response.status_code == 200
        data = response.json()
        assert "high_count" in data
        assert data["high_count"] == 45

    @pytest.mark.asyncio
    async def test_overview_returns_kev_count(
        self, client, mock_opensearch_client, sample_overview_aggregation_response
    ):
        """Test that overview returns KEV (Known Exploited Vulnerabilities) count."""
        mock_opensearch_client.search.return_value = sample_overview_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/overview")

        assert response.status_code == 200
        data = response.json()
        assert "kev_count" in data
        assert data["kev_count"] == 12

    @pytest.mark.asyncio
    async def test_overview_returns_avg_risk_score(
        self, client, mock_opensearch_client, sample_overview_aggregation_response
    ):
        """Test that overview returns average risk score."""
        mock_opensearch_client.search.return_value = sample_overview_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/overview")

        assert response.status_code == 200
        data = response.json()
        assert "avg_risk_score" in data
        assert data["avg_risk_score"] == 62.5

    @pytest.mark.asyncio
    async def test_overview_returns_act_count(
        self, client, mock_opensearch_client, sample_overview_aggregation_response
    ):
        """Test that overview returns ACT (Act Now) SSVC decision count."""
        mock_opensearch_client.search.return_value = sample_overview_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/overview")

        assert response.status_code == 200
        data = response.json()
        assert "act_count" in data
        assert data["act_count"] == 10

    @pytest.mark.asyncio
    async def test_overview_returns_attend_count(
        self, client, mock_opensearch_client, sample_overview_aggregation_response
    ):
        """Test that overview returns ATTEND SSVC decision count."""
        mock_opensearch_client.search.return_value = sample_overview_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/overview")

        assert response.status_code == 200
        data = response.json()
        assert "attend_count" in data
        assert data["attend_count"] == 35

    @pytest.mark.asyncio
    async def test_overview_returns_remediated_last_7d(
        self, client, mock_opensearch_client, sample_overview_aggregation_response
    ):
        """Test that overview returns count of remediated CVEs in last 7 days."""
        mock_opensearch_client.search.return_value = sample_overview_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/overview")

        assert response.status_code == 200
        data = response.json()
        assert "remediated_last_7d" in data
        assert data["remediated_last_7d"] == 8

    @pytest.mark.asyncio
    async def test_overview_handles_error_gracefully(
        self, client, mock_opensearch_client
    ):
        """Test that overview handles OpenSearch errors gracefully."""
        mock_opensearch_client.search.side_effect = Exception("Connection failed")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/overview")

        assert response.status_code == 200
        data = response.json()
        assert data["total_cves"] == 0
        assert data["critical_count"] == 0


# ============================================================================
# Tests for GET /api/vulnerabilities/terrain
# ============================================================================


class TestVulnerabilitiesTerrain:
    """Tests for the vulnerabilities terrain visualization endpoint."""

    @pytest.mark.asyncio
    async def test_terrain_returns_cells(
        self, client, mock_opensearch_client, sample_terrain_aggregation_response
    ):
        """Test that terrain returns cells array."""
        mock_opensearch_client.search.return_value = sample_terrain_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/terrain")

        assert response.status_code == 200
        data = response.json()
        assert "cells" in data
        assert isinstance(data["cells"], list)

    @pytest.mark.asyncio
    async def test_terrain_cells_have_required_fields(
        self, client, mock_opensearch_client, sample_terrain_aggregation_response
    ):
        """Test that terrain cells have required fields: x, y, risk_score, cve_count, severity."""
        mock_opensearch_client.search.return_value = sample_terrain_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/terrain")

        assert response.status_code == 200
        data = response.json()

        # At least one cell should exist
        assert len(data["cells"]) > 0

        for cell in data["cells"]:
            assert "x" in cell
            assert "y" in cell
            assert "risk_score" in cell
            assert "cve_count" in cell
            assert "severity" in cell

    @pytest.mark.asyncio
    async def test_terrain_returns_x_axis_labels(
        self, client, mock_opensearch_client, sample_terrain_aggregation_response
    ):
        """Test that terrain returns x_axis labels."""
        mock_opensearch_client.search.return_value = sample_terrain_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/terrain")

        assert response.status_code == 200
        data = response.json()
        assert "x_axis" in data
        assert data["x_axis"] == ["Low", "Medium", "High", "Critical"]

    @pytest.mark.asyncio
    async def test_terrain_returns_y_axis_labels(
        self, client, mock_opensearch_client, sample_terrain_aggregation_response
    ):
        """Test that terrain returns y_axis labels."""
        mock_opensearch_client.search.return_value = sample_terrain_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/terrain")

        assert response.status_code == 200
        data = response.json()
        assert "y_axis" in data
        assert data["y_axis"] == ["none", "poc", "active"]

    @pytest.mark.asyncio
    async def test_terrain_handles_error_gracefully(
        self, client, mock_opensearch_client
    ):
        """Test that terrain handles errors gracefully."""
        mock_opensearch_client.search.side_effect = Exception("Connection failed")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/terrain")

        assert response.status_code == 200
        data = response.json()
        assert data["cells"] == []


# ============================================================================
# Tests for GET /api/vulnerabilities/heatmap
# ============================================================================


class TestVulnerabilitiesHeatmap:
    """Tests for the vulnerabilities calendar heatmap endpoint."""

    @pytest.mark.asyncio
    async def test_heatmap_returns_data_array(
        self, client, mock_opensearch_client, sample_heatmap_aggregation_response
    ):
        """Test that heatmap returns data array."""
        mock_opensearch_client.search.return_value = sample_heatmap_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/heatmap")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_heatmap_data_has_required_fields(
        self, client, mock_opensearch_client, sample_heatmap_aggregation_response
    ):
        """Test that heatmap data items have required fields: date, count, max_severity."""
        mock_opensearch_client.search.return_value = sample_heatmap_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/heatmap")

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]) > 0
        for item in data["data"]:
            assert "date" in item
            assert "count" in item
            assert "max_severity" in item

    @pytest.mark.asyncio
    async def test_heatmap_date_format(
        self, client, mock_opensearch_client, sample_heatmap_aggregation_response
    ):
        """Test that heatmap dates are in expected format YYYY-MM-DD."""
        mock_opensearch_client.search.return_value = sample_heatmap_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/heatmap")

        assert response.status_code == 200
        data = response.json()

        # Check first item date format
        first_date = data["data"][0]["date"]
        assert first_date == "2024-01-15"

    @pytest.mark.asyncio
    async def test_heatmap_handles_error_gracefully(
        self, client, mock_opensearch_client
    ):
        """Test that heatmap handles errors gracefully."""
        mock_opensearch_client.search.side_effect = Exception("Connection failed")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/heatmap")

        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []


# ============================================================================
# Tests for GET /api/vulnerabilities/sunburst
# ============================================================================


class TestVulnerabilitiesSunburst:
    """Tests for the vulnerabilities CWE sunburst visualization endpoint."""

    @pytest.mark.asyncio
    async def test_sunburst_returns_hierarchical_structure(
        self, client, mock_opensearch_client, sample_sunburst_aggregation_response
    ):
        """Test that sunburst returns hierarchical structure with name and children."""
        mock_opensearch_client.search.return_value = sample_sunburst_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/sunburst")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "children" in data
        assert data["name"] == "CWEs"

    @pytest.mark.asyncio
    async def test_sunburst_children_have_name_and_value(
        self, client, mock_opensearch_client, sample_sunburst_aggregation_response
    ):
        """Test that sunburst children have name, value, and children fields."""
        mock_opensearch_client.search.return_value = sample_sunburst_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/sunburst")

        assert response.status_code == 200
        data = response.json()

        assert len(data["children"]) > 0
        for child in data["children"]:
            assert "name" in child
            assert "value" in child
            assert "children" in child

    @pytest.mark.asyncio
    async def test_sunburst_nested_children_have_name_and_value(
        self, client, mock_opensearch_client, sample_sunburst_aggregation_response
    ):
        """Test that nested children (CWE IDs) have name and value."""
        mock_opensearch_client.search.return_value = sample_sunburst_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/sunburst")

        assert response.status_code == 200
        data = response.json()

        # Check nested children
        first_category = data["children"][0]
        assert len(first_category["children"]) > 0
        for nested_child in first_category["children"]:
            assert "name" in nested_child
            assert "value" in nested_child

    @pytest.mark.asyncio
    async def test_sunburst_handles_error_gracefully(
        self, client, mock_opensearch_client
    ):
        """Test that sunburst handles errors gracefully."""
        mock_opensearch_client.search.side_effect = Exception("Connection failed")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/sunburst")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "CWEs"
        assert data["children"] == []


# ============================================================================
# Tests for GET /api/vulnerabilities/bubbles
# ============================================================================


class TestVulnerabilitiesBubbles:
    """Tests for the vulnerabilities priority bubbles visualization endpoint."""

    @pytest.mark.asyncio
    async def test_bubbles_returns_bubbles_array(
        self, client, mock_opensearch_client, sample_bubbles_response
    ):
        """Test that bubbles endpoint returns bubbles array."""
        mock_opensearch_client.search.return_value = sample_bubbles_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/bubbles")

        assert response.status_code == 200
        data = response.json()
        assert "bubbles" in data
        assert isinstance(data["bubbles"], list)

    @pytest.mark.asyncio
    async def test_bubbles_have_required_fields(
        self, client, mock_opensearch_client, sample_bubbles_response
    ):
        """Test that bubbles have required fields: cve_id, risk_score, severity, radius, color."""
        mock_opensearch_client.search.return_value = sample_bubbles_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/bubbles")

        assert response.status_code == 200
        data = response.json()

        assert len(data["bubbles"]) > 0
        for bubble in data["bubbles"]:
            assert "cve_id" in bubble
            assert "risk_score" in bubble
            assert "severity" in bubble
            assert "radius" in bubble
            assert "color" in bubble

    @pytest.mark.asyncio
    async def test_bubbles_critical_color_is_red(
        self, client, mock_opensearch_client, sample_bubbles_response
    ):
        """Test that Critical severity bubbles have red color."""
        mock_opensearch_client.search.return_value = sample_bubbles_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/bubbles")

        assert response.status_code == 200
        data = response.json()

        critical_bubbles = [b for b in data["bubbles"] if b["severity"] == "Critical"]
        assert len(critical_bubbles) > 0
        # Critical should be red-ish (#FF0000 or similar)
        for bubble in critical_bubbles:
            assert bubble["color"].upper().startswith("#")

    @pytest.mark.asyncio
    async def test_bubbles_radius_based_on_risk_score(
        self, client, mock_opensearch_client, sample_bubbles_response
    ):
        """Test that bubble radius is based on risk score."""
        mock_opensearch_client.search.return_value = sample_bubbles_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/bubbles")

        assert response.status_code == 200
        data = response.json()

        # Higher risk score should have larger radius
        bubbles = data["bubbles"]
        if len(bubbles) >= 2:
            high_risk = max(bubbles, key=lambda b: b["risk_score"])
            low_risk = min(bubbles, key=lambda b: b["risk_score"])
            assert high_risk["radius"] >= low_risk["radius"]

    @pytest.mark.asyncio
    async def test_bubbles_limit_parameter(
        self, client, mock_opensearch_client, sample_bubbles_response
    ):
        """Test that bubbles endpoint respects limit parameter."""
        mock_opensearch_client.search.return_value = sample_bubbles_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/bubbles?limit=10")

        assert response.status_code == 200
        # Verify the OpenSearch query used the limit
        call_args = mock_opensearch_client.search.call_args
        assert call_args[1]["body"]["size"] == 10

    @pytest.mark.asyncio
    async def test_bubbles_handles_error_gracefully(
        self, client, mock_opensearch_client
    ):
        """Test that bubbles handles errors gracefully."""
        mock_opensearch_client.search.side_effect = Exception("Connection failed")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/bubbles")

        assert response.status_code == 200
        data = response.json()
        assert data["bubbles"] == []


# ============================================================================
# Tests for GET /api/vulnerabilities/trends
# ============================================================================


class TestVulnerabilitiesTrends:
    """Tests for the vulnerabilities temporal trends endpoint."""

    @pytest.mark.asyncio
    async def test_trends_returns_data_array(
        self, client, mock_opensearch_client, sample_trends_aggregation_response
    ):
        """Test that trends returns data array."""
        mock_opensearch_client.search.return_value = sample_trends_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/trends")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_trends_data_has_date_and_count(
        self, client, mock_opensearch_client, sample_trends_aggregation_response
    ):
        """Test that trends data items have date and count fields."""
        mock_opensearch_client.search.return_value = sample_trends_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/trends")

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]) > 0
        for item in data["data"]:
            assert "date" in item
            assert "count" in item

    @pytest.mark.asyncio
    async def test_trends_interval_parameter_weekly(
        self, client, mock_opensearch_client, sample_trends_aggregation_response
    ):
        """Test that trends respects interval parameter for weekly aggregation."""
        mock_opensearch_client.search.return_value = sample_trends_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/trends?interval=week")

        assert response.status_code == 200
        # Verify the query used correct interval
        call_args = mock_opensearch_client.search.call_args
        body = call_args[1]["body"]
        assert "aggs" in body

    @pytest.mark.asyncio
    async def test_trends_interval_parameter_daily(
        self, client, mock_opensearch_client, sample_trends_aggregation_response
    ):
        """Test that trends respects interval parameter for daily aggregation."""
        mock_opensearch_client.search.return_value = sample_trends_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/trends?interval=day")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_trends_interval_parameter_monthly(
        self, client, mock_opensearch_client, sample_trends_aggregation_response
    ):
        """Test that trends respects interval parameter for monthly aggregation."""
        mock_opensearch_client.search.return_value = sample_trends_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/trends?interval=month")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_trends_handles_error_gracefully(
        self, client, mock_opensearch_client
    ):
        """Test that trends handles errors gracefully."""
        mock_opensearch_client.search.side_effect = Exception("Connection failed")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/api/vulnerabilities/trends")

        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
