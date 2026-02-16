"""Trigger handler for incident creation events.

Automatically triggers /investigate for high/critical severity incidents.
"""
from typing import Any, Optional

from ..gateway_client import GatewayClient


class IncidentCreatedTrigger:
    """Trigger handler for new incident creation events.

    Triggers /investigate command for high or critical severity incidents.
    """

    HIGH_SEVERITY_LEVELS = {"high", "critical"}

    def __init__(self, gateway: GatewayClient):
        """Initialize the trigger.

        Args:
            gateway: Gateway client for sending commands
        """
        self.gateway = gateway

    def should_trigger(self, event: dict[str, Any]) -> bool:
        """Check if event should trigger an action.

        Args:
            event: The incident creation event

        Returns:
            True if incident severity is high or critical
        """
        severity = event.get("severity", "").lower()
        return severity in self.HIGH_SEVERITY_LEVELS

    async def handle(self, event: dict[str, Any]) -> None:
        """Handle the incident creation event.

        Args:
            event: The incident creation event
        """
        if not self.should_trigger(event):
            return

        incident_id = event.get("incident_id", "unknown")
        severity = event.get("severity", "unknown")

        await self.gateway.send_command(
            command=f"/investigate {incident_id}",
            cooldown_key=f"incident:{incident_id}",
            dedup_key=f"investigate:{incident_id}",
            metadata={
                "incident_id": incident_id,
                "severity": severity,
                "trigger": "incident_created",
                "title": event.get("title", "")
            }
        )


__all__ = ["IncidentCreatedTrigger"]
