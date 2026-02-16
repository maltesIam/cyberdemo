"""
Collaboration models for SOC team communication.

Provides structured models for real-time chat, mentions, attachments,
and reactions within the incident response workflow.
"""

from sqlalchemy import String, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import enum
from uuid import uuid4

from ..core.database import Base


class MessageType(str, enum.Enum):
    """Types of collaboration messages."""
    TEXT = "text"
    SYSTEM = "system"
    EVIDENCE = "evidence"
    ACTION = "action"


class AttachmentType(str, enum.Enum):
    """Types of message attachments."""
    FILE = "file"
    IMAGE = "image"
    LOG = "log"
    SCREENSHOT = "screenshot"
    PCAP = "pcap"


class CollabChannel(Base):
    """Collaboration channel for incident discussions."""

    __tablename__ = "collab_channels"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    incident_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    channel_type: Mapped[str] = mapped_column(String(20), default="incident")  # incident, general, team
    created_by: Mapped[str] = mapped_column(String(100), default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_archived: Mapped[bool] = mapped_column(default=False)


class CollabMessage(Base):
    """Individual message in a collaboration channel."""

    __tablename__ = "collab_messages"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    channel_id: Mapped[str] = mapped_column(String(36), ForeignKey("collab_channels.id"), index=True)
    incident_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    user: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(String(5000))
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType), default=MessageType.TEXT
    )
    mentions: Mapped[list | None] = mapped_column(JSON, nullable=True)  # List of @mentions
    attachments: Mapped[list | None] = mapped_column(JSON, nullable=True)  # List of attachment objects
    reactions: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {emoji: [users]}
    thread_id: Mapped[str | None] = mapped_column(String(36), nullable=True)  # For threaded replies
    is_edited: Mapped[bool] = mapped_column(default=False)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Reaction(Base):
    """Reaction to a message (emoji reactions)."""

    __tablename__ = "collab_reactions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    message_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("collab_messages.id"), index=True
    )
    user: Mapped[str] = mapped_column(String(100))
    emoji: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Attachment(Base):
    """Attachment metadata for messages."""

    __tablename__ = "collab_attachments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    message_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("collab_messages.id"), index=True
    )
    filename: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[AttachmentType] = mapped_column(
        Enum(AttachmentType), default=AttachmentType.FILE
    )
    file_size: Mapped[int] = mapped_column(default=0)
    storage_path: Mapped[str] = mapped_column(String(500))
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    uploaded_by: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
