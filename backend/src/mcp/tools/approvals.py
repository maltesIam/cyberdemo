"""
Approvals MCP Tools.

Tools for managing approval workflows for sensitive actions.
"""

from typing import Any, Dict, List

# Tool definitions
APPROVAL_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "approvals_get",
        "description": "Get the status of an approval request for an incident.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "incident_id": {
                    "type": "string",
                    "description": "The incident ID"
                }
            },
            "required": ["incident_id"]
        }
    },
    {
        "name": "approvals_request",
        "description": "Request approval for a sensitive action (e.g., contain VIP device).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "incident_id": {
                    "type": "string",
                    "description": "The incident ID"
                },
                "action": {
                    "type": "string",
                    "enum": ["contain", "isolate", "disable_user"],
                    "description": "The action requiring approval"
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for the action"
                }
            },
            "required": ["incident_id", "action", "reason"]
        }
    }
]


async def handle_approvals_get(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle approvals_get tool call."""
    incident_id = args.get("incident_id")

    if not incident_id:
        raise ValueError("incident_id is required")

    return {
        "incident_id": incident_id,
        "status": "pending",
        "action": "contain",
        "requested_at": "2026-02-14T11:20:00Z",
        "requested_by": "soulbot",
        "decided_by": None,
        "decision_time": None
    }


async def handle_approvals_request(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle approvals_request tool call."""
    incident_id = args.get("incident_id")
    action = args.get("action")
    reason = args.get("reason")

    if not incident_id or not action or not reason:
        raise ValueError("incident_id, action, and reason are required")

    return {
        "status": "success",
        "approval_id": f"APR-{incident_id[-3:]}-001",
        "incident_id": incident_id,
        "action": action,
        "reason": reason,
        "requested_at": "2026-02-14T11:20:00Z",
        "message": "Approval request created and sent to security team"
    }


# Handler mapping
approval_handlers = {
    "approvals_get": handle_approvals_get,
    "approvals_request": handle_approvals_request,
}
