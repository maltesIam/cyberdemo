"""
Integration tests for EPSS API Client.

EPSS (Exploit Prediction Scoring System) provides probability scores
for CVE exploitation.

These tests are written FIRST following TDD.
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.clients.epss_client import EPSSClient


@pytest.mark.asyncio
async def test_epss_fetch_scores_success():
    """
    RED: Test that EPSSClient can fetch EPSS scores successfully.

    EPSS API: https://api.first.org/data/v1/epss
    """
    client = EPSSClient()

    # Test with a known CVE
    result = await client.fetch_score("CVE-2024-0001")

    # Assertions
    assert result is not None
    assert "cve_id" in result
    assert "epss_score" in result
    assert "epss_percentile" in result

    # Validate data types and ranges
    assert isinstance(result["epss_score"], float)
    assert isinstance(result["epss_percentile"], float)
    assert 0.0 <= result["epss_score"] <= 1.0
    assert 0.0 <= result["epss_percentile"] <= 1.0


@pytest.mark.asyncio
async def test_epss_handles_api_error():
    """
    RED: Test that EPSSClient handles API errors gracefully.
    """
    client = EPSSClient()

    # Mock HTTP error
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=500,
            json=AsyncMock(return_value={"error": "Internal server error"})
        )

        # Should handle error without raising exception
        result = await client.fetch_score("CVE-2024-0001")

        # Should return None on error
        assert result is None


@pytest.mark.asyncio
async def test_epss_handles_invalid_cve():
    """
    RED: Test that EPSSClient handles invalid CVE IDs.
    """
    client = EPSSClient()

    # Test with invalid CVE
    result = await client.fetch_score("INVALID-CVE")

    # Should return None for invalid CVE
    assert result is None


@pytest.mark.asyncio
async def test_epss_handles_timeout():
    """
    RED: Test that EPSSClient handles timeouts gracefully.
    """
    client = EPSSClient(timeout=5)

    # Mock timeout
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = TimeoutError("Request timed out")

        # Should handle timeout without raising exception
        result = await client.fetch_score("CVE-2024-0001")

        # Should return None on timeout
        assert result is None


@pytest.mark.asyncio
async def test_epss_fetch_multiple_scores():
    """
    RED: Test batch fetching of EPSS scores.
    """
    client = EPSSClient()

    cve_ids = ["CVE-2024-0001", "CVE-2024-0002", "CVE-2024-0003"]

    results = await client.fetch_scores(cve_ids)

    # Should return dict mapping CVE ID to EPSS data
    assert isinstance(results, dict)
    assert len(results) <= len(cve_ids)

    # Check structure
    for cve_id, data in results.items():
        if data is not None:
            assert "epss_score" in data
            assert "epss_percentile" in data
            assert 0.0 <= data["epss_score"] <= 1.0


@pytest.mark.asyncio
async def test_epss_respects_max_items_limit():
    """
    RED: Test that client respects MAX_ITEMS_PER_SOURCE limit (100).
    """
    client = EPSSClient()

    # Try to fetch 200 CVEs
    cve_ids = [f"CVE-2024-{i:04d}" for i in range(200)]

    results = await client.fetch_scores(cve_ids)

    # Should limit to 100 items
    assert len(results) <= 100


@pytest.mark.asyncio
async def test_epss_handles_missing_data():
    """
    RED: Test handling when EPSS has no data for a CVE.
    """
    client = EPSSClient()

    # Mock response with no data
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={"data": []})
        )

        result = await client.fetch_score("CVE-2024-9999")

        # Should return None when no data available
        assert result is None


@pytest.mark.asyncio
async def test_epss_handles_malformed_response():
    """
    RED: Test handling of malformed API responses.
    """
    client = EPSSClient()

    # Mock malformed response
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value={"unexpected": "structure"})
        )

        result = await client.fetch_score("CVE-2024-0001")

        # Should return None for malformed response
        assert result is None
