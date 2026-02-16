"""
Unit tests for HaveIBeenPwned (HIBP) API Client.

HIBP provides data breach and password exposure checking services.
Uses k-anonymity for password checks to avoid sending the full password hash.

API Documentation: https://haveibeenpwned.com/api/v3
Rate limit: 1500ms between requests for breach search API (requires API key)
Password API: No rate limit, uses k-anonymity (first 5 chars of SHA1 hash)

These tests are written FIRST following TDD.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
import hashlib

# Import will fail until we implement the module (RED phase)
try:
    from src.clients.hibp_client import HIBPClient
except ImportError:
    pass


@pytest.mark.asyncio
async def test_hibp_check_password_pwned():
    """
    RED: Test that HIBPClient can check if a password has been pwned.

    Expected behavior:
    - Check password against HIBP Passwords API
    - Return the count of times the password appears in breaches
    """
    client = HIBPClient()

    # The password "password123" - we'll mock the API response
    # SHA1 hash of "password123" is: CBFDAC6008F9CAB4083784CBD1874F76618D2A97
    # API is called with first 5 chars: CBFDA
    # Response includes suffix C6008F9CAB4083784CBD1874F76618D2A97:12345

    mock_response = MagicMock()
    mock_response.status_code = 200
    # HIBP returns suffixes with counts, one per line
    mock_response.text = """C6008F9CAB4083784CBD1874F76618D2A97:12345
1234567890ABCDEF1234567890ABCDEF123:500
0000000000000000000000000000000000000:1"""

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_password("password123")

        # Verify request was made correctly (only first 5 chars of SHA1)
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        # URL should contain the prefix CBFDA
        assert "CBFDA" in call_args[0][0]

        # Should return the count
        assert result == 12345

    await client.close()


@pytest.mark.asyncio
async def test_hibp_check_password_not_pwned():
    """
    RED: Test that HIBPClient returns 0 for a password not found in breaches.

    Expected behavior:
    - Check password against HIBP Passwords API
    - Return 0 when password hash suffix is not in response
    """
    client = HIBPClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    # Response doesn't include the suffix we're looking for
    mock_response.text = """1234567890ABCDEF1234567890ABCDEF123:500
0000000000000000000000000000000000000:1
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA:99"""

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        # Use a password whose hash suffix won't be in the mock response
        result = await client.check_password("my-super-secure-unique-password-xyz123")

        # Should return 0 (not found)
        assert result == 0

    await client.close()


@pytest.mark.asyncio
async def test_hibp_check_email_breaches():
    """
    RED: Test that HIBPClient can check email for breaches.

    Expected behavior:
    - Check email against HIBP breach API (requires API key)
    - Return list of breaches the email appears in
    """
    client = HIBPClient(api_key="test-api-key-123")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "Name": "Adobe",
            "Title": "Adobe",
            "Domain": "adobe.com",
            "BreachDate": "2013-10-04",
            "AddedDate": "2013-12-04T00:00:00Z",
            "ModifiedDate": "2022-05-15T23:52:49Z",
            "PwnCount": 152445165,
            "Description": "In October 2013, 153 million Adobe accounts were breached...",
            "DataClasses": ["Email addresses", "Password hints", "Passwords", "Usernames"],
            "IsVerified": True,
            "IsFabricated": False,
            "IsSensitive": False,
            "IsRetired": False,
            "IsSpamList": False,
            "IsMalware": False,
            "IsSubscriptionFree": False,
            "LogoPath": "https://haveibeenpwned.com/Content/Images/PwnedLogos/Adobe.png"
        },
        {
            "Name": "LinkedIn",
            "Title": "LinkedIn",
            "Domain": "linkedin.com",
            "BreachDate": "2012-05-05",
            "AddedDate": "2016-05-21T21:35:40Z",
            "ModifiedDate": "2023-02-07T12:17:03Z",
            "PwnCount": 164611595,
            "Description": "In May 2012, LinkedIn had 164 million email addresses and passwords exposed...",
            "DataClasses": ["Email addresses", "Passwords"],
            "IsVerified": True,
            "IsFabricated": False,
            "IsSensitive": False,
            "IsRetired": False,
            "IsSpamList": False,
            "IsMalware": False,
            "IsSubscriptionFree": False,
            "LogoPath": "https://haveibeenpwned.com/Content/Images/PwnedLogos/LinkedIn.png"
        }
    ]

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_email_breaches("test@example.com")

        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        # URL should contain the email
        assert "test%40example.com" in call_args[0][0] or "test@example.com" in call_args[0][0]
        # Should include API key header
        assert "hibp-api-key" in call_args[1].get("headers", {})

        # Should return list of breaches
        assert result is not None
        assert len(result) == 2
        assert result[0]["Name"] == "Adobe"
        assert result[1]["Name"] == "LinkedIn"

    await client.close()


@pytest.mark.asyncio
async def test_hibp_check_email_not_found():
    """
    RED: Test that HIBPClient returns empty list when email not found in breaches.

    Expected behavior:
    - When email is not in any breach, API returns 404
    - Client should return empty list
    """
    client = HIBPClient(api_key="test-api-key-123")

    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_email_breaches("clean@example.com")

        # Should return empty list for not found
        assert result == []

    await client.close()


@pytest.mark.asyncio
async def test_hibp_handles_rate_limit():
    """
    RED: Test that HIBPClient handles rate limiting (429 status).

    Expected behavior:
    - When API returns 429 rate limit, client should return None
    - Should log appropriate warning
    """
    client = HIBPClient(api_key="test-api-key-123")

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {"retry-after": "2"}

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_email_breaches("test@example.com")

        # Should return None on rate limit
        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_hibp_handles_api_error():
    """
    RED: Test that HIBPClient handles API errors gracefully.

    Expected behavior:
    - When API returns server error, client should return None
    - No exceptions should propagate
    """
    client = HIBPClient(api_key="test-api-key-123")

    mock_response = MagicMock()
    mock_response.status_code = 500

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_email_breaches("test@example.com")

        # Should return None on error
        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_hibp_handles_timeout():
    """
    RED: Test timeout handling.

    Expected behavior:
    - When request times out, return None (for email) or 0 (for password)
    - No exceptions should propagate
    """
    client = HIBPClient(timeout=5)

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Request timed out")

        # Password check should return 0 on timeout (fail-safe)
        result = await client.check_password("test123")
        assert result == 0

    await client.close()


@pytest.mark.asyncio
async def test_hibp_handles_timeout_email():
    """
    RED: Test timeout handling for email breaches check.

    Expected behavior:
    - When request times out, return None
    - No exceptions should propagate
    """
    client = HIBPClient(api_key="test-api-key-123", timeout=5)

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Request timed out")

        # Email check should return None on timeout
        result = await client.check_email_breaches("test@example.com")
        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_hibp_uses_k_anonymity():
    """
    RED: Test that password check uses k-anonymity (SHA1 prefix only).

    Expected behavior:
    - Password is hashed with SHA1
    - Only first 5 characters of hash are sent to API
    - Client matches suffix locally to find the count
    """
    client = HIBPClient()

    # Test with known password "test"
    # SHA1("test") = A94A8FE5CCB19BA61C4C0873D391E987982FBBD3
    # Prefix: A94A8 (first 5 chars)
    # Suffix: FE5CCB19BA61C4C0873D391E987982FBBD3 (rest)

    mock_response = MagicMock()
    mock_response.status_code = 200
    # Response should include the suffix with count
    mock_response.text = """FE5CCB19BA61C4C0873D391E987982FBBD3:86453
0000000000000000000000000000000000000:1
1234567890ABCDEF1234567890ABCDEF123:500"""

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_password("test")

        # Verify only the prefix was sent
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        url = call_args[0][0]
        # URL should end with the prefix A94A8
        assert "A94A8" in url
        # URL should NOT contain the full hash
        assert "FE5CCB19BA61C4C0873D391E987982FBBD3" not in url

        # Should find the matching suffix and return count
        assert result == 86453

    await client.close()


@pytest.mark.asyncio
async def test_hibp_client_close():
    """
    RED: Test that client can be properly closed.
    """
    client = HIBPClient()

    # Should not raise any exceptions
    await client.close()


@pytest.mark.asyncio
async def test_hibp_custom_timeout():
    """
    RED: Test that custom timeout is applied.
    """
    client = HIBPClient(timeout=15)

    # Verify timeout was set
    assert client.timeout == 15

    await client.close()


@pytest.mark.asyncio
async def test_hibp_email_requires_api_key():
    """
    RED: Test that email breach check fails without API key.

    Expected behavior:
    - When no API key is provided, email check should return None
    - Should log appropriate warning
    """
    client = HIBPClient()  # No API key

    # Should return None without making a request
    result = await client.check_email_breaches("test@example.com")

    assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_hibp_password_no_api_key_required():
    """
    RED: Test that password check works without API key.

    Expected behavior:
    - Password API uses k-anonymity and doesn't require API key
    """
    client = HIBPClient()  # No API key

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "FE5CCB19BA61C4C0873D391E987982FBBD3:100"

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_password("test")

        # Should work without API key
        mock_get.assert_called_once()
        # Verify no API key header was sent for password check
        call_args = mock_get.call_args
        headers = call_args[1].get("headers", {})
        assert "hibp-api-key" not in headers

    await client.close()


@pytest.mark.asyncio
async def test_hibp_handles_request_error():
    """
    RED: Test handling of network/request errors.

    Expected behavior:
    - When network error occurs, return appropriate default
    - No exceptions should propagate
    """
    client = HIBPClient()

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await client.check_password("test123")

        # Should return 0 on error (fail-safe for password check)
        assert result == 0

    await client.close()


@pytest.mark.asyncio
async def test_hibp_uses_correct_base_urls():
    """
    RED: Test that client uses correct HIBP API URLs.

    Expected behavior:
    - Password API: https://api.pwnedpasswords.com/range/{prefix}
    - Breach API: https://haveibeenpwned.com/api/v3/breachedaccount/{email}
    """
    client = HIBPClient(api_key="test-api-key-123")

    # Test password URL
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "0000000000000000000000000000000000000:1"

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        await client.check_password("test")

        call_args = mock_get.call_args
        url = call_args[0][0]
        assert "api.pwnedpasswords.com/range/" in url

    # Test email breach URL
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        await client.check_email_breaches("test@example.com")

        call_args = mock_get.call_args
        url = call_args[0][0]
        assert "haveibeenpwned.com/api/v3/breachedaccount/" in url

    await client.close()


@pytest.mark.asyncio
async def test_hibp_auth_error_handling():
    """
    RED: Test handling of authentication errors (401).

    Expected behavior:
    - When API returns 401, client should return None
    - Should log appropriate error
    """
    client = HIBPClient(api_key="invalid-key")

    mock_response = MagicMock()
    mock_response.status_code = 401

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_email_breaches("test@example.com")

        # Should return None on auth error
        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_hibp_user_agent_header():
    """
    RED: Test that proper User-Agent header is sent.

    HIBP requires a user agent string.
    """
    client = HIBPClient(api_key="test-api-key-123")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        await client.check_email_breaches("test@example.com")

        call_args = mock_get.call_args
        headers = call_args[1].get("headers", {})
        # Should have a user agent
        assert "User-Agent" in headers or "user-agent" in headers

    await client.close()
