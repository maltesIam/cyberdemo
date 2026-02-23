"""
PlaybookExecutionDB SQLAlchemy model for the playbook_executions table.

This model implements TECH-006: Database schema for playbook_executions table
as specified in the Functional Specification.

The playbook_executions table tracks the state of playbook executions,
supporting pause/resume (REQ-005-001-002, REQ-005-001-003) and
rollback (REQ-005-001-004) operations with full state persistence.

Task: T-2.3.001
Agent: build-3
"""
from sqlalchemy import String, Integer, DateTime, Enum, JSON, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
import enum
from uuid import uuid4

from ..core.database import Base


def utcnow() -> datetime:
    """Return current UTC time as a naive datetime for DB compatibility."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class PlaybookExecutionStatus(str, enum.Enum):
    """Status of a playbook execution.

    Follows execution lifecycle with support for:
    - PAUSED: REQ-005-001-002 - Pause endpoint
    - RESUMED via RUNNING: REQ-005-001-003 - Resume endpoint
    - ROLLED_BACK: REQ-005-001-004 - Rollback endpoint
    """
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class PlaybookExecutionDB(Base):
    """
    SQLAlchemy model for tracking playbook execution state.

    This table stores all playbook execution state, enabling:
    - REQ-005-001-001: Execute playbook endpoint
    - REQ-005-001-002: Pause execution
    - REQ-005-001-003: Resume execution
    - REQ-005-001-004: Rollback execution
    - REQ-005-001-005: Get execution status
    - REQ-005-001-006: State persistence in PostgreSQL

    Implements:
    - TECH-006: Database schema for playbook_executions table
    - BR-017: Playbooks define sequence of actions and decision points
    - BR-018: Destructive actions require human approval
    - BR-019: Playbook state persists between sessions
    - BR-020: Each action is registered in audit log
    """

    __tablename__ = "playbook_executions"

    # Primary key - UUID string
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    # Reference to the playbook definition
    playbook_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True  # Indexed for filtering by playbook
    )

    # Playbook name for quick reference
    playbook_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    # Execution status with default PENDING
    status: Mapped[PlaybookExecutionStatus] = mapped_column(
        Enum(PlaybookExecutionStatus),
        default=PlaybookExecutionStatus.PENDING,
        index=True  # Indexed for filtering by status
    )

    # Current step index (0-based) - used for pause/resume
    current_step: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    # Total number of steps in the playbook
    total_steps: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    # Input context (JSON) - contains the execution input data
    context: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict
    )

    # Results of each executed step (JSON array)
    step_results: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
        default=None
    )

    # Rollback data for each executed step (JSON array)
    # Stores undo actions for REQ-005-001-004
    rollback_data: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
        default=None
    )

    # Error message if execution failed
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None
    )

    # What triggered this execution
    triggered_by: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        default=None
    )

    # Session tracking for execution grouping
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

    paused_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        default=None
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        default=None
    )

    def can_pause(self) -> bool:
        """Check if the execution can be paused.

        Returns:
            True if status is RUNNING, False otherwise.
        """
        return self.status == PlaybookExecutionStatus.RUNNING

    def can_resume(self) -> bool:
        """Check if the execution can be resumed.

        Returns:
            True if status is PAUSED, False otherwise.
        """
        return self.status == PlaybookExecutionStatus.PAUSED

    def can_rollback(self) -> bool:
        """Check if the execution can be rolled back.

        Rollback is possible when:
        - Status is COMPLETED or FAILED (not already rolled back)
        - There is rollback data available

        Returns:
            True if rollback is possible, False otherwise.
        """
        if self.status == PlaybookExecutionStatus.ROLLED_BACK:
            return False
        if self.status not in (
            PlaybookExecutionStatus.COMPLETED,
            PlaybookExecutionStatus.FAILED
        ):
            return False
        return bool(self.rollback_data)

    def get_progress_percentage(self) -> int:
        """Calculate progress percentage based on current step.

        Returns:
            Progress percentage (0-100).
        """
        if self.total_steps <= 0:
            return 0
        return int((self.current_step / self.total_steps) * 100)

    def to_dict(self) -> dict:
        """Convert the model to a dictionary.

        Returns:
            Dictionary representation of the execution.
        """
        return {
            "id": self.id,
            "playbook_id": self.playbook_id,
            "playbook_name": self.playbook_name,
            "status": self.status.value if self.status else None,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "progress": self.get_progress_percentage(),
            "context": self.context,
            "step_results": self.step_results,
            "rollback_data": self.rollback_data,
            "error": self.error_message,
            "triggered_by": self.triggered_by,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "paused_at": self.paused_at.isoformat() if self.paused_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<PlaybookExecutionDB(id={self.id}, "
            f"playbook={self.playbook_name}, status={self.status})>"
        )
