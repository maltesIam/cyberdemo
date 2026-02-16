"""
Unit tests for Censys API Client.

Censys provides internet-wide scanning data for hosts, certificates, and services.
It's similar to Shodan but with different data sources and scanning methodology.

API Documentation: https://search.censys.io/api
Rate limit: 250 requests/month (free tier)

These tests are written FIRST following TDD (RED phase).
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

# Import will fail until we implement the module (RED phase)
try:
    from src.clients.censys_client import CensysClient
except ImportError:
    pass


# =============================================================================
# Host Search Tests
# =============================================================================


@pytest.mark.asyncio
async def test_censys_search_hosts_returns_data():
    """
    RED: Test that CensysClient.search_hosts() returns search results.

    Expected behavior:
    - Execute search query on Censys hosts API
    - Return list of matching hosts with IP, services, and metadata
    """
    client = CensysClient(api_id="test-api-id", api_secret="test-api-secret")

    # Mock successful API response based on Censys Search 2.0 API structure
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 200,
        "status": "OK",
        "result": {
            "query": "services.port: 22",
            "total": 2,
            "hits": [
                {
                    "ip": "8.8.8.8",
                    "services": [
                        {
                            "port": 22,
                            "service_name": "SSH",
                            "transport_protocol": "TCP",
                            "software": [
                                {"product": "OpenSSH", "version": "8.2"}
                            ]
                        }
                    ],
                    "location": {
                        "country": "United States",
                        "country_code": "US",
                        "city": "Mountain View"
                    },
                    "autonomous_system": {
                        "asn": 15169,
                        "name": "GOOGLE",
                        "description": "Google LLC"
                    },
                    "last_updated_at": "2024-01-15T10:30:00Z"
                },
                {
                    "ip": "1.2.3.4",
                    "services": [
                        {
                            "port": 22,
                            "service_name": "SSH",
                            "transport_protocol": "TCP",
                            "software": [
                                {"product": "OpenSSH", "version": "7.9"}
                            ]
                        },
                        {
                            "port": 80,
                            "service_name": "HTTP",
                            "transport_protocol": "TCP",
                            "software": [
                                {"product": "nginx", "version": "1.18.0"}
                            ]
                        }
                    ],
                    "location": {
                        "country": "Germany",
                        "country_code": "DE",
                        "city": "Berlin"
                    },
                    "autonomous_system": {
                        "asn": 12345,
                        "name": "EXAMPLE-ISP",
                        "description": "Example ISP"
                    },
                    "last_updated_at": "2024-01-14T08:00:00Z"
                }
            ],
            "links": {
                "next": "eyJxdWVyeSI6..."
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.search_hosts("services.port: 22")

        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "search" in call_args[0][0]

        # Verify response structure
        assert result is not None
        assert "hits" in result
        assert len(result["hits"]) == 2
        assert result["hits"][0]["ip"] == "8.8.8.8"
        assert result["total"] == 2

    await client.close()


@pytest.mark.asyncio
async def test_censys_search_hosts_with_pagination():
    """
    RED: Test search_hosts with pagination using cursor.

    Expected behavior:
    - Accept cursor parameter for pagination
    - Return results for specified page
    """
    client = CensysClient(api_id="test-api-id", api_secret="test-api-secret")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 200,
        "status": "OK",
        "result": {
            "query": "services.port: 443",
            "total": 150,
            "hits": [
                {
                    "ip": "10.20.30.40",
                    "services": [{"port": 443, "service_name": "HTTPS"}],
                    "location": {"country_code": "JP"}
                }
            ],
            "links": {
                "prev": "eyJwcmV2Ijoi...",
                "next": "eyJuZXh0Ijoi..."
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.search_hosts("services.port: 443", cursor="eyJxdWVyeSI6...")

        # Verify cursor was passed
        call_args = mock_get.call_args
        assert call_args[1]["params"]["cursor"] == "eyJxdWVyeSI6..."

        assert result is not None
        assert len(result["hits"]) == 1

    await client.close()


@pytest.mark.asyncio
async def test_censys_search_hosts_no_results():
    """
    RED: Test search_hosts when no matches found.

    Expected behavior:
    - Return empty hits list when no matches
    """
    client = CensysClient(api_id="test-api-id", api_secret="test-api-secret")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 200,
        "status": "OK",
        "result": {
            "query": "nonexistent-very-specific-query",
            "total": 0,
            "hits": [],
            "links": {}
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.search_hosts("nonexistent-very-specific-query")

        assert result is not None
        assert result["hits"] == []
        assert result["total"] == 0

    await client.close()


# =============================================================================
# Host Details Tests
# =============================================================================


@pytest.mark.asyncio
async def test_censys_get_host_details():
    """
    RED: Test that CensysClient.get_host() returns detailed host information.

    Expected behavior:
    - Fetch host details for an IP
    - Return dict with services, location, AS info, etc.
    """
    client = CensysClient(api_id="test-api-id", api_secret="test-api-secret")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 200,
        "status": "OK",
        "result": {
            "ip": "8.8.8.8",
            "services": [
                {
                    "port": 53,
                    "service_name": "DNS",
                    "transport_protocol": "UDP",
                    "extended_service_name": "Google Public DNS",
                    "software": [],
                    "observed_at": "2024-01-15T10:30:00Z"
                },
                {
                    "port": 443,
                    "service_name": "HTTPS",
                    "transport_protocol": "TCP",
                    "software": [
                        {"product": "nginx", "version": "1.18.0"}
                    ],
                    "tls": {
                        "certificates": {
                            "leaf_data": {
                                "subject_dn": "CN=dns.google"
                            }
                        }
                    },
                    "observed_at": "2024-01-15T10:30:00Z"
                }
            ],
            "location": {
                "continent": "North America",
                "country": "United States",
                "country_code": "US",
                "city": "Mountain View",
                "postal_code": "94043",
                "timezone": "America/Los_Angeles",
                "coordinates": {
                    "latitude": 37.4056,
                    "longitude": -122.0775
                }
            },
            "autonomous_system": {
                "asn": 15169,
                "name": "GOOGLE",
                "description": "Google LLC",
                "bgp_prefix": "8.8.8.0/24",
                "country_code": "US"
            },
            "operating_system": {
                "product": "Linux",
                "vendor": "Linux",
                "version": None
            },
            "last_updated_at": "2024-01-15T10:30:00Z",
            "dns": {
                "reverse_dns": {
                    "names": ["dns.google"]
                }
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_host("8.8.8.8")

        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "8.8.8.8" in call_args[0][0]

        # Verify response structure
        assert result is not None
        assert result["ip"] == "8.8.8.8"
        assert len(result["services"]) == 2
        assert result["location"]["country_code"] == "US"
        assert result["autonomous_system"]["asn"] == 15169

    await client.close()


@pytest.mark.asyncio
async def test_censys_get_host_not_found():
    """
    RED: Test get_host when IP not found in Censys.

    Expected behavior:
    - Return None when IP is not in database
    """
    client = CensysClient(api_id="test-api-id", api_secret="test-api-secret")

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {
        "code": 404,
        "status": "Not Found",
        "error": "No information available for that IP."
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_host("10.0.0.1")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_censys_get_host_parses_services():
    """
    RED: Test that services are correctly parsed from host details.

    Expected behavior:
    - Services include port, protocol, software info
    """
    client = CensysClient(api_id="test-api-id", api_secret="test-api-secret")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 200,
        "status": "OK",
        "result": {
            "ip": "192.168.1.1",
            "services": [
                {
                    "port": 22,
                    "service_name": "SSH",
                    "transport_protocol": "TCP",
                    "software": [
                        {"product": "OpenSSH", "version": "8.4", "vendor": "OpenBSD"}
                    ],
                    "banner": "SSH-2.0-OpenSSH_8.4"
                },
                {
                    "port": 3306,
                    "service_name": "MYSQL",
                    "transport_protocol": "TCP",
                    "software": [
                        {"product": "MySQL", "version": "8.0.27"}
                    ]
                }
            ],
            "location": {"country_code": "DE"},
            "autonomous_system": {"asn": 12345},
            "last_updated_at": "2024-01-15T10:30:00Z"
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_host("192.168.1.1")

        assert result is not None
        assert len(result["services"]) == 2

        # Check SSH service
        ssh_service = next((s for s in result["services"] if s["port"] == 22), None)
        assert ssh_service is not None
        assert ssh_service["service_name"] == "SSH"
        assert ssh_service["software"][0]["product"] == "OpenSSH"
        assert ssh_service["software"][0]["version"] == "8.4"

        # Check MySQL service
        mysql_service = next((s for s in result["services"] if s["port"] == 3306), None)
        assert mysql_service is not None
        assert mysql_service["service_name"] == "MYSQL"

    await client.close()


# =============================================================================
# Rate Limit Tests (250/month)
# =============================================================================


@pytest.mark.asyncio
async def test_censys_handles_rate_limit():
    """
    RED: Test that client handles 429 rate limit response.

    Censys free tier: 250 requests/month

    Expected behavior:
    - When API returns 429, return None
    - Log warning about rate limit
    """
    client = CensysClient(api_id="test-api-id", api_secret="test-api-secret")

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.json.return_value = {
        "code": 429,
        "status": "Too Many Requests",
        "error": "Rate limit exceeded. You have exceeded your monthly quota of 250 requests."
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_host("8.8.8.8")

        # Should return None on rate limit
        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_censys_search_rate_limit():
    """
    RED: Test that search also handles rate limits.

    Expected behavior:
    - Search returns None on rate limit
    """
    client = CensysClient(api_id="test-api-id", api_secret="test-api-secret")

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.json.return_value = {
        "code": 429,
        "status": "Too Many Requests",
        "error": "Rate limit exceeded"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.search_hosts("services.port: 22")

        assert result is None

    await client.close()


# =============================================================================
# Error Handling Tests
# =============================================================================


@pytest.mark.asyncio
async def test_censys_handles_api_error():
    """
    RED: Test handling of generic API errors (400).

    Expected behavior:
    - Return None on API error
    - Log error message
    """
    client = CensysClient(api_id="test-api-id", api_secret="test-api-secret")

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        "code": 400,
        "status": "Bad Request",
        "error": "Invalid query syntax"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.search_hosts("invalid:::query")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_censys_handles_auth_error():
    """
    RED: Test handling of authentication errors (401).

    Expected behavior:
    - Return None on auth error
    - Log error about invalid credentials
    """
    client = CensysClient(api_id="invalid-id", api_secret="invalid-secret")

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {
        "code": 401,
        "status": "Unauthorized",
        "error": "Invalid API credentials"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_host("8.8.8.8")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_censys_handles_forbidden():
    """
    RED: Test handling of forbidden access (403).

    Expected behavior:
    - Return None on forbidden
    """
    client = CensysClient(api_id="test-api-id", api_secret="test-api-secret")

    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.json.return_value = {
        "code": 403,
        "status": "Forbidden",
        "error": "Access denied to this resource"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_host("8.8.8.8")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_censys_handles_server_error():
    """
    RED: Test handling of server errors (500).

    Expected behavior:
    - Return None on server error
    - Log error
    """
    client = CensysClient(api_id="test-api-id", api_secret="test-api-secret")

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {
        "code": 500,
        "status": "Internal Server Error",
        "error": "An unexpected error occurred"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_host("8.8.8.8")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_censys_handles_timeout():
    """
    RED: Test timeout handling.

    Expected behavior:
    - Return None on timeout
    - No exceptions should propagate
    """
    client = CensysClient(api_id="test-api-id", api_secret="test-api-secret", timeout=5)

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Request timed out")

        result = await client.get_host("8.8.8.8")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_censys_handles_request_error():
    """
    RED: Test handling of network/request errors.

    Expected behavior:
    - Return None on network error
    - No exceptions should propagate
    """
    client = CensysClient(api_id="test-api-id", api_secret="test-api-secret")

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await client.search_hosts("services.port: 22")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_censys_handles_connection_error():
    """
    RED: Test handling of connection errors.

    Expected behavior:
    - Return None on connection error
    """
    client = CensysClient(api_id="test-api-id", api_secret="test-api-secret")

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.ConnectError("Failed to connect")

        result = await client.get_host("8.8.8.8")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_censys_handles_malformed_response():
    """
    RED: Test handling of malformed API response.

    Expected behavior:
    - Return None without crashing when response structure is unexpected
    """
    client = CensysClient(api_id="test-api-id", api_secret="test-api-secret")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "unexpected": "data"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_host("8.8.8.8")

        # Should handle gracefully
        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_censys_handles_json_parse_error():
    """
    RED: Test handling of JSON parse errors.

    Expected behavior:
    - Return None and log error
    """
    client = CensysClient(api_id="test-api-id", api_secret="test-api-secret")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_host("8.8.8.8")

        assert result is None

    await client.close()


# =============================================================================
# Client Configuration Tests
# =============================================================================


@pytest.mark.asyncio
async def test_censys_requires_api_credentials():
    """
    RED: Test that client requires both API ID and API Secret.

    Censys uses HTTP Basic Auth with API ID as username and API Secret as password.

    Expected behavior:
    - Client stores both api_id and api_secret
    """
    client = CensysClient(api_id="my-api-id", api_secret="my-api-secret")

    assert client.api_id == "my-api-id"
    assert client.api_secret == "my-api-secret"

    await client.close()


@pytest.mark.asyncio
async def test_censys_custom_timeout():
    """
    RED: Test that custom timeout is applied.
    """
    client = CensysClient(api_id="test-id", api_secret="test-secret", timeout=60)

    assert client.timeout == 60

    await client.close()


@pytest.mark.asyncio
async def test_censys_client_close():
    """
    RED: Test that client can be properly closed.
    """
    client = CensysClient(api_id="test-id", api_secret="test-secret")

    # Should not raise any exceptions
    await client.close()


@pytest.mark.asyncio
async def test_censys_uses_correct_base_url():
    """
    RED: Test that client uses correct Censys API base URL.
    """
    client = CensysClient(api_id="test-id", api_secret="test-secret")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 200,
        "status": "OK",
        "result": {
            "ip": "8.8.8.8",
            "services": [],
            "location": {},
            "autonomous_system": {}
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        await client.get_host("8.8.8.8")

        # Verify correct URL was called
        call_args = mock_get.call_args
        assert "search.censys.io" in call_args[0][0]

    await client.close()


@pytest.mark.asyncio
async def test_censys_uses_basic_auth():
    """
    RED: Test that API credentials are used for HTTP Basic Auth.

    Censys uses Basic Auth with API ID as username and API Secret as password.
    """
    client = CensysClient(api_id="test-api-id-123", api_secret="test-api-secret-456")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 200,
        "status": "OK",
        "result": {
            "ip": "8.8.8.8",
            "services": [],
            "location": {},
            "autonomous_system": {}
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        await client.get_host("8.8.8.8")

        # Verify auth was included
        call_args = mock_get.call_args
        assert "auth" in call_args[1]
        auth = call_args[1]["auth"]
        assert auth == ("test-api-id-123", "test-api-secret-456")

    await client.close()


@pytest.mark.asyncio
async def test_censys_context_manager():
    """
    RED: Test using client as async context manager.
    """
    async with CensysClient(api_id="test-id", api_secret="test-secret") as client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 200,
            "status": "OK",
            "result": {
                "ip": "8.8.8.8",
                "services": [],
                "location": {},
                "autonomous_system": {}
            }
        }

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            result = await client.get_host("8.8.8.8")
            assert result is not None


# =============================================================================
# Full Workflow Test
# =============================================================================


@pytest.mark.asyncio
async def test_censys_full_workflow():
    """
    RED: Test full workflow: search hosts -> get host details.

    This simulates a complete enrichment workflow.
    """
    client = CensysClient(api_id="test-api-id", api_secret="test-api-secret")

    # Mock for search
    mock_search_response = MagicMock()
    mock_search_response.status_code = 200
    mock_search_response.json.return_value = {
        "code": 200,
        "status": "OK",
        "result": {
            "query": "services.port: 22",
            "total": 1,
            "hits": [
                {
                    "ip": "185.199.108.153",
                    "services": [{"port": 22, "service_name": "SSH"}],
                    "location": {"country_code": "US"}
                }
            ]
        }
    }

    # Mock for host details
    mock_host_response = MagicMock()
    mock_host_response.status_code = 200
    mock_host_response.json.return_value = {
        "code": 200,
        "status": "OK",
        "result": {
            "ip": "185.199.108.153",
            "services": [
                {
                    "port": 22,
                    "service_name": "SSH",
                    "transport_protocol": "TCP",
                    "software": [{"product": "OpenSSH", "version": "8.2"}]
                },
                {
                    "port": 443,
                    "service_name": "HTTPS",
                    "transport_protocol": "TCP",
                    "software": [{"product": "nginx", "version": "1.18.0"}]
                }
            ],
            "location": {
                "country_code": "US",
                "city": "San Francisco"
            },
            "autonomous_system": {
                "asn": 36459,
                "name": "GITHUB",
                "description": "GitHub, Inc."
            },
            "last_updated_at": "2024-01-15T10:30:00Z"
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        # First call returns search results
        mock_get.return_value = mock_search_response

        # Step 1: Search for hosts
        search_result = await client.search_hosts("services.port: 22")
        assert search_result is not None
        assert len(search_result["hits"]) == 1
        ip_to_lookup = search_result["hits"][0]["ip"]

        # Change mock response for host details
        mock_get.return_value = mock_host_response

        # Step 2: Get host details
        host_details = await client.get_host(ip_to_lookup)
        assert host_details is not None
        assert host_details["ip"] == "185.199.108.153"
        assert len(host_details["services"]) == 2
        assert host_details["autonomous_system"]["name"] == "GITHUB"

    await client.close()
