"""
Unit tests for OpenCTI API Client.

OpenCTI (Open Cyber Threat Intelligence) is an open-source platform
for managing cyber threat intelligence. It uses STIX 2.1 format and
provides a GraphQL API.

This implementation is a synthetic/mock client for demo purposes,
as OpenCTI is typically self-hosted.

API Documentation: https://docs.opencti.io/latest/deployment/connectors/
GraphQL API: https://docs.opencti.io/latest/development/api-usage/

These tests are written FIRST following TDD (RED phase).
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

# Import will fail until we implement the module (RED phase)
try:
    from src.clients.opencti_client import OpenCTIClient
except ImportError:
    pass


# =============================================================================
# Search Indicators Tests
# =============================================================================


@pytest.mark.asyncio
async def test_opencti_search_indicators():
    """
    RED: Test that OpenCTIClient.search_indicators() returns STIX indicators.

    Expected behavior:
    - Execute search query on OpenCTI GraphQL API
    - Return list of STIX indicators with pattern, type, etc.
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    result = await client.search_indicators("malware")

    # Verify response structure
    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0

    # Verify indicator structure (STIX 2.1 format)
    indicator = result[0]
    assert "id" in indicator
    assert "type" in indicator
    assert indicator["type"] == "indicator"
    assert "pattern" in indicator
    assert "pattern_type" in indicator
    assert "name" in indicator

    await client.close()


@pytest.mark.asyncio
async def test_opencti_search_indicators_empty_results():
    """
    RED: Test search_indicators when no matches found.

    Expected behavior:
    - Return empty list when no indicators match query
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    result = await client.search_indicators("nonexistent-query-xyz-12345")

    assert result is not None
    assert isinstance(result, list)
    # May return empty list for non-matching query
    # The synthetic data should still return something for common queries

    await client.close()


@pytest.mark.asyncio
async def test_opencti_search_indicators_by_pattern_type():
    """
    RED: Test search_indicators filtering by pattern type (stix, yara, sigma).

    Expected behavior:
    - Filter results by pattern_type
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    result = await client.search_indicators("ip", pattern_type="stix")

    assert result is not None
    assert isinstance(result, list)

    # All returned indicators should have STIX pattern type
    for indicator in result:
        assert indicator.get("pattern_type") == "stix"

    await client.close()


# =============================================================================
# Get Indicator Details Tests
# =============================================================================


@pytest.mark.asyncio
async def test_opencti_get_indicator():
    """
    RED: Test that OpenCTIClient.get_indicator() returns indicator details.

    Expected behavior:
    - Fetch indicator by ID
    - Return full STIX indicator object with labels, kill chain phases, etc.
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    # Get a known indicator ID from synthetic data
    result = await client.get_indicator("indicator--abc123")

    assert result is not None
    assert result["id"] == "indicator--abc123"
    assert result["type"] == "indicator"
    assert "pattern" in result
    assert "name" in result
    assert "description" in result
    assert "valid_from" in result

    await client.close()


@pytest.mark.asyncio
async def test_opencti_get_indicator_not_found():
    """
    RED: Test get_indicator when ID not found.

    Expected behavior:
    - Return None when indicator ID doesn't exist
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    result = await client.get_indicator("indicator--nonexistent-id-999")

    assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_opencti_get_indicator_includes_labels():
    """
    RED: Test that indicator details include labels (tags).

    Expected behavior:
    - Indicator should include labels array
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    result = await client.get_indicator("indicator--abc123")

    assert result is not None
    assert "labels" in result
    assert isinstance(result["labels"], list)

    await client.close()


# =============================================================================
# Search Threat Actors Tests
# =============================================================================


@pytest.mark.asyncio
async def test_opencti_search_threat_actors():
    """
    RED: Test that OpenCTIClient.search_threat_actors() returns threat actors.

    Expected behavior:
    - Execute search query for threat actors
    - Return list of STIX threat-actor objects
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    result = await client.search_threat_actors("APT")

    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0

    # Verify threat actor structure (STIX 2.1 format)
    actor = result[0]
    assert "id" in actor
    assert "type" in actor
    assert actor["type"] == "threat-actor"
    assert "name" in actor
    assert "aliases" in actor or "description" in actor

    await client.close()


@pytest.mark.asyncio
async def test_opencti_search_threat_actors_by_sophistication():
    """
    RED: Test filtering threat actors by sophistication level.

    Expected behavior:
    - Filter by sophistication (none, minimal, intermediate, advanced, expert)
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    result = await client.search_threat_actors("", sophistication="advanced")

    assert result is not None
    assert isinstance(result, list)

    # All returned actors should have advanced sophistication
    for actor in result:
        assert actor.get("sophistication") == "advanced"

    await client.close()


# =============================================================================
# Get Threat Actor Details Tests
# =============================================================================


@pytest.mark.asyncio
async def test_opencti_get_threat_actor():
    """
    RED: Test that OpenCTIClient.get_threat_actor() returns threat actor details.

    Expected behavior:
    - Fetch threat actor by ID
    - Return full STIX threat-actor object
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    result = await client.get_threat_actor("threat-actor--apt28")

    assert result is not None
    assert result["id"] == "threat-actor--apt28"
    assert result["type"] == "threat-actor"
    assert "name" in result
    assert "description" in result
    assert "goals" in result or "aliases" in result

    await client.close()


@pytest.mark.asyncio
async def test_opencti_get_threat_actor_not_found():
    """
    RED: Test get_threat_actor when ID not found.

    Expected behavior:
    - Return None when threat actor ID doesn't exist
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    result = await client.get_threat_actor("threat-actor--nonexistent-999")

    assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_opencti_get_threat_actor_includes_aliases():
    """
    RED: Test that threat actor details include aliases.

    Expected behavior:
    - Threat actor should include aliases array
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    result = await client.get_threat_actor("threat-actor--apt28")

    assert result is not None
    assert "aliases" in result
    assert isinstance(result["aliases"], list)

    await client.close()


# =============================================================================
# Get Relationships Tests
# =============================================================================


@pytest.mark.asyncio
async def test_opencti_get_relationships():
    """
    RED: Test that OpenCTIClient.get_relationships() returns STIX relationships.

    Expected behavior:
    - Fetch relationships for an indicator
    - Return list of STIX relationship objects
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    result = await client.get_relationships("indicator--abc123")

    assert result is not None
    assert isinstance(result, list)

    # Verify relationship structure (STIX 2.1)
    if len(result) > 0:
        relationship = result[0]
        assert "id" in relationship
        assert "type" in relationship
        assert relationship["type"] == "relationship"
        assert "relationship_type" in relationship
        assert "source_ref" in relationship
        assert "target_ref" in relationship

    await client.close()


@pytest.mark.asyncio
async def test_opencti_get_relationships_by_type():
    """
    RED: Test filtering relationships by type.

    Expected behavior:
    - Filter by relationship_type (indicates, uses, attributed-to, etc.)
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    result = await client.get_relationships(
        "indicator--abc123",
        relationship_type="indicates"
    )

    assert result is not None
    assert isinstance(result, list)

    # All returned relationships should be "indicates" type
    for rel in result:
        assert rel.get("relationship_type") == "indicates"

    await client.close()


@pytest.mark.asyncio
async def test_opencti_get_relationships_empty():
    """
    RED: Test get_relationships when no relationships exist.

    Expected behavior:
    - Return empty list when no relationships found
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    result = await client.get_relationships("indicator--no-relationships")

    assert result is not None
    assert isinstance(result, list)
    assert result == []

    await client.close()


# =============================================================================
# Error Handling Tests (for _make_request method used in production mode)
# =============================================================================


@pytest.mark.asyncio
async def test_opencti_handles_api_error():
    """
    RED: Test handling of generic API errors via _make_request.

    Note: The synthetic client uses embedded data, but the _make_request
    method handles real API calls. This test verifies error handling
    for production GraphQL API usage.

    Expected behavior:
    - _make_request returns None on API error
    - No exceptions should propagate
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    # Mock HTTP client to simulate API error
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {
        "errors": [{"message": "Internal server error"}]
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        # Test _make_request directly (used for real API calls)
        result = await client._make_request("query { test }")

        # Should return None on error, not raise exception
        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_opencti_handles_timeout():
    """
    RED: Test timeout handling via _make_request.

    Expected behavior:
    - _make_request returns None on timeout
    - No exceptions should propagate
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key",
        timeout=5
    )

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.TimeoutException("Request timed out")

        # Test _make_request directly
        result = await client._make_request("query { test }")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_opencti_handles_connection_error():
    """
    RED: Test handling of connection errors via _make_request.

    Expected behavior:
    - _make_request returns None on connection error
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.ConnectError("Failed to connect")

        # Test _make_request directly
        result = await client._make_request("query { test }")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_opencti_handles_auth_error():
    """
    RED: Test handling of authentication errors (401) via _make_request.

    Expected behavior:
    - _make_request returns None on auth error
    - Log error about invalid credentials
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="invalid-api-key"
    )

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {
        "errors": [{"message": "Invalid API key"}]
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        # Test _make_request directly
        result = await client._make_request("query { test }")

        assert result is None

    await client.close()


# =============================================================================
# Client Lifecycle Tests
# =============================================================================


@pytest.mark.asyncio
async def test_opencti_client_close():
    """
    RED: Test that client can be properly closed.
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    # Should not raise any exceptions
    await client.close()


@pytest.mark.asyncio
async def test_opencti_context_manager():
    """
    RED: Test using client as async context manager.
    """
    async with OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    ) as client:
        result = await client.search_indicators("malware")
        assert result is not None


@pytest.mark.asyncio
async def test_opencti_client_configuration():
    """
    RED: Test that client stores configuration correctly.
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="my-api-key-123",
        timeout=60
    )

    assert client.base_url == "https://opencti.example.com"
    assert client.api_key == "my-api-key-123"
    assert client.timeout == 60

    await client.close()


@pytest.mark.asyncio
async def test_opencti_default_timeout():
    """
    RED: Test that default timeout is applied.
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    # Default timeout should be 30 seconds
    assert client.timeout == 30

    await client.close()


# =============================================================================
# Synthetic Data Tests (Demo Mode)
# =============================================================================


@pytest.mark.asyncio
async def test_opencti_synthetic_indicators():
    """
    RED: Test that synthetic data is available for demo mode.

    Expected behavior:
    - Client should return synthetic STIX indicators
    - Indicators should be realistic for demo purposes
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    result = await client.search_indicators("ip")

    assert result is not None
    assert len(result) > 0

    # Verify synthetic data has proper STIX indicator patterns
    for indicator in result:
        assert indicator["pattern_type"] in ["stix", "yara", "sigma", "snort"]
        assert indicator["pattern"] is not None

    await client.close()


@pytest.mark.asyncio
async def test_opencti_synthetic_threat_actors():
    """
    RED: Test that synthetic threat actor data is available.

    Expected behavior:
    - Client should return synthetic threat actors
    - Threat actors should match known APT groups for realism
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    result = await client.search_threat_actors("apt")

    assert result is not None
    assert len(result) > 0

    # Verify threat actors have proper structure
    for actor in result:
        assert "name" in actor
        assert "sophistication" in actor

    await client.close()


# =============================================================================
# Integration-like Tests
# =============================================================================


@pytest.mark.asyncio
async def test_opencti_full_workflow():
    """
    RED: Test full workflow: search indicators -> get details -> get relationships.

    This simulates a complete threat intelligence enrichment workflow.
    """
    client = OpenCTIClient(
        base_url="https://opencti.example.com",
        api_key="test-api-key"
    )

    # Step 1: Search for indicators
    indicators = await client.search_indicators("malware")
    assert indicators is not None
    assert len(indicators) > 0

    # Step 2: Get details for first indicator
    indicator_id = indicators[0]["id"]
    details = await client.get_indicator(indicator_id)
    assert details is not None
    assert details["id"] == indicator_id

    # Step 3: Get relationships for the indicator
    relationships = await client.get_relationships(indicator_id)
    assert relationships is not None
    assert isinstance(relationships, list)

    await client.close()
