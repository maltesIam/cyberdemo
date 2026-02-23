"""
Copilot API endpoints - DEPRECATED.

This module is deprecated. Use src.api.aip_assist instead.
All exports are re-exported from aip_assist for backwards compatibility.

aIP = Artificial Intelligence Person
"""

# Re-export everything from aip_assist for backwards compatibility
from .aip_assist import (
    # Router
    router,
    # Response schemas
    SessionStateResponse,
    SuggestionFeedbackRequest,
    # Endpoint functions
    get_session_state,
    submit_suggestion_feedback,
    # WebSocket functions (deprecated names)
    websocket_aip_assist_actions as websocket_copilot_actions,
)

# Make all exports available at module level
__all__ = [
    "router",
    "SessionStateResponse",
    "SuggestionFeedbackRequest",
    "get_session_state",
    "submit_suggestion_feedback",
    "websocket_copilot_actions",
]
