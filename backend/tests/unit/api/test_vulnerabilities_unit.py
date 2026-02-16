"""
Unit tests for Vulnerabilities API endpoints.

Following TDD: Tests for query building, filtering, aggregation, and error handling.
Uses mocking for OpenSearch client to isolate API logic.
"""
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from fastapi import HTTPException

from src.main import app
from src.api.vulnerabilities import (
    get_vulnerability_summary,
    get_cve,
    VulnerabilityList,
    VulnerabilitySummary,
)


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
def sample_vulnerability_hits():
    """Sample vulnerability search hits."""
    return {
        "hits": {
            "total": {"value": 3},
            "hits": [
                {
                    "_source": {
                        "cve_id": "CVE-2024-1234",
                        "title": "Critical RCE Vulnerability",
                        "severity": "Critical",
                        "cvss_score": 9.8,
                        "epss_score": 0.95,
                        "exploit_available": True,
                        "asset_id": "ASSET-001",
                    }
                },
                {
                    "_source": {
                        "cve_id": "CVE-2024-5678",
                        "title": "SQL Injection Flaw",
                        "severity": "High",
                        "cvss_score": 8.5,
                        "epss_score": 0.75,
                        "exploit_available": True,
                        "asset_id": "ASSET-002",
                    }
                },
                {
                    "_source": {
                        "cve_id": "CVE-2024-9999",
                        "title": "Buffer Overflow",
                        "severity": "Medium",
                        "cvss_score": 6.5,
                        "epss_score": 0.30,
                        "exploit_available": False,
                        "asset_id": "ASSET-003",
                    }
                },
            ],
        }
    }


@pytest.fixture
def sample_summary_response():
    """Sample aggregation response for summary endpoint."""
    return {
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
                                "exploit_available": True,
                            }
                        },
                        {
                            "_source": {
                                "cve_id": "CVE-2024-0002",
                                "title": "Second Critical",
                                "severity": "Critical",
                                "cvss_score": 9.9,
                                "exploit_available": True,
                            }
                        },
                    ]
                }
            },
        }
    }


# ============================================================================
# Tests for list_vulnerabilities() - via HTTP client
# ============================================================================


class TestListVulnerabilities:
    """Tests for the list_vulnerabilities endpoint via HTTP."""

    @pytest.mark.asyncio
    async def test_default_list_no_filters(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test default list with no filters returns match_all query."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

        # Verify search was called
        mock_opensearch_client.search.assert_called_once()
        call_args = mock_opensearch_client.search.call_args
        assert call_args[1]["index"] == "ctem-findings-v1"
        # Default query should be match_all
        assert call_args[1]["body"]["query"] == {"match_all": {}}
        assert call_args[1]["body"]["sort"] == [{"cvss_score": "desc"}]

    @pytest.mark.asyncio
    async def test_severity_filter_critical(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test filtering by Critical severity."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?severity=Critical")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert query["bool"]["must"] == [{"term": {"severity": "Critical"}}]

    @pytest.mark.asyncio
    async def test_severity_filter_high(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test filtering by High severity."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?severity=High")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert {"term": {"severity": "High"}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_severity_filter_medium(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test filtering by Medium severity."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?severity=Medium")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_severity_filter_low(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test filtering by Low severity."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?severity=Low")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_cvss_min_filter(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test filtering by minimum CVSS score."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?cvss_min=7.0")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert {"range": {"cvss_score": {"gte": 7.0}}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_cvss_max_filter(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test filtering by maximum CVSS score."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?cvss_max=9.0")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert {"range": {"cvss_score": {"lte": 9.0}}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_cvss_range_filters(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test filtering by CVSS range (both min and max)."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?cvss_min=5.0&cvss_max=8.0")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        must_clauses = query["bool"]["must"]
        assert {"range": {"cvss_score": {"gte": 5.0}}} in must_clauses
        assert {"range": {"cvss_score": {"lte": 8.0}}} in must_clauses

    @pytest.mark.asyncio
    async def test_epss_min_filter(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test filtering by minimum EPSS score."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?epss_min=0.5")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert {"range": {"epss_score": {"gte": 0.5}}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_epss_max_filter(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test filtering by maximum EPSS score."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?epss_max=0.9")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_epss_range_filters(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test filtering by EPSS range (both min and max)."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?epss_min=0.3&epss_max=0.8")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_exploit_available_true_filter(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test filtering by exploit_available=True."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?exploit_available=true")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert {"term": {"exploit_available": True}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_exploit_available_false_filter(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test filtering by exploit_available=False."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?exploit_available=false")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_kev_filter_true(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test filtering by KEV=True (Known Exploited Vulnerabilities)."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?kev=true")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_kev_filter_false(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test filtering by KEV=False."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?kev=false")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_search_by_cve_id(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test search by CVE ID with wildcard."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?search=CVE-2024-1234")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        search_clause = query["bool"]["must"][0]

        assert search_clause["bool"]["should"][0] == {
            "wildcard": {"cve_id": "*CVE-2024-1234*"}
        }
        assert search_clause["bool"]["should"][1] == {"match": {"title": "CVE-2024-1234"}}

    @pytest.mark.asyncio
    async def test_search_by_title(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test search by title text."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?search=buffer%20overflow")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_search_lowercase_converted_to_uppercase(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test that lowercase CVE search is converted to uppercase."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?search=cve-2024")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        search_clause = query["bool"]["must"][0]
        # CVE wildcard should be uppercased
        assert search_clause["bool"]["should"][0]["wildcard"]["cve_id"] == "*CVE-2024*"

    @pytest.mark.asyncio
    async def test_pagination_page_1(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test pagination with page 1."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?page=1&page_size=50")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 50

        call_args = mock_opensearch_client.search.call_args
        assert call_args[1]["body"]["from"] == 0
        assert call_args[1]["body"]["size"] == 50

    @pytest.mark.asyncio
    async def test_pagination_page_2(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test pagination with page 2."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?page=2&page_size=50")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        assert call_args[1]["body"]["from"] == 50  # (2-1) * 50

    @pytest.mark.asyncio
    async def test_pagination_custom_page_size(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test pagination with custom page size."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?page=3&page_size=25")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        assert call_args[1]["body"]["from"] == 50  # (3-1) * 25
        assert call_args[1]["body"]["size"] == 25

    @pytest.mark.asyncio
    async def test_sorting_cvss_descending(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test that results are sorted by CVSS score descending."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        assert call_args[1]["body"]["sort"] == [{"cvss_score": "desc"}]

    @pytest.mark.asyncio
    async def test_combined_filters(
        self, client, mock_opensearch_client, sample_vulnerability_hits
    ):
        """Test multiple filters combined."""
        mock_opensearch_client.search.return_value = sample_vulnerability_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get(
                "/vulnerabilities?severity=Critical&cvss_min=9.0&cvss_max=10.0&exploit_available=true"
            )

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        must_clauses = query["bool"]["must"]

        assert {"term": {"severity": "Critical"}} in must_clauses
        assert {"range": {"cvss_score": {"gte": 9.0}}} in must_clauses
        assert {"range": {"cvss_score": {"lte": 10.0}}} in must_clauses
        assert {"term": {"exploit_available": True}} in must_clauses

    @pytest.mark.asyncio
    async def test_empty_results(self, client, mock_opensearch_client):
        """Test handling of empty search results."""
        empty_response = {"hits": {"total": {"value": 0}, "hits": []}}
        mock_opensearch_client.search.return_value = empty_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["data"] == []
        assert data["total_pages"] == 0

    @pytest.mark.asyncio
    async def test_total_pages_calculation(self, client, mock_opensearch_client):
        """Test correct total_pages calculation."""
        response_data = {"hits": {"total": {"value": 125}, "hits": []}}
        mock_opensearch_client.search.return_value = response_data

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?page_size=50")

        assert response.status_code == 200
        data = response.json()
        # 125 / 50 = 2.5, rounded up = 3 pages
        assert data["total_pages"] == 3

    @pytest.mark.asyncio
    async def test_total_pages_exact_division(self, client, mock_opensearch_client):
        """Test total_pages when total divides evenly by page_size."""
        response_data = {"hits": {"total": {"value": 100}, "hits": []}}
        mock_opensearch_client.search.return_value = response_data

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities?page_size=50")

        assert response.status_code == 200
        data = response.json()
        assert data["total_pages"] == 2

    @pytest.mark.asyncio
    async def test_exception_returns_empty_list(self, client, mock_opensearch_client):
        """Test that exceptions return empty list instead of crashing."""
        mock_opensearch_client.search.side_effect = Exception("OpenSearch connection failed")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities")

        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["total"] == 0


# ============================================================================
# Tests for get_vulnerability_summary()
# ============================================================================


class TestGetVulnerabilitySummary:
    """Tests for the get_vulnerability_summary endpoint."""

    @pytest.mark.asyncio
    async def test_by_severity_aggregation(self, mock_opensearch_client, sample_summary_response):
        """Test that by_severity aggregation is correctly parsed."""
        mock_opensearch_client.search.return_value = sample_summary_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_vulnerability_summary()

        assert result.by_severity == {
            "Critical": 15,
            "High": 45,
            "Medium": 80,
            "Low": 20,
        }

    @pytest.mark.asyncio
    async def test_by_exposure_aggregation(self, mock_opensearch_client, sample_summary_response):
        """Test that by_exposure aggregation is correctly parsed."""
        mock_opensearch_client.search.return_value = sample_summary_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_vulnerability_summary()

        assert result.by_exposure == {"External": 30, "Internal": 130}

    @pytest.mark.asyncio
    async def test_kev_count_aggregation(self, mock_opensearch_client, sample_summary_response):
        """Test that kev_count filter aggregation is correctly parsed."""
        mock_opensearch_client.search.return_value = sample_summary_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_vulnerability_summary()

        assert result.kev_count == 12

    @pytest.mark.asyncio
    async def test_exploit_available_count(self, mock_opensearch_client, sample_summary_response):
        """Test that exploit_available_count is correctly parsed."""
        mock_opensearch_client.search.return_value = sample_summary_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_vulnerability_summary()

        assert result.exploit_available_count == 25

    @pytest.mark.asyncio
    async def test_avg_cvss_calculation(self, mock_opensearch_client, sample_summary_response):
        """Test that avg_cvss is correctly calculated and rounded."""
        mock_opensearch_client.search.return_value = sample_summary_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_vulnerability_summary()

        assert result.avg_cvss == 7.35

    @pytest.mark.asyncio
    async def test_avg_cvss_rounding(self, mock_opensearch_client):
        """Test that avg_cvss is rounded to 2 decimal places."""
        response = {
            "aggregations": {
                "by_severity": {"buckets": []},
                "by_exposure": {"buckets": []},
                "kev_count": {"doc_count": 0},
                "exploit_available_count": {"doc_count": 0},
                "avg_cvss": {"value": 7.3567891},
                "top_cves": {"hits": {"hits": []}},
            }
        }
        mock_opensearch_client.search.return_value = response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_vulnerability_summary()

        assert result.avg_cvss == 7.36  # Rounded

    @pytest.mark.asyncio
    async def test_avg_cvss_null_handling(self, mock_opensearch_client):
        """Test that null avg_cvss value defaults to 0.0."""
        response = {
            "aggregations": {
                "by_severity": {"buckets": []},
                "by_exposure": {"buckets": []},
                "kev_count": {"doc_count": 0},
                "exploit_available_count": {"doc_count": 0},
                "avg_cvss": {"value": None},
                "top_cves": {"hits": {"hits": []}},
            }
        }
        mock_opensearch_client.search.return_value = response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_vulnerability_summary()

        assert result.avg_cvss == 0.0

    @pytest.mark.asyncio
    async def test_top_cves_extraction(self, mock_opensearch_client, sample_summary_response):
        """Test that top_cves top_hits are correctly extracted."""
        mock_opensearch_client.search.return_value = sample_summary_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_vulnerability_summary()

        assert len(result.top_cves) == 2
        assert result.top_cves[0]["cve_id"] == "CVE-2024-0001"
        assert result.top_cves[0]["cvss_score"] == 10.0
        assert result.top_cves[1]["cve_id"] == "CVE-2024-0002"

    @pytest.mark.asyncio
    async def test_aggregation_query_structure(self, mock_opensearch_client, sample_summary_response):
        """Test that the aggregation query is correctly structured."""
        mock_opensearch_client.search.return_value = sample_summary_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_vulnerability_summary()

        call_args = mock_opensearch_client.search.call_args
        body = call_args[1]["body"]

        assert body["size"] == 0  # No hits needed for aggregation
        assert "aggs" in body
        assert "by_severity" in body["aggs"]
        assert "by_exposure" in body["aggs"]
        assert "kev_count" in body["aggs"]
        assert "exploit_available_count" in body["aggs"]
        assert "avg_cvss" in body["aggs"]
        assert "top_cves" in body["aggs"]

    @pytest.mark.asyncio
    async def test_top_cves_sort_order(self, mock_opensearch_client, sample_summary_response):
        """Test that top_cves are sorted by CVSS descending."""
        mock_opensearch_client.search.return_value = sample_summary_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_vulnerability_summary()

        call_args = mock_opensearch_client.search.call_args
        top_cves_agg = call_args[1]["body"]["aggs"]["top_cves"]["top_hits"]

        assert top_cves_agg["sort"] == [{"cvss_score": "desc"}]
        assert top_cves_agg["size"] == 5

    @pytest.mark.asyncio
    async def test_error_returns_empty_summary(self, mock_opensearch_client):
        """Test that errors return empty summary instead of crashing."""
        mock_opensearch_client.search.side_effect = Exception("OpenSearch error")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_vulnerability_summary()

        assert result.by_severity == {}
        assert result.by_exposure == {}
        assert result.kev_count == 0
        assert result.exploit_available_count == 0
        assert result.avg_cvss == 0.0
        assert result.top_cves == []

    @pytest.mark.asyncio
    async def test_missing_exposure_buckets(self, mock_opensearch_client):
        """Test handling of missing by_exposure buckets."""
        response = {
            "aggregations": {
                "by_severity": {"buckets": [{"key": "Critical", "doc_count": 10}]},
                # by_exposure missing or empty
                "kev_count": {"doc_count": 5},
                "exploit_available_count": {"doc_count": 5},
                "avg_cvss": {"value": 8.0},
                "top_cves": {"hits": {"hits": []}},
            }
        }
        mock_opensearch_client.search.return_value = response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_vulnerability_summary()

        # Should handle missing by_exposure gracefully
        assert result.by_exposure == {}


# ============================================================================
# Tests for get_cve()
# ============================================================================


class TestGetCVE:
    """Tests for the get_cve endpoint."""

    @pytest.mark.asyncio
    async def test_exact_cve_match(self, mock_opensearch_client):
        """Test exact CVE ID match returns full details."""
        response = {
            "hits": {
                "total": {"value": 2},
                "hits": [
                    {
                        "_source": {
                            "cve_id": "CVE-2024-1234",
                            "title": "Critical RCE",
                            "severity": "Critical",
                            "cvss_score": 9.8,
                            "asset_id": "ASSET-001",
                        }
                    },
                    {
                        "_source": {
                            "cve_id": "CVE-2024-1234",
                            "title": "Critical RCE",
                            "severity": "Critical",
                            "cvss_score": 9.8,
                            "asset_id": "ASSET-002",
                        }
                    },
                ],
            }
        }
        mock_opensearch_client.search.return_value = response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_cve("CVE-2024-1234")

        # Verify the CVE detail is returned
        assert result["cve_id"] == "CVE-2024-1234"
        assert result["title"] == "Critical RCE"
        assert result["severity"] == "Critical"

    @pytest.mark.asyncio
    async def test_affected_asset_calculation(self, mock_opensearch_client):
        """Test that affected_asset_count is calculated from findings."""
        response = {
            "hits": {
                "total": {"value": 3},
                "hits": [
                    {
                        "_source": {
                            "cve_id": "CVE-2024-5678",
                            "title": "SQL Injection",
                            "asset_id": "ASSET-001",
                        }
                    },
                    {
                        "_source": {
                            "cve_id": "CVE-2024-5678",
                            "title": "SQL Injection",
                            "asset_id": "ASSET-002",
                        }
                    },
                    {
                        "_source": {
                            "cve_id": "CVE-2024-5678",
                            "title": "SQL Injection",
                            "asset_id": "ASSET-001",  # Duplicate
                        }
                    },
                ],
            }
        }
        mock_opensearch_client.search.return_value = response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_cve("CVE-2024-5678")

        # Should have 2 unique affected assets (ASSET-001 and ASSET-002)
        assert result["affected_asset_count"] == 2
        assert set(result["affected_assets"]) == {"ASSET-001", "ASSET-002"}

    @pytest.mark.asyncio
    async def test_affected_assets_handles_missing_asset_id(self, mock_opensearch_client):
        """Test that findings without asset_id are handled."""
        response = {
            "hits": {
                "total": {"value": 2},
                "hits": [
                    {
                        "_source": {
                            "cve_id": "CVE-2024-9999",
                            "title": "Buffer Overflow",
                            "asset_id": "ASSET-001",
                        }
                    },
                    {
                        "_source": {
                            "cve_id": "CVE-2024-9999",
                            "title": "Buffer Overflow",
                            # No asset_id
                        }
                    },
                ],
            }
        }
        mock_opensearch_client.search.return_value = response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_cve("CVE-2024-9999")

        # Should only count the one with asset_id
        assert result["affected_asset_count"] == 1
        assert "ASSET-001" in result["affected_assets"]

    @pytest.mark.asyncio
    async def test_404_handling_cve_not_found(self, mock_opensearch_client):
        """Test 404 response when CVE is not found."""
        response = {"hits": {"total": {"value": 0}, "hits": []}}
        mock_opensearch_client.search.return_value = response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            with pytest.raises(HTTPException) as exc_info:
                await get_cve("CVE-9999-0000")

        assert exc_info.value.status_code == 404
        assert "CVE-9999-0000 not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_500_error_handling(self, mock_opensearch_client):
        """Test 500 error when OpenSearch fails."""
        mock_opensearch_client.search.side_effect = Exception("Connection timeout")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            with pytest.raises(HTTPException) as exc_info:
                await get_cve("CVE-2024-1234")

        assert exc_info.value.status_code == 500
        assert "Connection timeout" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_query_uses_term_match(self, mock_opensearch_client):
        """Test that query uses term match for CVE ID."""
        response = {
            "hits": {
                "total": {"value": 1},
                "hits": [{"_source": {"cve_id": "CVE-2024-1234", "title": "Test"}}],
            }
        }
        mock_opensearch_client.search.return_value = response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_cve("CVE-2024-1234")

        call_args = mock_opensearch_client.search.call_args
        assert call_args[1]["body"]["query"] == {"term": {"cve_id": "CVE-2024-1234"}}
        assert call_args[1]["body"]["size"] == 10

    @pytest.mark.asyncio
    async def test_http_exception_not_wrapped(self, mock_opensearch_client):
        """Test that HTTPException is re-raised without wrapping."""
        response = {"hits": {"total": {"value": 0}, "hits": []}}
        mock_opensearch_client.search.return_value = response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            with pytest.raises(HTTPException) as exc_info:
                await get_cve("CVE-NOTFOUND")

        # Should be 404, not 500
        assert exc_info.value.status_code == 404
