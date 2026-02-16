"""
MCP (Model Context Protocol) Backend Server Module.

Provides JSON-RPC 2.0 interface for SoulInTheBot to interact with SOC systems.
"""

from .server import router as mcp_router

__all__ = ["mcp_router"]
