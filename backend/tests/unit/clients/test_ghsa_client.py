"""
Unit tests for GitHub Security Advisories (GHSA) API Client.

GHSA provides vulnerability advisories via GitHub's GraphQL API.

API Documentation: https://docs.github.com/en/graphql/reference/objects#securityadvisory
Rate limit: 5000 points/hour (GraphQL)

These tests are written FIRST following TDD (RED phase).
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

# Import will fail until we implement the module (RED phase)
try:
    from src.clients.ghsa_client import GHSAClient
except ImportError:
    pass


# =============================================================================
# Client Initialization Tests
# =============================================================================

@pytest.mark.asyncio
async def test_ghsa_client_creation():
    """
    RED: Test that GHSAClient can be created with optional token.

    Expected behavior:
    - Client can be created with or without a GitHub token
    - Default timeout is 30 seconds
    """
    # With token
    client_with_token = GHSAClient(token="test-github-token")
    assert client_with_token.token == "test-github-token"
    assert client_with_token.timeout == 30
    await client_with_token.close()

    # Without token (uses synthetic data)
    client_without_token = GHSAClient()
    assert client_without_token.token is None
    await client_without_token.close()


@pytest.mark.asyncio
async def test_ghsa_custom_timeout():
    """
    RED: Test that custom timeout is applied.
    """
    client = GHSAClient(token="test-token", timeout=60)

    assert client.timeout == 60

    await client.close()


@pytest.mark.asyncio
async def test_ghsa_client_close():
    """
    RED: Test that client can be properly closed.
    """
    client = GHSAClient(token="test-token")

    # Should not raise any exceptions
    await client.close()


@pytest.mark.asyncio
async def test_ghsa_context_manager():
    """
    RED: Test that client works as an async context manager.

    Expected behavior:
    - Can be used with 'async with' syntax
    - Properly closes on exit
    """
    async with GHSAClient(token="test-token") as client:
        assert client is not None
        assert client.token == "test-token"

    # Client should be closed after exiting context


# =============================================================================
# Fetch Advisory Tests
# =============================================================================

@pytest.mark.asyncio
async def test_ghsa_fetch_advisory_found():
    """
    RED: Test fetching an advisory that exists.

    Expected behavior:
    - Query GHSA GraphQL API for specific advisory
    - Return formatted dict with advisory data
    """
    client = GHSAClient(token="test-token")

    # Mock successful GraphQL response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "securityAdvisory": {
                "ghsaId": "GHSA-jfhm-5ghh-2f97",
                "summary": "ReDoS vulnerability in lodash",
                "severity": "HIGH",
                "publishedAt": "2024-01-15T00:00:00Z",
                "identifiers": [
                    {"type": "GHSA", "value": "GHSA-jfhm-5ghh-2f97"},
                    {"type": "CVE", "value": "CVE-2020-8203"}
                ],
                "vulnerabilities": {
                    "nodes": [
                        {
                            "package": {
                                "ecosystem": "NPM",
                                "name": "lodash"
                            },
                            "vulnerableVersionRange": "< 4.17.20",
                            "firstPatchedVersion": {
                                "identifier": "4.17.20"
                            }
                        }
                    ]
                }
            }
        }
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.fetch_advisory("GHSA-jfhm-5ghh-2f97")

        # Verify request was made
        mock_post.assert_called_once()

        # Verify response structure
        assert result is not None
        assert result["ghsa_id"] == "GHSA-jfhm-5ghh-2f97"
        assert result["summary"] == "ReDoS vulnerability in lodash"
        assert result["severity"] == "HIGH"
        assert result["published_at"] == "2024-01-15T00:00:00Z"
        assert result["cve_id"] == "CVE-2020-8203"
        assert len(result["affected_packages"]) == 1
        assert result["affected_packages"][0]["ecosystem"] == "npm"
        assert result["affected_packages"][0]["package_name"] == "lodash"
        assert result["affected_packages"][0]["vulnerable_versions"] == "< 4.17.20"
        assert result["affected_packages"][0]["patched_version"] == "4.17.20"

    await client.close()


@pytest.mark.asyncio
async def test_ghsa_fetch_advisory_not_found():
    """
    RED: Test fetching an advisory that doesn't exist.

    Expected behavior:
    - Return None for non-existent advisory
    """
    client = GHSAClient(token="test-token")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "securityAdvisory": None
        }
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.fetch_advisory("GHSA-xxxx-yyyy-zzzz")

        assert result is None

    await client.close()


# =============================================================================
# Search by CVE Tests
# =============================================================================

@pytest.mark.asyncio
async def test_ghsa_search_by_cve_found():
    """
    RED: Test searching advisories by CVE ID.

    Expected behavior:
    - Query GHSA for advisories matching the CVE
    - Return list of matching advisories
    """
    client = GHSAClient(token="test-token")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "securityAdvisories": {
                "nodes": [
                    {
                        "ghsaId": "GHSA-jfhm-5ghh-2f97",
                        "summary": "ReDoS vulnerability in lodash",
                        "severity": "HIGH",
                        "publishedAt": "2024-01-15T00:00:00Z",
                        "identifiers": [
                            {"type": "GHSA", "value": "GHSA-jfhm-5ghh-2f97"},
                            {"type": "CVE", "value": "CVE-2020-8203"}
                        ],
                        "vulnerabilities": {
                            "nodes": [
                                {
                                    "package": {
                                        "ecosystem": "NPM",
                                        "name": "lodash"
                                    },
                                    "vulnerableVersionRange": "< 4.17.20",
                                    "firstPatchedVersion": {
                                        "identifier": "4.17.20"
                                    }
                                }
                            ]
                        }
                    }
                ],
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": None
                }
            }
        }
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.search_by_cve("CVE-2020-8203")

        # Verify request was made with CVE filter
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        request_body = call_args[1]["json"]
        assert "CVE-2020-8203" in str(request_body)

        # Verify response
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["ghsa_id"] == "GHSA-jfhm-5ghh-2f97"
        assert result[0]["cve_id"] == "CVE-2020-8203"

    await client.close()


@pytest.mark.asyncio
async def test_ghsa_search_by_cve_not_found():
    """
    RED: Test searching for CVE with no matching advisories.

    Expected behavior:
    - Return empty list
    """
    client = GHSAClient(token="test-token")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "securityAdvisories": {
                "nodes": [],
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": None
                }
            }
        }
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.search_by_cve("CVE-9999-99999")

        assert isinstance(result, list)
        assert len(result) == 0

    await client.close()


# =============================================================================
# Search by Package Tests
# =============================================================================

@pytest.mark.asyncio
async def test_ghsa_search_by_package():
    """
    RED: Test searching advisories by ecosystem and package name.

    Expected behavior:
    - Query GHSA for advisories affecting the specified package
    - Return list of matching advisories
    """
    client = GHSAClient(token="test-token")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "securityVulnerabilities": {
                "nodes": [
                    {
                        "advisory": {
                            "ghsaId": "GHSA-jfhm-5ghh-2f97",
                            "summary": "ReDoS vulnerability in lodash",
                            "severity": "HIGH",
                            "publishedAt": "2024-01-15T00:00:00Z",
                            "identifiers": [
                                {"type": "GHSA", "value": "GHSA-jfhm-5ghh-2f97"},
                                {"type": "CVE", "value": "CVE-2020-8203"}
                            ]
                        },
                        "package": {
                            "ecosystem": "NPM",
                            "name": "lodash"
                        },
                        "vulnerableVersionRange": "< 4.17.20",
                        "firstPatchedVersion": {
                            "identifier": "4.17.20"
                        }
                    },
                    {
                        "advisory": {
                            "ghsaId": "GHSA-35jh-r3h4-6jhm",
                            "summary": "Prototype Pollution in lodash",
                            "severity": "CRITICAL",
                            "publishedAt": "2024-02-01T00:00:00Z",
                            "identifiers": [
                                {"type": "GHSA", "value": "GHSA-35jh-r3h4-6jhm"},
                                {"type": "CVE", "value": "CVE-2019-10744"}
                            ]
                        },
                        "package": {
                            "ecosystem": "NPM",
                            "name": "lodash"
                        },
                        "vulnerableVersionRange": "< 4.17.12",
                        "firstPatchedVersion": {
                            "identifier": "4.17.12"
                        }
                    }
                ],
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": None
                }
            }
        }
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.search_by_package("npm", "lodash")

        # Verify request was made with package filter
        mock_post.assert_called_once()

        # Verify response
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["ghsa_id"] == "GHSA-jfhm-5ghh-2f97"
        assert result[0]["affected_packages"][0]["package_name"] == "lodash"
        assert result[1]["ghsa_id"] == "GHSA-35jh-r3h4-6jhm"
        assert result[1]["severity"] == "CRITICAL"

    await client.close()


# =============================================================================
# Error Handling Tests
# =============================================================================

@pytest.mark.asyncio
async def test_ghsa_handles_auth_error():
    """
    RED: Test handling of authentication errors (401).

    Expected behavior:
    - Return None/empty list and log error
    """
    client = GHSAClient(token="invalid-token")

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {
        "message": "Bad credentials"
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.fetch_advisory("GHSA-xxxx-yyyy-zzzz")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_ghsa_handles_network_error():
    """
    RED: Test handling of network/connection errors.

    Expected behavior:
    - Return None and log error
    - No exceptions should propagate
    """
    client = GHSAClient(token="test-token")

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.ConnectError("Connection failed")

        result = await client.fetch_advisory("GHSA-jfhm-5ghh-2f97")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_ghsa_handles_timeout():
    """
    RED: Test timeout handling.

    Expected behavior:
    - Return None on timeout
    - No exceptions should propagate
    """
    client = GHSAClient(token="test-token", timeout=5)

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.TimeoutException("Request timed out")

        result = await client.search_by_cve("CVE-2020-8203")

        assert result == []

    await client.close()


@pytest.mark.asyncio
async def test_ghsa_handles_rate_limit():
    """
    RED: Test handling of rate limit (403 with rate limit message).

    GitHub GraphQL rate limit is 5000 points/hour.

    Expected behavior:
    - Return None/empty and log warning
    """
    client = GHSAClient(token="test-token")

    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.json.return_value = {
        "message": "API rate limit exceeded"
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.fetch_advisory("GHSA-jfhm-5ghh-2f97")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_ghsa_handles_malformed_response():
    """
    RED: Test handling of malformed/unexpected API response.

    Expected behavior:
    - Handle gracefully without crashing
    - Return None
    """
    client = GHSAClient(token="test-token")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "unexpected": "data",
        "no_data_key": True
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.fetch_advisory("GHSA-jfhm-5ghh-2f97")

        assert result is None

    await client.close()


# =============================================================================
# Data Parsing Tests
# =============================================================================

@pytest.mark.asyncio
async def test_ghsa_parses_affected_packages_correctly():
    """
    RED: Test correct parsing of affected packages from vulnerabilities.

    Expected behavior:
    - Extract ecosystem, package name, versions correctly
    - Handle missing firstPatchedVersion
    """
    client = GHSAClient(token="test-token")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "securityAdvisory": {
                "ghsaId": "GHSA-test-1234-5678",
                "summary": "Test vulnerability",
                "severity": "MODERATE",
                "publishedAt": "2024-03-01T00:00:00Z",
                "identifiers": [
                    {"type": "GHSA", "value": "GHSA-test-1234-5678"}
                ],
                "vulnerabilities": {
                    "nodes": [
                        {
                            "package": {
                                "ecosystem": "PIP",
                                "name": "requests"
                            },
                            "vulnerableVersionRange": ">= 2.0.0, < 2.25.0",
                            "firstPatchedVersion": {
                                "identifier": "2.25.0"
                            }
                        },
                        {
                            "package": {
                                "ecosystem": "MAVEN",
                                "name": "org.apache.logging.log4j:log4j-core"
                            },
                            "vulnerableVersionRange": "< 2.17.0",
                            "firstPatchedVersion": None  # No patched version yet
                        }
                    ]
                }
            }
        }
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.fetch_advisory("GHSA-test-1234-5678")

        assert result is not None
        assert len(result["affected_packages"]) == 2

        # First package (PIP/Python)
        pkg1 = result["affected_packages"][0]
        assert pkg1["ecosystem"] == "pip"
        assert pkg1["package_name"] == "requests"
        assert pkg1["vulnerable_versions"] == ">= 2.0.0, < 2.25.0"
        assert pkg1["patched_version"] == "2.25.0"

        # Second package (Maven/Java) - no patched version
        pkg2 = result["affected_packages"][1]
        assert pkg2["ecosystem"] == "maven"
        assert pkg2["package_name"] == "org.apache.logging.log4j:log4j-core"
        assert pkg2["vulnerable_versions"] == "< 2.17.0"
        assert pkg2["patched_version"] is None

    await client.close()


@pytest.mark.asyncio
async def test_ghsa_maps_severity_correctly():
    """
    RED: Test that severity values are correctly mapped.

    GHSA severities: LOW, MODERATE, HIGH, CRITICAL

    Expected behavior:
    - Map GHSA severity to standard format
    """
    client = GHSAClient(token="test-token")

    severities = ["LOW", "MODERATE", "HIGH", "CRITICAL"]

    for severity in severities:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "securityAdvisory": {
                    "ghsaId": f"GHSA-test-{severity.lower()}",
                    "summary": f"Test {severity} vulnerability",
                    "severity": severity,
                    "publishedAt": "2024-01-15T00:00:00Z",
                    "identifiers": [
                        {"type": "GHSA", "value": f"GHSA-test-{severity.lower()}"}
                    ],
                    "vulnerabilities": {
                        "nodes": []
                    }
                }
            }
        }

        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await client.fetch_advisory(f"GHSA-test-{severity.lower()}")

            assert result is not None
            assert result["severity"] == severity

    await client.close()


# =============================================================================
# Synthetic Data Tests (No Token)
# =============================================================================

@pytest.mark.asyncio
async def test_ghsa_synthetic_data_without_token():
    """
    RED: Test that client returns synthetic data when no token provided.

    Expected behavior:
    - Return demo/synthetic data for common queries
    """
    client = GHSAClient()  # No token

    # Should return synthetic data for known CVEs
    result = await client.search_by_cve("CVE-2021-44228")  # Log4Shell

    assert isinstance(result, list)
    assert len(result) > 0
    assert any("log4j" in str(adv).lower() for adv in result)

    await client.close()


@pytest.mark.asyncio
async def test_ghsa_synthetic_fetch_advisory_without_token():
    """
    RED: Test fetching advisory returns synthetic data without token.
    """
    client = GHSAClient()  # No token

    # Should return synthetic data for known GHSA ID
    result = await client.fetch_advisory("GHSA-jfhm-5ghh-2f97")

    assert result is not None
    assert result["ghsa_id"] == "GHSA-jfhm-5ghh-2f97"
    assert "affected_packages" in result

    await client.close()


# =============================================================================
# Multiple CVE in Advisory Tests
# =============================================================================

@pytest.mark.asyncio
async def test_ghsa_advisory_with_multiple_cves():
    """
    RED: Test parsing advisory with multiple CVE identifiers.

    Expected behavior:
    - Return primary CVE in cve_id field
    - All identifiers accessible
    """
    client = GHSAClient(token="test-token")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "securityAdvisory": {
                "ghsaId": "GHSA-multi-cve-test",
                "summary": "Multi CVE vulnerability",
                "severity": "HIGH",
                "publishedAt": "2024-01-15T00:00:00Z",
                "identifiers": [
                    {"type": "GHSA", "value": "GHSA-multi-cve-test"},
                    {"type": "CVE", "value": "CVE-2024-0001"},
                    {"type": "CVE", "value": "CVE-2024-0002"}
                ],
                "vulnerabilities": {
                    "nodes": []
                }
            }
        }
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.fetch_advisory("GHSA-multi-cve-test")

        assert result is not None
        # Primary CVE should be the first one
        assert result["cve_id"] == "CVE-2024-0001"

    await client.close()


# =============================================================================
# GraphQL Error Handling Tests
# =============================================================================

@pytest.mark.asyncio
async def test_ghsa_handles_graphql_errors():
    """
    RED: Test handling of GraphQL-level errors in response.

    Expected behavior:
    - Handle errors array in response gracefully
    """
    client = GHSAClient(token="test-token")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "errors": [
            {
                "type": "NOT_FOUND",
                "message": "Could not resolve to a SecurityAdvisory"
            }
        ],
        "data": {
            "securityAdvisory": None
        }
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.fetch_advisory("GHSA-invalid-id")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_ghsa_handles_json_parse_error():
    """
    RED: Test handling of JSON parse errors.

    Expected behavior:
    - Return None and log error
    """
    client = GHSAClient(token="test-token")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await client.fetch_advisory("GHSA-jfhm-5ghh-2f97")

        assert result is None

    await client.close()


# =============================================================================
# Authorization Header Tests
# =============================================================================

@pytest.mark.asyncio
async def test_ghsa_includes_bearer_token():
    """
    RED: Test that Bearer token is included in request headers.

    GitHub GraphQL uses Bearer token authentication.
    """
    client = GHSAClient(token="test-github-token-123")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "securityAdvisory": None
        }
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        await client.fetch_advisory("GHSA-test-1234-5678")

        # Verify authorization header
        call_args = mock_post.call_args
        assert "headers" in call_args[1]
        assert "Authorization" in call_args[1]["headers"]
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-github-token-123"

    await client.close()


@pytest.mark.asyncio
async def test_ghsa_uses_correct_graphql_endpoint():
    """
    RED: Test that client uses correct GitHub GraphQL API endpoint.
    """
    client = GHSAClient(token="test-token")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "securityAdvisory": None
        }
    }

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        await client.fetch_advisory("GHSA-test-1234-5678")

        # Verify correct URL was called
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://api.github.com/graphql"

    await client.close()
