"""Trigger handler for rejected approvals."""

from typing import Optional
from ..base import BaseTriggerHandler, TriggerEvent
from ..gateway_client import GatewayClient


class ApprovalRejectedTrigger(BaseTriggerHandler):
    """Trigger that fires when an approval request is rejected.

    This trigger monitors for approval rejections and sends an
    acknowledgment command to record the rejection and adjust response.
    """

    def __init__(self, gateway_client: Optional[GatewayClient] = None):
        super().__init__(gateway_client)

    @property
    def trigger_name(self) -> str:
        return "approval_rejected"

    @property
    def description(self) -> str:
        return "Triggers when an approval request is rejected, acknowledging and adjusting response"

    @property
    def event_types(self) -> list[str]:
        return ["approval.rejected"]

    def should_trigger(self, event: TriggerEvent) -> bool:
        """Any rejection should trigger acknowledgment."""
        return True

    def get_command(self, event: TriggerEvent) -> str:
        """Generate the /acknowledge-rejection command."""
        approval_id = event.data.get("approval_id", "unknown")
        action_type = event.data.get("action_type", "unknown")
        rejection_reason = event.data.get("rejection_reason", "No reason provided")

        # Escape quotes in reason
        reason_escaped = rejection_reason.replace('"', '\\"')

        return f'/acknowledge-rejection {approval_id} --action {action_type} --reason "{reason_escaped}"'
