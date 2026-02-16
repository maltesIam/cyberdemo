"""Trigger handler for significant IOC score changes."""

from typing import Optional
from ..base import BaseTriggerHandler, TriggerEvent
from ..gateway_client import GatewayClient


class IOCScoreChangedTrigger(BaseTriggerHandler):
    """Trigger that fires when an IOC's threat score increases significantly.

    This trigger monitors for significant score increases that may indicate
    new threat intelligence about a previously known IOC.
    """

    # Minimum score increase to trigger
    SCORE_INCREASE_THRESHOLD = 30

    # Minimum new score to trigger
    MIN_NEW_SCORE = 70

    def __init__(self, gateway_client: Optional[GatewayClient] = None):
        super().__init__(gateway_client)

    @property
    def trigger_name(self) -> str:
        return "ioc_score_changed"

    @property
    def description(self) -> str:
        return "Triggers when an IOC's threat score increases significantly"

    @property
    def event_types(self) -> list[str]:
        return ["intel.ioc.score_changed"]

    def should_trigger(self, event: TriggerEvent) -> bool:
        """Check if the score increase is significant."""
        data = event.data

        previous_score = data.get("previous_score", 0)
        new_score = data.get("new_score", 0)

        # Must be an increase
        if new_score <= previous_score:
            return False

        # Calculate increase
        score_increase = new_score - previous_score

        # Check if increase is significant enough
        if score_increase < self.SCORE_INCREASE_THRESHOLD:
            return False

        # Check if new score is above minimum threshold
        if new_score < self.MIN_NEW_SCORE:
            return False

        return True

    def get_command(self, event: TriggerEvent) -> str:
        """Generate the /check-intel command."""
        ioc_value = event.data.get("ioc_value", "unknown")
        ioc_type = event.data.get("ioc_type", "unknown")
        new_score = event.data.get("new_score", 0)

        return f"/check-intel {ioc_type}:{ioc_value} --score-change --new-score {new_score}"
