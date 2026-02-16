"""Configuration API for policy engine, integrations, and notification settings."""
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..models.config import (
    PolicyConfig,
    IntegrationConfig,
    NotificationPreferences,
    SystemConfig,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Configuration"])

# In-memory configuration store (in production, use database/config service)
_system_config: Optional[SystemConfig] = None


def _get_config() -> SystemConfig:
    """Get current system configuration."""
    global _system_config
    if _system_config is None:
        _system_config = SystemConfig()
    return _system_config


def _set_config(config: SystemConfig) -> None:
    """Set system configuration."""
    global _system_config
    config.last_updated = datetime.utcnow().isoformat()
    _system_config = config


# ============================================================================
# Policy Configuration Endpoints
# ============================================================================


class PolicyConfigResponse(BaseModel):
    """Response model for policy configuration."""

    auto_contain_threshold: int
    false_positive_threshold: int
    auto_contain_enabled: bool
    vip_list: list[str]
    critical_tags: list[str]
    asset_criticality_overrides: dict[str, str]
    last_updated: Optional[str] = None


class UpdatePolicyConfigRequest(BaseModel):
    """Request model for updating policy configuration."""

    auto_contain_threshold: Optional[int] = Field(None, ge=0, le=100)
    false_positive_threshold: Optional[int] = Field(None, ge=0, le=100)
    auto_contain_enabled: Optional[bool] = None
    vip_list: Optional[list[str]] = None
    critical_tags: Optional[list[str]] = None
    asset_criticality_overrides: Optional[dict[str, str]] = None


@router.get("/policy", response_model=PolicyConfigResponse)
async def get_policy_config():
    """Get current policy engine configuration.

    Returns the policy engine settings including thresholds and VIP asset list.
    """
    config = _get_config()

    return PolicyConfigResponse(
        auto_contain_threshold=config.policy.auto_contain_threshold,
        false_positive_threshold=config.policy.false_positive_threshold,
        auto_contain_enabled=config.policy.auto_contain_enabled,
        vip_list=config.policy.vip_list,
        critical_tags=config.policy.critical_tags,
        asset_criticality_overrides=config.policy.asset_criticality_overrides,
        last_updated=config.last_updated,
    )


@router.put("/policy", response_model=PolicyConfigResponse)
async def update_policy_config(request: UpdatePolicyConfigRequest):
    """Update policy engine configuration.

    Updates the policy engine settings. Only provided fields will be updated.
    Validates threshold ranges (0-100).
    """
    config = _get_config()

    # Update only provided fields
    new_policy = PolicyConfig(
        auto_contain_threshold=(
            request.auto_contain_threshold
            if request.auto_contain_threshold is not None
            else config.policy.auto_contain_threshold
        ),
        false_positive_threshold=(
            request.false_positive_threshold
            if request.false_positive_threshold is not None
            else config.policy.false_positive_threshold
        ),
        auto_contain_enabled=(
            request.auto_contain_enabled
            if request.auto_contain_enabled is not None
            else config.policy.auto_contain_enabled
        ),
        vip_list=(
            request.vip_list
            if request.vip_list is not None
            else config.policy.vip_list
        ),
        critical_tags=(
            request.critical_tags
            if request.critical_tags is not None
            else config.policy.critical_tags
        ),
        asset_criticality_overrides=(
            request.asset_criticality_overrides
            if request.asset_criticality_overrides is not None
            else config.policy.asset_criticality_overrides
        ),
    )

    # Validate that false_positive_threshold < auto_contain_threshold
    if new_policy.false_positive_threshold >= new_policy.auto_contain_threshold:
        raise HTTPException(
            status_code=400,
            detail="False positive threshold must be less than auto-contain threshold"
        )

    config.policy = new_policy
    _set_config(config)

    logger.info("Policy configuration updated")

    return PolicyConfigResponse(
        auto_contain_threshold=config.policy.auto_contain_threshold,
        false_positive_threshold=config.policy.false_positive_threshold,
        auto_contain_enabled=config.policy.auto_contain_enabled,
        vip_list=config.policy.vip_list,
        critical_tags=config.policy.critical_tags,
        asset_criticality_overrides=config.policy.asset_criticality_overrides,
        last_updated=config.last_updated,
    )


# ============================================================================
# Notification Configuration Endpoints
# ============================================================================


class NotificationConfigResponse(BaseModel):
    """Response model for notification configuration."""

    slack_enabled: bool
    teams_enabled: bool
    email_enabled: bool
    webhook_enabled: bool
    slack_webhook_url: Optional[str] = None
    teams_webhook_url: Optional[str] = None
    email_recipients: list[str]
    custom_webhook_url: Optional[str] = None
    notify_on_critical: bool
    notify_on_high: bool
    notify_on_medium: bool
    notify_on_containment: bool
    notify_on_approval_needed: bool
    template_style: str
    last_updated: Optional[str] = None


class UpdateNotificationConfigRequest(BaseModel):
    """Request model for updating notification configuration."""

    slack_enabled: Optional[bool] = None
    teams_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    webhook_enabled: Optional[bool] = None
    slack_webhook_url: Optional[str] = None
    teams_webhook_url: Optional[str] = None
    email_recipients: Optional[list[str]] = None
    custom_webhook_url: Optional[str] = None
    notify_on_critical: Optional[bool] = None
    notify_on_high: Optional[bool] = None
    notify_on_medium: Optional[bool] = None
    notify_on_containment: Optional[bool] = None
    notify_on_approval_needed: Optional[bool] = None
    template_style: Optional[str] = None


@router.get("/notifications", response_model=NotificationConfigResponse)
async def get_notification_config():
    """Get current notification configuration.

    Returns notification channel settings and triggers.
    Sensitive values like webhook URLs are partially masked.
    """
    config = _get_config()
    notif = config.notifications

    return NotificationConfigResponse(
        slack_enabled=notif.slack_enabled,
        teams_enabled=notif.teams_enabled,
        email_enabled=notif.email_enabled,
        webhook_enabled=notif.webhook_enabled,
        slack_webhook_url=_mask_url(notif.slack_webhook_url),
        teams_webhook_url=_mask_url(notif.teams_webhook_url),
        email_recipients=notif.email_recipients,
        custom_webhook_url=_mask_url(notif.custom_webhook_url),
        notify_on_critical=notif.notify_on_critical,
        notify_on_high=notif.notify_on_high,
        notify_on_medium=notif.notify_on_medium,
        notify_on_containment=notif.notify_on_containment,
        notify_on_approval_needed=notif.notify_on_approval_needed,
        template_style=notif.template_style,
        last_updated=config.last_updated,
    )


@router.put("/notifications", response_model=NotificationConfigResponse)
async def update_notification_config(request: UpdateNotificationConfigRequest):
    """Update notification configuration.

    Updates notification settings. Only provided fields will be updated.
    """
    config = _get_config()
    notif = config.notifications

    # Update only provided fields
    new_notif = NotificationPreferences(
        slack_enabled=(
            request.slack_enabled
            if request.slack_enabled is not None
            else notif.slack_enabled
        ),
        teams_enabled=(
            request.teams_enabled
            if request.teams_enabled is not None
            else notif.teams_enabled
        ),
        email_enabled=(
            request.email_enabled
            if request.email_enabled is not None
            else notif.email_enabled
        ),
        webhook_enabled=(
            request.webhook_enabled
            if request.webhook_enabled is not None
            else notif.webhook_enabled
        ),
        slack_webhook_url=(
            request.slack_webhook_url
            if request.slack_webhook_url is not None
            else notif.slack_webhook_url
        ),
        teams_webhook_url=(
            request.teams_webhook_url
            if request.teams_webhook_url is not None
            else notif.teams_webhook_url
        ),
        email_recipients=(
            request.email_recipients
            if request.email_recipients is not None
            else notif.email_recipients
        ),
        custom_webhook_url=(
            request.custom_webhook_url
            if request.custom_webhook_url is not None
            else notif.custom_webhook_url
        ),
        notify_on_critical=(
            request.notify_on_critical
            if request.notify_on_critical is not None
            else notif.notify_on_critical
        ),
        notify_on_high=(
            request.notify_on_high
            if request.notify_on_high is not None
            else notif.notify_on_high
        ),
        notify_on_medium=(
            request.notify_on_medium
            if request.notify_on_medium is not None
            else notif.notify_on_medium
        ),
        notify_on_containment=(
            request.notify_on_containment
            if request.notify_on_containment is not None
            else notif.notify_on_containment
        ),
        notify_on_approval_needed=(
            request.notify_on_approval_needed
            if request.notify_on_approval_needed is not None
            else notif.notify_on_approval_needed
        ),
        template_style=(
            request.template_style
            if request.template_style is not None
            else notif.template_style
        ),
    )

    config.notifications = new_notif
    _set_config(config)

    logger.info("Notification configuration updated")

    return NotificationConfigResponse(
        slack_enabled=new_notif.slack_enabled,
        teams_enabled=new_notif.teams_enabled,
        email_enabled=new_notif.email_enabled,
        webhook_enabled=new_notif.webhook_enabled,
        slack_webhook_url=_mask_url(new_notif.slack_webhook_url),
        teams_webhook_url=_mask_url(new_notif.teams_webhook_url),
        email_recipients=new_notif.email_recipients,
        custom_webhook_url=_mask_url(new_notif.custom_webhook_url),
        notify_on_critical=new_notif.notify_on_critical,
        notify_on_high=new_notif.notify_on_high,
        notify_on_medium=new_notif.notify_on_medium,
        notify_on_containment=new_notif.notify_on_containment,
        notify_on_approval_needed=new_notif.notify_on_approval_needed,
        template_style=new_notif.template_style,
        last_updated=config.last_updated,
    )


# ============================================================================
# Integration Configuration Endpoints
# ============================================================================


class IntegrationConfigResponse(BaseModel):
    """Response model for integration configuration."""

    api_keys: dict[str, str]  # Keys are masked
    webhook_urls: dict[str, str]  # URLs are masked
    enabled_integrations: list[str]
    last_updated: Optional[str] = None


class UpdateIntegrationConfigRequest(BaseModel):
    """Request model for updating integration configuration."""

    api_keys: Optional[dict[str, str]] = None
    webhook_urls: Optional[dict[str, str]] = None
    enabled_integrations: Optional[list[str]] = None


@router.get("/integrations", response_model=IntegrationConfigResponse)
async def get_integration_config():
    """Get current integration configuration.

    Returns integration settings with masked sensitive values.
    """
    config = _get_config()
    integ = config.integrations

    return IntegrationConfigResponse(
        api_keys={k: _mask_key(v) for k, v in integ.api_keys.items()},
        webhook_urls={k: _mask_url(v) for k, v in integ.webhook_urls.items()},
        enabled_integrations=integ.enabled_integrations,
        last_updated=config.last_updated,
    )


@router.put("/integrations", response_model=IntegrationConfigResponse)
async def update_integration_config(request: UpdateIntegrationConfigRequest):
    """Update integration configuration.

    Updates integration settings. Only provided fields will be updated.
    """
    config = _get_config()
    integ = config.integrations

    # Merge API keys (only update provided keys, keep existing ones)
    new_api_keys = dict(integ.api_keys)
    if request.api_keys:
        for key, value in request.api_keys.items():
            if value:  # Only update if value is provided
                new_api_keys[key] = value

    # Merge webhook URLs
    new_webhook_urls = dict(integ.webhook_urls)
    if request.webhook_urls:
        for key, value in request.webhook_urls.items():
            if value:
                new_webhook_urls[key] = value

    new_integ = IntegrationConfig(
        api_keys=new_api_keys,
        webhook_urls=new_webhook_urls,
        enabled_integrations=(
            request.enabled_integrations
            if request.enabled_integrations is not None
            else integ.enabled_integrations
        ),
    )

    config.integrations = new_integ
    _set_config(config)

    logger.info("Integration configuration updated")

    return IntegrationConfigResponse(
        api_keys={k: _mask_key(v) for k, v in new_integ.api_keys.items()},
        webhook_urls={k: _mask_url(v) for k, v in new_integ.webhook_urls.items()},
        enabled_integrations=new_integ.enabled_integrations,
        last_updated=config.last_updated,
    )


# ============================================================================
# Complete Configuration Endpoint
# ============================================================================


class FullConfigResponse(BaseModel):
    """Response model for complete system configuration."""

    policy: PolicyConfigResponse
    notifications: NotificationConfigResponse
    integrations: IntegrationConfigResponse
    last_updated: Optional[str] = None


@router.get("/all", response_model=FullConfigResponse)
async def get_full_config():
    """Get complete system configuration.

    Returns all configuration sections (policy, notifications, integrations).
    Sensitive values are masked.
    """
    config = _get_config()

    return FullConfigResponse(
        policy=PolicyConfigResponse(
            auto_contain_threshold=config.policy.auto_contain_threshold,
            false_positive_threshold=config.policy.false_positive_threshold,
            auto_contain_enabled=config.policy.auto_contain_enabled,
            vip_list=config.policy.vip_list,
            critical_tags=config.policy.critical_tags,
            asset_criticality_overrides=config.policy.asset_criticality_overrides,
            last_updated=config.last_updated,
        ),
        notifications=NotificationConfigResponse(
            slack_enabled=config.notifications.slack_enabled,
            teams_enabled=config.notifications.teams_enabled,
            email_enabled=config.notifications.email_enabled,
            webhook_enabled=config.notifications.webhook_enabled,
            slack_webhook_url=_mask_url(config.notifications.slack_webhook_url),
            teams_webhook_url=_mask_url(config.notifications.teams_webhook_url),
            email_recipients=config.notifications.email_recipients,
            custom_webhook_url=_mask_url(config.notifications.custom_webhook_url),
            notify_on_critical=config.notifications.notify_on_critical,
            notify_on_high=config.notifications.notify_on_high,
            notify_on_medium=config.notifications.notify_on_medium,
            notify_on_containment=config.notifications.notify_on_containment,
            notify_on_approval_needed=config.notifications.notify_on_approval_needed,
            template_style=config.notifications.template_style,
            last_updated=config.last_updated,
        ),
        integrations=IntegrationConfigResponse(
            api_keys={k: _mask_key(v) for k, v in config.integrations.api_keys.items()},
            webhook_urls={k: _mask_url(v) for k, v in config.integrations.webhook_urls.items()},
            enabled_integrations=config.integrations.enabled_integrations,
            last_updated=config.last_updated,
        ),
        last_updated=config.last_updated,
    )


@router.post("/reset")
async def reset_config():
    """Reset all configuration to defaults.

    WARNING: This will reset all settings to their default values.
    """
    global _system_config
    _system_config = SystemConfig()
    _system_config.last_updated = datetime.utcnow().isoformat()

    logger.info("Configuration reset to defaults")

    return {"message": "Configuration reset to defaults", "timestamp": _system_config.last_updated}


# ============================================================================
# Helper Functions
# ============================================================================


def _mask_url(url: Optional[str]) -> Optional[str]:
    """Mask a URL for security, showing only the beginning and end."""
    if not url:
        return None
    if len(url) <= 20:
        return "****"
    return f"{url[:15]}...{url[-5:]}"


def _mask_key(key: str) -> str:
    """Mask an API key, showing only the last 4 characters."""
    if not key:
        return ""
    if len(key) <= 8:
        return "****"
    return f"****{key[-4:]}"
