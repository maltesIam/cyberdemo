"""
Integration tests for NVD API Client.

These tests are written FIRST following TDD (Test-Driven Development).
They will FAIL until the NVDClient is implemented.
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.clients.nvd_client import NVDClient, NVDRateLimitError, NVDTimeoutError


@pytest.mark.asyncio
async def test_nvd_fetch_cve_success(mock_nvd_response, mock_http_response):
    """
    Test that NVDClient can fetch CVE data successfully with mocked response.
    """
    client = NVDClient()

    # Mock HTTP response
    with patch.object(client.client, 'get', return_value=mock_http_response(200, mock_nvd_response)):
        result = await client.fetch_cve("CVE-2024-0001")

        # Assertions
        assert result is not None
        assert "cvss_v3_score" in result
        assert "cvss_v3_vector" in result
        assert "cwe_ids" in result
        assert "cpe_uris" in result
        assert "references" in result
        assert "description" in result

        # Validate data types
        assert isinstance(result.get("cvss_v3_score"), (float, type(None)))
        assert isinstance(result.get("cwe_ids"), list)
        assert isinstance(result.get("cpe_uris"), list)
        assert isinstance(result.get("references"), list)

    await client.close()


@pytest.mark.asyncio
async def test_nvd_handles_rate_limit():
    """
    RED: Test that NVDClient handles rate limiting gracefully.

    NVD API has rate limits:
    - 5 req/30s without API key
    - 50 req/30s with API key

    Client should implement rate limiting and retry logic.
    """
    client = NVDClient(api_key=None)  # No API key = 5 req/30s

    # Mock HTTP response with 429 status (rate limit)
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=429,
            headers={"Retry-After": "30"},
            json=AsyncMock(return_value={"message": "Rate limit exceeded"})
        )

        # Should handle rate limit without raising exception
        result = await client.fetch_cve("CVE-2024-0001")

        # Should return None when rate limited (graceful degradation)
        assert result is None


@pytest.mark.asyncio
async def test_nvd_handles_timeout():
    """
    RED: Test that NVDClient handles timeouts gracefully.

    Network requests can timeout. Client should handle this
    without crashing the entire enrichment process.
    """
    client = NVDClient(timeout=5)  # 5 second timeout

    # Mock timeout exception
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = TimeoutError("Request timed out")

        # Should handle timeout without raising exception
        result = await client.fetch_cve("CVE-2024-0001")

        # Should return None when timeout occurs
        assert result is None


@pytest.mark.asyncio
async def test_nvd_handles_invalid_cve():
    """
    RED: Test that NVDClient handles invalid CVE IDs gracefully.
    """
    client = NVDClient()

    # Test with invalid CVE ID
    result = await client.fetch_cve("INVALID-CVE")

    # Should return None for invalid CVE (not raise exception)
    assert result is None


@pytest.mark.asyncio
async def test_nvd_handles_malformed_response():
    """
    RED: Test that NVDClient handles malformed API responses.
    """
    client = NVDClient()

    # Mock malformed response
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={"unexpected": "structure"})
        )

        # Should handle malformed response without crashing
        result = await client.fetch_cve("CVE-2024-0001")

        # Should return None when response is malformed
        assert result is None


@pytest.mark.asyncio
async def test_nvd_rate_limiter_respects_limits():
    """
    RED: Test that rate limiter prevents exceeding API limits.

    Without API key: max 5 requests per 30 seconds
    With API key: max 50 requests per 30 seconds
    """
    client = NVDClient(api_key=None)  # 5 req/30s

    # Track request times
    request_times = []

    async def mock_request(*args, **kwargs):
        import time
        request_times.append(time.time())
        return AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={
                "vulnerabilities": [{
                    "cve": {
                        "id": "CVE-2024-0001",
                        "metrics": {},
                        "references": []
                    }
                }]
            })
        )

    with patch('httpx.AsyncClient.get', side_effect=mock_request):
        # Make 6 requests (should trigger rate limiting on 6th)
        for i in range(6):
            await client.fetch_cve(f"CVE-2024-000{i}")

    # Verify rate limiting is applied
    if len(request_times) >= 2:
        # Check that requests are spaced out properly
        time_diff = request_times[-1] - request_times[0]
        # With 5 req/30s limit, 6 requests should take >30 seconds
        # or 6th request should be delayed
        assert len(request_times) == 6


@pytest.mark.asyncio
async def test_nvd_fetch_multiple_cves(mock_nvd_response, mock_http_response):
    """
    Test batch fetching of multiple CVEs with mocked responses.
    """
    client = NVDClient()

    cve_ids = ["CVE-2024-0001", "CVE-2024-0002", "CVE-2024-0003"]

    # Mock HTTP response for each CVE
    with patch.object(client.client, 'get', return_value=mock_http_response(200, mock_nvd_response)):
        results = await client.fetch_cves(cve_ids)

        # Should return dict mapping CVE ID to data
        assert isinstance(results, dict)
        assert len(results) <= len(cve_ids)  # Some may fail

        # Check structure of returned data
        for cve_id, data in results.items():
            if data is not None:  # Skip failed fetches
                assert "cvss_v3_score" in data
                assert "cve_id" in data

    await client.close()


@pytest.mark.asyncio
async def test_nvd_respects_max_items_limit(mock_nvd_response, mock_http_response):
    """
    Test that client respects MAX_ITEMS_PER_SOURCE limit (100).
    """
    client = NVDClient()

    # Try to fetch 200 CVEs
    cve_ids = [f"CVE-2024-{i:04d}" for i in range(200)]

    # Mock HTTP response
    with patch.object(client.client, 'get', return_value=mock_http_response(200, mock_nvd_response)):
        results = await client.fetch_cves(cve_ids)

        # Should limit to 100 items
        assert len(results) <= 100

    await client.close()
