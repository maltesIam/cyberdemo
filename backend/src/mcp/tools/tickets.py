"""
Tickets MCP Tools.

Tools for creating and managing IT service tickets.
"""

from typing import Any, Dict, List

# Tool definitions
TICKET_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "tickets_create",
        "description": "Create a new IT service ticket for an incident.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Ticket title"
                },
                "description": {
                    "type": "string",
                    "description": "Detailed description"
                },
                "incident_id": {
                    "type": "string",
                    "description": "Related incident ID"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "high",
                    "description": "Ticket priority"
                }
            },
            "required": ["title", "description", "incident_id"]
        }
    },
    {
        "name": "tickets_list",
        "description": "List tickets, optionally filtered by incident.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "incident_id": {
                    "type": "string",
                    "description": "Filter by incident ID"
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "description": "Maximum tickets to return"
                }
            }
        }
    }
]


def _get_scenario_mgr():
    """Get the ScenarioStateManager if available."""
    try:
        from src.scenarios.scenario_state_manager import get_scenario_manager
        return get_scenario_manager()
    except ImportError:
        return None


async def handle_tickets_create(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tickets_create tool call."""
    title = args.get("title")
    description = args.get("description")
    incident_id = args.get("incident_id")
    priority = args.get("priority", "high")

    if not title or not description or not incident_id:
        raise ValueError("title, description, and incident_id are required")

    # Register mutation in scenario state (REQ-002-004-003)
    mgr = _get_scenario_mgr()
    if mgr and mgr.is_active():
        ticket_id = mgr.create_ticket({
            "title": title,
            "description": description,
            "incident_id": incident_id,
            "priority": priority,
        })
        return {
            "status": "success",
            "ticket_id": ticket_id,
            "title": title,
            "incident_id": incident_id,
            "priority": priority,
            "created_at": "2026-02-14T12:00:00Z",
            "message": "Ticket created successfully in ServiceNow"
        }

    return {
        "status": "success",
        "ticket_id": f"TKT-{incident_id[-3:]}-001",
        "title": title,
        "incident_id": incident_id,
        "priority": priority,
        "created_at": "2026-02-14T12:00:00Z",
        "message": "Ticket created successfully in ServiceNow"
    }


async def handle_tickets_list(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tickets_list tool call."""
    incident_id = args.get("incident_id")
    limit = args.get("limit", 20)

    # Check if scenario is active (REQ-002-004-001)
    mgr = _get_scenario_mgr()
    if mgr and mgr.is_active():
        tickets = mgr.get_tickets_for_incident(incident_id, limit)
        if tickets:
            return {"data": tickets, "total": len(tickets)}
        # Fall through to static if no scenario tickets

    # Static mock data (backward compatibility)
    tickets = [
        {
            "ticket_id": "TKT-001-001",
            "title": "Security Incident: Malware Containment",
            "incident_id": "INC-ANCHOR-001",
            "status": "open",
            "priority": "critical"
        }
    ]

    if incident_id:
        tickets = [t for t in tickets if t["incident_id"] == incident_id]

    return {"data": tickets[:limit], "total": len(tickets)}


# Handler mapping
ticket_handlers = {
    "tickets_create": handle_tickets_create,
    "tickets_list": handle_tickets_list,
}
