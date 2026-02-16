"""
Configuration models for the SOC platform.

Defines policy engine configuration, integration settings, and API keys.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PolicyConfig(BaseModel):
    """Policy Engine configuration."""
    model_config = ConfigDict(use_enum_values=True)

    auto_contain_threshold: int = Field(
        default=90,
        ge=0,
        le=100,
        description="Confidence threshold for auto-containment (0-100)",
    )
    false_positive_threshold: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Confidence threshold below which alerts are marked as false positive (0-100)",
    )
    auto_contain_enabled: bool = Field(
        default=True,
        description="Whether auto-containment is enabled",
    )
    vip_list: list[str] = Field(
        default_factory=list,
        description="List of VIP asset identifiers requiring approval",
    )
    critical_tags: list[str] = Field(
        default_factory=lambda: ["vip", "executive", "server", "domain-controller"],
        description="Asset tags that require human approval",
    )
    asset_criticality_overrides: dict[str, str] = Field(
        default_factory=dict,
        description="Asset ID to criticality level overrides (low, medium, high, critical)",
    )


class IntegrationConfig(BaseModel):
    """Integration configuration for external services."""
    model_config = ConfigDict(use_enum_values=True)

    api_keys: dict[str, str] = Field(
        default_factory=dict,
        description="API keys for external services (service_name -> key)",
    )
    webhook_urls: dict[str, str] = Field(
        default_factory=dict,
        description="Webhook URLs for integrations (integration_name -> url)",
    )
    enabled_integrations: list[str] = Field(
        default_factory=list,
        description="List of enabled integration names",
    )


class NotificationPreferences(BaseModel):
    """Notification preferences configuration."""
    model_config = ConfigDict(use_enum_values=True)

    slack_enabled: bool = Field(default=False, description="Enable Slack notifications")
    teams_enabled: bool = Field(default=False, description="Enable Teams notifications")
    email_enabled: bool = Field(default=False, description="Enable email notifications")
    webhook_enabled: bool = Field(default=False, description="Enable webhook notifications")

    slack_webhook_url: Optional[str] = Field(None, description="Slack webhook URL")
    teams_webhook_url: Optional[str] = Field(None, description="Teams webhook URL")
    email_recipients: list[str] = Field(default_factory=list, description="Email recipient addresses")
    custom_webhook_url: Optional[str] = Field(None, description="Custom webhook URL")

    # Notification triggers
    notify_on_critical: bool = Field(default=True, description="Notify on critical incidents")
    notify_on_high: bool = Field(default=True, description="Notify on high severity incidents")
    notify_on_medium: bool = Field(default=False, description="Notify on medium severity incidents")
    notify_on_containment: bool = Field(default=True, description="Notify on auto-containment actions")
    notify_on_approval_needed: bool = Field(default=True, description="Notify when approval is needed")

    # Template selection
    template_style: str = Field(default="detailed", description="Notification template style")


class SystemConfig(BaseModel):
    """Complete system configuration."""

    policy: PolicyConfig = Field(default_factory=PolicyConfig)
    integrations: IntegrationConfig = Field(default_factory=IntegrationConfig)
    notifications: NotificationPreferences = Field(default_factory=NotificationPreferences)
    last_updated: Optional[str] = Field(None, description="ISO timestamp of last update")
