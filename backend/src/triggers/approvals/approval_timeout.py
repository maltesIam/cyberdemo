"""Trigger handler for approval timeouts."""

from typing import Optional
from ..base import BaseTriggerHandler, TriggerEvent
from ..gateway_client import GatewayClient


class ApprovalTimeoutTrigger(BaseTriggerHandler):
    """Trigger that fires when an approval request times out.

    This trigger monitors for expired approval requests and triggers
    escalation to ensure timely response to security incidents.
    """

    def __init__(self, gateway_client: Optional[GatewayClient] = None):
        super().__init__(gateway_client)

    @property
    def trigger_name(self) -> str:
        return "approval_timeout"

    @property
    def description(self) -> str:
        return "Triggers when an approval request expires, escalating for immediate attention"

    @property
    def event_types(self) -> list[str]:
        return ["approval.timeout"]

    def should_trigger(self, event: TriggerEvent) -> bool:
        """Any timeout should trigger escalation."""
        return True

    def get_command(self, event: TriggerEvent) -> str:
        """Generate the /escalate command."""
        approval_id = event.data.get("approval_id", "unknown")
        action_type = event.data.get("action_type", "unknown")
        incident_id = event.data.get("incident_id", "")
        timeout_minutes = event.data.get("timeout_minutes", 0)

        cmd = f"/escalate {approval_id} --reason timeout --action {action_type} --waited-minutes {timeout_minutes}"
        if incident_id:
            cmd += f" --incident {incident_id}"

        return cmd
