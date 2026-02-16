"""Trigger handler for incident closed events.

When an incident is closed, triggers /generate-summary to create
a summary report of the incident resolution.
"""
from typing import Any, Dict

from ..base import BaseTriggerHandler, TriggerEvent, TriggerResult


class IncidentClosedTrigger(BaseTriggerHandler):
    """Trigger that fires when an incident is closed.

    Sends /generate-summary command to create incident summary.
    """

    @property
    def trigger_name(self) -> str:
        return "incident_closed"

    @property
    def description(self) -> str:
        return "Triggers summary generation when an incident is closed"

    @property
    def event_types(self) -> list[str]:
        return ["incident.closed"]

    def should_trigger(self, event: TriggerEvent) -> bool:
        """Check if event should trigger summary generation.

        Requires incident_id in event data.
        """
        return "incident_id" in event.data

    def get_command(self, event: TriggerEvent) -> str:
        """Return the /generate-summary command."""
        return "/generate-summary"

    def get_context(self, event: TriggerEvent) -> Dict[str, Any]:
        """Include incident details in context."""
        context = super().get_context(event)
        context.update({
            "incident_id": event.data.get("incident_id"),
            "closed_by": event.data.get("closed_by"),
            "resolution": event.data.get("resolution"),
        })
        return context

    async def process(self, event: TriggerEvent) -> TriggerResult:
        """Process the event with validation."""
        # Check event type first
        if event.event_type not in self.event_types:
            return TriggerResult(
                triggered=False,
                message=f"Event type {event.event_type} not handled"
            )

        # Validate incident_id is present
        if "incident_id" not in event.data:
            return TriggerResult(
                triggered=False,
                error="Missing required field: incident_id"
            )

        # Use parent process for standard flow
        return await super().process(event)


__all__ = ["IncidentClosedTrigger"]
