"""Trigger handler for containment failure events.

Automatically triggers /retry when containment actions fail.
"""
from typing import Any

from ..gateway_client import GatewayClient


class ContainmentFailedTrigger:
    """Trigger handler for containment failure events.

    Triggers /retry command when containment actions fail.
    """

    MAX_RETRY_ATTEMPTS = 3

    def __init__(self, gateway: GatewayClient):
        """Initialize the trigger.

        Args:
            gateway: Gateway client for sending commands
        """
        self.gateway = gateway

    def should_trigger(self, event: dict[str, Any]) -> bool:
        """Check if event should trigger an action.

        Args:
            event: The containment failure event

        Returns:
            True if retry should be attempted
        """
        attempt_count = event.get("attempt_count", 0)
        return (
            bool(event.get("host_id"))
            and bool(event.get("containment_id"))
            and attempt_count < self.MAX_RETRY_ATTEMPTS
        )

    async def handle(self, event: dict[str, Any]) -> None:
        """Handle the containment failure event.

        Args:
            event: The containment failure event
        """
        if not self.should_trigger(event):
            return

        host_id = event.get("host_id", "unknown")
        containment_id = event.get("containment_id", "unknown")
        failure_reason = event.get("failure_reason", "Unknown error")
        attempt_count = event.get("attempt_count", 0)

        await self.gateway.send_command(
            command=f"/retry containment {containment_id} on {host_id}",
            cooldown_key=f"containment_retry:{containment_id}",
            dedup_key=f"retry_containment:{containment_id}:{attempt_count + 1}",
            metadata={
                "host_id": host_id,
                "containment_id": containment_id,
                "failure_reason": failure_reason,
                "attempt_count": attempt_count + 1,
                "trigger": "containment_failed"
            }
        )


__all__ = ["ContainmentFailedTrigger"]
