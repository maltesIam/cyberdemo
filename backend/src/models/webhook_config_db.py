"""
WebhookConfigDB SQLAlchemy model for the webhook_configs table.

This model implements TECH-005: Database schema for webhook_configs table
as specified in the Functional Specification.

The webhook_configs table stores webhook configurations for active invocation
of the AI agent when specific events occur.

Task: T-1.1.002
Agent: build-1
"""
from sqlalchemy import String, Integer, DateTime, Boolean, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
import enum
from uuid import uuid4

from ..core.database import Base


def utcnow() -> datetime:
    """Return current UTC time as a naive datetime for DB compatibility."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class WebhookEventType(str, enum.Enum):
    """Types of events that can trigger a webhook.

    Based on BR-001: Critical alerts (severity >= critical) trigger automatic
    agent analysis. Additional event types support various automation scenarios.
    """
    # Alert-based events
    CRITICAL_ALERT = "critical_alert"
    HIGH_SEVERITY_ALERT = "high_severity_alert"

    # Incident events
    INCIDENT_CREATED = "incident_created"

    # Analysis events
    ANALYSIS_REQUEST = "analysis_request"

    # Correlation events
    CORRELATION_FOUND = "correlation_found"


class WebhookConfigDB(Base):
    """
    SQLAlchemy model for webhook configuration.

    This table stores the configuration for webhooks that allow the product
    to actively invoke the AI agent when specific events occur.

    Implements:
    - TECH-005: Database schema for webhook_configs table
    - REQ-001-001-001: API endpoint POST /api/v1/webhooks/configure
    - REQ-001-001-002: Dispatcher that sends events to configured endpoint
    - REQ-001-001-003: Retry logic with backoff exponential (3 attempts)
    - REQ-001-001-004: Timeout configurable per webhook (default 30s)
    - REQ-001-001-005: Response validation
    """

    __tablename__ = "webhook_configs"

    # Primary key - UUID string
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    # Human-readable name for the webhook (unique)
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    # Target URL for the webhook
    url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False
    )

    # Event types that trigger this webhook (JSON array of strings)
    event_types: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list
    )

    # Secret for HMAC signature validation (TECH-009)
    secret: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
        default=None
    )

    # Timeout in seconds (REQ-001-001-004, BR-002: default 30s)
    timeout_seconds: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False
    )

    # Maximum retry attempts (REQ-001-001-003: 3 attempts)
    max_retries: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False
    )

    # Base delay between retries in seconds
    retry_delay_seconds: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False
    )

    # Whether the webhook is active
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True  # Indexed for filtering active webhooks
    )

    # Custom headers to include in webhook requests (JSON)
    headers: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        default=None
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utcnow,
        onupdate=utcnow,
        nullable=False
    )

    # Tracking timestamps
    last_triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        default=None
    )

    last_success_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        default=None
    )

    last_failure_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        default=None
    )

    # Failure tracking
    failure_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    def should_retry(self) -> bool:
        """Check if the webhook should be retried after a failure.

        Returns:
            True if failure_count < max_retries, False otherwise.
        """
        return self.failure_count < self.max_retries

    def get_retry_delay(self) -> int:
        """Calculate the retry delay with exponential backoff.

        Uses exponential backoff: base_delay * 2^(failure_count - 1)
        Capped at 60 seconds.

        Returns:
            Delay in seconds before next retry.
        """
        if self.failure_count <= 0:
            return self.retry_delay_seconds

        delay = self.retry_delay_seconds * (2 ** (self.failure_count - 1))
        return min(delay, 60)  # Cap at 60 seconds

    def increment_failure_count(self) -> None:
        """Increment the failure count and update last_failure_at."""
        self.failure_count += 1
        self.last_failure_at = utcnow()

    def reset_failure_count(self) -> None:
        """Reset the failure count and update last_success_at."""
        self.failure_count = 0
        self.last_success_at = utcnow()

    def __repr__(self) -> str:
        return f"<WebhookConfigDB(id={self.id}, name={self.name}, active={self.is_active})>"
