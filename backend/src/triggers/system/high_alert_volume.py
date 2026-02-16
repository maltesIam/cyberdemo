"""Trigger handler for high alert volume events.

When alert volume exceeds threshold (>100/hour by default),
triggers /triage-alerts to help prioritize the queue.
"""
from typing import Any, Dict, Optional

from ..base import BaseTriggerHandler, TriggerEvent, TriggerResult


class HighAlertVolumeTrigger(BaseTriggerHandler):
    """Trigger that fires when alert volume is high.

    Sends /triage-alerts command when count exceeds threshold.
    """

    DEFAULT_THRESHOLD = 100

    def __init__(
        self,
        gateway_client: Optional[Any] = None,
        threshold: int = DEFAULT_THRESHOLD
    ):
        """Initialize with optional custom threshold.

        Args:
            gateway_client: The gateway client for sending commands.
            threshold: Alert count threshold (default 100/hour).
        """
        super().__init__(gateway_client)
        self.threshold = threshold

    @property
    def trigger_name(self) -> str:
        return "high_alert_volume"

    @property
    def description(self) -> str:
        return f"Triggers alert triage when volume exceeds {self.threshold}/hour"

    @property
    def event_types(self) -> list[str]:
        return ["alerts.volume_threshold"]

    def should_trigger(self, event: TriggerEvent) -> bool:
        """Check if alert count exceeds threshold."""
        count = event.data.get("count", 0)
        # Use threshold from event if provided, otherwise use instance threshold
        event_threshold = event.data.get("threshold", self.threshold)
        return count > event_threshold

    def get_command(self, event: TriggerEvent) -> str:
        """Return the /triage-alerts command."""
        return "/triage-alerts"

    def get_context(self, event: TriggerEvent) -> Dict[str, Any]:
        """Include volume details in context."""
        context = super().get_context(event)
        context.update({
            "count": event.data.get("count"),
            "period": event.data.get("period"),
            "threshold": event.data.get("threshold", self.threshold),
        })
        return context


__all__ = ["HighAlertVolumeTrigger"]
