"""
AnalysisJob SQLAlchemy model for the analysis_jobs table.

This model implements TECH-004: Database schema for analysis_jobs table
as specified in the Functional Specification.

The analysis_jobs table tracks asynchronous analysis requests made to the
AI agent, supporting job queuing, status tracking, and result storage.

Task: T-1.1.001
Agent: build-1
"""
from sqlalchemy import String, Integer, DateTime, Enum, JSON, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timedelta, timezone
import enum
from uuid import uuid4

from ..core.database import Base


def utcnow() -> datetime:
    """Return current UTC time as a naive datetime for DB compatibility."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class AnalysisJobStatus(str, enum.Enum):
    """Status of an analysis job.

    Follows job lifecycle: pending -> processing -> completed/failed
    """
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisJobType(str, enum.Enum):
    """Type of analysis job.

    Maps to the different MCP tools for agent orchestration:
    - ALERT_ANALYSIS: agent_analyze_alert tool (REQ-001-003-001)
    - IOC_INVESTIGATION: agent_investigate_ioc tool (REQ-001-003-002)
    - EVENT_CORRELATION: agent_correlate_events tool (REQ-001-003-006)
    - REPORT_GENERATION: agent_generate_report tool (REQ-001-003-004)
    - ACTION_RECOMMENDATION: agent_recommend_action tool (REQ-001-003-003)
    """
    ALERT_ANALYSIS = "alert_analysis"
    IOC_INVESTIGATION = "ioc_investigation"
    EVENT_CORRELATION = "event_correlation"
    REPORT_GENERATION = "report_generation"
    ACTION_RECOMMENDATION = "action_recommendation"


class AnalysisJobDB(Base):
    """
    SQLAlchemy model for tracking asynchronous analysis jobs.

    This table stores all analysis requests made to the AI agent,
    enabling job queuing, status tracking, and result storage.

    Implements:
    - TECH-004: Database schema for analysis_jobs table
    - REQ-001-002-005: Job persistence in PostgreSQL
    - REQ-001-002-006: Support for cleanup of jobs > 24h
    - BR-002: 30 second timeout default
    """

    __tablename__ = "analysis_jobs"

    # Primary key - UUID string
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    # Job classification
    job_type: Mapped[AnalysisJobType] = mapped_column(
        Enum(AnalysisJobType),
        nullable=False
    )

    # Job status with default PENDING
    status: Mapped[AnalysisJobStatus] = mapped_column(
        Enum(AnalysisJobStatus),
        default=AnalysisJobStatus.PENDING,
        index=True  # Indexed for filtering pending jobs
    )

    # Input payload (JSON) - contains the analysis request data
    payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict
    )

    # Result data (JSON) - contains the analysis result when completed
    result: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        default=None
    )

    # Error message if job failed
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None
    )

    # Job priority (1-10, higher = more urgent, default 5)
    priority: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False
    )

    # Retry tracking
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    max_retries: Mapped[int] = mapped_column(
        Integer,
        default=3,  # REQ-001-001-003: Retry logic with 3 attempts
        nullable=False
    )

    # Timeout in seconds (BR-002: default 30s)
    timeout_seconds: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False
    )

    # Session tracking for job grouping
    session_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True  # Indexed for quick session-based lookups
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

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        default=None
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        default=None
    )

    # Composite index for efficient job queue queries
    __table_args__ = (
        Index('ix_analysis_jobs_status_priority', 'status', 'priority'),
    )

    def can_retry(self) -> bool:
        """Check if the job can be retried.

        Returns:
            True if retry_count < max_retries, False otherwise.
        """
        return self.retry_count < self.max_retries

    def is_expired(self, max_age_hours: int = 24) -> bool:
        """Check if the job is expired (older than max_age_hours).

        Used for cleanup of old jobs per REQ-001-002-006.

        Args:
            max_age_hours: Maximum age in hours before job is considered expired.
                          Default is 24 hours.

        Returns:
            True if job is older than max_age_hours, False otherwise.
        """
        if self.created_at is None:
            return False
        age = utcnow() - self.created_at
        return age > timedelta(hours=max_age_hours)

    def to_dict(self) -> dict:
        """Convert the model to a dictionary.

        Returns:
            Dictionary representation of the job.
        """
        return {
            "id": self.id,
            "job_type": self.job_type.value if self.job_type else None,
            "status": self.status.value if self.status else None,
            "payload": self.payload,
            "result": self.result,
            "error": self.error_message,
            "progress": self._calculate_progress(),
            "priority": self.priority,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def _calculate_progress(self) -> int:
        """Calculate progress based on status.

        Returns:
            Progress percentage (0-100).
        """
        if self.status == AnalysisJobStatus.COMPLETED:
            return 100
        elif self.status == AnalysisJobStatus.PROCESSING:
            return 50
        elif self.status == AnalysisJobStatus.FAILED:
            return 0
        elif self.status == AnalysisJobStatus.CANCELLED:
            return 0
        else:
            return 0

    def __repr__(self) -> str:
        return f"<AnalysisJobDB(id={self.id}, type={self.job_type}, status={self.status})>"
