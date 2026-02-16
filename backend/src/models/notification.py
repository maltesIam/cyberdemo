"""
Notification models for the SOC platform.

Defines channel types, templates, and configuration for multi-channel notifications.
"""
import enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class NotificationChannelType(str, enum.Enum):
    """Supported notification channel types."""
    SLACK = "slack"
    TEAMS = "teams"
    EMAIL = "email"
    WEBHOOK = "webhook"


class NotificationTemplate(BaseModel):
    """Template for notification messages."""
    model_config = ConfigDict(use_enum_values=True)

    name: str = Field(..., description="Template identifier")
    channel: NotificationChannelType = Field(..., description="Target channel")
    content: str = Field(..., description="Template content with {variable} placeholders")
    variables: list[str] = Field(
        default_factory=list,
        description="List of variable names expected in the template",
    )
    description: Optional[str] = Field(None, description="Human-readable description")


class NotificationChannel(BaseModel):
    """Configuration for a notification channel."""
    model_config = ConfigDict(use_enum_values=True)

    type: NotificationChannelType = Field(..., description="Channel type")
    enabled: bool = Field(True, description="Whether channel is active")
    config: dict = Field(
        default_factory=dict,
        description="Channel-specific configuration (webhook_url, smtp settings, etc.)",
    )
    templates: dict[str, str] = Field(
        default_factory=dict,
        description="Named templates for this channel (name -> template content)",
    )


class NotificationConfig(BaseModel):
    """Complete notification configuration for the SOC platform."""

    slack: Optional[NotificationChannel] = Field(
        None,
        description="Slack configuration",
    )
    teams: Optional[NotificationChannel] = Field(
        None,
        description="Microsoft Teams configuration",
    )
    email: Optional[NotificationChannel] = Field(
        None,
        description="Email/SMTP configuration",
    )
    webhook: Optional[NotificationChannel] = Field(
        None,
        description="Generic webhook configuration",
    )

    def get_enabled_channels(self) -> list[NotificationChannel]:
        """Return list of enabled channels."""
        channels = []
        for ch in [self.slack, self.teams, self.email, self.webhook]:
            if ch and ch.enabled:
                channels.append(ch)
        return channels


class NotificationResult(BaseModel):
    """Result of a notification send attempt."""
    model_config = ConfigDict(use_enum_values=True)

    success: bool = Field(..., description="Whether notification was sent successfully")
    channel: NotificationChannelType = Field(..., description="Channel used")
    message_id: Optional[str] = Field(None, description="External message ID if available")
    error: Optional[str] = Field(None, description="Error message if failed")
    timestamp: Optional[str] = Field(None, description="ISO timestamp of send attempt")


class TestNotificationRequest(BaseModel):
    """Request to send a test notification."""
    model_config = ConfigDict(use_enum_values=True)

    channel: NotificationChannelType = Field(..., description="Channel to test")
    message: str = Field("Test notification from CyberDemo SOC", description="Test message")
