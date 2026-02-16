"""
Integration tests for AlienVault OTX API Client.

AlienVault OTX (Open Threat Exchange) provides threat intelligence
including pulses, IOCs, malware families, and ATT&CK TTPs.

These tests are written FIRST following TDD.
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.clients.otx_client import OTXClient


@pytest.mark.asyncio
async def test_otx_fetch_ip_success():
    """
    RED: Test that OTXClient can fetch IP reputation successfully.
    """
    client = OTXClient(api_key="test-key")

    result = await client.fetch_ip_reputation("8.8.8.8")

    # Assertions
    assert result is not None
    assert "indicator_value" in result
    assert "indicator_type" in result
    assert "reputation_score" in result
    assert "malware_families" in result
    assert "threat_types" in result
    assert "pulses" in result

    # Validate data types
    assert isinstance(result["reputation_score"], (int, float))
    assert isinstance(result["malware_families"], list)
    assert isinstance(result["threat_types"], list)
    assert isinstance(result["pulses"], list)


@pytest.mark.asyncio
async def test_otx_fetch_domain_success():
    """
    RED: Test that OTXClient can fetch domain reputation.
    """
    client = OTXClient(api_key="test-key")

    result = await client.fetch_domain_reputation("example.com")

    assert result is not None
    assert result["indicator_type"] == "domain"
    assert "reputation_score" in result


@pytest.mark.asyncio
async def test_otx_fetch_hash_success():
    """
    RED: Test that OTXClient can fetch file hash reputation.
    """
    client = OTXClient(api_key="test-key")

    test_hash = "44d88612fea8a8f36de82e1278abb02f"  # Example MD5

    result = await client.fetch_hash_reputation(test_hash)

    assert result is not None
    assert result["indicator_type"] == "hash"
    assert "malware_families" in result


@pytest.mark.asyncio
async def test_otx_handles_api_error():
    """
    RED: Test that OTXClient handles API errors gracefully.
    """
    client = OTXClient(api_key="invalid-key")

    # Mock HTTP error
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=403,
            json=AsyncMock(return_value={"error": "Invalid API key"})
        )

        result = await client.fetch_ip_reputation("1.1.1.1")

        # Should return None on error
        assert result is None


@pytest.mark.asyncio
async def test_otx_handles_timeout():
    """
    RED: Test that OTXClient handles timeouts gracefully.
    """
    client = OTXClient(api_key="test-key", timeout=5)

    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = TimeoutError("Request timed out")

        result = await client.fetch_ip_reputation("1.1.1.1")

        assert result is None


@pytest.mark.asyncio
async def test_otx_fetch_multiple_indicators():
    """
    RED: Test batch fetching of multiple indicators.
    """
    client = OTXClient(api_key="test-key")

    indicators = [
        {"type": "ip", "value": "8.8.8.8"},
        {"type": "domain", "value": "example.com"},
        {"type": "hash", "value": "44d88612fea8a8f36de82e1278abb02f"}
    ]

    results = await client.fetch_indicators(indicators)

    assert isinstance(results, list)
    assert len(results) <= len(indicators)


@pytest.mark.asyncio
async def test_otx_respects_max_items_limit():
    """
    RED: Test that client respects MAX_ITEMS_PER_SOURCE limit (100).
    """
    client = OTXClient(api_key="test-key")

    # Try to fetch 200 indicators
    indicators = [
        {"type": "ip", "value": f"192.168.1.{i}"}
        for i in range(200)
    ]

    results = await client.fetch_indicators(indicators)

    # Should limit to 100 items
    assert len(results) <= 100


@pytest.mark.asyncio
async def test_otx_extracts_mitre_techniques():
    """
    RED: Test extraction of MITRE ATT&CK techniques from pulses.
    """
    client = OTXClient(api_key="test-key")

    # Mock response with MITRE techniques
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={
                "pulses": [
                    {
                        "name": "Test Pulse",
                        "attack_ids": [
                            {"id": "T1071", "name": "Application Layer Protocol"},
                            {"id": "T1090", "name": "Proxy"}
                        ]
                    }
                ]
            })
        )

        result = await client.fetch_ip_reputation("1.2.3.4")

        if result:
            # Should extract ATT&CK techniques
            assert "attack_techniques" in result
            assert isinstance(result["attack_techniques"], list)


@pytest.mark.asyncio
async def test_otx_handles_no_data():
    """
    RED: Test handling when OTX has no data for an indicator.
    """
    client = OTXClient(api_key="test-key")

    # Mock response with no pulses
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={"pulses": []})
        )

        result = await client.fetch_ip_reputation("192.0.2.1")

        # Should still return result, but with empty/default values
        assert result is not None
        assert result["reputation_score"] == 0  # Clean if no pulses
