"""
MCP Data Tools Registry.

Provides data generation tools that can be called via MCP protocol.
Each tool generates synthetic cybersecurity data.
"""

from typing import Any, Callable, Dict, List, Awaitable
from .generators import DATA_TOOLS, data_handlers


def get_all_data_tools() -> List[Dict[str, Any]]:
    """Get all registered MCP data tools."""
    return DATA_TOOLS


def get_data_tool_handlers() -> Dict[str, Callable[[Dict[str, Any]], Awaitable[Any]]]:
    """Get all data tool handlers by name."""
    return data_handlers


__all__ = [
    "get_all_data_tools",
    "get_data_tool_handlers",
    "DATA_TOOLS",
    "data_handlers",
]
