"""
Copilot Mode Models - DEPRECATED.

This module is deprecated. Use src.models.aip_assist instead.
All exports are re-exported from aip_assist for backwards compatibility.

aIP = Artificial Intelligence Person
"""

# Re-export everything from aip_assist for backwards compatibility
from .aip_assist import (
    # Primary types (new names)
    AipActionType,
    AipActionContext,
    AipActionBatch,
    AipSuggestionResponse,
    AipSessionState,
    # Backwards compatibility aliases
    CopilotActionType,
    CopilotActionContext,
    CopilotActionBatch,
    CopilotSuggestionResponse,
    CopilotSessionState,
    # Legacy models
    ActionContext,
    Suggestion,
    SuggestionResponse,
    ExplanationResponse,
    Completion,
    AutoCompleteResponse,
)

# Make all exports available at module level
__all__ = [
    # Primary types
    "AipActionType",
    "AipActionContext",
    "AipActionBatch",
    "AipSuggestionResponse",
    "AipSessionState",
    # Backwards compatibility
    "CopilotActionType",
    "CopilotActionContext",
    "CopilotActionBatch",
    "CopilotSuggestionResponse",
    "CopilotSessionState",
    # Legacy models
    "ActionContext",
    "Suggestion",
    "SuggestionResponse",
    "ExplanationResponse",
    "Completion",
    "AutoCompleteResponse",
]
