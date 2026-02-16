"""
Pytest configuration and shared fixtures for all tests.

This file provides reusable mock fixtures for API clients,
database sessions, and other common test dependencies.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any
from datetime import datetime


# ============================================================================
# Pytest Configuration
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Mock API Responses
# ============================================================================

@pytest.fixture
def mock_nvd_response() -> Dict[str, Any]:
    """Mock NVD API response for testing."""
    return {
        "vulnerabilities": [{
            "cve": {
                "id": "CVE-2024-0001",
                "sourceIdentifier": "cve@mitre.org",
                "published": "2024-01-01T12:00:00.000",
                "lastModified": "2024-02-13T10:30:00.000",
                "vulnStatus": "Analyzed",
                "descriptions": [
                    {
                        "lang": "en",
                        "value": "Test vulnerability description for testing purposes"
                    }
                ],
                "metrics": {
                    "cvssMetricV31": [{
                        "source": "nvd@nist.gov",
                        "type": "Primary",
                        "cvssData": {
                            "version": "3.1",
                            "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                            "baseScore": 9.8,
                            "baseSeverity": "CRITICAL"
                        }
                    }]
                },
                "weaknesses": [
                    {
                        "source": "nvd@nist.gov",
                        "type": "Primary",
                        "description": [{
                            "lang": "en",
                            "value": "CWE-79"
                        }]
                    }
                ],
                "configurations": [
                    {
                        "nodes": [{
                            "operator": "OR",
                            "cpeMatch": [{
                                "vulnerable": True,
                                "criteria": "cpe:2.3:a:vendor:product:1.0:*:*:*:*:*:*:*"
                            }]
                        }]
                    }
                ],
                "references": [
                    {
                        "url": "https://example.com/advisory",
                        "source": "cve@mitre.org"
                    }
                ]
            }
        }]
    }


@pytest.fixture
def mock_epss_response() -> Dict[str, Any]:
    """Mock EPSS API response for testing."""
    return {
        "status": "OK",
        "status-code": 200,
        "version": "1.0",
        "data": [{
            "cve": "CVE-2024-0001",
            "epss": "0.85123",
            "percentile": "0.95678",
            "date": "2024-02-13"
        }]
    }


@pytest.fixture
def mock_otx_response() -> Dict[str, Any]:
    """Mock AlienVault OTX API response for testing."""
    return {
        "indicator": "1.2.3.4",
        "type": "IPv4",
        "type_title": "IPv4",
        "pulse_info": {
            "count": 2,
            "pulses": [
                {
                    "id": "pulse1",
                    "name": "Malicious Infrastructure",
                    "description": "Known malicious infrastructure",
                    "created": "2024-01-15T10:30:00",
                    "modified": "2024-02-01T14:20:00",
                    "author_name": "SecurityResearcher",
                    "pulse_source": "api",
                    "TLP": "white",
                    "tags": ["malware", "botnet", "c2"],
                    "references": ["https://example.com/analysis"],
                    "attack_ids": [
                        {
                            "id": "T1071",
                            "name": "Application Layer Protocol"
                        },
                        {
                            "id": "T1095",
                            "name": "Non-Application Layer Protocol"
                        }
                    ]
                }
            ]
        }
    }


@pytest.fixture
def mock_abuseipdb_response() -> Dict[str, Any]:
    """Mock AbuseIPDB API response for testing."""
    return {
        "data": {
            "ipAddress": "1.2.3.4",
            "isPublic": True,
            "ipVersion": 4,
            "isWhitelisted": False,
            "abuseConfidenceScore": 100,
            "countryCode": "CN",
            "countryName": "China",
            "usageType": "Data Center/Web Hosting/Transit",
            "isp": "Test ISP",
            "domain": "test.example.com",
            "hostnames": ["malicious.example.com"],
            "totalReports": 50,
            "numDistinctUsers": 25,
            "lastReportedAt": "2024-02-13T10:00:00+00:00"
        }
    }


@pytest.fixture
def mock_greynoise_response() -> Dict[str, Any]:
    """Mock GreyNoise API response for testing."""
    return {
        "ip": "1.2.3.4",
        "noise": True,
        "riot": False,
        "classification": "malicious",
        "name": "Malicious Scanner",
        "link": "https://viz.greynoise.io/ip/1.2.3.4",
        "last_seen": "2024-02-13",
        "message": "Success"
    }


# ============================================================================
# Mock Client Fixtures
# ============================================================================

@pytest.fixture
def mock_nvd_client(mock_nvd_response):
    """Mock NVD client for testing."""
    client = MagicMock()
    client.fetch_cve = AsyncMock(return_value={
        "cve_id": "CVE-2024-0001",
        "cvss_v3_score": 9.8,
        "cvss_v3_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "cwe_ids": ["CWE-79"],
        "cpe_uris": ["cpe:2.3:a:vendor:product:1.0:*:*:*:*:*:*:*"],
        "references": ["https://example.com/advisory"],
        "description": "Test vulnerability description"
    })
    client.fetch_cves = AsyncMock(return_value={
        "CVE-2024-0001": {
            "cve_id": "CVE-2024-0001",
            "cvss_v3_score": 9.8
        }
    })
    client.close = AsyncMock()
    return client


@pytest.fixture
def mock_epss_client(mock_epss_response):
    """Mock EPSS client for testing."""
    client = MagicMock()
    client.fetch_score = AsyncMock(return_value={
        "cve_id": "CVE-2024-0001",
        "epss_score": 0.85123,
        "epss_percentile": 0.95678
    })
    client.fetch_scores = AsyncMock(return_value={
        "CVE-2024-0001": {
            "epss_score": 0.85123,
            "epss_percentile": 0.95678
        }
    })
    client.close = AsyncMock()
    return client


@pytest.fixture
def mock_otx_client(mock_otx_response):
    """Mock OTX client for testing."""
    client = MagicMock()
    client.fetch_ip_reputation = AsyncMock(return_value={
        "indicator_type": "ip",
        "indicator_value": "1.2.3.4",
        "reputation_score": 85,
        "pulse_count": 2,
        "tags": ["malware", "botnet", "c2"],
        "mitre_techniques": ["T1071", "T1095"]
    })
    client.close = AsyncMock()
    return client


@pytest.fixture
def mock_abuseipdb_client(mock_abuseipdb_response):
    """Mock AbuseIPDB client for testing."""
    client = MagicMock()
    client.fetch_ip_reputation = AsyncMock(return_value={
        "indicator_type": "ip",
        "indicator_value": "1.2.3.4",
        "abuse_confidence_score": 100,
        "country_code": "CN",
        "is_whitelisted": False,
        "total_reports": 50
    })
    client.close = AsyncMock()
    return client


@pytest.fixture
def mock_greynoise_client(mock_greynoise_response):
    """Mock GreyNoise client for testing."""
    client = MagicMock()
    client.fetch_ip_classification = AsyncMock(return_value={
        "indicator_type": "ip",
        "indicator_value": "1.2.3.4",
        "classification": "malicious",
        "noise": True,
        "riot": False,
        "last_seen": "2024-02-13"
    })
    client.close = AsyncMock()
    return client


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
async def mock_db_session():
    """Mock async database session for testing."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.close = AsyncMock()

    # Mock query results
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=None)
    result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
    session.execute.return_value = result

    return session


@pytest.fixture
def mock_async_session_maker(mock_db_session):
    """Mock async session maker for testing."""
    async def session_maker():
        return mock_db_session

    return session_maker


# ============================================================================
# Enrichment Service Fixtures
# ============================================================================

@pytest.fixture
def mock_enrichment_service(
    mock_nvd_client,
    mock_epss_client,
    mock_otx_client,
    mock_abuseipdb_client,
    mock_greynoise_client
):
    """Mock EnrichmentService with all clients mocked."""
    from src.services.enrichment_service import EnrichmentService

    service = EnrichmentService()

    # Replace real clients with mocks
    service.nvd_client = mock_nvd_client
    service.epss_client = mock_epss_client
    service.otx_client = mock_otx_client
    service.abuseipdb_client = mock_abuseipdb_client
    service.greynoise_client = mock_greynoise_client

    return service


# ============================================================================
# Synthetic Generator Fixtures
# ============================================================================

@pytest.fixture
def mock_recorded_future():
    """Mock RecordedFuture generator for testing."""
    from src.generators.enrichment.recorded_future_mock import RecordedFutureMock
    return RecordedFutureMock(seed=42)


@pytest.fixture
def mock_tenable_vpr():
    """Mock Tenable VPR generator for testing."""
    from src.generators.enrichment.tenable_mock import TenableVPRMock
    return TenableVPRMock(seed=42)


@pytest.fixture
def mock_crowdstrike():
    """Mock CrowdStrike generator for testing."""
    from src.generators.enrichment.crowdstrike_mock import CrowdStrikeSandboxMock
    return CrowdStrikeSandboxMock(seed=42)


# ============================================================================
# Utility Functions
# ============================================================================

def create_mock_http_response(status_code: int, json_data: Dict[str, Any]) -> MagicMock:
    """Create a mock HTTP response for testing."""
    response = MagicMock()
    response.status_code = status_code
    response.json = MagicMock(return_value=json_data)
    response.text = str(json_data)
    response.headers = {}
    return response


@pytest.fixture
def mock_http_response():
    """Factory fixture for creating mock HTTP responses."""
    return create_mock_http_response


# ============================================================================
# HTTP Client Fixtures
# ============================================================================

@pytest.fixture
async def client():
    """
    Async HTTP client for testing FastAPI endpoints.

    This fixture creates a test client that can make async requests
    to the FastAPI application.
    """
    from httpx import AsyncClient, ASGITransport
    from src.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
