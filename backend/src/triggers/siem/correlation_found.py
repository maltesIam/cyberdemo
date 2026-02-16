"""Trigger handler for correlation detection events.

Automatically triggers investigation expansion when correlations are found.
"""
from typing import Any

from ..gateway_client import GatewayClient


class CorrelationFoundTrigger:
    """Trigger handler for correlation detection events.

    Sends command to expand investigation when incidents are correlated.
    """

    CONFIDENCE_THRESHOLD = 0.7

    def __init__(self, gateway: GatewayClient):
        """Initialize the trigger.

        Args:
            gateway: Gateway client for sending commands
        """
        self.gateway = gateway

    def should_trigger(self, event: dict[str, Any]) -> bool:
        """Check if event should trigger an action.

        Args:
            event: The correlation event

        Returns:
            True if correlation confidence is above threshold
        """
        confidence = event.get("confidence", 0)
        return (
            bool(event.get("primary_incident_id"))
            and bool(event.get("correlated_incident_ids"))
            and confidence >= self.CONFIDENCE_THRESHOLD
        )

    async def handle(self, event: dict[str, Any]) -> None:
        """Handle the correlation detection event.

        Args:
            event: The correlation event
        """
        if not self.should_trigger(event):
            return

        primary_id = event.get("primary_incident_id", "unknown")
        correlated_ids = event.get("correlated_incident_ids", [])
        correlation_type = event.get("correlation_type", "unknown")
        confidence = event.get("confidence", 0)

        correlated_str = ",".join(correlated_ids)

        await self.gateway.send_command(
            command=f"/expand_investigation {primary_id} correlate {correlated_str}",
            cooldown_key=f"correlation:{primary_id}",
            dedup_key=f"correlation:{primary_id}:{correlated_str}",
            metadata={
                "primary_incident_id": primary_id,
                "correlated_incident_ids": correlated_ids,
                "correlation_type": correlation_type,
                "confidence": confidence,
                "trigger": "correlation_found"
            }
        )


__all__ = ["CorrelationFoundTrigger"]
