"""
Reports MCP Tools.

Tools for generating incident postmortems and reports.
"""

from typing import Any, Dict, List

# Tool definitions
REPORT_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "reports_generate_postmortem",
        "description": "Generate a postmortem report for a closed incident.",
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
        "name": "reports_get_postmortem",
        "description": "Get an existing postmortem report.",
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
    }
]


async def handle_reports_generate_postmortem(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle reports_generate_postmortem tool call."""
    incident_id = args.get("incident_id")

    if not incident_id:
        raise ValueError("incident_id is required")

    return {
        "status": "success",
        "postmortem_id": f"PM-{incident_id[-3:]}-001",
        "incident_id": incident_id,
        "generated_at": "2026-02-14T15:30:00Z",
        "sections": [
            "Executive Summary",
            "Timeline of Events",
            "Root Cause Analysis",
            "Impact Assessment",
            "Remediation Actions",
            "Lessons Learned",
            "Recommendations"
        ],
        "message": "Postmortem report generated successfully"
    }


async def handle_reports_get_postmortem(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle reports_get_postmortem tool call."""
    incident_id = args.get("incident_id")

    if not incident_id:
        raise ValueError("incident_id is required")

    return {
        "postmortem_id": f"PM-{incident_id[-3:]}-001",
        "incident_id": incident_id,
        "generated_at": "2026-02-14T15:30:00Z",
        "executive_summary": "A sophisticated malware attack was detected and contained within 15 minutes.",
        "timeline": [
            {"time": "10:30", "event": "Initial detection"},
            {"time": "10:32", "event": "Investigation started"},
            {"time": "10:35", "event": "Containment executed"},
            {"time": "10:45", "event": "Ticket created"}
        ],
        "root_cause": "Phishing email with malicious attachment",
        "impact": "1 workstation compromised, 0 data exfiltration",
        "recommendations": ["Enhance email filtering", "User awareness training"]
    }


# Handler mapping
report_handlers = {
    "reports_generate_postmortem": handle_reports_generate_postmortem,
    "reports_get_postmortem": handle_reports_get_postmortem,
}
