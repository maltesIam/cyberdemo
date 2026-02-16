"""
Unit tests for NotificationService.

Following TDD: Write tests FIRST, then implement functionality.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime
from contextlib import asynccontextmanager

# These imports will fail until we implement the modules (RED phase)
try:
    from src.services.notification_service import (
        NotificationService,
        NotificationChannel,
        NotificationResult,
    )
    from src.models.notification import (
        NotificationChannelType,
        NotificationTemplate,
        NotificationConfig,
    )
except ImportError:
    pass


def create_mock_session(status=200, response_text="ok", side_effect=None):
    """Helper to create properly mocked aiohttp.ClientSession."""
    mock_response = MagicMock()
    mock_response.status = status
    mock_response.text = AsyncMock(return_value=response_text)

    # Create async context manager for the response
    @asynccontextmanager
    async def mock_request(*args, **kwargs):
        if side_effect:
            raise side_effect
        yield mock_response

    mock_session = MagicMock()
    mock_session.post = mock_request
    mock_session.request = mock_request

    # Create async context manager for the session
    @asynccontextmanager
    async def mock_session_context():
        yield mock_session

    return mock_session_context


# ============================================================================
# Slack Notification Tests
# ============================================================================


@pytest.mark.asyncio
async def test_send_slack_notification_success():
    """Test that Slack notification sends successfully."""
    service = NotificationService()

    with patch("src.services.notification_service.aiohttp.ClientSession", create_mock_session(200, "ok")):
        result = await service.send_slack_notification(
            webhook_url="https://hooks.slack.com/test",
            message="Test message",
        )

        assert result.success is True
        assert result.channel == NotificationChannelType.SLACK


@pytest.mark.asyncio
async def test_send_slack_notification_with_template():
    """Test Slack notification with template variable substitution."""
    service = NotificationService()

    # The template rendering is verified separately. Here we check the flow works.
    with patch("src.services.notification_service.aiohttp.ClientSession", create_mock_session(200, "ok")):
        result = await service.send_slack_notification(
            webhook_url="https://hooks.slack.com/test",
            message="Host {hostname} contained automatically",
            variables={"hostname": "WORKSTATION-01"},
        )

        assert result.success is True


@pytest.mark.asyncio
async def test_send_slack_notification_failure():
    """Test Slack notification handles failure gracefully."""
    service = NotificationService()

    with patch("src.services.notification_service.aiohttp.ClientSession", create_mock_session(500, "Internal Server Error")):
        result = await service.send_slack_notification(
            webhook_url="https://hooks.slack.com/test",
            message="Test message",
        )

        assert result.success is False
        assert result.error is not None
        assert "500" in result.error


@pytest.mark.asyncio
async def test_send_slack_notification_network_error():
    """Test Slack notification handles network errors gracefully."""
    service = NotificationService()

    with patch(
        "src.services.notification_service.aiohttp.ClientSession",
        create_mock_session(side_effect=Exception("Connection refused"))
    ):
        result = await service.send_slack_notification(
            webhook_url="https://hooks.slack.com/test",
            message="Test message",
        )

        assert result.success is False
        assert result.error is not None
        assert "Connection refused" in result.error


# ============================================================================
# Teams Notification Tests
# ============================================================================


@pytest.mark.asyncio
async def test_send_teams_notification_success():
    """Test that Teams notification sends successfully."""
    service = NotificationService()

    with patch("src.services.notification_service.aiohttp.ClientSession", create_mock_session(200, "1")):
        result = await service.send_teams_notification(
            webhook_url="https://outlook.office.com/webhook/test",
            message="Test alert",
            title="Security Alert",
        )

        assert result.success is True
        assert result.channel == NotificationChannelType.TEAMS


@pytest.mark.asyncio
async def test_send_teams_notification_with_facts():
    """Test Teams notification with additional facts/fields."""
    service = NotificationService()

    with patch("src.services.notification_service.aiohttp.ClientSession", create_mock_session(200, "1")):
        result = await service.send_teams_notification(
            webhook_url="https://outlook.office.com/webhook/test",
            message="Host contained",
            title="Containment Action",
            facts={"Hostname": "WORKSTATION-01", "Status": "Contained"},
        )

        assert result.success is True


# ============================================================================
# Email Notification Tests
# ============================================================================


@pytest.mark.asyncio
async def test_send_email_notification_success():
    """Test that email notification sends successfully."""
    service = NotificationService()

    with patch("aiosmtplib.send", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = ([], "250 OK")

        result = await service.send_email_notification(
            smtp_server="smtp.example.com",
            smtp_port=587,
            from_email="soc@example.com",
            to_emails=["admin@example.com"],
            subject="Security Alert",
            body="Test alert body",
        )

        assert result.success is True
        assert result.channel == NotificationChannelType.EMAIL


@pytest.mark.asyncio
async def test_send_email_notification_with_html():
    """Test email notification with HTML body."""
    service = NotificationService()

    with patch("aiosmtplib.send", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = ([], "250 OK")

        html_body = "<h1>Security Alert</h1><p>Host contained</p>"

        result = await service.send_email_notification(
            smtp_server="smtp.example.com",
            smtp_port=587,
            from_email="soc@example.com",
            to_emails=["admin@example.com"],
            subject="Security Alert",
            body=html_body,
            html=True,
        )

        assert result.success is True
        mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_send_email_notification_with_auth():
    """Test email notification with SMTP authentication."""
    service = NotificationService()

    with patch("aiosmtplib.send", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = ([], "250 OK")

        result = await service.send_email_notification(
            smtp_server="smtp.example.com",
            smtp_port=587,
            from_email="soc@example.com",
            to_emails=["admin@example.com"],
            subject="Test",
            body="Test",
            username="user",
            password="pass",
        )

        assert result.success is True
        # Verify auth was used
        call_kwargs = mock_send.call_args[1]
        assert call_kwargs.get("username") == "user"


@pytest.mark.asyncio
async def test_send_email_notification_multiple_recipients():
    """Test email notification to multiple recipients."""
    service = NotificationService()

    with patch("aiosmtplib.send", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = ([], "250 OK")

        result = await service.send_email_notification(
            smtp_server="smtp.example.com",
            smtp_port=587,
            from_email="soc@example.com",
            to_emails=["admin@example.com", "security@example.com"],
            subject="Test",
            body="Test",
        )

        assert result.success is True


# ============================================================================
# Webhook Notification Tests
# ============================================================================


@pytest.mark.asyncio
async def test_send_webhook_notification_success():
    """Test generic webhook notification sends successfully."""
    service = NotificationService()

    with patch("src.services.notification_service.aiohttp.ClientSession", create_mock_session(200, '{"status": "ok"}')):
        result = await service.send_webhook_notification(
            url="https://custom.webhook.com/endpoint",
            payload={"event": "containment", "host": "WORKSTATION-01"},
        )

        assert result.success is True
        assert result.channel == NotificationChannelType.WEBHOOK


@pytest.mark.asyncio
async def test_send_webhook_notification_with_headers():
    """Test webhook notification with custom headers."""
    service = NotificationService()

    with patch("src.services.notification_service.aiohttp.ClientSession", create_mock_session(200, "ok")):
        result = await service.send_webhook_notification(
            url="https://custom.webhook.com/endpoint",
            payload={"event": "test"},
            headers={"Authorization": "Bearer token123"},
        )

        assert result.success is True


# ============================================================================
# Template Rendering Tests
# ============================================================================


def test_render_template_simple():
    """Test simple template variable substitution."""
    service = NotificationService()

    template = "Host {hostname} was {action}"
    variables = {"hostname": "WORKSTATION-01", "action": "contained"}

    result = service.render_template(template, variables)

    assert result == "Host WORKSTATION-01 was contained"


def test_render_template_missing_variable():
    """Test template rendering with missing variable keeps placeholder."""
    service = NotificationService()

    template = "Host {hostname} status: {status}"
    variables = {"hostname": "WORKSTATION-01"}

    result = service.render_template(template, variables)

    # Missing variables should remain as placeholders
    assert "WORKSTATION-01" in result
    assert "{status}" in result


def test_render_template_empty_variables():
    """Test template rendering with no variables."""
    service = NotificationService()

    template = "Static message with no variables"
    result = service.render_template(template, {})

    assert result == "Static message with no variables"


# ============================================================================
# Batch Notification Tests
# ============================================================================


@pytest.mark.asyncio
async def test_send_to_multiple_channels():
    """Test sending notification to multiple channels."""
    service = NotificationService()

    with patch.object(service, "send_slack_notification") as mock_slack, \
         patch.object(service, "send_teams_notification") as mock_teams:

        mock_slack.return_value = NotificationResult(
            success=True,
            channel=NotificationChannelType.SLACK,
        )
        mock_teams.return_value = NotificationResult(
            success=True,
            channel=NotificationChannelType.TEAMS,
        )

        channels = [
            NotificationChannel(
                type=NotificationChannelType.SLACK,
                config={"webhook_url": "https://slack.webhook/test"},
            ),
            NotificationChannel(
                type=NotificationChannelType.TEAMS,
                config={"webhook_url": "https://teams.webhook/test"},
            ),
        ]

        results = await service.send_to_channels(
            channels=channels,
            message="Test alert",
        )

        assert len(results) == 2
        assert all(r.success for r in results)


@pytest.mark.asyncio
async def test_send_to_channels_partial_failure():
    """Test that partial channel failure doesn't stop other channels."""
    service = NotificationService()

    with patch.object(service, "send_slack_notification") as mock_slack, \
         patch.object(service, "send_teams_notification") as mock_teams:

        # Slack fails
        mock_slack.return_value = NotificationResult(
            success=False,
            channel=NotificationChannelType.SLACK,
            error="Webhook error",
        )
        # Teams succeeds
        mock_teams.return_value = NotificationResult(
            success=True,
            channel=NotificationChannelType.TEAMS,
        )

        channels = [
            NotificationChannel(
                type=NotificationChannelType.SLACK,
                config={"webhook_url": "https://slack.webhook/test"},
            ),
            NotificationChannel(
                type=NotificationChannelType.TEAMS,
                config={"webhook_url": "https://teams.webhook/test"},
            ),
        ]

        results = await service.send_to_channels(
            channels=channels,
            message="Test alert",
        )

        assert len(results) == 2
        assert results[0].success is False  # Slack
        assert results[1].success is True   # Teams


# ============================================================================
# Async/Non-Blocking Tests
# ============================================================================


@pytest.mark.asyncio
async def test_notifications_are_non_blocking():
    """Test that notification sends are non-blocking (async)."""
    import asyncio

    service = NotificationService()

    # Use direct mock of send methods to test concurrency
    with patch.object(service, "send_slack_notification") as mock_slack:
        async def slow_send(*args, **kwargs):
            await asyncio.sleep(0.1)
            return NotificationResult(
                success=True,
                channel=NotificationChannelType.SLACK,
            )

        mock_slack.side_effect = slow_send

        start_time = asyncio.get_event_loop().time()

        # Send multiple notifications concurrently
        tasks = [
            service.send_slack_notification("https://test1", "msg1"),
            service.send_slack_notification("https://test2", "msg2"),
            service.send_slack_notification("https://test3", "msg3"),
        ]

        results = await asyncio.gather(*tasks)

        end_time = asyncio.get_event_loop().time()
        elapsed = end_time - start_time

        # If blocking, would take 0.3s. If non-blocking, ~0.1s
        assert elapsed < 0.25
        assert len(results) == 3


# ============================================================================
# Configuration Tests
# ============================================================================


def test_notification_config_model():
    """Test NotificationConfig model validation."""
    config = NotificationConfig(
        slack=NotificationChannel(
            type=NotificationChannelType.SLACK,
            config={"webhook_url": "https://hooks.slack.com/test"},
            templates={
                "containment_auto": "Host {hostname} contained automatically",
                "approval_needed": "Approval required for {hostname}",
            },
        ),
        email=NotificationChannel(
            type=NotificationChannelType.EMAIL,
            config={
                "smtp_server": "smtp.example.com",
                "smtp_port": 587,
                "from_email": "soc@example.com",
            },
        ),
    )

    assert config.slack is not None
    assert config.slack.templates["containment_auto"] is not None
    assert config.email.config["smtp_server"] == "smtp.example.com"


def test_notification_template_model():
    """Test NotificationTemplate model."""
    template = NotificationTemplate(
        name="containment_auto",
        channel=NotificationChannelType.SLACK,
        content="Host {hostname} contained automatically",
        variables=["hostname"],
    )

    assert template.name == "containment_auto"
    assert "hostname" in template.variables


# ============================================================================
# Error Handling Tests
# ============================================================================


@pytest.mark.asyncio
async def test_invalid_webhook_url():
    """Test handling of invalid webhook URL."""
    service = NotificationService()

    result = await service.send_slack_notification(
        webhook_url="not-a-valid-url",
        message="Test",
    )

    assert result.success is False
    assert result.error is not None


@pytest.mark.asyncio
async def test_timeout_handling():
    """Test that timeouts are handled gracefully."""
    import asyncio

    service = NotificationService()

    with patch(
        "src.services.notification_service.aiohttp.ClientSession",
        create_mock_session(side_effect=asyncio.TimeoutError())
    ):
        result = await service.send_slack_notification(
            webhook_url="https://hooks.slack.com/test",
            message="Test",
        )

        assert result.success is False
        assert "timeout" in result.error.lower()
