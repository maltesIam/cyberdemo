"""
Quick integration tests for API clients.

These tests verify the client implementations with proper mocking
to avoid making real API calls.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# Import all clients
from src.clients import (
    NVDClient,
    EPSSClient,
    OTXClient,
    AbuseIPDBClient,
    GreyNoiseClient,
)


@pytest.mark.asyncio
async def test_all_clients_instantiate():
    """Test that all clients can be instantiated."""
    nvd = NVDClient()
    epss = EPSSClient()
    otx = OTXClient(api_key="test")
    abuse = AbuseIPDBClient(api_key="test")
    grey = GreyNoiseClient(api_key="test")

    # All clients should have required methods
    assert hasattr(nvd, 'fetch_cve')
    assert hasattr(epss, 'fetch_score')
    assert hasattr(otx, 'fetch_ip_reputation')
    assert hasattr(abuse, 'fetch_ip_reputation')
    assert hasattr(grey, 'fetch_ip_classification')

    # Clean up
    await nvd.close()
    await epss.close()
    await otx.close()
    await abuse.close()
    await grey.close()


@pytest.mark.asyncio
async def test_nvd_client_with_mock():
    """Test NVD client with mocked response."""
    client = NVDClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "vulnerabilities": [{
            "cve": {
                "id": "CVE-2024-0001",
                "metrics": {
                    "cvssMetricV31": [{
                        "cvssData": {
                            "baseScore": 9.8,
                            "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
                        }
                    }]
                },
                "weaknesses": [],
                "configurations": [],
                "references": [],
                "descriptions": [{"lang": "en", "value": "Test vulnerability"}],
                "published": "2024-01-01",
                "lastModified": "2024-02-13"
            }
        }]
    }

    with patch.object(client.client, 'get', return_value=mock_response):
        result = await client.fetch_cve("CVE-2024-0001")

        assert result is not None
        assert result["cve_id"] == "CVE-2024-0001"
        assert result["cvss_v3_score"] == 9.8

    await client.close()


@pytest.mark.asyncio
async def test_epss_client_with_mock():
    """Test EPSS client with mocked response."""
    client = EPSSClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "OK",
        "data": [{
            "cve": "CVE-2024-0001",
            "epss": "0.85123",
            "percentile": "0.95678"
        }]
    }

    with patch.object(client.client, 'get', return_value=mock_response):
        result = await client.fetch_score("CVE-2024-0001")

        assert result is not None
        assert result["cve_id"] == "CVE-2024-0001"
        assert 0.0 <= result["epss_score"] <= 1.0
        assert 0.0 <= result["epss_percentile"] <= 1.0

    await client.close()


@pytest.mark.asyncio
async def test_otx_client_with_mock():
    """Test OTX client with mocked response."""
    client = OTXClient(api_key="test-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "pulse_info": {
            "pulses": [
                {
                    "id": "pulse1",
                    "name": "Test Pulse",
                    "created": "2024-01-01",
                    "author_name": "Test Author",
                    "tags": ["malware", "botnet"],
                    "attack_ids": [
                        {"id": "T1071", "name": "Application Layer Protocol"}
                    ]
                }
            ]
        }
    }

    with patch.object(client.client, 'get', return_value=mock_response):
        result = await client.fetch_ip_reputation("1.2.3.4")

        assert result is not None
        assert result["indicator_type"] == "ip"
        assert result["reputation_score"] >= 0

    await client.close()


@pytest.mark.asyncio
async def test_abuseipdb_client_with_mock():
    """Test AbuseIPDB client with mocked response."""
    client = AbuseIPDBClient(api_key="test-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "ipAddress": "1.2.3.4",
            "isWhitelisted": False,
            "abuseConfidenceScore": 100,
            "countryCode": "CN",
            "totalReports": 50
        }
    }

    with patch.object(client.client, 'get', return_value=mock_response):
        result = await client.fetch_ip_reputation("1.2.3.4")

        assert result is not None
        assert result["indicator_type"] == "ip"
        assert 0 <= result["abuse_confidence_score"] <= 100

    await client.close()


@pytest.mark.asyncio
async def test_greynoise_client_with_mock():
    """Test GreyNoise client with mocked response."""
    client = GreyNoiseClient(api_key="test-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ip": "1.2.3.4",
        "noise": True,
        "riot": False,
        "classification": "malicious",
        "name": "Malicious Scanner",
        "last_seen": "2024-02-13"
    }

    with patch.object(client.client, 'get', return_value=mock_response):
        result = await client.fetch_ip_classification("1.2.3.4")

        assert result is not None
        assert result["indicator_type"] == "ip"
        assert result["classification"] in ["benign", "malicious", "unknown"]

    await client.close()


@pytest.mark.asyncio
async def test_all_clients_handle_errors():
    """Test that all clients handle errors gracefully."""

    # Test NVD
    nvd = NVDClient()
    mock_response = MagicMock()
    mock_response.status_code = 500
    with patch.object(nvd.client, 'get', return_value=mock_response):
        result = await nvd.fetch_cve("CVE-2024-0001")
        assert result is None
    await nvd.close()

    # Test EPSS
    epss = EPSSClient()
    with patch.object(epss.client, 'get', return_value=mock_response):
        result = await epss.fetch_score("CVE-2024-0001")
        assert result is None
    await epss.close()

    # Test OTX
    otx = OTXClient(api_key="test")
    with patch.object(otx.client, 'get', return_value=mock_response):
        result = await otx.fetch_ip_reputation("1.2.3.4")
        assert result is None
    await otx.close()

    # Test AbuseIPDB
    abuse = AbuseIPDBClient(api_key="test")
    with patch.object(abuse.client, 'get', return_value=mock_response):
        result = await abuse.fetch_ip_reputation("1.2.3.4")
        assert result is None
    await abuse.close()

    # Test GreyNoise
    grey = GreyNoiseClient(api_key="test")
    with patch.object(grey.client, 'get', return_value=mock_response):
        result = await grey.fetch_ip_classification("1.2.3.4")
        assert result is None
    await grey.close()


@pytest.mark.asyncio
async def test_all_clients_respect_max_items():
    """Test that all clients respect MAX_ITEMS_PER_SOURCE limit."""

    # Test NVD
    nvd = NVDClient()
    cve_ids = [f"CVE-2024-{i:04d}" for i in range(200)]

    with patch.object(nvd, 'fetch_cve', return_value={"cve_id": "test"}):
        results = await nvd.fetch_cves(cve_ids)
        assert len(results) <= 100

    await nvd.close()

    # Test EPSS
    epss = EPSSClient()
    with patch.object(epss, 'fetch_score', return_value={"epss_score": 0.5}):
        results = await epss.fetch_scores(cve_ids)
        assert len(results) <= 100

    await epss.close()

    # Test AbuseIPDB
    abuse = AbuseIPDBClient(api_key="test")
    ips = [f"192.168.1.{i % 255}" for i in range(200)]

    with patch.object(abuse, 'fetch_ip_reputation', return_value={"abuse_confidence_score": 0}):
        results = await abuse.fetch_ips(ips)
        assert len(results) <= 100

    await abuse.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
