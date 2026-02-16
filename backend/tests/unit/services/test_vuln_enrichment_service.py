"""
Unit Tests for VulnerabilityEnrichmentService.

TDD RED PHASE: All tests written BEFORE implementation.

This service orchestrates CVE enrichment from multiple sources:
- NVD (existing client)
- EPSS (existing client)
- KEV (existing client)
- GHSA (synthetic if not ready)
- OSV (existing client)
- ExploitDB (synthetic if not ready)

Key constraints:
- MAX_ITEMS_PER_SOURCE = 100
- CircuitBreaker for each API source
- Never fail entire enrichment if one source fails
- Support force_refresh to bypass cache
"""
import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime
import uuid

from src.services.vuln_enrichment_service import (
    VulnerabilityEnrichmentService,
    MAX_ITEMS_PER_SOURCE,
)
from src.services.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerOpenError,
)


# =============================================================================
# HELPER FOR ASYNC TESTS
# =============================================================================

def run_async(coro):
    """Run an async coroutine synchronously."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def service():
    """Create a fresh VulnerabilityEnrichmentService instance for each test."""
    svc = VulnerabilityEnrichmentService()
    # Reset all circuit breakers
    for cb in svc.circuit_breakers.values():
        cb.reset()
    return svc


# =============================================================================
# TEST 1: test_enrichment_limits_to_100_items
# =============================================================================

def test_enrichment_limits_to_100_items():
    """
    Test that enrichment limits to MAX_ITEMS_PER_SOURCE (100).
    CRITICAL: Never process more than 100 CVEs at once.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        # Mock NVD and EPSS clients
        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD, \
             patch('src.services.vuln_enrichment_service.EPSSClient') as MockEPSS, \
             patch('src.services.vuln_enrichment_service.KEVClient') as MockKEV:

            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(side_effect=lambda cves: {
                cve: {"cve_id": cve, "cvss_v3_score": 7.5}
                for cve in cves
            })
            MockNVD.return_value = mock_nvd

            mock_epss = AsyncMock()
            mock_epss.fetch_scores = AsyncMock(side_effect=lambda cves: {
                cve: {"epss_score": 0.5, "epss_percentile": 0.75}
                for cve in cves
            })
            MockEPSS.return_value = mock_epss

            mock_kev = AsyncMock()
            mock_kev.get_kev_for_cves = AsyncMock(return_value={})
            MockKEV.return_value = mock_kev

            # Attempt to enrich 200 CVEs
            cve_ids = [f"CVE-2024-{i:04d}" for i in range(200)]

            result = await service.enrich_vulnerabilities(cve_ids=cve_ids)

            # Must limit to 100
            assert result["total_items"] == 100
            assert result["total_items"] == MAX_ITEMS_PER_SOURCE
            assert len(result.get("enriched_cves", [])) <= MAX_ITEMS_PER_SOURCE

    run_async(_test())


# =============================================================================
# TEST 2: test_enrichment_with_specific_cve_ids
# =============================================================================

def test_enrichment_with_specific_cve_ids():
    """
    Test enrichment with specific CVE IDs.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD, \
             patch('src.services.vuln_enrichment_service.EPSSClient') as MockEPSS, \
             patch('src.services.vuln_enrichment_service.KEVClient') as MockKEV:

            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(side_effect=lambda cves: {
                cve: {"cve_id": cve, "cvss_v3_score": 7.5}
                for cve in cves
            })
            MockNVD.return_value = mock_nvd

            mock_epss = AsyncMock()
            mock_epss.fetch_scores = AsyncMock(side_effect=lambda cves: {
                cve: {"epss_score": 0.5, "epss_percentile": 0.75}
                for cve in cves
            })
            MockEPSS.return_value = mock_epss

            mock_kev = AsyncMock()
            mock_kev.get_kev_for_cves = AsyncMock(return_value={})
            MockKEV.return_value = mock_kev

            cve_ids = ["CVE-2024-0001", "CVE-2024-0002", "CVE-2024-0003"]

            result = await service.enrich_vulnerabilities(cve_ids=cve_ids)

            assert result["total_items"] == 3
            assert "job_id" in result
            assert len(result.get("enriched_cves", [])) == 3

    run_async(_test())


# =============================================================================
# TEST 3: test_enrichment_with_specific_sources
# =============================================================================

def test_enrichment_with_specific_sources():
    """
    Test that only specified sources are used when sources parameter is provided.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD:
            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(side_effect=lambda cves: {
                cve: {"cve_id": cve, "cvss_v3_score": 7.5}
                for cve in cves
            })
            MockNVD.return_value = mock_nvd

            result = await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-0001"],
                sources=['nvd']
            )

            # Only NVD should be in sources
            assert "nvd" in result["sources"]
            assert result["sources"]["nvd"]["status"] == "success"
            # Other sources should not be present
            assert "epss" not in result["sources"]
            assert "kev" not in result["sources"]

    run_async(_test())


# =============================================================================
# TEST 4: test_enrichment_returns_job_structure
# =============================================================================

def test_enrichment_returns_job_structure():
    """
    Test that enrichment returns the required job structure.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD, \
             patch('src.services.vuln_enrichment_service.EPSSClient') as MockEPSS:

            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(side_effect=lambda cves: {
                cve: {"cve_id": cve, "cvss_v3_score": 7.5}
                for cve in cves
            })
            MockNVD.return_value = mock_nvd

            mock_epss = AsyncMock()
            mock_epss.fetch_scores = AsyncMock(side_effect=lambda cves: {
                cve: {"epss_score": 0.5, "epss_percentile": 0.75}
                for cve in cves
            })
            MockEPSS.return_value = mock_epss

            result = await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-0001"],
                sources=['nvd', 'epss']
            )

            # Validate structure
            assert "job_id" in result
            assert len(result["job_id"]) == 36  # UUID format
            assert "total_items" in result
            assert isinstance(result["total_items"], int)
            assert "successful_sources" in result
            assert isinstance(result["successful_sources"], int)
            assert "failed_sources" in result
            assert isinstance(result["failed_sources"], int)
            assert "sources" in result
            assert isinstance(result["sources"], dict)
            assert "errors" in result
            assert isinstance(result["errors"], list)
            assert "enriched_cves" in result
            assert isinstance(result["enriched_cves"], list)

    run_async(_test())


# =============================================================================
# TEST 5: test_single_source_failure_does_not_block_others
# =============================================================================

def test_single_source_failure_does_not_block_others():
    """
    Test that a single source failure does not block other sources.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        # Reset circuit breakers
        for cb in service.circuit_breakers.values():
            cb.reset()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD, \
             patch('src.services.vuln_enrichment_service.EPSSClient') as MockEPSS:

            # NVD fails
            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(side_effect=Exception("NVD API timeout"))
            MockNVD.return_value = mock_nvd

            # EPSS succeeds
            mock_epss = AsyncMock()
            mock_epss.fetch_scores = AsyncMock(return_value={
                "CVE-2024-0001": {"epss_score": 0.5, "epss_percentile": 0.75}
            })
            MockEPSS.return_value = mock_epss

            result = await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-0001"],
                sources=['nvd', 'epss']
            )

            # NVD should fail, EPSS should succeed
            assert result["sources"]["nvd"]["status"] == "failed"
            assert result["sources"]["epss"]["status"] == "success"
            assert result["successful_sources"] >= 1
            assert result["failed_sources"] >= 1

    run_async(_test())


# =============================================================================
# TEST 6: test_multiple_source_failures_still_returns_results
# =============================================================================

def test_multiple_source_failures_still_returns_results():
    """
    Test that multiple source failures still return a valid result structure.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        # Reset and then open all circuit breakers to simulate failures
        for cb in service.circuit_breakers.values():
            cb.failures = 5
            cb.state = CircuitState.OPEN
            cb.last_failure_time = datetime.now()

        result = await service.enrich_vulnerabilities(
            cve_ids=["CVE-2024-0001"],
            sources=['nvd', 'epss', 'kev']
        )

        # All sources failed
        assert result["successful_sources"] == 0
        assert result["failed_sources"] == 3

        # But we still get a valid structure
        assert "job_id" in result
        assert "sources" in result
        assert "errors" in result
        assert len(result["errors"]) == 3

    run_async(_test())


# =============================================================================
# TEST 7: test_circuit_breaker_prevents_hammering
# =============================================================================

def test_circuit_breaker_prevents_hammering():
    """
    Test that circuit breaker prevents hammering of failing APIs.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        # Reset circuit breaker first
        service.circuit_breakers['nvd'].reset()

        call_count = 0

        async def counting_failure(cves):
            nonlocal call_count
            call_count += 1
            raise Exception("API Error")

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD:
            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(side_effect=counting_failure)
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

    run_async(_test())


# =============================================================================
# TEST 8: test_force_refresh_bypasses_cache
# =============================================================================

def test_force_refresh_bypasses_cache():
    """
    Test that force_refresh=True bypasses cache.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch.object(service, '_get_from_cache') as mock_cache, \
             patch.object(service, '_enrich_from_source') as mock_enrich:

            mock_cache.return_value = {"count": 1, "data": {"CVE-2024-0001": {}}}
            mock_enrich.return_value = {"count": 1, "failed": 0, "data": {"CVE-2024-0001": {}}}

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
            # Source should be called directly
            assert mock_enrich.called

    run_async(_test())


# =============================================================================
# TEST 9: test_merge_enrichments_combines_sources
# =============================================================================

def test_merge_enrichments_combines_sources():
    """
    Test that _merge_enrichments correctly combines data from multiple sources.
    """
    service = VulnerabilityEnrichmentService()

    enrichments = {
        "nvd": {
            "cvss_v3_score": 7.5,
            "cvss_v3_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
            "cwe_ids": ["CWE-79"],
        },
        "epss": {
            "epss_score": 0.5,
            "epss_percentile": 0.75,
        },
        "kev": {
            "is_kev": True,
            "ransomware_use": True,
        },
    }

    merged = service._merge_enrichments("CVE-2024-0001", enrichments)

    # All sources should be merged
    assert merged["cvss_v3_score"] == 7.5
    assert merged["epss_score"] == 0.5
    assert merged["is_kev"] is True
    assert merged["ransomware_use"] is True


# =============================================================================
# TEST 10: test_enrich_single_cve_returns_complete_data
# =============================================================================

def test_enrich_single_cve_returns_complete_data():
    """
    Test that enrich_single_cve returns complete enrichment data.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD, \
             patch('src.services.vuln_enrichment_service.EPSSClient') as MockEPSS, \
             patch('src.services.vuln_enrichment_service.KEVClient') as MockKEV:

            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(return_value={
                "CVE-2024-0001": {"cve_id": "CVE-2024-0001", "cvss_v3_score": 7.5}
            })
            MockNVD.return_value = mock_nvd

            mock_epss = AsyncMock()
            mock_epss.fetch_scores = AsyncMock(return_value={
                "CVE-2024-0001": {"epss_score": 0.5, "epss_percentile": 0.75}
            })
            MockEPSS.return_value = mock_epss

            mock_kev = AsyncMock()
            mock_kev.get_kev_for_cves = AsyncMock(return_value={
                "CVE-2024-0001": {"is_kev": True, "date_added": "2024-01-15"}
            })
            MockKEV.return_value = mock_kev

            result = await service.enrich_single_cve(
                cve_id="CVE-2024-0001",
                sources=['nvd', 'epss', 'kev']
            )

            # Should have CVE ID
            assert result.get("cve_id") == "CVE-2024-0001"
            # Should have enrichment data from each source
            assert "enrichment_sources" in result
            assert "enriched_at" in result

    run_async(_test())


# =============================================================================
# TEST 11: test_ssvc_decision_calculated
# =============================================================================

def test_ssvc_decision_calculated():
    """
    Test that SSVC decision is calculated for enriched CVEs.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD, \
             patch('src.services.vuln_enrichment_service.EPSSClient') as MockEPSS, \
             patch('src.services.vuln_enrichment_service.KEVClient') as MockKEV:

            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(return_value={
                "CVE-2024-0001": {"cve_id": "CVE-2024-0001", "cvss_v3_score": 9.0}
            })
            MockNVD.return_value = mock_nvd

            mock_epss = AsyncMock()
            mock_epss.fetch_scores = AsyncMock(return_value={
                "CVE-2024-0001": {"epss_score": 0.8, "epss_percentile": 0.95}
            })
            MockEPSS.return_value = mock_epss

            mock_kev = AsyncMock()
            mock_kev.get_kev_for_cves = AsyncMock(return_value={
                "CVE-2024-0001": {"is_kev": True, "date_added": "2024-01-15"}
            })
            MockKEV.return_value = mock_kev

            result = await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-0001"],
                sources=['nvd', 'epss', 'kev']
            )

            # Should have SSVC decision
            enriched = result.get("enriched_cves", [])
            assert len(enriched) > 0

            cve_data = enriched[0]
            assert "ssvc_decision" in cve_data
            assert cve_data["ssvc_decision"] in ["immediate", "out-of-cycle", "scheduled", "defer"]

    run_async(_test())


# =============================================================================
# TEST 12: test_risk_score_calculated
# =============================================================================

def test_risk_score_calculated():
    """
    Test that risk score is calculated for enriched CVEs.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD, \
             patch('src.services.vuln_enrichment_service.EPSSClient') as MockEPSS, \
             patch('src.services.vuln_enrichment_service.KEVClient') as MockKEV:

            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(return_value={
                "CVE-2024-0001": {"cve_id": "CVE-2024-0001", "cvss_v3_score": 7.5}
            })
            MockNVD.return_value = mock_nvd

            mock_epss = AsyncMock()
            mock_epss.fetch_scores = AsyncMock(return_value={
                "CVE-2024-0001": {"epss_score": 0.5, "epss_percentile": 0.75}
            })
            MockEPSS.return_value = mock_epss

            mock_kev = AsyncMock()
            mock_kev.get_kev_for_cves = AsyncMock(return_value={})
            MockKEV.return_value = mock_kev

            result = await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-0001"],
                sources=['nvd', 'epss', 'kev']
            )

            enriched = result.get("enriched_cves", [])
            assert len(enriched) > 0

            cve_data = enriched[0]
            assert "risk_score" in cve_data
            assert 0 <= cve_data["risk_score"] <= 100

    run_async(_test())


# =============================================================================
# TEST 13: test_kev_status_included
# =============================================================================

def test_kev_status_included():
    """
    Test that KEV (Known Exploited Vulnerabilities) status is included.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD, \
             patch('src.services.vuln_enrichment_service.KEVClient') as MockKEV:

            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(return_value={
                "CVE-2024-0001": {"cve_id": "CVE-2024-0001", "cvss_v3_score": 7.5}
            })
            MockNVD.return_value = mock_nvd

            mock_kev = AsyncMock()
            mock_kev.get_kev_for_cves = AsyncMock(return_value={
                "CVE-2024-0001": {"is_kev": True, "date_added": "2024-01-15"}
            })
            MockKEV.return_value = mock_kev

            result = await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-0001"],
                sources=['nvd', 'kev']
            )

            enriched = result.get("enriched_cves", [])
            assert len(enriched) > 0

            cve_data = enriched[0]
            assert "is_kev" in cve_data
            assert "kev_date_added" in cve_data or "date_added" in cve_data

    run_async(_test())


# =============================================================================
# TEST 14: test_exploit_data_included
# =============================================================================

def test_exploit_data_included():
    """
    Test that exploit data (EPSS score, exploit availability) is included.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD, \
             patch('src.services.vuln_enrichment_service.EPSSClient') as MockEPSS:

            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(return_value={
                "CVE-2024-0001": {"cve_id": "CVE-2024-0001", "cvss_v3_score": 7.5}
            })
            MockNVD.return_value = mock_nvd

            mock_epss = AsyncMock()
            mock_epss.fetch_scores = AsyncMock(return_value={
                "CVE-2024-0001": {"epss_score": 0.5, "epss_percentile": 0.75}
            })
            MockEPSS.return_value = mock_epss

            result = await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-0001"],
                sources=['nvd', 'epss']
            )

            enriched = result.get("enriched_cves", [])
            assert len(enriched) > 0

            cve_data = enriched[0]
            assert "epss_score" in cve_data
            assert "epss_percentile" in cve_data

    run_async(_test())


# =============================================================================
# TEST 15: test_package_data_included
# =============================================================================

def test_package_data_included():
    """
    Test that package/software data is included from OSV.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD, \
             patch('src.services.vuln_enrichment_service.OSVClient') as MockOSV:

            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(return_value={
                "CVE-2024-0001": {"cve_id": "CVE-2024-0001", "cvss_v3_score": 7.5}
            })
            MockNVD.return_value = mock_nvd

            mock_osv = AsyncMock()
            mock_osv.query_by_cve = AsyncMock(return_value=[{
                "osv_id": "GHSA-xxxx-0001",
                "cve_id": "CVE-2024-0001",
                "severity": "HIGH",
                "affected": [{"package": {"ecosystem": "npm", "name": "express"}}]
            }])
            MockOSV.return_value = mock_osv

            result = await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-0001"],
                sources=['nvd', 'osv']
            )

            enriched = result.get("enriched_cves", [])
            assert len(enriched) > 0

            cve_data = enriched[0]
            # Should have affected packages or OSV data
            assert "affected_packages" in cve_data or "osv_data" in cve_data

    run_async(_test())


# =============================================================================
# TEST 16: test_empty_cve_list_returns_empty_result
# =============================================================================

def test_empty_cve_list_returns_empty_result():
    """
    Test that empty CVE list returns valid empty result.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        result = await service.enrich_vulnerabilities(
            cve_ids=[],
            sources=['nvd']
        )

        assert result["total_items"] == 0
        assert len(result.get("enriched_cves", [])) == 0
        assert "job_id" in result

    run_async(_test())


# =============================================================================
# TEST 17: test_invalid_cve_id_handled_gracefully
# =============================================================================

def test_invalid_cve_id_handled_gracefully():
    """
    Test that invalid CVE IDs are handled gracefully.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD:
            mock_nvd = AsyncMock()
            # NVD returns None for invalid CVEs
            mock_nvd.fetch_cves = AsyncMock(return_value={
                "INVALID-CVE": None,
                "CVE-9999-99999": None,
            })
            MockNVD.return_value = mock_nvd

            result = await service.enrich_vulnerabilities(
                cve_ids=["INVALID-CVE", "CVE-9999-99999"],
                sources=['nvd']
            )

            # Should not crash
            assert "job_id" in result
            # Invalid CVEs should be tracked
            assert result["total_items"] == 2

    run_async(_test())


# =============================================================================
# TEST 18: test_enrichment_metadata_included
# =============================================================================

def test_enrichment_metadata_included():
    """
    Test that enrichment metadata is included in results.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD, \
             patch('src.services.vuln_enrichment_service.EPSSClient') as MockEPSS:

            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(return_value={
                "CVE-2024-0001": {"cve_id": "CVE-2024-0001", "cvss_v3_score": 7.5}
            })
            MockNVD.return_value = mock_nvd

            mock_epss = AsyncMock()
            mock_epss.fetch_scores = AsyncMock(return_value={
                "CVE-2024-0001": {"epss_score": 0.5, "epss_percentile": 0.75}
            })
            MockEPSS.return_value = mock_epss

            result = await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-0001"],
                sources=['nvd', 'epss']
            )

            enriched = result.get("enriched_cves", [])
            assert len(enriched) > 0

            cve_data = enriched[0]
            assert "enriched_at" in cve_data
            assert "enrichment_sources" in cve_data
            assert isinstance(cve_data["enrichment_sources"], list)

    run_async(_test())


# =============================================================================
# TEST 19: test_sources_status_tracked
# =============================================================================

def test_sources_status_tracked():
    """
    Test that each source's status is tracked in the result.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD, \
             patch('src.services.vuln_enrichment_service.EPSSClient') as MockEPSS:

            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(return_value={
                "CVE-2024-0001": {"cve_id": "CVE-2024-0001", "cvss_v3_score": 7.5}
            })
            MockNVD.return_value = mock_nvd

            mock_epss = AsyncMock()
            mock_epss.fetch_scores = AsyncMock(return_value={
                "CVE-2024-0001": {"epss_score": 0.5, "epss_percentile": 0.75}
            })
            MockEPSS.return_value = mock_epss

            result = await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-0001"],
                sources=['nvd', 'epss']
            )

            # Sources should have status tracking
            assert "sources" in result
            assert "nvd" in result["sources"]
            assert "epss" in result["sources"]

            # Each source should have status and enriched_count
            assert result["sources"]["nvd"]["status"] == "success"
            assert "enriched_count" in result["sources"]["nvd"]

            assert result["sources"]["epss"]["status"] == "success"
            assert "enriched_count" in result["sources"]["epss"]

    run_async(_test())


# =============================================================================
# TEST 20: test_errors_collected_with_recoverable_flag
# =============================================================================

def test_errors_collected_with_recoverable_flag():
    """
    Test that errors are collected with recoverable flag.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        # Reset circuit breaker
        service.circuit_breakers['nvd'].reset()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD:
            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(side_effect=Exception("NVD API timeout"))
            MockNVD.return_value = mock_nvd

            result = await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-0001"],
                sources=['nvd']
            )

            # Errors should be collected
            assert len(result["errors"]) == 1

            error = result["errors"][0]
            assert "source" in error
            assert error["source"] == "nvd"
            assert "error" in error
            assert "recoverable" in error
            assert error["recoverable"] is True

    run_async(_test())


# =============================================================================
# TEST 21: test_get_pending_cves_from_db
# =============================================================================

def test_get_pending_cves_from_db():
    """
    Test that _get_pending_cves retrieves CVEs that need enrichment from DB.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        # Mock the database query
        with patch.object(service, '_get_pending_cves') as mock_get_pending:
            mock_get_pending.return_value = ["CVE-2024-0001", "CVE-2024-0002"]

            pending = await service._get_pending_cves(limit=100)

            assert len(pending) == 2
            assert "CVE-2024-0001" in pending

    run_async(_test())


# =============================================================================
# TEST 22: test_enrichment_with_none_cve_ids_gets_pending
# =============================================================================

def test_enrichment_with_none_cve_ids_gets_pending():
    """
    Test that if cve_ids is None, service gets pending CVEs from DB.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD, \
             patch('src.services.vuln_enrichment_service.EPSSClient') as MockEPSS, \
             patch('src.services.vuln_enrichment_service.KEVClient') as MockKEV, \
             patch.object(service, '_get_pending_cves') as mock_get_pending:

            mock_get_pending.return_value = ["CVE-2024-0001", "CVE-2024-0002"]

            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(side_effect=lambda cves: {
                cve: {"cve_id": cve, "cvss_v3_score": 7.5}
                for cve in cves
            })
            MockNVD.return_value = mock_nvd

            mock_epss = AsyncMock()
            mock_epss.fetch_scores = AsyncMock(side_effect=lambda cves: {
                cve: {"epss_score": 0.5, "epss_percentile": 0.75}
                for cve in cves
            })
            MockEPSS.return_value = mock_epss

            mock_kev = AsyncMock()
            mock_kev.get_kev_for_cves = AsyncMock(return_value={})
            MockKEV.return_value = mock_kev

            result = await service.enrich_vulnerabilities(
                cve_ids=None,  # Should trigger _get_pending_cves
                sources=['nvd', 'epss']
            )

            # Should have called _get_pending_cves
            mock_get_pending.assert_called_once()

            # Should have enriched the pending CVEs
            assert result["total_items"] == 2

    run_async(_test())


# =============================================================================
# TEST 23: test_calculate_ssvc_decision
# =============================================================================

def test_calculate_ssvc_decision():
    """
    Test SSVC decision calculation logic.
    """
    service = VulnerabilityEnrichmentService()

    # High exploit (KEV) + High impact (CVSS 9.0) = Immediate
    decision = service._calculate_ssvc_decision(
        is_kev=True,
        epss_score=0.8,
        cvss_score=9.0
    )
    assert decision == "immediate"

    # No KEV + High EPSS + High CVSS = Out-of-cycle
    decision = service._calculate_ssvc_decision(
        is_kev=False,
        epss_score=0.7,
        cvss_score=8.0
    )
    assert decision == "out-of-cycle"

    # Low exploit + Low impact = Defer
    decision = service._calculate_ssvc_decision(
        is_kev=False,
        epss_score=0.01,
        cvss_score=3.0
    )
    assert decision == "defer"


# =============================================================================
# TEST 24: test_calculate_risk_score
# =============================================================================

def test_calculate_risk_score():
    """
    Test risk score calculation combining multiple factors.
    """
    service = VulnerabilityEnrichmentService()

    # High risk: KEV + High EPSS + High CVSS
    score = service._calculate_risk_score(
        is_kev=True,
        epss_score=0.9,
        cvss_score=9.5
    )
    assert score >= 80

    # Medium risk
    score = service._calculate_risk_score(
        is_kev=False,
        epss_score=0.3,
        cvss_score=6.0
    )
    assert 30 <= score <= 70

    # Low risk
    score = service._calculate_risk_score(
        is_kev=False,
        epss_score=0.01,
        cvss_score=2.0
    )
    assert score <= 30


# =============================================================================
# TEST 25: test_synthetic_data_for_missing_sources
# =============================================================================

def test_synthetic_data_for_missing_sources():
    """
    Test that synthetic data is generated for sources that aren't ready.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        result = await service.enrich_vulnerabilities(
            cve_ids=["CVE-2024-0001"],
            sources=['exploitdb']  # This source uses synthetic data
        )

        # Should not crash and should have some result
        assert "job_id" in result
        assert "sources" in result
        # ExploitDB source should be tracked
        assert "exploitdb" in result["sources"]

    run_async(_test())


# =============================================================================
# TEST 26: test_default_sources_used_when_none_specified
# =============================================================================

def test_default_sources_used_when_none_specified():
    """
    Test that default sources are used when sources parameter is not provided.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD, \
             patch('src.services.vuln_enrichment_service.EPSSClient') as MockEPSS, \
             patch('src.services.vuln_enrichment_service.KEVClient') as MockKEV:

            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(return_value={
                "CVE-2024-0001": {"cve_id": "CVE-2024-0001", "cvss_v3_score": 7.5}
            })
            MockNVD.return_value = mock_nvd

            mock_epss = AsyncMock()
            mock_epss.fetch_scores = AsyncMock(return_value={
                "CVE-2024-0001": {"epss_score": 0.5, "epss_percentile": 0.75}
            })
            MockEPSS.return_value = mock_epss

            mock_kev = AsyncMock()
            mock_kev.get_kev_for_cves = AsyncMock(return_value={})
            MockKEV.return_value = mock_kev

            result = await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-0001"]
                # sources not specified
            )

            # Default sources should be used (nvd, epss, kev at minimum)
            assert "nvd" in result["sources"] or "epss" in result["sources"]

    run_async(_test())


# =============================================================================
# TEST 27: test_enrich_from_source_with_circuit_breaker
# =============================================================================

def test_enrich_from_source_with_circuit_breaker():
    """
    Test _enrich_from_source uses circuit breaker protection.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        # Open the circuit breaker
        service.circuit_breakers['nvd'].failures = 5
        service.circuit_breakers['nvd'].state = CircuitState.OPEN
        service.circuit_breakers['nvd'].last_failure_time = datetime.now()

        # Should raise CircuitBreakerOpenError
        with pytest.raises(CircuitBreakerOpenError):
            await service._enrich_from_source(
                source='nvd',
                cve_ids=["CVE-2024-0001"],
                force_refresh=False
            )

    run_async(_test())


# =============================================================================
# TEST 28: test_enrich_single_cve_full_flow
# =============================================================================

def test_enrich_single_cve_full_flow():
    """
    Test full flow of enriching a single CVE.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD, \
             patch('src.services.vuln_enrichment_service.EPSSClient') as MockEPSS, \
             patch('src.services.vuln_enrichment_service.KEVClient') as MockKEV:

            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(return_value={
                "CVE-2024-0001": {"cve_id": "CVE-2024-0001", "cvss_v3_score": 7.5}
            })
            MockNVD.return_value = mock_nvd

            mock_epss = AsyncMock()
            mock_epss.fetch_scores = AsyncMock(return_value={
                "CVE-2024-0001": {"epss_score": 0.5, "epss_percentile": 0.75}
            })
            MockEPSS.return_value = mock_epss

            mock_kev = AsyncMock()
            mock_kev.get_kev_for_cves = AsyncMock(return_value={
                "CVE-2024-0001": {"is_kev": True, "date_added": "2024-01-15"}
            })
            MockKEV.return_value = mock_kev

            result = await service.enrich_single_cve(
                cve_id="CVE-2024-0001",
                sources=['nvd', 'epss', 'kev']
            )

            # Should have all required fields
            assert result["cve_id"] == "CVE-2024-0001"
            assert "cvss_v3_score" in result
            assert "epss_score" in result
            assert "is_kev" in result
            assert "risk_score" in result
            assert "ssvc_decision" in result

    run_async(_test())


# =============================================================================
# TEST 29: test_batch_enrichment_performance
# =============================================================================

def test_batch_enrichment_performance():
    """
    Test that batch enrichment handles 100 CVEs efficiently.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD, \
             patch('src.services.vuln_enrichment_service.EPSSClient') as MockEPSS:

            mock_nvd = AsyncMock()
            mock_nvd.fetch_cves = AsyncMock(side_effect=lambda cves: {
                cve: {"cve_id": cve, "cvss_v3_score": 7.5}
                for cve in cves
            })
            MockNVD.return_value = mock_nvd

            mock_epss = AsyncMock()
            mock_epss.fetch_scores = AsyncMock(side_effect=lambda cves: {
                cve: {"epss_score": 0.5, "epss_percentile": 0.75}
                for cve in cves
            })
            MockEPSS.return_value = mock_epss

            cve_ids = [f"CVE-2024-{i:04d}" for i in range(100)]

            import time
            start = time.time()

            result = await service.enrich_vulnerabilities(
                cve_ids=cve_ids,
                sources=['nvd', 'epss']
            )

            elapsed = time.time() - start

            # Should complete within reasonable time (mocked)
            assert result["total_items"] == 100
            assert elapsed < 10  # Should be fast with mocks

    run_async(_test())


# =============================================================================
# TEST 30: test_cve_not_found_in_source
# =============================================================================

def test_cve_not_found_in_source():
    """
    Test handling of CVE not found in a specific source.
    """
    async def _test():
        service = VulnerabilityEnrichmentService()

        with patch('src.services.vuln_enrichment_service.NVDClient') as MockNVD:
            mock_nvd = AsyncMock()
            # NVD returns None for this CVE (not found)
            mock_nvd.fetch_cves = AsyncMock(return_value={
                "CVE-2024-9999": None
            })
            MockNVD.return_value = mock_nvd

            result = await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-9999"],
                sources=['nvd']
            )

            # Should handle gracefully
            assert result["total_items"] == 1
            # NVD should still report success (even if CVE not found)
            assert "nvd" in result["sources"]

    run_async(_test())
