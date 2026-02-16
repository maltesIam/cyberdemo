"""Trigger handler for high severity EDR detection events.

Automatically triggers /investigate for high/critical severity detections.
"""
from typing import Any

from ..gateway_client import GatewayClient


class DetectionHighSeverityTrigger:
    """Trigger handler for high severity EDR detections.

    Triggers /investigate command for high or critical severity detections.
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
            event: The detection event

        Returns:
            True if detection severity is high or critical
        """
        severity = event.get("severity", "").lower()
        return severity in self.HIGH_SEVERITY_LEVELS

    async def handle(self, event: dict[str, Any]) -> None:
        """Handle the high severity detection event.

        Args:
            event: The detection event
        """
        if not self.should_trigger(event):
            return

        detection_id = event.get("detection_id", "unknown")
        host_id = event.get("host_id", "unknown")
        severity = event.get("severity", "unknown")
        file_hash = event.get("hash", "unknown")

        await self.gateway.send_command(
            command=f"/investigate detection {detection_id} on {host_id}",
            cooldown_key=f"detection:{detection_id}",
            dedup_key=f"investigate_detection:{detection_id}",
            metadata={
                "detection_id": detection_id,
                "host_id": host_id,
                "severity": severity,
                "hash": file_hash,
                "trigger": "detection_high_severity"
            }
        )


__all__ = ["DetectionHighSeverityTrigger"]
