"""
Integration tests for AbuseIPDB API Client.

AbuseIPDB provides IP reputation data including abuse confidence scores
and report counts.

Rate limit: 1000 requests/day (free tier)

These tests are written FIRST following TDD.
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.clients.abuseipdb_client import AbuseIPDBClient


@pytest.mark.asyncio
async def test_abuseipdb_fetch_ip_success():
    """
    RED: Test that AbuseIPDBClient can fetch IP reputation successfully.
    """
    client = AbuseIPDBClient(api_key="test-key")

    result = await client.fetch_ip_reputation("8.8.8.8")

    # Assertions
    assert result is not None
    assert "indicator_value" in result
    assert "indicator_type" in result
    assert "abuse_confidence_score" in result
    assert "total_reports" in result
    assert "country" in result
    assert "is_whitelisted" in result

    # Validate data types and ranges
    assert isinstance(result["abuse_confidence_score"], int)
    assert 0 <= result["abuse_confidence_score"] <= 100
    assert isinstance(result["total_reports"], int)
    assert result["total_reports"] >= 0


@pytest.mark.asyncio
async def test_abuseipdb_handles_rate_limit():
    """
    RED: Test that AbuseIPDBClient handles rate limiting.

    Free tier: 1000 requests/day
    """
    client = AbuseIPDBClient(api_key="test-key")

    # Mock rate limit response
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=429,
            headers={"X-RateLimit-Remaining": "0"},
            json=AsyncMock(return_value={"errors": [{"detail": "Rate limit exceeded"}]})
        )

        result = await client.fetch_ip_reputation("1.1.1.1")

        # Should return None on rate limit
        assert result is None


@pytest.mark.asyncio
async def test_abuseipdb_handles_invalid_api_key():
    """
    RED: Test handling of invalid API key.
    """
    client = AbuseIPDBClient(api_key="invalid-key")

    # Mock auth error
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=401,
            json=AsyncMock(return_value={"errors": [{"detail": "Invalid API key"}]})
        )

        result = await client.fetch_ip_reputation("1.1.1.1")

        assert result is None


@pytest.mark.asyncio
async def test_abuseipdb_handles_timeout():
    """
    RED: Test timeout handling.
    """
    client = AbuseIPDBClient(api_key="test-key", timeout=5)

    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = TimeoutError("Request timed out")

        result = await client.fetch_ip_reputation("1.1.1.1")

        assert result is None


@pytest.mark.asyncio
async def test_abuseipdb_fetch_multiple_ips():
    """
    RED: Test batch fetching of multiple IPs.
    """
    client = AbuseIPDBClient(api_key="test-key")

    ips = ["8.8.8.8", "1.1.1.1", "192.168.1.1"]

    results = await client.fetch_ips(ips)

    assert isinstance(results, dict)
    assert len(results) <= len(ips)

    for ip, data in results.items():
        if data is not None:
            assert "abuse_confidence_score" in data


@pytest.mark.asyncio
async def test_abuseipdb_respects_max_items_limit():
    """
    RED: Test that client respects MAX_ITEMS_PER_SOURCE limit (100).
    """
    client = AbuseIPDBClient(api_key="test-key")

    # Try to fetch 200 IPs
    ips = [f"192.168.1.{i % 255}" for i in range(200)]

    results = await client.fetch_ips(ips)

    # Should limit to 100 items
    assert len(results) <= 100


@pytest.mark.asyncio
async def test_abuseipdb_handles_private_ip():
    """
    RED: Test handling of private/reserved IP addresses.
    """
    client = AbuseIPDBClient(api_key="test-key")

    # Private IP should return None or clean result
    result = await client.fetch_ip_reputation("192.168.1.1")

    # Should handle gracefully (might return None or clean result)
    if result is not None:
        assert result["abuse_confidence_score"] == 0


@pytest.mark.asyncio
async def test_abuseipdb_handles_whitelisted_ip():
    """
    RED: Test handling of whitelisted IPs (e.g., Google DNS).
    """
    client = AbuseIPDBClient(api_key="test-key")

    # Mock whitelisted IP response
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={
                "data": {
                    "ipAddress": "8.8.8.8",
                    "isWhitelisted": True,
                    "abuseConfidenceScore": 0,
                    "totalReports": 0,
                    "countryCode": "US"
                }
            })
        )

        result = await client.fetch_ip_reputation("8.8.8.8")

        assert result is not None
        assert result["is_whitelisted"] is True
        assert result["abuse_confidence_score"] == 0


@pytest.mark.asyncio
async def test_abuseipdb_handles_malformed_response():
    """
    RED: Test handling of malformed API responses.
    """
    client = AbuseIPDBClient(api_key="test-key")

    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={"unexpected": "structure"})
        )

        result = await client.fetch_ip_reputation("1.1.1.1")

        # Should return None for malformed response
        assert result is None
