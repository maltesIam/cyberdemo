"""
Intel MCP Tools.

Tools for querying threat intelligence about indicators.
"""

from typing import Any, Dict, List

# Tool definitions
INTEL_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "intel_get_indicator",
        "description": "Get threat intelligence for an indicator (hash, IP, domain).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "indicator_type": {
                    "type": "string",
                    "enum": ["filehash", "ip", "domain", "url"],
                    "description": "Type of indicator"
                },
                "value": {
                    "type": "string",
                    "description": "The indicator value to lookup"
                }
            },
            "required": ["indicator_type", "value"]
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


# Map intel_get_indicator types to scenario IOC types
_INDICATOR_TYPE_MAP = {
    "filehash": "hash",
    "ip": "ip",
    "domain": "domain",
    "url": "url",
}


async def handle_intel_get_indicator(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle intel_get_indicator tool call."""
    indicator_type = args.get("indicator_type")
    value = args.get("value")

    if not indicator_type or not value:
        raise ValueError("indicator_type and value are required")

    # Check if scenario is active (REQ-002-004-001)
    mgr = _get_scenario_mgr()
    if mgr and mgr.is_active():
        # Map the indicator type to scenario IOC type
        ioc_type = _INDICATOR_TYPE_MAP.get(indicator_type, indicator_type)
        ioc = mgr.get_ioc_by_value(ioc_type, value)
        if ioc:
            return {
                "indicator_type": indicator_type,
                "value": value,
                "verdict": "malicious",
                "vt_score": int(ioc["confidence_score"] * 0.5),
                "labels": ["apt29", "cozy-bear"],
                "sources": [ioc["source"]],
                "first_seen": "2026-01-15T00:00:00Z",
                "confidence": ioc["confidence_score"],
                "associated_threat": ioc["associated_threat"],
            }
        # IOC not found in current phase data - return benign
        return {
            "indicator_type": indicator_type,
            "value": value,
            "verdict": "benign",
            "vt_score": 0,
            "labels": [],
            "sources": ["VirusTotal"],
            "first_seen": None,
            "confidence": 10,
        }

    # Static mock data (backward compatibility)
    is_malicious = "malicious" in value.lower() or value.startswith("abc123")

    return {
        "indicator_type": indicator_type,
        "value": value,
        "verdict": "malicious" if is_malicious else "benign",
        "vt_score": 45 if is_malicious else 0,
        "labels": ["malware", "trojan"] if is_malicious else [],
        "sources": ["VirusTotal", "MISP"] if is_malicious else ["VirusTotal"],
        "first_seen": "2026-01-15T00:00:00Z" if is_malicious else None,
        "confidence": 95 if is_malicious else 10
    }


# Handler mapping
intel_handlers = {
    "intel_get_indicator": handle_intel_get_indicator,
}
