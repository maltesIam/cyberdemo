"""
Unit tests for Threats API endpoints.

Following TDD: Tests for IOC listing, filtering, geo aggregation, actor lookup, and MITRE coverage.
Uses mocking for OpenSearch client to isolate API logic.
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.api.threats import (
    list_iocs,
    get_ioc,
    get_threat_map,
    get_actor_iocs,
    get_mitre_coverage,
    IOCList,
    GeoMap,
    MitreMap,
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
def sample_ioc_hits():
    """Sample IOC search hits."""
    return {
        "hits": {
            "total": {"value": 3},
            "hits": [
                {
                    "_source": {
                        "indicator_value": "192.168.1.100",
                        "indicator_type": "ip",
                        "verdict": "malicious",
                        "confidence": 95,
                        "source": "AlienVault",
                        "last_seen": "2024-01-15T10:30:00Z",
                        "labels": ["APT29"],
                        "tags": ["c2"],
                    }
                },
                {
                    "_source": {
                        "indicator_value": "evil-domain.com",
                        "indicator_type": "domain",
                        "verdict": "malicious",
                        "confidence": 85,
                        "source": "ThreatFox",
                        "last_seen": "2024-01-14T08:00:00Z",
                        "labels": ["Cobalt Strike"],
                        "tags": ["phishing"],
                    }
                },
                {
                    "_source": {
                        "indicator_value": "abc123def456",
                        "indicator_type": "filehash",
                        "verdict": "suspicious",
                        "confidence": 70,
                        "source": "VirusTotal",
                        "last_seen": "2024-01-13T14:00:00Z",
                        "malware_family": "Emotet",
                    }
                },
            ],
        }
    }


@pytest.fixture
def sample_geo_response():
    """Sample geo aggregation response for threat map."""
    return {
        "hits": {"total": {"value": 250}},
        "aggregations": {
            "by_source": {
                "buckets": [
                    {"key": "Russia", "doc_count": 85},
                    {"key": "China", "doc_count": 65},
                    {"key": "North Korea", "doc_count": 45},
                    {"key": "Iran", "doc_count": 30},
                    {"key": "USA", "doc_count": 25},
                ]
            }
        },
    }


@pytest.fixture
def sample_mitre_response():
    """Sample MITRE ATT&CK aggregation response."""
    return {
        "hits": {"total": {"value": 500}},
        "aggregations": {
            "by_technique": {
                "buckets": [
                    {
                        "key": "T1059.001",
                        "doc_count": 120,
                        "technique_name": {
                            "buckets": [{"key": "PowerShell", "doc_count": 120}]
                        },
                        "by_severity": {
                            "buckets": [
                                {"key": "Critical", "doc_count": 30},
                                {"key": "High", "doc_count": 60},
                                {"key": "Medium", "doc_count": 30},
                            ]
                        },
                    },
                    {
                        "key": "T1053.005",
                        "doc_count": 80,
                        "technique_name": {
                            "buckets": [{"key": "Scheduled Task", "doc_count": 80}]
                        },
                        "by_severity": {
                            "buckets": [
                                {"key": "High", "doc_count": 50},
                                {"key": "Medium", "doc_count": 30},
                            ]
                        },
                    },
                    {
                        "key": "T1003.001",
                        "doc_count": 50,
                        "technique_name": {
                            "buckets": []  # Missing name
                        },
                        "by_severity": {
                            "buckets": [{"key": "Critical", "doc_count": 50}]
                        },
                    },
                ]
            }
        },
    }


# ============================================================================
# Tests for list_iocs() - Using HTTP Client for proper Query parameter handling
# ============================================================================


class TestListIOCs:
    """Tests for the list_iocs endpoint using HTTP client."""

    @pytest.fixture
    async def client(self):
        """Create async test client."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_default_list_no_filters(self, client, mock_opensearch_client, sample_ioc_hits):
        """Test default list with no filters returns match_all query."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/threats")

        assert response.status_code == 200
        data = response.json()

        # Verify search was called with match_all query
        mock_opensearch_client.search.assert_called_once()
        call_args = mock_opensearch_client.search.call_args
        assert call_args[1]["index"] == "threat-intel-v1"
        assert call_args[1]["body"]["query"] == {"match_all": {}}
        assert call_args[1]["body"]["from"] == 0
        assert call_args[1]["body"]["size"] == 50
        assert call_args[1]["body"]["sort"] == [{"last_seen": "desc"}]

        # Verify response
        assert data["total"] == 3
        assert len(data["data"]) == 3
        assert data["page"] == 1
        assert data["page_size"] == 50

    @pytest.mark.asyncio
    async def test_ioc_type_filter_ip(self, client, mock_opensearch_client, sample_ioc_hits):
        """Test filtering by ioc_type=ip."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/threats?ioc_type=ip")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert {"term": {"indicator_type": "ip"}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_ioc_type_filter_domain(self, client, mock_opensearch_client, sample_ioc_hits):
        """Test filtering by ioc_type=domain."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/threats?ioc_type=domain")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert {"term": {"indicator_type": "domain"}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_ioc_type_filter_filehash(self, client, mock_opensearch_client, sample_ioc_hits):
        """Test filtering by ioc_type=filehash."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/threats?ioc_type=filehash")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert {"term": {"indicator_type": "filehash"}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_verdict_filter_malicious(self, client, mock_opensearch_client, sample_ioc_hits):
        """Test filtering by verdict=malicious."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/threats?verdict=malicious")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert {"term": {"verdict": "malicious"}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_verdict_filter_suspicious(self, client, mock_opensearch_client, sample_ioc_hits):
        """Test filtering by verdict=suspicious."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/threats?verdict=suspicious")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert {"term": {"verdict": "suspicious"}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_verdict_filter_benign(self, client, mock_opensearch_client, sample_ioc_hits):
        """Test filtering by verdict=benign."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/threats?verdict=benign")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert {"term": {"verdict": "benign"}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_risk_min_filter(self, client, mock_opensearch_client, sample_ioc_hits):
        """Test filtering by minimum risk/confidence score."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/threats?risk_min=80")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert {"range": {"confidence": {"gte": 80}}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_risk_min_zero(self, client, mock_opensearch_client, sample_ioc_hits):
        """Test filtering by risk_min=0 (edge case)."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/threats?risk_min=0")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert {"range": {"confidence": {"gte": 0}}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_search_by_indicator_value(self, client, mock_opensearch_client, sample_ioc_hits):
        """Test search by indicator_value with wildcard."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/threats?search=192.168")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert {"wildcard": {"indicator_value": "*192.168*"}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_search_domain_pattern(self, client, mock_opensearch_client, sample_ioc_hits):
        """Test search by domain pattern."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/threats?search=evil")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        assert {"wildcard": {"indicator_value": "*evil*"}} in query["bool"]["must"]

    @pytest.mark.asyncio
    async def test_pagination_page_1(self, client, mock_opensearch_client, sample_ioc_hits):
        """Test pagination with page 1."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/threats?page=1&page_size=50")

        assert response.status_code == 200
        data = response.json()
        call_args = mock_opensearch_client.search.call_args
        assert call_args[1]["body"]["from"] == 0
        assert call_args[1]["body"]["size"] == 50
        assert data["page"] == 1
        assert data["page_size"] == 50

    @pytest.mark.asyncio
    async def test_pagination_page_3(self, client, mock_opensearch_client, sample_ioc_hits):
        """Test pagination with page 3."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/threats?page=3&page_size=25")

        assert response.status_code == 200
        data = response.json()
        call_args = mock_opensearch_client.search.call_args
        assert call_args[1]["body"]["from"] == 50  # (3-1) * 25
        assert call_args[1]["body"]["size"] == 25
        assert data["page"] == 3
        assert data["page_size"] == 25

    @pytest.mark.asyncio
    async def test_combined_filters(self, client, mock_opensearch_client, sample_ioc_hits):
        """Test multiple filters combined."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get(
                "/threats?ioc_type=ip&verdict=malicious&risk_min=90&search=192"
            )

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        must_clauses = query["bool"]["must"]

        assert {"term": {"indicator_type": "ip"}} in must_clauses
        assert {"term": {"verdict": "malicious"}} in must_clauses
        assert {"range": {"confidence": {"gte": 90}}} in must_clauses
        assert {"wildcard": {"indicator_value": "*192*"}} in must_clauses

    @pytest.mark.asyncio
    async def test_empty_results(self, client, mock_opensearch_client):
        """Test handling of empty search results."""
        empty_response = {"hits": {"total": {"value": 0}, "hits": []}}
        mock_opensearch_client.search.return_value = empty_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/threats")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["data"] == []
        assert data["total_pages"] == 0

    @pytest.mark.asyncio
    async def test_total_pages_calculation(self, client, mock_opensearch_client):
        """Test correct total_pages calculation."""
        response_data = {"hits": {"total": {"value": 175}, "hits": []}}
        mock_opensearch_client.search.return_value = response_data

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/threats?page_size=50")

        assert response.status_code == 200
        data = response.json()
        # 175 / 50 = 3.5, rounded up = 4 pages
        assert data["total_pages"] == 4

    @pytest.mark.asyncio
    async def test_sorting_by_last_seen(self, client, mock_opensearch_client, sample_ioc_hits):
        """Test that results are sorted by last_seen descending."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/threats")

        assert response.status_code == 200
        call_args = mock_opensearch_client.search.call_args
        assert call_args[1]["body"]["sort"] == [{"last_seen": "desc"}]

    @pytest.mark.asyncio
    async def test_exception_returns_empty_list(self, client, mock_opensearch_client):
        """Test that exceptions return empty list instead of crashing."""
        mock_opensearch_client.search.side_effect = Exception("OpenSearch error")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/threats")

        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["total"] == 0
        assert data["total_pages"] == 0


# ============================================================================
# Tests for get_ioc()
# ============================================================================


class TestGetIOC:
    """Tests for the get_ioc endpoint."""

    @pytest.mark.asyncio
    async def test_indicator_value_exact_match(self, mock_opensearch_client):
        """Test exact indicator_value match returns IOC details."""
        response = {
            "hits": {
                "total": {"value": 1},
                "hits": [
                    {
                        "_source": {
                            "indicator_value": "192.168.1.100",
                            "indicator_type": "ip",
                            "verdict": "malicious",
                            "confidence": 95,
                            "source": "AlienVault",
                            "labels": ["APT29"],
                        }
                    }
                ],
            }
        }
        mock_opensearch_client.search.return_value = response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_ioc("192.168.1.100")

        # Verify query structure
        call_args = mock_opensearch_client.search.call_args
        assert call_args[1]["body"]["query"] == {"term": {"indicator_value": "192.168.1.100"}}

        # Verify response
        assert result["indicator_value"] == "192.168.1.100"
        assert result["indicator_type"] == "ip"
        assert result["verdict"] == "malicious"
        assert result["confidence"] == 95

    @pytest.mark.asyncio
    async def test_get_domain_ioc(self, mock_opensearch_client):
        """Test getting a domain IOC."""
        response = {
            "hits": {
                "total": {"value": 1},
                "hits": [
                    {
                        "_source": {
                            "indicator_value": "malware.evil.com",
                            "indicator_type": "domain",
                            "verdict": "malicious",
                        }
                    }
                ],
            }
        }
        mock_opensearch_client.search.return_value = response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_ioc("malware.evil.com")

        assert result["indicator_value"] == "malware.evil.com"
        assert result["indicator_type"] == "domain"

    @pytest.mark.asyncio
    async def test_get_filehash_ioc(self, mock_opensearch_client):
        """Test getting a filehash IOC."""
        sha256 = "abc123def456789012345678901234567890123456789012345678901234"
        response = {
            "hits": {
                "total": {"value": 1},
                "hits": [
                    {
                        "_source": {
                            "indicator_value": sha256,
                            "indicator_type": "filehash",
                            "verdict": "malicious",
                            "malware_family": "Emotet",
                        }
                    }
                ],
            }
        }
        mock_opensearch_client.search.return_value = response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_ioc(sha256)

        assert result["indicator_value"] == sha256
        assert result["malware_family"] == "Emotet"

    @pytest.mark.asyncio
    async def test_404_handling_ioc_not_found(self, mock_opensearch_client):
        """Test 404 response when IOC is not found."""
        response = {"hits": {"total": {"value": 0}, "hits": []}}
        mock_opensearch_client.search.return_value = response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            with pytest.raises(HTTPException) as exc_info:
                await get_ioc("nonexistent-ioc")

        assert exc_info.value.status_code == 404
        assert "nonexistent-ioc not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_500_error_handling(self, mock_opensearch_client):
        """Test 500 error when OpenSearch fails."""
        mock_opensearch_client.search.side_effect = Exception("Connection refused")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            with pytest.raises(HTTPException) as exc_info:
                await get_ioc("192.168.1.100")

        assert exc_info.value.status_code == 500
        assert "Connection refused" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_http_exception_not_wrapped(self, mock_opensearch_client):
        """Test that HTTPException is re-raised without wrapping."""
        response = {"hits": {"total": {"value": 0}, "hits": []}}
        mock_opensearch_client.search.return_value = response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            with pytest.raises(HTTPException) as exc_info:
                await get_ioc("not-found")

        # Should be 404, not 500
        assert exc_info.value.status_code == 404


# ============================================================================
# Tests for get_threat_map()
# ============================================================================


class TestGetThreatMap:
    """Tests for the get_threat_map endpoint."""

    @pytest.mark.asyncio
    async def test_malicious_verdict_filtering(self, mock_opensearch_client, sample_geo_response):
        """Test that only malicious IOCs are included in the map."""
        mock_opensearch_client.search.return_value = sample_geo_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_threat_map()

        call_args = mock_opensearch_client.search.call_args
        body = call_args[1]["body"]
        assert body["query"] == {"term": {"verdict": "malicious"}}

    @pytest.mark.asyncio
    async def test_country_aggregation(self, mock_opensearch_client, sample_geo_response):
        """Test that countries are correctly aggregated."""
        mock_opensearch_client.search.return_value = sample_geo_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_threat_map()

        assert len(result.countries) == 5
        assert result.countries[0]["name"] == "Russia"
        assert result.countries[0]["count"] == 85
        assert result.countries[1]["name"] == "China"
        assert result.countries[1]["count"] == 65

    @pytest.mark.asyncio
    async def test_total_iocs_count(self, mock_opensearch_client, sample_geo_response):
        """Test that total_iocs is correctly extracted."""
        mock_opensearch_client.search.return_value = sample_geo_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_threat_map()

        assert result.total_iocs == 250

    @pytest.mark.asyncio
    async def test_top_50_limit(self, mock_opensearch_client, sample_geo_response):
        """Test that aggregation requests top 50 sources."""
        mock_opensearch_client.search.return_value = sample_geo_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_threat_map()

        call_args = mock_opensearch_client.search.call_args
        body = call_args[1]["body"]
        assert body["aggs"]["by_source"]["terms"]["size"] == 50

    @pytest.mark.asyncio
    async def test_no_hits_size_zero(self, mock_opensearch_client, sample_geo_response):
        """Test that no document hits are returned (size=0)."""
        mock_opensearch_client.search.return_value = sample_geo_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_threat_map()

        call_args = mock_opensearch_client.search.call_args
        body = call_args[1]["body"]
        assert body["size"] == 0

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_opensearch_client):
        """Test handling of empty geo aggregation results."""
        empty_response = {
            "hits": {"total": {"value": 0}},
            "aggregations": {"by_source": {"buckets": []}},
        }
        mock_opensearch_client.search.return_value = empty_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_threat_map()

        assert result.countries == []
        assert result.total_iocs == 0

    @pytest.mark.asyncio
    async def test_exception_returns_empty_map(self, mock_opensearch_client):
        """Test that exceptions return empty GeoMap instead of crashing."""
        mock_opensearch_client.search.side_effect = Exception("OpenSearch error")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_threat_map()

        assert isinstance(result, GeoMap)
        assert result.countries == []
        assert result.total_iocs == 0

    @pytest.mark.asyncio
    async def test_uses_threat_intel_index(self, mock_opensearch_client, sample_geo_response):
        """Test that the correct index is queried."""
        mock_opensearch_client.search.return_value = sample_geo_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_threat_map()

        call_args = mock_opensearch_client.search.call_args
        assert call_args[1]["index"] == "threat-intel-v1"


# ============================================================================
# Tests for get_actor_iocs()
# ============================================================================


class TestGetActorIOCs:
    """Tests for the get_actor_iocs endpoint."""

    @pytest.mark.asyncio
    async def test_labels_term_match(self, mock_opensearch_client, sample_ioc_hits):
        """Test that actor name is matched against labels field."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_actor_iocs("APT29")

        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        should_clauses = query["bool"]["should"]

        assert {"term": {"labels": "APT29"}} in should_clauses

    @pytest.mark.asyncio
    async def test_tags_term_match(self, mock_opensearch_client, sample_ioc_hits):
        """Test that actor name is matched against tags field."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_actor_iocs("Cobalt Strike")

        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        should_clauses = query["bool"]["should"]

        assert {"term": {"tags": "Cobalt Strike"}} in should_clauses

    @pytest.mark.asyncio
    async def test_malware_family_term_match(self, mock_opensearch_client, sample_ioc_hits):
        """Test that actor name is matched against malware_family field."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_actor_iocs("Emotet")

        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]
        should_clauses = query["bool"]["should"]

        assert {"term": {"malware_family": "Emotet"}} in should_clauses

    @pytest.mark.asyncio
    async def test_should_match_or_logic(self, mock_opensearch_client, sample_ioc_hits):
        """Test that should clauses use OR logic (minimum_should_match=1)."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_actor_iocs("APT29")

        call_args = mock_opensearch_client.search.call_args
        query = call_args[1]["body"]["query"]

        assert query["bool"]["minimum_should_match"] == 1

    @pytest.mark.asyncio
    async def test_size_limit_100(self, mock_opensearch_client, sample_ioc_hits):
        """Test that results are limited to 100."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_actor_iocs("APT29")

        call_args = mock_opensearch_client.search.call_args
        body = call_args[1]["body"]
        assert body["size"] == 100

    @pytest.mark.asyncio
    async def test_sorting_by_last_seen(self, mock_opensearch_client, sample_ioc_hits):
        """Test that results are sorted by last_seen descending."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_actor_iocs("APT29")

        call_args = mock_opensearch_client.search.call_args
        body = call_args[1]["body"]
        assert body["sort"] == [{"last_seen": "desc"}]

    @pytest.mark.asyncio
    async def test_response_structure(self, mock_opensearch_client, sample_ioc_hits):
        """Test that response includes actor name, iocs, and total."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_actor_iocs("APT29")

        assert result["actor"] == "APT29"
        assert "iocs" in result
        assert "total" in result
        assert len(result["iocs"]) == 3
        assert result["total"] == 3

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_opensearch_client):
        """Test handling of no matching IOCs for actor."""
        empty_response = {"hits": {"total": {"value": 0}, "hits": []}}
        mock_opensearch_client.search.return_value = empty_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_actor_iocs("UnknownActor")

        assert result["actor"] == "UnknownActor"
        assert result["iocs"] == []
        assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_exception_returns_empty_actor_data(self, mock_opensearch_client):
        """Test that exceptions return empty actor data instead of crashing."""
        mock_opensearch_client.search.side_effect = Exception("OpenSearch error")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_actor_iocs("APT29")

        assert result["actor"] == "APT29"
        assert result["iocs"] == []
        assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_uses_threat_intel_index(self, mock_opensearch_client, sample_ioc_hits):
        """Test that the correct index is queried."""
        mock_opensearch_client.search.return_value = sample_ioc_hits

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_actor_iocs("APT29")

        call_args = mock_opensearch_client.search.call_args
        assert call_args[1]["index"] == "threat-intel-v1"


# ============================================================================
# Tests for get_mitre_coverage()
# ============================================================================


class TestGetMitreCoverage:
    """Tests for the get_mitre_coverage endpoint."""

    @pytest.mark.asyncio
    async def test_technique_id_aggregation(self, mock_opensearch_client, sample_mitre_response):
        """Test that technique_id terms aggregation is correctly built."""
        mock_opensearch_client.search.return_value = sample_mitre_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_mitre_coverage()

        call_args = mock_opensearch_client.search.call_args
        body = call_args[1]["body"]

        assert "aggs" in body
        assert "by_technique" in body["aggs"]
        assert body["aggs"]["by_technique"]["terms"]["field"] == "technique_id"
        assert body["aggs"]["by_technique"]["terms"]["size"] == 100

    @pytest.mark.asyncio
    async def test_technique_name_extraction(self, mock_opensearch_client, sample_mitre_response):
        """Test that technique_name is extracted from sub-aggregation."""
        mock_opensearch_client.search.return_value = sample_mitre_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_mitre_coverage()

        # First technique should have extracted name
        assert result.techniques[0]["technique_id"] == "T1059.001"
        assert result.techniques[0]["technique_name"] == "PowerShell"

        # Second technique
        assert result.techniques[1]["technique_id"] == "T1053.005"
        assert result.techniques[1]["technique_name"] == "Scheduled Task"

    @pytest.mark.asyncio
    async def test_technique_name_fallback_to_id(self, mock_opensearch_client, sample_mitre_response):
        """Test that technique_name falls back to technique_id if name is missing."""
        mock_opensearch_client.search.return_value = sample_mitre_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_mitre_coverage()

        # Third technique has empty name buckets
        assert result.techniques[2]["technique_id"] == "T1003.001"
        assert result.techniques[2]["technique_name"] == "T1003.001"  # Falls back to ID

    @pytest.mark.asyncio
    async def test_severity_distribution(self, mock_opensearch_client, sample_mitre_response):
        """Test that severity distribution is correctly extracted."""
        mock_opensearch_client.search.return_value = sample_mitre_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_mitre_coverage()

        # First technique severity distribution
        assert result.techniques[0]["severity_distribution"] == {
            "Critical": 30,
            "High": 60,
            "Medium": 30,
        }

        # Second technique severity distribution
        assert result.techniques[1]["severity_distribution"] == {
            "High": 50,
            "Medium": 30,
        }

    @pytest.mark.asyncio
    async def test_doc_count_aggregation(self, mock_opensearch_client, sample_mitre_response):
        """Test that detection_count is correctly extracted from doc_count."""
        mock_opensearch_client.search.return_value = sample_mitre_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_mitre_coverage()

        assert result.techniques[0]["detection_count"] == 120
        assert result.techniques[1]["detection_count"] == 80
        assert result.techniques[2]["detection_count"] == 50

    @pytest.mark.asyncio
    async def test_total_detections(self, mock_opensearch_client, sample_mitre_response):
        """Test that total_detections is correctly extracted."""
        mock_opensearch_client.search.return_value = sample_mitre_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_mitre_coverage()

        assert result.total_detections == 500

    @pytest.mark.asyncio
    async def test_uses_edr_detections_index(self, mock_opensearch_client, sample_mitre_response):
        """Test that the EDR detections index is queried."""
        mock_opensearch_client.search.return_value = sample_mitre_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_mitre_coverage()

        call_args = mock_opensearch_client.search.call_args
        assert call_args[1]["index"] == "edr-detections-v1"

    @pytest.mark.asyncio
    async def test_no_hits_size_zero(self, mock_opensearch_client, sample_mitre_response):
        """Test that no document hits are returned (size=0)."""
        mock_opensearch_client.search.return_value = sample_mitre_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_mitre_coverage()

        call_args = mock_opensearch_client.search.call_args
        body = call_args[1]["body"]
        assert body["size"] == 0

    @pytest.mark.asyncio
    async def test_nested_aggregations_structure(
        self, mock_opensearch_client, sample_mitre_response
    ):
        """Test that nested aggregations are correctly requested."""
        mock_opensearch_client.search.return_value = sample_mitre_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            await get_mitre_coverage()

        call_args = mock_opensearch_client.search.call_args
        body = call_args[1]["body"]
        by_technique = body["aggs"]["by_technique"]

        # Verify nested aggs
        assert "aggs" in by_technique
        assert "technique_name" in by_technique["aggs"]
        assert "by_severity" in by_technique["aggs"]

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_opensearch_client):
        """Test handling of empty MITRE results."""
        empty_response = {
            "hits": {"total": {"value": 0}},
            "aggregations": {"by_technique": {"buckets": []}},
        }
        mock_opensearch_client.search.return_value = empty_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_mitre_coverage()

        assert isinstance(result, MitreMap)
        assert result.techniques == []
        assert result.total_detections == 0

    @pytest.mark.asyncio
    async def test_exception_returns_empty_mitre(self, mock_opensearch_client):
        """Test that exceptions return empty MitreMap instead of crashing."""
        mock_opensearch_client.search.side_effect = Exception("OpenSearch error")

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_mitre_coverage()

        assert isinstance(result, MitreMap)
        assert result.techniques == []
        assert result.total_detections == 0

    @pytest.mark.asyncio
    async def test_missing_severity_buckets(self, mock_opensearch_client):
        """Test handling of techniques without severity distribution."""
        response = {
            "hits": {"total": {"value": 100}},
            "aggregations": {
                "by_technique": {
                    "buckets": [
                        {
                            "key": "T1001",
                            "doc_count": 50,
                            "technique_name": {"buckets": [{"key": "Data Obfuscation"}]},
                            # Missing by_severity
                        }
                    ]
                }
            },
        }
        mock_opensearch_client.search.return_value = response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            result = await get_mitre_coverage()

        # Should handle missing severity gracefully
        assert result.techniques[0]["technique_id"] == "T1001"
        assert result.techniques[0]["severity_distribution"] == {}
