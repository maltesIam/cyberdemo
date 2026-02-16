"""
Playbook data models.

Defines the structure for SOAR playbooks including steps,
execution runs, and status tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class PlaybookRunStatus(str, Enum):
    """Status of a playbook execution run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    """Status of an individual step execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


@dataclass
class PlaybookStep:
    """A single step in a playbook.

    Attributes:
        action: The action to execute (e.g., "edr.contain_host")
        params: Parameters to pass to the action
        timeout: Maximum execution time in seconds
        on_error: Error handling behavior (fail, continue, notify_human)
    """
    action: str
    params: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 120  # Default 2 minutes
    on_error: str = "fail"  # fail, continue, notify_human

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlaybookStep":
        """Create a PlaybookStep from a dictionary."""
        return cls(
            action=data["action"],
            params=data.get("params", {}),
            timeout=data.get("timeout", 120),
            on_error=data.get("on_error", "fail")
        )


@dataclass
class Playbook:
    """A security playbook definition.

    Attributes:
        id: Unique identifier for the playbook
        name: Human-readable name
        description: Description of what the playbook does
        triggers: List of events that can trigger this playbook
        steps: Ordered list of steps to execute
        enabled: Whether the playbook is active
        created_at: When the playbook was created
        updated_at: When the playbook was last modified
    """
    id: str
    name: str
    description: str
    triggers: List[str]
    steps: List[PlaybookStep]
    enabled: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = self.created_at

    @classmethod
    def from_dict(cls, data: Dict[str, Any], playbook_id: Optional[str] = None) -> "Playbook":
        """Create a Playbook from a dictionary (typically loaded from YAML).

        Args:
            data: Dictionary with playbook definition
            playbook_id: Optional ID to use, otherwise generated
        """
        steps = [
            PlaybookStep.from_dict(s) if isinstance(s, dict) else s
            for s in data.get("steps", [])
        ]

        return cls(
            id=playbook_id or f"pb-{uuid4().hex[:8]}",
            name=data["name"],
            description=data.get("description", ""),
            triggers=data.get("triggers", []),
            steps=steps,
            enabled=data.get("enabled", True)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert playbook to dictionary for YAML serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "triggers": self.triggers,
            "steps": [
                {
                    "action": step.action,
                    "params": step.params,
                    "timeout": step.timeout,
                    "on_error": step.on_error
                }
                for step in self.steps
            ],
            "enabled": self.enabled
        }


@dataclass
class StepResult:
    """Result of executing a single playbook step.

    Attributes:
        step_index: Index of the step in the playbook
        action: The action that was executed
        status: Execution status
        result: Output from the action (if successful)
        error: Error message (if failed)
        duration_ms: How long the step took in milliseconds
        started_at: When the step started
        completed_at: When the step finished
    """
    step_index: int
    action: str
    status: StepStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "step_index": self.step_index,
            "action": self.action,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class PlaybookRun:
    """Record of a playbook execution.

    Attributes:
        id: Unique identifier for this run
        playbook_id: ID of the playbook that was executed
        playbook_name: Name of the playbook
        status: Current execution status
        context: Input context provided for execution
        step_results: Results of each step
        started_at: When execution began
        completed_at: When execution finished
        triggered_by: What triggered this run
        error: Overall error message (if failed)
    """
    id: str
    playbook_id: str
    playbook_name: str
    status: PlaybookRunStatus
    context: Dict[str, Any] = field(default_factory=dict)
    step_results: List[StepResult] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    triggered_by: Optional[str] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.utcnow()

    @classmethod
    def create(
        cls,
        playbook: Playbook,
        context: Dict[str, Any],
        triggered_by: Optional[str] = None
    ) -> "PlaybookRun":
        """Create a new run for a playbook."""
        return cls(
            id=f"run-{uuid4().hex[:12]}",
            playbook_id=playbook.id,
            playbook_name=playbook.name,
            status=PlaybookRunStatus.PENDING,
            context=context,
            triggered_by=triggered_by
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "playbook_id": self.playbook_id,
            "playbook_name": self.playbook_name,
            "status": self.status.value,
            "context": self.context,
            "step_results": [r.to_dict() for r in self.step_results],
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "triggered_by": self.triggered_by,
            "error": self.error
        }
