"""Trigger handler for IOC matches in network traffic."""

from typing import Optional
from ..base import BaseTriggerHandler, TriggerEvent
from ..gateway_client import GatewayClient


class IOCMatchNetworkTrigger(BaseTriggerHandler):
    """Trigger that fires when a known IOC is found in network traffic.

    This trigger monitors network activity for connections to known
    malicious IOCs and triggers investigation.
    """

    # Minimum threat score to trigger
    THREAT_SCORE_THRESHOLD = 60

    def __init__(self, gateway_client: Optional[GatewayClient] = None):
        super().__init__(gateway_client)

    @property
    def trigger_name(self) -> str:
        return "ioc_match_network"

    @property
    def description(self) -> str:
        return "Triggers when a known IOC is detected in network traffic"

    @property
    def event_types(self) -> list[str]:
        return ["intel.ioc.network_match"]

    def should_trigger(self, event: TriggerEvent) -> bool:
        """Check if the network IOC match warrants investigation."""
        data = event.data

        # Check threat score threshold
        threat_score = data.get("threat_score", 0)
        if threat_score < self.THREAT_SCORE_THRESHOLD:
            return False

        return True

    def get_command(self, event: TriggerEvent) -> str:
        """Generate the /check-intel command."""
        ioc_value = event.data.get("ioc_value", "unknown")
        ioc_type = event.data.get("ioc_type", "unknown")
        source_host = event.data.get("source_host", "unknown")
        match_type = event.data.get("match_type", "connection")

        return f"/check-intel {ioc_type}:{ioc_value} --source {source_host} --match-type {match_type}"
