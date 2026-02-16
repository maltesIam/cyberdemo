"""Unit tests for EDR Trigger Handlers.

Tests the EDR-related trigger handlers that respond to
detection and containment events.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.triggers.edr.detection_high_severity import DetectionHighSeverityTrigger
from src.triggers.edr.hash_propagation import HashPropagationTrigger
from src.triggers.edr.containment_failed import ContainmentFailedTrigger
from src.triggers.edr.containment_completed import ContainmentCompletedTrigger
from src.triggers.edr.containment_lifted import ContainmentLiftedTrigger
from src.triggers.gateway_client import GatewayClient


class TestDetectionHighSeverityTrigger:
    """Tests for DetectionHighSeverityTrigger handler."""

    @pytest.fixture
    def mock_gateway(self):
        gateway = MagicMock(spec=GatewayClient)
        gateway.send_command = AsyncMock(return_value=MagicMock(success=True))
        return gateway

    @pytest.fixture
    def trigger(self, mock_gateway):
        return DetectionHighSeverityTrigger(gateway=mock_gateway)

    def test_should_trigger_for_high_severity(self, trigger):
        """Test: High severity detections should trigger."""
        event = {
            "detection_id": "DET-001",
            "severity": "high",
            "host_id": "WS-FIN-042",
            "hash": "abc123def456"
        }
        assert trigger.should_trigger(event) is True

    def test_should_trigger_for_critical_severity(self, trigger):
        """Test: Critical severity detections should trigger."""
        event = {
            "detection_id": "DET-002",
            "severity": "critical",
            "host_id": "SRV-DC-01",
            "hash": "def456abc123"
        }
        assert trigger.should_trigger(event) is True

    def test_should_not_trigger_for_medium_severity(self, trigger):
        """Test: Medium severity detections should NOT trigger."""
        event = {
            "detection_id": "DET-003",
            "severity": "medium",
            "host_id": "WS-DEV-005",
            "hash": "xyz789"
        }
        assert trigger.should_trigger(event) is False

    @pytest.mark.asyncio
    async def test_handle_sends_investigate_command(self, trigger, mock_gateway):
        """Test: High severity detections send /investigate command."""
        event = {
            "detection_id": "DET-001",
            "severity": "high",
            "host_id": "WS-FIN-042",
            "hash": "abc123def456"
        }

        await trigger.handle(event)

        mock_gateway.send_command.assert_called_once()
        call_args = mock_gateway.send_command.call_args
        assert "/investigate" in call_args.kwargs["command"]


class TestHashPropagationTrigger:
    """Tests for HashPropagationTrigger handler."""

    @pytest.fixture
    def mock_gateway(self):
        gateway = MagicMock(spec=GatewayClient)
        gateway.send_command = AsyncMock(return_value=MagicMock(success=True))
        return gateway

    @pytest.fixture
    def trigger(self, mock_gateway):
        return HashPropagationTrigger(gateway=mock_gateway)

    def test_should_trigger_for_propagation_threshold(self, trigger):
        """Test: Hash seen on 3+ hosts should trigger /hunt."""
        event = {
            "hash": "abc123def456",
            "hosts_affected": ["WS-001", "WS-002", "WS-003"],
            "propagation_count": 3,
            "first_seen": datetime.now().isoformat()
        }
        assert trigger.should_trigger(event) is True

    def test_should_not_trigger_below_threshold(self, trigger):
        """Test: Hash on fewer than 3 hosts should NOT trigger."""
        event = {
            "hash": "abc123def456",
            "hosts_affected": ["WS-001", "WS-002"],
            "propagation_count": 2,
            "first_seen": datetime.now().isoformat()
        }
        assert trigger.should_trigger(event) is False

    @pytest.mark.asyncio
    async def test_handle_sends_hunt_command(self, trigger, mock_gateway):
        """Test: Hash propagation sends /hunt command."""
        event = {
            "hash": "abc123def456",
            "hosts_affected": ["WS-001", "WS-002", "WS-003"],
            "propagation_count": 3,
            "first_seen": datetime.now().isoformat()
        }

        await trigger.handle(event)

        mock_gateway.send_command.assert_called_once()
        call_args = mock_gateway.send_command.call_args
        assert "/hunt" in call_args.kwargs["command"]


class TestContainmentFailedTrigger:
    """Tests for ContainmentFailedTrigger handler."""

    @pytest.fixture
    def mock_gateway(self):
        gateway = MagicMock(spec=GatewayClient)
        gateway.send_command = AsyncMock(return_value=MagicMock(success=True))
        return gateway

    @pytest.fixture
    def trigger(self, mock_gateway):
        return ContainmentFailedTrigger(gateway=mock_gateway)

    @pytest.mark.asyncio
    async def test_handle_sends_retry_command(self, trigger, mock_gateway):
        """Test: Containment failure sends /retry command."""
        event = {
            "host_id": "WS-FIN-042",
            "containment_id": "CON-001",
            "failure_reason": "Host unreachable",
            "attempt_count": 1
        }

        await trigger.handle(event)

        mock_gateway.send_command.assert_called_once()
        call_args = mock_gateway.send_command.call_args
        assert "/retry" in call_args.kwargs["command"]


class TestContainmentCompletedTrigger:
    """Tests for ContainmentCompletedTrigger handler."""

    @pytest.fixture
    def mock_gateway(self):
        gateway = MagicMock(spec=GatewayClient)
        gateway.send_command = AsyncMock(return_value=MagicMock(success=True))
        return gateway

    @pytest.fixture
    def trigger(self, mock_gateway):
        return ContainmentCompletedTrigger(gateway=mock_gateway)

    @pytest.mark.asyncio
    async def test_handle_sends_status_update(self, trigger, mock_gateway):
        """Test: Containment completion sends status update command."""
        event = {
            "host_id": "WS-FIN-042",
            "containment_id": "CON-001",
            "completed_at": datetime.now().isoformat(),
            "duration_seconds": 45
        }

        await trigger.handle(event)

        mock_gateway.send_command.assert_called_once()


class TestContainmentLiftedTrigger:
    """Tests for ContainmentLiftedTrigger handler."""

    @pytest.fixture
    def mock_gateway(self):
        gateway = MagicMock(spec=GatewayClient)
        gateway.send_command = AsyncMock(return_value=MagicMock(success=True))
        return gateway

    @pytest.fixture
    def trigger(self, mock_gateway):
        return ContainmentLiftedTrigger(gateway=mock_gateway)

    @pytest.mark.asyncio
    async def test_handle_sends_lift_confirmation(self, trigger, mock_gateway):
        """Test: Containment lift sends confirmation command."""
        event = {
            "host_id": "WS-FIN-042",
            "containment_id": "CON-001",
            "lifted_at": datetime.now().isoformat(),
            "lifted_by": "analyst@company.com",
            "reason": "Incident resolved, host clean"
        }

        await trigger.handle(event)

        mock_gateway.send_command.assert_called_once()
