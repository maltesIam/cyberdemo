"""
Unit tests for Feodo Tracker API Client.

Feodo Tracker (abuse.ch) provides C2 server intelligence including
botnet command-and-control server IPs and malware families.

API Documentation: https://feodotracker.abuse.ch/
Data Source: https://feodotracker.abuse.ch/downloads/ipblocklist.json
Rate limit: Unlimited (free API, no authentication required)

These tests are written FIRST following TDD.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from src.clients.feodo_tracker_client import FeodoTrackerClient


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def client():
    """Create a Feodo Tracker client instance."""
    return FeodoTrackerClient()


@pytest.fixture
def mock_blocklist_response():
    """Mock successful blocklist response from Feodo Tracker."""
    return [
        {
            "ip_address": "185.215.113.0",
            "port": 443,
            "status": "online",
            "hostname": None,
            "as_number": 9009,
            "as_name": "M247 Ltd",
            "country": "DE",
            "first_seen": "2023-06-01",
            "last_online": "2023-06-15",
            "malware": "Dridex"
        },
        {
            "ip_address": "192.168.1.100",
            "port": 8080,
            "status": "offline",
            "hostname": "c2-server.evil.com",
            "as_number": 12345,
            "as_name": "Evil Corp AS",
            "country": "RU",
            "first_seen": "2023-05-01",
            "last_online": "2023-05-20",
            "malware": "Emotet"
        },
        {
            "ip_address": "10.0.0.1",
            "port": 443,
            "status": "online",
            "hostname": None,
            "as_number": 54321,
            "as_name": "Another AS",
            "country": "US",
            "first_seen": "2023-07-01",
            "last_online": "2023-07-10",
            "malware": "Dridex"
        },
        {
            "ip_address": "172.16.0.50",
            "port": 9000,
            "status": "online",
            "hostname": None,
            "as_number": 11111,
            "as_name": "Test AS",
            "country": "CN",
            "first_seen": "2023-08-01",
            "last_online": "2023-08-15",
            "malware": "QakBot"
        }
    ]


@pytest.fixture
def mock_empty_blocklist():
    """Mock empty blocklist response."""
    return []


# =============================================================================
# Test: Get Blocklist
# =============================================================================

@pytest.mark.asyncio
async def test_feodo_get_blocklist_returns_ips(client, mock_blocklist_response):
    """
    RED: Test that FeodoTrackerClient can fetch the IP blocklist.

    Given the Feodo Tracker API is available
    When we call get_blocklist
    Then we should get a list of C2 server IPs with threat intelligence
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_blocklist_response
        mock_get.return_value = mock_response

        result = await client.get_blocklist()

        # Verify GET was called
        mock_get.assert_called_once()

        # Verify response structure
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 4

        # Verify first entry has expected fields
        first_entry = result[0]
        assert first_entry["ip_address"] == "185.215.113.0"
        assert first_entry["port"] == 443
        assert first_entry["status"] == "online"
        assert first_entry["malware"] == "Dridex"
        assert first_entry["country"] == "DE"
        assert first_entry["as_number"] == 9009
        assert first_entry["as_name"] == "M247 Ltd"


@pytest.mark.asyncio
async def test_feodo_get_blocklist_empty_response(client, mock_empty_blocklist):
    """
    RED: Test handling of empty blocklist.
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_empty_blocklist
        mock_get.return_value = mock_response

        result = await client.get_blocklist()

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0


# =============================================================================
# Test: Check IP
# =============================================================================

@pytest.mark.asyncio
async def test_feodo_check_ip_found(client, mock_blocklist_response):
    """
    RED: Test that FeodoTrackerClient can find a known malicious IP.

    Given an IP that exists in the Feodo Tracker blocklist
    When we call check_ip with that IP
    Then we should get the threat intelligence data for that IP
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_blocklist_response
        mock_get.return_value = mock_response

        result = await client.check_ip("185.215.113.0")

        # Verify response
        assert result is not None
        assert result["ip_address"] == "185.215.113.0"
        assert result["port"] == 443
        assert result["malware"] == "Dridex"
        assert result["status"] == "online"
        assert result["country"] == "DE"


@pytest.mark.asyncio
async def test_feodo_check_ip_not_found(client, mock_blocklist_response):
    """
    RED: Test that FeodoTrackerClient returns None for unknown IP.

    Given an IP that does NOT exist in the Feodo Tracker blocklist
    When we call check_ip with that IP
    Then we should get None
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_blocklist_response
        mock_get.return_value = mock_response

        result = await client.check_ip("8.8.8.8")

        # Should return None for unknown IP
        assert result is None


@pytest.mark.asyncio
async def test_feodo_check_ip_with_second_entry(client, mock_blocklist_response):
    """
    RED: Test finding an IP that's not first in the list.
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_blocklist_response
        mock_get.return_value = mock_response

        result = await client.check_ip("192.168.1.100")

        assert result is not None
        assert result["ip_address"] == "192.168.1.100"
        assert result["malware"] == "Emotet"
        assert result["status"] == "offline"


# =============================================================================
# Test: Filter by Malware
# =============================================================================

@pytest.mark.asyncio
async def test_feodo_filter_by_malware(client, mock_blocklist_response):
    """
    RED: Test that FeodoTrackerClient can filter IPs by malware family.

    Given a malware family name
    When we call get_by_malware with that name
    Then we should get all IPs associated with that malware
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_blocklist_response
        mock_get.return_value = mock_response

        result = await client.get_by_malware("Dridex")

        # Verify response
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2  # Two Dridex entries in mock data

        # Verify all returned entries are Dridex
        for entry in result:
            assert entry["malware"] == "Dridex"


@pytest.mark.asyncio
async def test_feodo_filter_by_malware_case_insensitive(client, mock_blocklist_response):
    """
    RED: Test that malware filtering is case-insensitive.
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_blocklist_response
        mock_get.return_value = mock_response

        # Use lowercase
        result = await client.get_by_malware("dridex")

        assert result is not None
        assert len(result) == 2


@pytest.mark.asyncio
async def test_feodo_filter_by_malware_not_found(client, mock_blocklist_response):
    """
    RED: Test filtering by non-existent malware returns empty list.
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_blocklist_response
        mock_get.return_value = mock_response

        result = await client.get_by_malware("NonExistentMalware")

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0


@pytest.mark.asyncio
async def test_feodo_filter_by_malware_emotet(client, mock_blocklist_response):
    """
    RED: Test filtering by Emotet malware.
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_blocklist_response
        mock_get.return_value = mock_response

        result = await client.get_by_malware("Emotet")

        assert result is not None
        assert len(result) == 1
        assert result[0]["ip_address"] == "192.168.1.100"


# =============================================================================
# Test: Error Handling
# =============================================================================

@pytest.mark.asyncio
async def test_feodo_handles_api_error(client):
    """
    RED: Test that FeodoTrackerClient handles API errors gracefully.
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        result = await client.get_blocklist()

        # Should return empty list on API error
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0


@pytest.mark.asyncio
async def test_feodo_handles_timeout(client):
    """
    RED: Test that FeodoTrackerClient handles timeout gracefully.
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Request timed out")

        result = await client.get_blocklist()

        # Should return empty list on timeout
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0


@pytest.mark.asyncio
async def test_feodo_handles_connection_error(client):
    """
    RED: Test that FeodoTrackerClient handles connection errors gracefully.
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_get.side_effect = httpx.ConnectError("Connection refused")

        result = await client.get_blocklist()

        # Should return empty list on connection error
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0


@pytest.mark.asyncio
async def test_feodo_handles_malformed_json(client):
    """
    RED: Test handling of malformed JSON response.
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        result = await client.get_blocklist()

        # Should return empty list on JSON parse error
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0


@pytest.mark.asyncio
async def test_feodo_check_ip_handles_api_error(client):
    """
    RED: Test that check_ip returns None on API error.
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_get.return_value = mock_response

        result = await client.check_ip("1.2.3.4")

        assert result is None


@pytest.mark.asyncio
async def test_feodo_get_by_malware_handles_api_error(client):
    """
    RED: Test that get_by_malware returns empty list on API error.
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Timeout")

        result = await client.get_by_malware("Emotet")

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0


# =============================================================================
# Test: Client Lifecycle
# =============================================================================

@pytest.mark.asyncio
async def test_feodo_client_close():
    """
    RED: Test that client can be closed properly.
    """
    client = FeodoTrackerClient()

    with patch.object(client.client, 'aclose') as mock_close:
        mock_close.return_value = None
        await client.close()
        mock_close.assert_called_once()


@pytest.mark.asyncio
async def test_feodo_client_custom_timeout():
    """
    RED: Test that client respects custom timeout.
    """
    client = FeodoTrackerClient(timeout=60)

    assert client.timeout == 60


@pytest.mark.asyncio
async def test_feodo_client_default_timeout():
    """
    RED: Test that client has sensible default timeout.
    """
    client = FeodoTrackerClient()

    assert client.timeout == 30  # Default timeout


# =============================================================================
# Test: Caching Behavior
# =============================================================================

@pytest.mark.asyncio
async def test_feodo_blocklist_caching(client, mock_blocklist_response):
    """
    RED: Test that blocklist is cached to avoid repeated API calls.

    The client should cache the blocklist for a reasonable period
    to reduce load on the Feodo Tracker API.
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_blocklist_response
        mock_get.return_value = mock_response

        # First call
        result1 = await client.get_blocklist()
        # Second call should use cache
        result2 = await client.get_blocklist()

        # API should only be called once due to caching
        assert mock_get.call_count == 1
        assert result1 == result2


@pytest.mark.asyncio
async def test_feodo_check_ip_uses_cached_blocklist(client, mock_blocklist_response):
    """
    RED: Test that check_ip uses cached blocklist.
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_blocklist_response
        mock_get.return_value = mock_response

        # Call check_ip twice for different IPs
        await client.check_ip("185.215.113.0")
        await client.check_ip("192.168.1.100")

        # Should still only call API once (uses cache)
        assert mock_get.call_count == 1


@pytest.mark.asyncio
async def test_feodo_clear_cache(client, mock_blocklist_response):
    """
    RED: Test that cache can be cleared.
    """
    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_blocklist_response
        mock_get.return_value = mock_response

        # First call
        await client.get_blocklist()

        # Clear cache
        client.clear_cache()

        # Second call should hit API again
        await client.get_blocklist()

        # API should be called twice (cache was cleared)
        assert mock_get.call_count == 2
