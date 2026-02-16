from sqlalchemy import String, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import enum
from uuid import uuid4

from ..core.database import Base


class ActionType(str, enum.Enum):
    CONTAIN_HOST = "contain_host"
    RELEASE_HOST = "release_host"
    UPDATE_ALERT = "update_alert"
    HUNT_HASH = "hunt_hash"
    REQUEST_APPROVAL = "request_approval"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"
    ESCALATE = "escalate"
    NOTIFY = "notify"


class ActionLog(Base):
    """Log of all actions taken by the SOC agent."""

    __tablename__ = "action_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    alert_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("alerts.id"), nullable=True)
    host_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    action_type: Mapped[ActionType] = mapped_column(Enum(ActionType))
    actor: Mapped[str] = mapped_column(String(100))  # "agent" or username
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reasoning: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
