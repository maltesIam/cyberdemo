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


async def handle_intel_get_indicator(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle intel_get_indicator tool call."""
    indicator_type = args.get("indicator_type")
    value = args.get("value")

    if not indicator_type or not value:
        raise ValueError("indicator_type and value are required")

    # Mock data - malicious for certain patterns
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
