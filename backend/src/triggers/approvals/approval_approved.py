"""Trigger handler for approved actions."""

from typing import Optional
from ..base import BaseTriggerHandler, TriggerEvent
from ..gateway_client import GatewayClient


class ApprovalApprovedTrigger(BaseTriggerHandler):
    """Trigger that fires when an action is approved.

    This trigger monitors for approval grants and triggers the
    execution of the approved action (e.g., containment).
    """

    def __init__(self, gateway_client: Optional[GatewayClient] = None):
        super().__init__(gateway_client)

    @property
    def trigger_name(self) -> str:
        return "approval_approved"

    @property
    def description(self) -> str:
        return "Triggers when an action is approved, executing the approved containment or remediation"

    @property
    def event_types(self) -> list[str]:
        return ["approval.approved"]

    def should_trigger(self, event: TriggerEvent) -> bool:
        """Any approved action should trigger."""
        # All approved actions should be executed
        return True

    def get_command(self, event: TriggerEvent) -> str:
        """Generate the /execute-containment command."""
        approval_id = event.data.get("approval_id", "unknown")
        action_type = event.data.get("action_type", "containment")
        target_asset = event.data.get("target_asset", event.data.get("target", "unknown"))
        incident_id = event.data.get("incident_id", "")

        cmd = f"/execute-containment {approval_id} --action {action_type} --target {target_asset}"
        if incident_id:
            cmd += f" --incident {incident_id}"

        return cmd
