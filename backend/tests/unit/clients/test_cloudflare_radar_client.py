"""
Unit tests for Cloudflare Radar API Client.

Cloudflare Radar provides internet traffic insights, domain rankings, and traffic anomalies.

API Documentation: https://developers.cloudflare.com/radar/
Rate limit: Requires API Token

These tests are written FIRST following TDD.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

# Import will fail until we implement the module (RED phase)
try:
    from src.clients.cloudflare_radar_client import CloudflareRadarClient
except ImportError:
    pass


@pytest.mark.asyncio
async def test_radar_get_domain_ranking():
    """
    RED: Test that CloudflareRadarClient can fetch domain ranking.

    Expected behavior:
    - Fetch ranking for a known domain (e.g., google.com)
    - Return dict with domain popularity data
    """
    client = CloudflareRadarClient(api_token="test_token")

    # Mock successful API response for domain ranking
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "result": {
            "rank": 1,
            "domain": "google.com",
            "categories": ["Search Engines"],
            "bucket": "top_100"
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_domain_ranking("google.com")

        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "google.com" in str(call_args)

        # Verify response structure
        assert result is not None
        assert result["rank"] == 1
        assert result["domain"] == "google.com"
        assert "categories" in result
        assert result["bucket"] == "top_100"

    await client.close()


@pytest.mark.asyncio
async def test_radar_get_traffic_anomalies():
    """
    RED: Test that CloudflareRadarClient can fetch traffic anomalies.

    Expected behavior:
    - Fetch traffic anomalies for a location (e.g., US)
    - Return dict with anomaly data
    """
    client = CloudflareRadarClient(api_token="test_token")

    # Mock successful API response for traffic anomalies
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "result": {
            "anomalies": [
                {
                    "location": "US",
                    "timestamp": "2024-01-15T10:00:00Z",
                    "type": "traffic_drop",
                    "severity": "medium",
                    "description": "Traffic anomaly detected"
                }
            ]
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_traffic_anomalies("US")

        # Verify request was made correctly
        mock_get.assert_called_once()

        # Verify response structure
        assert result is not None
        assert "anomalies" in result
        assert len(result["anomalies"]) > 0
        assert result["anomalies"][0]["location"] == "US"
        assert result["anomalies"][0]["type"] == "traffic_drop"

    await client.close()


@pytest.mark.asyncio
async def test_radar_get_dns_stats():
    """
    RED: Test that CloudflareRadarClient can fetch DNS query stats.

    Expected behavior:
    - Fetch DNS stats for a domain
    - Return dict with DNS query statistics
    """
    client = CloudflareRadarClient(api_token="test_token")

    # Mock successful API response for DNS stats
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "result": {
            "domain": "example.com",
            "query_count": 1000000,
            "response_time_avg_ms": 25.5,
            "error_rate": 0.01,
            "record_types": {
                "A": 60,
                "AAAA": 20,
                "CNAME": 10,
                "MX": 10
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_dns_stats("example.com")

        # Verify request was made correctly
        mock_get.assert_called_once()

        # Verify response structure
        assert result is not None
        assert result["domain"] == "example.com"
        assert result["query_count"] == 1000000
        assert "response_time_avg_ms" in result
        assert "record_types" in result

    await client.close()


@pytest.mark.asyncio
async def test_radar_handles_rate_limit():
    """
    RED: Test rate limit handling.

    Expected behavior:
    - When API returns 429 (rate limited), return None
    - Log appropriate warning
    """
    client = CloudflareRadarClient(api_token="test_token")

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.json.return_value = {"success": False, "errors": [{"message": "Rate limit exceeded"}]}

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_domain_ranking("google.com")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_radar_handles_api_error():
    """
    RED: Test that CloudflareRadarClient handles API errors gracefully.

    Expected behavior:
    - When API returns error status, client should return None
    - No exceptions should be raised
    """
    client = CloudflareRadarClient(api_token="test_token")

    # Mock server error response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"success": False, "errors": [{"message": "Internal Server Error"}]}

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_domain_ranking("google.com")

        # Should return None on error
        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_radar_handles_timeout():
    """
    RED: Test timeout handling.

    Expected behavior:
    - When request times out, return None
    - No exceptions should propagate
    """
    client = CloudflareRadarClient(api_token="test_token", timeout=5)

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Request timed out")

        result = await client.get_domain_ranking("google.com")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_radar_requires_api_token():
    """
    RED: Test that CloudflareRadarClient requires API token.

    Expected behavior:
    - Creating client without api_token raises ValueError
    """
    with pytest.raises(ValueError, match="API token is required"):
        CloudflareRadarClient(api_token=None)

    with pytest.raises(ValueError, match="API token is required"):
        CloudflareRadarClient(api_token="")


@pytest.mark.asyncio
async def test_radar_client_close():
    """
    RED: Test that client can be properly closed.
    """
    client = CloudflareRadarClient(api_token="test_token")

    # Should not raise any exceptions
    await client.close()


@pytest.mark.asyncio
async def test_radar_uses_correct_base_url():
    """
    RED: Test that client uses correct Cloudflare Radar API base URL.
    """
    client = CloudflareRadarClient(api_token="test_token")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "result": {"rank": 1, "domain": "google.com", "categories": [], "bucket": "top_100"}
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        await client.get_domain_ranking("google.com")

        # Verify correct URL was called
        call_args = mock_get.call_args
        assert "api.cloudflare.com" in call_args[0][0]
        assert "radar" in call_args[0][0]

    await client.close()


@pytest.mark.asyncio
async def test_radar_custom_timeout():
    """
    RED: Test that custom timeout is applied.
    """
    client = CloudflareRadarClient(api_token="test_token", timeout=10)

    # Verify timeout was set
    assert client.timeout == 10

    await client.close()


@pytest.mark.asyncio
async def test_radar_auth_header():
    """
    RED: Test that API token is sent in Authorization header.
    """
    client = CloudflareRadarClient(api_token="my_secret_token")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "result": {"rank": 1, "domain": "google.com", "categories": [], "bucket": "top_100"}
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        await client.get_domain_ranking("google.com")

        # Verify Authorization header was included
        call_args = mock_get.call_args
        headers = call_args.kwargs.get("headers", {})
        assert "Authorization" in headers
        assert "Bearer my_secret_token" in headers["Authorization"]

    await client.close()


@pytest.mark.asyncio
async def test_radar_handles_request_error():
    """
    RED: Test handling of network/request errors.

    Expected behavior:
    - When network error occurs, return None
    - No exceptions should propagate
    """
    client = CloudflareRadarClient(api_token="test_token")

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await client.get_domain_ranking("google.com")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_radar_handles_unsuccessful_response():
    """
    RED: Test handling of Cloudflare API unsuccessful response.

    Expected behavior:
    - When success=False in response, return None
    """
    client = CloudflareRadarClient(api_token="test_token")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": False,
        "errors": [{"code": 1000, "message": "Invalid domain"}]
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_domain_ranking("invalid-domain")

        assert result is None

    await client.close()
