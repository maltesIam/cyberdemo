"""Trigger handler for containment lifted events.

Automatically sends confirmation when containment is lifted.
"""
from typing import Any

from ..gateway_client import GatewayClient


class ContainmentLiftedTrigger:
    """Trigger handler for containment lifted events.

    Sends confirmation when containment actions are lifted/removed.
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
            event: The containment lifted event

        Returns:
            True if containment lift details are present
        """
        return bool(event.get("host_id") and event.get("containment_id"))

    async def handle(self, event: dict[str, Any]) -> None:
        """Handle the containment lifted event.

        Args:
            event: The containment lifted event
        """
        if not self.should_trigger(event):
            return

        host_id = event.get("host_id", "unknown")
        containment_id = event.get("containment_id", "unknown")
        lifted_by = event.get("lifted_by", "unknown")
        reason = event.get("reason", "No reason provided")

        await self.gateway.send_command(
            command=f"/confirm containment {containment_id} lifted from {host_id}",
            cooldown_key=f"containment_lift:{containment_id}",
            dedup_key=f"containment_lifted:{containment_id}",
            metadata={
                "host_id": host_id,
                "containment_id": containment_id,
                "lifted_at": event.get("lifted_at"),
                "lifted_by": lifted_by,
                "reason": reason,
                "trigger": "containment_lifted"
            }
        )


__all__ = ["ContainmentLiftedTrigger"]
