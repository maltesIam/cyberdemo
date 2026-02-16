"""Trigger handler for new threat intelligence feeds."""

from typing import Optional
from ..base import BaseTriggerHandler, TriggerEvent
from ..gateway_client import GatewayClient


class NewIntelFeedTrigger(BaseTriggerHandler):
    """Trigger that fires when a new high-priority threat feed is available.

    This trigger monitors for new threat intelligence feeds that are
    relevant to the organization and require attention.
    """

    # Priority levels that trigger
    HIGH_PRIORITIES = {"high", "urgent", "critical"}

    # Minimum relevance score (0-100)
    MIN_RELEVANCE_SCORE = 50

    def __init__(self, gateway_client: Optional[GatewayClient] = None):
        super().__init__(gateway_client)

    @property
    def trigger_name(self) -> str:
        return "new_intel_feed"

    @property
    def description(self) -> str:
        return "Triggers when a new high-priority threat intelligence feed is available"

    @property
    def event_types(self) -> list[str]:
        return ["intel.feed.new"]

    def should_trigger(self, event: TriggerEvent) -> bool:
        """Check if the feed is high priority and relevant."""
        data = event.data

        # Check priority
        priority = data.get("priority", "").lower()
        if priority not in self.HIGH_PRIORITIES:
            return False

        # Check relevance score
        relevance_score = data.get("relevance_score", 0)
        if relevance_score < self.MIN_RELEVANCE_SCORE:
            return False

        return True

    def get_command(self, event: TriggerEvent) -> str:
        """Generate the /check-intel command for the feed."""
        feed_name = event.data.get("feed_name", "unknown")
        feed_type = event.data.get("feed_type", "general")
        ioc_count = event.data.get("ioc_count", 0)

        return f"/check-intel feed:{feed_name} --type {feed_type} --ioc-count {ioc_count}"
