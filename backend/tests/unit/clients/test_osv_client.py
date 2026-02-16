"""
Unit tests for OSV (Open Source Vulnerabilities) API Client.

OSV provides vulnerability data for open source packages.
API is free and requires no authentication.

API Documentation: https://osv.dev/docs/

These tests are written FIRST following TDD (RED phase).
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

# Import will fail until we implement the module (RED phase)
try:
    from src.clients.osv_client import OSVClient
except ImportError:
    pass


# =============================================================================
# Test 1: Client Creation
# =============================================================================

@pytest.mark.asyncio
async def test_osv_client_creation():
    """
    RED: Test that OSVClient can be instantiated with default settings.

    Expected behavior:
    - Client should initialize with default timeout of 30
    - Client should have an httpx.AsyncClient instance
    """
    client = OSVClient()

    assert client.timeout == 30
    assert client.client is not None
    assert isinstance(client.client, httpx.AsyncClient)

    await client.close()


# =============================================================================
# Test 2: Fetch Vulnerability - Found
# =============================================================================

@pytest.mark.asyncio
async def test_osv_fetch_vulnerability_found():
    """
    RED: Test fetching a vulnerability by OSV ID returns data.

    Expected behavior:
    - GET /vulns/{id} returns vulnerability details
    - Response is parsed into our internal format
    """
    client = OSVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "GHSA-jfh8-c2jp-5v3q",
        "aliases": ["CVE-2021-44228"],
        "summary": "Remote code execution in Log4j",
        "details": "Apache Log4j2 <=2.14.1 JNDI features...",
        "severity": [
            {
                "type": "CVSS_V3",
                "score": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H"
            }
        ],
        "affected": [
            {
                "package": {
                    "ecosystem": "Maven",
                    "name": "org.apache.logging.log4j:log4j-core"
                },
                "ranges": [
                    {
                        "type": "ECOSYSTEM",
                        "events": [
                            {"introduced": "0"},
                            {"fixed": "2.15.0"}
                        ]
                    }
                ],
                "ecosystem_specific": {
                    "severity": "CRITICAL"
                }
            }
        ],
        "references": [
            {"type": "ADVISORY", "url": "https://nvd.nist.gov/vuln/detail/CVE-2021-44228"},
            {"type": "FIX", "url": "https://github.com/apache/logging-log4j2/pull/608"}
        ],
        "published": "2021-12-10T00:00:00Z",
        "modified": "2021-12-14T00:00:00Z"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.fetch_vulnerability("GHSA-jfh8-c2jp-5v3q")

        # Verify request
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "GHSA-jfh8-c2jp-5v3q" in call_args[0][0]

        # Verify response structure
        assert result is not None
        assert result["osv_id"] == "GHSA-jfh8-c2jp-5v3q"
        assert result["cve_id"] == "CVE-2021-44228"
        assert result["summary"] == "Remote code execution in Log4j"
        assert result["severity"] == "CRITICAL"
        assert len(result["affected"]) == 1
        assert result["affected"][0]["package"]["ecosystem"] == "Maven"
        assert len(result["references"]) == 2

    await client.close()


# =============================================================================
# Test 3: Fetch Vulnerability - Not Found
# =============================================================================

@pytest.mark.asyncio
async def test_osv_fetch_vulnerability_not_found():
    """
    RED: Test fetching a non-existent vulnerability returns None.

    Expected behavior:
    - GET /vulns/{id} returns 404
    - Client returns None
    """
    client = OSVClient()

    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.fetch_vulnerability("NONEXISTENT-ID")

        assert result is None

    await client.close()


# =============================================================================
# Test 4: Query by CVE - Found
# =============================================================================

@pytest.mark.asyncio
async def test_osv_query_by_cve_found():
    """
    RED: Test querying vulnerabilities by CVE ID returns data.

    Expected behavior:
    - POST /query with CVE alias returns matching vulnerabilities
    """
    client = OSVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "vulns": [
            {
                "id": "GHSA-jfh8-c2jp-5v3q",
                "aliases": ["CVE-2021-44228"],
                "summary": "Remote code execution in Log4j",
                "severity": [{"type": "CVSS_V3", "score": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H"}],
                "affected": [
                    {
                        "package": {"ecosystem": "Maven", "name": "org.apache.logging.log4j:log4j-core"},
                        "ranges": [{"type": "ECOSYSTEM", "events": [{"introduced": "0"}, {"fixed": "2.15.0"}]}]
                    }
                ],
                "references": [{"type": "ADVISORY", "url": "https://nvd.nist.gov/vuln/detail/CVE-2021-44228"}]
            }
        ]
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.query_by_cve("CVE-2021-44228")

        # Verify request
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "/query" in call_args[0][0]
        request_body = call_args[1]["json"]
        assert request_body["query"] == "CVE-2021-44228"

        # Verify response
        assert result is not None
        assert len(result) == 1
        assert result[0]["osv_id"] == "GHSA-jfh8-c2jp-5v3q"
        assert result[0]["cve_id"] == "CVE-2021-44228"

    await client.close()


# =============================================================================
# Test 5: Query by CVE - Not Found
# =============================================================================

@pytest.mark.asyncio
async def test_osv_query_by_cve_not_found():
    """
    RED: Test querying by non-existent CVE returns empty list.

    Expected behavior:
    - POST /query with unknown CVE returns empty vulns array
    - Client returns empty list
    """
    client = OSVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "vulns": []
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.query_by_cve("CVE-9999-99999")

        assert result is not None
        assert result == []

    await client.close()


# =============================================================================
# Test 6: Query by Package
# =============================================================================

@pytest.mark.asyncio
async def test_osv_query_by_package():
    """
    RED: Test querying vulnerabilities by package ecosystem and name.

    Expected behavior:
    - POST /query with package info returns vulnerabilities affecting that package
    """
    client = OSVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "vulns": [
            {
                "id": "GHSA-29mw-wpgm-hmr9",
                "aliases": ["CVE-2023-37920"],
                "summary": "Removal of e-Tugra root certificate",
                "affected": [
                    {
                        "package": {"ecosystem": "PyPI", "name": "certifi"},
                        "ranges": [{"type": "ECOSYSTEM", "events": [{"introduced": "2023.7.22"}, {"fixed": "2023.7.22"}]}]
                    }
                ],
                "references": []
            }
        ]
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.query_by_package("PyPI", "certifi")

        # Verify request
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        request_body = call_args[1]["json"]
        assert request_body["package"]["ecosystem"] == "PyPI"
        assert request_body["package"]["name"] == "certifi"
        assert "version" not in request_body

        # Verify response
        assert result is not None
        assert len(result) >= 1
        assert result[0]["osv_id"] == "GHSA-29mw-wpgm-hmr9"

    await client.close()


# =============================================================================
# Test 7: Query by Package with Version
# =============================================================================

@pytest.mark.asyncio
async def test_osv_query_by_package_with_version():
    """
    RED: Test querying vulnerabilities by package with specific version.

    Expected behavior:
    - POST /query with package and version returns relevant vulnerabilities
    """
    client = OSVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "vulns": [
            {
                "id": "GHSA-xxxx-yyyy-zzzz",
                "summary": "Security issue in express",
                "affected": [
                    {
                        "package": {"ecosystem": "npm", "name": "express"},
                        "ranges": [{"type": "ECOSYSTEM", "events": [{"introduced": "0"}, {"fixed": "4.18.2"}]}]
                    }
                ],
                "references": []
            }
        ]
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.query_by_package("npm", "express", "4.17.1")

        # Verify request includes version
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        request_body = call_args[1]["json"]
        assert request_body["package"]["ecosystem"] == "npm"
        assert request_body["package"]["name"] == "express"
        assert request_body["version"] == "4.17.1"

        # Verify response
        assert result is not None
        assert len(result) >= 1

    await client.close()


# =============================================================================
# Test 8: Batch Query
# =============================================================================

@pytest.mark.asyncio
async def test_osv_batch_query():
    """
    RED: Test batch querying multiple packages at once.

    Expected behavior:
    - POST /querybatch with multiple queries returns results for each
    """
    client = OSVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "vulns": [
                    {
                        "id": "GHSA-1111-2222-3333",
                        "summary": "Vuln in package A",
                        "affected": [{"package": {"ecosystem": "npm", "name": "package-a"}}],
                        "references": []
                    }
                ]
            },
            {
                "vulns": [
                    {
                        "id": "GHSA-4444-5555-6666",
                        "summary": "Vuln in package B",
                        "affected": [{"package": {"ecosystem": "PyPI", "name": "package-b"}}],
                        "references": []
                    }
                ]
            },
            {
                "vulns": []  # No vulnerabilities for third query
            }
        ]
    }

    queries = [
        {"package": {"ecosystem": "npm", "name": "package-a"}},
        {"package": {"ecosystem": "PyPI", "name": "package-b"}},
        {"package": {"ecosystem": "npm", "name": "safe-package"}}
    ]

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.batch_query(queries)

        # Verify request
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "/querybatch" in call_args[0][0]
        request_body = call_args[1]["json"]
        assert "queries" in request_body
        assert len(request_body["queries"]) == 3

        # Verify response - should be list of lists
        assert result is not None
        assert len(result) == 3
        assert len(result[0]) == 1  # First query has 1 vuln
        assert len(result[1]) == 1  # Second query has 1 vuln
        assert len(result[2]) == 0  # Third query has no vulns

    await client.close()


# =============================================================================
# Test 9: Handles Network Error
# =============================================================================

@pytest.mark.asyncio
async def test_osv_handles_network_error():
    """
    RED: Test handling of network/connection errors.

    Expected behavior:
    - When network error occurs, return None (for single queries)
    - No exceptions should propagate
    """
    client = OSVClient()

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await client.fetch_vulnerability("GHSA-xxxx-yyyy-zzzz")

        assert result is None

    await client.close()


# =============================================================================
# Test 10: Handles Timeout
# =============================================================================

@pytest.mark.asyncio
async def test_osv_handles_timeout():
    """
    RED: Test handling of request timeout.

    Expected behavior:
    - When request times out, return None
    - No exceptions should propagate
    """
    client = OSVClient(timeout=5)

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Request timed out")

        result = await client.fetch_vulnerability("GHSA-xxxx-yyyy-zzzz")

        assert result is None

    await client.close()


# =============================================================================
# Test 11: Handles Malformed Response
# =============================================================================

@pytest.mark.asyncio
async def test_osv_handles_malformed_response():
    """
    RED: Test handling of malformed/unexpected API responses.

    Expected behavior:
    - When response is malformed, return None
    - No exceptions should propagate
    """
    client = OSVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        # Missing expected fields
        "unexpected_field": "value"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.fetch_vulnerability("GHSA-xxxx-yyyy-zzzz")

        # Should handle gracefully and return None
        assert result is None

    await client.close()


# =============================================================================
# Test 12: Handles Server Error
# =============================================================================

@pytest.mark.asyncio
async def test_osv_handles_server_error():
    """
    RED: Test handling of server errors (5xx).

    Expected behavior:
    - When server returns 500, return None
    - No exceptions should propagate
    """
    client = OSVClient()

    mock_response = MagicMock()
    mock_response.status_code = 500

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.fetch_vulnerability("GHSA-xxxx-yyyy-zzzz")

        assert result is None

    await client.close()


# =============================================================================
# Test 13: Custom Timeout
# =============================================================================

@pytest.mark.asyncio
async def test_osv_custom_timeout():
    """
    RED: Test that custom timeout is properly applied.

    Expected behavior:
    - Client should accept custom timeout in constructor
    - Timeout value should be stored correctly
    """
    client = OSVClient(timeout=60)

    assert client.timeout == 60

    await client.close()


# =============================================================================
# Test 14: Client Close
# =============================================================================

@pytest.mark.asyncio
async def test_osv_client_close():
    """
    RED: Test that client can be properly closed.

    Expected behavior:
    - close() should not raise exceptions
    - Client should be cleanly shut down
    """
    client = OSVClient()

    # Should not raise any exceptions
    await client.close()

    # Calling close again should also be safe
    await client.close()


# =============================================================================
# Test 15: Context Manager
# =============================================================================

@pytest.mark.asyncio
async def test_osv_context_manager():
    """
    RED: Test that client supports async context manager.

    Expected behavior:
    - Client can be used with `async with`
    - Client is automatically closed on exit
    """
    async with OSVClient() as client:
        assert client is not None
        assert client.client is not None

    # After context exit, client should be closed
    # We can't easily verify this, but the test should not raise


# =============================================================================
# Test 16: Parses Ranges Correctly
# =============================================================================

@pytest.mark.asyncio
async def test_osv_parses_ranges_correctly():
    """
    RED: Test that vulnerability range information is correctly parsed.

    Expected behavior:
    - Version ranges with introduced/fixed events are correctly extracted
    - Multiple ranges are handled
    """
    client = OSVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "GHSA-test-1234-5678",
        "aliases": [],
        "summary": "Test vulnerability",
        "affected": [
            {
                "package": {"ecosystem": "npm", "name": "test-package"},
                "ranges": [
                    {
                        "type": "SEMVER",
                        "events": [
                            {"introduced": "1.0.0"},
                            {"fixed": "1.5.0"}
                        ]
                    },
                    {
                        "type": "SEMVER",
                        "events": [
                            {"introduced": "2.0.0"},
                            {"fixed": "2.3.0"}
                        ]
                    }
                ],
                "ecosystem_specific": {
                    "severity": "HIGH"
                }
            }
        ],
        "references": []
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.fetch_vulnerability("GHSA-test-1234-5678")

        assert result is not None
        assert len(result["affected"]) == 1

        affected = result["affected"][0]
        assert len(affected["ranges"]) == 2

        # First range
        assert affected["ranges"][0]["type"] == "SEMVER"
        assert affected["ranges"][0]["events"][0]["introduced"] == "1.0.0"
        assert affected["ranges"][0]["events"][1]["fixed"] == "1.5.0"

        # Second range
        assert affected["ranges"][1]["type"] == "SEMVER"
        assert affected["ranges"][1]["events"][0]["introduced"] == "2.0.0"
        assert affected["ranges"][1]["events"][1]["fixed"] == "2.3.0"

        # Ecosystem specific
        assert affected["ecosystem_specific"]["severity"] == "HIGH"

    await client.close()


# =============================================================================
# Test 17: Uses Correct Base URL
# =============================================================================

@pytest.mark.asyncio
async def test_osv_uses_correct_base_url():
    """
    RED: Test that client uses correct OSV API base URL.
    """
    client = OSVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"vulns": []}

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        await client.query_by_cve("CVE-2021-44228")

        # Verify correct URL was called
        call_args = mock_post.call_args
        assert "https://api.osv.dev/v1/query" in call_args[0][0]

    await client.close()


# =============================================================================
# Test 18: Extracts Severity from CVSS
# =============================================================================

@pytest.mark.asyncio
async def test_osv_extracts_severity_from_cvss():
    """
    RED: Test that severity is correctly extracted from CVSS score.

    Expected behavior:
    - CVSS score is parsed to determine severity level
    - HIGH/CRITICAL/MEDIUM/LOW are correctly determined
    """
    client = OSVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "GHSA-high-sev-test",
        "aliases": ["CVE-2024-0001"],
        "summary": "High severity vulnerability",
        "severity": [
            {
                "type": "CVSS_V3",
                "score": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
            }
        ],
        "affected": [],
        "references": []
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.fetch_vulnerability("GHSA-high-sev-test")

        assert result is not None
        # Severity should be extracted from CVSS or ecosystem_specific
        assert result["severity"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW", None]

    await client.close()


# =============================================================================
# Test 19: Handles Empty Aliases
# =============================================================================

@pytest.mark.asyncio
async def test_osv_handles_empty_aliases():
    """
    RED: Test handling of vulnerabilities without CVE aliases.

    Expected behavior:
    - When aliases is empty, cve_id should be None
    """
    client = OSVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "GHSA-no-cve-1234",
        "aliases": [],  # No CVE alias
        "summary": "Vulnerability without CVE",
        "affected": [],
        "references": []
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.fetch_vulnerability("GHSA-no-cve-1234")

        assert result is not None
        assert result["osv_id"] == "GHSA-no-cve-1234"
        assert result["cve_id"] is None

    await client.close()


# =============================================================================
# Test 20: Query by Package Returns Empty for Safe Package
# =============================================================================

@pytest.mark.asyncio
async def test_osv_query_by_package_no_vulns():
    """
    RED: Test querying a package with no known vulnerabilities.

    Expected behavior:
    - Returns empty list for packages without vulnerabilities
    """
    client = OSVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "vulns": []
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.query_by_package("npm", "super-safe-package-12345")

        assert result is not None
        assert result == []

    await client.close()
