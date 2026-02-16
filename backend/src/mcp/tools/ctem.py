"""
CTEM MCP Tools.

Tools for querying Continuous Threat Exposure Management data.
"""

from typing import Any, Dict, List

# Tool definitions
CTEM_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "ctem_get_asset_risk",
        "description": "Get risk assessment and vulnerabilities for an asset.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "asset_id": {
                    "type": "string",
                    "description": "The asset ID to check"
                }
            },
            "required": ["asset_id"]
        }
    }
]


async def handle_ctem_get_asset_risk(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle ctem_get_asset_risk tool call."""
    asset_id = args.get("asset_id")

    if not asset_id:
        raise ValueError("asset_id is required")

    # Mock risk data - VIP assets have special tags
    is_vip = "CFO" in asset_id.upper() or "VIP" in asset_id.upper()
    is_server = "SRV" in asset_id.upper()

    return {
        "asset_id": asset_id,
        "risk_color": "Yellow" if is_server else "Green",
        "risk_score": 65 if is_server else 35,
        "asset_tags": ["vip", "executive"] if is_vip else ["standard-user"],
        "vulnerabilities": [
            {"cve": "CVE-2026-1234", "severity": "high"} if is_server else None
        ],
        "last_scan": "2026-02-13T00:00:00Z"
    }


# Handler mapping
ctem_handlers = {
    "ctem_get_asset_risk": handle_ctem_get_asset_risk,
}
