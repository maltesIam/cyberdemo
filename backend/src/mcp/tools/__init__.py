"""
MCP Tools Registry.

Registers all available tools that SoulInTheBot can use.
Each tool has:
- name: Unique identifier
- description: What the tool does
- inputSchema: JSON Schema for parameters
- handler: Async function to execute
"""

from typing import Any, Callable, Dict, List, Awaitable
from .siem import SIEM_TOOLS, siem_handlers
from .edr import EDR_TOOLS, edr_handlers
from .intel import INTEL_TOOLS, intel_handlers
from .ctem import CTEM_TOOLS, ctem_handlers
from .approvals import APPROVAL_TOOLS, approval_handlers
from .tickets import TICKET_TOOLS, ticket_handlers
from .reports import REPORT_TOOLS, report_handlers


def get_all_tools() -> List[Dict[str, Any]]:
    """Get all registered MCP tools."""
    tools = []
    tools.extend(SIEM_TOOLS)
    tools.extend(EDR_TOOLS)
    tools.extend(INTEL_TOOLS)
    tools.extend(CTEM_TOOLS)
    tools.extend(APPROVAL_TOOLS)
    tools.extend(TICKET_TOOLS)
    tools.extend(REPORT_TOOLS)
    return tools


def get_tool_handlers() -> Dict[str, Callable[[Dict[str, Any]], Awaitable[Any]]]:
    """Get all tool handlers by name."""
    handlers = {}
    handlers.update(siem_handlers)
    handlers.update(edr_handlers)
    handlers.update(intel_handlers)
    handlers.update(ctem_handlers)
    handlers.update(approval_handlers)
    handlers.update(ticket_handlers)
    handlers.update(report_handlers)
    return handlers
