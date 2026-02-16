"""Tests for Intel-related trigger handlers.

RED Phase: These tests define the expected behavior before implementation.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from src.triggers import TriggerEvent, GatewayClient
from src.triggers.intel import (
    NewMaliciousIOCTrigger,
    IOCScoreChangedTrigger,
    IOCMatchNetworkTrigger,
    NewIntelFeedTrigger,
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
# NewMaliciousIOCTrigger Tests
# ============================================================================

class TestNewMaliciousIOCTrigger:
    """Tests for new malicious IOC detection trigger."""

    def test_trigger_name(self, mock_gateway_client):
        """Test that trigger has correct name."""
        trigger = NewMaliciousIOCTrigger(mock_gateway_client)
        assert trigger.trigger_name == "new_malicious_ioc"

    def test_description(self, mock_gateway_client):
        """Test that trigger has meaningful description."""
        trigger = NewMaliciousIOCTrigger(mock_gateway_client)
        assert "malicious" in trigger.description.lower()
        assert "IOC" in trigger.description

    def test_event_types(self, mock_gateway_client):
        """Test that trigger responds to correct event types."""
        trigger = NewMaliciousIOCTrigger(mock_gateway_client)
        assert "intel.ioc.new" in trigger.event_types

    def test_should_trigger_for_malicious_ioc(self, mock_gateway_client, base_timestamp):
        """Test trigger fires for malicious IOC with high confidence."""
        trigger = NewMaliciousIOCTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.ioc.new",
            source="threat_intel_platform",
            timestamp=base_timestamp,
            data={
                "ioc_type": "ip",
                "ioc_value": "192.168.1.100",
                "classification": "malicious",
                "confidence": 95,
                "threat_type": "c2_server",
            },
            severity="high",
        )
        assert trigger.should_trigger(event) is True

    def test_should_not_trigger_for_benign_ioc(self, mock_gateway_client, base_timestamp):
        """Test trigger does not fire for benign IOC."""
        trigger = NewMaliciousIOCTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.ioc.new",
            source="threat_intel_platform",
            timestamp=base_timestamp,
            data={
                "ioc_type": "ip",
                "ioc_value": "8.8.8.8",
                "classification": "benign",
                "confidence": 99,
            },
            severity="low",
        )
        assert trigger.should_trigger(event) is False

    def test_should_not_trigger_for_low_confidence(self, mock_gateway_client, base_timestamp):
        """Test trigger does not fire for low confidence malicious IOC."""
        trigger = NewMaliciousIOCTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.ioc.new",
            source="threat_intel_platform",
            timestamp=base_timestamp,
            data={
                "ioc_type": "ip",
                "ioc_value": "10.0.0.1",
                "classification": "malicious",
                "confidence": 30,  # Below threshold
            },
            severity="low",
        )
        assert trigger.should_trigger(event) is False

    def test_get_command(self, mock_gateway_client, base_timestamp):
        """Test correct command is generated."""
        trigger = NewMaliciousIOCTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.ioc.new",
            source="threat_intel_platform",
            timestamp=base_timestamp,
            data={
                "ioc_type": "ip",
                "ioc_value": "192.168.1.100",
                "classification": "malicious",
                "confidence": 95,
            },
        )
        command = trigger.get_command(event)
        assert "/check-intel" in command
        assert "192.168.1.100" in command

    @pytest.mark.asyncio
    async def test_process_sends_command(self, mock_gateway_client, base_timestamp):
        """Test that processing triggers command to gateway."""
        trigger = NewMaliciousIOCTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.ioc.new",
            source="threat_intel_platform",
            timestamp=base_timestamp,
            data={
                "ioc_type": "ip",
                "ioc_value": "192.168.1.100",
                "classification": "malicious",
                "confidence": 95,
            },
            severity="high",
        )
        result = await trigger.process(event)
        assert result.triggered is True
        mock_gateway_client.send_command.assert_called_once()


# ============================================================================
# IOCScoreChangedTrigger Tests
# ============================================================================

class TestIOCScoreChangedTrigger:
    """Tests for IOC score change trigger."""

    def test_trigger_name(self, mock_gateway_client):
        """Test that trigger has correct name."""
        trigger = IOCScoreChangedTrigger(mock_gateway_client)
        assert trigger.trigger_name == "ioc_score_changed"

    def test_event_types(self, mock_gateway_client):
        """Test that trigger responds to correct event types."""
        trigger = IOCScoreChangedTrigger(mock_gateway_client)
        assert "intel.ioc.score_changed" in trigger.event_types

    def test_should_trigger_for_significant_increase(self, mock_gateway_client, base_timestamp):
        """Test trigger fires when score increases significantly."""
        trigger = IOCScoreChangedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.ioc.score_changed",
            source="threat_intel_platform",
            timestamp=base_timestamp,
            data={
                "ioc_value": "malware.example.com",
                "previous_score": 40,
                "new_score": 85,  # Significant increase
                "ioc_type": "domain",
            },
        )
        assert trigger.should_trigger(event) is True

    def test_should_not_trigger_for_minor_increase(self, mock_gateway_client, base_timestamp):
        """Test trigger does not fire for minor score change."""
        trigger = IOCScoreChangedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.ioc.score_changed",
            source="threat_intel_platform",
            timestamp=base_timestamp,
            data={
                "ioc_value": "example.com",
                "previous_score": 40,
                "new_score": 45,  # Minor increase
                "ioc_type": "domain",
            },
        )
        assert trigger.should_trigger(event) is False

    def test_should_not_trigger_for_score_decrease(self, mock_gateway_client, base_timestamp):
        """Test trigger does not fire when score decreases."""
        trigger = IOCScoreChangedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.ioc.score_changed",
            source="threat_intel_platform",
            timestamp=base_timestamp,
            data={
                "ioc_value": "example.com",
                "previous_score": 80,
                "new_score": 60,  # Decrease
                "ioc_type": "domain",
            },
        )
        assert trigger.should_trigger(event) is False

    def test_get_command(self, mock_gateway_client, base_timestamp):
        """Test correct command is generated."""
        trigger = IOCScoreChangedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.ioc.score_changed",
            source="threat_intel_platform",
            timestamp=base_timestamp,
            data={
                "ioc_value": "malware.example.com",
                "previous_score": 40,
                "new_score": 85,
                "ioc_type": "domain",
            },
        )
        command = trigger.get_command(event)
        assert "/check-intel" in command


# ============================================================================
# IOCMatchNetworkTrigger Tests
# ============================================================================

class TestIOCMatchNetworkTrigger:
    """Tests for IOC found in network traffic trigger."""

    def test_trigger_name(self, mock_gateway_client):
        """Test that trigger has correct name."""
        trigger = IOCMatchNetworkTrigger(mock_gateway_client)
        assert trigger.trigger_name == "ioc_match_network"

    def test_event_types(self, mock_gateway_client):
        """Test that trigger responds to correct event types."""
        trigger = IOCMatchNetworkTrigger(mock_gateway_client)
        assert "intel.ioc.network_match" in trigger.event_types

    def test_should_trigger_for_high_severity_match(self, mock_gateway_client, base_timestamp):
        """Test trigger fires for high severity network IOC match."""
        trigger = IOCMatchNetworkTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.ioc.network_match",
            source="network_monitor",
            timestamp=base_timestamp,
            data={
                "ioc_value": "192.168.1.100",
                "ioc_type": "ip",
                "match_type": "outbound_connection",
                "source_host": "workstation-001",
                "threat_score": 90,
            },
            severity="high",
        )
        assert trigger.should_trigger(event) is True

    def test_should_trigger_for_known_malicious_domain(self, mock_gateway_client, base_timestamp):
        """Test trigger fires for known malicious domain in network."""
        trigger = IOCMatchNetworkTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.ioc.network_match",
            source="dns_monitor",
            timestamp=base_timestamp,
            data={
                "ioc_value": "c2-server.malicious.com",
                "ioc_type": "domain",
                "match_type": "dns_query",
                "source_host": "server-002",
                "threat_score": 95,
            },
            severity="critical",
        )
        assert trigger.should_trigger(event) is True

    def test_should_not_trigger_for_low_threat_score(self, mock_gateway_client, base_timestamp):
        """Test trigger does not fire for low threat score match."""
        trigger = IOCMatchNetworkTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.ioc.network_match",
            source="network_monitor",
            timestamp=base_timestamp,
            data={
                "ioc_value": "10.0.0.1",
                "ioc_type": "ip",
                "match_type": "outbound_connection",
                "source_host": "workstation-001",
                "threat_score": 20,  # Low threat score
            },
            severity="low",
        )
        assert trigger.should_trigger(event) is False

    def test_get_command_includes_source_host(self, mock_gateway_client, base_timestamp):
        """Test command includes source host information."""
        trigger = IOCMatchNetworkTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.ioc.network_match",
            source="network_monitor",
            timestamp=base_timestamp,
            data={
                "ioc_value": "192.168.1.100",
                "ioc_type": "ip",
                "match_type": "outbound_connection",
                "source_host": "workstation-001",
                "threat_score": 90,
            },
        )
        command = trigger.get_command(event)
        assert "/check-intel" in command


# ============================================================================
# NewIntelFeedTrigger Tests
# ============================================================================

class TestNewIntelFeedTrigger:
    """Tests for new threat intelligence feed trigger."""

    def test_trigger_name(self, mock_gateway_client):
        """Test that trigger has correct name."""
        trigger = NewIntelFeedTrigger(mock_gateway_client)
        assert trigger.trigger_name == "new_intel_feed"

    def test_event_types(self, mock_gateway_client):
        """Test that trigger responds to correct event types."""
        trigger = NewIntelFeedTrigger(mock_gateway_client)
        assert "intel.feed.new" in trigger.event_types

    def test_should_trigger_for_high_priority_feed(self, mock_gateway_client, base_timestamp):
        """Test trigger fires for high priority threat feed."""
        trigger = NewIntelFeedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.feed.new",
            source="threat_intel_platform",
            timestamp=base_timestamp,
            data={
                "feed_name": "APT-Activity-2024",
                "feed_type": "tactical",
                "priority": "high",
                "ioc_count": 150,
                "relevance_score": 85,
            },
        )
        assert trigger.should_trigger(event) is True

    def test_should_trigger_for_urgent_industry_feed(self, mock_gateway_client, base_timestamp):
        """Test trigger fires for urgent industry-relevant feed."""
        trigger = NewIntelFeedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.feed.new",
            source="isac",
            timestamp=base_timestamp,
            data={
                "feed_name": "Financial-Sector-Alert",
                "feed_type": "industry",
                "priority": "urgent",
                "ioc_count": 50,
                "relevance_score": 95,
            },
            severity="critical",
        )
        assert trigger.should_trigger(event) is True

    def test_should_not_trigger_for_low_priority_feed(self, mock_gateway_client, base_timestamp):
        """Test trigger does not fire for low priority feed."""
        trigger = NewIntelFeedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.feed.new",
            source="threat_intel_platform",
            timestamp=base_timestamp,
            data={
                "feed_name": "General-IOC-Update",
                "feed_type": "general",
                "priority": "low",
                "ioc_count": 10,
                "relevance_score": 30,
            },
        )
        assert trigger.should_trigger(event) is False

    def test_should_not_trigger_for_low_relevance(self, mock_gateway_client, base_timestamp):
        """Test trigger does not fire for low relevance feed."""
        trigger = NewIntelFeedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.feed.new",
            source="threat_intel_platform",
            timestamp=base_timestamp,
            data={
                "feed_name": "Some-Feed",
                "feed_type": "general",
                "priority": "medium",
                "ioc_count": 5,
                "relevance_score": 25,
            },
        )
        assert trigger.should_trigger(event) is False

    def test_get_command(self, mock_gateway_client, base_timestamp):
        """Test correct command is generated."""
        trigger = NewIntelFeedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.feed.new",
            source="threat_intel_platform",
            timestamp=base_timestamp,
            data={
                "feed_name": "APT-Activity-2024",
                "feed_type": "tactical",
                "priority": "high",
                "ioc_count": 150,
            },
        )
        command = trigger.get_command(event)
        assert "/check-intel" in command

    @pytest.mark.asyncio
    async def test_process_sends_command(self, mock_gateway_client, base_timestamp):
        """Test that processing triggers command to gateway."""
        trigger = NewIntelFeedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="intel.feed.new",
            source="threat_intel_platform",
            timestamp=base_timestamp,
            data={
                "feed_name": "APT-Activity-2024",
                "feed_type": "tactical",
                "priority": "high",
                "ioc_count": 150,
                "relevance_score": 85,
            },
        )
        result = await trigger.process(event)
        assert result.triggered is True
        mock_gateway_client.send_command.assert_called_once()
