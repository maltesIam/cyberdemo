"""
Unit tests for Vulnerabilities SSVC and Classification API endpoints.

Following TDD: Tests for SSVC summary, SSVC tree, CWEs, and Packages endpoints.
Uses mocking for OpenSearch client and database to isolate API logic.

Endpoints:
- GET /api/vulnerabilities/ssvc/summary
- GET /api/vulnerabilities/ssvc/tree
- GET /api/vulnerabilities/cwes
- GET /api/vulnerabilities/cwes/{cwe_id}
- GET /api/vulnerabilities/packages
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
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
def sample_ssvc_aggregation_response():
    """Sample OpenSearch response with SSVC decision aggregations."""
    return {
        "aggregations": {
            "ssvc_decisions": {
                "buckets": [
                    {"key": "Act", "doc_count": 15},
                    {"key": "Attend", "doc_count": 45},
                    {"key": "Track*", "doc_count": 30},
                    {"key": "Track", "doc_count": 60},
                ]
            },
            "critical_requires_action": {
                "doc_count": 25
            }
        }
    }


@pytest.fixture
def sample_ssvc_tree_response():
    """Sample OpenSearch response for SSVC tree aggregation."""
    return {
        "aggregations": {
            "exploitation_status": {
                "buckets": [
                    {
                        "key": "active",
                        "doc_count": 25,
                        "automatable": {
                            "buckets": [
                                {"key": 1, "key_as_string": "true", "doc_count": 15},
                                {"key": 0, "key_as_string": "false", "doc_count": 10},
                            ]
                        }
                    },
                    {
                        "key": "poc",
                        "doc_count": 50,
                        "technical_impact": {
                            "buckets": [
                                {"key": "total", "doc_count": 20},
                                {"key": "partial", "doc_count": 30},
                            ]
                        }
                    },
                    {
                        "key": "none",
                        "doc_count": 75,
                    }
                ]
            }
        }
    }


@pytest.fixture
def sample_cwes_aggregation_response():
    """Sample OpenSearch response for CWE aggregations."""
    return {
        "aggregations": {
            "cwes": {
                "buckets": [
                    {
                        "key": "CWE-79",
                        "doc_count": 25,
                        "severity_breakdown": {
                            "buckets": [
                                {"key": "Critical", "doc_count": 5},
                                {"key": "High", "doc_count": 10},
                                {"key": "Medium", "doc_count": 8},
                                {"key": "Low", "doc_count": 2},
                            ]
                        }
                    },
                    {
                        "key": "CWE-89",
                        "doc_count": 18,
                        "severity_breakdown": {
                            "buckets": [
                                {"key": "Critical", "doc_count": 8},
                                {"key": "High", "doc_count": 6},
                                {"key": "Medium", "doc_count": 3},
                                {"key": "Low", "doc_count": 1},
                            ]
                        }
                    },
                ]
            }
        }
    }


@pytest.fixture
def sample_cwe_detail_response():
    """Sample OpenSearch response for CWE detail."""
    return {
        "hits": {
            "total": {"value": 25},
            "hits": [
                {"_source": {"cve_id": "CVE-2024-0001", "severity": "Critical"}},
                {"_source": {"cve_id": "CVE-2024-0002", "severity": "High"}},
                {"_source": {"cve_id": "CVE-2024-0003", "severity": "High"}},
                {"_source": {"cve_id": "CVE-2024-0004", "severity": "Medium"}},
                {"_source": {"cve_id": "CVE-2024-0005", "severity": "Low"}},
            ]
        },
        "aggregations": {
            "severity_breakdown": {
                "buckets": [
                    {"key": "Critical", "doc_count": 5},
                    {"key": "High", "doc_count": 10},
                    {"key": "Medium", "doc_count": 8},
                    {"key": "Low", "doc_count": 2},
                ]
            }
        }
    }


@pytest.fixture
def sample_packages_aggregation_response():
    """Sample OpenSearch response for vulnerable packages."""
    return {
        "aggregations": {
            "packages": {
                "buckets": [
                    {
                        "key": "npm:lodash",
                        "doc_count": 12,
                        "critical_count": {"doc_count": 2}
                    },
                    {
                        "key": "pip:django",
                        "doc_count": 8,
                        "critical_count": {"doc_count": 1}
                    },
                    {
                        "key": "maven:log4j",
                        "doc_count": 5,
                        "critical_count": {"doc_count": 3}
                    },
                ]
            }
        }
    }


# ============================================================================
# Tests for SSVC Summary Endpoint
# ============================================================================


class TestSSVCSummary:
    """Tests for GET /api/vulnerabilities/ssvc/summary endpoint."""

    @pytest.mark.asyncio
    async def test_ssvc_summary_returns_decision_counts(
        self, client, mock_opensearch_client, sample_ssvc_aggregation_response
    ):
        """Test that SSVC summary returns count for each decision type."""
        mock_opensearch_client.search.return_value = sample_ssvc_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/ssvc/summary")

        assert response.status_code == 200
        data = response.json()

        assert "decisions" in data
        assert data["decisions"]["Act"] == 15
        assert data["decisions"]["Attend"] == 45
        assert data["decisions"]["Track*"] == 30
        assert data["decisions"]["Track"] == 60

    @pytest.mark.asyncio
    async def test_ssvc_summary_calculates_total_and_percentage(
        self, client, mock_opensearch_client, sample_ssvc_aggregation_response
    ):
        """Test that total count and act_percentage are calculated correctly."""
        mock_opensearch_client.search.return_value = sample_ssvc_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/ssvc/summary")

        assert response.status_code == 200
        data = response.json()

        # Total should be 15 + 45 + 30 + 60 = 150
        assert data["total"] == 150
        # Act percentage = 15 / 150 * 100 = 10.0
        assert data["act_percentage"] == 10.0

    @pytest.mark.asyncio
    async def test_ssvc_summary_returns_critical_requires_action(
        self, client, mock_opensearch_client, sample_ssvc_aggregation_response
    ):
        """Test that critical_requires_action count is returned."""
        mock_opensearch_client.search.return_value = sample_ssvc_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/ssvc/summary")

        assert response.status_code == 200
        data = response.json()

        assert data["critical_requires_action"] == 25

    @pytest.mark.asyncio
    async def test_ssvc_summary_handles_empty_data(
        self, client, mock_opensearch_client
    ):
        """Test that empty data returns zero counts."""
        empty_response = {
            "aggregations": {
                "ssvc_decisions": {"buckets": []},
                "critical_requires_action": {"doc_count": 0}
            }
        }
        mock_opensearch_client.search.return_value = empty_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/ssvc/summary")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 0
        assert data["act_percentage"] == 0.0
        assert data["critical_requires_action"] == 0


# ============================================================================
# Tests for SSVC Tree Endpoint
# ============================================================================


class TestSSVCTree:
    """Tests for GET /api/vulnerabilities/ssvc/tree endpoint."""

    @pytest.mark.asyncio
    async def test_ssvc_tree_returns_hierarchical_structure(
        self, client, mock_opensearch_client, sample_ssvc_tree_response
    ):
        """Test that SSVC tree returns proper hierarchical structure."""
        mock_opensearch_client.search.return_value = sample_ssvc_tree_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/ssvc/tree")

        assert response.status_code == 200
        data = response.json()

        assert "name" in data
        assert data["name"] == "SSVC Decision Tree"
        assert "children" in data
        assert len(data["children"]) > 0

    @pytest.mark.asyncio
    async def test_ssvc_tree_groups_by_exploitation_status(
        self, client, mock_opensearch_client, sample_ssvc_tree_response
    ):
        """Test that tree groups nodes by exploitation status."""
        mock_opensearch_client.search.return_value = sample_ssvc_tree_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/ssvc/tree")

        assert response.status_code == 200
        data = response.json()

        # Find exploitation nodes
        exploitation_names = [child["name"] for child in data["children"]]
        assert "Exploitation: active" in exploitation_names
        assert "Exploitation: poc" in exploitation_names
        assert "Exploitation: none" in exploitation_names

    @pytest.mark.asyncio
    async def test_ssvc_tree_includes_counts_and_decisions(
        self, client, mock_opensearch_client, sample_ssvc_tree_response
    ):
        """Test that tree nodes include counts and decisions at leaves."""
        mock_opensearch_client.search.return_value = sample_ssvc_tree_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/ssvc/tree")

        assert response.status_code == 200
        data = response.json()

        # Check active exploitation node has count
        active_node = next(
            (c for c in data["children"] if c["name"] == "Exploitation: active"),
            None
        )
        assert active_node is not None
        assert active_node["count"] == 25

        # Check it has children with decisions
        assert "children" in active_node
        assert len(active_node["children"]) > 0

    @pytest.mark.asyncio
    async def test_ssvc_tree_handles_empty_data(
        self, client, mock_opensearch_client
    ):
        """Test that empty data returns valid tree structure."""
        empty_response = {
            "aggregations": {
                "exploitation_status": {"buckets": []}
            }
        }
        mock_opensearch_client.search.return_value = empty_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/ssvc/tree")

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "SSVC Decision Tree"
        assert data["children"] == []


# ============================================================================
# Tests for CWEs List Endpoint
# ============================================================================


class TestCWEsList:
    """Tests for GET /api/vulnerabilities/cwes endpoint."""

    @pytest.mark.asyncio
    async def test_cwes_list_returns_unique_cwes(
        self, client, mock_opensearch_client, sample_cwes_aggregation_response
    ):
        """Test that CWEs list returns unique CWEs with counts."""
        mock_opensearch_client.search.return_value = sample_cwes_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/cwes")

        assert response.status_code == 200
        data = response.json()

        assert "cwes" in data
        assert len(data["cwes"]) == 2

        cwe_79 = next((c for c in data["cwes"] if c["cwe_id"] == "CWE-79"), None)
        assert cwe_79 is not None
        assert cwe_79["cve_count"] == 25

    @pytest.mark.asyncio
    async def test_cwes_list_includes_severity_counts(
        self, client, mock_opensearch_client, sample_cwes_aggregation_response
    ):
        """Test that each CWE includes severity breakdown counts."""
        mock_opensearch_client.search.return_value = sample_cwes_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/cwes")

        assert response.status_code == 200
        data = response.json()

        cwe_79 = next((c for c in data["cwes"] if c["cwe_id"] == "CWE-79"), None)
        assert cwe_79 is not None
        assert cwe_79["critical_count"] == 5
        assert cwe_79["high_count"] == 10

    @pytest.mark.asyncio
    async def test_cwes_list_returns_total_count(
        self, client, mock_opensearch_client, sample_cwes_aggregation_response
    ):
        """Test that total count of unique CWEs is returned."""
        mock_opensearch_client.search.return_value = sample_cwes_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/cwes")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_cwes_list_handles_empty_data(
        self, client, mock_opensearch_client
    ):
        """Test that empty data returns empty list."""
        empty_response = {
            "aggregations": {
                "cwes": {"buckets": []}
            }
        }
        mock_opensearch_client.search.return_value = empty_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/cwes")

        assert response.status_code == 200
        data = response.json()

        assert data["cwes"] == []
        assert data["total"] == 0


# ============================================================================
# Tests for CWE Detail Endpoint
# ============================================================================


class TestCWEDetail:
    """Tests for GET /api/vulnerabilities/cwes/{cwe_id} endpoint."""

    @pytest.mark.asyncio
    async def test_cwe_detail_returns_metadata(
        self, client, mock_opensearch_client, sample_cwe_detail_response
    ):
        """Test that CWE detail returns CWE metadata."""
        mock_opensearch_client.search.return_value = sample_cwe_detail_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/cwes/CWE-79")

        assert response.status_code == 200
        data = response.json()

        assert data["cwe_id"] == "CWE-79"
        assert "name" in data
        assert "description" in data

    @pytest.mark.asyncio
    async def test_cwe_detail_returns_cve_list(
        self, client, mock_opensearch_client, sample_cwe_detail_response
    ):
        """Test that CWE detail returns list of affected CVEs."""
        mock_opensearch_client.search.return_value = sample_cwe_detail_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/cwes/CWE-79")

        assert response.status_code == 200
        data = response.json()

        assert "cves" in data
        assert "CVE-2024-0001" in data["cves"]
        assert "CVE-2024-0002" in data["cves"]

    @pytest.mark.asyncio
    async def test_cwe_detail_returns_severity_breakdown(
        self, client, mock_opensearch_client, sample_cwe_detail_response
    ):
        """Test that CWE detail returns severity breakdown."""
        mock_opensearch_client.search.return_value = sample_cwe_detail_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/cwes/CWE-79")

        assert response.status_code == 200
        data = response.json()

        assert "severity_breakdown" in data
        assert data["severity_breakdown"]["Critical"] == 5
        assert data["severity_breakdown"]["High"] == 10

    @pytest.mark.asyncio
    async def test_cwe_detail_returns_404_not_found(
        self, client, mock_opensearch_client
    ):
        """Test that 404 is returned when CWE has no CVEs."""
        empty_response = {
            "hits": {"total": {"value": 0}, "hits": []},
            "aggregations": {"severity_breakdown": {"buckets": []}}
        }
        mock_opensearch_client.search.return_value = empty_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/cwes/CWE-9999")

        assert response.status_code == 404


# ============================================================================
# Tests for Packages Endpoint
# ============================================================================


class TestPackages:
    """Tests for GET /api/vulnerabilities/packages endpoint."""

    @pytest.mark.asyncio
    async def test_packages_returns_vulnerable_packages(
        self, client, mock_opensearch_client, sample_packages_aggregation_response
    ):
        """Test that packages endpoint returns list of vulnerable packages."""
        mock_opensearch_client.search.return_value = sample_packages_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/packages")

        assert response.status_code == 200
        data = response.json()

        assert "packages" in data
        assert len(data["packages"]) == 3

        # Check lodash package
        lodash = next((p for p in data["packages"] if p["name"] == "lodash"), None)
        assert lodash is not None
        assert lodash["ecosystem"] == "npm"
        assert lodash["cve_count"] == 12

    @pytest.mark.asyncio
    async def test_packages_includes_severity_counts(
        self, client, mock_opensearch_client, sample_packages_aggregation_response
    ):
        """Test that each package includes critical count."""
        mock_opensearch_client.search.return_value = sample_packages_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/packages")

        assert response.status_code == 200
        data = response.json()

        lodash = next((p for p in data["packages"] if p["name"] == "lodash"), None)
        assert lodash is not None
        assert lodash["critical_count"] == 2

    @pytest.mark.asyncio
    async def test_packages_returns_total_count(
        self, client, mock_opensearch_client, sample_packages_aggregation_response
    ):
        """Test that total count of packages is returned."""
        mock_opensearch_client.search.return_value = sample_packages_aggregation_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/packages")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 3

    @pytest.mark.asyncio
    async def test_packages_handles_empty_data(
        self, client, mock_opensearch_client
    ):
        """Test that empty data returns empty list."""
        empty_response = {
            "aggregations": {
                "packages": {"buckets": []}
            }
        }
        mock_opensearch_client.search.return_value = empty_response

        with patch(OPENSEARCH_CLIENT_PATH, return_value=mock_opensearch_client):
            response = await client.get("/vulnerabilities/packages")

        assert response.status_code == 200
        data = response.json()

        assert data["packages"] == []
        assert data["total"] == 0
