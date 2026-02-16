"""Tests for report trigger handlers.

TDD RED Phase: These tests define expected behavior for report triggers.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.triggers.base import TriggerEvent


def make_event(event_type: str, source: str = "test", **data) -> TriggerEvent:
    """Helper to create TriggerEvent instances."""
    return TriggerEvent(
        event_type=event_type,
        source=source,
        timestamp=datetime.now(),
        data=data,
    )


class TestIncidentClosedTrigger:
    """Tests for incident_closed trigger -> /generate-summary."""

    @pytest.fixture
    def mock_gateway_client(self):
        """Create a mock gateway client."""
        client = MagicMock()
        client.send_command = AsyncMock(return_value={"status": "success"})
        return client

    @pytest.mark.asyncio
    async def test_trigger_on_incident_closed(self, mock_gateway_client):
        """Should trigger /generate-summary when incident is closed."""
        from src.triggers.reports.incident_closed import IncidentClosedTrigger

        trigger = IncidentClosedTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="incident.closed",
            incident_id="INC-2024-001",
            closed_by="analyst@soc.local",
            resolution="confirmed_malicious",
        )

        result = await trigger.process(event)

        assert result.triggered is True
        assert result.command == "/generate-summary"
        mock_gateway_client.send_command.assert_called_once()
        call_args = mock_gateway_client.send_command.call_args
        assert "INC-2024-001" in str(call_args)

    @pytest.mark.asyncio
    async def test_should_not_trigger_on_other_events(self, mock_gateway_client):
        """Should not trigger on non-incident-closed events."""
        from src.triggers.reports.incident_closed import IncidentClosedTrigger

        trigger = IncidentClosedTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="incident.created",
            incident_id="INC-2024-002",
        )

        result = await trigger.process(event)

        assert result.triggered is False
        mock_gateway_client.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_validates_incident_id_present(self, mock_gateway_client):
        """Should require incident_id in event data."""
        from src.triggers.reports.incident_closed import IncidentClosedTrigger

        trigger = IncidentClosedTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="incident.closed",
            # Missing incident_id
        )

        result = await trigger.process(event)

        assert result.triggered is False
        assert result.error is not None
        mock_gateway_client.send_command.assert_not_called()


class TestPostmortemGeneratedTrigger:
    """Tests for postmortem_generated trigger -> /notify-team."""

    @pytest.fixture
    def mock_gateway_client(self):
        """Create a mock gateway client."""
        client = MagicMock()
        client.send_command = AsyncMock(return_value={"status": "success"})
        return client

    @pytest.mark.asyncio
    async def test_trigger_on_postmortem_ready(self, mock_gateway_client):
        """Should trigger /notify-team when postmortem is generated."""
        from src.triggers.reports.postmortem_generated import PostmortemGeneratedTrigger

        trigger = PostmortemGeneratedTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="postmortem.ready",
            incident_id="INC-2024-001",
            postmortem_id="PM-2024-001",
        )

        result = await trigger.process(event)

        assert result.triggered is True
        assert result.command == "/notify-team"
        mock_gateway_client.send_command.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_not_trigger_on_draft_postmortem(self, mock_gateway_client):
        """Should not trigger if postmortem is still draft."""
        from src.triggers.reports.postmortem_generated import PostmortemGeneratedTrigger

        trigger = PostmortemGeneratedTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="postmortem.draft",
            incident_id="INC-2024-001",
        )

        result = await trigger.process(event)

        assert result.triggered is False
        mock_gateway_client.send_command.assert_not_called()


class TestTicketCreatedTrigger:
    """Tests for ticket_created trigger -> /track-ticket."""

    @pytest.fixture
    def mock_gateway_client(self):
        """Create a mock gateway client."""
        client = MagicMock()
        client.send_command = AsyncMock(return_value={"status": "success"})
        return client

    @pytest.mark.asyncio
    async def test_trigger_on_ticket_created(self, mock_gateway_client):
        """Should trigger /track-ticket when ticket is created."""
        from src.triggers.reports.ticket_created import TicketCreatedTrigger

        trigger = TicketCreatedTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="ticket.created",
            ticket_id="JIRA-SOC-123",
            incident_id="INC-2024-001",
            priority="high",
        )

        result = await trigger.process(event)

        assert result.triggered is True
        assert result.command == "/track-ticket"
        mock_gateway_client.send_command.assert_called_once()
        call_args = mock_gateway_client.send_command.call_args
        assert "JIRA-SOC-123" in str(call_args)

    @pytest.mark.asyncio
    async def test_should_not_trigger_on_ticket_update(self, mock_gateway_client):
        """Should not trigger on ticket update events."""
        from src.triggers.reports.ticket_created import TicketCreatedTrigger

        trigger = TicketCreatedTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="ticket.updated",
            ticket_id="JIRA-SOC-123",
        )

        result = await trigger.process(event)

        assert result.triggered is False
        mock_gateway_client.send_command.assert_not_called()


class TestDailySummaryTrigger:
    """Tests for daily_summary trigger -> /daily-report."""

    @pytest.fixture
    def mock_gateway_client(self):
        """Create a mock gateway client."""
        client = MagicMock()
        client.send_command = AsyncMock(return_value={"status": "success"})
        return client

    @pytest.mark.asyncio
    async def test_trigger_on_scheduled_daily(self, mock_gateway_client):
        """Should trigger /daily-report on scheduled event."""
        from src.triggers.reports.daily_summary import DailySummaryTrigger

        trigger = DailySummaryTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="schedule.daily_summary",
            period="daily",
        )

        result = await trigger.process(event)

        assert result.triggered is True
        assert result.command == "/daily-report"
        mock_gateway_client.send_command.assert_called_once()

    @pytest.mark.asyncio
    async def test_includes_date_range_in_context(self, mock_gateway_client):
        """Should include date range in the command context."""
        from src.triggers.reports.daily_summary import DailySummaryTrigger

        trigger = DailySummaryTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="schedule.daily_summary",
            period="daily",
        )

        result = await trigger.process(event)

        assert result.triggered is True
        # Should include context with date info
        assert result.context is not None

    @pytest.mark.asyncio
    async def test_should_not_trigger_on_other_schedules(self, mock_gateway_client):
        """Should not trigger on non-daily schedules."""
        from src.triggers.reports.daily_summary import DailySummaryTrigger

        trigger = DailySummaryTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="schedule.weekly_summary",
            period="weekly",
        )

        result = await trigger.process(event)

        assert result.triggered is False
        mock_gateway_client.send_command.assert_not_called()
