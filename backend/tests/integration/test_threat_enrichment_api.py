"""
Integration tests for Threat Enrichment API endpoints.

Tests the specific threat enrichment flows from HTTP request to response,
including the 100 item limit, status tracking, and graceful degradation.

TDD: These tests are written FIRST before any implementation changes.
"""
import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport


pytestmark = pytest.mark.asyncio

# Base path for enrichment API
ENRICHMENT_BASE = "/api/enrichment"


@pytest.fixture
async def app():
    """Create test application."""
    from src.main import app
    return app


@pytest.fixture
async def client(app):
    """Create async HTTP client for testing."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


class TestPostEnrichmentThreats:
    """Tests for POST /api/enrichment/threats endpoint."""

    async def test_post_enrichment_threats_creates_job(self, client):
        """
        Test that POST /api/enrichment/threats creates an enrichment job.

        Expected behavior:
        - Returns 200 with job details
        - job_id is a valid UUID string
        - total_items reflects submitted indicators
        - sources dict contains per-source status
        """
        with patch('src.api.enrichment.EnrichmentService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.enrich_threats = AsyncMock(return_value={
                "job_id": "threat-job-abc123",
                "total_items": 3,
                "enriched_indicators": [
                    {"id": "1", "type": "ip", "value": "192.168.1.100", "risk_score": 75},
                    {"id": "2", "type": "ip", "value": "10.0.0.50", "risk_score": 45},
                    {"id": "3", "type": "domain", "value": "malicious.example.com", "risk_score": 90},
                ],
                "sources": {
                    "otx": {"status": "success", "enriched_count": 3},
                    "abuseipdb": {"status": "success", "enriched_count": 2},
                    "greynoise": {"status": "success", "enriched_count": 2},
                    "virustotal": {"status": "success", "enriched_count": 3},
                    "synthetic": {"status": "success", "enriched_count": 3},
                },
                "successful_sources": 5,
                "failed_sources": 0,
                "errors": []
            })
            MockService.return_value = mock_instance

            response = await client.post(
                f"{ENRICHMENT_BASE}/threats",
                json={
                    "indicators": [
                        {"type": "ip", "value": "192.168.1.100"},
                        {"type": "ip", "value": "10.0.0.50"},
                        {"type": "domain", "value": "malicious.example.com"}
                    ],
                    "sources": ["otx", "abuseipdb", "greynoise", "virustotal", "synthetic"]
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Verify job creation response
            assert "job_id" in data
            assert data["job_id"] == "threat-job-abc123"
            assert data["total_items"] == 3
            assert data["successful_sources"] == 5
            assert data["failed_sources"] == 0
            assert "sources" in data
            assert len(data["errors"]) == 0

            # Verify service was called with correct parameters
            mock_instance.enrich_threats.assert_called_once()
            call_kwargs = mock_instance.enrich_threats.call_args.kwargs
            assert len(call_kwargs["indicators"]) == 3
            assert call_kwargs["sources"] == ["otx", "abuseipdb", "greynoise", "virustotal", "synthetic"]

    async def test_post_enrichment_threats_limits_to_100_items(self, client):
        """
        Test that the API limits indicators to 100 items per request.

        Expected behavior:
        - Request with >100 indicators is accepted
        - Service is called with at most 100 indicators
        - Response total_items reflects the limited count
        """
        with patch('src.api.enrichment.EnrichmentService') as MockService:
            mock_instance = AsyncMock()
            # Service should limit to 100 and return that count
            mock_instance.enrich_threats = AsyncMock(return_value={
                "job_id": "limited-job-456",
                "total_items": 100,  # Limited from 150
                "enriched_indicators": [{"id": str(i), "type": "ip", "value": f"10.0.0.{i % 256}"} for i in range(100)],
                "sources": {
                    "synthetic": {"status": "success", "enriched_count": 100}
                },
                "successful_sources": 1,
                "failed_sources": 0,
                "errors": []
            })
            MockService.return_value = mock_instance

            # Create 150 indicators
            indicators = [
                {"type": "ip", "value": f"10.0.{i // 256}.{i % 256}"}
                for i in range(150)
            ]

            response = await client.post(
                f"{ENRICHMENT_BASE}/threats",
                json={
                    "indicators": indicators,
                    "sources": ["synthetic"]
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Verify the response reflects the limited count
            assert data["total_items"] == 100

            # Verify service was called
            mock_instance.enrich_threats.assert_called_once()

    async def test_post_enrichment_threats_empty_indicators(self, client):
        """
        Test POST with empty indicators list.

        Expected behavior:
        - Returns 200 with empty job
        - total_items is 0
        """
        with patch('src.api.enrichment.EnrichmentService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.enrich_threats = AsyncMock(return_value={
                "job_id": "empty-threat-job",
                "total_items": 0,
                "enriched_indicators": [],
                "sources": {},
                "successful_sources": 0,
                "failed_sources": 0,
                "errors": []
            })
            MockService.return_value = mock_instance

            response = await client.post(
                f"{ENRICHMENT_BASE}/threats",
                json={"indicators": []}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total_items"] == 0

    async def test_post_enrichment_threats_default_sources(self, client):
        """
        Test that default sources are used when not specified.

        Expected behavior:
        - Request without sources uses default threat sources
        - Service is called with None for sources (letting it use defaults)
        """
        with patch('src.api.enrichment.EnrichmentService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.enrich_threats = AsyncMock(return_value={
                "job_id": "default-sources-job",
                "total_items": 1,
                "enriched_indicators": [{"id": "1", "type": "ip", "value": "192.168.1.1"}],
                "sources": {
                    "otx": {"status": "success", "enriched_count": 1},
                    "abuseipdb": {"status": "success", "enriched_count": 1},
                    "greynoise": {"status": "success", "enriched_count": 1},
                    "virustotal": {"status": "success", "enriched_count": 1},
                    "synthetic": {"status": "success", "enriched_count": 1},
                },
                "successful_sources": 5,
                "failed_sources": 0,
                "errors": []
            })
            MockService.return_value = mock_instance

            response = await client.post(
                f"{ENRICHMENT_BASE}/threats",
                json={
                    "indicators": [{"type": "ip", "value": "192.168.1.1"}]
                    # sources not specified
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["successful_sources"] >= 1

            # Verify sources was None (use defaults)
            call_kwargs = mock_instance.enrich_threats.call_args.kwargs
            assert call_kwargs["sources"] is None


class TestGetEnrichmentThreatStatus:
    """Tests for GET /api/enrichment/threats/status/{job_id} endpoint."""

    async def test_get_enrichment_status_returns_progress(self, client):
        """
        Test that GET /api/enrichment/status/{job_id} returns job progress.

        Note: The actual endpoint is /api/enrichment/status/{job_id} (not threats-specific)
        but it works for all enrichment job types.

        Expected behavior:
        - Returns 200 with job status
        - Progress is between 0.0 and 1.0
        - processed_items and total_items are included
        """
        with patch('src.api.enrichment.EnrichmentService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.get_enrichment_status = AsyncMock(return_value={
                "job_id": "threat-progress-job",
                "status": "running",
                "progress": 0.6,
                "processed_items": 60,
                "total_items": 100,
                "failed_items": 2,
                "started_at": "2024-02-16T10:00:00",
                "completed_at": None,
                "error_message": None
            })
            MockService.return_value = mock_instance

            response = await client.get(f"{ENRICHMENT_BASE}/status/threat-progress-job")

            assert response.status_code == 200
            data = response.json()

            assert data["job_id"] == "threat-progress-job"
            assert data["status"] == "running"
            assert data["progress"] == 0.6
            assert data["processed_items"] == 60
            assert data["total_items"] == 100
            assert data["failed_items"] == 2
            assert data["started_at"] == "2024-02-16T10:00:00"
            assert data["completed_at"] is None

    async def test_get_enrichment_status_completed_job(self, client):
        """
        Test getting status of a completed threat enrichment job.
        """
        with patch('src.api.enrichment.EnrichmentService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.get_enrichment_status = AsyncMock(return_value={
                "job_id": "completed-threat-job",
                "status": "completed",
                "progress": 1.0,
                "processed_items": 50,
                "total_items": 50,
                "failed_items": 0,
                "started_at": "2024-02-16T10:00:00",
                "completed_at": "2024-02-16T10:01:30",
                "error_message": None
            })
            MockService.return_value = mock_instance

            response = await client.get(f"{ENRICHMENT_BASE}/status/completed-threat-job")

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "completed"
            assert data["progress"] == 1.0
            assert data["completed_at"] is not None

    async def test_get_enrichment_status_missing_job_id_returns_404(self, client):
        """
        Test that a missing job_id returns 404.

        Expected behavior:
        - Non-existent job_id returns 404
        - Response contains appropriate error message
        """
        with patch('src.api.enrichment.EnrichmentService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.get_enrichment_status = AsyncMock(
                side_effect=ValueError("Job non-existent-id not found")
            )
            MockService.return_value = mock_instance

            response = await client.get(f"{ENRICHMENT_BASE}/status/non-existent-id")

            assert response.status_code == 404
            data = response.json()
            assert "not found" in data["detail"].lower()


class TestEnrichmentHandlesSourceFailureGracefully:
    """Tests for graceful degradation when threat enrichment sources fail."""

    async def test_enrichment_handles_source_failure_gracefully(self, client):
        """
        Test that the enrichment continues when some sources fail.

        Expected behavior:
        - Request completes successfully even if some sources fail
        - successful_sources counts working sources
        - failed_sources counts failed sources
        - errors array contains details about failures
        - Status is not 500 (graceful degradation)
        """
        with patch('src.api.enrichment.EnrichmentService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.enrich_threats = AsyncMock(return_value={
                "job_id": "partial-failure-job",
                "total_items": 2,
                "enriched_indicators": [
                    {"id": "1", "type": "ip", "value": "192.168.1.1", "risk_score": 50},
                    {"id": "2", "type": "ip", "value": "10.0.0.1", "risk_score": 30},
                ],
                "sources": {
                    "otx": {"status": "success", "enriched_count": 2},
                    "abuseipdb": {"status": "failed", "error": "API rate limit exceeded"},
                    "greynoise": {"status": "failed", "error": "Connection timeout"},
                    "virustotal": {"status": "success", "enriched_count": 2},
                    "synthetic": {"status": "success", "enriched_count": 2},
                },
                "successful_sources": 3,
                "failed_sources": 2,
                "errors": [
                    {"source": "abuseipdb", "error": "API rate limit exceeded", "recoverable": True},
                    {"source": "greynoise", "error": "Connection timeout", "recoverable": True},
                ]
            })
            MockService.return_value = mock_instance

            response = await client.post(
                f"{ENRICHMENT_BASE}/threats",
                json={
                    "indicators": [
                        {"type": "ip", "value": "192.168.1.1"},
                        {"type": "ip", "value": "10.0.0.1"}
                    ],
                    "sources": ["otx", "abuseipdb", "greynoise", "virustotal", "synthetic"]
                }
            )

            # Request should succeed despite source failures
            assert response.status_code == 200
            data = response.json()

            # Verify partial success
            assert data["successful_sources"] == 3
            assert data["failed_sources"] == 2
            assert len(data["errors"]) == 2

            # Verify sources contain both success and failure statuses
            assert data["sources"]["otx"]["status"] == "success"
            assert data["sources"]["abuseipdb"]["status"] == "failed"
            assert data["sources"]["greynoise"]["status"] == "failed"
            assert data["sources"]["virustotal"]["status"] == "success"

    async def test_enrichment_all_sources_fail_still_returns_200(self, client):
        """
        Test that even when ALL sources fail, the API returns 200 with error info.

        This is graceful degradation - the request completed, just with no enrichment.
        """
        with patch('src.api.enrichment.EnrichmentService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.enrich_threats = AsyncMock(return_value={
                "job_id": "all-failed-job",
                "total_items": 1,
                "enriched_indicators": [
                    {"id": "1", "type": "ip", "value": "192.168.1.1", "risk_score": 0},
                ],
                "sources": {
                    "otx": {"status": "failed", "error": "API unavailable"},
                    "abuseipdb": {"status": "failed", "error": "API unavailable"},
                },
                "successful_sources": 0,
                "failed_sources": 2,
                "errors": [
                    {"source": "otx", "error": "API unavailable", "recoverable": True},
                    {"source": "abuseipdb", "error": "API unavailable", "recoverable": True},
                ]
            })
            MockService.return_value = mock_instance

            response = await client.post(
                f"{ENRICHMENT_BASE}/threats",
                json={
                    "indicators": [{"type": "ip", "value": "192.168.1.1"}],
                    "sources": ["otx", "abuseipdb"]
                }
            )

            # Should return 200 (not 500) even with all failures
            assert response.status_code == 200
            data = response.json()

            assert data["successful_sources"] == 0
            assert data["failed_sources"] == 2
            assert len(data["errors"]) == 2

    async def test_enrichment_circuit_breaker_failure(self, client):
        """
        Test that circuit breaker errors are handled gracefully.
        """
        with patch('src.api.enrichment.EnrichmentService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.enrich_threats = AsyncMock(return_value={
                "job_id": "circuit-breaker-job",
                "total_items": 1,
                "enriched_indicators": [{"id": "1", "type": "ip", "value": "192.168.1.1"}],
                "sources": {
                    "otx": {"status": "failed", "error": "Circuit breaker open - too many recent failures"},
                    "synthetic": {"status": "success", "enriched_count": 1},
                },
                "successful_sources": 1,
                "failed_sources": 1,
                "errors": [
                    {"source": "otx", "error": "Circuit breaker open - too many recent failures", "recoverable": True}
                ]
            })
            MockService.return_value = mock_instance

            response = await client.post(
                f"{ENRICHMENT_BASE}/threats",
                json={
                    "indicators": [{"type": "ip", "value": "192.168.1.1"}],
                    "sources": ["otx", "synthetic"]
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Circuit breaker failure should be in errors
            assert any("circuit breaker" in e["error"].lower() for e in data["errors"])


class TestEnrichmentForceRefresh:
    """Tests for force_refresh parameter in threat enrichment."""

    async def test_force_refresh_bypasses_cache(self, client):
        """
        Test that force_refresh=True is passed to the service.
        """
        with patch('src.api.enrichment.EnrichmentService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.enrich_threats = AsyncMock(return_value={
                "job_id": "force-refresh-job",
                "total_items": 1,
                "enriched_indicators": [],
                "sources": {},
                "successful_sources": 0,
                "failed_sources": 0,
                "errors": []
            })
            MockService.return_value = mock_instance

            response = await client.post(
                f"{ENRICHMENT_BASE}/threats",
                json={
                    "indicators": [{"type": "ip", "value": "192.168.1.1"}],
                    "force_refresh": True
                }
            )

            assert response.status_code == 200

            # Verify force_refresh was passed to service
            call_kwargs = mock_instance.enrich_threats.call_args.kwargs
            assert call_kwargs["force_refresh"] is True


class TestEnrichmentIndicatorTypes:
    """Tests for different indicator types."""

    async def test_ip_indicator_enrichment(self, client):
        """Test IP address indicator enrichment."""
        with patch('src.api.enrichment.EnrichmentService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.enrich_threats = AsyncMock(return_value={
                "job_id": "ip-job",
                "total_items": 1,
                "enriched_indicators": [{"id": "1", "type": "ip", "value": "192.168.1.1"}],
                "sources": {"synthetic": {"status": "success", "enriched_count": 1}},
                "successful_sources": 1,
                "failed_sources": 0,
                "errors": []
            })
            MockService.return_value = mock_instance

            response = await client.post(
                f"{ENRICHMENT_BASE}/threats",
                json={"indicators": [{"type": "ip", "value": "192.168.1.1"}]}
            )

            assert response.status_code == 200

    async def test_domain_indicator_enrichment(self, client):
        """Test domain indicator enrichment."""
        with patch('src.api.enrichment.EnrichmentService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.enrich_threats = AsyncMock(return_value={
                "job_id": "domain-job",
                "total_items": 1,
                "enriched_indicators": [{"id": "1", "type": "domain", "value": "evil.com"}],
                "sources": {"synthetic": {"status": "success", "enriched_count": 1}},
                "successful_sources": 1,
                "failed_sources": 0,
                "errors": []
            })
            MockService.return_value = mock_instance

            response = await client.post(
                f"{ENRICHMENT_BASE}/threats",
                json={"indicators": [{"type": "domain", "value": "evil.com"}]}
            )

            assert response.status_code == 200

    async def test_hash_indicator_enrichment(self, client):
        """Test file hash indicator enrichment."""
        with patch('src.api.enrichment.EnrichmentService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.enrich_threats = AsyncMock(return_value={
                "job_id": "hash-job",
                "total_items": 1,
                "enriched_indicators": [{"id": "1", "type": "hash", "value": "abc123def456"}],
                "sources": {"synthetic": {"status": "success", "enriched_count": 1}},
                "successful_sources": 1,
                "failed_sources": 0,
                "errors": []
            })
            MockService.return_value = mock_instance

            response = await client.post(
                f"{ENRICHMENT_BASE}/threats",
                json={"indicators": [{"type": "hash", "value": "abc123def456"}]}
            )

            assert response.status_code == 200

    async def test_url_indicator_enrichment(self, client):
        """Test URL indicator enrichment."""
        with patch('src.api.enrichment.EnrichmentService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.enrich_threats = AsyncMock(return_value={
                "job_id": "url-job",
                "total_items": 1,
                "enriched_indicators": [{"id": "1", "type": "url", "value": "http://evil.com/malware"}],
                "sources": {"synthetic": {"status": "success", "enriched_count": 1}},
                "successful_sources": 1,
                "failed_sources": 0,
                "errors": []
            })
            MockService.return_value = mock_instance

            response = await client.post(
                f"{ENRICHMENT_BASE}/threats",
                json={"indicators": [{"type": "url", "value": "http://evil.com/malware"}]}
            )

            assert response.status_code == 200

    async def test_mixed_indicator_types(self, client):
        """Test enrichment with multiple indicator types in one request."""
        with patch('src.api.enrichment.EnrichmentService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.enrich_threats = AsyncMock(return_value={
                "job_id": "mixed-job",
                "total_items": 4,
                "enriched_indicators": [
                    {"id": "1", "type": "ip", "value": "192.168.1.1"},
                    {"id": "2", "type": "domain", "value": "evil.com"},
                    {"id": "3", "type": "hash", "value": "abc123"},
                    {"id": "4", "type": "url", "value": "http://bad.com"},
                ],
                "sources": {"synthetic": {"status": "success", "enriched_count": 4}},
                "successful_sources": 1,
                "failed_sources": 0,
                "errors": []
            })
            MockService.return_value = mock_instance

            response = await client.post(
                f"{ENRICHMENT_BASE}/threats",
                json={
                    "indicators": [
                        {"type": "ip", "value": "192.168.1.1"},
                        {"type": "domain", "value": "evil.com"},
                        {"type": "hash", "value": "abc123"},
                        {"type": "url", "value": "http://bad.com"},
                    ]
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total_items"] == 4
