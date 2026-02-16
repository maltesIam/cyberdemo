"""Trigger handler for hash propagation events.

Automatically triggers /hunt when a hash is seen on multiple hosts.
"""
from typing import Any

from ..gateway_client import GatewayClient


class HashPropagationTrigger:
    """Trigger handler for hash propagation events.

    Triggers /hunt command when a hash is detected on 3 or more hosts.
    """

    PROPAGATION_THRESHOLD = 3

    def __init__(self, gateway: GatewayClient):
        """Initialize the trigger.

        Args:
            gateway: Gateway client for sending commands
        """
        self.gateway = gateway

    def should_trigger(self, event: dict[str, Any]) -> bool:
        """Check if event should trigger an action.

        Args:
            event: The propagation event

        Returns:
            True if hash is seen on 3 or more hosts
        """
        propagation_count = event.get("propagation_count", 0)
        return propagation_count >= self.PROPAGATION_THRESHOLD

    async def handle(self, event: dict[str, Any]) -> None:
        """Handle the hash propagation event.

        Args:
            event: The propagation event
        """
        if not self.should_trigger(event):
            return

        file_hash = event.get("hash", "unknown")
        hosts_affected = event.get("hosts_affected", [])
        propagation_count = event.get("propagation_count", 0)

        await self.gateway.send_command(
            command=f"/hunt hash {file_hash} across {propagation_count} hosts",
            cooldown_key=f"hash_propagation:{file_hash}",
            dedup_key=f"hunt_hash:{file_hash}:{propagation_count}",
            metadata={
                "hash": file_hash,
                "hosts_affected": hosts_affected,
                "propagation_count": propagation_count,
                "first_seen": event.get("first_seen"),
                "trigger": "hash_propagation"
            }
        )


__all__ = ["HashPropagationTrigger"]
