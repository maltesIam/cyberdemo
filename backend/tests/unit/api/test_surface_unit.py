"""
Unit tests for Surface WOW Command Center API.

Tests for /surface/overview, /surface/nodes, and /surface/connections endpoints.
Uses mocking for OpenSearch client to test each function in isolation.
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport

from src.main import app


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def mock_opensearch_client():
    """Create a mock AsyncOpenSearch client."""
    return AsyncMock()


@pytest.fixture
async def client(mock_opensearch_client):
    """Create async test client with mocked OpenSearch."""
    with patch(
        "src.opensearch.client.get_opensearch_client",
        return_value=mock_opensearch_client
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac, mock_opensearch_client


# ============================================================================
# get_overview() Tests
# ============================================================================


class TestGetOverview:
    """Tests for the get_overview() endpoint."""

    @pytest.mark.asyncio
    async def test_total_assets_query(self, client):
        """Test total_assets count query against assets-inventory-v1."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {"hits": {"total": {"value": 150}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}, "aggregations": {"critical": {"doc_count": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
        ])

        response = await ac.get("/surface/overview")
        data = response.json()

        assert response.status_code == 200
        assert data["total_assets"] == 150
        first_call = mock_client.search.call_args_list[0]
        assert first_call.kwargs["index"] == "assets-inventory-v1"

    @pytest.mark.asyncio
    async def test_critical_assets_query(self, client):
        """Test critical_assets query filters risk_score >= 80."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {"hits": {"total": {"value": 100}}},
            {"hits": {"total": {"value": 25}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}, "aggregations": {"critical": {"doc_count": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
        ])

        response = await ac.get("/surface/overview")
        data = response.json()

        assert data["critical_assets"] == 25
        second_call = mock_client.search.call_args_list[1]
        assert second_call.kwargs["index"] == "ctem-asset-risk-v1"
        query_body = second_call.kwargs["body"]
        assert query_body["query"]["range"]["risk_score"]["gte"] == 80

    @pytest.mark.asyncio
    async def test_active_detections_query(self, client):
        """Test active_detections count from edr-detections-v1."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {"hits": {"total": {"value": 100}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 42}}},
            {"hits": {"total": {"value": 0}}, "aggregations": {"critical": {"doc_count": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
        ])

        response = await ac.get("/surface/overview")
        data = response.json()

        assert data["active_detections"] == 42
        third_call = mock_client.search.call_args_list[2]
        assert third_call.kwargs["index"] == "edr-detections-v1"

    @pytest.mark.asyncio
    async def test_open_incidents_query(self, client):
        """Test open_incidents excludes closed/resolved status."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {"hits": {"total": {"value": 100}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 15}}, "aggregations": {"critical": {"doc_count": 5}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
        ])

        response = await ac.get("/surface/overview")
        data = response.json()

        assert data["open_incidents"] == 15
        fourth_call = mock_client.search.call_args_list[3]
        assert fourth_call.kwargs["index"] == "siem-incidents-v1"
        query_body = fourth_call.kwargs["body"]
        must_not = query_body["query"]["bool"]["must_not"]
        assert {"terms": {"status": ["closed", "resolved"]}} in must_not

    @pytest.mark.asyncio
    async def test_critical_incidents_query(self, client):
        """Test critical_incidents uses severity=Critical aggregation."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {"hits": {"total": {"value": 100}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 20}}, "aggregations": {"critical": {"doc_count": 8}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
        ])

        response = await ac.get("/surface/overview")
        data = response.json()

        assert data["critical_incidents"] == 8
        fourth_call = mock_client.search.call_args_list[3]
        query_body = fourth_call.kwargs["body"]
        aggs = query_body["aggs"]["critical"]["filter"]["term"]
        assert aggs["severity"] == "Critical"

    @pytest.mark.asyncio
    async def test_contained_hosts_query(self, client):
        """Test contained_hosts filters by containment_status=contained."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {"hits": {"total": {"value": 100}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}, "aggregations": {"critical": {"doc_count": 0}}},
            {"hits": {"total": {"value": 3}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
        ])

        response = await ac.get("/surface/overview")
        data = response.json()

        assert data["contained_hosts"] == 3
        fifth_call = mock_client.search.call_args_list[4]
        assert fifth_call.kwargs["index"] == "assets-inventory-v1"
        query_body = fifth_call.kwargs["body"]
        assert query_body["query"]["term"]["edr.containment_status"] == "contained"

    @pytest.mark.asyncio
    async def test_critical_cves_query(self, client):
        """Test critical_cves filters cvss_score >= 9.0."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {"hits": {"total": {"value": 100}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}, "aggregations": {"critical": {"doc_count": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 12}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
        ])

        response = await ac.get("/surface/overview")
        data = response.json()

        assert data["critical_cves"] == 12
        sixth_call = mock_client.search.call_args_list[5]
        assert sixth_call.kwargs["index"] == "ctem-findings-v1"
        query_body = sixth_call.kwargs["body"]
        assert query_body["query"]["range"]["cvss_score"]["gte"] == 9.0

    @pytest.mark.asyncio
    async def test_kev_cves_query(self, client):
        """Test kev_cves filters exploit_available=true."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {"hits": {"total": {"value": 100}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}, "aggregations": {"critical": {"doc_count": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 7}}},
            {"hits": {"total": {"value": 0}}},
        ])

        response = await ac.get("/surface/overview")
        data = response.json()

        assert data["kev_cves"] == 7
        seventh_call = mock_client.search.call_args_list[6]
        assert seventh_call.kwargs["index"] == "ctem-findings-v1"
        query_body = seventh_call.kwargs["body"]
        assert query_body["query"]["term"]["exploit_available"] is True

    @pytest.mark.asyncio
    async def test_high_risk_iocs_query(self, client):
        """Test high_risk_iocs filters verdict=malicious and confidence >= 80."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {"hits": {"total": {"value": 100}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}, "aggregations": {"critical": {"doc_count": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 0}}},
            {"hits": {"total": {"value": 18}}},
        ])

        response = await ac.get("/surface/overview")
        data = response.json()

        assert data["high_risk_iocs"] == 18
        eighth_call = mock_client.search.call_args_list[7]
        assert eighth_call.kwargs["index"] == "threat-intel-v1"
        query_body = eighth_call.kwargs["body"]
        must_clauses = query_body["query"]["bool"]["must"]
        assert {"term": {"verdict": "malicious"}} in must_clauses
        assert {"range": {"confidence": {"gte": 80}}} in must_clauses

    @pytest.mark.asyncio
    async def test_error_handling_opensearch_down(self, client):
        """Test graceful error handling when OpenSearch is unavailable."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=Exception("Connection refused"))

        response = await ac.get("/surface/overview")
        data = response.json()

        assert response.status_code == 200
        assert data["total_assets"] == 0
        assert data["critical_assets"] == 0
        assert data["active_detections"] == 0
        assert data["open_incidents"] == 0
        assert data["critical_incidents"] == 0
        assert data["contained_hosts"] == 0
        assert data["critical_cves"] == 0
        assert data["kev_cves"] == 0
        assert data["high_risk_iocs"] == 0
        assert data["timestamp"] != ""

    @pytest.mark.asyncio
    async def test_timestamp_format_iso(self, client):
        """Test timestamp is in ISO 8601 format."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=Exception("Connection refused"))

        response = await ac.get("/surface/overview")
        data = response.json()

        timestamp = data["timestamp"]
        assert timestamp != ""
        parsed = datetime.fromisoformat(timestamp)
        assert isinstance(parsed, datetime)

    @pytest.mark.asyncio
    async def test_partial_opensearch_failures(self, client):
        """Test that partial failures don't break the entire response."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {"hits": {"total": {"value": 100}}},
            Exception("Timeout"),
            {"hits": {"total": {"value": 50}}},
            Exception("Index not found"),
            Exception("Connection lost"),
            Exception("Connection lost"),
            Exception("Connection lost"),
            Exception("Connection lost"),
        ])

        response = await ac.get("/surface/overview")
        data = response.json()

        assert data["total_assets"] == 100
        assert data["critical_assets"] == 0
        assert data["active_detections"] == 50
        assert data["open_incidents"] == 0


# ============================================================================
# get_nodes() Tests
# ============================================================================


class TestGetNodes:
    """Tests for the get_nodes() endpoint."""

    @pytest.mark.asyncio
    async def test_default_pagination(self, client):
        """Test default pagination (page=1, page_size=200)."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "total": {"value": 500},
                "hits": [
                    {"_source": {"asset_id": "A001", "hostname": "SRV-001", "ip": "10.0.0.1", "asset_type": "server"}}
                ]
            }
        })

        response = await ac.get("/surface/nodes")

        assert response.status_code == 200
        first_call = mock_client.search.call_args_list[0]
        body = first_call.kwargs["body"]
        assert body["from"] == 0
        assert body["size"] == 200

    @pytest.mark.asyncio
    async def test_custom_pagination(self, client):
        """Test custom pagination parameters."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {"total": {"value": 100}, "hits": []}
        })

        response = await ac.get("/surface/nodes?page=3&page_size=50")

        assert response.status_code == 200
        first_call = mock_client.search.call_args_list[0]
        body = first_call.kwargs["body"]
        assert body["from"] == 100
        assert body["size"] == 50

    @pytest.mark.asyncio
    async def test_filter_by_asset_type(self, client):
        """Test filtering by asset_type parameter."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {"total": {"value": 0}, "hits": []}
        })

        response = await ac.get("/surface/nodes?asset_type=server")

        assert response.status_code == 200
        first_call = mock_client.search.call_args_list[0]
        query = first_call.kwargs["body"]["query"]
        assert {"term": {"asset_type": "server"}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_filter_by_risk_min(self, client):
        """Test filtering by risk_min parameter (post-query filter)."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {
                "hits": {
                    "total": {"value": 2},
                    "hits": [
                        {"_source": {"asset_id": "A001", "hostname": "H1", "ip": "10.0.0.1"}},
                        {"_source": {"asset_id": "A002", "hostname": "H2", "ip": "10.0.0.2"}},
                    ]
                }
            },
            {"aggregations": {"by_asset": {"buckets": []}}},
            {"aggregations": {"by_asset": {"buckets": []}}},
            {
                "hits": {
                    "hits": [
                        {"_source": {"asset_id": "A001", "risk_color": "Green", "finding_count": 0}},
                        {"_source": {"asset_id": "A002", "risk_color": "Red", "finding_count": 10}},
                    ]
                }
            },
            {"aggregations": {"by_asset": {"buckets": []}}},
        ])

        response = await ac.get("/surface/nodes?risk_min=50")
        data = response.json()

        # Only A002 should be returned (risk_score > 50)
        assert len(data["nodes"]) == 1
        assert data["nodes"][0]["id"] == "A002"
        assert data["nodes"][0]["risk_score"] >= 50

    @pytest.mark.asyncio
    async def test_filter_by_risk_max(self, client):
        """Test filtering by risk_max parameter."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {
                "hits": {
                    "total": {"value": 2},
                    "hits": [
                        {"_source": {"asset_id": "A001", "hostname": "H1", "ip": "10.0.0.1"}},
                        {"_source": {"asset_id": "A002", "hostname": "H2", "ip": "10.0.0.2"}},
                    ]
                }
            },
            {"aggregations": {"by_asset": {"buckets": []}}},
            {"aggregations": {"by_asset": {"buckets": []}}},
            {
                "hits": {
                    "hits": [
                        {"_source": {"asset_id": "A001", "risk_color": "Green", "finding_count": 0}},
                        {"_source": {"asset_id": "A002", "risk_color": "Red", "finding_count": 10}},
                    ]
                }
            },
            {"aggregations": {"by_asset": {"buckets": []}}},
        ])

        response = await ac.get("/surface/nodes?risk_max=50")
        data = response.json()

        assert len(data["nodes"]) == 1
        assert data["nodes"][0]["id"] == "A001"
        assert data["nodes"][0]["risk_score"] <= 50

    @pytest.mark.asyncio
    async def test_search_by_hostname(self, client):
        """Test search parameter uses wildcard on hostname."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {"total": {"value": 0}, "hits": []}
        })

        response = await ac.get("/surface/nodes?search=srv")

        assert response.status_code == 200
        first_call = mock_client.search.call_args_list[0]
        query = first_call.kwargs["body"]["query"]
        assert {"wildcard": {"hostname": "*SRV*"}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_empty_results(self, client):
        """Test handling of empty search results."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {"total": {"value": 0}, "hits": []}
        })

        response = await ac.get("/surface/nodes")
        data = response.json()

        assert data["total"] == 0
        assert data["nodes"] == []

    @pytest.mark.asyncio
    async def test_layer_building_base(self, client):
        """Test that base layer is always True."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {
                "hits": {
                    "total": {"value": 1},
                    "hits": [{"_source": {"asset_id": "A001", "hostname": "H1", "ip": "10.0.0.1"}}]
                }
            },
            {"aggregations": {"by_asset": {"buckets": []}}},
            {"aggregations": {"by_asset": {"buckets": []}}},
            {"hits": {"hits": []}},
            {"aggregations": {"by_asset": {"buckets": []}}},
        ])

        response = await ac.get("/surface/nodes")
        data = response.json()

        assert len(data["nodes"]) == 1
        assert data["nodes"][0]["layers"]["base"] is True

    @pytest.mark.asyncio
    async def test_layer_building_edr(self, client):
        """Test EDR layer enrichment with detection data."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {
                "hits": {
                    "total": {"value": 1},
                    "hits": [{
                        "_source": {
                            "asset_id": "A001",
                            "hostname": "H1",
                            "ip": "10.0.0.1",
                            "edr": {"agent_version": "7.2.1", "containment_status": "normal"}
                        }
                    }]
                }
            },
            {
                "aggregations": {
                    "by_asset": {
                        "buckets": [{
                            "key": "A001",
                            "doc_count": 5,
                            "max_sev": {"buckets": [{"key": "High"}]}
                        }]
                    }
                }
            },
            {"aggregations": {"by_asset": {"buckets": []}}},
            {"hits": {"hits": []}},
            {"aggregations": {"by_asset": {"buckets": []}}},
        ])

        response = await ac.get("/surface/nodes")
        data = response.json()

        edr_layer = data["nodes"][0]["layers"]["edr"]
        assert edr_layer["active"] is True
        assert edr_layer["detection_count"] == 5
        assert edr_layer["max_severity"] == "High"

    @pytest.mark.asyncio
    async def test_layer_building_siem(self, client):
        """Test SIEM layer enrichment with incident data."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {
                "hits": {
                    "total": {"value": 1},
                    "hits": [{"_source": {"asset_id": "A001", "hostname": "H1", "ip": "10.0.0.1"}}]
                }
            },
            {"aggregations": {"by_asset": {"buckets": []}}},
            {
                "aggregations": {
                    "by_asset": {
                        "buckets": [{
                            "key": "A001",
                            "doc_count": 3,
                            "latest_status": {"buckets": [{"key": "investigating"}]}
                        }]
                    }
                }
            },
            {"hits": {"hits": []}},
            {"aggregations": {"by_asset": {"buckets": []}}},
        ])

        response = await ac.get("/surface/nodes")
        data = response.json()

        siem_layer = data["nodes"][0]["layers"]["siem"]
        assert siem_layer["active"] is True
        assert siem_layer["incident_count"] == 3
        assert siem_layer["status"] == "investigating"

    @pytest.mark.asyncio
    async def test_layer_building_vulnerabilities(self, client):
        """Test vulnerabilities layer enrichment."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {
                "hits": {
                    "total": {"value": 1},
                    "hits": [{"_source": {"asset_id": "A001", "hostname": "H1", "ip": "10.0.0.1"}}]
                }
            },
            {"aggregations": {"by_asset": {"buckets": []}}},
            {"aggregations": {"by_asset": {"buckets": []}}},
            {"hits": {"hits": []}},
            {
                "aggregations": {
                    "by_asset": {
                        "buckets": [{
                            "key": "A001",
                            "doc_count": 15,
                            "critical": {"doc_count": 3},
                            "kev": {"doc_count": 2}
                        }]
                    }
                }
            },
        ])

        response = await ac.get("/surface/nodes")
        data = response.json()

        vuln_layer = data["nodes"][0]["layers"]["vulnerabilities"]
        assert vuln_layer["active"] is True
        assert vuln_layer["cve_count"] == 15
        assert vuln_layer["critical_count"] == 3
        assert vuln_layer["kev_count"] == 2

    @pytest.mark.asyncio
    async def test_layer_building_threats(self, client):
        """Test threats layer enrichment via IP matching."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {
                "hits": {
                    "total": {"value": 1},
                    "hits": [{"_source": {"asset_id": "A001", "hostname": "H1", "ip": "10.0.0.1"}}]
                }
            },
            {"aggregations": {"by_asset": {"buckets": []}}},
            {"aggregations": {"by_asset": {"buckets": []}}},
            {"hits": {"hits": []}},
            {"aggregations": {"by_asset": {"buckets": []}}},
            {
                "aggregations": {
                    "by_ip": {
                        "buckets": [{
                            "key": "10.0.0.1",
                            "doc_count": 4,
                            "actors": {"buckets": [{"key": "APT29"}, {"key": "FIN7"}]}
                        }]
                    }
                }
            },
        ])

        response = await ac.get("/surface/nodes")
        data = response.json()

        threats_layer = data["nodes"][0]["layers"]["threats"]
        assert threats_layer["active"] is True
        assert threats_layer["ioc_count"] == 4
        assert "APT29" in threats_layer["actors"]
        assert "FIN7" in threats_layer["actors"]

    @pytest.mark.asyncio
    async def test_layer_building_containment(self, client):
        """Test containment layer for contained hosts."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {
                "hits": {
                    "total": {"value": 1},
                    "hits": [{
                        "_source": {
                            "asset_id": "A001",
                            "hostname": "H1",
                            "ip": "10.0.0.1",
                            "edr": {
                                "containment_status": "contained",
                                "last_seen": "2024-01-15T10:30:00Z"
                            }
                        }
                    }]
                }
            },
            {"aggregations": {"by_asset": {"buckets": []}}},
            {"aggregations": {"by_asset": {"buckets": []}}},
            {"hits": {"hits": []}},
            {"aggregations": {"by_asset": {"buckets": []}}},
        ])

        response = await ac.get("/surface/nodes")
        data = response.json()

        containment_layer = data["nodes"][0]["layers"]["containment"]
        assert containment_layer["active"] is True
        assert containment_layer["is_contained"] is True
        assert containment_layer["contained_at"] == "2024-01-15T10:30:00Z"

    @pytest.mark.asyncio
    async def test_layer_building_relations(self, client):
        """Test relations layer based on incident count."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {
                "hits": {
                    "total": {"value": 1},
                    "hits": [{"_source": {"asset_id": "A001", "hostname": "H1", "ip": "10.0.0.1"}}]
                }
            },
            {"aggregations": {"by_asset": {"buckets": []}}},
            {
                "aggregations": {
                    "by_asset": {
                        "buckets": [{
                            "key": "A001",
                            "doc_count": 7,
                            "latest_status": {"buckets": [{"key": "open"}]}
                        }]
                    }
                }
            },
            {"hits": {"hits": []}},
            {"aggregations": {"by_asset": {"buckets": []}}},
        ])

        response = await ac.get("/surface/nodes")
        data = response.json()

        relations_layer = data["nodes"][0]["layers"]["relations"]
        assert relations_layer["active"] is True
        assert relations_layer["connection_count"] == 7

    @pytest.mark.asyncio
    async def test_risk_score_computation_formula(self, client):
        """Test risk_score is computed as base_score + min(findings * 2, 20)."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {
                "hits": {
                    "total": {"value": 3},
                    "hits": [
                        {"_source": {"asset_id": "A001", "hostname": "H1", "ip": "10.0.0.1"}},
                        {"_source": {"asset_id": "A002", "hostname": "H2", "ip": "10.0.0.2"}},
                        {"_source": {"asset_id": "A003", "hostname": "H3", "ip": "10.0.0.3"}},
                    ]
                }
            },
            {"aggregations": {"by_asset": {"buckets": []}}},
            {"aggregations": {"by_asset": {"buckets": []}}},
            {
                "hits": {
                    "hits": [
                        {"_source": {"asset_id": "A001", "risk_color": "Red", "finding_count": 0}},
                        {"_source": {"asset_id": "A002", "risk_color": "Yellow", "finding_count": 5}},
                        {"_source": {"asset_id": "A003", "risk_color": "Green", "finding_count": 15}},
                    ]
                }
            },
            {"aggregations": {"by_asset": {"buckets": []}}},
        ])

        response = await ac.get("/surface/nodes")
        data = response.json()

        # A001: Red(80) + min(0*2, 20) = 80
        assert data["nodes"][0]["risk_score"] == 80
        # A002: Yellow(50) + min(5*2, 20) = 50 + 10 = 60
        assert data["nodes"][1]["risk_score"] == 60
        # A003: Green(20) + min(15*2, 20) = 20 + 20 = 40
        assert data["nodes"][2]["risk_score"] == 40

    @pytest.mark.asyncio
    async def test_error_handling_returns_empty(self, client):
        """Test that OpenSearch errors return empty NodeList."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=Exception("Connection refused"))

        response = await ac.get("/surface/nodes")
        data = response.json()

        assert data["total"] == 0
        assert data["nodes"] == []


# ============================================================================
# get_connections() Tests
# ============================================================================


class TestGetConnections:
    """Tests for the get_connections() endpoint."""

    @pytest.mark.asyncio
    async def test_incident_based_connection_creation(self, client):
        """Test connections are created from incidents with multiple related assets."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [{
                    "_source": {
                        "incident_id": "INC-001",
                        "title": "Shared IOC Detection",
                        "severity": "High",
                        "related_assets": ["A001", "A002", "A003"],
                        "created_at": "2024-01-15T10:00:00Z"
                    }
                }]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        assert len(data["connections"]) == 3
        pairs = {(c["source_id"], c["target_id"]) for c in data["connections"]}
        assert ("A001", "A002") in pairs
        assert ("A001", "A003") in pairs
        assert ("A002", "A003") in pairs

    @pytest.mark.asyncio
    async def test_connection_type_lateral_movement(self, client):
        """Test connection type inference for lateral movement."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [{
                    "_source": {
                        "title": "Lateral Movement Detected",
                        "severity": "Critical",
                        "related_assets": ["A001", "A002"],
                        "created_at": "2024-01-15T10:00:00Z"
                    }
                }]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        assert len(data["connections"]) == 1
        assert data["connections"][0]["type"] == "lateral_movement"

    @pytest.mark.asyncio
    async def test_connection_type_c2_communication(self, client):
        """Test connection type inference for C2 communication."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [{
                    "_source": {
                        "title": "C2 Beacon Activity",
                        "severity": "High",
                        "related_assets": ["A001", "A002"],
                        "created_at": "2024-01-15T10:00:00Z"
                    }
                }]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        assert data["connections"][0]["type"] == "c2_communication"

    @pytest.mark.asyncio
    async def test_connection_type_data_exfil(self, client):
        """Test connection type inference for data exfiltration."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [{
                    "_source": {
                        "title": "Data Exfiltration Attempt",
                        "severity": "Critical",
                        "related_assets": ["A001", "A002"],
                        "created_at": "2024-01-15T10:00:00Z"
                    }
                }]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        assert data["connections"][0]["type"] == "data_exfil"

    @pytest.mark.asyncio
    async def test_connection_type_shared_ioc_default(self, client):
        """Test default connection type is shared_ioc."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [{
                    "_source": {
                        "title": "Generic Security Alert",
                        "severity": "Medium",
                        "related_assets": ["A001", "A002"],
                        "created_at": "2024-01-15T10:00:00Z"
                    }
                }]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        assert data["connections"][0]["type"] == "shared_ioc"

    @pytest.mark.asyncio
    async def test_severity_to_strength_mapping_critical(self, client):
        """Test Critical severity maps to strength 1.0."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [{
                    "_source": {
                        "title": "Alert",
                        "severity": "Critical",
                        "related_assets": ["A001", "A002"],
                        "created_at": "2024-01-15T10:00:00Z"
                    }
                }]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        assert data["connections"][0]["strength"] == 1.0

    @pytest.mark.asyncio
    async def test_severity_to_strength_mapping_high(self, client):
        """Test High severity maps to strength 0.8."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [{
                    "_source": {
                        "title": "Alert",
                        "severity": "High",
                        "related_assets": ["A001", "A002"],
                        "created_at": "2024-01-15T10:00:00Z"
                    }
                }]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        assert data["connections"][0]["strength"] == 0.8

    @pytest.mark.asyncio
    async def test_severity_to_strength_mapping_medium(self, client):
        """Test Medium severity maps to strength 0.5."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [{
                    "_source": {
                        "title": "Alert",
                        "severity": "Medium",
                        "related_assets": ["A001", "A002"],
                        "created_at": "2024-01-15T10:00:00Z"
                    }
                }]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        assert data["connections"][0]["strength"] == 0.5

    @pytest.mark.asyncio
    async def test_severity_to_strength_mapping_low(self, client):
        """Test Low severity maps to strength 0.3."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [{
                    "_source": {
                        "title": "Alert",
                        "severity": "Low",
                        "related_assets": ["A001", "A002"],
                        "created_at": "2024-01-15T10:00:00Z"
                    }
                }]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        assert data["connections"][0]["strength"] == 0.3

    @pytest.mark.asyncio
    async def test_deduplication_logic(self, client):
        """Test that duplicate asset pairs are deduplicated."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "title": "First Alert",
                            "severity": "High",
                            "related_assets": ["A001", "A002"],
                            "created_at": "2024-01-15T10:00:00Z"
                        }
                    },
                    {
                        "_source": {
                            "title": "Second Alert",
                            "severity": "Critical",
                            "related_assets": ["A002", "A001"],
                            "created_at": "2024-01-15T11:00:00Z"
                        }
                    }
                ]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        assert len(data["connections"]) == 1

    @pytest.mark.asyncio
    async def test_type_filter(self, client):
        """Test filtering connections by type parameter."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "title": "Lateral Movement",
                            "severity": "High",
                            "related_assets": ["A001", "A002"],
                            "created_at": "2024-01-15T10:00:00Z"
                        }
                    },
                    {
                        "_source": {
                            "title": "Generic Alert",
                            "severity": "Medium",
                            "related_assets": ["A003", "A004"],
                            "created_at": "2024-01-15T11:00:00Z"
                        }
                    }
                ]
            }
        })

        response = await ac.get("/surface/connections?type=lateral_movement")
        data = response.json()

        assert len(data["connections"]) == 1
        assert data["connections"][0]["type"] == "lateral_movement"

    @pytest.mark.asyncio
    async def test_asset_ids_filter(self, client):
        """Test filtering by asset_ids parameter."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {"hits": []}
        })

        response = await ac.get("/surface/connections?asset_ids=A001,A002,A003")

        assert response.status_code == 200
        call_args = mock_client.search.call_args
        query = call_args.kwargs["body"]["query"]
        assert {"terms": {"related_assets": ["A001", "A002", "A003"]}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_empty_related_assets_handling(self, client):
        """Test incidents with empty or single related_assets are skipped."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [
                    {"_source": {"title": "Single Asset Alert", "severity": "High", "related_assets": ["A001"], "created_at": "2024-01-15T10:00:00Z"}},
                    {"_source": {"title": "No Assets Alert", "severity": "High", "related_assets": [], "created_at": "2024-01-15T11:00:00Z"}},
                    {"_source": {"title": "Missing Assets Alert", "severity": "High", "created_at": "2024-01-15T12:00:00Z"}},
                    {"_source": {"title": "Valid Alert", "severity": "Medium", "related_assets": ["A001", "A002"], "created_at": "2024-01-15T13:00:00Z"}}
                ]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        assert len(data["connections"]) == 1
        assert data["connections"][0]["source_id"] == "A001"
        assert data["connections"][0]["target_id"] == "A002"

    @pytest.mark.asyncio
    async def test_connection_timestamp(self, client):
        """Test connection includes incident timestamp."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [{
                    "_source": {
                        "title": "Alert",
                        "severity": "High",
                        "related_assets": ["A001", "A002"],
                        "created_at": "2024-01-15T10:30:45Z"
                    }
                }]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        assert data["connections"][0]["timestamp"] == "2024-01-15T10:30:45Z"

    @pytest.mark.asyncio
    async def test_error_handling_returns_empty(self, client):
        """Test that OpenSearch errors return empty ConnectionList."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=Exception("Connection refused"))

        response = await ac.get("/surface/connections")
        data = response.json()

        assert data["connections"] == []

    @pytest.mark.asyncio
    async def test_multiple_incidents_multiple_connections(self, client):
        """Test connections from multiple incidents with different asset groups."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [
                    {"_source": {"title": "Group 1 Alert", "severity": "High", "related_assets": ["A001", "A002"], "created_at": "2024-01-15T10:00:00Z"}},
                    {"_source": {"title": "Group 2 Alert", "severity": "Medium", "related_assets": ["A003", "A004"], "created_at": "2024-01-15T11:00:00Z"}},
                    {"_source": {"title": "Cross-Group Alert", "severity": "Critical", "related_assets": ["A001", "A003", "A005"], "created_at": "2024-01-15T12:00:00Z"}}
                ]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        # Group 1: A001-A002 (1), Group 2: A003-A004 (1), Cross-Group: A001-A003, A001-A005, A003-A005 (3)
        assert len(data["connections"]) == 5

    @pytest.mark.asyncio
    async def test_case_insensitive_type_matching(self, client):
        """Test that type matching in titles is case insensitive."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [{
                    "_source": {
                        "title": "LATERAL MOVEMENT DETECTED",
                        "severity": "High",
                        "related_assets": ["A001", "A002"],
                        "created_at": "2024-01-15T10:00:00Z"
                    }
                }]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        assert data["connections"][0]["type"] == "lateral_movement"

    @pytest.mark.asyncio
    async def test_default_severity_handling(self, client):
        """Test handling of missing severity field."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [{
                    "_source": {
                        "title": "Alert without severity",
                        "related_assets": ["A001", "A002"],
                        "created_at": "2024-01-15T10:00:00Z"
                    }
                }]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        assert data["connections"][0]["strength"] == 0.5

    @pytest.mark.asyncio
    async def test_null_title_handling(self, client):
        """Test handling of null/missing title field."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [{
                    "_source": {
                        "title": None,
                        "severity": "High",
                        "related_assets": ["A001", "A002"],
                        "created_at": "2024-01-15T10:00:00Z"
                    }
                }]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        assert data["connections"][0]["type"] == "shared_ioc"


# ============================================================================
# Edge Cases
# ============================================================================


class TestEdgeCases:
    """Additional edge case tests."""

    @pytest.mark.asyncio
    async def test_get_overview_with_zero_values(self, client):
        """Test overview returns zeros when all queries return 0."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {"total": {"value": 0}},
            "aggregations": {"critical": {"doc_count": 0}}
        })

        response = await ac.get("/surface/overview")
        data = response.json()

        assert data["total_assets"] == 0
        assert data["critical_assets"] == 0
        assert data["active_detections"] == 0

    @pytest.mark.asyncio
    async def test_get_nodes_with_null_nested_data(self, client):
        """Test nodes handle null nested objects gracefully."""
        ac, mock_client = client

        mock_client.search = AsyncMock(side_effect=[
            {
                "hits": {
                    "total": {"value": 1},
                    "hits": [{
                        "_source": {
                            "asset_id": "A001",
                            "hostname": "H1",
                            "ip": None,
                            "edr": None,
                            "ctem": None
                        }
                    }]
                }
            },
            {"aggregations": {"by_asset": {"buckets": []}}},
            {"aggregations": {"by_asset": {"buckets": []}}},
            {"hits": {"hits": []}},
            {"aggregations": {"by_asset": {"buckets": []}}},
        ])

        response = await ac.get("/surface/nodes")
        data = response.json()

        assert len(data["nodes"]) == 1
        node = data["nodes"][0]
        assert node["ip"] is None
        assert node["layers"]["edr"]["active"] is False
        assert node["layers"]["ctem"]["active"] is False

    @pytest.mark.asyncio
    async def test_get_connections_with_special_characters_in_title(self, client):
        """Test connection type detection with special characters in title."""
        ac, mock_client = client

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [{
                    "_source": {
                        "title": "C2/C&C - Beacon-like traffic detected!",
                        "severity": "High",
                        "related_assets": ["A001", "A002"],
                        "created_at": "2024-01-15T10:00:00Z"
                    }
                }]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        assert data["connections"][0]["type"] == "c2_communication"

    @pytest.mark.asyncio
    async def test_large_related_assets_list(self, client):
        """Test handling of incident with many related assets."""
        ac, mock_client = client

        assets = [f"A{str(i).zfill(3)}" for i in range(10)]

        mock_client.search = AsyncMock(return_value={
            "hits": {
                "hits": [{
                    "_source": {
                        "title": "Mass Infection",
                        "severity": "Critical",
                        "related_assets": assets,
                        "created_at": "2024-01-15T10:00:00Z"
                    }
                }]
            }
        })

        response = await ac.get("/surface/connections")
        data = response.json()

        # n choose 2 = 10 * 9 / 2 = 45
        assert len(data["connections"]) == 45
