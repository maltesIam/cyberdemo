"""
Unit tests for CISA KEV (Known Exploited Vulnerabilities) API Client.

CISA KEV provides a catalog of vulnerabilities that are known to be actively
exploited in the wild. This is critical for vulnerability prioritization.

API URL: https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
Rate limit: Free API, no authentication required.

These tests are written FIRST following TDD (RED phase).
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

# Import will fail until we implement the module (RED phase)
try:
    from src.clients.kev_client import KEVClient, KEV_API_URL
except ImportError:
    pass


@pytest.mark.asyncio
async def test_kev_client_creation():
    """
    RED: Test that KEVClient can be created with default timeout.

    Expected behavior:
    - Client should be created successfully
    - Default timeout should be 30 seconds
    """
    client = KEVClient()

    assert client is not None
    assert client.timeout == 30
    assert client.client is not None

    await client.close()


@pytest.mark.asyncio
async def test_kev_custom_timeout():
    """
    RED: Test that custom timeout is applied.

    Expected behavior:
    - Client should accept custom timeout value
    - Timeout should be stored and used
    """
    client = KEVClient(timeout=60)

    assert client.timeout == 60

    await client.close()


@pytest.mark.asyncio
async def test_kev_fetch_catalog_returns_data():
    """
    RED: Test that fetch_kev_catalog returns full KEV catalog data.

    Expected behavior:
    - Returns dict with "vulnerabilities" array
    - Each vulnerability has expected fields
    """
    client = KEVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "title": "CISA Catalog of Known Exploited Vulnerabilities",
        "catalogVersion": "2024.02.09",
        "dateReleased": "2024-02-09T00:00:00.000Z",
        "count": 2,
        "vulnerabilities": [
            {
                "cveID": "CVE-2024-21351",
                "vendorProject": "Microsoft",
                "product": "Windows",
                "vulnerabilityName": "Microsoft Windows SmartScreen Security Feature Bypass Vulnerability",
                "dateAdded": "2024-02-09",
                "shortDescription": "Microsoft Windows SmartScreen contains a security feature bypass vulnerability.",
                "requiredAction": "Apply mitigations per vendor instructions or discontinue use of the product if mitigations are unavailable.",
                "dueDate": "2024-02-16",
                "knownRansomwareCampaignUse": "Known"
            },
            {
                "cveID": "CVE-2024-21412",
                "vendorProject": "Microsoft",
                "product": "Windows",
                "vulnerabilityName": "Microsoft Windows Internet Shortcut Files Security Feature Bypass Vulnerability",
                "dateAdded": "2024-02-09",
                "shortDescription": "Microsoft Windows Internet Shortcut Files contain a security feature bypass vulnerability.",
                "requiredAction": "Apply mitigations per vendor instructions or discontinue use of the product if mitigations are unavailable.",
                "dueDate": "2024-02-16",
                "knownRansomwareCampaignUse": "Unknown"
            }
        ]
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.fetch_kev_catalog()

        mock_get.assert_called_once()
        assert result is not None
        assert "vulnerabilities" in result
        assert len(result["vulnerabilities"]) == 2
        assert result["vulnerabilities"][0]["cveID"] == "CVE-2024-21351"

    await client.close()


@pytest.mark.asyncio
async def test_kev_check_cve_found():
    """
    RED: Test that check_cve returns data when CVE is in KEV catalog.

    Expected behavior:
    - Return dict with is_kev=True and vulnerability details
    - Proper field mapping from raw API response
    """
    client = KEVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "vulnerabilities": [
            {
                "cveID": "CVE-2024-21351",
                "vendorProject": "Microsoft",
                "product": "Windows",
                "vulnerabilityName": "Microsoft Windows SmartScreen Security Feature Bypass Vulnerability",
                "dateAdded": "2024-02-09",
                "shortDescription": "Microsoft Windows SmartScreen contains a security feature bypass vulnerability.",
                "requiredAction": "Apply mitigations per vendor instructions or discontinue use of the product if mitigations are unavailable.",
                "dueDate": "2024-02-16",
                "knownRansomwareCampaignUse": "Known"
            }
        ]
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_cve("CVE-2024-21351")

        assert result is not None
        assert result["is_kev"] is True
        assert result["date_added"] == "2024-02-09"
        assert result["due_date"] == "2024-02-16"
        assert result["required_action"] == "Apply mitigations per vendor instructions or discontinue use of the product if mitigations are unavailable."
        assert result["ransomware_use"] is True
        assert result["vendor"] == "Microsoft"
        assert result["product"] == "Windows"
        assert result["vulnerability_name"] == "Microsoft Windows SmartScreen Security Feature Bypass Vulnerability"

    await client.close()


@pytest.mark.asyncio
async def test_kev_check_cve_not_found():
    """
    RED: Test that check_cve returns None when CVE is not in KEV catalog.

    Expected behavior:
    - Return None for CVE not in KEV
    """
    client = KEVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "vulnerabilities": [
            {
                "cveID": "CVE-2024-21351",
                "vendorProject": "Microsoft",
                "product": "Windows",
                "vulnerabilityName": "Microsoft Windows SmartScreen Security Feature Bypass Vulnerability",
                "dateAdded": "2024-02-09",
                "shortDescription": "Description",
                "requiredAction": "Apply patches",
                "dueDate": "2024-02-16",
                "knownRansomwareCampaignUse": "Known"
            }
        ]
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_cve("CVE-2099-99999")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_kev_batch_check_multiple_cves():
    """
    RED: Test that get_kev_for_cves checks multiple CVEs and returns dict.

    Expected behavior:
    - Return dict mapping CVE ID to KEV data or None
    """
    client = KEVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "vulnerabilities": [
            {
                "cveID": "CVE-2024-21351",
                "vendorProject": "Microsoft",
                "product": "Windows",
                "vulnerabilityName": "Vulnerability 1",
                "dateAdded": "2024-02-09",
                "shortDescription": "Description",
                "requiredAction": "Apply patches",
                "dueDate": "2024-02-16",
                "knownRansomwareCampaignUse": "Known"
            },
            {
                "cveID": "CVE-2024-21412",
                "vendorProject": "Microsoft",
                "product": "Windows",
                "vulnerabilityName": "Vulnerability 2",
                "dateAdded": "2024-02-09",
                "shortDescription": "Description",
                "requiredAction": "Apply patches",
                "dueDate": "2024-02-16",
                "knownRansomwareCampaignUse": "Unknown"
            }
        ]
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_kev_for_cves(["CVE-2024-21351", "CVE-2024-21412", "CVE-2099-99999"])

        assert result is not None
        assert "CVE-2024-21351" in result
        assert "CVE-2024-21412" in result
        assert "CVE-2099-99999" in result

        # Found CVEs should have data
        assert result["CVE-2024-21351"] is not None
        assert result["CVE-2024-21351"]["is_kev"] is True

        assert result["CVE-2024-21412"] is not None
        assert result["CVE-2024-21412"]["is_kev"] is True

        # Not found CVE should be None
        assert result["CVE-2099-99999"] is None

    await client.close()


@pytest.mark.asyncio
async def test_kev_handles_network_error():
    """
    RED: Test that client handles network errors gracefully.

    Expected behavior:
    - When network error occurs, return None
    - No exceptions should propagate
    """
    client = KEVClient()

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await client.fetch_kev_catalog()

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_kev_handles_timeout():
    """
    RED: Test timeout handling.

    Expected behavior:
    - When request times out, return None
    - No exceptions should propagate
    """
    client = KEVClient(timeout=5)

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Request timed out")

        result = await client.fetch_kev_catalog()

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_kev_handles_malformed_response():
    """
    RED: Test handling of malformed API response.

    Expected behavior:
    - When response is malformed, return None
    - No exceptions should propagate
    """
    client = KEVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "unexpected_field": "unexpected_value"
        # Missing "vulnerabilities" field
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.fetch_kev_catalog()

        # Should return the response even if structure is unexpected
        # (let the caller handle missing fields)
        assert result is not None
        assert "vulnerabilities" not in result

    await client.close()


@pytest.mark.asyncio
async def test_kev_handles_server_error():
    """
    RED: Test handling of server error (5xx).

    Expected behavior:
    - When server returns 5xx, return None
    - No exceptions should propagate
    """
    client = KEVClient()

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"error": "Internal Server Error"}

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.fetch_kev_catalog()

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_kev_client_close():
    """
    RED: Test that client can be properly closed.

    Expected behavior:
    - close() should not raise any exceptions
    - Client should be properly closed
    """
    client = KEVClient()

    # Should not raise any exceptions
    await client.close()


@pytest.mark.asyncio
async def test_kev_context_manager():
    """
    RED: Test that client supports async context manager.

    Expected behavior:
    - Client should work with "async with" syntax
    - Client should be automatically closed on exit
    """
    async with KEVClient() as client:
        assert client is not None
        assert client.client is not None

    # After context exit, client should be closed
    # (we can't directly verify this without checking internal state)


@pytest.mark.asyncio
async def test_kev_ransomware_known_maps_to_true():
    """
    RED: Test that "Known" ransomware use maps to True.

    Expected behavior:
    - knownRansomwareCampaignUse: "Known" -> ransomware_use: True
    """
    client = KEVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "vulnerabilities": [
            {
                "cveID": "CVE-2024-21351",
                "vendorProject": "Microsoft",
                "product": "Windows",
                "vulnerabilityName": "Test Vulnerability",
                "dateAdded": "2024-02-09",
                "shortDescription": "Description",
                "requiredAction": "Apply patches",
                "dueDate": "2024-02-16",
                "knownRansomwareCampaignUse": "Known"
            }
        ]
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_cve("CVE-2024-21351")

        assert result is not None
        assert result["ransomware_use"] is True

    await client.close()


@pytest.mark.asyncio
async def test_kev_ransomware_unknown_maps_to_false():
    """
    RED: Test that "Unknown" ransomware use maps to False.

    Expected behavior:
    - knownRansomwareCampaignUse: "Unknown" -> ransomware_use: False
    """
    client = KEVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "vulnerabilities": [
            {
                "cveID": "CVE-2024-21412",
                "vendorProject": "Microsoft",
                "product": "Windows",
                "vulnerabilityName": "Test Vulnerability",
                "dateAdded": "2024-02-09",
                "shortDescription": "Description",
                "requiredAction": "Apply patches",
                "dueDate": "2024-02-16",
                "knownRansomwareCampaignUse": "Unknown"
            }
        ]
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_cve("CVE-2024-21412")

        assert result is not None
        assert result["ransomware_use"] is False

    await client.close()


@pytest.mark.asyncio
async def test_kev_uses_correct_url():
    """
    RED: Test that client uses correct CISA KEV API URL.

    Expected behavior:
    - Client should call the correct CISA KEV feed URL
    """
    client = KEVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"vulnerabilities": []}

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        await client.fetch_kev_catalog()

        # Verify correct URL was called
        mock_get.assert_called_once_with(
            "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
        )

    await client.close()


@pytest.mark.asyncio
async def test_kev_check_cve_with_empty_catalog():
    """
    RED: Test check_cve with empty vulnerabilities array.

    Expected behavior:
    - Return None when catalog is empty
    """
    client = KEVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "vulnerabilities": []
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.check_cve("CVE-2024-21351")

        assert result is None

    await client.close()


@pytest.mark.asyncio
async def test_kev_check_cve_case_insensitive():
    """
    RED: Test that CVE ID check is case-insensitive.

    Expected behavior:
    - CVE-2024-21351 and cve-2024-21351 should both find the same entry
    """
    client = KEVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "vulnerabilities": [
            {
                "cveID": "CVE-2024-21351",
                "vendorProject": "Microsoft",
                "product": "Windows",
                "vulnerabilityName": "Test Vulnerability",
                "dateAdded": "2024-02-09",
                "shortDescription": "Description",
                "requiredAction": "Apply patches",
                "dueDate": "2024-02-16",
                "knownRansomwareCampaignUse": "Known"
            }
        ]
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        # Test lowercase input
        result = await client.check_cve("cve-2024-21351")

        assert result is not None
        assert result["is_kev"] is True

    await client.close()


@pytest.mark.asyncio
async def test_kev_batch_check_returns_empty_dict_on_error():
    """
    RED: Test that get_kev_for_cves handles catalog fetch error gracefully.

    Expected behavior:
    - When catalog fetch fails, return dict with all None values
    """
    client = KEVClient()

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Request timed out")

        result = await client.get_kev_for_cves(["CVE-2024-21351", "CVE-2024-21412"])

        assert result is not None
        assert result["CVE-2024-21351"] is None
        assert result["CVE-2024-21412"] is None

    await client.close()


@pytest.mark.asyncio
async def test_kev_catalog_caching():
    """
    RED: Test that multiple check_cve calls don't refetch catalog unnecessarily.

    Expected behavior:
    - If check_cve is called multiple times, catalog should be fetched only once
    - (This test verifies efficient batch processing within get_kev_for_cves)
    """
    client = KEVClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "vulnerabilities": [
            {
                "cveID": "CVE-2024-21351",
                "vendorProject": "Microsoft",
                "product": "Windows",
                "vulnerabilityName": "Test Vulnerability",
                "dateAdded": "2024-02-09",
                "shortDescription": "Description",
                "requiredAction": "Apply patches",
                "dueDate": "2024-02-16",
                "knownRansomwareCampaignUse": "Known"
            }
        ]
    }

    with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        # Call get_kev_for_cves which should only fetch once
        await client.get_kev_for_cves(["CVE-2024-21351", "CVE-2024-21412", "CVE-2024-21413"])

        # Should only call API once (not 3 times)
        assert mock_get.call_count == 1

    await client.close()
