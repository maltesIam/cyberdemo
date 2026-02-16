"""Trigger handler for OpenSearch connection lost events.

When OpenSearch connection is lost, triggers /alert-ops to
notify operations team of the critical failure.
"""
from typing import Any, Dict

from ..base import BaseTriggerHandler, TriggerEvent, TriggerResult


class OpenSearchConnectionLostTrigger(BaseTriggerHandler):
    """Trigger that fires when OpenSearch connection is lost.

    Sends /alert-ops command to notify operations.
    """

    @property
    def trigger_name(self) -> str:
        return "opensearch_connection_lost"

    @property
    def description(self) -> str:
        return "Triggers ops alert when OpenSearch connection is lost"

    @property
    def event_types(self) -> list[str]:
        return ["opensearch.connection_lost"]

    def should_trigger(self, event: TriggerEvent) -> bool:
        """Check if event should trigger alert."""
        return True  # All connection_lost events trigger

    def get_command(self, event: TriggerEvent) -> str:
        """Return the /alert-ops command."""
        return "/alert-ops"

    def get_context(self, event: TriggerEvent) -> Dict[str, Any]:
        """Include connection error details in context."""
        context = super().get_context(event)
        context.update({
            "host": event.data.get("host"),
            "error": event.data.get("error"),
            "error_details": event.data.get("error"),
        })
        return context


__all__ = ["OpenSearchConnectionLostTrigger"]
