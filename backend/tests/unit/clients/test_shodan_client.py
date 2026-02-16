"""
Unit tests for Shodan API Client.

Shodan is the search engine for internet-connected devices. It provides
information about exposed services, open ports, and vulnerabilities.

API Documentation: https://developer.shodan.io/api
Rate limit: 100 requests/month (free tier)

These tests are written FIRST following TDD (Red-Green-Refactor).
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from typing import List

# Import will fail until we implement the module (RED phase)
try:
    from src.clients.shodan_client import (
        ShodanClient,
        ServiceInfo,
        HostInfo,
        VulnerabilityInfo,
    )
except ImportError:
    pass


# ============================================================================
# HOST INFORMATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_shodan_get_host_returns_host_info():
    """
    RED: Test that ShodanClient.get_host() returns host information.

    Expected behavior:
    - Fetch host information for an IP
    - Return HostInfo with IP, ports, services, OS, etc.
    """
    client = ShodanClient(api_key="test-api-key")

    # Mock successful API response based on Shodan API structure
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ip_str": "8.8.8.8",
        "ip": 134744072,
        "org": "Google LLC",
        "isp": "Google LLC",
        "asn": "AS15169",
        "hostnames": ["dns.google"],
        "country_code": "US",
        "country_name": "United States",
        "city": "Mountain View",
        "region_code": "CA",
        "os": None,
        "ports": [53, 443],
        "vulns": [],
        "tags": ["cloud"],
        "last_update": "2024-01-15T10:30:00.000000",
        "data": [
            {
                "port": 53,
                "transport": "udp",
                "product": "Google DNS",
                "version": None,
                "cpe": [],
                "timestamp": "2024-01-15T10:30:00.000000"
            },
            {
                "port": 443,
                "transport": "tcp",
                "product": "nginx",
                "version": "1.18.0",
                "cpe": ["cpe:/a:nginx:nginx:1.18.0"],
                "timestamp": "2024-01-15T10:30:00.000000"
            }
        ]
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_host("8.8.8.8")

        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "8.8.8.8" in call_args[0][0]
        assert call_args[1]["params"]["key"] == "test-api-key"

        # Verify response structure
        assert result is not None
        assert isinstance(result, HostInfo)
        assert result.ip == "8.8.8.8"
        assert result.org == "Google LLC"
        assert result.asn == "AS15169"
        assert result.country_code == "US"
        assert 53 in result.ports
        assert 443 in result.ports
        assert len(result.services) == 2

    await client.close()


@pytest.mark.asyncio
async def test_shodan_get_host_parses_services():
    """
    RED: Test that services are correctly parsed from host data.

    Expected behavior:
    - Services include port, transport, product, version
    - Each service is a ServiceInfo object
    """
    client = ShodanClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ip_str": "192.168.1.1",
        "ip": 3232235777,
        "org": "Test Org",
        "isp": "Test ISP",
        "asn": "AS12345",
        "hostnames": [],
        "country_code": "DE",
        "country_name": "Germany",
        "city": "Berlin",
        "region_code": "BE",
        "os": "Linux",
        "ports": [22, 80, 443],
        "vulns": [],
        "tags": [],
        "last_update": "2024-01-15T10:30:00.000000",
        "data": [
            {
                "port": 22,
                "transport": "tcp",
                "product": "OpenSSH",
                "version": "8.2",
                "cpe": ["cpe:/a:openbsd:openssh:8.2"],
                "timestamp": "2024-01-15T10:30:00.000000"
            },
            {
                "port": 80,
                "transport": "tcp",
                "product": "Apache httpd",
                "version": "2.4.41",
                "cpe": ["cpe:/a:apache:http_server:2.4.41"],
                "timestamp": "2024-01-15T10:30:00.000000"
            },
            {
                "port": 443,
                "transport": "tcp",
                "product": "Apache httpd",
                "version": "2.4.41",
                "cpe": ["cpe:/a:apache:http_server:2.4.41"],
                "ssl": {"cert": {"expires": "2025-01-01"}},
                "timestamp": "2024-01-15T10:30:00.000000"
            }
        ]
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_host("192.168.1.1")

        assert result is not None
        assert len(result.services) == 3

        # Check SSH service
        ssh_service = next((s for s in result.services if s.port == 22), None)
        assert ssh_service is not None
        assert isinstance(ssh_service, ServiceInfo)
        assert ssh_service.transport == "tcp"
        assert ssh_service.product == "OpenSSH"
        assert ssh_service.version == "8.2"

        # Check HTTP service
        http_service = next((s for s in result.services if s.port == 80), None)
        assert http_service is not None
        assert http_service.product == "Apache httpd"

    await client.close()


@pytest.mark.asyncio
async def test_shodan_get_host_not_found():
    """
    RED: Test handling of IP not found in Shodan.

    Expected behavior:
    - When IP is not in Shodan database, return None
    """
    client = ShodanClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {
        "error": "No information available for that IP."
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_host("10.0.0.1")

        assert result is None

    await client.close()


# ============================================================================
# SEARCH TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_shodan_search_returns_results():
    """
    RED: Test that ShodanClient.search() returns search results.

    Expected behavior:
    - Execute search query
    - Return list of matching hosts
    """
    client = ShodanClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "matches": [
            {
                "ip_str": "1.2.3.4",
                "port": 80,
                "transport": "tcp",
                "product": "nginx",
                "version": "1.18.0",
                "org": "Example Org",
                "asn": "AS12345",
                "hostnames": ["example.com"],
                "location": {
                    "country_code": "US",
                    "city": "New York"
                },
                "timestamp": "2024-01-15T10:30:00.000000"
            },
            {
                "ip_str": "5.6.7.8",
                "port": 443,
                "transport": "tcp",
                "product": "Apache httpd",
                "version": "2.4.41",
                "org": "Another Org",
                "asn": "AS67890",
                "hostnames": [],
                "location": {
                    "country_code": "DE",
                    "city": "Berlin"
                },
                "timestamp": "2024-01-15T10:30:00.000000"
            }
        ],
        "total": 2
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        results = await client.search("nginx country:US")

        # Verify request
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["params"]["query"] == "nginx country:US"

        # Verify results
        assert results is not None
        assert len(results) == 2
        assert results[0]["ip_str"] == "1.2.3.4"
        assert results[1]["ip_str"] == "5.6.7.8"

    await client.close()


@pytest.mark.asyncio
async def test_shodan_search_with_pagination():
    """
    RED: Test search with pagination (page parameter).

    Expected behavior:
    - Pass page parameter to API
    - Return results for specified page
    """
    client = ShodanClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "matches": [
            {
                "ip_str": "10.20.30.40",
                "port": 22,
                "transport": "tcp",
                "product": "OpenSSH",
                "org": "Page 2 Org",
                "location": {"country_code": "JP"}
            }
        ],
        "total": 150
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        results = await client.search("port:22", page=2)

        # Verify page parameter was passed
        call_args = mock_get.call_args
        assert call_args[1]["params"]["page"] == 2

        assert results is not None
        assert len(results) == 1

    await client.close()


@pytest.mark.asyncio
async def test_shodan_search_no_results():
    """
    RED: Test search with no matching results.

    Expected behavior:
    - Return empty list when no matches
    """
    client = ShodanClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "matches": [],
        "total": 0
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        results = await client.search("nonexistent-very-specific-query-xyz")

        assert results is not None
        assert results == []

    await client.close()


# ============================================================================
# GET SERVICES TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_shodan_get_services_returns_list():
    """
    RED: Test that get_services() returns exposed services for an IP.

    Expected behavior:
    - Fetch services from host data
    - Return List[ServiceInfo]
    """
    client = ShodanClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ip_str": "203.0.113.50",
        "ip": 3405803826,
        "org": "Test Corp",
        "isp": "Test ISP",
        "asn": "AS99999",
        "hostnames": ["server.test.com"],
        "country_code": "AU",
        "country_name": "Australia",
        "city": "Sydney",
        "os": "Ubuntu",
        "ports": [21, 22, 3306, 6379],
        "vulns": [],
        "tags": [],
        "data": [
            {
                "port": 21,
                "transport": "tcp",
                "product": "vsftpd",
                "version": "3.0.3",
                "cpe": []
            },
            {
                "port": 22,
                "transport": "tcp",
                "product": "OpenSSH",
                "version": "8.4",
                "cpe": ["cpe:/a:openbsd:openssh:8.4"]
            },
            {
                "port": 3306,
                "transport": "tcp",
                "product": "MySQL",
                "version": "8.0.27",
                "cpe": ["cpe:/a:mysql:mysql:8.0.27"]
            },
            {
                "port": 6379,
                "transport": "tcp",
                "product": "Redis",
                "version": "6.2.6",
                "cpe": []
            }
        ]
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        services = await client.get_services("203.0.113.50")

        assert services is not None
        assert isinstance(services, list)
        assert len(services) == 4

        # All should be ServiceInfo objects
        for service in services:
            assert isinstance(service, ServiceInfo)

        # Check specific services
        ftp = next((s for s in services if s.port == 21), None)
        assert ftp is not None
        assert ftp.product == "vsftpd"

        mysql = next((s for s in services if s.port == 3306), None)
        assert mysql is not None
        assert mysql.product == "MySQL"
        assert mysql.version == "8.0.27"

        redis = next((s for s in services if s.port == 6379), None)
        assert redis is not None
        assert redis.product == "Redis"

    await client.close()


@pytest.mark.asyncio
async def test_shodan_get_services_empty_for_unknown_ip():
    """
    RED: Test get_services returns empty list for unknown IP.

    Expected behavior:
    - When IP not found, return empty list
    """
    client = ShodanClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {
        "error": "No information available for that IP."
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        services = await client.get_services("10.0.0.1")

        assert services is not None
        assert services == []

    await client.close()


# ============================================================================
# VULNERABILITY TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_shodan_check_vulnerabilities_returns_vulns():
    """
    RED: Test that check_vulnerabilities() returns vulnerability list.

    Expected behavior:
    - Fetch vulnerabilities from host data
    - Return List[VulnerabilityInfo] with CVE IDs
    """
    client = ShodanClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ip_str": "185.199.108.153",
        "ip": 3116822681,
        "org": "GitHub, Inc.",
        "isp": "GitHub",
        "asn": "AS36459",
        "hostnames": ["github.com"],
        "country_code": "US",
        "os": None,
        "ports": [22, 443],
        "vulns": ["CVE-2021-44228", "CVE-2021-45046", "CVE-2022-22965"],
        "tags": [],
        "data": [
            {
                "port": 443,
                "transport": "tcp",
                "product": "Apache httpd",
                "version": "2.4.49",
                "vulns": {
                    "CVE-2021-44228": {
                        "cvss": 10.0,
                        "references": ["https://nvd.nist.gov/vuln/detail/CVE-2021-44228"],
                        "summary": "Log4j RCE vulnerability",
                        "verified": True
                    },
                    "CVE-2021-45046": {
                        "cvss": 9.0,
                        "references": ["https://nvd.nist.gov/vuln/detail/CVE-2021-45046"],
                        "summary": "Log4j DoS vulnerability",
                        "verified": True
                    },
                    "CVE-2022-22965": {
                        "cvss": 9.8,
                        "references": ["https://nvd.nist.gov/vuln/detail/CVE-2022-22965"],
                        "summary": "Spring4Shell RCE",
                        "verified": False
                    }
                }
            }
        ]
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        vulns = await client.check_vulnerabilities("185.199.108.153")

        assert vulns is not None
        assert isinstance(vulns, list)
        assert len(vulns) == 3

        # Check vulnerability info
        log4j = next((v for v in vulns if v.cve_id == "CVE-2021-44228"), None)
        assert log4j is not None
        assert isinstance(log4j, VulnerabilityInfo)
        assert log4j.cvss == 10.0
        assert log4j.verified is True
        assert "Log4j" in log4j.summary

        spring = next((v for v in vulns if v.cve_id == "CVE-2022-22965"), None)
        assert spring is not None
        assert spring.cvss == 9.8
        assert spring.verified is False

    await client.close()


@pytest.mark.asyncio
async def test_shodan_check_vulnerabilities_no_vulns():
    """
    RED: Test check_vulnerabilities for host with no vulns.

    Expected behavior:
    - Return empty list when no vulnerabilities
    """
    client = ShodanClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ip_str": "8.8.8.8",
        "ip": 134744072,
        "org": "Google LLC",
        "ports": [53, 443],
        "vulns": [],
        "data": [
            {
                "port": 53,
                "transport": "udp",
                "product": "Google DNS",
                "vulns": {}
            }
        ]
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        vulns = await client.check_vulnerabilities("8.8.8.8")

        assert vulns is not None
        assert vulns == []

    await client.close()


@pytest.mark.asyncio
async def test_shodan_check_vulnerabilities_unknown_ip():
    """
    RED: Test check_vulnerabilities for unknown IP.

    Expected behavior:
    - Return empty list when IP not found
    """
    client = ShodanClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {
        "error": "No information available for that IP."
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        vulns = await client.check_vulnerabilities("192.168.1.1")

        assert vulns is not None
        assert vulns == []

    await client.close()


# ============================================================================
# RATE LIMIT TESTS (100/month)
# ============================================================================


@pytest.mark.asyncio
async def test_shodan_rate_limit_handling():
    """
    RED: Test that client handles 429 rate limit response.

    Expected behavior:
    - When API returns 429, return None
    - Log warning about rate limit
    """
    client = ShodanClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.json.return_value = {
        "error": "Rate limit exceeded"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_host("8.8.8.8")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_shodan_rate_limit_tracking():
    """
    RED: Test that client tracks rate limit usage.

    Expected behavior:
    - Client tracks remaining requests
    - Provides method to check remaining quota
    """
    client = ShodanClient(api_key="test-api-key")

    # Initial state
    assert client.get_remaining_requests() is None  # Unknown until first request

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {
        "X-Rate-Limit-Remaining": "95",
        "X-Rate-Limit-Limit": "100"
    }
    mock_response.json.return_value = {
        "ip_str": "8.8.8.8",
        "org": "Google LLC",
        "ports": [53],
        "data": []
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        await client.get_host("8.8.8.8")

        # After request, should have remaining count
        assert client.get_remaining_requests() == 95

    await client.close()


@pytest.mark.asyncio
async def test_shodan_search_rate_limit():
    """
    RED: Test that search also handles rate limits.

    Expected behavior:
    - Search returns empty list on rate limit
    """
    client = ShodanClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.json.return_value = {
        "error": "Rate limit exceeded"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        results = await client.search("nginx")

        assert results == []

    await client.close()


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_shodan_handles_auth_error():
    """
    RED: Test handling of authentication errors (401).

    Expected behavior:
    - When API returns 401, return None
    - Log error about invalid API key
    """
    client = ShodanClient(api_key="invalid-key")

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {
        "error": "Invalid API key"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_host("8.8.8.8")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_shodan_handles_server_error():
    """
    RED: Test handling of server errors (500).

    Expected behavior:
    - When API returns 500, return None
    - Log error
    """
    client = ShodanClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {
        "error": "Internal server error"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_host("8.8.8.8")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_shodan_handles_timeout():
    """
    RED: Test timeout handling.

    Expected behavior:
    - When request times out, return None
    - No exceptions should propagate
    """
    client = ShodanClient(api_key="test-api-key", timeout=5)

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Request timed out")

        result = await client.get_host("8.8.8.8")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_shodan_handles_request_error():
    """
    RED: Test handling of network/request errors.

    Expected behavior:
    - When network error occurs, return None
    - No exceptions should propagate
    """
    client = ShodanClient(api_key="test-api-key")

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await client.get_host("8.8.8.8")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_shodan_handles_malformed_response():
    """
    RED: Test handling of malformed API response.

    Expected behavior:
    - When response JSON is invalid or missing expected fields
    - Client should return None without crashing
    """
    client = ShodanClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    # Malformed response missing expected fields
    mock_response.json.return_value = {
        "unexpected": "data"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_host("8.8.8.8")

        # Should handle gracefully
        assert result is None

    await client.close()


# ============================================================================
# CLIENT CONFIGURATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_shodan_client_close():
    """
    RED: Test that client can be properly closed.
    """
    client = ShodanClient(api_key="test-api-key")

    # Should not raise any exceptions
    await client.close()


@pytest.mark.asyncio
async def test_shodan_custom_timeout():
    """
    RED: Test that custom timeout is applied.
    """
    client = ShodanClient(api_key="test-api-key", timeout=15)

    assert client.timeout == 15

    await client.close()


@pytest.mark.asyncio
async def test_shodan_uses_correct_base_url():
    """
    RED: Test that client uses correct Shodan API base URL.
    """
    client = ShodanClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ip_str": "8.8.8.8",
        "org": "Google",
        "ports": [],
        "data": []
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        await client.get_host("8.8.8.8")

        # Verify correct URL was called
        call_args = mock_get.call_args
        assert "api.shodan.io" in call_args[0][0]
        assert "/shodan/host/" in call_args[0][0]

    await client.close()


@pytest.mark.asyncio
async def test_shodan_api_key_in_params():
    """
    RED: Test that API key is included in request params.
    """
    client = ShodanClient(api_key="my-secret-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ip_str": "8.8.8.8",
        "org": "Google",
        "ports": [],
        "data": []
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        await client.get_host("8.8.8.8")

        # Verify API key was in params
        call_args = mock_get.call_args
        assert call_args[1]["params"]["key"] == "my-secret-api-key"

    await client.close()


# ============================================================================
# DATA MODEL TESTS
# ============================================================================


def test_service_info_dataclass():
    """
    RED: Test ServiceInfo dataclass structure.
    """
    service = ServiceInfo(
        port=443,
        transport="tcp",
        product="nginx",
        version="1.18.0",
        cpe=["cpe:/a:nginx:nginx:1.18.0"]
    )

    assert service.port == 443
    assert service.transport == "tcp"
    assert service.product == "nginx"
    assert service.version == "1.18.0"
    assert len(service.cpe) == 1


def test_host_info_dataclass():
    """
    RED: Test HostInfo dataclass structure.
    """
    service = ServiceInfo(port=80, transport="tcp", product="nginx", version="1.18.0")
    host = HostInfo(
        ip="8.8.8.8",
        org="Google LLC",
        isp="Google LLC",
        asn="AS15169",
        hostnames=["dns.google"],
        country_code="US",
        city="Mountain View",
        os=None,
        ports=[53, 443],
        services=[service],
        tags=["cloud"],
        last_update="2024-01-15T10:30:00.000000"
    )

    assert host.ip == "8.8.8.8"
    assert host.org == "Google LLC"
    assert host.asn == "AS15169"
    assert host.country_code == "US"
    assert len(host.ports) == 2
    assert len(host.services) == 1
    assert host.os is None


def test_vulnerability_info_dataclass():
    """
    RED: Test VulnerabilityInfo dataclass structure.
    """
    vuln = VulnerabilityInfo(
        cve_id="CVE-2021-44228",
        cvss=10.0,
        summary="Log4j RCE vulnerability",
        references=["https://nvd.nist.gov/vuln/detail/CVE-2021-44228"],
        verified=True
    )

    assert vuln.cve_id == "CVE-2021-44228"
    assert vuln.cvss == 10.0
    assert "Log4j" in vuln.summary
    assert vuln.verified is True
    assert len(vuln.references) == 1


# ============================================================================
# INTEGRATION-STYLE TESTS (with mocked HTTP)
# ============================================================================


@pytest.mark.asyncio
async def test_shodan_full_workflow():
    """
    RED: Test full workflow: get host -> get services -> check vulns.

    This simulates a complete enrichment workflow.
    """
    client = ShodanClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ip_str": "185.199.108.153",
        "ip": 3116822681,
        "org": "GitHub, Inc.",
        "isp": "GitHub",
        "asn": "AS36459",
        "hostnames": ["github.com"],
        "country_code": "US",
        "country_name": "United States",
        "city": "San Francisco",
        "os": "Linux",
        "ports": [22, 443],
        "vulns": ["CVE-2021-44228"],
        "tags": ["cdn"],
        "data": [
            {
                "port": 22,
                "transport": "tcp",
                "product": "OpenSSH",
                "version": "8.2",
                "cpe": ["cpe:/a:openbsd:openssh:8.2"],
                "vulns": {}
            },
            {
                "port": 443,
                "transport": "tcp",
                "product": "nginx",
                "version": "1.18.0",
                "cpe": ["cpe:/a:nginx:nginx:1.18.0"],
                "ssl": {"cert": {"expires": "2025-01-01"}},
                "vulns": {
                    "CVE-2021-44228": {
                        "cvss": 10.0,
                        "references": ["https://nvd.nist.gov/vuln/detail/CVE-2021-44228"],
                        "summary": "Log4j RCE",
                        "verified": True
                    }
                }
            }
        ],
        "last_update": "2024-01-15T10:30:00.000000"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        # Step 1: Get host info
        host = await client.get_host("185.199.108.153")
        assert host is not None
        assert host.ip == "185.199.108.153"
        assert host.org == "GitHub, Inc."

        # Step 2: Get services (reusing same mock)
        services = await client.get_services("185.199.108.153")
        assert len(services) == 2
        assert any(s.port == 22 and s.product == "OpenSSH" for s in services)
        assert any(s.port == 443 and s.product == "nginx" for s in services)

        # Step 3: Check vulnerabilities
        vulns = await client.check_vulnerabilities("185.199.108.153")
        assert len(vulns) >= 1
        assert any(v.cve_id == "CVE-2021-44228" for v in vulns)

    await client.close()


@pytest.mark.asyncio
async def test_shodan_context_manager():
    """
    RED: Test using client as async context manager.
    """
    async with ShodanClient(api_key="test-api-key") as client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ip_str": "8.8.8.8",
            "org": "Google",
            "ports": [53],
            "data": []
        }

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            result = await client.get_host("8.8.8.8")
            assert result is not None
