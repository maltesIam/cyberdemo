"""Trigger handler for new malicious IOC detection."""

from typing import Optional
from ..base import BaseTriggerHandler, TriggerEvent
from ..gateway_client import GatewayClient


class NewMaliciousIOCTrigger(BaseTriggerHandler):
    """Trigger that fires when a new malicious IOC is detected.

    This trigger monitors for new IOCs with high confidence malicious
    classification and sends a /check-intel command to investigate.
    """

    # Minimum confidence score to trigger (0-100)
    CONFIDENCE_THRESHOLD = 70

    def __init__(self, gateway_client: Optional[GatewayClient] = None):
        super().__init__(gateway_client)

    @property
    def trigger_name(self) -> str:
        return "new_malicious_ioc"

    @property
    def description(self) -> str:
        return "Triggers when a new malicious IOC is detected with high confidence"

    @property
    def event_types(self) -> list[str]:
        return ["intel.ioc.new"]

    def should_trigger(self, event: TriggerEvent) -> bool:
        """Check if the IOC is malicious with sufficient confidence."""
        data = event.data

        # Check classification
        classification = data.get("classification", "").lower()
        if classification != "malicious":
            return False

        # Check confidence threshold
        confidence = data.get("confidence", 0)
        if confidence < self.CONFIDENCE_THRESHOLD:
            return False

        return True

    def get_command(self, event: TriggerEvent) -> str:
        """Generate the /check-intel command."""
        ioc_value = event.data.get("ioc_value", "unknown")
        ioc_type = event.data.get("ioc_type", "unknown")

        return f"/check-intel {ioc_type}:{ioc_value}"
