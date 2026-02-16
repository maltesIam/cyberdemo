"""Trigger handler for incident reopened events.

Automatically triggers re-investigation when incidents are reopened.
"""
from typing import Any

from ..gateway_client import GatewayClient


class IncidentReopenedTrigger:
    """Trigger handler for incident reopened events.

    Sends command to re-investigate when previously closed incidents are reopened.
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
            event: The reopened event

        Returns:
            True if incident was reopened
        """
        return (
            bool(event.get("incident_id"))
            and event.get("new_status") == "reopened"
        )

    async def handle(self, event: dict[str, Any]) -> None:
        """Handle the incident reopened event.

        Args:
            event: The reopened event
        """
        if not self.should_trigger(event):
            return

        incident_id = event.get("incident_id", "unknown")
        previous_status = event.get("previous_status", "unknown")
        reopen_reason = event.get("reopen_reason", "No reason provided")

        await self.gateway.send_command(
            command=f"/reinvestigate {incident_id}",
            cooldown_key=f"reopen:{incident_id}",
            dedup_key=f"reinvestigate:{incident_id}",
            metadata={
                "incident_id": incident_id,
                "previous_status": previous_status,
                "reopen_reason": reopen_reason,
                "trigger": "incident_reopened"
            }
        )


__all__ = ["IncidentReopenedTrigger"]
