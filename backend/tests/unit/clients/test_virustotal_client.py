"""
Unit tests for VirusTotal API Client.

VirusTotal provides threat intelligence for files, URLs, domains, and IPs.

API Documentation: https://developers.virustotal.com/reference/overview
Rate limit: 500 requests/day (free tier), 4 requests/minute

These tests are written FIRST following TDD (RED phase).
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

# Import will fail until we implement the module (RED phase)
try:
    from src.clients.virustotal_client import VirusTotalClient
except ImportError:
    pass


# =============================================================================
# IP Lookup Tests
# =============================================================================

@pytest.mark.asyncio
async def test_virustotal_check_ip_returns_report():
    """
    RED: Test that VirusTotalClient can check an IP and return a report.

    Expected behavior:
    - Fetch IP report from VirusTotal
    - Return dict with IP analysis including malicious/harmless stats
    """
    client = VirusTotalClient(api_key="test-api-key")

    # Mock successful API response based on VirusTotal API v3 structure
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "ip_address",
            "id": "8.8.8.8",
            "attributes": {
                "network": "8.8.8.0/24",
                "country": "US",
                "as_owner": "GOOGLE",
                "asn": 15169,
                "regional_internet_registry": "ARIN",
                "last_analysis_stats": {
                    "harmless": 70,
                    "malicious": 0,
                    "suspicious": 0,
                    "undetected": 10,
                    "timeout": 0
                },
                "reputation": 0,
                "last_analysis_date": 1700000000,
                "whois": "NetRange: 8.8.8.0 - 8.8.8.255",
                "last_modification_date": 1700000000
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_ip("8.8.8.8")

        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "8.8.8.8" in call_args[0][0]

        # Verify response structure
        assert result is not None
        assert result["id"] == "8.8.8.8"
        assert result["type"] == "ip_address"
        assert "last_analysis_stats" in result["attributes"]
        assert result["attributes"]["last_analysis_stats"]["malicious"] == 0
        assert result["attributes"]["country"] == "US"

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_check_ip_malicious():
    """
    RED: Test IP check for a known malicious IP.

    Expected behavior:
    - Return report with malicious detections
    """
    client = VirusTotalClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "ip_address",
            "id": "185.141.63.120",
            "attributes": {
                "network": "185.141.63.0/24",
                "country": "RU",
                "as_owner": "MALICIOUS-HOSTING",
                "asn": 12345,
                "last_analysis_stats": {
                    "harmless": 20,
                    "malicious": 45,
                    "suspicious": 5,
                    "undetected": 10,
                    "timeout": 0
                },
                "reputation": -100,
                "last_analysis_date": 1700000000
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_ip("185.141.63.120")

        assert result is not None
        assert result["attributes"]["last_analysis_stats"]["malicious"] == 45
        assert result["attributes"]["reputation"] == -100

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_get_ip_report():
    """
    RED: Test get_ip_report returns detailed IP analysis.

    Expected behavior:
    - Return comprehensive IP report with all available data
    """
    client = VirusTotalClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "ip_address",
            "id": "1.2.3.4",
            "attributes": {
                "network": "1.2.3.0/24",
                "country": "DE",
                "continent": "EU",
                "as_owner": "Example ISP",
                "asn": 54321,
                "regional_internet_registry": "RIPE",
                "last_analysis_stats": {
                    "harmless": 60,
                    "malicious": 2,
                    "suspicious": 1,
                    "undetected": 17,
                    "timeout": 0
                },
                "last_analysis_results": {
                    "Vendor1": {
                        "category": "harmless",
                        "result": "clean",
                        "method": "blacklist",
                        "engine_name": "Vendor1"
                    },
                    "Vendor2": {
                        "category": "malicious",
                        "result": "malware",
                        "method": "blacklist",
                        "engine_name": "Vendor2"
                    }
                },
                "reputation": -15,
                "total_votes": {
                    "harmless": 10,
                    "malicious": 5
                }
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_ip_report("1.2.3.4")

        assert result is not None
        assert "last_analysis_results" in result["attributes"]
        assert "total_votes" in result["attributes"]

    await client.close()


# =============================================================================
# URL Analysis Tests
# =============================================================================

@pytest.mark.asyncio
async def test_virustotal_check_url_clean():
    """
    RED: Test URL analysis for a clean URL.

    Expected behavior:
    - Submit URL for analysis
    - Return analysis results
    """
    client = VirusTotalClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "url",
            "id": "aHR0cHM6Ly9nb29nbGUuY29t",  # Base64 encoded URL
            "attributes": {
                "url": "https://google.com",
                "last_http_response_content_length": 12345,
                "last_http_response_code": 200,
                "last_final_url": "https://www.google.com/",
                "last_analysis_stats": {
                    "harmless": 75,
                    "malicious": 0,
                    "suspicious": 0,
                    "undetected": 5,
                    "timeout": 0
                },
                "reputation": 100,
                "categories": {
                    "Forcepoint ThreatSeeker": "search engines and portals"
                },
                "last_analysis_date": 1700000000
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_url("https://google.com")

        assert result is not None
        assert result["attributes"]["url"] == "https://google.com"
        assert result["attributes"]["last_analysis_stats"]["malicious"] == 0

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_check_url_malicious():
    """
    RED: Test URL analysis for a malicious URL.

    Expected behavior:
    - Return analysis with malicious detections
    """
    client = VirusTotalClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "url",
            "id": "aHR0cDovL21hbHdhcmUuY29t",
            "attributes": {
                "url": "http://malware.com/bad.exe",
                "last_http_response_code": 200,
                "last_analysis_stats": {
                    "harmless": 10,
                    "malicious": 55,
                    "suspicious": 10,
                    "undetected": 5,
                    "timeout": 0
                },
                "reputation": -200,
                "threat_names": ["malware", "phishing"],
                "categories": {
                    "Vendor1": "malware"
                },
                "last_analysis_date": 1700000000
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_url("http://malware.com/bad.exe")

        assert result is not None
        assert result["attributes"]["last_analysis_stats"]["malicious"] == 55
        assert result["attributes"]["reputation"] == -200

    await client.close()


# =============================================================================
# Hash/File Analysis Tests
# =============================================================================

@pytest.mark.asyncio
async def test_virustotal_check_hash_clean():
    """
    RED: Test file hash analysis for a clean file.

    Expected behavior:
    - Lookup file by SHA256 hash
    - Return analysis results
    """
    client = VirusTotalClient(api_key="test-api-key")

    # SHA256 of a clean file (e.g., notepad.exe)
    sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "file",
            "id": sha256,
            "attributes": {
                "sha256": sha256,
                "sha1": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
                "md5": "d41d8cd98f00b204e9800998ecf8427e",
                "size": 0,
                "type_description": "empty",
                "meaningful_name": "empty.txt",
                "last_analysis_stats": {
                    "harmless": 0,
                    "malicious": 0,
                    "suspicious": 0,
                    "undetected": 70,
                    "type-unsupported": 10,
                    "timeout": 0,
                    "confirmed-timeout": 0,
                    "failure": 0
                },
                "reputation": 0,
                "last_analysis_date": 1700000000
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_hash(sha256)

        assert result is not None
        assert result["attributes"]["sha256"] == sha256
        assert result["attributes"]["last_analysis_stats"]["malicious"] == 0

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_check_hash_malicious():
    """
    RED: Test file hash analysis for a known malicious file.

    Expected behavior:
    - Return analysis with malicious detections and threat names
    """
    client = VirusTotalClient(api_key="test-api-key")

    # Example malicious hash
    sha256 = "bad0bad0bad0bad0bad0bad0bad0bad0bad0bad0bad0bad0bad0bad0bad0bad0"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "file",
            "id": sha256,
            "attributes": {
                "sha256": sha256,
                "sha1": "bad1bad1bad1bad1bad1bad1bad1bad1bad1bad1",
                "md5": "badbadbadbadbadbadbadbadbadbadb",
                "size": 123456,
                "type_description": "Win32 EXE",
                "meaningful_name": "malware.exe",
                "last_analysis_stats": {
                    "harmless": 0,
                    "malicious": 60,
                    "suspicious": 5,
                    "undetected": 5,
                    "type-unsupported": 0,
                    "timeout": 0,
                    "confirmed-timeout": 0,
                    "failure": 0
                },
                "reputation": -500,
                "popular_threat_classification": {
                    "suggested_threat_label": "trojan.generic/msil",
                    "popular_threat_category": [
                        {"count": 40, "value": "trojan"},
                        {"count": 15, "value": "downloader"}
                    ],
                    "popular_threat_name": [
                        {"count": 20, "value": "emotet"},
                        {"count": 10, "value": "generic"}
                    ]
                },
                "last_analysis_date": 1700000000
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_hash(sha256)

        assert result is not None
        assert result["attributes"]["last_analysis_stats"]["malicious"] == 60
        assert "popular_threat_classification" in result["attributes"]

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_check_hash_md5():
    """
    RED: Test hash lookup with MD5.

    Expected behavior:
    - Accept MD5 hash format
    - Return file analysis
    """
    client = VirusTotalClient(api_key="test-api-key")

    md5 = "d41d8cd98f00b204e9800998ecf8427e"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "file",
            "id": md5,
            "attributes": {
                "md5": md5,
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "last_analysis_stats": {
                    "harmless": 0,
                    "malicious": 0,
                    "suspicious": 0,
                    "undetected": 70,
                    "timeout": 0
                }
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_hash(md5)

        assert result is not None
        assert result["attributes"]["md5"] == md5

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_check_hash_sha1():
    """
    RED: Test hash lookup with SHA1.

    Expected behavior:
    - Accept SHA1 hash format
    - Return file analysis
    """
    client = VirusTotalClient(api_key="test-api-key")

    sha1 = "da39a3ee5e6b4b0d3255bfef95601890afd80709"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "file",
            "id": sha1,
            "attributes": {
                "sha1": sha1,
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "last_analysis_stats": {
                    "harmless": 0,
                    "malicious": 0,
                    "suspicious": 0,
                    "undetected": 70,
                    "timeout": 0
                }
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_hash(sha1)

        assert result is not None
        assert result["attributes"]["sha1"] == sha1

    await client.close()


# =============================================================================
# Quota Handling Tests (500/day limit)
# =============================================================================

@pytest.mark.asyncio
async def test_virustotal_quota_exceeded():
    """
    RED: Test handling when daily quota is exceeded.

    VirusTotal free tier: 500 requests/day
    API returns 429 when quota exceeded.
    """
    client = VirusTotalClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.json.return_value = {
        "error": {
            "code": "QuotaExceededError",
            "message": "You have exceeded your daily quota. Please try again tomorrow."
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_ip("8.8.8.8")

        # Should return None on quota exceeded
        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_rate_limit_per_minute():
    """
    RED: Test handling of per-minute rate limit (4 req/min).

    Expected behavior:
    - Return None and log warning
    """
    client = VirusTotalClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {"X-RateLimit-Reset": "60"}
    mock_response.json.return_value = {
        "error": {
            "code": "TooManyRequestsError",
            "message": "Request rate limit exceeded. Please reduce your request rate."
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_url("https://example.com")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_get_quota_status():
    """
    RED: Test getting current quota status.

    Expected behavior:
    - Return dict with quota information
    """
    client = VirusTotalClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "user",
            "id": "test-user",
            "attributes": {
                "quotas": {
                    "api_requests_daily": {
                        "used": 100,
                        "allowed": 500
                    },
                    "api_requests_hourly": {
                        "used": 10,
                        "allowed": 240
                    },
                    "api_requests_monthly": {
                        "used": 5000,
                        "allowed": 15500
                    }
                }
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_quota_status()

        assert result is not None
        assert "quotas" in result
        assert result["quotas"]["api_requests_daily"]["used"] == 100
        assert result["quotas"]["api_requests_daily"]["allowed"] == 500

    await client.close()


# =============================================================================
# Error Handling Tests
# =============================================================================

@pytest.mark.asyncio
async def test_virustotal_handles_not_found():
    """
    RED: Test handling when resource is not found (404).

    Expected behavior:
    - Return None for unknown hash/URL/IP
    """
    client = VirusTotalClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {
        "error": {
            "code": "NotFoundError",
            "message": "Resource not found"
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_hash("0000000000000000000000000000000000000000000000000000000000000000")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_handles_invalid_api_key():
    """
    RED: Test handling of invalid/missing API key (401).

    Expected behavior:
    - Return None and log error
    """
    client = VirusTotalClient(api_key="invalid-key")

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {
        "error": {
            "code": "AuthenticationError",
            "message": "Invalid API key"
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_ip("8.8.8.8")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_handles_forbidden():
    """
    RED: Test handling of forbidden access (403).

    Expected behavior:
    - Return None and log error
    """
    client = VirusTotalClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.json.return_value = {
        "error": {
            "code": "ForbiddenError",
            "message": "You do not have access to this resource"
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_ip("8.8.8.8")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_handles_server_error():
    """
    RED: Test handling of server errors (5xx).

    Expected behavior:
    - Return None and log error
    """
    client = VirusTotalClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {
        "error": {
            "code": "InternalServerError",
            "message": "Internal server error"
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_ip("8.8.8.8")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_handles_timeout():
    """
    RED: Test timeout handling.

    Expected behavior:
    - Return None on timeout
    - No exceptions should propagate
    """
    client = VirusTotalClient(api_key="test-api-key", timeout=5)

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Request timed out")

        result = await client.check_ip("1.1.1.1")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_handles_request_error():
    """
    RED: Test handling of network/request errors.

    Expected behavior:
    - Return None on network error
    - No exceptions should propagate
    """
    client = VirusTotalClient(api_key="test-api-key")

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await client.check_hash("abc123")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_handles_connection_error():
    """
    RED: Test handling of connection errors.

    Expected behavior:
    - Return None on connection error
    """
    client = VirusTotalClient(api_key="test-api-key")

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.ConnectError("Failed to connect")

        result = await client.check_url("https://example.com")

        assert result is None

    await client.close()


# =============================================================================
# Response Parsing Tests
# =============================================================================

@pytest.mark.asyncio
async def test_virustotal_parses_analysis_stats_correctly():
    """
    RED: Test correct parsing of analysis statistics.

    Expected behavior:
    - Extract and structure last_analysis_stats
    """
    client = VirusTotalClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "ip_address",
            "id": "8.8.8.8",
            "attributes": {
                "last_analysis_stats": {
                    "harmless": 70,
                    "malicious": 2,
                    "suspicious": 1,
                    "undetected": 7,
                    "timeout": 0
                }
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_ip("8.8.8.8")

        stats = result["attributes"]["last_analysis_stats"]
        assert stats["harmless"] == 70
        assert stats["malicious"] == 2
        assert stats["suspicious"] == 1
        assert stats["undetected"] == 7
        assert stats["timeout"] == 0

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_parses_threat_classification():
    """
    RED: Test parsing of threat classification data.

    Expected behavior:
    - Extract threat labels and categories
    """
    client = VirusTotalClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "file",
            "id": "abc123",
            "attributes": {
                "sha256": "abc123",
                "last_analysis_stats": {
                    "malicious": 50
                },
                "popular_threat_classification": {
                    "suggested_threat_label": "ransomware.wannacry/gen",
                    "popular_threat_category": [
                        {"count": 30, "value": "ransomware"},
                        {"count": 15, "value": "trojan"}
                    ],
                    "popular_threat_name": [
                        {"count": 25, "value": "wannacry"}
                    ]
                }
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_hash("abc123")

        classification = result["attributes"]["popular_threat_classification"]
        assert classification["suggested_threat_label"] == "ransomware.wannacry/gen"
        assert classification["popular_threat_category"][0]["value"] == "ransomware"

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_handles_malformed_response():
    """
    RED: Test handling of malformed/unexpected API response.

    Expected behavior:
    - Handle gracefully without crashing
    """
    client = VirusTotalClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "unexpected": "data"
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_ip("8.8.8.8")

        # Should return None for malformed response
        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_handles_json_parse_error():
    """
    RED: Test handling of JSON parse errors.

    Expected behavior:
    - Return None and log error
    """
    client = VirusTotalClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_ip("8.8.8.8")

        assert result is None

    await client.close()


# =============================================================================
# Client Configuration Tests
# =============================================================================

@pytest.mark.asyncio
async def test_virustotal_requires_api_key():
    """
    RED: Test that client requires API key.

    Expected behavior:
    - Client can be created with API key
    """
    client = VirusTotalClient(api_key="my-api-key")

    assert client.api_key == "my-api-key"

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_custom_timeout():
    """
    RED: Test that custom timeout is applied.
    """
    client = VirusTotalClient(api_key="test-key", timeout=60)

    assert client.timeout == 60

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_client_close():
    """
    RED: Test that client can be properly closed.
    """
    client = VirusTotalClient(api_key="test-key")

    # Should not raise any exceptions
    await client.close()


@pytest.mark.asyncio
async def test_virustotal_uses_correct_base_url():
    """
    RED: Test that client uses correct VirusTotal API v3 base URL.
    """
    client = VirusTotalClient(api_key="test-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "ip_address",
            "id": "8.8.8.8",
            "attributes": {}
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        await client.check_ip("8.8.8.8")

        # Verify correct URL was called
        call_args = mock_get.call_args
        assert "https://www.virustotal.com/api/v3/" in call_args[0][0]

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_includes_api_key_header():
    """
    RED: Test that API key is included in request headers.

    VirusTotal uses x-apikey header for authentication.
    """
    client = VirusTotalClient(api_key="test-api-key-123")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "ip_address",
            "id": "8.8.8.8",
            "attributes": {}
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        await client.check_ip("8.8.8.8")

        # Verify API key header was included
        call_args = mock_get.call_args
        assert "headers" in call_args[1]
        assert call_args[1]["headers"]["x-apikey"] == "test-api-key-123"

    await client.close()


# =============================================================================
# Domain Lookup Tests
# =============================================================================

@pytest.mark.asyncio
async def test_virustotal_check_domain():
    """
    RED: Test domain lookup functionality.

    Expected behavior:
    - Fetch domain report
    - Return dict with domain analysis
    """
    client = VirusTotalClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "domain",
            "id": "example.com",
            "attributes": {
                "registrar": "Example Registrar",
                "creation_date": 1234567890,
                "last_modification_date": 1700000000,
                "last_analysis_stats": {
                    "harmless": 70,
                    "malicious": 0,
                    "suspicious": 0,
                    "undetected": 10,
                    "timeout": 0
                },
                "reputation": 0,
                "categories": {
                    "Vendor1": "business"
                },
                "whois": "Domain Name: EXAMPLE.COM"
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_domain("example.com")

        assert result is not None
        assert result["type"] == "domain"
        assert result["id"] == "example.com"
        assert result["attributes"]["last_analysis_stats"]["malicious"] == 0

    await client.close()


# =============================================================================
# Structured Response Tests for Threat Enrichment
# =============================================================================

@pytest.mark.asyncio
async def test_virustotal_get_enrichment_data_ip():
    """
    RED: Test getting structured enrichment data for IP.

    Expected behavior:
    - Return enrichment-ready data structure
    """
    client = VirusTotalClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "ip_address",
            "id": "185.141.63.120",
            "attributes": {
                "country": "RU",
                "as_owner": "SUSPICIOUS-HOSTING",
                "asn": 12345,
                "last_analysis_stats": {
                    "harmless": 10,
                    "malicious": 55,
                    "suspicious": 5,
                    "undetected": 10,
                    "timeout": 0
                },
                "reputation": -150
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_enrichment_data("ip", "185.141.63.120")

        assert result is not None
        assert result["indicator"] == "185.141.63.120"
        assert result["indicator_type"] == "ip"
        assert result["source"] == "virustotal"
        assert "malicious_count" in result
        assert result["malicious_count"] == 55
        assert "total_engines" in result
        assert "country" in result
        assert result["is_malicious"] is True

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_get_enrichment_data_hash():
    """
    RED: Test getting structured enrichment data for file hash.

    Expected behavior:
    - Return enrichment-ready data structure with threat info
    """
    client = VirusTotalClient(api_key="test-api-key")

    sha256 = "bad0bad0bad0bad0bad0bad0bad0bad0bad0bad0bad0bad0bad0bad0bad0bad0"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "type": "file",
            "id": sha256,
            "attributes": {
                "sha256": sha256,
                "meaningful_name": "malware.exe",
                "type_description": "Win32 EXE",
                "last_analysis_stats": {
                    "harmless": 0,
                    "malicious": 60,
                    "suspicious": 5,
                    "undetected": 5,
                    "timeout": 0
                },
                "reputation": -500,
                "popular_threat_classification": {
                    "suggested_threat_label": "trojan.emotet"
                }
            }
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_enrichment_data("hash", sha256)

        assert result is not None
        assert result["indicator"] == sha256
        assert result["indicator_type"] == "hash"
        assert result["source"] == "virustotal"
        assert result["malicious_count"] == 60
        assert result["is_malicious"] is True
        assert "threat_label" in result

    await client.close()


@pytest.mark.asyncio
async def test_virustotal_get_enrichment_data_not_found():
    """
    RED: Test enrichment data for unknown indicator.

    Expected behavior:
    - Return None for not found
    """
    client = VirusTotalClient(api_key="test-api-key")

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {
        "error": {
            "code": "NotFoundError"
        }
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_enrichment_data("hash", "unknown123")

        assert result is None

    await client.close()
