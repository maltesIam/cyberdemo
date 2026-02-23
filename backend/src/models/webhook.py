"""
Webhook configuration Pydantic models.

Task: T-1.1.004
Requirement: TECH-001 - Agent Orchestration MCP Server
REQ-001-001-001 to REQ-001-001-005 - Webhook system requirements

These models define the structure for webhook configurations that allow
the CyberDemo product to invoke the AI agent (SoulInTheBot) for analysis.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


# Valid webhook event types based on functional spec
VALID_WEBHOOK_EVENTS = [
    # Alert events
    "alert.created",
    "alert.updated",
    "alert.critical",
    "alert.escalated",
    "alert.resolved",
    # Analysis events
    "analysis.requested",
    "analysis.completed",
    "analysis.failed",
    # Incident events
    "incident.created",
    "incident.updated",
    "incident.escalated",
    # Detection events
    "detection.created",
    "detection.high_severity",
    # System events
    "system.health_warning",
]


class WebhookConfig(BaseModel):
    """
    Configuration for a webhook endpoint that receives events from CyberDemo.

    This model represents the settings for invoking the AI agent via webhook
    when specific events occur in the SOC platform.

    Attributes:
        id: Unique identifier for the webhook configuration
        name: Human-readable name for the webhook
        url: HTTP(S) endpoint URL to send events to
        events: List of event types that trigger this webhook
        enabled: Whether the webhook is active
        secret: Optional HMAC secret for request signing (TECH-009)
        timeout_seconds: Request timeout (REQ-001-001-004), default 30s, max 120s
        retry_count: Number of retry attempts (REQ-001-001-003), default 3
        headers: Optional custom headers to include in requests
        created_at: Timestamp when config was created
        updated_at: Timestamp when config was last modified
    """

    id: str = Field(default_factory=lambda: f"wh-{uuid4().hex[:12]}")
    name: str = Field(..., min_length=1, max_length=100)
    url: HttpUrl
    events: list[str] = Field(..., min_length=1)
    enabled: bool = Field(default=True)
    secret: Optional[str] = Field(default=None, min_length=8, max_length=256)
    timeout_seconds: int = Field(default=30, ge=1, le=120)
    retry_count: int = Field(default=3, ge=0, le=10)
    headers: Optional[dict[str, str]] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("events")
    @classmethod
    def validate_events(cls, v: list[str]) -> list[str]:
        """Validate that all events are known event types."""
        for event in v:
            if event not in VALID_WEBHOOK_EVENTS:
                raise ValueError(f"Unknown event type: {event}. Valid types: {VALID_WEBHOOK_EVENTS}")
        return v

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """Override to convert HttpUrl to string for serialization."""
        data = super().model_dump(**kwargs)
        data["url"] = str(self.url)
        return data

    class Config:
        json_schema_extra = {
            "example": {
                "id": "wh-abc123def456",
                "name": "Agent Analysis Webhook",
                "url": "https://agent.example.com/webhook/analysis",
                "events": ["alert.critical", "alert.escalated"],
                "enabled": True,
                "timeout_seconds": 30,
                "retry_count": 3
            }
        }


class WebhookConfigCreate(BaseModel):
    """
    Request model for creating a new webhook configuration.

    This is the API input model for POST /api/v1/webhooks/configure.
    """

    name: str = Field(..., min_length=1, max_length=100)
    url: HttpUrl
    events: list[str] = Field(..., min_length=1)
    enabled: bool = Field(default=True)
    secret: Optional[str] = Field(default=None, min_length=8, max_length=256)
    timeout_seconds: int = Field(default=30, ge=1, le=120)
    retry_count: int = Field(default=3, ge=0, le=10)
    headers: Optional[dict[str, str]] = Field(default=None)

    @field_validator("events")
    @classmethod
    def validate_events(cls, v: list[str]) -> list[str]:
        """Validate that all events are known event types."""
        for event in v:
            if event not in VALID_WEBHOOK_EVENTS:
                raise ValueError(f"Unknown event type: {event}")
        return v


class WebhookConfigUpdate(BaseModel):
    """
    Request model for updating an existing webhook configuration.

    All fields are optional to allow partial updates.
    """

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    url: Optional[HttpUrl] = None
    events: Optional[list[str]] = Field(default=None, min_length=1)
    enabled: Optional[bool] = None
    secret: Optional[str] = Field(default=None, min_length=8, max_length=256)
    timeout_seconds: Optional[int] = Field(default=None, ge=1, le=120)
    retry_count: Optional[int] = Field(default=None, ge=0, le=10)
    headers: Optional[dict[str, str]] = None

    @field_validator("events")
    @classmethod
    def validate_events(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate that all events are known event types."""
        if v is not None:
            for event in v:
                if event not in VALID_WEBHOOK_EVENTS:
                    raise ValueError(f"Unknown event type: {event}")
        return v


class WebhookDeliveryStatus(str, Enum):
    """Status of a webhook delivery attempt."""

    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class WebhookDelivery(BaseModel):
    """
    Record of a webhook delivery attempt.

    This model tracks each attempt to deliver an event to a webhook endpoint,
    including retry attempts and their outcomes.

    Attributes:
        id: Unique identifier for this delivery
        webhook_id: Reference to the WebhookConfig
        event_type: The event type that was delivered
        event_id: Unique ID of the event instance
        payload: The data that was sent
        status: Current delivery status
        response_code: HTTP response code from endpoint
        response_body: Response body from endpoint
        attempt_count: Number of delivery attempts made
        next_retry_at: When the next retry will occur (if retrying)
        created_at: When the delivery was initiated
        delivered_at: When the delivery succeeded (if successful)
    """

    id: str = Field(default_factory=lambda: f"del-{uuid4().hex[:12]}")
    webhook_id: str
    event_type: str
    event_id: str
    payload: dict[str, Any]
    status: WebhookDeliveryStatus = WebhookDeliveryStatus.PENDING
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    attempt_count: int = Field(default=0, ge=0)
    next_retry_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
