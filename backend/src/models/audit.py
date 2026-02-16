"""Audit log models for compliance tracking."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class AuditActionType(str, Enum):
    """Types of actions that can be audited."""
    CONTAINMENT = "containment"
    APPROVAL = "approval"
    INVESTIGATION = "investigation"
    CONFIG_CHANGE = "config_change"
    ALERT_UPDATE = "alert_update"
    ESCALATION = "escalation"
    NOTIFICATION = "notification"
    PLAYBOOK_EXECUTION = "playbook_execution"
    USER_LOGIN = "user_login"
    DATA_EXPORT = "data_export"


class AuditOutcome(str, Enum):
    """Possible outcomes of audited actions."""
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    DENIED = "denied"
    APPROVED = "approved"


class AuditLog(BaseModel):
    """Audit log entry model."""
    id: str = Field(..., description="Unique audit log ID")
    timestamp: datetime = Field(..., description="When the action occurred")
    user: str = Field(..., description="User who performed the action")
    action_type: AuditActionType = Field(..., description="Type of action")
    target: str = Field(..., description="Target of the action (e.g., asset ID, incident ID)")
    target_type: str = Field(default="", description="Type of target (asset, incident, etc.)")
    details: dict = Field(default_factory=dict, description="Additional action details")
    policy_decision: Optional[str] = Field(None, description="Policy engine decision if applicable")
    outcome: AuditOutcome = Field(..., description="Outcome of the action")
    ip_address: Optional[str] = Field(None, description="IP address of the user")
    session_id: Optional[str] = Field(None, description="Session ID if applicable")


class AuditLogFilter(BaseModel):
    """Filter parameters for querying audit logs."""
    date_from: Optional[datetime] = Field(None, description="Filter logs from this date")
    date_to: Optional[datetime] = Field(None, description="Filter logs until this date")
    user: Optional[str] = Field(None, description="Filter by user")
    action_type: Optional[AuditActionType] = Field(None, description="Filter by action type")
    target: Optional[str] = Field(None, description="Filter by target (partial match)")
    outcome: Optional[AuditOutcome] = Field(None, description="Filter by outcome")


class AuditExportFormat(str, Enum):
    """Export format options."""
    CSV = "csv"
    JSON = "json"


class AuditExportRequest(BaseModel):
    """Request model for audit log export."""
    format: AuditExportFormat = Field(default=AuditExportFormat.CSV, description="Export format")
    filters: Optional[AuditLogFilter] = Field(None, description="Filters to apply to export")


class AuditLogResponse(BaseModel):
    """Response model for paginated audit logs."""
    data: list[AuditLog]
    total: int
    page: int
    page_size: int
    total_pages: int = 0
