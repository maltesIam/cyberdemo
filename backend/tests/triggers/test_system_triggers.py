"""Tests for system trigger handlers.

TDD RED Phase: These tests define expected behavior for system triggers.
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


class TestSystemHealthWarningTrigger:
    """Tests for system_health_warning trigger -> /check-health."""

    @pytest.fixture
    def mock_gateway_client(self):
        """Create a mock gateway client."""
        client = MagicMock()
        client.send_command = AsyncMock(return_value={"status": "success"})
        return client

    @pytest.mark.asyncio
    async def test_trigger_on_health_degraded(self, mock_gateway_client):
        """Should trigger /check-health when system health is degraded."""
        from src.triggers.system.system_health_warning import SystemHealthWarningTrigger

        trigger = SystemHealthWarningTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="system.health_degraded",
            component="api_gateway",
            status="degraded",
            details="High latency detected",
        )

        result = await trigger.process(event)

        assert result.triggered is True
        assert result.command == "/check-health"
        mock_gateway_client.send_command.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_not_trigger_on_healthy_status(self, mock_gateway_client):
        """Should not trigger when system is healthy."""
        from src.triggers.system.system_health_warning import SystemHealthWarningTrigger

        trigger = SystemHealthWarningTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="system.health_check",
            component="api_gateway",
            status="healthy",
        )

        result = await trigger.process(event)

        assert result.triggered is False
        mock_gateway_client.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_includes_component_in_context(self, mock_gateway_client):
        """Should include component info in the command context."""
        from src.triggers.system.system_health_warning import SystemHealthWarningTrigger

        trigger = SystemHealthWarningTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="system.health_degraded",
            component="database",
            status="degraded",
        )

        result = await trigger.process(event)

        assert result.triggered is True
        call_args = mock_gateway_client.send_command.call_args
        assert "database" in str(call_args)


class TestOpenSearchConnectionLostTrigger:
    """Tests for opensearch_connection_lost trigger -> /alert-ops."""

    @pytest.fixture
    def mock_gateway_client(self):
        """Create a mock gateway client."""
        client = MagicMock()
        client.send_command = AsyncMock(return_value={"status": "success"})
        return client

    @pytest.mark.asyncio
    async def test_trigger_on_opensearch_down(self, mock_gateway_client):
        """Should trigger /alert-ops when OpenSearch connection is lost."""
        from src.triggers.system.opensearch_connection_lost import OpenSearchConnectionLostTrigger

        trigger = OpenSearchConnectionLostTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="opensearch.connection_lost",
            host="opensearch.local:9200",
            error="Connection refused",
        )

        result = await trigger.process(event)

        assert result.triggered is True
        assert result.command == "/alert-ops"
        mock_gateway_client.send_command.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_not_trigger_on_connection_restored(self, mock_gateway_client):
        """Should not trigger when connection is restored."""
        from src.triggers.system.opensearch_connection_lost import OpenSearchConnectionLostTrigger

        trigger = OpenSearchConnectionLostTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="opensearch.connection_restored",
            host="opensearch.local:9200",
        )

        result = await trigger.process(event)

        assert result.triggered is False
        mock_gateway_client.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_includes_error_details_in_context(self, mock_gateway_client):
        """Should include error details in the context."""
        from src.triggers.system.opensearch_connection_lost import OpenSearchConnectionLostTrigger

        trigger = OpenSearchConnectionLostTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="opensearch.connection_lost",
            host="opensearch.local:9200",
            error="Connection timeout after 30s",
        )

        result = await trigger.process(event)

        assert result.triggered is True
        assert result.context is not None


class TestHighAlertVolumeTrigger:
    """Tests for high_alert_volume trigger -> /triage-alerts."""

    @pytest.fixture
    def mock_gateway_client(self):
        """Create a mock gateway client."""
        client = MagicMock()
        client.send_command = AsyncMock(return_value={"status": "success"})
        return client

    @pytest.mark.asyncio
    async def test_trigger_on_high_volume(self, mock_gateway_client):
        """Should trigger /triage-alerts when >100 alerts/hour."""
        from src.triggers.system.high_alert_volume import HighAlertVolumeTrigger

        trigger = HighAlertVolumeTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="alerts.volume_threshold",
            count=150,
            period="1h",
            threshold=100,
        )

        result = await trigger.process(event)

        assert result.triggered is True
        assert result.command == "/triage-alerts"
        mock_gateway_client.send_command.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_not_trigger_below_threshold(self, mock_gateway_client):
        """Should not trigger when alert count is below threshold."""
        from src.triggers.system.high_alert_volume import HighAlertVolumeTrigger

        trigger = HighAlertVolumeTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="alerts.volume_threshold",
            count=50,
            period="1h",
            threshold=100,
        )

        result = await trigger.process(event)

        assert result.triggered is False
        mock_gateway_client.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_configurable_threshold(self, mock_gateway_client):
        """Should respect custom threshold configuration."""
        from src.triggers.system.high_alert_volume import HighAlertVolumeTrigger

        trigger = HighAlertVolumeTrigger(
            gateway_client=mock_gateway_client,
            threshold=50  # Custom lower threshold
        )

        event = make_event(
            event_type="alerts.volume_threshold",
            count=75,
            period="1h",
        )

        result = await trigger.process(event)

        assert result.triggered is True
        mock_gateway_client.send_command.assert_called_once()


class TestScheduledHealthCheckTrigger:
    """Tests for scheduled_health_check trigger -> /health-check."""

    @pytest.fixture
    def mock_gateway_client(self):
        """Create a mock gateway client."""
        client = MagicMock()
        client.send_command = AsyncMock(return_value={"status": "success"})
        return client

    @pytest.mark.asyncio
    async def test_trigger_on_scheduled_check(self, mock_gateway_client):
        """Should trigger /health-check on scheduled event."""
        from src.triggers.system.scheduled_health_check import ScheduledHealthCheckTrigger

        trigger = ScheduledHealthCheckTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="schedule.health_check",
            check_type="full",
        )

        result = await trigger.process(event)

        assert result.triggered is True
        assert result.command == "/health-check"
        mock_gateway_client.send_command.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_not_trigger_on_other_schedules(self, mock_gateway_client):
        """Should not trigger on non-health-check schedules."""
        from src.triggers.system.scheduled_health_check import ScheduledHealthCheckTrigger

        trigger = ScheduledHealthCheckTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="schedule.backup",
        )

        result = await trigger.process(event)

        assert result.triggered is False
        mock_gateway_client.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_includes_check_scope_in_context(self, mock_gateway_client):
        """Should include check scope/type in context."""
        from src.triggers.system.scheduled_health_check import ScheduledHealthCheckTrigger

        trigger = ScheduledHealthCheckTrigger(gateway_client=mock_gateway_client)

        event = make_event(
            event_type="schedule.health_check",
            check_type="opensearch",
            scope=["opensearch", "api", "database"],
        )

        result = await trigger.process(event)

        assert result.triggered is True
        assert result.context is not None
        # Check that scope info is passed
        call_args = mock_gateway_client.send_command.call_args
        assert "opensearch" in str(call_args)
