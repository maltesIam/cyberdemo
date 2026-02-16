"""Tests for Approval-related trigger handlers.

RED Phase: These tests define the expected behavior before implementation.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from src.triggers import TriggerEvent
from src.triggers.gateway_client import GatewayClient, CommandResult
from src.triggers.approvals import (
    ApprovalApprovedTrigger,
    ApprovalRejectedTrigger,
    ApprovalTimeoutTrigger,
    NewApprovalNeededTrigger,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_gateway_client():
    """Create a mock gateway client."""
    client = MagicMock(spec=GatewayClient)
    client.send_command = AsyncMock(return_value=CommandResult(success=True, message_id="msg-001"))
    return client


@pytest.fixture
def base_timestamp():
    """Provide a consistent timestamp for tests."""
    return datetime(2024, 2, 14, 10, 30, 0)


# ============================================================================
# ApprovalApprovedTrigger Tests
# ============================================================================

class TestApprovalApprovedTrigger:
    """Tests for approval granted trigger."""

    def test_trigger_name(self, mock_gateway_client):
        """Test that trigger has correct name."""
        trigger = ApprovalApprovedTrigger(mock_gateway_client)
        assert trigger.trigger_name == "approval_approved"

    def test_description(self, mock_gateway_client):
        """Test that trigger has meaningful description."""
        trigger = ApprovalApprovedTrigger(mock_gateway_client)
        assert "approved" in trigger.description.lower() or "granted" in trigger.description.lower()

    def test_event_types(self, mock_gateway_client):
        """Test that trigger responds to correct event types."""
        trigger = ApprovalApprovedTrigger(mock_gateway_client)
        assert "approval.approved" in trigger.event_types

    def test_should_trigger_for_containment_approval(self, mock_gateway_client, base_timestamp):
        """Test trigger fires when containment is approved."""
        trigger = ApprovalApprovedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.approved",
            source="approval_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-001",
                "action_type": "containment",
                "target_asset": "workstation-001",
                "approver": "security_manager",
                "approval_time": base_timestamp.isoformat(),
                "incident_id": "INC-001",
            },
        )
        assert trigger.should_trigger(event) is True

    def test_should_trigger_for_isolation_approval(self, mock_gateway_client, base_timestamp):
        """Test trigger fires when isolation is approved."""
        trigger = ApprovalApprovedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.approved",
            source="approval_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-002",
                "action_type": "isolation",
                "target_asset": "server-001",
                "approver": "soc_lead",
                "incident_id": "INC-002",
            },
        )
        assert trigger.should_trigger(event) is True

    def test_should_trigger_for_any_approved_action(self, mock_gateway_client, base_timestamp):
        """Test trigger fires for any approved action."""
        trigger = ApprovalApprovedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.approved",
            source="approval_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-003",
                "action_type": "block_ip",
                "target": "192.168.1.100",
                "approver": "network_admin",
            },
        )
        assert trigger.should_trigger(event) is True

    def test_get_command_for_containment(self, mock_gateway_client, base_timestamp):
        """Test correct command is generated for containment."""
        trigger = ApprovalApprovedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.approved",
            source="approval_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-001",
                "action_type": "containment",
                "target_asset": "workstation-001",
                "incident_id": "INC-001",
            },
        )
        command = trigger.get_command(event)
        assert "/execute-containment" in command

    @pytest.mark.asyncio
    async def test_process_sends_command(self, mock_gateway_client, base_timestamp):
        """Test that processing triggers command to gateway."""
        trigger = ApprovalApprovedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.approved",
            source="approval_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-001",
                "action_type": "containment",
                "target_asset": "workstation-001",
                "incident_id": "INC-001",
            },
        )
        result = await trigger.process(event)
        assert result.triggered is True
        mock_gateway_client.send_command.assert_called_once()


# ============================================================================
# ApprovalRejectedTrigger Tests
# ============================================================================

class TestApprovalRejectedTrigger:
    """Tests for approval rejected trigger."""

    def test_trigger_name(self, mock_gateway_client):
        """Test that trigger has correct name."""
        trigger = ApprovalRejectedTrigger(mock_gateway_client)
        assert trigger.trigger_name == "approval_rejected"

    def test_event_types(self, mock_gateway_client):
        """Test that trigger responds to correct event types."""
        trigger = ApprovalRejectedTrigger(mock_gateway_client)
        assert "approval.rejected" in trigger.event_types

    def test_should_trigger_for_rejected_containment(self, mock_gateway_client, base_timestamp):
        """Test trigger fires when containment is rejected."""
        trigger = ApprovalRejectedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.rejected",
            source="approval_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-010",
                "action_type": "containment",
                "target_asset": "critical-server",
                "rejector": "ciso",
                "rejection_reason": "Business critical system - need alternative approach",
                "incident_id": "INC-005",
            },
        )
        assert trigger.should_trigger(event) is True

    def test_should_trigger_for_any_rejection(self, mock_gateway_client, base_timestamp):
        """Test trigger fires for any rejected action."""
        trigger = ApprovalRejectedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.rejected",
            source="approval_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-011",
                "action_type": "block_user",
                "target": "user@example.com",
                "rejector": "hr_manager",
                "rejection_reason": "User is VIP - escalate to CISO",
            },
        )
        assert trigger.should_trigger(event) is True

    def test_get_command_includes_acknowledge(self, mock_gateway_client, base_timestamp):
        """Test command includes acknowledge-rejection."""
        trigger = ApprovalRejectedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.rejected",
            source="approval_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-010",
                "action_type": "containment",
                "rejection_reason": "Business critical",
            },
        )
        command = trigger.get_command(event)
        assert "/acknowledge-rejection" in command

    @pytest.mark.asyncio
    async def test_process_sends_command(self, mock_gateway_client, base_timestamp):
        """Test that processing triggers command to gateway."""
        trigger = ApprovalRejectedTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.rejected",
            source="approval_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-010",
                "action_type": "containment",
                "rejection_reason": "Business critical",
            },
        )
        result = await trigger.process(event)
        assert result.triggered is True
        mock_gateway_client.send_command.assert_called_once()


# ============================================================================
# ApprovalTimeoutTrigger Tests
# ============================================================================

class TestApprovalTimeoutTrigger:
    """Tests for approval timeout trigger."""

    def test_trigger_name(self, mock_gateway_client):
        """Test that trigger has correct name."""
        trigger = ApprovalTimeoutTrigger(mock_gateway_client)
        assert trigger.trigger_name == "approval_timeout"

    def test_event_types(self, mock_gateway_client):
        """Test that trigger responds to correct event types."""
        trigger = ApprovalTimeoutTrigger(mock_gateway_client)
        assert "approval.timeout" in trigger.event_types

    def test_should_trigger_for_critical_timeout(self, mock_gateway_client, base_timestamp):
        """Test trigger fires for critical action timeout."""
        trigger = ApprovalTimeoutTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.timeout",
            source="approval_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-020",
                "action_type": "containment",
                "target_asset": "infected-workstation",
                "requested_at": "2024-02-14T09:00:00",
                "timeout_minutes": 30,
                "incident_id": "INC-010",
                "severity": "critical",
            },
            severity="high",
        )
        assert trigger.should_trigger(event) is True

    def test_should_trigger_for_any_timeout(self, mock_gateway_client, base_timestamp):
        """Test trigger fires for any approval timeout."""
        trigger = ApprovalTimeoutTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.timeout",
            source="approval_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-021",
                "action_type": "block_ip",
                "target": "10.0.0.50",
                "requested_at": "2024-02-14T08:00:00",
                "timeout_minutes": 60,
            },
        )
        assert trigger.should_trigger(event) is True

    def test_get_command_includes_escalate(self, mock_gateway_client, base_timestamp):
        """Test command includes escalate."""
        trigger = ApprovalTimeoutTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.timeout",
            source="approval_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-020",
                "action_type": "containment",
                "incident_id": "INC-010",
            },
        )
        command = trigger.get_command(event)
        assert "/escalate" in command

    def test_context_includes_timeout_info(self, mock_gateway_client, base_timestamp):
        """Test context includes timeout information."""
        trigger = ApprovalTimeoutTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.timeout",
            source="approval_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-020",
                "action_type": "containment",
                "timeout_minutes": 30,
            },
        )
        context = trigger.get_context(event)
        assert "trigger" in context
        assert context["trigger"] == "approval_timeout"

    @pytest.mark.asyncio
    async def test_process_sends_command(self, mock_gateway_client, base_timestamp):
        """Test that processing triggers command to gateway."""
        trigger = ApprovalTimeoutTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.timeout",
            source="approval_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-020",
                "action_type": "containment",
                "incident_id": "INC-010",
            },
        )
        result = await trigger.process(event)
        assert result.triggered is True
        mock_gateway_client.send_command.assert_called_once()


# ============================================================================
# NewApprovalNeededTrigger Tests
# ============================================================================

class TestNewApprovalNeededTrigger:
    """Tests for new approval request trigger."""

    def test_trigger_name(self, mock_gateway_client):
        """Test that trigger has correct name."""
        trigger = NewApprovalNeededTrigger(mock_gateway_client)
        assert trigger.trigger_name == "new_approval_needed"

    def test_event_types(self, mock_gateway_client):
        """Test that trigger responds to correct event types."""
        trigger = NewApprovalNeededTrigger(mock_gateway_client)
        assert "approval.requested" in trigger.event_types

    def test_should_trigger_for_urgent_approval(self, mock_gateway_client, base_timestamp):
        """Test trigger fires for urgent approval request."""
        trigger = NewApprovalNeededTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.requested",
            source="soar_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-030",
                "action_type": "containment",
                "target_asset": "compromised-server",
                "requested_by": "soc_analyst",
                "urgency": "high",
                "incident_id": "INC-015",
                "justification": "Active ransomware infection detected",
            },
            severity="critical",
        )
        assert trigger.should_trigger(event) is True

    def test_should_trigger_for_critical_action(self, mock_gateway_client, base_timestamp):
        """Test trigger fires for critical action requiring approval."""
        trigger = NewApprovalNeededTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.requested",
            source="soar_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-031",
                "action_type": "full_isolation",
                "target_asset": "domain-controller",
                "requested_by": "incident_responder",
                "urgency": "critical",
            },
            severity="critical",
        )
        assert trigger.should_trigger(event) is True

    def test_should_not_trigger_for_low_urgency(self, mock_gateway_client, base_timestamp):
        """Test trigger does not fire for low urgency requests."""
        trigger = NewApprovalNeededTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.requested",
            source="soar_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-032",
                "action_type": "software_install",
                "target_asset": "workstation-050",
                "requested_by": "it_admin",
                "urgency": "low",
            },
            severity="low",
        )
        assert trigger.should_trigger(event) is False

    def test_get_command_for_notification(self, mock_gateway_client, base_timestamp):
        """Test command format for new approval notification."""
        trigger = NewApprovalNeededTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.requested",
            source="soar_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-030",
                "action_type": "containment",
                "target_asset": "compromised-server",
                "incident_id": "INC-015",
                "urgency": "high",
            },
        )
        command = trigger.get_command(event)
        # The command should notify about the pending approval
        assert "APR-030" in command or "approval" in command.lower()

    def test_context_includes_approval_details(self, mock_gateway_client, base_timestamp):
        """Test context includes approval request details."""
        trigger = NewApprovalNeededTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.requested",
            source="soar_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-030",
                "action_type": "containment",
                "urgency": "high",
            },
        )
        context = trigger.get_context(event)
        assert "trigger" in context
        assert context["trigger"] == "new_approval_needed"

    @pytest.mark.asyncio
    async def test_process_sends_command(self, mock_gateway_client, base_timestamp):
        """Test that processing triggers command to gateway."""
        trigger = NewApprovalNeededTrigger(mock_gateway_client)
        event = TriggerEvent(
            event_type="approval.requested",
            source="soar_system",
            timestamp=base_timestamp,
            data={
                "approval_id": "APR-030",
                "action_type": "containment",
                "target_asset": "compromised-server",
                "urgency": "high",
            },
            severity="high",
        )
        result = await trigger.process(event)
        assert result.triggered is True
        mock_gateway_client.send_command.assert_called_once()
