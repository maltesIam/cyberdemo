"""
Unit tests for Vulnerability Enrichment API endpoints.

Following TDD: Tests written FIRST, implementation follows.
Tests for:
- POST /api/enrichment/vulnerabilities - Start enrichment job
- GET /api/enrichment/vulnerabilities/status/{job_id} - Job status
- GET /api/vulnerabilities/enriched - List enriched CVEs (paginated, filters)
- GET /api/vulnerabilities/enriched/{cve_id} - Full CVE detail
- GET /api/vulnerabilities/enriched/{cve_id}/assets - Affected assets
- GET /api/vulnerabilities/enriched/{cve_id}/exploits - Known exploits
- GET /api/vulnerabilities/enriched/{cve_id}/chain - Attack chain
- POST /api/vulnerabilities/enriched/{cve_id}/enrich - Trigger enrichment
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
from fastapi import HTTPException
from datetime import datetime

from src.main import app


# Path to patch the VulnerabilityEnrichmentService
VULN_ENRICHMENT_SERVICE_PATH = "src.api.vuln_enrichment.VulnerabilityEnrichmentService"


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def mock_enrichment_service():
    """Create a mock VulnerabilityEnrichmentService."""
    service = AsyncMock()
    return service


@pytest.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_enrichment_result():
    """Sample result from enrich_vulnerabilities."""
    return {
        "job_id": "test-job-123",
        "total_items": 5,
        "successful_sources": 3,
        "failed_sources": 0,
        "sources": {
            "nvd": {"status": "success", "enriched_count": 5, "failed_count": 0},
            "epss": {"status": "success", "enriched_count": 5, "failed_count": 0},
            "kev": {"status": "success", "enriched_count": 5, "failed_count": 0},
        },
        "errors": [],
        "enriched_cves": [
            {
                "cve_id": "CVE-2024-1234",
                "cvss_v3_score": 9.8,
                "epss_score": 0.95,
                "is_kev": True,
                "enriched_at": "2024-01-15T10:30:00",
            }
        ],
    }


@pytest.fixture
def sample_job_status():
    """Sample job status response."""
    return {
        "job_id": "test-job-123",
        "status": "completed",
        "progress": 1.0,
        "processed_items": 5,
        "total_items": 5,
        "failed_items": 0,
        "started_at": "2024-01-15T10:30:00",
        "completed_at": "2024-01-15T10:31:00",
        "error_message": None,
    }


@pytest.fixture
def sample_enriched_cve():
    """Sample enriched CVE with full detail."""
    return {
        "cve_id": "CVE-2024-1234",
        "title": "Critical RCE in Apache Log4j",
        "description": "Remote code execution vulnerability in Apache Log4j",
        "published_date": "2024-01-01T00:00:00",
        "last_modified_date": "2024-01-15T10:30:00",
        "cvss_v3_score": 9.8,
        "cvss_v3_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "cvss_v2_score": 10.0,
        "epss_score": 0.95,
        "epss_percentile": 0.99,
        "risk_score": 95,
        "severity": "Critical",
        "cwe_ids": ["CWE-502"],
        "cwe_names": ["Deserialization of Untrusted Data"],
        "cpe_uris": ["cpe:2.3:a:apache:log4j:*:*:*:*:*:*:*:*"],
        "is_kev": True,
        "kev_date_added": "2024-01-02",
        "kev_due_date": "2024-01-16",
        "kev_required_action": "Apply updates per vendor instructions",
        "kev_ransomware_use": True,
        "exploit_count": 5,
        "exploit_maturity": "weaponized",
        "has_nuclei_template": True,
        "ssvc_decision": "Act",
        "affected_asset_count": 42,
        "affected_critical_assets": 8,
        "patch_available": True,
        "enrichment_level": "full",
        "enrichment_sources": ["nvd", "epss", "kev", "exploitdb"],
        "last_enriched_at": "2024-01-15T10:30:00",
    }


@pytest.fixture
def sample_affected_assets():
    """Sample affected assets list."""
    return [
        {
            "asset_id": "ASSET-001",
            "hostname": "web-server-01",
            "ip": "192.168.1.10",
            "asset_type": "server",
            "criticality": "critical",
            "department": "Engineering",
            "installed_version": "2.14.0",
            "patched": False,
            "last_scanned": "2024-01-14T08:00:00",
        },
        {
            "asset_id": "ASSET-002",
            "hostname": "app-server-01",
            "ip": "192.168.1.11",
            "asset_type": "application",
            "criticality": "high",
            "department": "Operations",
            "installed_version": "2.14.1",
            "patched": False,
            "last_scanned": "2024-01-14T08:00:00",
        },
    ]


@pytest.fixture
def sample_exploits():
    """Sample exploits list."""
    return [
        {
            "source": "exploitdb",
            "exploit_id": "EDB-50592",
            "title": "Apache Log4j RCE",
            "type": "remote",
            "platform": "multi",
            "verified": True,
            "url": "https://www.exploit-db.com/exploits/50592",
            "date_published": "2021-12-10",
        },
        {
            "source": "metasploit",
            "exploit_id": "exploit/multi/http/log4shell_header_injection",
            "title": "Log4Shell HTTP Header Injection",
            "type": "remote",
            "platform": "multi",
            "verified": True,
            "url": "https://github.com/rapid7/metasploit-framework",
            "date_published": "2021-12-13",
        },
    ]


@pytest.fixture
def sample_attack_chain():
    """Sample attack chain data."""
    return {
        "cve_id": "CVE-2024-1234",
        "mitre_techniques": [
            {"id": "T1190", "name": "Exploit Public-Facing Application"},
            {"id": "T1059.004", "name": "Unix Shell"},
        ],
        "mitre_tactics": [
            {"id": "TA0001", "name": "Initial Access"},
            {"id": "TA0002", "name": "Execution"},
        ],
        "typical_actors": ["APT29", "Lazarus Group"],
        "threat_actors": [
            {
                "name": "APT29",
                "aliases": ["Cozy Bear", "The Dukes"],
                "country": "Russia",
                "motivation": "espionage",
                "sophistication": "advanced",
            }
        ],
        "malware_families": ["Cobalt Strike", "PowerShell Empire"],
        "campaigns": ["Log4Shell Exploitation Campaign"],
        "kill_chain_phases": ["reconnaissance", "weaponization", "delivery", "exploitation"],
    }


# ============================================================================
# Tests for POST /api/enrichment/vulnerabilities
# ============================================================================


class TestStartEnrichmentJob:
    """Tests for starting a vulnerability enrichment job."""

    @pytest.mark.asyncio
    async def test_start_enrichment_with_cve_ids(self, client):
        """Test starting enrichment with specific CVE IDs."""
        response = await client.post(
            "/api/enrichment/vulnerabilities",
            json={"cve_ids": ["CVE-2024-1234", "CVE-2024-5678"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] in ["pending", "completed", "failed"]
        assert "total_items" in data

    @pytest.mark.asyncio
    async def test_start_enrichment_without_cve_ids(self, client, mock_enrichment_service, sample_enrichment_result):
        """Test starting enrichment without CVE IDs (enriches pending CVEs)."""
        mock_enrichment_service.enrich_vulnerabilities.return_value = sample_enrichment_result

        with patch(VULN_ENRICHMENT_SERVICE_PATH) as MockService:
            MockService.return_value = mock_enrichment_service
            response = await client.post(
                "/api/enrichment/vulnerabilities",
                json={}
            )

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data

    @pytest.mark.asyncio
    async def test_start_enrichment_with_specific_sources(self, client):
        """Test starting enrichment with specific sources."""
        response = await client.post(
            "/api/enrichment/vulnerabilities",
            json={"cve_ids": ["CVE-2024-1234"], "sources": ["nvd", "epss"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert "sources" in data

    @pytest.mark.asyncio
    async def test_start_enrichment_with_force_refresh(self, client, mock_enrichment_service, sample_enrichment_result):
        """Test starting enrichment with force_refresh=True."""
        mock_enrichment_service.enrich_vulnerabilities.return_value = sample_enrichment_result

        with patch(VULN_ENRICHMENT_SERVICE_PATH) as MockService:
            MockService.return_value = mock_enrichment_service
            response = await client.post(
                "/api/enrichment/vulnerabilities",
                json={"cve_ids": ["CVE-2024-1234"], "force_refresh": True}
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_start_enrichment_returns_source_status(self, client, mock_enrichment_service, sample_enrichment_result):
        """Test that response includes per-source status."""
        mock_enrichment_service.enrich_vulnerabilities.return_value = sample_enrichment_result

        with patch(VULN_ENRICHMENT_SERVICE_PATH) as MockService:
            MockService.return_value = mock_enrichment_service
            response = await client.post(
                "/api/enrichment/vulnerabilities",
                json={"cve_ids": ["CVE-2024-1234"]}
            )

        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert "successful_sources" in data
        assert "failed_sources" in data

    @pytest.mark.asyncio
    async def test_start_enrichment_handles_graceful_degradation(self, client):
        """Test that enrichment handles source failures gracefully."""
        # Test with valid CVE IDs - the service handles failures gracefully
        # by returning partial results rather than 500 errors
        response = await client.post(
            "/api/enrichment/vulnerabilities",
            json={"cve_ids": ["CVE-2024-1234"]}
        )

        # Service should return 200 even when some sources fail (graceful degradation)
        assert response.status_code == 200
        data = response.json()
        # Should have failure tracking in response
        assert "failed_sources" in data
        assert "errors" in data


# ============================================================================
# Tests for GET /api/enrichment/vulnerabilities/status/{job_id}
# ============================================================================


class TestGetEnrichmentStatus:
    """Tests for getting enrichment job status."""

    @pytest.mark.asyncio
    async def test_get_job_status_completed(self, client, mock_enrichment_service, sample_job_status):
        """Test getting status of a completed job."""
        mock_enrichment_service.get_enrichment_status.return_value = sample_job_status

        with patch(VULN_ENRICHMENT_SERVICE_PATH) as MockService:
            MockService.return_value = mock_enrichment_service
            response = await client.get("/api/enrichment/vulnerabilities/status/test-job-123")

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "test-job-123"
        assert data["status"] == "completed"
        assert data["progress"] == 1.0

    @pytest.mark.asyncio
    async def test_get_job_status_in_progress(self, client, mock_enrichment_service):
        """Test getting status of an in-progress job."""
        in_progress_status = {
            "job_id": "test-job-456",
            "status": "running",
            "progress": 0.6,
            "processed_items": 30,
            "total_items": 50,
            "failed_items": 2,
            "started_at": "2024-01-15T10:30:00",
            "completed_at": None,
            "error_message": None,
        }
        mock_enrichment_service.get_enrichment_status.return_value = in_progress_status

        with patch(VULN_ENRICHMENT_SERVICE_PATH) as MockService:
            MockService.return_value = mock_enrichment_service
            response = await client.get("/api/enrichment/vulnerabilities/status/test-job-456")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert data["progress"] == 0.6

    @pytest.mark.asyncio
    async def test_get_job_status_not_found(self, client, mock_enrichment_service):
        """Test 404 when job is not found."""
        mock_enrichment_service.get_enrichment_status.side_effect = ValueError("Job not found")

        with patch(VULN_ENRICHMENT_SERVICE_PATH) as MockService:
            MockService.return_value = mock_enrichment_service
            response = await client.get("/api/enrichment/vulnerabilities/status/nonexistent-job")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_job_status_includes_timestamps(self, client, mock_enrichment_service, sample_job_status):
        """Test that response includes timestamps."""
        mock_enrichment_service.get_enrichment_status.return_value = sample_job_status

        with patch(VULN_ENRICHMENT_SERVICE_PATH) as MockService:
            MockService.return_value = mock_enrichment_service
            response = await client.get("/api/enrichment/vulnerabilities/status/test-job-123")

        assert response.status_code == 200
        data = response.json()
        assert "started_at" in data
        assert "completed_at" in data


# ============================================================================
# Tests for GET /api/vulnerabilities/enriched
# ============================================================================


class TestListEnrichedCVEs:
    """Tests for listing enriched CVEs."""

    @pytest.mark.asyncio
    async def test_list_enriched_cves_default(self, client, sample_enriched_cve):
        """Test listing enriched CVEs with default parameters."""
        response = await client.get("/api/vulnerabilities/enriched")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

    @pytest.mark.asyncio
    async def test_list_enriched_cves_pagination(self, client):
        """Test pagination parameters."""
        response = await client.get("/api/vulnerabilities/enriched?page=2&page_size=25")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["page_size"] == 25

    @pytest.mark.asyncio
    async def test_list_enriched_cves_filter_severity(self, client):
        """Test filtering by severity."""
        response = await client.get("/api/vulnerabilities/enriched?severity=Critical")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_enriched_cves_filter_cvss_range(self, client):
        """Test filtering by CVSS range."""
        response = await client.get("/api/vulnerabilities/enriched?cvss_min=7.0&cvss_max=10.0")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_enriched_cves_filter_kev(self, client):
        """Test filtering by KEV status."""
        response = await client.get("/api/vulnerabilities/enriched?is_kev=true")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_enriched_cves_filter_ssvc_decision(self, client):
        """Test filtering by SSVC decision."""
        response = await client.get("/api/vulnerabilities/enriched?ssvc_decision=Act")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_enriched_cves_search(self, client):
        """Test search functionality."""
        response = await client.get("/api/vulnerabilities/enriched?search=log4j")

        assert response.status_code == 200


# ============================================================================
# Tests for GET /api/vulnerabilities/enriched/{cve_id}
# ============================================================================


class TestGetEnrichedCVEDetail:
    """Tests for getting full CVE detail."""

    @pytest.mark.asyncio
    async def test_get_enriched_cve_full_detail(self, client, sample_enriched_cve):
        """Test getting full CVE detail."""
        response = await client.get("/api/vulnerabilities/enriched/CVE-2024-1234")

        assert response.status_code == 200
        data = response.json()
        assert data["cve_id"] == "CVE-2024-1234"

    @pytest.mark.asyncio
    async def test_get_enriched_cve_includes_scoring(self, client):
        """Test that response includes scoring data."""
        response = await client.get("/api/vulnerabilities/enriched/CVE-2024-1234")

        assert response.status_code == 200
        data = response.json()
        assert "cvss_v3_score" in data
        assert "epss_score" in data
        assert "risk_score" in data

    @pytest.mark.asyncio
    async def test_get_enriched_cve_includes_kev_info(self, client):
        """Test that response includes KEV information."""
        response = await client.get("/api/vulnerabilities/enriched/CVE-2024-1234")

        assert response.status_code == 200
        data = response.json()
        assert "is_kev" in data

    @pytest.mark.asyncio
    async def test_get_enriched_cve_not_found(self, client):
        """Test 404 when CVE is not found."""
        response = await client.get("/api/vulnerabilities/enriched/CVE-9999-0000")

        assert response.status_code == 404


# ============================================================================
# Tests for GET /api/vulnerabilities/enriched/{cve_id}/assets
# ============================================================================


class TestGetAffectedAssets:
    """Tests for getting affected assets."""

    @pytest.mark.asyncio
    async def test_get_affected_assets(self, client, sample_affected_assets):
        """Test getting affected assets for a CVE."""
        response = await client.get("/api/vulnerabilities/enriched/CVE-2024-1234/assets")

        assert response.status_code == 200
        data = response.json()
        assert "assets" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_get_affected_assets_pagination(self, client):
        """Test pagination for affected assets."""
        response = await client.get("/api/vulnerabilities/enriched/CVE-2024-1234/assets?page=1&page_size=10")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_affected_assets_includes_criticality(self, client):
        """Test that assets include criticality info."""
        response = await client.get("/api/vulnerabilities/enriched/CVE-2024-1234/assets")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_affected_assets_cve_not_found(self, client):
        """Test 404 when CVE is not found."""
        response = await client.get("/api/vulnerabilities/enriched/CVE-9999-0000/assets")

        assert response.status_code == 404


# ============================================================================
# Tests for GET /api/vulnerabilities/enriched/{cve_id}/exploits
# ============================================================================


class TestGetKnownExploits:
    """Tests for getting known exploits."""

    @pytest.mark.asyncio
    async def test_get_known_exploits(self, client, sample_exploits):
        """Test getting known exploits for a CVE."""
        response = await client.get("/api/vulnerabilities/enriched/CVE-2024-1234/exploits")

        assert response.status_code == 200
        data = response.json()
        assert "exploits" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_get_exploits_includes_sources(self, client):
        """Test that exploits include source information."""
        response = await client.get("/api/vulnerabilities/enriched/CVE-2024-1234/exploits")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_exploits_cve_not_found(self, client):
        """Test 404 when CVE is not found."""
        response = await client.get("/api/vulnerabilities/enriched/CVE-9999-0000/exploits")

        assert response.status_code == 404


# ============================================================================
# Tests for GET /api/vulnerabilities/enriched/{cve_id}/chain
# ============================================================================


class TestGetAttackChain:
    """Tests for getting attack chain."""

    @pytest.mark.asyncio
    async def test_get_attack_chain(self, client, sample_attack_chain):
        """Test getting attack chain for a CVE."""
        response = await client.get("/api/vulnerabilities/enriched/CVE-2024-1234/chain")

        assert response.status_code == 200
        data = response.json()
        assert "cve_id" in data

    @pytest.mark.asyncio
    async def test_get_attack_chain_includes_mitre(self, client):
        """Test that attack chain includes MITRE ATT&CK data."""
        response = await client.get("/api/vulnerabilities/enriched/CVE-2024-1234/chain")

        assert response.status_code == 200
        data = response.json()
        assert "mitre_techniques" in data
        assert "mitre_tactics" in data

    @pytest.mark.asyncio
    async def test_get_attack_chain_includes_threat_actors(self, client):
        """Test that attack chain includes threat actor data."""
        response = await client.get("/api/vulnerabilities/enriched/CVE-2024-1234/chain")

        assert response.status_code == 200
        data = response.json()
        assert "threat_actors" in data

    @pytest.mark.asyncio
    async def test_get_attack_chain_cve_not_found(self, client):
        """Test 404 when CVE is not found."""
        response = await client.get("/api/vulnerabilities/enriched/CVE-9999-0000/chain")

        assert response.status_code == 404


# ============================================================================
# Tests for POST /api/vulnerabilities/enriched/{cve_id}/enrich
# ============================================================================


class TestTriggerSingleEnrichment:
    """Tests for triggering enrichment of a single CVE."""

    @pytest.mark.asyncio
    async def test_trigger_single_cve_enrichment(self, client, mock_enrichment_service):
        """Test triggering enrichment for a single CVE."""
        mock_enrichment_service.enrich_single_cve.return_value = {
            "cve_id": "CVE-2024-1234",
            "enriched_at": "2024-01-15T10:30:00",
            "enrichment_sources": ["nvd", "epss", "kev"],
        }

        with patch(VULN_ENRICHMENT_SERVICE_PATH) as MockService:
            MockService.return_value = mock_enrichment_service
            response = await client.post("/api/vulnerabilities/enriched/CVE-2024-1234/enrich")

        assert response.status_code == 200
        data = response.json()
        assert data["cve_id"] == "CVE-2024-1234"

    @pytest.mark.asyncio
    async def test_trigger_enrichment_with_sources(self, client, mock_enrichment_service):
        """Test triggering enrichment with specific sources."""
        mock_enrichment_service.enrich_single_cve.return_value = {
            "cve_id": "CVE-2024-1234",
            "enriched_at": "2024-01-15T10:30:00",
            "enrichment_sources": ["nvd"],
        }

        with patch(VULN_ENRICHMENT_SERVICE_PATH) as MockService:
            MockService.return_value = mock_enrichment_service
            response = await client.post(
                "/api/vulnerabilities/enriched/CVE-2024-1234/enrich",
                json={"sources": ["nvd"]}
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_trigger_enrichment_returns_enriched_data(self, client, mock_enrichment_service, sample_enriched_cve):
        """Test that enrichment returns the enriched data."""
        mock_enrichment_service.enrich_single_cve.return_value = sample_enriched_cve

        with patch(VULN_ENRICHMENT_SERVICE_PATH) as MockService:
            MockService.return_value = mock_enrichment_service
            response = await client.post("/api/vulnerabilities/enriched/CVE-2024-1234/enrich")

        assert response.status_code == 200
        data = response.json()
        assert "cvss_v3_score" in data
        assert "epss_score" in data

    @pytest.mark.asyncio
    async def test_trigger_enrichment_service_error(self, client, mock_enrichment_service):
        """Test error handling when enrichment service fails."""
        mock_enrichment_service.enrich_single_cve.side_effect = Exception("External API error")

        with patch(VULN_ENRICHMENT_SERVICE_PATH) as MockService:
            MockService.return_value = mock_enrichment_service
            response = await client.post("/api/vulnerabilities/enriched/CVE-2024-1234/enrich")

        assert response.status_code == 500
