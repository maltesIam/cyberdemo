"""Trigger handler for system health warning events.

When system health is degraded, triggers /check-health to
investigate and report on system status.
"""
from typing import Any, Dict

from ..base import BaseTriggerHandler, TriggerEvent, TriggerResult


class SystemHealthWarningTrigger(BaseTriggerHandler):
    """Trigger that fires when system health is degraded.

    Sends /check-health command to investigate.
    """

    @property
    def trigger_name(self) -> str:
        return "system_health_warning"

    @property
    def description(self) -> str:
        return "Triggers health check when system health is degraded"

    @property
    def event_types(self) -> list[str]:
        return ["system.health_degraded"]

    def should_trigger(self, event: TriggerEvent) -> bool:
        """Check if event should trigger health check."""
        return True  # All health_degraded events trigger

    def get_command(self, event: TriggerEvent) -> str:
        """Return the /check-health command."""
        return "/check-health"

    def get_context(self, event: TriggerEvent) -> Dict[str, Any]:
        """Include component details in context."""
        context = super().get_context(event)
        context.update({
            "component": event.data.get("component"),
            "status": event.data.get("status"),
            "details": event.data.get("details"),
        })
        return context


__all__ = ["SystemHealthWarningTrigger"]
