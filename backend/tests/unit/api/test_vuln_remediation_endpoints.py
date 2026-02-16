"""
Unit tests for Vulnerability Remediation API endpoints.

Following TDD: Tests for remediation statistics and Sankey flow visualization.
Uses mocking for OpenSearch client to isolate API logic.
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
def sample_remediation_stats_response():
    """Sample aggregation response for remediation stats endpoint."""
    return {
        "hits": {"total": {"value": 410}},
        "aggregations": {
            "by_status": {
                "buckets": [
                    {"key": "open", "doc_count": 100},
                    {"key": "in_progress", "doc_count": 35},
                    {"key": "remediated", "doc_count": 250},
                    {"key": "accepted_risk", "doc_count": 15},
                    {"key": "false_positive", "doc_count": 10},
                ]
            },
            "by_severity_status": {
                "buckets": [
                    {
                        "key": "Critical",
                        "doc_count": 25,
                        "status_breakdown": {
                            "buckets": [
                                {"key": "open", "doc_count": 5},
                                {"key": "remediated", "doc_count": 20},
                            ]
                        },
                    },
                    {
                        "key": "High",
                        "doc_count": 105,
                        "status_breakdown": {
                            "buckets": [
                                {"key": "open", "doc_count": 25},
                                {"key": "remediated", "doc_count": 80},
                            ]
                        },
                    },
                    {
                        "key": "Medium",
                        "doc_count": 145,
                        "status_breakdown": {
                            "buckets": [
                                {"key": "open", "doc_count": 45},
                                {"key": "remediated", "doc_count": 100},
                            ]
                        },
                    },
                    {
                        "key": "Low",
                        "doc_count": 75,
                        "status_breakdown": {
                            "buckets": [
                                {"key": "open", "doc_count": 25},
                                {"key": "remediated", "doc_count": 50},
                            ]
                        },
                    },
                ]
            },
            "mttr_by_severity": {
                "buckets": [
                    {"key": "Critical", "doc_count": 20, "avg_remediation_days": {"value": 3.5}},
                    {"key": "High", "doc_count": 80, "avg_remediation_days": {"value": 7.2}},
                    {"key": "Medium", "doc_count": 100, "avg_remediation_days": {"value": 14.8}},
                    {"key": "Low", "doc_count": 50, "avg_remediation_days": {"value": 30.1}},
                ]
            },
            "sla_compliance": {
                "buckets": [
                    {"key": "on_track", "doc_count": 75},
                    {"key": "at_risk", "doc_count": 18},
                    {"key": "overdue", "doc_count": 7},
                ]
            },
            "remediated_last_7_days": {"doc_count": 25},
            "remediated_last_30_days": {"doc_count": 85},
        },
    }


@pytest.fixture
def sample_sankey_flow_response():
    """Sample aggregation response for Sankey flow endpoint."""
    return {
        "aggregations": {
            "flow_transitions": {
                "buckets": [
                    {
                        "key": "discovered",
                        "doc_count": 150,
                        "next_status": {
                            "buckets": [
                                {"key": "triaged", "doc_count": 150},
                            ]
                        },
                    },
                    {
                        "key": "triaged",
                        "doc_count": 145,
                        "next_status": {
                            "buckets": [
                                {"key": "assigned", "doc_count": 120},
                                {"key": "false_positive", "doc_count": 10},
                                {"key": "accepted_risk", "doc_count": 15},
                            ]
                        },
                    },
                    {
                        "key": "assigned",
                        "doc_count": 120,
                        "next_status": {
                            "buckets": [
                                {"key": "in_progress", "doc_count": 100},
                            ]
                        },
                    },
                    {
                        "key": "in_progress",
                        "doc_count": 100,
                        "next_status": {
                            "buckets": [
                                {"key": "remediated", "doc_count": 85},
                            ]
                        },
                    },
                    {
                        "key": "remediated",
                        "doc_count": 85,
                        "next_status": {
                            "buckets": [
                                {"key": "verified", "doc_count": 80},
                            ]
                        },
                    },
                ]
            }
        }
    }


# ============================================================================
# Tests for GET /vulnerabilities/remediation/stats
# ============================================================================


class TestRemediationStats:
    """Tests for the remediation stats endpoint."""

    @pytest.mark.asyncio
    async def test_remediation_stats_returns_200(
        self, client, mock_opensearch_client, sample_remediation_stats_response
    ):
        """Test that remediation stats endpoint returns 200 OK."""
        mock_opensearch_client.search.return_value = sample_remediation_stats_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/remediation/stats")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_remediation_stats_total_counts(
        self, client, mock_opensearch_client, sample_remediation_stats_response
    ):
        """Test that total counts are correctly parsed from aggregations."""
        mock_opensearch_client.search.return_value = sample_remediation_stats_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/remediation/stats")

        data = response.json()
        assert data["total_open"] == 100
        assert data["in_progress"] == 35
        assert data["remediated"] == 250
        assert data["accepted_risk"] == 15
        assert data["false_positive"] == 10

    @pytest.mark.asyncio
    async def test_remediation_stats_by_severity(
        self, client, mock_opensearch_client, sample_remediation_stats_response
    ):
        """Test that by_severity breakdown is correctly parsed."""
        mock_opensearch_client.search.return_value = sample_remediation_stats_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/remediation/stats")

        data = response.json()
        assert "by_severity" in data
        assert data["by_severity"]["Critical"]["open"] == 5
        assert data["by_severity"]["Critical"]["remediated"] == 20
        assert data["by_severity"]["High"]["open"] == 25
        assert data["by_severity"]["High"]["remediated"] == 80

    @pytest.mark.asyncio
    async def test_remediation_stats_mttr_days(
        self, client, mock_opensearch_client, sample_remediation_stats_response
    ):
        """Test that MTTR (Mean Time To Remediate) is correctly parsed."""
        mock_opensearch_client.search.return_value = sample_remediation_stats_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/remediation/stats")

        data = response.json()
        assert "mttr_days" in data
        assert data["mttr_days"]["Critical"] == 3.5
        assert data["mttr_days"]["High"] == 7.2
        assert data["mttr_days"]["Medium"] == 14.8
        assert data["mttr_days"]["Low"] == 30.1

    @pytest.mark.asyncio
    async def test_remediation_stats_sla_compliance(
        self, client, mock_opensearch_client, sample_remediation_stats_response
    ):
        """Test that SLA compliance metrics are correctly parsed."""
        mock_opensearch_client.search.return_value = sample_remediation_stats_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/remediation/stats")

        data = response.json()
        assert "sla_compliance" in data
        assert data["sla_compliance"]["on_track"] == 75
        assert data["sla_compliance"]["at_risk"] == 18
        assert data["sla_compliance"]["overdue"] == 7

    @pytest.mark.asyncio
    async def test_remediation_stats_time_based_metrics(
        self, client, mock_opensearch_client, sample_remediation_stats_response
    ):
        """Test that time-based remediation metrics are included."""
        mock_opensearch_client.search.return_value = sample_remediation_stats_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/remediation/stats")

        data = response.json()
        assert data["remediated_last_7_days"] == 25
        assert data["remediated_last_30_days"] == 85

    @pytest.mark.asyncio
    async def test_remediation_stats_error_handling(
        self, client, mock_opensearch_client
    ):
        """Test that errors return empty stats instead of crashing."""
        mock_opensearch_client.search.side_effect = Exception("OpenSearch error")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/remediation/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_open"] == 0
        assert data["remediated"] == 0


# ============================================================================
# Tests for GET /vulnerabilities/remediation/flow
# ============================================================================


class TestRemediationFlow:
    """Tests for the Sankey flow visualization endpoint."""

    @pytest.mark.asyncio
    async def test_remediation_flow_returns_200(
        self, client, mock_opensearch_client, sample_sankey_flow_response
    ):
        """Test that flow endpoint returns 200 OK."""
        mock_opensearch_client.search.return_value = sample_sankey_flow_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/remediation/flow")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_remediation_flow_has_nodes(
        self, client, mock_opensearch_client, sample_sankey_flow_response
    ):
        """Test that flow response contains nodes array."""
        mock_opensearch_client.search.return_value = sample_sankey_flow_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/remediation/flow")

        data = response.json()
        assert "nodes" in data
        assert len(data["nodes"]) > 0
        # Check node structure
        node = data["nodes"][0]
        assert "id" in node
        assert "name" in node

    @pytest.mark.asyncio
    async def test_remediation_flow_has_links(
        self, client, mock_opensearch_client, sample_sankey_flow_response
    ):
        """Test that flow response contains links array."""
        mock_opensearch_client.search.return_value = sample_sankey_flow_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/remediation/flow")

        data = response.json()
        assert "links" in data
        assert len(data["links"]) > 0
        # Check link structure
        link = data["links"][0]
        assert "source" in link
        assert "target" in link
        assert "value" in link

    @pytest.mark.asyncio
    async def test_remediation_flow_link_values(
        self, client, mock_opensearch_client, sample_sankey_flow_response
    ):
        """Test that link values are correctly extracted from aggregations."""
        mock_opensearch_client.search.return_value = sample_sankey_flow_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/remediation/flow")

        data = response.json()
        links = data["links"]

        # Find specific links and verify values
        discovered_to_triaged = next(
            (l for l in links if l["source"] == "discovered" and l["target"] == "triaged"),
            None,
        )
        assert discovered_to_triaged is not None
        assert discovered_to_triaged["value"] == 150

    @pytest.mark.asyncio
    async def test_remediation_flow_error_handling(
        self, client, mock_opensearch_client
    ):
        """Test that errors return empty flow data instead of crashing."""
        mock_opensearch_client.search.side_effect = Exception("OpenSearch error")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/remediation/flow")

        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "links" in data
