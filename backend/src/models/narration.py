"""
Narration Message database model.

TECH-007: Tabla narration_messages para historial
REQ-003-002-002: Formato de mensaje {type, content, confidence, timestamp}

Stores narration messages from agent reasoning during investigations.
"""
from sqlalchemy import String, Float, DateTime, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import enum
from uuid import uuid4

from ..core.database import Base


class NarrationType(str, enum.Enum):
    """Type of narration message.

    REQ-003-001-002: Messages with type (thinking/finding/decision/action)
    """
    THINKING = "thinking"   # Agent's thought process
    FINDING = "finding"     # Discovery of relevant information
    DECISION = "decision"   # Conclusion or decision made
    ACTION = "action"       # Action being taken


class ConfidenceLevel(str, enum.Enum):
    """Confidence level for narration messages.

    REQ-003-001-003: Confidence indicator (high/medium/low)

    Ranges:
    - LOW: 0.0-0.33
    - MEDIUM: 0.34-0.66
    - HIGH: 0.67-1.0
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def confidence_from_score(score: float) -> ConfidenceLevel:
    """Convert a confidence score (0.0-1.0) to a ConfidenceLevel.

    Args:
        score: Confidence score between 0.0 and 1.0

    Returns:
        ConfidenceLevel based on the score

    Raises:
        ValueError: If score is not between 0.0 and 1.0
    """
    if score < 0.0 or score > 1.0:
        raise ValueError(f"Confidence score must be between 0.0 and 1.0, got {score}")

    if score <= 0.33:
        return ConfidenceLevel.LOW
    elif score <= 0.66:
        return ConfidenceLevel.MEDIUM
    else:
        return ConfidenceLevel.HIGH


class NarrationMessage(Base):
    """Narration message from agent reasoning.

    TECH-007: Database table for narration message history.
    """

    __tablename__ = "narration_messages"

    # Primary key - UUID
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    # Session identifier for grouping messages
    session_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False
    )

    # Type of narration message
    message_type: Mapped[NarrationType] = mapped_column(
        Enum(NarrationType),
        nullable=False
    )

    # Content of the narration
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Confidence level (categorical)
    confidence: Mapped[ConfidenceLevel] = mapped_column(
        Enum(ConfidenceLevel),
        default=ConfidenceLevel.MEDIUM
    )

    # Confidence score (numerical, 0.0-1.0)
    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.5
    )

    # Timestamp when the narration was generated
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # Record creation timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
