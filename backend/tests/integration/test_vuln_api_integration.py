"""
Integration tests for Vulnerability API endpoints.

Tests the complete flow across vulnerability endpoints:
- Enrichment endpoints
- Remediation statistics
- Sankey flow visualization
- Error handling across endpoints
- Pagination and filtering
"""
import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport

from src.main import app


pytestmark = pytest.mark.asyncio


@pytest.fixture
async def client():
    """Create async HTTP client for testing."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def mock_opensearch_client():
    """Create a mock OpenSearch client."""
    client = AsyncMock()
    return client


OPENSEARCH_CLIENT_PATH = "src.opensearch.client.get_opensearch_client"


class TestVulnerabilityEndpointsIntegration:
    """Integration tests for vulnerability management flow."""

    async def test_full_flow_get_cve_then_remediation_stats(
        self, client, mock_opensearch_client
    ):
        """Test flow: Get CVE details -> Check remediation stats."""
        # Mock CVE details response
        cve_response = {
            "hits": {
                "total": {"value": 2},
                "hits": [
                    {
                        "_source": {
                            "cve_id": "CVE-2024-1234",
                            "title": "Critical RCE Vulnerability",
                            "severity": "Critical",
                            "cvss_score": 9.8,
                            "epss_score": 0.95,
                            "asset_id": "ASSET-001",
                        }
                    },
                    {
                        "_source": {
                            "cve_id": "CVE-2024-1234",
                            "title": "Critical RCE Vulnerability",
                            "severity": "Critical",
                            "cvss_score": 9.8,
                            "epss_score": 0.95,
                            "asset_id": "ASSET-002",
                        }
                    },
                ],
            }
        }

        # Mock remediation stats response
        remediation_stats_response = {
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
                    ]
                },
                "mttr_by_severity": {
                    "buckets": [
                        {"key": "Critical", "avg_remediation_days": {"value": 3.5}},
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

        # Set up mock to return different responses for different calls
        mock_opensearch_client.search.side_effect = [
            cve_response,
            remediation_stats_response,
        ]

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            # Step 1: Get CVE details
            cve_resp = await client.get("/vulnerabilities/cves/CVE-2024-1234")
            assert cve_resp.status_code == 200
            cve_data = cve_resp.json()
            assert cve_data["cve_id"] == "CVE-2024-1234"
            assert cve_data["affected_asset_count"] == 2

            # Step 2: Get remediation stats
            stats_resp = await client.get("/vulnerabilities/remediation/stats")
            assert stats_resp.status_code == 200
            stats_data = stats_resp.json()
            assert "total_open" in stats_data
            assert "remediated" in stats_data

    async def test_list_vulnerabilities_then_get_flow(
        self, client, mock_opensearch_client
    ):
        """Test flow: List vulnerabilities -> Get Sankey flow."""
        # Mock list vulnerabilities response
        list_response = {
            "hits": {
                "total": {"value": 3},
                "hits": [
                    {
                        "_source": {
                            "cve_id": "CVE-2024-1234",
                            "title": "Critical RCE",
                            "severity": "Critical",
                            "cvss_score": 9.8,
                        }
                    },
                    {
                        "_source": {
                            "cve_id": "CVE-2024-5678",
                            "title": "SQL Injection",
                            "severity": "High",
                            "cvss_score": 8.5,
                        }
                    },
                    {
                        "_source": {
                            "cve_id": "CVE-2024-9999",
                            "title": "XSS Flaw",
                            "severity": "Medium",
                            "cvss_score": 6.5,
                        }
                    },
                ],
            }
        }

        # Mock Sankey flow response
        flow_response = {
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
                                ]
                            },
                        },
                    ]
                }
            }
        }

        mock_opensearch_client.search.side_effect = [list_response, flow_response]

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            # Step 1: List vulnerabilities
            list_resp = await client.get("/vulnerabilities")
            assert list_resp.status_code == 200
            list_data = list_resp.json()
            assert list_data["total"] == 3
            assert len(list_data["data"]) == 3

            # Step 2: Get Sankey flow
            flow_resp = await client.get("/vulnerabilities/remediation/flow")
            assert flow_resp.status_code == 200
            flow_data = flow_resp.json()
            assert "nodes" in flow_data
            assert "links" in flow_data


class TestVulnerabilityErrorHandling:
    """Tests for error handling across vulnerability endpoints."""

    async def test_cve_not_found_returns_404(self, client, mock_opensearch_client):
        """Test that non-existent CVE returns 404."""
        mock_opensearch_client.search.return_value = {
            "hits": {"total": {"value": 0}, "hits": []}
        }

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/cves/CVE-9999-0000")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    async def test_list_vulnerabilities_opensearch_error(
        self, client, mock_opensearch_client
    ):
        """Test that OpenSearch errors are handled gracefully in list."""
        mock_opensearch_client.search.side_effect = Exception("Connection refused")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities")

        # Should return empty list, not 500
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["total"] == 0

    async def test_remediation_stats_opensearch_error(
        self, client, mock_opensearch_client
    ):
        """Test that OpenSearch errors are handled gracefully in remediation stats."""
        mock_opensearch_client.search.side_effect = Exception("Timeout")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/remediation/stats")

        # Should return empty stats, not 500
        assert response.status_code == 200
        data = response.json()
        assert data["total_open"] == 0
        assert data["remediated"] == 0

    async def test_remediation_flow_opensearch_error(
        self, client, mock_opensearch_client
    ):
        """Test that OpenSearch errors are handled gracefully in flow endpoint."""
        mock_opensearch_client.search.side_effect = Exception("Cluster unavailable")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/remediation/flow")

        # Should return empty flow, not 500
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "links" in data

    async def test_get_cve_opensearch_error_returns_500(
        self, client, mock_opensearch_client
    ):
        """Test that OpenSearch errors in get_cve return 500."""
        mock_opensearch_client.search.side_effect = Exception("Connection timeout")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/cves/CVE-2024-1234")

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


class TestVulnerabilityPagination:
    """Tests for pagination across vulnerability endpoints."""

    async def test_pagination_page_1(self, client, mock_opensearch_client):
        """Test pagination with page 1."""
        mock_opensearch_client.search.return_value = {
            "hits": {
                "total": {"value": 150},
                "hits": [
                    {"_source": {"cve_id": f"CVE-2024-{i:04d}"}}
                    for i in range(50)
                ],
            }
        }

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?page=1&page_size=50")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 50
        assert data["total"] == 150
        assert data["total_pages"] == 3

        # Verify correct offset was used
        call_args = mock_opensearch_client.search.call_args
        assert call_args[1]["body"]["from"] == 0
        assert call_args[1]["body"]["size"] == 50

    async def test_pagination_page_2(self, client, mock_opensearch_client):
        """Test pagination with page 2."""
        mock_opensearch_client.search.return_value = {
            "hits": {
                "total": {"value": 150},
                "hits": [
                    {"_source": {"cve_id": f"CVE-2024-{i:04d}"}}
                    for i in range(50, 100)
                ],
            }
        }

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?page=2&page_size=50")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2

        # Verify correct offset was used
        call_args = mock_opensearch_client.search.call_args
        assert call_args[1]["body"]["from"] == 50

    async def test_pagination_last_page(self, client, mock_opensearch_client):
        """Test pagination with last page (partial results)."""
        mock_opensearch_client.search.return_value = {
            "hits": {
                "total": {"value": 125},
                "hits": [
                    {"_source": {"cve_id": f"CVE-2024-{i:04d}"}}
                    for i in range(25)  # Only 25 results on last page
                ],
            }
        }

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?page=3&page_size=50")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 3
        assert data["total_pages"] == 3  # ceil(125/50) = 3


class TestVulnerabilityFiltering:
    """Tests for filtering across vulnerability endpoints."""

    async def test_filter_by_severity_critical(self, client, mock_opensearch_client):
        """Test filtering vulnerabilities by Critical severity."""
        mock_opensearch_client.search.return_value = {
            "hits": {
                "total": {"value": 15},
                "hits": [
                    {
                        "_source": {
                            "cve_id": "CVE-2024-0001",
                            "severity": "Critical",
                            "cvss_score": 9.8,
                        }
                    }
                ],
            }
        }

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?severity=Critical")

        assert response.status_code == 200

        # Verify the query included severity filter
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert {"term": {"severity": "Critical"}} in query["bool"]["must"]

    async def test_filter_by_cvss_range(self, client, mock_opensearch_client):
        """Test filtering vulnerabilities by CVSS score range."""
        mock_opensearch_client.search.return_value = {
            "hits": {
                "total": {"value": 45},
                "hits": [
                    {
                        "_source": {
                            "cve_id": "CVE-2024-0001",
                            "cvss_score": 8.0,
                        }
                    }
                ],
            }
        }

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?cvss_min=7.0&cvss_max=9.0")

        assert response.status_code == 200

        # Verify the query included CVSS range filters
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        must_clauses = query["bool"]["must"]
        assert {"range": {"cvss_score": {"gte": 7.0}}} in must_clauses
        assert {"range": {"cvss_score": {"lte": 9.0}}} in must_clauses

    async def test_filter_by_exploit_available(self, client, mock_opensearch_client):
        """Test filtering vulnerabilities by exploit availability."""
        mock_opensearch_client.search.return_value = {
            "hits": {
                "total": {"value": 30},
                "hits": [
                    {
                        "_source": {
                            "cve_id": "CVE-2024-0001",
                            "exploit_available": True,
                        }
                    }
                ],
            }
        }

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?exploit_available=true")

        assert response.status_code == 200

        # Verify the query included exploit filter
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert {"term": {"exploit_available": True}} in query["bool"]["must"]

    async def test_search_by_cve_id(self, client, mock_opensearch_client):
        """Test searching vulnerabilities by CVE ID."""
        mock_opensearch_client.search.return_value = {
            "hits": {
                "total": {"value": 1},
                "hits": [
                    {
                        "_source": {
                            "cve_id": "CVE-2024-1234",
                            "title": "Test Vulnerability",
                        }
                    }
                ],
            }
        }

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?search=CVE-2024-1234")

        assert response.status_code == 200

        # Verify the query included search
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        search_clause = query["bool"]["must"][0]
        assert "bool" in search_clause
        assert "should" in search_clause["bool"]

    async def test_combined_filters(self, client, mock_opensearch_client):
        """Test combining multiple filters."""
        mock_opensearch_client.search.return_value = {
            "hits": {
                "total": {"value": 5},
                "hits": [
                    {
                        "_source": {
                            "cve_id": "CVE-2024-0001",
                            "severity": "Critical",
                            "cvss_score": 9.5,
                            "exploit_available": True,
                        }
                    }
                ],
            }
        }

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get(
                "/vulnerabilities?severity=Critical&cvss_min=9.0&exploit_available=true"
            )

        assert response.status_code == 200

        # Verify all filters are applied
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        must_clauses = query["bool"]["must"]

        assert {"term": {"severity": "Critical"}} in must_clauses
        assert {"range": {"cvss_score": {"gte": 9.0}}} in must_clauses
        assert {"term": {"exploit_available": True}} in must_clauses


class TestVulnerabilitySummary:
    """Tests for vulnerability summary endpoint integration."""

    async def test_summary_endpoint_success(self, client, mock_opensearch_client):
        """Test vulnerability summary endpoint returns correct data."""
        mock_opensearch_client.search.return_value = {
            "aggregations": {
                "by_severity": {
                    "buckets": [
                        {"key": "Critical", "doc_count": 15},
                        {"key": "High", "doc_count": 45},
                        {"key": "Medium", "doc_count": 80},
                        {"key": "Low", "doc_count": 20},
                    ]
                },
                "by_exposure": {
                    "buckets": [
                        {"key": "External", "doc_count": 30},
                        {"key": "Internal", "doc_count": 130},
                    ]
                },
                "kev_count": {"doc_count": 12},
                "exploit_available_count": {"doc_count": 25},
                "avg_cvss": {"value": 7.35},
                "top_cves": {
                    "hits": {
                        "hits": [
                            {
                                "_source": {
                                    "cve_id": "CVE-2024-0001",
                                    "title": "Top Critical",
                                    "severity": "Critical",
                                    "cvss_score": 10.0,
                                }
                            }
                        ]
                    }
                },
            }
        }

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/summary")

        assert response.status_code == 200
        data = response.json()

        assert data["by_severity"]["Critical"] == 15
        assert data["by_severity"]["High"] == 45
        assert data["kev_count"] == 12
        assert data["exploit_available_count"] == 25
        assert data["avg_cvss"] == 7.35
        assert len(data["top_cves"]) == 1

    async def test_summary_endpoint_error_handling(
        self, client, mock_opensearch_client
    ):
        """Test summary endpoint handles errors gracefully."""
        mock_opensearch_client.search.side_effect = Exception("OpenSearch error")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/summary")

        assert response.status_code == 200
        data = response.json()

        # Should return empty summary
        assert data["by_severity"] == {}
        assert data["kev_count"] == 0
        assert data["avg_cvss"] == 0.0
