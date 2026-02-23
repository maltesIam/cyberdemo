"""
Copilot Service - DEPRECATED.

This module is deprecated. Use src.services.aip_assist_service instead.
All exports are re-exported from aip_assist_service for backwards compatibility.

aIP = Artificial Intelligence Person
"""

# Re-export everything from aip_assist_service for backwards compatibility
from .aip_assist_service import (
    # Primary class and function
    AipAssistService,
    get_aip_assist_service,
    reset_aip_assist_service,
    # Backwards compatibility aliases
    CopilotService,
    get_copilot_service,
)

# Make all exports available at module level
__all__ = [
    "AipAssistService",
    "get_aip_assist_service",
    "reset_aip_assist_service",
    "CopilotService",
    "get_copilot_service",
]
