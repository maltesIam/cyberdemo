"""Trigger handler for daily summary schedule events.

When the daily summary is scheduled, triggers /daily-report
to generate the daily SOC report.
"""
from typing import Any, Dict
from datetime import datetime, timedelta

from ..base import BaseTriggerHandler, TriggerEvent, TriggerResult


class DailySummaryTrigger(BaseTriggerHandler):
    """Trigger that fires on daily summary schedule.

    Sends /daily-report command to generate daily report.
    """

    @property
    def trigger_name(self) -> str:
        return "daily_summary"

    @property
    def description(self) -> str:
        return "Triggers daily report generation on schedule"

    @property
    def event_types(self) -> list[str]:
        return ["schedule.daily_summary"]

    def should_trigger(self, event: TriggerEvent) -> bool:
        """Check if event should trigger daily report."""
        return True  # All daily_summary events trigger

    def get_command(self, event: TriggerEvent) -> str:
        """Return the /daily-report command."""
        return "/daily-report"

    def get_context(self, event: TriggerEvent) -> Dict[str, Any]:
        """Include date range in context."""
        context = super().get_context(event)

        # Calculate date range (last 24 hours)
        end_date = event.timestamp
        start_date = end_date - timedelta(days=1)

        context.update({
            "period": event.data.get("period", "daily"),
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
        })
        return context


__all__ = ["DailySummaryTrigger"]
