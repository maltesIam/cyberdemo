"""
Copilot MCP Tools - DEPRECATED.

This module is deprecated. Use src.mcp.tools.aip_assist instead.
All exports are re-exported from aip_assist for backwards compatibility.

aIP = Artificial Intelligence Person
"""

# Re-export everything from aip_assist for backwards compatibility
from .aip_assist import (
    # Primary exports (new names)
    AIP_ASSIST_TOOLS,
    aip_assist_handlers,
    handle_aip_get_suggestion,
    handle_aip_explain_why,
    handle_aip_auto_complete,
    # Backwards compatibility aliases
    COPILOT_TOOLS,
    copilot_handlers,
    handle_copilot_get_suggestion,
    handle_copilot_explain_why,
    handle_copilot_auto_complete,
)

# Make all exports available at module level
__all__ = [
    # New names
    "AIP_ASSIST_TOOLS",
    "aip_assist_handlers",
    "handle_aip_get_suggestion",
    "handle_aip_explain_why",
    "handle_aip_auto_complete",
    # Backwards compatibility
    "COPILOT_TOOLS",
    "copilot_handlers",
    "handle_copilot_get_suggestion",
    "handle_copilot_explain_why",
    "handle_copilot_auto_complete",
]
