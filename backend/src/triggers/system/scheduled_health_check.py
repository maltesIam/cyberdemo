"""Trigger handler for scheduled health check events.

When a periodic health check is scheduled, triggers /health-check
to perform comprehensive system health verification.
"""
from typing import Any, Dict

from ..base import BaseTriggerHandler, TriggerEvent, TriggerResult


class ScheduledHealthCheckTrigger(BaseTriggerHandler):
    """Trigger that fires on scheduled health check.

    Sends /health-check command for periodic verification.
    """

    @property
    def trigger_name(self) -> str:
        return "scheduled_health_check"

    @property
    def description(self) -> str:
        return "Triggers periodic health check on schedule"

    @property
    def event_types(self) -> list[str]:
        return ["schedule.health_check"]

    def should_trigger(self, event: TriggerEvent) -> bool:
        """Check if event should trigger health check."""
        return True  # All schedule.health_check events trigger

    def get_command(self, event: TriggerEvent) -> str:
        """Return the /health-check command."""
        return "/health-check"

    def get_context(self, event: TriggerEvent) -> Dict[str, Any]:
        """Include check scope in context."""
        context = super().get_context(event)
        context.update({
            "check_type": event.data.get("check_type", "full"),
            "scope": event.data.get("scope", []),
        })
        return context


__all__ = ["ScheduledHealthCheckTrigger"]
