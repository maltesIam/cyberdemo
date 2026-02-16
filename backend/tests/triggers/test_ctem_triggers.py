"""Tests for CTEM-related trigger handlers.

RED Phase: These tests define the expected behavior before implementation.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from src.triggers import TriggerEvent, GatewayClient
from src.triggers.ctem import (
    CriticalVulnerabilityTrigger,
    AssetRiskChangedTrigger,
    VIPAssetVulnerabilityTrigger,
    ExploitAvailableTrigger,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_gateway_client():
    """Create a mock gateway client."""
    client = MagicMock(spec=GatewayClient)
    client.send_command = AsyncMock(return_value={"status": "accepted"})
    client.is_connected = True
    return client


@pytest.fixture
def base_timestamp():
    """Provide a consistent timestamp for tests."""
    return datetime(2024, 2, 14, 10, 30, 0)


# ============================================================================
# CriticalVulnerabilityTrigger Tests
# ============================================================================

class TestCriticalVulnerabilityTrigger:
    """Tests for critical vulnerability detection trigger."""

    def test_trigger_name(self, mock_gateway_client):
        """Test that trigger has correct name."""
        trigger = CriticalVulnerabilityTrigger(mock_gateway_client)
        assert trigger.trigger_name == "critical_vulnerability"

    def test_description(self, mock_gateway_client):
        """Test that trigger has meaningful description."""
        trigger = CriticalVulnerabilityTrigger(mock_gateway_client)
        assert "critical" in trigger.description.lower()
        assert "vulnerability" in trigger.description.lower() or "CVE" in trigger.description

    def test_event_types(self, mock_gateway_client):
        """Test that trigger responds to correct event types."""
        trigger = CriticalVulnerabilityTrigger(mock_gateway_client)
        assert "ctem.vulnerability.new" in trigger.event_types

    def test_should_trigger_for_critical_cve(self, mock_gateway_client, base_timestamp):
        """Test trigger fires for critical CVE."""
        trigger = CriticalVulnerabilityTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.vulnerability.new",
            source="vulnerability_scanner",
            timestamp=base_timestamp,
            data={
                "cve_id": "CVE-2024-0001",
                "cvss_score": 9.8,
                "severity": "critical",
                "affected_assets": ["server-001", "server-002"],
                "has_exploit": False,
            },
            severity="critical",
        )
        assert trigger.should_trigger(event) is True

    def test_should_trigger_for_high_cvss(self, mock_gateway_client, base_timestamp):
        """Test trigger fires for high CVSS score (>=9.0)."""
        trigger = CriticalVulnerabilityTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.vulnerability.new",
            source="vulnerability_scanner",
            timestamp=base_timestamp,
            data={
                "cve_id": "CVE-2024-0002",
                "cvss_score": 9.1,
                "severity": "critical",
                "affected_assets": ["db-server"],
            },
        )
        assert trigger.should_trigger(event) is True

    def test_should_not_trigger_for_low_cvss(self, mock_gateway_client, base_timestamp):
        """Test trigger does not fire for low CVSS score."""
        trigger = CriticalVulnerabilityTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.vulnerability.new",
            source="vulnerability_scanner",
            timestamp=base_timestamp,
            data={
                "cve_id": "CVE-2024-0003",
                "cvss_score": 4.5,
                "severity": "medium",
                "affected_assets": ["workstation-001"],
            },
        )
        assert trigger.should_trigger(event) is False

    def test_should_not_trigger_for_high_but_not_critical(self, mock_gateway_client, base_timestamp):
        """Test trigger does not fire for high (but not critical) CVSS."""
        trigger = CriticalVulnerabilityTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.vulnerability.new",
            source="vulnerability_scanner",
            timestamp=base_timestamp,
            data={
                "cve_id": "CVE-2024-0004",
                "cvss_score": 7.5,
                "severity": "high",
                "affected_assets": ["server-003"],
            },
        )
        assert trigger.should_trigger(event) is False

    def test_get_command(self, mock_gateway_client, base_timestamp):
        """Test correct command is generated."""
        trigger = CriticalVulnerabilityTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.vulnerability.new",
            source="vulnerability_scanner",
            timestamp=base_timestamp,
            data={
                "cve_id": "CVE-2024-0001",
                "cvss_score": 9.8,
                "severity": "critical",
                "affected_assets": ["server-001"],
            },
        )
        command = trigger.get_command(event)
        assert "/assess-vuln" in command
        assert "CVE-2024-0001" in command

    @pytest.mark.asyncio
    async def test_process_sends_command(self, mock_gateway_client, base_timestamp):
        """Test that processing triggers command to gateway."""
        trigger = CriticalVulnerabilityTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.vulnerability.new",
            source="vulnerability_scanner",
            timestamp=base_timestamp,
            data={
                "cve_id": "CVE-2024-0001",
                "cvss_score": 9.8,
                "severity": "critical",
                "affected_assets": ["server-001"],
            },
            severity="critical",
        )
        result = await trigger.process(event)
        assert result.triggered is True
        mock_gateway_client.send_command.assert_called_once()


# ============================================================================
# AssetRiskChangedTrigger Tests
# ============================================================================

class TestAssetRiskChangedTrigger:
    """Tests for asset risk level change trigger."""

    def test_trigger_name(self, mock_gateway_client):
        """Test that trigger has correct name."""
        trigger = AssetRiskChangedTrigger(mock_gateway_client)
        assert trigger.trigger_name == "asset_risk_changed"

    def test_event_types(self, mock_gateway_client):
        """Test that trigger responds to correct event types."""
        trigger = AssetRiskChangedTrigger(mock_gateway_client)
        assert "ctem.asset.risk_changed" in trigger.event_types

    def test_should_trigger_for_change_to_red(self, mock_gateway_client, base_timestamp):
        """Test trigger fires when risk changes to Red."""
        trigger = AssetRiskChangedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.asset.risk_changed",
            source="risk_calculator",
            timestamp=base_timestamp,
            data={
                "asset_id": "server-001",
                "asset_name": "Production Database",
                "previous_risk": "Yellow",
                "new_risk": "Red",
                "risk_factors": ["critical_vuln", "internet_exposed"],
            },
            severity="high",
        )
        assert trigger.should_trigger(event) is True

    def test_should_trigger_for_change_from_green_to_red(self, mock_gateway_client, base_timestamp):
        """Test trigger fires when risk changes from Green to Red."""
        trigger = AssetRiskChangedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.asset.risk_changed",
            source="risk_calculator",
            timestamp=base_timestamp,
            data={
                "asset_id": "workstation-055",
                "asset_name": "CFO Workstation",
                "previous_risk": "Green",
                "new_risk": "Red",
                "risk_factors": ["malware_detected"],
            },
            severity="critical",
        )
        assert trigger.should_trigger(event) is True

    def test_should_not_trigger_for_change_to_yellow(self, mock_gateway_client, base_timestamp):
        """Test trigger does not fire for change to Yellow."""
        trigger = AssetRiskChangedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.asset.risk_changed",
            source="risk_calculator",
            timestamp=base_timestamp,
            data={
                "asset_id": "server-002",
                "asset_name": "Dev Server",
                "previous_risk": "Green",
                "new_risk": "Yellow",
                "risk_factors": ["outdated_software"],
            },
        )
        assert trigger.should_trigger(event) is False

    def test_should_not_trigger_for_improvement(self, mock_gateway_client, base_timestamp):
        """Test trigger does not fire when risk improves."""
        trigger = AssetRiskChangedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.asset.risk_changed",
            source="risk_calculator",
            timestamp=base_timestamp,
            data={
                "asset_id": "server-003",
                "asset_name": "Staging Server",
                "previous_risk": "Red",
                "new_risk": "Yellow",
                "risk_factors": ["patched_vulnerabilities"],
            },
        )
        assert trigger.should_trigger(event) is False

    def test_get_command(self, mock_gateway_client, base_timestamp):
        """Test correct command is generated."""
        trigger = AssetRiskChangedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.asset.risk_changed",
            source="risk_calculator",
            timestamp=base_timestamp,
            data={
                "asset_id": "server-001",
                "asset_name": "Production Database",
                "previous_risk": "Yellow",
                "new_risk": "Red",
            },
        )
        command = trigger.get_command(event)
        assert "/assess-vuln" in command


# ============================================================================
# VIPAssetVulnerabilityTrigger Tests
# ============================================================================

class TestVIPAssetVulnerabilityTrigger:
    """Tests for VIP asset vulnerability trigger."""

    def test_trigger_name(self, mock_gateway_client):
        """Test that trigger has correct name."""
        trigger = VIPAssetVulnerabilityTrigger(mock_gateway_client)
        assert trigger.trigger_name == "vip_asset_vulnerability"

    def test_event_types(self, mock_gateway_client):
        """Test that trigger responds to correct event types."""
        trigger = VIPAssetVulnerabilityTrigger(mock_gateway_client)
        assert "ctem.vulnerability.new" in trigger.event_types

    def test_should_trigger_for_vip_with_any_vuln(self, mock_gateway_client, base_timestamp):
        """Test trigger fires for any vulnerability on VIP asset."""
        trigger = VIPAssetVulnerabilityTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.vulnerability.new",
            source="vulnerability_scanner",
            timestamp=base_timestamp,
            data={
                "cve_id": "CVE-2024-0010",
                "cvss_score": 6.5,  # Medium, but VIP asset
                "severity": "medium",
                "affected_assets": ["ceo-laptop"],
                "asset_classification": "vip",
            },
            severity="medium",
        )
        assert trigger.should_trigger(event) is True

    def test_should_trigger_for_critical_infrastructure(self, mock_gateway_client, base_timestamp):
        """Test trigger fires for critical infrastructure vulnerability."""
        trigger = VIPAssetVulnerabilityTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.vulnerability.new",
            source="vulnerability_scanner",
            timestamp=base_timestamp,
            data={
                "cve_id": "CVE-2024-0011",
                "cvss_score": 5.0,
                "severity": "medium",
                "affected_assets": ["domain-controller-01"],
                "asset_classification": "critical_infrastructure",
            },
        )
        assert trigger.should_trigger(event) is True

    def test_should_not_trigger_for_standard_asset(self, mock_gateway_client, base_timestamp):
        """Test trigger does not fire for standard (non-VIP) asset."""
        trigger = VIPAssetVulnerabilityTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.vulnerability.new",
            source="vulnerability_scanner",
            timestamp=base_timestamp,
            data={
                "cve_id": "CVE-2024-0012",
                "cvss_score": 6.5,
                "severity": "medium",
                "affected_assets": ["workstation-100"],
                "asset_classification": "standard",
            },
        )
        assert trigger.should_trigger(event) is False

    def test_get_command_includes_vip_flag(self, mock_gateway_client, base_timestamp):
        """Test command indicates VIP asset."""
        trigger = VIPAssetVulnerabilityTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.vulnerability.new",
            source="vulnerability_scanner",
            timestamp=base_timestamp,
            data={
                "cve_id": "CVE-2024-0010",
                "cvss_score": 6.5,
                "affected_assets": ["ceo-laptop"],
                "asset_classification": "vip",
            },
        )
        command = trigger.get_command(event)
        assert "/assess-vuln" in command

    @pytest.mark.asyncio
    async def test_process_sends_command(self, mock_gateway_client, base_timestamp):
        """Test that processing triggers command to gateway."""
        trigger = VIPAssetVulnerabilityTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.vulnerability.new",
            source="vulnerability_scanner",
            timestamp=base_timestamp,
            data={
                "cve_id": "CVE-2024-0010",
                "cvss_score": 6.5,
                "affected_assets": ["ceo-laptop"],
                "asset_classification": "vip",
            },
            severity="medium",
        )
        result = await trigger.process(event)
        assert result.triggered is True
        mock_gateway_client.send_command.assert_called_once()


# ============================================================================
# ExploitAvailableTrigger Tests
# ============================================================================

class TestExploitAvailableTrigger:
    """Tests for exploit availability trigger."""

    def test_trigger_name(self, mock_gateway_client):
        """Test that trigger has correct name."""
        trigger = ExploitAvailableTrigger(mock_gateway_client)
        assert trigger.trigger_name == "exploit_available"

    def test_event_types(self, mock_gateway_client):
        """Test that trigger responds to correct event types."""
        trigger = ExploitAvailableTrigger(mock_gateway_client)
        assert "ctem.exploit.available" in trigger.event_types

    def test_should_trigger_for_public_exploit(self, mock_gateway_client, base_timestamp):
        """Test trigger fires when public exploit becomes available."""
        trigger = ExploitAvailableTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.exploit.available",
            source="exploit_db",
            timestamp=base_timestamp,
            data={
                "cve_id": "CVE-2024-0020",
                "exploit_type": "public",
                "exploit_source": "exploit-db",
                "affected_assets": ["web-server-01", "web-server-02"],
                "exploit_maturity": "functional",
            },
            severity="high",
        )
        assert trigger.should_trigger(event) is True

    def test_should_trigger_for_weaponized_exploit(self, mock_gateway_client, base_timestamp):
        """Test trigger fires for weaponized exploit."""
        trigger = ExploitAvailableTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.exploit.available",
            source="threat_intel",
            timestamp=base_timestamp,
            data={
                "cve_id": "CVE-2024-0021",
                "exploit_type": "weaponized",
                "exploit_source": "in_the_wild",
                "affected_assets": ["app-server-01"],
                "exploit_maturity": "weaponized",
            },
            severity="critical",
        )
        assert trigger.should_trigger(event) is True

    def test_should_trigger_for_poc_exploit(self, mock_gateway_client, base_timestamp):
        """Test trigger fires for proof-of-concept exploit."""
        trigger = ExploitAvailableTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.exploit.available",
            source="github",
            timestamp=base_timestamp,
            data={
                "cve_id": "CVE-2024-0022",
                "exploit_type": "poc",
                "exploit_source": "github",
                "affected_assets": ["db-server-01"],
                "exploit_maturity": "proof_of_concept",
            },
        )
        assert trigger.should_trigger(event) is True

    def test_should_not_trigger_if_no_affected_assets(self, mock_gateway_client, base_timestamp):
        """Test trigger does not fire if no assets are affected."""
        trigger = ExploitAvailableTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.exploit.available",
            source="exploit_db",
            timestamp=base_timestamp,
            data={
                "cve_id": "CVE-2024-0023",
                "exploit_type": "public",
                "exploit_source": "exploit-db",
                "affected_assets": [],  # No affected assets
                "exploit_maturity": "functional",
            },
        )
        assert trigger.should_trigger(event) is False

    def test_get_command(self, mock_gateway_client, base_timestamp):
        """Test correct command is generated."""
        trigger = ExploitAvailableTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.exploit.available",
            source="exploit_db",
            timestamp=base_timestamp,
            data={
                "cve_id": "CVE-2024-0020",
                "exploit_type": "public",
                "affected_assets": ["web-server-01"],
            },
        )
        command = trigger.get_command(event)
        assert "/assess-vuln" in command
        assert "CVE-2024-0020" in command

    @pytest.mark.asyncio
    async def test_process_sends_command(self, mock_gateway_client, base_timestamp):
        """Test that processing triggers command to gateway."""
        trigger = ExploitAvailableTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="ctem.exploit.available",
            source="exploit_db",
            timestamp=base_timestamp,
            data={
                "cve_id": "CVE-2024-0020",
                "exploit_type": "public",
                "affected_assets": ["web-server-01"],
                "exploit_maturity": "functional",
            },
            severity="high",
        )
        result = await trigger.process(event)
        assert result.triggered is True
        mock_gateway_client.send_command.assert_called_once()
