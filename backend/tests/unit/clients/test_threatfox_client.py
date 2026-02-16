"""
Unit tests for ThreatFox API Client.

ThreatFox (abuse.ch) provides threat intelligence data including IOC information,
malware families, and threat types.

API Documentation: https://threatfox.abuse.ch/api/
Rate limit: Free, unlimited API

These tests are written FIRST following TDD.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

# Import will fail until we implement the module (RED phase)
try:
    from src.clients.threatfox_client import ThreatFoxClient
except ImportError:
    pass


@pytest.mark.asyncio
async def test_threatfox_search_ioc_returns_data():
    """
    RED: Test that ThreatFoxClient can search for an IOC and return data.

    Expected behavior:
    - Search for a known malicious IP
    - Return dict with IOC data including threat_type, malware, confidence_level
    """
    client = ThreatFoxClient()

    # Mock successful API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "query_status": "ok",
        "data": [{
            "id": "123456",
            "ioc": "185.141.63.120:443",
            "threat_type": "botnet_cc",
            "threat_type_desc": "Botnet Command & Control server",
            "malware": "Cobalt Strike",
            "malware_printable": "Cobalt Strike",
            "confidence_level": 75,
            "first_seen": "2023-01-15 12:00:00 UTC",
            "last_seen": "2023-06-20 18:30:00 UTC",
            "tags": ["CobaltStrike", "APT"]
        }]
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.search_ioc("185.141.63.120")

        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["json"]["query"] == "search_ioc"
        assert call_args[1]["json"]["search_term"] == "185.141.63.120"

        # Verify response structure
        assert result is not None
        assert result["query_status"] == "ok"
        assert "data" in result
        assert len(result["data"]) > 0

        # Verify IOC data structure
        ioc_data = result["data"][0]
        assert "ioc" in ioc_data
        assert "threat_type" in ioc_data
        assert "malware" in ioc_data
        assert "confidence_level" in ioc_data
        assert "first_seen" in ioc_data
        assert "last_seen" in ioc_data
        assert "tags" in ioc_data

    await client.close()


@pytest.mark.asyncio
async def test_threatfox_search_unknown_ioc_returns_empty():
    """
    RED: Test that searching for unknown IOC returns empty data.

    Expected behavior:
    - Search for an IOC that doesn't exist in ThreatFox database
    - Return dict with query_status "no_result" and empty data
    """
    client = ThreatFoxClient()

    # Mock response for unknown IOC
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "query_status": "no_result",
        "data": []
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.search_ioc("192.168.1.1")

        assert result is not None
        assert result["query_status"] == "no_result"
        assert result["data"] == []

    await client.close()


@pytest.mark.asyncio
async def test_threatfox_handles_api_error():
    """
    RED: Test that ThreatFoxClient handles API errors gracefully.

    Expected behavior:
    - When API returns error status, client should return None
    - No exceptions should be raised
    """
    client = ThreatFoxClient()

    # Mock server error response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {
        "query_status": "server_error"
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.search_ioc("8.8.8.8")

        # Should return None on error
        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_threatfox_handles_timeout():
    """
    RED: Test timeout handling.

    Expected behavior:
    - When request times out, return None
    - No exceptions should propagate
    """
    client = ThreatFoxClient(timeout=5)

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.TimeoutException("Request timed out")

        result = await client.search_ioc("1.1.1.1")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_threatfox_handles_request_error():
    """
    RED: Test handling of network/request errors.

    Expected behavior:
    - When network error occurs, return None
    - No exceptions should propagate
    """
    client = ThreatFoxClient()

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.RequestError("Connection failed")

        result = await client.search_ioc("1.1.1.1")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_threatfox_returns_malware_families():
    """
    RED: Test that search_by_malware returns malware family data.

    Expected behavior:
    - Search for a malware family name
    - Return dict with all IOCs associated with that malware
    """
    client = ThreatFoxClient()

    # Mock response with multiple IOCs for malware family
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "query_status": "ok",
        "data": [
            {
                "id": "123",
                "ioc": "185.141.63.120:443",
                "threat_type": "botnet_cc",
                "malware": "Cobalt Strike",
                "confidence_level": 75,
                "first_seen": "2023-01-15 12:00:00 UTC",
                "last_seen": "2023-06-20 18:30:00 UTC",
                "tags": ["CobaltStrike"]
            },
            {
                "id": "124",
                "ioc": "192.168.100.50:8080",
                "threat_type": "botnet_cc",
                "malware": "Cobalt Strike",
                "confidence_level": 80,
                "first_seen": "2023-02-01 10:00:00 UTC",
                "last_seen": "2023-05-15 14:00:00 UTC",
                "tags": ["CobaltStrike", "C2"]
            }
        ]
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.search_by_malware("Cobalt Strike")

        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["json"]["query"] == "malwareinfo"
        assert call_args[1]["json"]["malware"] == "Cobalt Strike"

        # Verify response
        assert result is not None
        assert result["query_status"] == "ok"
        assert len(result["data"]) == 2

        # All results should be for the same malware family
        for ioc in result["data"]:
            assert ioc["malware"] == "Cobalt Strike"

    await client.close()


@pytest.mark.asyncio
async def test_threatfox_get_ioc_by_id():
    """
    RED: Test that get_ioc_by_id retrieves specific IOC details.

    Expected behavior:
    - Fetch IOC by its ThreatFox ID
    - Return detailed IOC information
    """
    client = ThreatFoxClient()

    # Mock response for specific IOC
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "query_status": "ok",
        "data": {
            "id": "123456",
            "ioc": "185.141.63.120:443",
            "threat_type": "botnet_cc",
            "threat_type_desc": "Botnet Command & Control server",
            "malware": "Cobalt Strike",
            "malware_printable": "Cobalt Strike",
            "malware_alias": "CobaltStrike,Beacon",
            "malware_malpedia": "https://malpedia.caad.fkie.fraunhofer.de/details/win.cobalt_strike",
            "confidence_level": 75,
            "first_seen": "2023-01-15 12:00:00 UTC",
            "last_seen": "2023-06-20 18:30:00 UTC",
            "reporter": "anonymous",
            "reference": "https://example.com/report",
            "tags": ["CobaltStrike", "APT"]
        }
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.get_ioc_by_id("123456")

        # Verify request
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["json"]["query"] == "ioc"
        assert call_args[1]["json"]["id"] == "123456"

        # Verify response
        assert result is not None
        assert result["query_status"] == "ok"
        assert result["data"]["id"] == "123456"
        assert "malware_malpedia" in result["data"]
        assert "reporter" in result["data"]

    await client.close()


@pytest.mark.asyncio
async def test_threatfox_get_ioc_by_id_not_found():
    """
    RED: Test handling of non-existent IOC ID.

    Expected behavior:
    - When IOC ID doesn't exist, return dict with no_result status
    """
    client = ThreatFoxClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "query_status": "no_result",
        "data": None
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.get_ioc_by_id("999999999")

        assert result is not None
        assert result["query_status"] == "no_result"

    await client.close()


@pytest.mark.asyncio
async def test_threatfox_search_malware_not_found():
    """
    RED: Test handling of unknown malware family search.
    """
    client = ThreatFoxClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "query_status": "no_result",
        "data": []
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.search_by_malware("NonExistentMalware12345")

        assert result is not None
        assert result["query_status"] == "no_result"
        assert result["data"] == []

    await client.close()


@pytest.mark.asyncio
async def test_threatfox_handles_illegal_search_term():
    """
    RED: Test handling of illegal search term response.

    ThreatFox returns "illegal_search_term" for certain invalid inputs.
    """
    client = ThreatFoxClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "query_status": "illegal_search_term",
        "data": None
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.search_ioc("ab")  # Too short search term

        assert result is not None
        assert result["query_status"] == "illegal_search_term"

    await client.close()


@pytest.mark.asyncio
async def test_threatfox_client_close():
    """
    RED: Test that client can be properly closed.
    """
    client = ThreatFoxClient()

    # Should not raise any exceptions
    await client.close()


@pytest.mark.asyncio
async def test_threatfox_custom_timeout():
    """
    RED: Test that custom timeout is applied.
    """
    client = ThreatFoxClient(timeout=10)

    # Verify timeout was set (checking client configuration)
    assert client.timeout == 10

    await client.close()


@pytest.mark.asyncio
async def test_threatfox_uses_correct_base_url():
    """
    RED: Test that client uses correct ThreatFox API base URL.
    """
    client = ThreatFoxClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"query_status": "ok", "data": []}

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        await client.search_ioc("test")

        # Verify correct URL was called
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://threatfox-api.abuse.ch/api/v1/"

    await client.close()
