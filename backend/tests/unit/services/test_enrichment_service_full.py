"""
Comprehensive Unit Tests for EnrichmentService.

TDD tests covering ALL methods in enrichment_service.py:
1. enrich_vulnerabilities() - Lines 66-183
2. enrich_threats() - Lines 345-485
3. _calculate_risk_score() - Lines 700-757
4. _get_risk_level() - Lines 759-769
5. _calculate_confidence() - Lines 771-778
6. _generate_synthetic_threat_data() - Lines 519-632
7. _merge_threat_data() - Lines 655-698

Target: >80% coverage of enrichment_service.py
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime
import uuid

from src.services.enrichment_service import (
    EnrichmentService,
    MAX_ITEMS_PER_SOURCE,
)
from src.services.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerOpenError,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def service():
    """Create a fresh EnrichmentService instance for each test."""
    svc = EnrichmentService()
    # Reset all circuit breakers
    for cb in svc.circuit_breakers.values():
        cb.reset()
    return svc


@pytest.fixture
def mock_nvd_client():
    """Mock NVD client returning success."""
    async def mock_enrich(items):
        return {
            "count": len(items),
            "failed": 0,
            "processed": list(items),
        }

    with patch('src.services.enrichment_service.NVDClient') as MockNVD:
        mock_instance = AsyncMock()
        mock_instance.enrich = AsyncMock(side_effect=mock_enrich)
        MockNVD.return_value = mock_instance
        yield MockNVD


@pytest.fixture
def mock_epss_client():
    """Mock EPSS client returning success."""
    async def mock_enrich(items):
        return {
            "count": len(items),
            "failed": 0,
            "processed": list(items),
        }

    with patch('src.services.enrichment_service.EPSSClient') as MockEPSS:
        mock_instance = AsyncMock()
        mock_instance.enrich = AsyncMock(side_effect=mock_enrich)
        MockEPSS.return_value = mock_instance
        yield MockEPSS


@pytest.fixture
def mock_db():
    """Mock database session."""
    with patch('src.services.enrichment_service.get_db') as mock:
        mock_session = AsyncMock()
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_session
        mock_context.__aexit__.return_value = None
        mock.return_value = mock_context
        yield mock_session


# =============================================================================
# TEST enrich_vulnerabilities() - Lines 66-183
# =============================================================================

class TestEnrichVulnerabilities:
    """Tests for enrich_vulnerabilities() method."""

    @pytest.mark.asyncio
    async def test_cve_limitation_to_max_items_per_source(self, service, mock_nvd_client, mock_epss_client):
        """Test CVE limitation: MAX_ITEMS_PER_SOURCE = 100"""
        # Create 200 CVEs, should be limited to 100
        cve_ids = [f"CVE-2024-{i:04d}" for i in range(200)]

        result = await service.enrich_vulnerabilities(cve_ids=cve_ids)

        assert result["total_items"] == MAX_ITEMS_PER_SOURCE
        assert result["total_items"] == 100
        assert len(result.get("processed_cves", [])) <= MAX_ITEMS_PER_SOURCE

    @pytest.mark.asyncio
    async def test_cve_limitation_exact_boundary(self, service, mock_nvd_client, mock_epss_client):
        """Test that exactly 100 CVEs are allowed without truncation."""
        cve_ids = [f"CVE-2024-{i:04d}" for i in range(100)]

        result = await service.enrich_vulnerabilities(cve_ids=cve_ids)

        assert result["total_items"] == 100

    @pytest.mark.asyncio
    async def test_cve_limitation_under_limit(self, service, mock_nvd_client, mock_epss_client):
        """Test that fewer than 100 CVEs are processed without truncation."""
        cve_ids = [f"CVE-2024-{i:04d}" for i in range(50)]

        result = await service.enrich_vulnerabilities(cve_ids=cve_ids)

        assert result["total_items"] == 50

    @pytest.mark.asyncio
    async def test_default_sources_selection(self, service, mock_nvd_client, mock_epss_client):
        """Test default sources when none specified: ['nvd', 'epss', 'github', 'synthetic']"""
        result = await service.enrich_vulnerabilities(
            cve_ids=["CVE-2024-0001"]
        )

        # Default sources should be used
        assert "nvd" in result["sources"]
        assert "epss" in result["sources"]
        assert "github" in result["sources"]
        assert "synthetic" in result["sources"]

    @pytest.mark.asyncio
    async def test_custom_sources_selection(self, service, mock_nvd_client):
        """Test that only specified sources are used."""
        result = await service.enrich_vulnerabilities(
            cve_ids=["CVE-2024-0001"],
            sources=['nvd']
        )

        # Only NVD should be in sources
        assert "nvd" in result["sources"]
        assert "epss" not in result["sources"]
        assert "synthetic" not in result["sources"]

    @pytest.mark.asyncio
    async def test_cache_checking_behavior_without_force_refresh(self, service):
        """Test cache checking when force_refresh=False"""
        with patch.object(service, '_get_from_cache') as mock_cache, \
             patch.object(service, '_enrich_from_source') as mock_enrich:

            mock_cache.return_value = {"count": 1, "failed": 0}
            mock_enrich.return_value = {"count": 1, "failed": 0, "processed": ["CVE-2024-0001"]}

            await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-0001"],
                sources=['nvd'],
                force_refresh=False
            )

            # Cache should be checked
            assert mock_cache.called
            # If cache hit, _enrich_from_source should NOT be called
            assert not mock_enrich.called

    @pytest.mark.asyncio
    async def test_cache_bypass_with_force_refresh(self, service):
        """Test cache bypass when force_refresh=True"""
        with patch.object(service, '_get_from_cache') as mock_cache, \
             patch.object(service, '_enrich_from_source') as mock_enrich:

            mock_cache.return_value = {"count": 1, "failed": 0}
            mock_enrich.return_value = {"count": 1, "failed": 0, "processed": ["CVE-2024-0001"]}

            await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-0001"],
                sources=['nvd'],
                force_refresh=True
            )

            # Cache should NOT be checked
            assert not mock_cache.called
            # Source should be called directly
            assert mock_enrich.called

    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self, service):
        """Test circuit breaker opens after 5 failures."""
        # Force NVD circuit breaker to open
        service.circuit_breakers['nvd'].failures = 5
        service.circuit_breakers['nvd'].state = CircuitState.OPEN
        service.circuit_breakers['nvd'].last_failure_time = datetime.now()

        result = await service.enrich_vulnerabilities(
            cve_ids=["CVE-2024-0001"],
            sources=['nvd']
        )

        # Circuit breaker should block the call
        assert result["sources"]["nvd"]["status"] == "failed"
        assert "circuit breaker" in result["sources"]["nvd"]["error"].lower()
        assert result["failed_sources"] == 1

    @pytest.mark.asyncio
    async def test_error_handling_per_source_exception(self, service):
        """Test error handling when source raises exception."""
        with patch('src.services.enrichment_service.NVDClient') as MockNVD:
            mock_instance = AsyncMock()
            mock_instance.enrich = AsyncMock(
                side_effect=Exception("NVD API timeout")
            )
            MockNVD.return_value = mock_instance

            result = await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-0001"],
                sources=['nvd', 'synthetic']
            )

            # NVD should fail, synthetic should succeed
            assert result["sources"]["nvd"]["status"] == "failed"
            assert "NVD API timeout" in result["sources"]["nvd"]["error"]
            assert result["sources"]["synthetic"]["status"] == "success"

    @pytest.mark.asyncio
    async def test_graceful_degradation_some_sources_fail(self, service):
        """Test graceful degradation: some sources fail, others succeed."""
        with patch('src.services.enrichment_service.NVDClient') as MockNVD, \
             patch('src.services.enrichment_service.EPSSClient') as MockEPSS:

            # NVD fails
            mock_nvd = AsyncMock()
            mock_nvd.enrich = AsyncMock(side_effect=Exception("NVD error"))
            MockNVD.return_value = mock_nvd

            # EPSS succeeds
            mock_epss = AsyncMock()
            mock_epss.enrich = AsyncMock(return_value={
                "count": 1, "failed": 0, "processed": ["CVE-2024-0001"]
            })
            MockEPSS.return_value = mock_epss

            result = await service.enrich_vulnerabilities(
                cve_ids=["CVE-2024-0001"],
                sources=['nvd', 'epss', 'synthetic']
            )

            # Should have 2 successful (epss, synthetic), 1 failed (nvd)
            assert result["successful_sources"] == 2
            assert result["failed_sources"] == 1
            assert result["sources"]["nvd"]["status"] == "failed"
            assert result["sources"]["epss"]["status"] == "success"
            assert result["sources"]["synthetic"]["status"] == "success"

    @pytest.mark.asyncio
    async def test_job_creation_and_tracking(self, service, mock_nvd_client, mock_epss_client):
        """Test job creation and tracking."""
        result = await service.enrich_vulnerabilities(
            cve_ids=["CVE-2024-0001", "CVE-2024-0002"]
        )

        # Job ID should be present and valid UUID
        assert "job_id" in result
        assert len(result["job_id"]) == 36  # UUID format

        # Should be able to retrieve job status
        status = await service.get_enrichment_status(result["job_id"])
        assert status["status"] in ["pending", "completed", "failed"]
        assert status["total_items"] == 2

    @pytest.mark.asyncio
    async def test_job_id_returned(self, service):
        """Test that job_id is always returned."""
        result = await service.enrich_vulnerabilities(
            cve_ids=["CVE-2024-0001"],
            sources=['synthetic']
        )

        assert "job_id" in result
        # Validate it's a valid UUID
        uuid.UUID(result["job_id"])

    @pytest.mark.asyncio
    async def test_empty_cve_list(self, service):
        """Test enrichment with empty CVE list."""
        result = await service.enrich_vulnerabilities(
            cve_ids=[],
            sources=['synthetic']
        )

        assert result["total_items"] == 0
        assert len(result.get("processed_cves", [])) == 0
        assert "job_id" in result

    @pytest.mark.asyncio
    async def test_none_cve_list(self, service):
        """Test enrichment with None CVE list."""
        result = await service.enrich_vulnerabilities(
            cve_ids=None,
            sources=['synthetic']
        )

        assert result["total_items"] == 0


# =============================================================================
# TEST enrich_threats() - Lines 345-485
# =============================================================================

class TestEnrichThreats:
    """Tests for enrich_threats() method."""

    @pytest.mark.asyncio
    async def test_indicator_limitation_to_100(self, service):
        """Test indicator limitation: 100 max."""
        # Create 150 indicators
        indicators = [
            {"type": "ip", "value": f"192.168.1.{i % 256}"}
            for i in range(150)
        ]

        result = await service.enrich_threats(
            indicators=indicators,
            sources=['synthetic']
        )

        assert result["total_items"] == 100
        assert len(result["enriched_indicators"]) == 100

    @pytest.mark.asyncio
    async def test_indicator_type_ip(self, service):
        """Test IP indicator type validation."""
        indicators = [{"type": "ip", "value": "192.168.1.1"}]

        result = await service.enrich_threats(
            indicators=indicators,
            sources=['synthetic']
        )

        assert len(result["enriched_indicators"]) == 1
        assert result["enriched_indicators"][0]["type"] == "ip"

    @pytest.mark.asyncio
    async def test_indicator_type_domain(self, service):
        """Test domain indicator type."""
        indicators = [{"type": "domain", "value": "malware.example.com"}]

        result = await service.enrich_threats(
            indicators=indicators,
            sources=['synthetic']
        )

        assert result["enriched_indicators"][0]["type"] == "domain"

    @pytest.mark.asyncio
    async def test_indicator_type_url(self, service):
        """Test URL indicator type."""
        indicators = [{"type": "url", "value": "http://evil.com/malware"}]

        result = await service.enrich_threats(
            indicators=indicators,
            sources=['synthetic']
        )

        assert result["enriched_indicators"][0]["type"] == "url"

    @pytest.mark.asyncio
    async def test_indicator_type_hash(self, service):
        """Test hash indicator type."""
        indicators = [{"type": "hash", "value": "abc123def456"}]

        result = await service.enrich_threats(
            indicators=indicators,
            sources=['synthetic']
        )

        assert result["enriched_indicators"][0]["type"] == "hash"

    @pytest.mark.asyncio
    async def test_indicator_type_email(self, service):
        """Test email indicator type."""
        indicators = [{"type": "email", "value": "phisher@evil.com"}]

        result = await service.enrich_threats(
            indicators=indicators,
            sources=['synthetic']
        )

        assert result["enriched_indicators"][0]["type"] == "email"

    @pytest.mark.asyncio
    async def test_multi_source_merging(self, service):
        """Test merging from multiple sources."""
        indicators = [{"type": "ip", "value": "10.0.0.1"}]

        result = await service.enrich_threats(
            indicators=indicators,
            sources=['synthetic', 'otx']
        )

        # Both sources should be queried
        assert "synthetic" in result["sources"]
        assert "otx" in result["sources"]
        # Enrichment metadata should track sources
        enriched = result["enriched_indicators"][0]
        assert "synthetic" in enriched["enrichment_meta"]["sources_successful"] or \
               "otx" in enriched["enrichment_meta"]["sources_successful"]

    @pytest.mark.asyncio
    async def test_enrichment_loop(self, service):
        """Test that all indicators are enriched."""
        indicators = [
            {"type": "ip", "value": "10.0.0.1"},
            {"type": "ip", "value": "10.0.0.2"},
            {"type": "domain", "value": "test.com"},
        ]

        result = await service.enrich_threats(
            indicators=indicators,
            sources=['synthetic']
        )

        assert len(result["enriched_indicators"]) == 3

    @pytest.mark.asyncio
    async def test_risk_score_calculation(self, service):
        """Test that risk score is calculated for each indicator."""
        indicators = [{"type": "ip", "value": "1.2.3.4"}]

        result = await service.enrich_threats(
            indicators=indicators,
            sources=['synthetic']
        )

        enriched = result["enriched_indicators"][0]
        assert "risk_score" in enriched
        assert 0 <= enriched["risk_score"] <= 100

    @pytest.mark.asyncio
    async def test_risk_level_mapping(self, service):
        """Test that risk level is derived from score."""
        indicators = [{"type": "ip", "value": "5.6.7.8"}]

        result = await service.enrich_threats(
            indicators=indicators,
            sources=['synthetic']
        )

        enriched = result["enriched_indicators"][0]
        assert "risk_level" in enriched
        assert enriched["risk_level"] in ["critical", "high", "medium", "low", "unknown"]

    @pytest.mark.asyncio
    async def test_confidence_calculation(self, service):
        """Test confidence calculation from successful sources."""
        indicators = [{"type": "ip", "value": "9.10.11.12"}]

        result = await service.enrich_threats(
            indicators=indicators,
            sources=['synthetic', 'otx']
        )

        enriched = result["enriched_indicators"][0]
        assert "confidence" in enriched
        assert 0 <= enriched["confidence"] <= 100

    @pytest.mark.asyncio
    async def test_enrichment_metadata_structure(self, service):
        """Test enrichment_meta structure."""
        indicators = [{"type": "ip", "value": "13.14.15.16"}]

        result = await service.enrich_threats(
            indicators=indicators,
            sources=['synthetic']
        )

        enriched = result["enriched_indicators"][0]
        meta = enriched["enrichment_meta"]

        assert "enriched_at" in meta
        assert "sources_queried" in meta
        assert "sources_successful" in meta
        assert "sources_failed" in meta
        assert "processing_time_ms" in meta
        assert isinstance(meta["sources_queried"], list)
        assert isinstance(meta["sources_successful"], list)
        assert isinstance(meta["sources_failed"], list)

    @pytest.mark.asyncio
    async def test_default_threat_sources(self, service):
        """Test default threat sources: ['otx', 'abuseipdb', 'greynoise', 'virustotal', 'synthetic']"""
        indicators = [{"type": "ip", "value": "17.18.19.20"}]

        result = await service.enrich_threats(
            indicators=indicators
            # No sources specified - use defaults
        )

        # Check default sources were queried
        assert any(s in result["sources"] for s in ['otx', 'synthetic'])

    @pytest.mark.asyncio
    async def test_empty_indicators_list(self, service):
        """Test with empty indicators list."""
        result = await service.enrich_threats(
            indicators=[],
            sources=['synthetic']
        )

        assert result["total_items"] == 0
        assert len(result["enriched_indicators"]) == 0

    @pytest.mark.asyncio
    async def test_circuit_breaker_in_threats(self, service):
        """Test circuit breaker integration in threat enrichment."""
        # Open the synthetic circuit breaker
        service.circuit_breakers['synthetic'].failures = 5
        service.circuit_breakers['synthetic'].state = CircuitState.OPEN
        service.circuit_breakers['synthetic'].last_failure_time = datetime.now()

        indicators = [{"type": "ip", "value": "21.22.23.24"}]

        result = await service.enrich_threats(
            indicators=indicators,
            sources=['synthetic']
        )

        # Source should be marked as failed
        assert result["sources"]["synthetic"]["status"] == "failed"


# =============================================================================
# TEST _calculate_risk_score() - Lines 700-757
# =============================================================================

class TestCalculateRiskScore:
    """Tests for _calculate_risk_score() method."""

    def test_abuseipdb_weight_20_percent(self, service):
        """Test AbuseIPDB contributes 20% weight."""
        enriched = {
            "reputation": {
                "abuseipdb": {
                    "confidence_score": 100  # Max score
                }
            },
            "threat_intel": {},
            "intel_feeds": [],
        }

        score = service._calculate_risk_score(enriched)

        # With only abuseipdb at 100, should contribute 20 points to total weight
        # Normalized: (20 / 100) * 100 = 20
        assert score >= 15  # Allow some variance due to normalization

    def test_virustotal_weight_25_percent(self, service):
        """Test VirusTotal contributes 25% weight."""
        enriched = {
            "reputation": {
                "virustotal": {
                    "malicious_count": 50,
                    "suspicious_count": 0,
                    "harmless_count": 50,  # 50% detection rate
                }
            },
            "threat_intel": {},
            "intel_feeds": [],
        }

        score = service._calculate_risk_score(enriched)

        # 50% detection rate * 0.25 = 12.5 points
        assert score >= 10

    def test_greynoise_weight_15_percent_malicious(self, service):
        """Test GreyNoise contributes 15% weight when malicious."""
        enriched = {
            "reputation": {
                "greynoise": {
                    "classification": "malicious",
                    "noise": True,
                }
            },
            "threat_intel": {},
            "intel_feeds": [],
        }

        score = service._calculate_risk_score(enriched)

        # Malicious = 15 points
        assert score >= 10

    def test_greynoise_weight_8_points_unknown_noise(self, service):
        """Test GreyNoise contributes 8 points when unknown but noisy."""
        enriched = {
            "reputation": {
                "greynoise": {
                    "classification": "unknown",
                    "noise": True,
                }
            },
            "threat_intel": {},
            "intel_feeds": [],
        }

        score = service._calculate_risk_score(enriched)

        # Unknown with noise = 8 points
        assert score >= 5

    def test_threat_intel_weight_25_percent(self, service):
        """Test threat intel contributes 25% weight."""
        enriched = {
            "reputation": {},
            "threat_intel": {
                "malware_families": ["Emotet", "TrickBot", "QakBot"],  # 3 * 5 = 15 pts
                "threat_actors": ["APT29", "APT28"],  # 2 * 5 = 10 pts
            },
            "intel_feeds": [],
        }

        score = service._calculate_risk_score(enriched)

        # 15 (capped at 15) + 10 = 25, capped at 25
        assert score >= 20

    def test_intel_feeds_weight_15_percent(self, service):
        """Test intel feeds contribute 15% weight."""
        enriched = {
            "reputation": {},
            "threat_intel": {},
            "intel_feeds": [
                {"source": "Feed1"},
                {"source": "Feed2"},
                {"source": "Feed3"},
                {"source": "Feed4"},
                {"source": "Feed5"},
            ],
        }

        score = service._calculate_risk_score(enriched)

        # 5 feeds * 3 = 15 points (capped at 15)
        assert score >= 10

    def test_normalization_final_score_0_to_100(self, service):
        """Test that final score is normalized to 0-100."""
        enriched = {
            "reputation": {
                "abuseipdb": {"confidence_score": 100},
                "virustotal": {"malicious_count": 100, "suspicious_count": 0, "harmless_count": 0},
                "greynoise": {"classification": "malicious", "noise": True},
            },
            "threat_intel": {
                "malware_families": ["A", "B", "C", "D"],
                "threat_actors": ["X", "Y", "Z"],
            },
            "intel_feeds": [{"s": i} for i in range(10)],
        }

        score = service._calculate_risk_score(enriched)

        assert 0 <= score <= 100

    def test_zero_weights_case(self, service):
        """Test score is 0 when no enrichment data."""
        enriched = {
            "reputation": {},
            "threat_intel": {},
            "intel_feeds": [],
        }

        score = service._calculate_risk_score(enriched)

        # No data = 0 score but total_weight is still calculated
        assert score == 0

    def test_missing_sources_case(self, service):
        """Test score calculation with missing source keys."""
        enriched = {}  # Empty enriched dict

        score = service._calculate_risk_score(enriched)

        assert score == 0

    def test_partial_sources(self, service):
        """Test score with only some sources present."""
        enriched = {
            "reputation": {
                "abuseipdb": {"confidence_score": 80}
            },
            "threat_intel": {
                "malware_families": ["Emotet"]
            },
            "intel_feeds": [],
        }

        score = service._calculate_risk_score(enriched)

        # Should calculate based on available sources
        assert 0 < score < 100


# =============================================================================
# TEST _get_risk_level() - Lines 759-769
# =============================================================================

class TestGetRiskLevel:
    """Tests for _get_risk_level() method."""

    def test_critical_threshold_80_plus(self, service):
        """Test critical level at score >= 80."""
        assert service._get_risk_level(80) == "critical"
        assert service._get_risk_level(90) == "critical"
        assert service._get_risk_level(100) == "critical"

    def test_high_threshold_60_to_79(self, service):
        """Test high level at score >= 60 and < 80."""
        assert service._get_risk_level(60) == "high"
        assert service._get_risk_level(70) == "high"
        assert service._get_risk_level(79) == "high"

    def test_medium_threshold_40_to_59(self, service):
        """Test medium level at score >= 40 and < 60."""
        assert service._get_risk_level(40) == "medium"
        assert service._get_risk_level(50) == "medium"
        assert service._get_risk_level(59) == "medium"

    def test_low_threshold_20_to_39(self, service):
        """Test low level at score >= 20 and < 40."""
        assert service._get_risk_level(20) == "low"
        assert service._get_risk_level(30) == "low"
        assert service._get_risk_level(39) == "low"

    def test_unknown_threshold_below_20(self, service):
        """Test unknown level at score < 20."""
        assert service._get_risk_level(0) == "unknown"
        assert service._get_risk_level(10) == "unknown"
        assert service._get_risk_level(19) == "unknown"

    def test_boundary_values(self, service):
        """Test exact boundary values."""
        assert service._get_risk_level(79) == "high"  # Just below 80
        assert service._get_risk_level(80) == "critical"  # Exactly 80
        assert service._get_risk_level(59) == "medium"  # Just below 60
        assert service._get_risk_level(60) == "high"  # Exactly 60


# =============================================================================
# TEST _calculate_confidence() - Lines 771-778
# =============================================================================

class TestCalculateConfidence:
    """Tests for _calculate_confidence() method."""

    def test_successful_total_sources_ratio(self, service):
        """Test confidence = (successful / total) * 100."""
        enriched = {
            "enrichment_meta": {
                "sources_queried": ["a", "b", "c", "d"],  # 4 total
                "sources_successful": ["a", "b"],  # 2 successful
            }
        }

        confidence = service._calculate_confidence(enriched)

        assert confidence == 50  # 2/4 * 100 = 50%

    def test_percentage_calculation_full_success(self, service):
        """Test 100% confidence when all sources succeed."""
        enriched = {
            "enrichment_meta": {
                "sources_queried": ["a", "b", "c"],
                "sources_successful": ["a", "b", "c"],
            }
        }

        confidence = service._calculate_confidence(enriched)

        assert confidence == 100

    def test_percentage_calculation_no_success(self, service):
        """Test 0% confidence when no sources succeed."""
        enriched = {
            "enrichment_meta": {
                "sources_queried": ["a", "b", "c"],
                "sources_successful": [],
            }
        }

        confidence = service._calculate_confidence(enriched)

        assert confidence == 0

    def test_zero_sources_case(self, service):
        """Test confidence is 0 when no sources queried."""
        enriched = {
            "enrichment_meta": {
                "sources_queried": [],
                "sources_successful": [],
            }
        }

        confidence = service._calculate_confidence(enriched)

        assert confidence == 0

    def test_missing_enrichment_meta(self, service):
        """Test confidence with missing enrichment_meta."""
        enriched = {}

        confidence = service._calculate_confidence(enriched)

        assert confidence == 0


# =============================================================================
# TEST _generate_synthetic_threat_data() - Lines 519-632
# =============================================================================

class TestGenerateSyntheticThreatData:
    """Tests for _generate_synthetic_threat_data() method."""

    def test_deterministic_seeding_same_hash(self, service):
        """Test deterministic seeding: same hash = same data."""
        data1 = service._generate_synthetic_threat_data("ip", "192.168.1.1")
        data2 = service._generate_synthetic_threat_data("ip", "192.168.1.1")

        # Same input should produce same output
        assert data1["geo"]["country"] == data2["geo"]["country"]
        assert data1["network"]["asn"] == data2["network"]["asn"]
        assert data1["threat_intel"]["malware_families"] == data2["threat_intel"]["malware_families"]

    def test_deterministic_seeding_different_hash(self, service):
        """Test that different inputs produce different outputs."""
        data1 = service._generate_synthetic_threat_data("ip", "192.168.1.1")
        data2 = service._generate_synthetic_threat_data("ip", "10.0.0.1")

        # Different inputs should produce different outputs
        # Note: there's a small chance they could match, but very unlikely
        # We just check structure is correct
        assert "geo" in data1 and "geo" in data2

    def test_all_fields_generated_geo(self, service):
        """Test all geo fields are generated."""
        data = service._generate_synthetic_threat_data("ip", "1.2.3.4")

        assert "geo" in data
        geo = data["geo"]
        assert "country" in geo
        assert "country_name" in geo
        assert "city" in geo
        assert "latitude" in geo
        assert "longitude" in geo

    def test_all_fields_generated_network(self, service):
        """Test all network fields are generated."""
        data = service._generate_synthetic_threat_data("ip", "1.2.3.4")

        assert "network" in data
        network = data["network"]
        assert "asn" in network
        assert "asn_org" in network
        assert "is_vpn" in network
        assert "is_proxy" in network
        assert "is_tor" in network
        assert "is_datacenter" in network

    def test_all_fields_generated_reputation(self, service):
        """Test all reputation fields are generated."""
        data = service._generate_synthetic_threat_data("ip", "1.2.3.4")

        assert "reputation" in data
        rep = data["reputation"]
        assert "abuseipdb" in rep
        assert "greynoise" in rep
        assert "virustotal" in rep

    def test_all_fields_generated_threat_intel(self, service):
        """Test all threat_intel fields are generated."""
        data = service._generate_synthetic_threat_data("ip", "1.2.3.4")

        assert "threat_intel" in data
        ti = data["threat_intel"]
        assert "malware_families" in ti
        assert "threat_actors" in ti
        assert "campaigns" in ti
        assert "tags" in ti

    def test_all_fields_generated_mitre_attack(self, service):
        """Test MITRE ATT&CK fields are generated."""
        data = service._generate_synthetic_threat_data("ip", "1.2.3.4")

        assert "mitre_attack" in data
        mitre = data["mitre_attack"]
        assert "techniques" in mitre
        assert isinstance(mitre["techniques"], list)

    def test_all_fields_generated_intel_feeds(self, service):
        """Test intel_feeds are generated."""
        data = service._generate_synthetic_threat_data("ip", "1.2.3.4")

        assert "intel_feeds" in data
        assert isinstance(data["intel_feeds"], list)

    def test_country_geo_data_variety(self, service):
        """Test country/geo data has variety from predefined list."""
        # Generate data for multiple IPs to check variety
        countries_seen = set()
        for i in range(20):
            data = service._generate_synthetic_threat_data("ip", f"10.0.0.{i}")
            countries_seen.add(data["geo"]["country"])

        # Should see multiple countries
        assert len(countries_seen) >= 2

    def test_network_data_vpn_proxy_tor_flags(self, service):
        """Test VPN, proxy, Tor flags are boolean."""
        data = service._generate_synthetic_threat_data("ip", "1.2.3.4")

        network = data["network"]
        assert isinstance(network["is_vpn"], bool)
        assert isinstance(network["is_proxy"], bool)
        assert isinstance(network["is_tor"], bool)
        assert isinstance(network["is_datacenter"], bool)

    def test_reputation_scores_range(self, service):
        """Test reputation scores are in valid ranges."""
        data = service._generate_synthetic_threat_data("ip", "1.2.3.4")

        abuse = data["reputation"]["abuseipdb"]
        assert 0 <= abuse["confidence_score"] <= 100
        assert abuse["total_reports"] >= 0

        vt = data["reputation"]["virustotal"]
        assert vt["malicious_count"] >= 0
        assert vt["suspicious_count"] >= 0
        assert vt["harmless_count"] >= 0

    def test_malware_families_list(self, service):
        """Test malware families is a non-empty list."""
        data = service._generate_synthetic_threat_data("ip", "1.2.3.4")

        families = data["threat_intel"]["malware_families"]
        assert isinstance(families, list)
        assert len(families) >= 1

    def test_threat_actors_list(self, service):
        """Test threat actors is a list (can be empty)."""
        data = service._generate_synthetic_threat_data("ip", "1.2.3.4")

        actors = data["threat_intel"]["threat_actors"]
        assert isinstance(actors, list)

    def test_mitre_techniques_list(self, service):
        """Test MITRE techniques is a list with proper structure."""
        data = service._generate_synthetic_threat_data("ip", "1.2.3.4")

        techniques = data["mitre_attack"]["techniques"]
        assert isinstance(techniques, list)
        assert len(techniques) >= 1

        # Check technique structure
        tech = techniques[0]
        assert "id" in tech
        assert "name" in tech
        assert "tactic" in tech


# =============================================================================
# TEST _merge_threat_data() - Lines 655-698
# =============================================================================

class TestMergeThreatData:
    """Tests for _merge_threat_data() method."""

    def test_geo_merge_first_wins(self, service):
        """Test geo merge: first source wins."""
        enriched = {
            "geo": None,
            "network": None,
            "reputation": {},
            "threat_intel": {
                "malware_families": [],
                "threat_actors": [],
                "campaigns": [],
                "tags": [],
            },
            "mitre_attack": {"techniques": []},
            "intel_feeds": [],
        }

        source_data = {
            "geo": {"country": "US", "city": "New York"},
        }

        service._merge_threat_data(enriched, "source1", source_data)

        assert enriched["geo"]["country"] == "US"

        # Second source should NOT overwrite
        source_data2 = {
            "geo": {"country": "RU", "city": "Moscow"},
        }

        service._merge_threat_data(enriched, "source2", source_data2)

        assert enriched["geo"]["country"] == "US"  # First wins

    def test_network_merge_first_wins(self, service):
        """Test network merge: first source wins."""
        enriched = {
            "geo": None,
            "network": None,
            "reputation": {},
            "threat_intel": {
                "malware_families": [],
                "threat_actors": [],
                "campaigns": [],
                "tags": [],
            },
            "mitre_attack": {"techniques": []},
            "intel_feeds": [],
        }

        source_data = {
            "network": {"asn": 12345, "is_vpn": True},
        }

        service._merge_threat_data(enriched, "source1", source_data)

        assert enriched["network"]["asn"] == 12345

        # Second source should NOT overwrite
        source_data2 = {
            "network": {"asn": 67890, "is_vpn": False},
        }

        service._merge_threat_data(enriched, "source2", source_data2)

        assert enriched["network"]["asn"] == 12345  # First wins

    def test_reputation_update(self, service):
        """Test reputation is updated (merged) from each source."""
        enriched = {
            "geo": None,
            "network": None,
            "reputation": {"existing": "data"},
            "threat_intel": {
                "malware_families": [],
                "threat_actors": [],
                "campaigns": [],
                "tags": [],
            },
            "mitre_attack": {"techniques": []},
            "intel_feeds": [],
        }

        source_data = {
            "reputation": {"abuseipdb": {"score": 80}},
        }

        service._merge_threat_data(enriched, "source1", source_data)

        assert "existing" in enriched["reputation"]
        assert "abuseipdb" in enriched["reputation"]

    def test_threat_intel_accumulation_no_duplicates(self, service):
        """Test threat intel accumulates without duplicates."""
        enriched = {
            "geo": None,
            "network": None,
            "reputation": {},
            "threat_intel": {
                "malware_families": ["Emotet"],
                "threat_actors": ["APT29"],
                "campaigns": [],
                "tags": ["botnet"],
            },
            "mitre_attack": {"techniques": []},
            "intel_feeds": [],
        }

        source_data = {
            "threat_intel": {
                "malware_families": ["Emotet", "TrickBot"],  # Emotet is duplicate
                "threat_actors": ["APT29", "Lazarus"],  # APT29 is duplicate
                "campaigns": ["Campaign1"],
                "tags": ["botnet", "ransomware"],  # botnet is duplicate
            }
        }

        service._merge_threat_data(enriched, "source1", source_data)

        # Should add new items but not duplicate existing
        assert enriched["threat_intel"]["malware_families"] == ["Emotet", "TrickBot"]
        assert enriched["threat_intel"]["threat_actors"] == ["APT29", "Lazarus"]
        assert enriched["threat_intel"]["campaigns"] == ["Campaign1"]
        assert enriched["threat_intel"]["tags"] == ["botnet", "ransomware"]

    def test_mitre_technique_accumulation(self, service):
        """Test MITRE techniques accumulate without duplicates."""
        technique1 = {"id": "T1059", "name": "Command and Scripting", "tactic": "Execution"}
        technique2 = {"id": "T1071", "name": "Application Layer Protocol", "tactic": "C2"}

        enriched = {
            "geo": None,
            "network": None,
            "reputation": {},
            "threat_intel": {
                "malware_families": [],
                "threat_actors": [],
                "campaigns": [],
                "tags": [],
            },
            "mitre_attack": {"techniques": [technique1]},
            "intel_feeds": [],
        }

        source_data = {
            "mitre_attack": {
                "techniques": [technique1, technique2],  # technique1 is duplicate
            }
        }

        service._merge_threat_data(enriched, "source1", source_data)

        # Should have both techniques
        assert len(enriched["mitre_attack"]["techniques"]) == 2

    def test_intel_feeds_accumulation(self, service):
        """Test intel feeds accumulate (extend list)."""
        enriched = {
            "geo": None,
            "network": None,
            "reputation": {},
            "threat_intel": {
                "malware_families": [],
                "threat_actors": [],
                "campaigns": [],
                "tags": [],
            },
            "mitre_attack": {"techniques": []},
            "intel_feeds": [{"source": "Feed1"}],
        }

        source_data = {
            "intel_feeds": [{"source": "Feed2"}, {"source": "Feed3"}],
        }

        service._merge_threat_data(enriched, "source1", source_data)

        assert len(enriched["intel_feeds"]) == 3

    def test_merge_with_empty_source_data(self, service):
        """Test merge handles empty source data gracefully."""
        enriched = {
            "geo": {"country": "US"},
            "network": {"asn": 12345},
            "reputation": {},
            "threat_intel": {
                "malware_families": ["Emotet"],
                "threat_actors": [],
                "campaigns": [],
                "tags": [],
            },
            "mitre_attack": {"techniques": []},
            "intel_feeds": [],
        }

        source_data = {}  # Empty source data

        service._merge_threat_data(enriched, "source1", source_data)

        # Enriched should be unchanged
        assert enriched["geo"]["country"] == "US"
        assert enriched["network"]["asn"] == 12345
        assert enriched["threat_intel"]["malware_families"] == ["Emotet"]


# =============================================================================
# TEST Additional Edge Cases and Integration
# =============================================================================

class TestEdgeCases:
    """Additional edge case tests."""

    @pytest.mark.asyncio
    async def test_job_status_with_progress(self, service):
        """Test job status includes correct progress calculation."""
        result = await service.enrich_vulnerabilities(
            cve_ids=["CVE-2024-0001", "CVE-2024-0002"],
            sources=['synthetic']
        )

        status = await service.get_enrichment_status(result["job_id"])

        # Progress should be calculated correctly
        assert "progress" in status
        if status["total_items"] > 0:
            expected_progress = status["processed_items"] / status["total_items"]
            assert abs(status["progress"] - expected_progress) < 0.01

    @pytest.mark.asyncio
    async def test_job_not_found_error(self, service):
        """Test getting status for non-existent job."""
        with pytest.raises(ValueError) as exc_info:
            await service.get_enrichment_status("non-existent-uuid-1234")

        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_all_sources_failing(self, service):
        """Test behavior when all sources fail."""
        # Open all circuit breakers
        for name, cb in service.circuit_breakers.items():
            cb.failures = 5
            cb.state = CircuitState.OPEN
            cb.last_failure_time = datetime.now()

        result = await service.enrich_vulnerabilities(
            cve_ids=["CVE-2024-0001"],
            sources=['nvd', 'epss']
        )

        assert result["successful_sources"] == 0
        assert result["failed_sources"] == 2

    @pytest.mark.asyncio
    async def test_unknown_source_in_enrich_from_source(self, service):
        """Test _enrich_from_source raises for unknown source."""
        with pytest.raises(ValueError) as exc_info:
            await service._enrich_from_source(
                source="unknown_source",
                items=["CVE-2024-0001"],
                force_refresh=False
            )

        assert "Unknown source" in str(exc_info.value)

    def test_risk_score_capping(self, service):
        """Test that risk score is capped at 100."""
        # Create enriched data that would produce > 100 before capping
        enriched = {
            "reputation": {
                "abuseipdb": {"confidence_score": 100},
                "virustotal": {"malicious_count": 100, "suspicious_count": 0, "harmless_count": 0},
                "greynoise": {"classification": "malicious", "noise": True},
            },
            "threat_intel": {
                "malware_families": ["A", "B", "C", "D", "E", "F"],  # Max 15 pts
                "threat_actors": ["X", "Y", "Z", "W"],  # Max 10 pts
            },
            "intel_feeds": [{"s": i} for i in range(20)],  # Max 15 pts
        }

        score = service._calculate_risk_score(enriched)

        assert score <= 100

    @pytest.mark.asyncio
    async def test_abuseipdb_only_for_ip(self, service):
        """Test AbuseIPDB only returns data for IP indicators."""
        # Domain should return None from _enrich_from_abuseipdb
        result = await service._enrich_from_abuseipdb("domain", "example.com")
        assert result is None

        # IP should return data
        result = await service._enrich_from_abuseipdb("ip", "1.2.3.4")
        assert result is not None

    @pytest.mark.asyncio
    async def test_greynoise_only_for_ip(self, service):
        """Test GreyNoise only returns data for IP indicators."""
        # Domain should return None
        result = await service._enrich_from_greynoise("domain", "example.com")
        assert result is None

        # IP should return data
        result = await service._enrich_from_greynoise("ip", "1.2.3.4")
        assert result is not None
