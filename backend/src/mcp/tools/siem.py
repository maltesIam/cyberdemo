"""
SIEM MCP Tools.

Tools for interacting with the SIEM (Security Information and Event Management) system.
"""

from typing import Any, Dict, List

# Tool definitions
SIEM_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "siem_list_incidents",
        "description": "List security incidents from SIEM. Can filter by severity, status, or date range.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "severity": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "description": "Filter by severity level"
                },
                "status": {
                    "type": "string",
                    "enum": ["open", "investigating", "contained", "closed"],
                    "description": "Filter by incident status"
                },
                "limit": {
                    "type": "integer",
                    "default": 50,
                    "description": "Maximum number of incidents to return"
                }
            }
        }
    },
    {
        "name": "siem_get_incident",
        "description": "Get detailed information about a specific incident by ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "incident_id": {
                    "type": "string",
                    "description": "The incident ID (e.g., INC-ANCHOR-001)"
                }
            },
            "required": ["incident_id"]
        }
    },
    {
        "name": "siem_add_comment",
        "description": "Add an investigation comment to an incident.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "incident_id": {
                    "type": "string",
                    "description": "The incident ID"
                },
                "comment": {
                    "type": "string",
                    "description": "The comment text to add"
                }
            },
            "required": ["incident_id", "comment"]
        }
    },
    {
        "name": "siem_close_incident",
        "description": "Close an incident with a resolution.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "incident_id": {
                    "type": "string",
                    "description": "The incident ID"
                },
                "resolution": {
                    "type": "string",
                    "enum": ["true_positive", "false_positive", "benign"],
                    "description": "Resolution type"
                },
                "notes": {
                    "type": "string",
                    "description": "Closure notes"
                }
            },
            "required": ["incident_id", "resolution"]
        }
    }
]


# Tool handlers
async def handle_siem_list_incidents(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle siem_list_incidents tool call."""
    severity = args.get("severity")
    status = args.get("status")
    limit = args.get("limit", 50)

    # Mock data for demo
    incidents = [
        {
            "id": "INC-ANCHOR-001",
            "title": "Suspicious PowerShell Activity",
            "severity": "critical",
            "status": "open",
            "asset": "WS-FIN-042",
            "created_at": "2026-02-14T10:30:00Z"
        },
        {
            "id": "INC-ANCHOR-002",
            "title": "VIP Device - Malware Detected",
            "severity": "critical",
            "status": "investigating",
            "asset": "LAPTOP-CFO-01",
            "created_at": "2026-02-14T11:15:00Z"
        },
        {
            "id": "INC-ANCHOR-003",
            "title": "Benign Script Execution",
            "severity": "low",
            "status": "open",
            "asset": "SRV-DEV-03",
            "created_at": "2026-02-14T09:00:00Z"
        }
    ]

    # Apply filters
    if severity:
        incidents = [i for i in incidents if i["severity"] == severity]
    if status:
        incidents = [i for i in incidents if i["status"] == status]

    return {"data": incidents[:limit], "total": len(incidents)}


async def handle_siem_get_incident(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle siem_get_incident tool call."""
    incident_id = args.get("incident_id")

    if not incident_id:
        raise ValueError("incident_id is required")

    # Mock data for anchor incidents
    incidents = {
        "INC-ANCHOR-001": {
            "id": "INC-ANCHOR-001",
            "title": "Suspicious PowerShell Activity",
            "description": "PowerShell encoded command detected on finance workstation",
            "severity": "critical",
            "status": "open",
            "asset": "WS-FIN-042",
            "detection_ids": ["DET-001"],
            "created_at": "2026-02-14T10:30:00Z",
            "entities": ["192.168.1.42", "malware.exe", "DOMAIN\\finance_user"]
        },
        "INC-ANCHOR-002": {
            "id": "INC-ANCHOR-002",
            "title": "VIP Device - Malware Detected",
            "severity": "critical",
            "status": "investigating",
            "asset": "LAPTOP-CFO-01",
            "detection_ids": ["DET-002"],
            "created_at": "2026-02-14T11:15:00Z"
        }
    }

    if incident_id not in incidents:
        # Return a generic incident for unknown IDs
        return {
            "id": incident_id,
            "title": f"Incident {incident_id}",
            "severity": "medium",
            "status": "open",
            "created_at": "2026-02-14T12:00:00Z"
        }

    return incidents[incident_id]


async def handle_siem_add_comment(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle siem_add_comment tool call."""
    incident_id = args.get("incident_id")
    comment = args.get("comment")

    if not incident_id or not comment:
        raise ValueError("incident_id and comment are required")

    return {
        "status": "success",
        "incident_id": incident_id,
        "comment_id": f"CMT-{incident_id[-3:]}-001",
        "message": "Comment added successfully"
    }


async def handle_siem_close_incident(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle siem_close_incident tool call."""
    incident_id = args.get("incident_id")
    resolution = args.get("resolution")

    if not incident_id or not resolution:
        raise ValueError("incident_id and resolution are required")

    return {
        "status": "success",
        "incident_id": incident_id,
        "resolution": resolution,
        "closed_at": "2026-02-14T15:00:00Z"
    }


# Handler mapping
siem_handlers = {
    "siem_list_incidents": handle_siem_list_incidents,
    "siem_get_incident": handle_siem_get_incident,
    "siem_add_comment": handle_siem_add_comment,
    "siem_close_incident": handle_siem_close_incident,
}
