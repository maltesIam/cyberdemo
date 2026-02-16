"""
Unit tests for MISP API Client.

MISP (Malware Information Sharing Platform) is a threat intelligence sharing platform
that allows organizations to share, store, and correlate Indicators of Compromise (IOCs).

Since MISP is typically self-hosted, this client includes synthetic data generation
for demo mode when no real MISP instance is available.

API Documentation: https://www.misp-project.org/openapi/
Rate limit: Depends on instance configuration

These tests are written FIRST following TDD.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

# Import will fail until we implement the module (RED phase)
try:
    from src.clients.misp_client import MISPClient
except ImportError:
    pass


@pytest.mark.asyncio
async def test_misp_search_events():
    """
    RED: Test that MISPClient can search for events by query.

    Expected behavior:
    - Search for events matching a query term
    - Return list of events with event details
    """
    client = MISPClient(
        base_url="https://misp.example.org",
        api_key="test-api-key"
    )

    # Mock successful API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": [
            {
                "Event": {
                    "id": "12345",
                    "uuid": "550e8400-e29b-41d4-a716-446655440000",
                    "info": "APT29 Campaign Targeting Government Agencies",
                    "date": "2024-01-15",
                    "threat_level_id": "1",
                    "analysis": "2",
                    "distribution": "1",
                    "org_id": "1",
                    "orgc_id": "1",
                    "published": True,
                    "timestamp": "1705315200",
                    "attribute_count": "15",
                    "Tag": [
                        {"name": "tlp:amber"},
                        {"name": "apt29"}
                    ]
                }
            }
        ]
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.search_events("APT29")

        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args

        # Should use restSearch endpoint
        assert "/events/restSearch" in call_args[0][0]

        # Should include Authorization header
        assert "Authorization" in call_args[1]["headers"]

        # Verify response structure
        assert result is not None
        assert "response" in result
        assert len(result["response"]) > 0

        event = result["response"][0]["Event"]
        assert "id" in event
        assert "uuid" in event
        assert "info" in event
        assert "date" in event
        assert "threat_level_id" in event
        assert "Tag" in event

    await client.close()


@pytest.mark.asyncio
async def test_misp_search_attributes():
    """
    RED: Test that MISPClient can search for attributes by type and value.

    Expected behavior:
    - Search for attributes of specific type (ip-dst, domain, md5, etc.)
    - Return list of matching attributes with associated event info
    """
    client = MISPClient(
        base_url="https://misp.example.org",
        api_key="test-api-key"
    )

    # Mock successful API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": {
            "Attribute": [
                {
                    "id": "67890",
                    "event_id": "12345",
                    "category": "Network activity",
                    "type": "ip-dst",
                    "value": "185.141.63.120",
                    "to_ids": True,
                    "timestamp": "1705315200",
                    "comment": "C2 server for APT29 campaign",
                    "Event": {
                        "id": "12345",
                        "info": "APT29 Campaign",
                        "org_id": "1"
                    }
                }
            ]
        }
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.search_attributes(type="ip-dst", value="185.141.63.120")

        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args

        # Should use attributes/restSearch endpoint
        assert "/attributes/restSearch" in call_args[0][0]

        # Verify payload includes type and value
        payload = call_args[1]["json"]
        assert payload["type"] == "ip-dst"
        assert payload["value"] == "185.141.63.120"

        # Verify response structure
        assert result is not None
        assert "response" in result
        assert "Attribute" in result["response"]

        attr = result["response"]["Attribute"][0]
        assert attr["type"] == "ip-dst"
        assert attr["value"] == "185.141.63.120"
        assert "Event" in attr

    await client.close()


@pytest.mark.asyncio
async def test_misp_get_event():
    """
    RED: Test that MISPClient can get event details by ID.

    Expected behavior:
    - Fetch complete event details including all attributes
    - Return full event structure with attributes, tags, and metadata
    """
    client = MISPClient(
        base_url="https://misp.example.org",
        api_key="test-api-key"
    )

    # Mock successful API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "Event": {
            "id": "12345",
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "info": "APT29 Campaign Targeting Government Agencies",
            "date": "2024-01-15",
            "threat_level_id": "1",
            "analysis": "2",
            "distribution": "1",
            "published": True,
            "timestamp": "1705315200",
            "Org": {
                "id": "1",
                "name": "CIRCL"
            },
            "Orgc": {
                "id": "1",
                "name": "CIRCL"
            },
            "Attribute": [
                {
                    "id": "67890",
                    "type": "ip-dst",
                    "category": "Network activity",
                    "value": "185.141.63.120",
                    "to_ids": True
                },
                {
                    "id": "67891",
                    "type": "md5",
                    "category": "Payload delivery",
                    "value": "d41d8cd98f00b204e9800998ecf8427e",
                    "to_ids": True
                }
            ],
            "Tag": [
                {"name": "tlp:amber"},
                {"name": "apt29"},
                {"name": "misp-galaxy:mitre-attack-pattern=\"Spearphishing Attachment - T1566.001\""}
            ],
            "Galaxy": [
                {
                    "name": "MITRE ATT&CK - Attack Pattern",
                    "type": "mitre-attack-pattern",
                    "GalaxyCluster": [
                        {
                            "value": "Spearphishing Attachment - T1566.001",
                            "description": "Adversaries may send spearphishing emails..."
                        }
                    ]
                }
            ]
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_event("12345")

        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args

        # Should use events/view endpoint
        assert "/events/view/12345" in call_args[0][0]

        # Verify response structure
        assert result is not None
        assert "Event" in result

        event = result["Event"]
        assert event["id"] == "12345"
        assert "Attribute" in event
        assert len(event["Attribute"]) == 2
        assert "Tag" in event
        assert "Galaxy" in event
        assert "Org" in event

    await client.close()


@pytest.mark.asyncio
async def test_misp_get_correlations():
    """
    RED: Test that MISPClient can get correlated indicators.

    Expected behavior:
    - Given an indicator, find all related/correlated indicators
    - Return list of correlated events and attributes
    """
    client = MISPClient(
        base_url="https://misp.example.org",
        api_key="test-api-key"
    )

    # Mock successful API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": [
            {
                "Attribute": {
                    "id": "67890",
                    "type": "ip-dst",
                    "value": "185.141.63.120",
                    "event_id": "12345"
                },
                "RelatedAttribute": [
                    {
                        "id": "67900",
                        "type": "ip-dst",
                        "value": "185.141.63.121",
                        "event_id": "12346",
                        "Event": {
                            "id": "12346",
                            "info": "Related APT29 activity"
                        }
                    },
                    {
                        "id": "67901",
                        "type": "domain",
                        "value": "malware.example.com",
                        "event_id": "12347",
                        "Event": {
                            "id": "12347",
                            "info": "Malware distribution network"
                        }
                    }
                ]
            }
        ]
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.get_correlations("185.141.63.120")

        # Verify request was made
        mock_post.assert_called_once()

        # Verify response structure
        assert result is not None
        assert "response" in result
        assert len(result["response"]) > 0

        correlation = result["response"][0]
        assert "Attribute" in correlation
        assert "RelatedAttribute" in correlation
        assert len(correlation["RelatedAttribute"]) == 2

    await client.close()


@pytest.mark.asyncio
async def test_misp_handles_api_error():
    """
    RED: Test that MISPClient handles API errors gracefully.

    Expected behavior:
    - When API returns error status, client should return None
    - No exceptions should be raised
    """
    client = MISPClient(
        base_url="https://misp.example.org",
        api_key="test-api-key"
    )

    # Mock server error response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.search_events("test")

        # Should return None on error
        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_misp_handles_timeout():
    """
    RED: Test timeout handling.

    Expected behavior:
    - When request times out, return None
    - No exceptions should propagate
    """
    client = MISPClient(
        base_url="https://misp.example.org",
        api_key="test-api-key",
        timeout=5
    )

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.TimeoutException("Request timed out")

        result = await client.search_events("test")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_misp_client_close():
    """
    RED: Test that client can be properly closed.
    """
    client = MISPClient(
        base_url="https://misp.example.org",
        api_key="test-api-key"
    )

    # Should not raise any exceptions
    await client.close()


@pytest.mark.asyncio
async def test_misp_handles_auth_error():
    """
    RED: Test handling of authentication errors.

    Expected behavior:
    - When API returns 401/403, client should return None
    - No exceptions should be raised
    """
    client = MISPClient(
        base_url="https://misp.example.org",
        api_key="invalid-api-key"
    )

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.search_events("test")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_misp_handles_request_error():
    """
    RED: Test handling of network/request errors.

    Expected behavior:
    - When network error occurs, return None
    - No exceptions should propagate
    """
    client = MISPClient(
        base_url="https://misp.example.org",
        api_key="test-api-key"
    )

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.RequestError("Connection failed")

        result = await client.search_events("test")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_misp_custom_timeout():
    """
    RED: Test that custom timeout is applied.
    """
    client = MISPClient(
        base_url="https://misp.example.org",
        api_key="test-api-key",
        timeout=60
    )

    # Verify timeout was set
    assert client.timeout == 60

    await client.close()


@pytest.mark.asyncio
async def test_misp_search_events_no_results():
    """
    RED: Test handling of search with no results.

    Expected behavior:
    - Return empty response structure, not None
    """
    client = MISPClient(
        base_url="https://misp.example.org",
        api_key="test-api-key"
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": []
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.search_events("nonexistent-query-xyz")

        assert result is not None
        assert result["response"] == []

    await client.close()


@pytest.mark.asyncio
async def test_misp_get_event_not_found():
    """
    RED: Test handling of non-existent event.

    Expected behavior:
    - Return None when event doesn't exist
    """
    client = MISPClient(
        base_url="https://misp.example.org",
        api_key="test-api-key"
    )

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Event not found"

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_event("99999999")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_misp_uses_correct_headers():
    """
    RED: Test that client uses correct MISP API headers.
    """
    client = MISPClient(
        base_url="https://misp.example.org",
        api_key="test-api-key-12345"
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": []}

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        await client.search_events("test")

        # Verify headers
        call_args = mock_post.call_args
        headers = call_args[1]["headers"]

        assert headers["Authorization"] == "test-api-key-12345"
        assert headers["Accept"] == "application/json"
        assert headers["Content-Type"] == "application/json"

    await client.close()


@pytest.mark.asyncio
async def test_misp_synthetic_search_events():
    """
    RED: Test synthetic data generation for search_events in demo mode.

    When no real MISP instance is available, the client should generate
    realistic synthetic data for demonstration purposes.
    """
    # Demo mode client (no real API connection)
    client = MISPClient(
        base_url="https://misp.example.org",
        api_key="test-api-key",
        demo_mode=True
    )

    result = await client.search_events("APT29")

    # Should return synthetic data
    assert result is not None
    assert "response" in result
    assert len(result["response"]) > 0

    event = result["response"][0]["Event"]
    assert "id" in event
    assert "uuid" in event
    assert "info" in event
    assert "date" in event
    assert "threat_level_id" in event
    assert "Tag" in event

    await client.close()


@pytest.mark.asyncio
async def test_misp_synthetic_get_event():
    """
    RED: Test synthetic data generation for get_event in demo mode.
    """
    client = MISPClient(
        base_url="https://misp.example.org",
        api_key="test-api-key",
        demo_mode=True
    )

    result = await client.get_event("12345")

    # Should return synthetic data
    assert result is not None
    assert "Event" in result

    event = result["Event"]
    assert "id" in event
    assert "Attribute" in event
    assert len(event["Attribute"]) > 0
    assert "Tag" in event

    await client.close()


@pytest.mark.asyncio
async def test_misp_synthetic_search_attributes():
    """
    RED: Test synthetic data generation for search_attributes in demo mode.
    """
    client = MISPClient(
        base_url="https://misp.example.org",
        api_key="test-api-key",
        demo_mode=True
    )

    result = await client.search_attributes(type="ip-dst", value="1.2.3.4")

    # Should return synthetic data
    assert result is not None
    assert "response" in result
    assert "Attribute" in result["response"]
    assert len(result["response"]["Attribute"]) > 0

    attr = result["response"]["Attribute"][0]
    assert "type" in attr
    assert "value" in attr
    assert "Event" in attr

    await client.close()


@pytest.mark.asyncio
async def test_misp_synthetic_get_correlations():
    """
    RED: Test synthetic data generation for get_correlations in demo mode.
    """
    client = MISPClient(
        base_url="https://misp.example.org",
        api_key="test-api-key",
        demo_mode=True
    )

    result = await client.get_correlations("185.141.63.120")

    # Should return synthetic data
    assert result is not None
    assert "response" in result
    assert len(result["response"]) > 0

    correlation = result["response"][0]
    assert "Attribute" in correlation
    assert "RelatedAttribute" in correlation
    assert len(correlation["RelatedAttribute"]) > 0

    await client.close()
