"""
Analysis Job Pydantic models.

Task: T-1.1.004
Requirement: TECH-001, TECH-004 - Agent Orchestration and Job Tracking
REQ-001-002-001 to REQ-001-002-006 - Async Analysis Queue requirements

These models define the structure for analysis jobs that are queued
for the AI agent to process asynchronously.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class JobStatus(str, Enum):
    """
    Status states for an analysis job.

    Follows the lifecycle: PENDING -> PROCESSING -> COMPLETED/FAILED/CANCELLED
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Valid job types that can be queued for analysis
# Maps to MCP tools: REQ-001-003-001 to REQ-001-003-006
VALID_JOB_TYPES = [
    "alert_analysis",        # agent_analyze_alert (REQ-001-003-001)
    "ioc_investigation",     # agent_investigate_ioc (REQ-001-003-002)
    "recommendation",        # agent_recommend_action (REQ-001-003-003)
    "report_generation",     # agent_generate_report (REQ-001-003-004)
    "decision_explanation",  # agent_explain_decision (REQ-001-003-005)
    "event_correlation",     # agent_correlate_events (REQ-001-003-006)
]


class AnalysisJob(BaseModel):
    """
    An analysis job queued for the AI agent.

    This model represents a unit of work that the product has requested
    from the AI agent. Jobs are processed asynchronously and their status
    can be tracked via the analysis queue API.

    Attributes:
        id: Unique identifier for the job (auto-generated)
        job_type: Type of analysis to perform (maps to MCP tool)
        payload: Input data for the analysis
        status: Current job status
        result: Output from successful analysis
        error: Error message if job failed
        progress: Completion percentage (0-100)
        created_at: When the job was queued
        started_at: When processing began
        completed_at: When processing finished
        expires_at: When the job should be cleaned up (24h from creation)
    """

    id: str = Field(default_factory=lambda: f"job-{uuid4().hex[:12]}")
    job_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    status: JobStatus = Field(default=JobStatus.PENDING)
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    progress: int = Field(default=0, ge=0, le=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    session_id: Optional[str] = None
    priority: int = Field(default=5, ge=1, le=10)

    @field_validator("job_type")
    @classmethod
    def validate_job_type(cls, v: str) -> str:
        """Validate that job_type is a known type."""
        if v not in VALID_JOB_TYPES:
            raise ValueError(f"Unknown job type: {v}. Valid types: {VALID_JOB_TYPES}")
        return v

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """Override to convert enum to string for serialization."""
        data = super().model_dump(**kwargs)
        if isinstance(data.get("status"), JobStatus):
            data["status"] = data["status"].value
        return data

    class Config:
        json_schema_extra = {
            "example": {
                "id": "job-abc123def456",
                "job_type": "alert_analysis",
                "payload": {"alert_id": "ALT-2024-001"},
                "status": "pending",
                "progress": 0,
                "created_at": "2026-02-22T12:00:00Z"
            }
        }


class AnalysisJobCreateRequest(BaseModel):
    """
    Request model for creating a new analysis job.

    This is the API input model for POST /api/v1/analysis/queue.
    REQ-001-002-001
    """

    job_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=5, ge=1, le=10)
    session_id: Optional[str] = None

    @field_validator("job_type")
    @classmethod
    def validate_job_type(cls, v: str) -> str:
        """Validate that job_type is a known type."""
        if v not in VALID_JOB_TYPES:
            raise ValueError(f"Unknown job type: {v}. Valid types: {VALID_JOB_TYPES}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "job_type": "alert_analysis",
                "payload": {"alert_id": "ALT-2024-001"},
                "priority": 5
            }
        }


class AnalysisJobResponse(BaseModel):
    """
    Response model for analysis job API endpoints.

    This is the API output model for:
    - POST /api/v1/analysis/queue (REQ-001-002-001)
    - GET /api/v1/analysis/status/{job_id} (REQ-001-002-002)
    - GET /api/v1/analysis/result/{job_id} (REQ-001-002-003)
    """

    id: str
    job_type: str
    status: str
    progress: int = Field(ge=0, le=100)
    payload: Optional[dict[str, Any]] = None
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "job-abc123def456",
                "job_type": "alert_analysis",
                "status": "completed",
                "progress": 100,
                "result": {
                    "verdict": "malicious",
                    "confidence": 0.92,
                    "recommendations": ["Isolate host", "Block hash"]
                },
                "created_at": "2026-02-22T12:00:00Z",
                "started_at": "2026-02-22T12:00:01Z",
                "completed_at": "2026-02-22T12:00:05Z"
            }
        }


class AnalysisJobQueueResponse(BaseModel):
    """
    Response when a job is queued successfully.

    Returns the job_id for tracking purposes.
    """

    job_id: str
    status: str = "pending"
    message: str = "Analysis job queued successfully"
    estimated_wait_seconds: Optional[int] = None


class JobStatusUpdate(BaseModel):
    """
    Model for WebSocket job status notifications.

    REQ-001-002-004 - WebSocket /ws/analysis for notifications
    """

    job_id: str
    status: str
    progress: int = Field(ge=0, le=100)
    message: Optional[str] = None
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
