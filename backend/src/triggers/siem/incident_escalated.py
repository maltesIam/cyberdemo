"""Trigger handler for incident escalation events.

Automatically notifies when incidents are escalated between tiers.
"""
from typing import Any

from ..gateway_client import GatewayClient


class IncidentEscalatedTrigger:
    """Trigger handler for incident escalation events.

    Sends notification/command when incidents are escalated to higher tiers.
    """

    def __init__(self, gateway: GatewayClient):
        """Initialize the trigger.

        Args:
            gateway: Gateway client for sending commands
        """
        self.gateway = gateway

    def should_trigger(self, event: dict[str, Any]) -> bool:
        """Check if event should trigger an action.

        Args:
            event: The escalation event

        Returns:
            True if escalation details are present
        """
        return bool(event.get("incident_id") and event.get("new_tier"))

    async def handle(self, event: dict[str, Any]) -> None:
        """Handle the incident escalation event.

        Args:
            event: The escalation event
        """
        if not self.should_trigger(event):
            return

        incident_id = event.get("incident_id", "unknown")
        new_tier = event.get("new_tier", "unknown")
        reason = event.get("reason", "No reason provided")

        await self.gateway.send_command(
            command=f"/escalation_notice {incident_id} to {new_tier}",
            cooldown_key=f"escalation:{incident_id}:{new_tier}",
            dedup_key=f"escalation:{incident_id}:{new_tier}",
            metadata={
                "incident_id": incident_id,
                "previous_tier": event.get("previous_tier"),
                "new_tier": new_tier,
                "reason": reason,
                "trigger": "incident_escalated"
            }
        )


__all__ = ["IncidentEscalatedTrigger"]
