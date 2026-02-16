"""Trigger handler for SLA breach events.

Automatically triggers priority response when SLAs are breached.
"""
from typing import Any

from ..gateway_client import GatewayClient


class SLABreachTrigger:
    """Trigger handler for SLA breach events.

    Sends priority notification when incident SLAs are breached.
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
            event: The SLA breach event

        Returns:
            True if SLA breach details are present
        """
        return bool(event.get("incident_id") and event.get("sla_type"))

    async def handle(self, event: dict[str, Any]) -> None:
        """Handle the SLA breach event.

        Args:
            event: The SLA breach event
        """
        if not self.should_trigger(event):
            return

        incident_id = event.get("incident_id", "unknown")
        sla_type = event.get("sla_type", "unknown")
        exceeded_minutes = event.get("exceeded_by_minutes", 0)

        await self.gateway.send_command(
            command=f"/sla_alert {incident_id} {sla_type} exceeded by {exceeded_minutes}m",
            cooldown_key=f"sla:{incident_id}:{sla_type}",
            dedup_key=f"sla_breach:{incident_id}:{sla_type}",
            metadata={
                "incident_id": incident_id,
                "sla_type": sla_type,
                "breach_at": event.get("breach_at"),
                "exceeded_by_minutes": exceeded_minutes,
                "trigger": "sla_breach",
                "priority": "high"
            }
        )


__all__ = ["SLABreachTrigger"]
