"""
Integration tests for GreyNoise API Client.

GreyNoise classifies IPs as benign, malicious, or unknown based on
internet-wide scanning data.

Community tier: Limited free access

These tests are written FIRST following TDD.
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.clients.greynoise_client import GreyNoiseClient


@pytest.mark.asyncio
async def test_greynoise_fetch_ip_success():
    """
    RED: Test that GreyNoiseClient can fetch IP classification successfully.
    """
    client = GreyNoiseClient(api_key="test-key")

    result = await client.fetch_ip_classification("8.8.8.8")

    # Assertions
    assert result is not None
    assert "indicator_value" in result
    assert "indicator_type" in result
    assert "classification" in result
    assert "tags" in result
    assert "first_seen" in result
    assert "last_seen" in result

    # Validate data types
    assert result["classification"] in ["benign", "malicious", "unknown"]
    assert isinstance(result["tags"], list)


@pytest.mark.asyncio
async def test_greynoise_handles_malicious_classification():
    """
    RED: Test handling of malicious IP classification.
    """
    client = GreyNoiseClient(api_key="test-key")

    # Mock malicious response
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={
                "ip": "1.2.3.4",
                "classification": "malicious",
                "tags": ["scanner", "brute_force"],
                "first_seen": "2024-01-01",
                "last_seen": "2024-02-13"
            })
        )

        result = await client.fetch_ip_classification("1.2.3.4")

        assert result is not None
        assert result["classification"] == "malicious"
        assert "scanner" in result["tags"]


@pytest.mark.asyncio
async def test_greynoise_handles_benign_classification():
    """
    RED: Test handling of benign IP classification.
    """
    client = GreyNoiseClient(api_key="test-key")

    # Mock benign response
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={
                "ip": "8.8.8.8",
                "classification": "benign",
                "tags": ["google_dns"],
                "first_seen": "2020-01-01",
                "last_seen": "2024-02-13"
            })
        )

        result = await client.fetch_ip_classification("8.8.8.8")

        assert result is not None
        assert result["classification"] == "benign"


@pytest.mark.asyncio
async def test_greynoise_handles_api_error():
    """
    RED: Test that GreyNoiseClient handles API errors gracefully.
    """
    client = GreyNoiseClient(api_key="invalid-key")

    # Mock auth error
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=401,
            json=AsyncMock(return_value={"error": "Invalid API key"})
        )

        result = await client.fetch_ip_classification("1.1.1.1")

        # Should return None on error
        assert result is None


@pytest.mark.asyncio
async def test_greynoise_handles_timeout():
    """
    RED: Test timeout handling.
    """
    client = GreyNoiseClient(api_key="test-key", timeout=5)

    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = TimeoutError("Request timed out")

        result = await client.fetch_ip_classification("1.1.1.1")

        assert result is None


@pytest.mark.asyncio
async def test_greynoise_fetch_multiple_ips():
    """
    RED: Test batch fetching of multiple IPs.
    """
    client = GreyNoiseClient(api_key="test-key")

    ips = ["8.8.8.8", "1.1.1.1", "1.2.3.4"]

    results = await client.fetch_ips(ips)

    assert isinstance(results, dict)
    assert len(results) <= len(ips)

    for ip, data in results.items():
        if data is not None:
            assert "classification" in data


@pytest.mark.asyncio
async def test_greynoise_respects_max_items_limit():
    """
    RED: Test that client respects MAX_ITEMS_PER_SOURCE limit (100).
    """
    client = GreyNoiseClient(api_key="test-key")

    # Try to fetch 200 IPs
    ips = [f"192.168.1.{i % 255}" for i in range(200)]

    results = await client.fetch_ips(ips)

    # Should limit to 100 items
    assert len(results) <= 100


@pytest.mark.asyncio
async def test_greynoise_handles_unknown_ip():
    """
    RED: Test handling of unknown IPs (not in GreyNoise database).
    """
    client = GreyNoiseClient(api_key="test-key")

    # Mock response for unknown IP
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=404,
            json=AsyncMock(return_value={"error": "IP not found"})
        )

        result = await client.fetch_ip_classification("192.168.1.1")

        # Should return result with "unknown" classification
        # or None depending on implementation
        if result is not None:
            assert result["classification"] == "unknown"


@pytest.mark.asyncio
async def test_greynoise_handles_rate_limit():
    """
    RED: Test handling of rate limiting (community tier).
    """
    client = GreyNoiseClient(api_key="test-key")

    # Mock rate limit response
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=429,
            json=AsyncMock(return_value={"error": "Rate limit exceeded"})
        )

        result = await client.fetch_ip_classification("1.1.1.1")

        # Should return None on rate limit
        assert result is None


@pytest.mark.asyncio
async def test_greynoise_handles_malformed_response():
    """
    RED: Test handling of malformed API responses.
    """
    client = GreyNoiseClient(api_key="test-key")

    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={"unexpected": "structure"})
        )

        result = await client.fetch_ip_classification("1.1.1.1")

        # Should return None for malformed response
        assert result is None
