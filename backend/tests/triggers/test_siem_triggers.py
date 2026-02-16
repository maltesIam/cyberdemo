"""Unit tests for SIEM Trigger Handlers.

Tests the SIEM-related trigger handlers that respond to
incident events and send appropriate commands.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.triggers.siem.incident_created import IncidentCreatedTrigger
from src.triggers.siem.incident_escalated import IncidentEscalatedTrigger
from src.triggers.siem.sla_breach import SLABreachTrigger
from src.triggers.siem.correlation_found import CorrelationFoundTrigger
from src.triggers.siem.incident_reopened import IncidentReopenedTrigger
from src.triggers.gateway_client import GatewayClient


class TestIncidentCreatedTrigger:
    """Tests for IncidentCreatedTrigger handler."""

    @pytest.fixture
    def mock_gateway(self):
        """Create mock gateway client."""
        gateway = MagicMock(spec=GatewayClient)
        gateway.send_command = AsyncMock(return_value=MagicMock(success=True))
        return gateway

    @pytest.fixture
    def trigger(self, mock_gateway):
        """Create trigger with mock gateway."""
        return IncidentCreatedTrigger(gateway=mock_gateway)

    def test_should_trigger_for_high_severity(self, trigger):
        """Test: High severity incidents should trigger /investigate."""
        event = {
            "incident_id": "INC-001",
            "severity": "high",
            "status": "new",
            "title": "Suspicious Activity Detected"
        }
        assert trigger.should_trigger(event) is True

    def test_should_trigger_for_critical_severity(self, trigger):
        """Test: Critical severity incidents should trigger /investigate."""
        event = {
            "incident_id": "INC-002",
            "severity": "critical",
            "status": "new",
            "title": "Active Breach Detected"
        }
        assert trigger.should_trigger(event) is True

    def test_should_not_trigger_for_low_severity(self, trigger):
        """Test: Low severity incidents should NOT trigger."""
        event = {
            "incident_id": "INC-003",
            "severity": "low",
            "status": "new",
            "title": "Information Event"
        }
        assert trigger.should_trigger(event) is False

    @pytest.mark.asyncio
    async def test_handle_sends_investigate_command(self, trigger, mock_gateway):
        """Test: High/critical incidents send /investigate command."""
        event = {
            "incident_id": "INC-001",
            "severity": "high",
            "status": "new",
            "title": "Suspicious Activity Detected"
        }

        await trigger.handle(event)

        mock_gateway.send_command.assert_called_once()
        call_args = mock_gateway.send_command.call_args
        assert "/investigate" in call_args.kwargs["command"]
        assert "INC-001" in call_args.kwargs["command"]


class TestIncidentEscalatedTrigger:
    """Tests for IncidentEscalatedTrigger handler."""

    @pytest.fixture
    def mock_gateway(self):
        gateway = MagicMock(spec=GatewayClient)
        gateway.send_command = AsyncMock(return_value=MagicMock(success=True))
        return gateway

    @pytest.fixture
    def trigger(self, mock_gateway):
        return IncidentEscalatedTrigger(gateway=mock_gateway)

    @pytest.mark.asyncio
    async def test_handle_escalation_event(self, trigger, mock_gateway):
        """Test: Escalation events send appropriate command."""
        event = {
            "incident_id": "INC-001",
            "previous_tier": "tier1",
            "new_tier": "tier2",
            "reason": "Complexity requires senior analyst"
        }

        await trigger.handle(event)

        mock_gateway.send_command.assert_called_once()


class TestSLABreachTrigger:
    """Tests for SLABreachTrigger handler."""

    @pytest.fixture
    def mock_gateway(self):
        gateway = MagicMock(spec=GatewayClient)
        gateway.send_command = AsyncMock(return_value=MagicMock(success=True))
        return gateway

    @pytest.fixture
    def trigger(self, mock_gateway):
        return SLABreachTrigger(gateway=mock_gateway)

    @pytest.mark.asyncio
    async def test_handle_sla_breach_event(self, trigger, mock_gateway):
        """Test: SLA breach events trigger priority response."""
        event = {
            "incident_id": "INC-001",
            "sla_type": "response_time",
            "breach_at": datetime.now().isoformat(),
            "exceeded_by_minutes": 15
        }

        await trigger.handle(event)

        mock_gateway.send_command.assert_called_once()


class TestCorrelationFoundTrigger:
    """Tests for CorrelationFoundTrigger handler."""

    @pytest.fixture
    def mock_gateway(self):
        gateway = MagicMock(spec=GatewayClient)
        gateway.send_command = AsyncMock(return_value=MagicMock(success=True))
        return gateway

    @pytest.fixture
    def trigger(self, mock_gateway):
        return CorrelationFoundTrigger(gateway=mock_gateway)

    @pytest.mark.asyncio
    async def test_handle_correlation_event(self, trigger, mock_gateway):
        """Test: Correlation events trigger investigation expansion."""
        event = {
            "primary_incident_id": "INC-001",
            "correlated_incident_ids": ["INC-002", "INC-003"],
            "correlation_type": "ioc_match",
            "confidence": 0.95
        }

        await trigger.handle(event)

        mock_gateway.send_command.assert_called_once()


class TestIncidentReopenedTrigger:
    """Tests for IncidentReopenedTrigger handler."""

    @pytest.fixture
    def mock_gateway(self):
        gateway = MagicMock(spec=GatewayClient)
        gateway.send_command = AsyncMock(return_value=MagicMock(success=True))
        return gateway

    @pytest.fixture
    def trigger(self, mock_gateway):
        return IncidentReopenedTrigger(gateway=mock_gateway)

    @pytest.mark.asyncio
    async def test_handle_reopened_event(self, trigger, mock_gateway):
        """Test: Reopened incidents trigger re-investigation."""
        event = {
            "incident_id": "INC-001",
            "previous_status": "resolved",
            "new_status": "reopened",
            "reopen_reason": "New related activity detected"
        }

        await trigger.handle(event)

        mock_gateway.send_command.assert_called_once()
