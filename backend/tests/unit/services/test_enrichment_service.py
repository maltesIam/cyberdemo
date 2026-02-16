"""
Unit tests for EnrichmentService.

Following TDD: Write tests FIRST, then implement functionality.
"""
import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime


# These imports will fail until we implement the modules (RED phase)
# This is intentional in TDD - write test first, then implement
try:
    from src.services.enrichment_service import EnrichmentService, MAX_ITEMS_PER_SOURCE
    from src.services.circuit_breaker import CircuitBreaker, CircuitState, CircuitBreakerOpenError
except ImportError:
    # Will fail initially - this is expected in RED phase
    pass


@pytest.mark.asyncio
async def test_enrichment_limits_to_100_items_per_source():
    """
    Test that enrichment limits to MAX_ITEMS_PER_SOURCE (100)
    """
    service = EnrichmentService()

    # Attempt to enrich 200 CVEs
    cve_ids = [f"CVE-2024-{i:04d}" for i in range(200)]

    # Mock client.enrich() method to avoid real API calls
    async def mock_enrich(items):
        """Mock enrich that returns success for all items"""
        return {
            "count": len(items),
            "failed": 0,
            "processed": list(items)
        }

    # Patch the enrich method on instances
    with patch.object(AsyncMock(), 'enrich', side_effect=mock_enrich) as mock_nvd:
        with patch('src.services.enrichment_service.NVDClient') as MockNVDClient:
            with patch('src.services.enrichment_service.EPSSClient') as MockEPSSClient:
                # Configure mocks
                mock_nvd_instance = AsyncMock()
                mock_nvd_instance.enrich = AsyncMock(side_effect=mock_enrich)
                MockNVDClient.return_value = mock_nvd_instance

                mock_epss_instance = AsyncMock()
                mock_epss_instance.enrich = AsyncMock(side_effect=mock_enrich)
                MockEPSSClient.return_value = mock_epss_instance

                result = await service.enrich_vulnerabilities(cve_ids=cve_ids)

                # Must limit to 100
                assert result["total_items"] == 100, f"Expected 100 items, got {result['total_items']}"
                assert result["total_items"] == MAX_ITEMS_PER_SOURCE
                assert len(result.get("processed_cves", [])) <= MAX_ITEMS_PER_SOURCE


@pytest.mark.asyncio
async def test_enrichment_handles_source_failure_gracefully():
    """
    RED TEST: Test that enrichment continues when one source fails.

    This verifies graceful degradation - if one API fails, others should continue.
    """
    service = EnrichmentService()

    # Mock NVD to fail, but EPSS should succeed
    with patch('src.services.enrichment_service.NVDClient') as mock_nvd:
        mock_nvd.return_value.enrich = AsyncMock(side_effect=Exception("NVD API timeout"))

        result = await service.enrich_vulnerabilities(
            cve_ids=["CVE-2024-0001"],
            sources=['nvd', 'epss']
        )

        # NVD should be in failed, EPSS in success
        assert "sources" in result
        assert result["sources"]["nvd"]["status"] == "failed"
        assert "error" in result["sources"]["nvd"]

        # At least one source should succeed
        assert result["successful_sources"] >= 1
        assert len(result["errors"]) == 1
        assert result["errors"][0]["source"] == "nvd"
        assert result["errors"][0]["recoverable"] is True


@pytest.mark.asyncio
async def test_enrichment_handles_all_sources_failing():
    """
    RED TEST: Test behavior when ALL sources fail.

    Should return error information but not crash.
    """
    service = EnrichmentService()

    # Mock all sources to fail
    with patch('src.services.enrichment_service.NVDClient') as mock_nvd, \
         patch('src.services.enrichment_service.EPSSClient') as mock_epss:

        mock_nvd.return_value.enrich = AsyncMock(side_effect=Exception("NVD timeout"))
        mock_epss.return_value.enrich = AsyncMock(side_effect=Exception("EPSS timeout"))

        result = await service.enrich_vulnerabilities(
            cve_ids=["CVE-2024-0001"],
            sources=['nvd', 'epss']
        )

        # All sources failed
        assert result["successful_sources"] == 0
        assert result["failed_sources"] == 2
        assert len(result["errors"]) == 2


@pytest.mark.asyncio
async def test_enrichment_respects_force_refresh():
    """
    RED TEST: Test that force_refresh bypasses cache.
    """
    service = EnrichmentService()

    with patch.object(service, '_get_from_cache') as mock_cache, \
         patch.object(service, '_enrich_from_source') as mock_enrich:

        mock_cache.return_value = {"cached": "data"}
        mock_enrich.return_value = {"count": 1, "failed": 0}

        # With force_refresh=False, should use cache
        await service.enrich_vulnerabilities(
            cve_ids=["CVE-2024-0001"],
            sources=['nvd'],
            force_refresh=False
        )

        # Cache should be checked
        assert mock_cache.called

        # Reset mocks
        mock_cache.reset_mock()
        mock_enrich.reset_mock()

        # With force_refresh=True, should skip cache
        await service.enrich_vulnerabilities(
            cve_ids=["CVE-2024-0001"],
            sources=['nvd'],
            force_refresh=True
        )

        # Cache should NOT be checked
        assert not mock_cache.called


@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_5_failures():
    """
    RED TEST: Test circuit breaker opens after failure threshold.

    Circuit breaker should:
    1. Allow calls when CLOSED
    2. Open after 5 consecutive failures
    3. Block calls when OPEN
    """
    cb = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

    async def failing_func():
        raise Exception("API Error")

    # Initial state should be CLOSED
    assert cb.state == CircuitState.CLOSED

    # Fail 5 times
    for i in range(5):
        with pytest.raises(Exception):
            await cb.call(failing_func)

    # Circuit should now be OPEN
    assert cb.state == CircuitState.OPEN
    assert cb.failures == 5

    # 6th call should be blocked (not even attempted)
    with pytest.raises(CircuitBreakerOpenError) as exc_info:
        await cb.call(failing_func)

    assert "Circuit breaker is OPEN" in str(exc_info.value)


@pytest.mark.asyncio
async def test_circuit_breaker_resets_on_success():
    """
    RED TEST: Test circuit breaker resets failure count on success.
    """
    cb = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

    async def failing_func():
        raise Exception("API Error")

    async def success_func():
        return "success"

    # Fail 3 times
    for i in range(3):
        with pytest.raises(Exception):
            await cb.call(failing_func)

    assert cb.failures == 3
    assert cb.state == CircuitState.CLOSED  # Not yet open

    # Success should reset counter
    result = await cb.call(success_func)
    assert result == "success"
    assert cb.failures == 0
    assert cb.state == CircuitState.CLOSED


@pytest.mark.asyncio
async def test_circuit_breaker_half_open_after_timeout():
    """
    RED TEST: Test circuit breaker transitions to HALF_OPEN after timeout.
    """
    cb = CircuitBreaker(failure_threshold=5, timeout_seconds=0.1)  # 100ms timeout for testing

    async def failing_func():
        raise Exception("API Error")

    async def success_func():
        return "success"

    # Open the circuit
    for i in range(5):
        with pytest.raises(Exception):
            await cb.call(failing_func)

    assert cb.state == CircuitState.OPEN

    # Wait for timeout
    import asyncio
    await asyncio.sleep(0.2)  # Wait 200ms > 100ms timeout

    # Next call should transition to HALF_OPEN and succeed
    result = await cb.call(success_func)
    assert result == "success"
    assert cb.state == CircuitState.CLOSED  # Success closes it
    assert cb.failures == 0


@pytest.mark.asyncio
async def test_enrichment_creates_job_record():
    """
    RED TEST: Test that enrichment creates a job record in database.
    """
    service = EnrichmentService()

    # Mock database session
    with patch('src.services.enrichment_service.get_db') as mock_db:
        mock_session = AsyncMock()
        mock_db.return_value.__aenter__.return_value = mock_session

        result = await service.enrich_vulnerabilities(
            cve_ids=["CVE-2024-0001", "CVE-2024-0002"]
        )

        # Should have created a job record
        assert "job_id" in result
        assert result["job_id"] is not None

        # Session should have been used
        assert mock_session.add.called
        assert mock_session.commit.called


@pytest.mark.asyncio
async def test_enrichment_updates_job_status():
    """
    RED TEST: Test that enrichment updates job status as it progresses.
    """
    service = EnrichmentService()

    result = await service.enrich_vulnerabilities(
        cve_ids=["CVE-2024-0001"]
    )

    # Job should have a status
    assert "job_id" in result

    # Get job status
    status = await service.get_enrichment_status(result["job_id"])

    assert status["status"] in ["pending", "running", "completed", "failed"]
    assert "processed_items" in status
    assert "total_items" in status


@pytest.mark.asyncio
async def test_successful_enrichment_returns_results():
    """
    Test that successful enrichment returns proper result structure.

    Verifies:
    - job_id is present and valid UUID
    - total_items matches input count
    - processed_cves list is populated
    - sources dict contains status for each source
    - successful_sources count is accurate
    """
    service = EnrichmentService()

    async def mock_enrich(items):
        """Mock enrichment returning success"""
        return {
            "count": len(items),
            "failed": 0,
            "processed": list(items)
        }

    with patch('src.services.enrichment_service.NVDClient') as MockNVD, \
         patch('src.services.enrichment_service.EPSSClient') as MockEPSS:

        mock_nvd = AsyncMock()
        mock_nvd.enrich = AsyncMock(side_effect=mock_enrich)
        MockNVD.return_value = mock_nvd

        mock_epss = AsyncMock()
        mock_epss.enrich = AsyncMock(side_effect=mock_enrich)
        MockEPSS.return_value = mock_epss

        cve_ids = ["CVE-2024-0001", "CVE-2024-0002", "CVE-2024-0003"]
        result = await service.enrich_vulnerabilities(
            cve_ids=cve_ids,
            sources=['nvd', 'epss']
        )

        # Job ID should be a valid UUID string
        assert "job_id" in result
        assert len(result["job_id"]) == 36  # UUID format

        # Total items should match input
        assert result["total_items"] == len(cve_ids)

        # Processed CVEs should be populated
        assert "processed_cves" in result
        assert len(result["processed_cves"]) == len(cve_ids)

        # Sources should have status
        assert "sources" in result
        assert "nvd" in result["sources"]
        assert "epss" in result["sources"]
        assert result["sources"]["nvd"]["status"] == "success"
        assert result["sources"]["epss"]["status"] == "success"

        # Counts should be correct
        assert result["successful_sources"] == 2
        assert result["failed_sources"] == 0
        assert len(result["errors"]) == 0


@pytest.mark.asyncio
async def test_partial_failures_return_warning():
    """
    Test that partial source failures return warning info but don't fail the job.

    Verifies:
    - Enrichment completes (not fails) when some sources work
    - Failed sources are tracked in errors array
    - Error info contains source name, error message, and recoverable flag
    - Successful sources still provide data
    """
    service = EnrichmentService()

    async def mock_success(items):
        return {
            "count": len(items),
            "failed": 0,
            "processed": list(items)
        }

    with patch('src.services.enrichment_service.NVDClient') as MockNVD, \
         patch('src.services.enrichment_service.EPSSClient') as MockEPSS:

        # NVD succeeds
        mock_nvd = AsyncMock()
        mock_nvd.enrich = AsyncMock(side_effect=mock_success)
        MockNVD.return_value = mock_nvd

        # EPSS fails
        mock_epss = AsyncMock()
        mock_epss.enrich = AsyncMock(side_effect=Exception("EPSS API rate limit"))
        MockEPSS.return_value = mock_epss

        result = await service.enrich_vulnerabilities(
            cve_ids=["CVE-2024-0001"],
            sources=['nvd', 'epss']
        )

        # Job should complete (not fail entirely)
        assert result["successful_sources"] >= 1
        assert result["failed_sources"] == 1

        # Errors should be tracked
        assert len(result["errors"]) == 1
        error = result["errors"][0]
        assert error["source"] == "epss"
        assert "EPSS API rate limit" in error["error"]
        assert error["recoverable"] is True

        # Successful source should still provide data
        assert result["sources"]["nvd"]["status"] == "success"
        assert result["sources"]["nvd"]["enriched_count"] == 1


@pytest.mark.asyncio
async def test_enrichment_with_empty_cve_list():
    """
    Test enrichment with empty CVE list returns valid empty result.
    """
    service = EnrichmentService()

    result = await service.enrich_vulnerabilities(
        cve_ids=[],
        sources=['nvd']
    )

    assert "job_id" in result
    assert result["total_items"] == 0
    assert len(result.get("processed_cves", [])) == 0


@pytest.mark.asyncio
async def test_enrichment_with_synthetic_source():
    """
    Test that synthetic source works without external API calls.
    """
    service = EnrichmentService()

    result = await service.enrich_vulnerabilities(
        cve_ids=["CVE-2024-0001"],
        sources=['synthetic']
    )

    assert result["successful_sources"] == 1
    assert result["sources"]["synthetic"]["status"] == "success"
    assert result["sources"]["synthetic"]["enriched_count"] == 1


@pytest.mark.asyncio
async def test_enrichment_status_not_found():
    """
    Test that getting status for non-existent job raises ValueError.
    """
    service = EnrichmentService()

    with pytest.raises(ValueError) as exc_info:
        await service.get_enrichment_status("non-existent-job-id")

    assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_enrichment_progress_calculation():
    """
    Test that progress is calculated correctly.
    """
    service = EnrichmentService()

    result = await service.enrich_vulnerabilities(
        cve_ids=["CVE-2024-0001", "CVE-2024-0002"]
    )

    status = await service.get_enrichment_status(result["job_id"])

    # Progress should be between 0 and 1
    assert 0 <= status["progress"] <= 1

    # If completed, progress should be 1.0
    if status["status"] == "completed":
        assert status["progress"] == 1.0


@pytest.mark.asyncio
async def test_circuit_breaker_integration_with_enrichment():
    """
    Test that circuit breaker protects enrichment from failing sources.
    """
    service = EnrichmentService()

    # Reset circuit breaker state for the test
    service.circuit_breakers['nvd'].reset()

    call_count = 0

    async def counting_failure(items):
        nonlocal call_count
        call_count += 1
        raise Exception("API Error")

    with patch('src.services.enrichment_service.NVDClient') as MockNVD:
        mock_nvd = AsyncMock()
        mock_nvd.enrich = AsyncMock(side_effect=counting_failure)
        MockNVD.return_value = mock_nvd

        # First 5 calls should go through (and fail)
        for i in range(5):
            await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-0001"],
                sources=['nvd']
            )

        initial_count = call_count

        # Circuit should be open - next calls should be blocked
        result = await service.enrich_vulnerabilities(
            cve_ids=["CVE-2024-0001"],
            sources=['nvd']
        )

        # No additional API calls made (circuit blocked them)
        assert call_count == initial_count

        # Error should indicate circuit breaker
        assert result["sources"]["nvd"]["status"] == "failed"
        assert "circuit" in result["sources"]["nvd"]["error"].lower()
