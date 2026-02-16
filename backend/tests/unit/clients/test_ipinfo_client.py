"""
Unit tests for IPinfo API Client.

IPinfo provides IP geolocation, ASN, and basic metadata for IP addresses.

API Documentation: https://ipinfo.io/developers
Rate limit: 50,000 requests/month (free tier, no API key needed for basic)

These tests are written FIRST following TDD.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

# Import will fail until we implement the module (RED phase)
try:
    from src.clients.ipinfo_client import IPinfoClient
except ImportError:
    pass


@pytest.mark.asyncio
async def test_ipinfo_get_ip_returns_data():
    """
    RED: Test that IPinfoClient can fetch IP info and return data.

    Expected behavior:
    - Fetch info for a known IP (8.8.8.8 - Google DNS)
    - Return dict with IP geolocation and metadata
    """
    client = IPinfoClient()

    # Mock successful API response for Google DNS
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ip": "8.8.8.8",
        "hostname": "dns.google",
        "city": "Mountain View",
        "region": "California",
        "country": "US",
        "loc": "37.4056,-122.0775",
        "org": "AS15169 Google LLC",
        "postal": "94043",
        "timezone": "America/Los_Angeles"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_ip_info("8.8.8.8")

        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "8.8.8.8" in call_args[0][0]

        # Verify response structure
        assert result is not None
        assert result["ip"] == "8.8.8.8"
        assert result["hostname"] == "dns.google"
        assert result["city"] == "Mountain View"
        assert result["region"] == "California"
        assert result["country"] == "US"
        assert result["org"] == "AS15169 Google LLC"
        assert result["timezone"] == "America/Los_Angeles"

    await client.close()


@pytest.mark.asyncio
async def test_ipinfo_parses_location_correctly():
    """
    RED: Test that IPinfoClient parses lat/lng from loc field correctly.

    Expected behavior:
    - Parse "loc": "37.4056,-122.0775" into latitude and longitude floats
    - Return structured geolocation data
    """
    client = IPinfoClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ip": "8.8.8.8",
        "hostname": "dns.google",
        "city": "Mountain View",
        "region": "California",
        "country": "US",
        "loc": "37.4056,-122.0775",
        "org": "AS15169 Google LLC",
        "postal": "94043",
        "timezone": "America/Los_Angeles"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_geolocation("8.8.8.8")

        # Verify geolocation data structure
        assert result is not None
        assert "latitude" in result
        assert "longitude" in result
        assert result["latitude"] == 37.4056
        assert result["longitude"] == -122.0775
        assert result["city"] == "Mountain View"
        assert result["region"] == "California"
        assert result["country"] == "US"
        assert result["postal"] == "94043"
        assert result["timezone"] == "America/Los_Angeles"

    await client.close()


@pytest.mark.asyncio
async def test_ipinfo_parses_asn_from_org():
    """
    RED: Test that IPinfoClient parses ASN from org field correctly.

    Expected behavior:
    - Parse "org": "AS15169 Google LLC" into ASN number and organization name
    """
    client = IPinfoClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ip": "8.8.8.8",
        "hostname": "dns.google",
        "city": "Mountain View",
        "region": "California",
        "country": "US",
        "loc": "37.4056,-122.0775",
        "org": "AS15169 Google LLC",
        "postal": "94043",
        "timezone": "America/Los_Angeles"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_ip_info("8.8.8.8")

        # Verify ASN parsing
        assert result is not None
        assert "asn" in result
        assert "org_name" in result
        assert result["asn"] == "AS15169"
        assert result["org_name"] == "Google LLC"

    await client.close()


@pytest.mark.asyncio
async def test_ipinfo_handles_api_error():
    """
    RED: Test that IPinfoClient handles API errors gracefully.

    Expected behavior:
    - When API returns error status, client should return None
    - No exceptions should be raised
    """
    client = IPinfoClient()

    # Mock server error response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"error": "Internal Server Error"}

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_ip_info("8.8.8.8")

        # Should return None on error
        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_ipinfo_handles_timeout():
    """
    RED: Test timeout handling.

    Expected behavior:
    - When request times out, return None
    - No exceptions should propagate
    """
    client = IPinfoClient(timeout=5)

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Request timed out")

        result = await client.get_ip_info("8.8.8.8")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_ipinfo_handles_request_error():
    """
    RED: Test handling of network/request errors.

    Expected behavior:
    - When network error occurs, return None
    - No exceptions should propagate
    """
    client = IPinfoClient()

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await client.get_ip_info("8.8.8.8")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_ipinfo_handles_rate_limit():
    """
    RED: Test rate limit handling.

    Expected behavior:
    - When API returns 429 (rate limited), return None
    - Log appropriate warning
    """
    client = IPinfoClient()

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.json.return_value = {"error": "Rate limit exceeded"}

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_ip_info("8.8.8.8")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_ipinfo_handles_missing_fields():
    """
    RED: Test handling of responses with missing optional fields.

    Expected behavior:
    - When some fields are missing, still return available data
    - Use None or empty strings for missing fields
    """
    client = IPinfoClient()

    # Mock response with minimal data (some fields missing)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ip": "1.2.3.4",
        "country": "US"
        # Missing: hostname, city, region, loc, org, postal, timezone
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_ip_info("1.2.3.4")

        # Should still return data with available fields
        assert result is not None
        assert result["ip"] == "1.2.3.4"
        assert result["country"] == "US"
        # Missing fields should have defaults
        assert result.get("hostname") is None or result.get("hostname") == ""
        assert result.get("city") is None or result.get("city") == ""

    await client.close()


@pytest.mark.asyncio
async def test_ipinfo_handles_bogon_ip():
    """
    RED: Test handling of bogon/reserved IP addresses.

    Expected behavior:
    - IPinfo returns minimal data for bogon IPs
    - Client should handle this gracefully
    """
    client = IPinfoClient()

    # Mock response for private/bogon IP
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ip": "192.168.1.1",
        "bogon": True
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_ip_info("192.168.1.1")

        # Should return data indicating it's a bogon
        assert result is not None
        assert result["ip"] == "192.168.1.1"
        assert result.get("bogon") is True

    await client.close()


@pytest.mark.asyncio
async def test_ipinfo_get_geolocation_with_invalid_loc():
    """
    RED: Test geolocation parsing with invalid or missing loc field.

    Expected behavior:
    - When loc field is missing or malformed, return None for lat/lng
    """
    client = IPinfoClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ip": "1.2.3.4",
        "city": "Unknown",
        "country": "US"
        # Missing loc field
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_geolocation("1.2.3.4")

        # Should return None or dict with None lat/lng
        if result is not None:
            assert result.get("latitude") is None
            assert result.get("longitude") is None

    await client.close()


@pytest.mark.asyncio
async def test_ipinfo_client_close():
    """
    RED: Test that client can be properly closed.
    """
    client = IPinfoClient()

    # Should not raise any exceptions
    await client.close()


@pytest.mark.asyncio
async def test_ipinfo_custom_timeout():
    """
    RED: Test that custom timeout is applied.
    """
    client = IPinfoClient(timeout=10)

    # Verify timeout was set
    assert client.timeout == 10

    await client.close()


@pytest.mark.asyncio
async def test_ipinfo_uses_correct_base_url():
    """
    RED: Test that client uses correct IPinfo API base URL.
    """
    client = IPinfoClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ip": "8.8.8.8"}

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        await client.get_ip_info("8.8.8.8")

        # Verify correct URL was called
        call_args = mock_get.call_args
        assert "ipinfo.io" in call_args[0][0]
        assert "8.8.8.8" in call_args[0][0]

    await client.close()


@pytest.mark.asyncio
async def test_ipinfo_org_without_asn():
    """
    RED: Test parsing org field that doesn't have ASN format.

    Expected behavior:
    - When org field doesn't follow "AS##### Name" format
    - Should still work, with asn as None
    """
    client = IPinfoClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ip": "1.2.3.4",
        "city": "Test City",
        "country": "US",
        "loc": "40.0,-74.0",
        "org": "Some Organization"  # No ASN prefix
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_ip_info("1.2.3.4")

        # Should handle org without ASN gracefully
        assert result is not None
        assert result.get("asn") is None or result.get("asn") == ""
        assert result.get("org_name") == "Some Organization"

    await client.close()
