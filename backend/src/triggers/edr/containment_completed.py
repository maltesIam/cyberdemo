"""Trigger handler for containment completion events.

Automatically sends status update when containment is completed.
"""
from typing import Any

from ..gateway_client import GatewayClient


class ContainmentCompletedTrigger:
    """Trigger handler for containment completion events.

    Sends status update when containment actions complete successfully.
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
            event: The containment completion event

        Returns:
            True if containment completion details are present
        """
        return bool(event.get("host_id") and event.get("containment_id"))

    async def handle(self, event: dict[str, Any]) -> None:
        """Handle the containment completion event.

        Args:
            event: The containment completion event
        """
        if not self.should_trigger(event):
            return

        host_id = event.get("host_id", "unknown")
        containment_id = event.get("containment_id", "unknown")
        duration_seconds = event.get("duration_seconds", 0)

        await self.gateway.send_command(
            command=f"/status containment {containment_id} completed on {host_id}",
            cooldown_key=f"containment_complete:{containment_id}",
            dedup_key=f"containment_completed:{containment_id}",
            metadata={
                "host_id": host_id,
                "containment_id": containment_id,
                "completed_at": event.get("completed_at"),
                "duration_seconds": duration_seconds,
                "trigger": "containment_completed"
            }
        )


__all__ = ["ContainmentCompletedTrigger"]
