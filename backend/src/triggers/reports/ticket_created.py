"""Trigger handler for ticket created events.

When a ticket is created, triggers /track-ticket to start
tracking the ticket in the SOC workflow.
"""
from typing import Any, Dict

from ..base import BaseTriggerHandler, TriggerEvent, TriggerResult


class TicketCreatedTrigger(BaseTriggerHandler):
    """Trigger that fires when a ticket is created.

    Sends /track-ticket command to start tracking.
    """

    @property
    def trigger_name(self) -> str:
        return "ticket_created"

    @property
    def description(self) -> str:
        return "Triggers ticket tracking when a new ticket is created"

    @property
    def event_types(self) -> list[str]:
        return ["ticket.created"]

    def should_trigger(self, event: TriggerEvent) -> bool:
        """Check if event should trigger tracking."""
        return "ticket_id" in event.data

    def get_command(self, event: TriggerEvent) -> str:
        """Return the /track-ticket command."""
        return "/track-ticket"

    def get_context(self, event: TriggerEvent) -> Dict[str, Any]:
        """Include ticket details in context."""
        context = super().get_context(event)
        context.update({
            "ticket_id": event.data.get("ticket_id"),
            "incident_id": event.data.get("incident_id"),
            "priority": event.data.get("priority"),
        })
        return context


__all__ = ["TicketCreatedTrigger"]
