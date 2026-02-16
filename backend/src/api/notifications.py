"""Notifications API for configuring and testing notification channels."""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..models.notification import (
    NotificationChannelType,
    NotificationChannel,
    NotificationConfig,
    NotificationResult,
    TestNotificationRequest,
)
from ..services.notification_service import NotificationService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Notifications"])

# In-memory configuration store (in production, use database/config service)
_notification_config: Optional[NotificationConfig] = None

# Singleton service instance
_notification_service = NotificationService()


def _get_config() -> NotificationConfig:
    """Get current notification configuration."""
    global _notification_config
    if _notification_config is None:
        # Return default empty config
        _notification_config = NotificationConfig()
    return _notification_config


def _set_config(config: NotificationConfig) -> None:
    """Set notification configuration."""
    global _notification_config
    _notification_config = config


class NotificationConfigResponse(BaseModel):
    """Response model for notification configuration."""

    slack: Optional[NotificationChannel] = None
    teams: Optional[NotificationChannel] = None
    email: Optional[NotificationChannel] = None
    webhook: Optional[NotificationChannel] = None
    last_updated: Optional[str] = None


class UpdateNotificationConfigRequest(BaseModel):
    """Request model for updating notification configuration."""

    slack: Optional[NotificationChannel] = None
    teams: Optional[NotificationChannel] = None
    email: Optional[NotificationChannel] = None
    webhook: Optional[NotificationChannel] = None


class TestNotificationResponse(BaseModel):
    """Response model for test notification result."""

    success: bool
    channel: str
    message: Optional[str] = None
    error: Optional[str] = None
    timestamp: str


@router.get("/config/notifications", response_model=NotificationConfigResponse)
async def get_notification_config():
    """Get current notification configuration.

    Returns the configuration for all notification channels (Slack, Teams, Email, Webhook).
    Sensitive values like passwords and webhook URLs are partially masked.
    """
    config = _get_config()

    # Mask sensitive values for security
    response = NotificationConfigResponse(
        slack=_mask_channel_config(config.slack) if config.slack else None,
        teams=_mask_channel_config(config.teams) if config.teams else None,
        email=_mask_channel_config(config.email) if config.email else None,
        webhook=_mask_channel_config(config.webhook) if config.webhook else None,
        last_updated=datetime.utcnow().isoformat(),
    )

    return response


@router.put("/config/notifications", response_model=NotificationConfigResponse)
async def update_notification_config(request: UpdateNotificationConfigRequest):
    """Update notification configuration.

    Updates the configuration for notification channels. Only provided channels
    will be updated; others remain unchanged.

    Args:
        request: Updated channel configurations.

    Returns:
        Updated configuration (with sensitive values masked).
    """
    current_config = _get_config()

    # Update only provided channels
    new_config = NotificationConfig(
        slack=request.slack if request.slack is not None else current_config.slack,
        teams=request.teams if request.teams is not None else current_config.teams,
        email=request.email if request.email is not None else current_config.email,
        webhook=request.webhook if request.webhook is not None else current_config.webhook,
    )

    _set_config(new_config)
    logger.info("Notification configuration updated")

    # Return masked config
    return NotificationConfigResponse(
        slack=_mask_channel_config(new_config.slack) if new_config.slack else None,
        teams=_mask_channel_config(new_config.teams) if new_config.teams else None,
        email=_mask_channel_config(new_config.email) if new_config.email else None,
        webhook=_mask_channel_config(new_config.webhook) if new_config.webhook else None,
        last_updated=datetime.utcnow().isoformat(),
    )


@router.post("/notifications/test", response_model=TestNotificationResponse)
async def test_notification(request: TestNotificationRequest):
    """Send a test notification to verify channel configuration.

    Sends a test message to the specified channel using the current configuration.
    Useful for verifying webhook URLs, SMTP settings, etc.

    Args:
        request: Channel to test and optional custom message.

    Returns:
        Result of the test notification.
    """
    config = _get_config()
    channel = None
    channel_type = request.channel

    # Get channel config
    if channel_type == NotificationChannelType.SLACK:
        channel = config.slack
    elif channel_type == NotificationChannelType.TEAMS:
        channel = config.teams
    elif channel_type == NotificationChannelType.EMAIL:
        channel = config.email
    elif channel_type == NotificationChannelType.WEBHOOK:
        channel = config.webhook

    if not channel:
        raise HTTPException(
            status_code=404,
            detail=f"Channel {channel_type} is not configured"
        )

    if not channel.enabled:
        raise HTTPException(
            status_code=400,
            detail=f"Channel {channel_type} is disabled"
        )

    # Send test notification
    result: NotificationResult

    if channel_type == NotificationChannelType.SLACK:
        webhook_url = channel.config.get("webhook_url", "")
        result = await _notification_service.send_slack_notification(
            webhook_url=webhook_url,
            message=request.message,
        )

    elif channel_type == NotificationChannelType.TEAMS:
        webhook_url = channel.config.get("webhook_url", "")
        result = await _notification_service.send_teams_notification(
            webhook_url=webhook_url,
            message=request.message,
            title="Test Notification",
        )

    elif channel_type == NotificationChannelType.EMAIL:
        result = await _notification_service.send_email_notification(
            smtp_server=channel.config.get("smtp_server", ""),
            smtp_port=channel.config.get("smtp_port", 587),
            from_email=channel.config.get("from_email", ""),
            to_emails=channel.config.get("to_emails", []),
            subject="CyberDemo SOC - Test Notification",
            body=request.message,
            username=channel.config.get("username"),
            password=channel.config.get("password"),
        )

    elif channel_type == NotificationChannelType.WEBHOOK:
        url = channel.config.get("url", "")
        result = await _notification_service.send_webhook_notification(
            url=url,
            payload={"test": True, "message": request.message},
            headers=channel.config.get("headers"),
        )

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported channel type: {channel_type}"
        )

    return TestNotificationResponse(
        success=result.success,
        channel=channel_type.value,
        message="Test notification sent successfully" if result.success else None,
        error=result.error,
        timestamp=result.timestamp or datetime.utcnow().isoformat(),
    )


@router.get("/notifications/channels")
async def list_channels():
    """List available notification channels and their status.

    Returns a summary of all channels and whether they are configured/enabled.
    """
    config = _get_config()

    channels = []
    for channel_type in NotificationChannelType:
        channel = None
        if channel_type == NotificationChannelType.SLACK:
            channel = config.slack
        elif channel_type == NotificationChannelType.TEAMS:
            channel = config.teams
        elif channel_type == NotificationChannelType.EMAIL:
            channel = config.email
        elif channel_type == NotificationChannelType.WEBHOOK:
            channel = config.webhook

        channels.append({
            "type": channel_type.value,
            "configured": channel is not None,
            "enabled": channel.enabled if channel else False,
            "templates_count": len(channel.templates) if channel else 0,
        })

    return {"channels": channels}


@router.get("/notifications/templates")
async def list_templates():
    """List all notification templates across channels.

    Returns templates configured for each channel.
    """
    config = _get_config()
    templates = []

    for channel_type, channel in [
        (NotificationChannelType.SLACK, config.slack),
        (NotificationChannelType.TEAMS, config.teams),
        (NotificationChannelType.EMAIL, config.email),
        (NotificationChannelType.WEBHOOK, config.webhook),
    ]:
        if channel and channel.templates:
            for name, content in channel.templates.items():
                templates.append({
                    "name": name,
                    "channel": channel_type.value,
                    "content": content,
                })

    return {"templates": templates, "total": len(templates)}


def _mask_channel_config(channel: NotificationChannel) -> NotificationChannel:
    """Mask sensitive values in channel configuration.

    Args:
        channel: Channel configuration to mask.

    Returns:
        Channel with masked sensitive values.
    """
    if not channel:
        return channel

    masked_config = dict(channel.config)

    # Mask webhook URLs (show first 20 and last 10 chars)
    for key in ["webhook_url", "url"]:
        if key in masked_config and masked_config[key]:
            url = masked_config[key]
            if len(url) > 40:
                masked_config[key] = f"{url[:20]}...{url[-10:]}"

    # Mask passwords completely
    for key in ["password", "secret", "api_key"]:
        if key in masked_config:
            masked_config[key] = "********"

    return NotificationChannel(
        type=channel.type,
        enabled=channel.enabled,
        config=masked_config,
        templates=channel.templates,
    )
