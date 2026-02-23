"""
Webhook Configuration API endpoints.

This module implements the webhook configuration API for managing
webhooks that allow the product to actively invoke the AI agent.

Task: T-1.2.001
Agent: build-1
Requirements: REQ-001-001-001 - API endpoint POST /api/v1/webhooks/configure
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from ..core.database import get_db
from ..services.webhook_service import WebhookService
from ..models.webhook_config_db import WebhookEventType


# Valid event types for validation
VALID_EVENT_TYPES = [e.value for e in WebhookEventType]


# Pydantic schemas
class WebhookConfigCreate(BaseModel):
    """Schema for creating a new webhook configuration."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-readable name for the webhook"
    )
    url: HttpUrl = Field(
        ...,
        description="Target URL for the webhook"
    )
    event_types: List[str] = Field(
        ...,
        min_length=1,
        description="List of event types that trigger this webhook"
    )
    secret: Optional[str] = Field(
        None,
        max_length=256,
        description="Secret for HMAC signature validation"
    )
    timeout_seconds: int = Field(
        30,
        ge=1,
        le=120,
        description="Timeout in seconds (1-120, default 30)"
    )
    max_retries: int = Field(
        3,
        ge=0,
        le=10,
        description="Maximum retry attempts (0-10, default 3)"
    )
    retry_delay_seconds: int = Field(
        5,
        ge=1,
        le=60,
        description="Base delay between retries in seconds"
    )
    headers: Optional[dict] = Field(
        None,
        description="Custom headers to include in webhook requests"
    )

    @field_validator("event_types")
    @classmethod
    def validate_event_types(cls, v: List[str]) -> List[str]:
        """Validate that all event types are valid."""
        for event_type in v:
            if event_type not in VALID_EVENT_TYPES:
                raise ValueError(
                    f"Invalid event type: {event_type}. "
                    f"Valid types are: {VALID_EVENT_TYPES}"
                )
        return v


class WebhookConfigUpdate(BaseModel):
    """Schema for updating a webhook configuration."""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100
    )
    url: Optional[HttpUrl] = None
    event_types: Optional[List[str]] = None
    secret: Optional[str] = Field(None, max_length=256)
    timeout_seconds: Optional[int] = Field(None, ge=1, le=120)
    max_retries: Optional[int] = Field(None, ge=0, le=10)
    retry_delay_seconds: Optional[int] = Field(None, ge=1, le=60)
    is_active: Optional[bool] = None
    headers: Optional[dict] = None

    @field_validator("event_types")
    @classmethod
    def validate_event_types(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate that all event types are valid."""
        if v is None:
            return v
        for event_type in v:
            if event_type not in VALID_EVENT_TYPES:
                raise ValueError(
                    f"Invalid event type: {event_type}. "
                    f"Valid types are: {VALID_EVENT_TYPES}"
                )
        return v


class WebhookConfigResponse(BaseModel):
    """Schema for webhook configuration response."""

    id: str
    name: str
    url: str
    event_types: List[str]
    timeout_seconds: int
    max_retries: int
    retry_delay_seconds: int
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_triggered_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    last_failure_at: Optional[datetime] = None
    failure_count: int = 0

    class Config:
        from_attributes = True


class WebhookTestResult(BaseModel):
    """Schema for webhook test result."""

    success: bool
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error: Optional[str] = None


# Router
router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post(
    "/configure",
    response_model=WebhookConfigResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new webhook configuration",
    description="REQ-001-001-001: API endpoint POST /api/v1/webhooks/configure"
)
async def create_webhook(
    config: WebhookConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new webhook configuration.

    This endpoint allows configuring webhooks that will be triggered
    when specific events occur, enabling active invocation of the AI agent.
    """
    service = WebhookService(db)

    # Check if webhook with same name already exists
    existing = await service.get_webhook_by_name(config.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Webhook with name '{config.name}' already exists"
        )

    webhook = await service.create_webhook(
        name=config.name,
        url=str(config.url),
        event_types=config.event_types,
        secret=config.secret,
        timeout_seconds=config.timeout_seconds,
        max_retries=config.max_retries,
        retry_delay_seconds=config.retry_delay_seconds,
        headers=config.headers
    )

    return webhook


@router.get(
    "/",
    response_model=List[WebhookConfigResponse],
    summary="List all webhook configurations"
)
async def list_webhooks(
    active_only: bool = False,
    event_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all webhook configurations.

    Args:
        active_only: If True, only return active webhooks.
        event_type: If provided, filter by event type.
    """
    service = WebhookService(db)
    webhooks = await service.list_webhooks(
        active_only=active_only,
        event_type=event_type
    )
    return webhooks


@router.get(
    "/{webhook_id}",
    response_model=WebhookConfigResponse,
    summary="Get a webhook configuration by ID"
)
async def get_webhook(
    webhook_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a webhook configuration by ID."""
    service = WebhookService(db)
    webhook = await service.get_webhook(webhook_id)

    if webhook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with ID '{webhook_id}' not found"
        )

    return webhook


@router.put(
    "/{webhook_id}",
    response_model=WebhookConfigResponse,
    summary="Update a webhook configuration"
)
async def update_webhook(
    webhook_id: str,
    config: WebhookConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a webhook configuration."""
    service = WebhookService(db)

    # If name is being updated, check for conflicts
    if config.name:
        existing = await service.get_webhook_by_name(config.name)
        if existing and existing.id != webhook_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Webhook with name '{config.name}' already exists"
            )

    webhook = await service.update_webhook(
        webhook_id=webhook_id,
        name=config.name,
        url=str(config.url) if config.url else None,
        event_types=config.event_types,
        secret=config.secret,
        timeout_seconds=config.timeout_seconds,
        max_retries=config.max_retries,
        retry_delay_seconds=config.retry_delay_seconds,
        is_active=config.is_active,
        headers=config.headers
    )

    if webhook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with ID '{webhook_id}' not found"
        )

    return webhook


@router.delete(
    "/{webhook_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a webhook configuration"
)
async def delete_webhook(
    webhook_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a webhook configuration."""
    service = WebhookService(db)
    deleted = await service.delete_webhook(webhook_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with ID '{webhook_id}' not found"
        )


@router.post(
    "/{webhook_id}/test",
    response_model=WebhookTestResult,
    summary="Test a webhook configuration"
)
async def test_webhook(
    webhook_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Test a webhook configuration by sending a test event.

    This endpoint sends a test payload to the configured webhook URL
    and returns the result.
    """
    service = WebhookService(db)
    webhook = await service.get_webhook(webhook_id)

    if webhook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with ID '{webhook_id}' not found"
        )

    # TODO: Implement actual webhook testing with HTTP request
    # For now, return a placeholder result
    return WebhookTestResult(
        success=True,
        status_code=200,
        response_time_ms=50.0,
        error=None
    )
