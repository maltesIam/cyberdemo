"""
EDR MCP Tools.

Tools for interacting with the EDR (Endpoint Detection and Response) system.
"""

from typing import Any, Dict, List

# Tool definitions
EDR_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "edr_get_detection",
        "description": "Get detailed information about a specific detection.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "detection_id": {
                    "type": "string",
                    "description": "The detection ID"
                }
            },
            "required": ["detection_id"]
        }
    },
    {
        "name": "edr_get_process_tree",
        "description": "Get the process tree for a detection showing parent/child relationships.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "detection_id": {
                    "type": "string",
                    "description": "The detection ID"
                }
            },
            "required": ["detection_id"]
        }
    },
    {
        "name": "edr_hunt_hash",
        "description": "Hunt for a file hash across all endpoints to find propagation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "hash": {
                    "type": "string",
                    "description": "The SHA256 hash to search for"
                }
            },
            "required": ["hash"]
        }
    },
    {
        "name": "edr_contain_host",
        "description": "Isolate a host from the network to prevent lateral movement.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "The device ID to contain"
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for containment"
                }
            },
            "required": ["device_id", "reason"]
        }
    },
    {
        "name": "edr_lift_containment",
        "description": "Remove network isolation from a previously contained host.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "The device ID to release"
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for lifting containment"
                }
            },
            "required": ["device_id", "reason"]
        }
    },
    {
        "name": "edr_list_detections",
        "description": "List recent detections from EDR system.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "severity": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "description": "Filter by severity"
                },
                "limit": {
                    "type": "integer",
                    "default": 50,
                    "description": "Maximum detections to return"
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


# Tool handlers
async def handle_edr_get_detection(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle edr_get_detection tool call."""
    detection_id = args.get("detection_id")

    if not detection_id:
        raise ValueError("detection_id is required")

    # Check if scenario is active (REQ-002-004-001)
    mgr = _get_scenario_mgr()
    if mgr and mgr.is_active():
        detection = mgr.get_detection_by_id(detection_id)
        if detection:
            return detection

    # Static mock data (backward compatibility)
    return {
        "id": detection_id,
        "technique_id": "T1059.001",
        "technique_name": "PowerShell",
        "severity": "critical",
        "device_id": "DEV-WS-FIN-042",
        "hostname": "WS-FIN-042",
        "asset_id": "ASSET-FIN-042",
        "process_name": "powershell.exe",
        "process_hash": "abc123def456789malicious",
        "command_line": "powershell.exe -enc SQBuAHYAbwBrAGUA...",
        "user": "DOMAIN\\finance_user",
        "timestamp": "2026-02-14T10:30:00Z"
    }


async def handle_edr_get_process_tree(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle edr_get_process_tree tool call."""
    detection_id = args.get("detection_id")

    if not detection_id:
        raise ValueError("detection_id is required")

    return {
        "detection_id": detection_id,
        "process_tree": {
            "name": "explorer.exe",
            "pid": 1234,
            "children": [
                {
                    "name": "outlook.exe",
                    "pid": 2345,
                    "children": [
                        {
                            "name": "WINWORD.EXE",
                            "pid": 3456,
                            "children": [
                                {
                                    "name": "cmd.exe",
                                    "pid": 4567,
                                    "suspicious": True,
                                    "children": [
                                        {
                                            "name": "powershell.exe",
                                            "pid": 5678,
                                            "suspicious": True,
                                            "command_line": "powershell.exe -enc SQBuAHYAbwBrAGUA...",
                                            "children": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }


async def handle_edr_hunt_hash(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle edr_hunt_hash tool call."""
    hash_value = args.get("hash")

    if not hash_value:
        raise ValueError("hash is required")

    # Mock propagation data
    return {
        "hash": hash_value,
        "total_hosts_found": 3,
        "hosts": [
            {"hostname": "WS-FIN-042", "first_seen": "2026-02-14T10:30:00Z"},
            {"hostname": "WS-FIN-043", "first_seen": "2026-02-14T10:45:00Z"},
            {"hostname": "SRV-FILE-01", "first_seen": "2026-02-14T11:00:00Z"}
        ]
    }


async def handle_edr_contain_host(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle edr_contain_host tool call."""
    device_id = args.get("device_id")
    reason = args.get("reason")

    if not device_id or not reason:
        raise ValueError("device_id and reason are required")

    # Register mutation in scenario state (REQ-002-004-003)
    mgr = _get_scenario_mgr()
    if mgr and mgr.is_active():
        mgr.contain_host(device_id)

    return {
        "status": "success",
        "device_id": device_id,
        "action": "contain",
        "reason": reason,
        "executed_at": "2026-02-14T10:35:00Z",
        "message": f"Device {device_id} has been isolated from the network"
    }


async def handle_edr_lift_containment(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle edr_lift_containment tool call."""
    device_id = args.get("device_id")
    reason = args.get("reason")

    if not device_id or not reason:
        raise ValueError("device_id and reason are required")

    # Register mutation in scenario state (REQ-002-004-003)
    mgr = _get_scenario_mgr()
    if mgr and mgr.is_active():
        mgr.lift_containment(device_id)

    return {
        "status": "success",
        "device_id": device_id,
        "action": "lift_containment",
        "reason": reason,
        "executed_at": "2026-02-14T16:00:00Z"
    }


async def handle_edr_list_detections(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle edr_list_detections tool call."""
    severity = args.get("severity")
    limit = args.get("limit", 50)

    # Check if scenario is active (REQ-002-004-001)
    mgr = _get_scenario_mgr()
    if mgr and mgr.is_active():
        detections = mgr.get_detections(severity=severity, limit=limit)
        return {"data": detections, "total": len(detections)}

    # Static mock data (backward compatibility)
    detections = [
        {
            "id": "DET-001",
            "technique_id": "T1059.001",
            "severity": "critical",
            "hostname": "WS-FIN-042"
        },
        {
            "id": "DET-002",
            "technique_id": "T1055",
            "severity": "high",
            "hostname": "LAPTOP-CFO-01"
        }
    ]

    if severity:
        detections = [d for d in detections if d["severity"] == severity]

    return {"data": detections[:limit], "total": len(detections)}


# Handler mapping
edr_handlers = {
    "edr_get_detection": handle_edr_get_detection,
    "edr_get_process_tree": handle_edr_get_process_tree,
    "edr_hunt_hash": handle_edr_hunt_hash,
    "edr_contain_host": handle_edr_contain_host,
    "edr_lift_containment": handle_edr_lift_containment,
    "edr_list_detections": handle_edr_list_detections,
}
