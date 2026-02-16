"""Trigger handler for postmortem generated events.

When a postmortem is ready, triggers /notify-team to inform
the relevant team members.
"""
from typing import Any, Dict

from ..base import BaseTriggerHandler, TriggerEvent, TriggerResult


class PostmortemGeneratedTrigger(BaseTriggerHandler):
    """Trigger that fires when a postmortem is ready.

    Sends /notify-team command to alert team members.
    """

    @property
    def trigger_name(self) -> str:
        return "postmortem_generated"

    @property
    def description(self) -> str:
        return "Triggers team notification when a postmortem is ready"

    @property
    def event_types(self) -> list[str]:
        return ["postmortem.ready"]

    def should_trigger(self, event: TriggerEvent) -> bool:
        """Check if event should trigger notification."""
        return True  # All postmortem.ready events trigger

    def get_command(self, event: TriggerEvent) -> str:
        """Return the /notify-team command."""
        return "/notify-team"

    def get_context(self, event: TriggerEvent) -> Dict[str, Any]:
        """Include postmortem details in context."""
        context = super().get_context(event)
        context.update({
            "incident_id": event.data.get("incident_id"),
            "postmortem_id": event.data.get("postmortem_id"),
        })
        return context


__all__ = ["PostmortemGeneratedTrigger"]
