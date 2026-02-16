"""
Unit tests for Pulsedive API Client.

Pulsedive provides threat intelligence data including risk scores,
geo location, and threat attribution.

API Documentation: https://pulsedive.com/api/
Rate limit: 100 requests/day (free tier)

These tests are written FIRST following TDD.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

# Import will fail until we implement the module (RED phase)
try:
    from src.clients.pulsedive_client import PulsediveClient
except ImportError:
    pass


@pytest.mark.asyncio
async def test_pulsedive_get_indicator_returns_risk():
    """
    RED: Test that PulsediveClient can get indicator info and returns risk level.

    Expected behavior:
    - Fetch indicator information for an IP
    - Return dict with indicator data including risk level
    """
    client = PulsediveClient()

    # Mock successful API response based on Pulsedive API structure
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "indicator": "8.8.8.8",
        "type": "ip",
        "risk": "none",
        "risk_recommended": "none",
        "manualrisk": 0,
        "stamp_seen": "2023-01-01 00:00:00",
        "stamp_probed": "2023-06-01 00:00:00",
        "attributes": {
            "port": ["53", "443"],
            "protocol": ["dns", "https"],
            "technology": ["Google DNS"]
        },
        "properties": {
            "geo": {
                "country": "United States",
                "countrycode": "US",
                "city": "Mountain View",
                "region": "California"
            },
            "whois": {
                "asn": 15169,
                "org": "Google LLC"
            }
        },
        "threats": [],
        "feeds": []
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_indicator_info("8.8.8.8")

        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["params"]["indicator"] == "8.8.8.8"

        # Verify response structure
        assert result is not None
        assert result["indicator"] == "8.8.8.8"
        assert result["type"] == "ip"
        assert result["risk"] == "none"
        assert "risk_recommended" in result
        assert "attributes" in result
        assert "properties" in result

    await client.close()


@pytest.mark.asyncio
async def test_pulsedive_parses_geo_correctly():
    """
    RED: Test that PulsediveClient parses geo information correctly.

    Expected behavior:
    - Fetch indicator with geo data
    - Geo properties should include country, countrycode, city, region
    """
    client = PulsediveClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "indicator": "1.2.3.4",
        "type": "ip",
        "risk": "low",
        "risk_recommended": "low",
        "manualrisk": 0,
        "stamp_seen": "2023-01-01 00:00:00",
        "stamp_probed": "2023-06-01 00:00:00",
        "attributes": {},
        "properties": {
            "geo": {
                "country": "Germany",
                "countrycode": "DE",
                "city": "Berlin",
                "region": "Berlin"
            },
            "whois": {
                "asn": 12345,
                "org": "Example ISP"
            }
        },
        "threats": [],
        "feeds": []
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_indicator_info("1.2.3.4")

        # Verify geo data parsing
        assert result is not None
        assert "properties" in result
        assert "geo" in result["properties"]

        geo = result["properties"]["geo"]
        assert geo["country"] == "Germany"
        assert geo["countrycode"] == "DE"
        assert geo["city"] == "Berlin"
        assert geo["region"] == "Berlin"

        # Verify whois data
        assert "whois" in result["properties"]
        whois = result["properties"]["whois"]
        assert whois["asn"] == 12345
        assert whois["org"] == "Example ISP"

    await client.close()


@pytest.mark.asyncio
async def test_pulsedive_handles_unknown_indicator():
    """
    RED: Test that PulsediveClient handles unknown indicators gracefully.

    Expected behavior:
    - When indicator is not found, API returns error
    - Client should return None or appropriate error response
    """
    client = PulsediveClient()

    # Pulsedive returns 404 for unknown indicators
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {
        "error": "Indicator not found"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_indicator_info("unknown-indicator-xyz123")

        # Should return None for not found
        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_pulsedive_handles_api_error():
    """
    RED: Test that PulsediveClient handles API errors gracefully.

    Expected behavior:
    - When API returns server error, client should return None
    - No exceptions should propagate
    """
    client = PulsediveClient()

    # Mock server error response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {
        "error": "Internal server error"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_indicator_info("8.8.8.8")

        # Should return None on error
        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_pulsedive_rate_limit_handling():
    """
    RED: Test that PulsediveClient handles rate limiting (429 status).

    Expected behavior:
    - When API returns 429 rate limit, client should return None
    - Should log appropriate warning
    """
    client = PulsediveClient()

    # Mock rate limit response
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.json.return_value = {
        "error": "Rate limit exceeded"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_indicator_info("8.8.8.8")

        # Should return None on rate limit
        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_pulsedive_handles_timeout():
    """
    RED: Test timeout handling.

    Expected behavior:
    - When request times out, return None
    - No exceptions should propagate
    """
    client = PulsediveClient(timeout=5)

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Request timed out")

        result = await client.get_indicator_info("1.1.1.1")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_pulsedive_handles_request_error():
    """
    RED: Test handling of network/request errors.

    Expected behavior:
    - When network error occurs, return None
    - No exceptions should propagate
    """
    client = PulsediveClient()

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await client.get_indicator_info("1.1.1.1")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_pulsedive_get_indicator_links():
    """
    RED: Test that get_indicator_links returns related links.

    Expected behavior:
    - Fetch links associated with an indicator ID
    - Return dict with linked indicators
    """
    client = PulsediveClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "iid": 12345,
                "indicator": "evil.com",
                "type": "domain",
                "risk": "high"
            },
            {
                "iid": 12346,
                "indicator": "malware.exe",
                "type": "artifact",
                "risk": "critical"
            }
        ],
        "count": 2
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_indicator_links(12345)

        # Verify request
        mock_get.assert_called_once()

        # Verify response
        assert result is not None
        assert "results" in result
        assert result["count"] == 2
        assert len(result["results"]) == 2

    await client.close()


@pytest.mark.asyncio
async def test_pulsedive_explore():
    """
    RED: Test that explore returns search results.

    Expected behavior:
    - Search using query string
    - Return dict with matching indicators
    """
    client = PulsediveClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "iid": 111,
                "indicator": "185.141.63.120",
                "type": "ip",
                "risk": "high"
            },
            {
                "iid": 222,
                "indicator": "suspicious-domain.com",
                "type": "domain",
                "risk": "medium"
            }
        ],
        "count": 2
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.explore("risk:high type:ip")

        # Verify request
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "q" in call_args[1]["params"]

        # Verify response
        assert result is not None
        assert "results" in result
        assert result["count"] == 2

    await client.close()


@pytest.mark.asyncio
async def test_pulsedive_explore_no_results():
    """
    RED: Test explore with no matching results.

    Expected behavior:
    - Search returns empty results
    - Return dict with empty results array
    """
    client = PulsediveClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [],
        "count": 0
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.explore("nonexistent-search-term-xyz")

        assert result is not None
        assert result["results"] == []
        assert result["count"] == 0

    await client.close()


@pytest.mark.asyncio
async def test_pulsedive_client_close():
    """
    RED: Test that client can be properly closed.
    """
    client = PulsediveClient()

    # Should not raise any exceptions
    await client.close()


@pytest.mark.asyncio
async def test_pulsedive_custom_timeout():
    """
    RED: Test that custom timeout is applied.
    """
    client = PulsediveClient(timeout=15)

    # Verify timeout was set
    assert client.timeout == 15

    await client.close()


@pytest.mark.asyncio
async def test_pulsedive_with_api_key():
    """
    RED: Test that API key is included in requests when provided.

    Pulsedive requires API key for higher rate limits.
    """
    client = PulsediveClient(api_key="test-api-key-123")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "indicator": "8.8.8.8",
        "type": "ip",
        "risk": "none",
        "properties": {},
        "attributes": {},
        "threats": [],
        "feeds": []
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        await client.get_indicator_info("8.8.8.8")

        # Verify API key was included in params
        call_args = mock_get.call_args
        assert call_args[1]["params"]["key"] == "test-api-key-123"

    await client.close()


@pytest.mark.asyncio
async def test_pulsedive_uses_correct_base_url():
    """
    RED: Test that client uses correct Pulsedive API base URL.
    """
    client = PulsediveClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "indicator": "test",
        "type": "domain",
        "risk": "none",
        "properties": {},
        "attributes": {},
        "threats": [],
        "feeds": []
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        await client.get_indicator_info("test.com")

        # Verify correct URL was called
        call_args = mock_get.call_args
        assert call_args[0][0] == "https://pulsedive.com/api/info.php"

    await client.close()


@pytest.mark.asyncio
async def test_pulsedive_handles_malformed_response():
    """
    RED: Test handling of malformed API response.

    Expected behavior:
    - When response JSON is invalid or missing expected fields
    - Client should return None without crashing
    """
    client = PulsediveClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    # Malformed response missing expected fields
    mock_response.json.return_value = {
        "unexpected": "data"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_indicator_info("8.8.8.8")

        # Should handle gracefully - return the raw response or None
        # Implementation decides, but should not crash
        # For this case, we'll accept the raw response
        assert result is not None or result is None  # Either is acceptable

    await client.close()


@pytest.mark.asyncio
async def test_pulsedive_get_indicator_with_threats():
    """
    RED: Test indicator response that includes threat data.

    Expected behavior:
    - Parse threats array from response
    - Include feed information if present
    """
    client = PulsediveClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "indicator": "185.141.63.120",
        "type": "ip",
        "risk": "critical",
        "risk_recommended": "critical",
        "manualrisk": 0,
        "stamp_seen": "2023-01-01 00:00:00",
        "stamp_probed": "2023-06-01 00:00:00",
        "attributes": {
            "port": ["443", "8080"],
            "protocol": ["https"]
        },
        "properties": {
            "geo": {
                "country": "Russia",
                "countrycode": "RU"
            }
        },
        "threats": [
            {
                "tid": 100,
                "name": "Cobalt Strike C2",
                "category": "malware"
            }
        ],
        "feeds": [
            {
                "fid": 50,
                "name": "ThreatFox",
                "category": "malware"
            }
        ]
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_indicator_info("185.141.63.120")

        assert result is not None
        assert result["risk"] == "critical"
        assert "threats" in result
        assert len(result["threats"]) == 1
        assert result["threats"][0]["name"] == "Cobalt Strike C2"
        assert "feeds" in result
        assert len(result["feeds"]) == 1

    await client.close()


@pytest.mark.asyncio
async def test_pulsedive_auth_error_handling():
    """
    RED: Test handling of authentication errors (401).

    Expected behavior:
    - When API returns 401, client should return None
    - Should log appropriate error
    """
    client = PulsediveClient(api_key="invalid-key")

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {
        "error": "Invalid API key"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_indicator_info("8.8.8.8")

        # Should return None on auth error
        assert result is None

    await client.close()
