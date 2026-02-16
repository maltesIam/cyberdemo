"""Trigger handler for new approval requests."""

from typing import Optional
from ..base import BaseTriggerHandler, TriggerEvent
from ..gateway_client import GatewayClient


class NewApprovalNeededTrigger(BaseTriggerHandler):
    """Trigger that fires when a new urgent approval is needed.

    This trigger monitors for new approval requests with high or critical
    urgency and notifies the SOC analyst for immediate attention.
    """

    # Urgency levels that trigger notification
    HIGH_URGENCY_LEVELS = {"high", "critical", "urgent"}

    def __init__(self, gateway_client: Optional[GatewayClient] = None):
        super().__init__(gateway_client)

    @property
    def trigger_name(self) -> str:
        return "new_approval_needed"

    @property
    def description(self) -> str:
        return "Triggers when a new high-urgency approval request is created"

    @property
    def event_types(self) -> list[str]:
        return ["approval.requested"]

    def should_trigger(self, event: TriggerEvent) -> bool:
        """Check if the approval request is urgent."""
        data = event.data

        urgency = data.get("urgency", "").lower()
        if urgency not in self.HIGH_URGENCY_LEVELS:
            return False

        return True

    def get_command(self, event: TriggerEvent) -> str:
        """Generate a notification command for the pending approval."""
        approval_id = event.data.get("approval_id", "unknown")
        action_type = event.data.get("action_type", "unknown")
        target_asset = event.data.get("target_asset", "unknown")
        urgency = event.data.get("urgency", "high")
        incident_id = event.data.get("incident_id", "")

        cmd = f"Pending approval {approval_id}: {action_type} on {target_asset} (urgency: {urgency})"
        if incident_id:
            cmd += f" [Incident: {incident_id}]"

        return cmd
