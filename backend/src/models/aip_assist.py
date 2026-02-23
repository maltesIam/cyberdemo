"""
aIP Assist Models.

Pydantic models for aIP Assist (EPIC-004) that provides
proactive assistance to users (SOC analysts, medical professionals, etc.).

aIP = Artificial Intelligence Person

Implements:
- AipActionType: Enum for action types (REQ-004-001-003)
- AipActionContext: Schema for capturing user action context (REQ-004-001-003)
- AipActionBatch: Schema for batched actions via WebSocket
- AipSuggestionResponse: Schema for aIP suggestions
- AipSessionState: Schema for session tracking (REQ-004-002-005)
- Legacy models for backwards compatibility
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, computed_field


class AipActionType(str, Enum):
    """
    Types of user actions that can be captured by the aIP Assist system.

    REQ-004-001-003: Context includes action type for understanding
    what the user is doing.
    """
    CLICK = "click"
    VIEW = "view"
    SEARCH = "search"
    FILTER = "filter"
    SELECT = "select"
    EXPAND = "expand"
    NAVIGATE = "navigate"
    SUBMIT = "submit"
    HOVER = "hover"
    SCROLL = "scroll"
    SORT = "sort"
    EDIT = "edit"


class AipActionContext(BaseModel):
    """
    Context for a user action captured by the aIP Assist system.

    REQ-004-001-003: Context includes action, element, and visible data.

    This schema captures the full context of user interactions,
    enabling aIP Assist to provide contextually relevant suggestions.

    Required Fields:
        action: Type of action performed (click, view, search, etc.)
        element: UI element type that was interacted with
        session_id: Unique identifier for the user session

    Optional Fields:
        visible_data: Data visible to the user at time of action
        metadata: Additional metadata about the action
        element_id: Specific element ID (e.g., "alert-ALT-001")
        page: Current page/view in the application
        timestamp: When the action occurred (ISO format)
    """
    action: AipActionType = Field(..., description="Type of user action")
    element: str = Field(..., description="UI element type (e.g., 'alert-row', 'button')")
    session_id: str = Field(..., description="Unique session identifier")

    # Optional fields for richer context
    visible_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Data visible to user at time of action"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata about the action"
    )
    element_id: Optional[str] = Field(
        None,
        description="Specific element ID (e.g., 'alert-ALT-001')"
    )
    page: Optional[str] = Field(
        None,
        description="Current page/view (e.g., 'alerts', 'dashboard')"
    )
    timestamp: Optional[str] = Field(
        None,
        description="ISO timestamp when action occurred"
    )


class AipActionBatch(BaseModel):
    """
    A batch of actions for WebSocket transmission.

    Used for efficient transmission of multiple actions
    to the aIP Assist backend via WebSocket.
    """
    session_id: str = Field(..., description="Session identifier")
    actions: List[AipActionContext] = Field(
        ...,
        description="List of actions in this batch"
    )
    batch_timestamp: Optional[str] = Field(
        None,
        description="ISO timestamp when batch was created"
    )


class AipSuggestionResponse(BaseModel):
    """
    A suggestion response from the aIP Assist system.

    Represents a single suggestion that can be shown to the user.
    """
    suggestion_id: str = Field(..., description="Unique suggestion identifier")
    content: str = Field(..., description="Suggestion content/description")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score 0.0-1.0"
    )
    action_type: str = Field(
        ...,
        description="Type of action suggested (investigate, correlate, etc.)"
    )
    reason: Optional[str] = Field(
        None,
        description="Explanation for why this suggestion is relevant"
    )


class AipSessionState(BaseModel):
    """
    Tracks suggestion acceptance/rejection for a session.

    REQ-004-002-005: Tracking of acceptance/rejection by session.
    """
    session_id: str = Field(..., description="Session identifier")
    accepted_suggestions: int = Field(
        default=0,
        ge=0,
        description="Count of accepted suggestions"
    )
    rejected_suggestions: int = Field(
        default=0,
        ge=0,
        description="Count of rejected suggestions"
    )
    total_actions: int = Field(
        default=0,
        ge=0,
        description="Total actions observed"
    )

    @computed_field
    @property
    def acceptance_rate(self) -> float:
        """
        Calculate suggestion acceptance rate.

        Returns 0.0 if no suggestions have been made.
        """
        total = self.accepted_suggestions + self.rejected_suggestions
        if total == 0:
            return 0.0
        return self.accepted_suggestions / total


# =============================================================================
# Legacy Models (for backwards compatibility)
# =============================================================================


class ActionContext(BaseModel):
    """
    Legacy context for a user action captured by aIP Assist.

    This schema captures the context in which a user is working,
    enabling aIP Assist to provide relevant suggestions.

    DEPRECATED: Use AipActionContext for new implementations.

    Attributes:
        session_id: Unique identifier for the user session
        timestamp: When the action occurred
        page: Current page/view in the application
        selected_entity: Currently selected entity (alert, IOC, etc)
        recent_actions: List of the last 10 actions taken
        user_role: Role of the user (analyst, admin, etc)
    """
    session_id: str = Field(..., description="Unique session identifier")
    timestamp: datetime = Field(..., description="Timestamp of the action")
    page: str = Field(..., description="Current page/view (e.g., 'alerts', 'dashboard')")
    selected_entity: Optional[str] = Field(None, description="Currently selected entity ID")
    recent_actions: List[str] = Field(
        default_factory=list,
        description="List of last 10 actions",
        max_length=10
    )
    user_role: str = Field(..., description="User role (analyst, admin, manager)")


class Suggestion(BaseModel):
    """
    A suggestion from the aIP Assist system.

    Attributes:
        action: The suggested action to take
        description: Human-readable description
        confidence: Confidence score 0-1
        reasoning: Why this suggestion is relevant
    """
    action: str = Field(..., description="The suggested action")
    description: str = Field(..., description="Human-readable description")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    reasoning: str = Field(..., description="Why this suggestion is relevant")


class SuggestionResponse(BaseModel):
    """
    Response from aip_get_suggestion tool.
    """
    suggestions: List[Suggestion] = Field(
        default_factory=list,
        description="List of suggestions ordered by confidence"
    )
    timestamp: str = Field(..., description="ISO timestamp of response")


class ExplanationResponse(BaseModel):
    """
    Response from aip_explain_why tool.
    """
    explanation: str = Field(..., description="Detailed explanation")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    alternatives: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Alternative actions considered"
    )


class Completion(BaseModel):
    """
    An auto-completion result.

    Attributes:
        value: The completed value
        confidence: Confidence score 0-1
        source: Where this completion came from
    """
    value: str = Field(..., description="The completed value")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    source: str = Field(..., description="Source of completion (recent, known_iocs, etc)")


class AutoCompleteResponse(BaseModel):
    """
    Response from aip_auto_complete tool.
    """
    completions: List[Completion] = Field(
        default_factory=list,
        description="List of completions ordered by confidence"
    )


# =============================================================================
# Backwards Compatibility Aliases
# =============================================================================
# These aliases allow existing code to continue working during migration

CopilotActionType = AipActionType
CopilotActionContext = AipActionContext
CopilotActionBatch = AipActionBatch
CopilotSuggestionResponse = AipSuggestionResponse
CopilotSessionState = AipSessionState
