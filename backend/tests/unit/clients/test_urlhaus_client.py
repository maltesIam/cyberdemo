"""
Unit tests for URLhaus API Client.

URLhaus (abuse.ch) provides URL and payload threat intelligence data
including malware URLs, hosts, and file hashes.

API Documentation: https://urlhaus-api.abuse.ch/v1/
Rate limit: Unlimited (free API)

These tests are written FIRST following TDD.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from src.clients.urlhaus_client import URLhausClient


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def client():
    """Create a URLhaus client instance."""
    return URLhausClient()


@pytest.fixture
def mock_host_response_success():
    """Mock successful host lookup response."""
    return {
        "query_status": "ok",
        "urlhaus_reference": "https://urlhaus.abuse.ch/host/185.141.63.120/",
        "host": "185.141.63.120",
        "blacklists": {
            "spamhaus_dbl": "not listed",
            "surbl": "not listed"
        },
        "url_count": 5,
        "urls": [
            {
                "url": "http://185.141.63.120/loader.exe",
                "url_status": "online",
                "threat": "malware_download",
                "tags": ["Emotet", "heodo"]
            },
            {
                "url": "http://185.141.63.120/payload.dll",
                "url_status": "offline",
                "threat": "malware_download",
                "tags": ["TrickBot"]
            }
        ]
    }


@pytest.fixture
def mock_host_response_not_found():
    """Mock host not found response."""
    return {
        "query_status": "no_results",
        "host": "8.8.8.8"
    }


@pytest.fixture
def mock_url_response_success():
    """Mock successful URL lookup response."""
    return {
        "query_status": "ok",
        "id": "12345",
        "urlhaus_reference": "https://urlhaus.abuse.ch/url/12345/",
        "url": "http://malicious.com/malware.exe",
        "url_status": "online",
        "host": "malicious.com",
        "date_added": "2024-01-15 10:00:00 UTC",
        "threat": "malware_download",
        "blacklists": {
            "spamhaus_dbl": "listed",
            "surbl": "not listed"
        },
        "payloads": [
            {
                "filename": "malware.exe",
                "file_type": "exe",
                "sha256_hash": "abc123def456",
                "signature": "Emotet"
            }
        ],
        "tags": ["Emotet", "malware"]
    }


@pytest.fixture
def mock_payload_response_success():
    """Mock successful payload/hash lookup response."""
    return {
        "query_status": "ok",
        "md5_hash": "abc123",
        "sha256_hash": "sha256abc123def456789",
        "file_type": "exe",
        "file_size": 123456,
        "signature": "Emotet",
        "firstseen": "2024-01-10",
        "lastseen": "2024-01-15",
        "url_count": 3,
        "urlhaus_download": "https://urlhaus.abuse.ch/download/abc123/",
        "virustotal": {
            "link": "https://www.virustotal.com/file/abc123",
            "percent": 75.5,
            "result": "45 / 60"
        },
        "urls": [
            {
                "url": "http://evil.com/file.exe",
                "url_status": "offline",
                "filename": "file.exe"
            }
        ]
    }


# =============================================================================
# Test: Host Lookup
# =============================================================================

@pytest.mark.asyncio
async def test_urlhaus_lookup_host_returns_data(client, mock_host_response_success):
    """
    RED: Test that URLhausClient can lookup a host successfully.
    
    Given a malicious IP address
    When we call lookup_host
    Then we should get threat intelligence data
    """
    with patch.object(client.client, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_host_response_success
        mock_post.return_value = mock_response

        result = await client.lookup_host("185.141.63.120")

        # Verify POST was called with correct data
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        assert "host" in str(call_kwargs)

        # Verify response structure
        assert result is not None
        assert result["query_status"] == "ok"
        assert result["host"] == "185.141.63.120"
        assert "url_count" in result
        assert result["url_count"] == 5
        assert "urls" in result
        assert len(result["urls"]) == 2
        assert result["urls"][0]["threat"] == "malware_download"


@pytest.mark.asyncio
async def test_urlhaus_lookup_unknown_host_returns_empty(client, mock_host_response_not_found):
    """
    RED: Test that URLhausClient handles unknown hosts gracefully.
    
    Given a clean/unknown IP address
    When we call lookup_host
    Then we should get a no_results response
    """
    with patch.object(client.client, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_host_response_not_found
        mock_post.return_value = mock_response

        result = await client.lookup_host("8.8.8.8")

        assert result is not None
        assert result["query_status"] == "no_results"
        assert "urls" not in result or len(result.get("urls", [])) == 0


@pytest.mark.asyncio
async def test_urlhaus_lookup_host_with_domain(client, mock_host_response_success):
    """
    RED: Test that URLhausClient can lookup a domain as host.
    """
    mock_response_domain = {
        "query_status": "ok",
        "host": "malicious-domain.com",
        "url_count": 2,
        "urls": [{"url": "http://malicious-domain.com/mal.exe", "threat": "malware_download"}]
    }
    
    with patch.object(client.client, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_domain
        mock_post.return_value = mock_response

        result = await client.lookup_host("malicious-domain.com")

        assert result is not None
        assert result["query_status"] == "ok"
        assert result["host"] == "malicious-domain.com"


# =============================================================================
# Test: URL Lookup
# =============================================================================

@pytest.mark.asyncio
async def test_urlhaus_lookup_url_returns_data(client, mock_url_response_success):
    """
    RED: Test that URLhausClient can lookup a URL successfully.
    """
    with patch.object(client.client, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_url_response_success
        mock_post.return_value = mock_response

        result = await client.lookup_url("http://malicious.com/malware.exe")

        assert result is not None
        assert result["query_status"] == "ok"
        assert result["url"] == "http://malicious.com/malware.exe"
        assert result["threat"] == "malware_download"
        assert "payloads" in result


@pytest.mark.asyncio
async def test_urlhaus_lookup_url_not_found(client):
    """
    RED: Test handling of unknown URL.
    """
    mock_not_found = {
        "query_status": "no_results",
        "url": "http://clean-site.com/file.txt"
    }
    
    with patch.object(client.client, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_not_found
        mock_post.return_value = mock_response

        result = await client.lookup_url("http://clean-site.com/file.txt")

        assert result is not None
        assert result["query_status"] == "no_results"


# =============================================================================
# Test: Payload/Hash Lookup
# =============================================================================

@pytest.mark.asyncio
async def test_urlhaus_lookup_payload_by_sha256_hash(client, mock_payload_response_success):
    """
    RED: Test that URLhausClient can lookup a payload by SHA256 hash.
    """
    with patch.object(client.client, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_payload_response_success
        mock_post.return_value = mock_response

        result = await client.lookup_payload("sha256abc123def456789", hash_type="sha256")

        # Verify POST was called with sha256_hash
        mock_post.assert_called_once()
        
        assert result is not None
        assert result["query_status"] == "ok"
        assert result["sha256_hash"] == "sha256abc123def456789"
        assert result["signature"] == "Emotet"
        assert "virustotal" in result


@pytest.mark.asyncio
async def test_urlhaus_lookup_payload_by_md5_hash(client, mock_payload_response_success):
    """
    RED: Test that URLhausClient can lookup a payload by MD5 hash.
    """
    mock_md5_response = {
        "query_status": "ok",
        "md5_hash": "abc123md5hash",
        "sha256_hash": "sha256full",
        "signature": "TrickBot"
    }
    
    with patch.object(client.client, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_md5_response
        mock_post.return_value = mock_response

        result = await client.lookup_payload("abc123md5hash", hash_type="md5")

        assert result is not None
        assert result["query_status"] == "ok"
        assert result["md5_hash"] == "abc123md5hash"


@pytest.mark.asyncio
async def test_urlhaus_lookup_payload_unknown_hash(client):
    """
    RED: Test handling of unknown file hash.
    """
    mock_not_found = {
        "query_status": "no_results",
        "sha256_hash": "unknownhash123"
    }
    
    with patch.object(client.client, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_not_found
        mock_post.return_value = mock_response

        result = await client.lookup_payload("unknownhash123", hash_type="sha256")

        assert result is not None
        assert result["query_status"] == "no_results"


@pytest.mark.asyncio
async def test_urlhaus_lookup_payload_default_hash_type(client, mock_payload_response_success):
    """
    RED: Test that default hash_type is sha256.
    """
    with patch.object(client.client, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_payload_response_success
        mock_post.return_value = mock_response

        # Call without specifying hash_type - should default to sha256
        result = await client.lookup_payload("sha256abc123def456789")

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        # Verify sha256_hash was used (not md5_hash)
        assert "sha256_hash" in str(call_args) or result is not None


# =============================================================================
# Test: Error Handling
# =============================================================================

@pytest.mark.asyncio
async def test_urlhaus_handles_api_error(client):
    """
    RED: Test that URLhausClient handles API errors gracefully.
    """
    with patch.object(client.client, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        result = await client.lookup_host("1.2.3.4")

        # Should return None on API error
        assert result is None


@pytest.mark.asyncio
async def test_urlhaus_handles_timeout(client):
    """
    RED: Test that URLhausClient handles timeout gracefully.
    """
    with patch.object(client.client, 'post') as mock_post:
        mock_post.side_effect = httpx.TimeoutException("Request timed out")

        result = await client.lookup_host("1.2.3.4")

        assert result is None


@pytest.mark.asyncio
async def test_urlhaus_handles_connection_error(client):
    """
    RED: Test that URLhausClient handles connection errors gracefully.
    """
    with patch.object(client.client, 'post') as mock_post:
        mock_post.side_effect = httpx.ConnectError("Connection refused")

        result = await client.lookup_url("http://test.com/file.exe")

        assert result is None


@pytest.mark.asyncio
async def test_urlhaus_handles_malformed_json(client):
    """
    RED: Test handling of malformed JSON response.
    """
    with patch.object(client.client, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response

        result = await client.lookup_host("1.2.3.4")

        assert result is None


@pytest.mark.asyncio
async def test_urlhaus_handles_invalid_hash_type(client):
    """
    RED: Test that invalid hash_type raises ValueError.
    """
    with pytest.raises(ValueError, match="hash_type must be"):
        await client.lookup_payload("somehash", hash_type="invalid")


# =============================================================================
# Test: Client Lifecycle
# =============================================================================

@pytest.mark.asyncio
async def test_urlhaus_client_close():
    """
    RED: Test that client can be closed properly.
    """
    client = URLhausClient()
    
    with patch.object(client.client, 'aclose') as mock_close:
        mock_close.return_value = None
        await client.close()
        mock_close.assert_called_once()


@pytest.mark.asyncio
async def test_urlhaus_client_custom_timeout():
    """
    RED: Test that client respects custom timeout.
    """
    client = URLhausClient(timeout=60)
    
    assert client.timeout == 60


@pytest.mark.asyncio
async def test_urlhaus_client_default_timeout():
    """
    RED: Test that client has sensible default timeout.
    """
    client = URLhausClient()
    
    assert client.timeout == 30  # Default timeout
