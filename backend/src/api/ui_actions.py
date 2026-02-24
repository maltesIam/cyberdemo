"""
REST endpoint for UI actions - POST /api/v1/ui/action

REQ-001-002-002: POST request with action payload returns 200 and forwards command to WS Server.
TECH-003: REST endpoint POST /api/v1/ui/action for programmatic UI control.

Receives UI commands and forwards them via UIBridge to the Frontend MCP WS Server.
"""

import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from ..services.ui_bridge import UIBridge

logger = logging.getLogger(__name__)

router = APIRouter()

# Valid UI action types
VALID_UI_ACTIONS = {"navigate", "highlight", "chart", "timeline"}

# Module-level UIBridge singleton (lazily connected)
_ui_bridge: UIBridge | None = None


def get_ui_bridge() -> UIBridge:
    """Get or create the module-level UIBridge instance."""
    global _ui_bridge
    if _ui_bridge is None:
        _ui_bridge = UIBridge()
    return _ui_bridge


class UIActionRequest(BaseModel):
    """Request body for the UI action endpoint.

    Attributes:
        action: The type of UI action (navigate, highlight, chart, timeline)
        params: Action-specific parameters
    """

    action: str
    params: dict[str, Any]


async def handle_ui_action(
    request: UIActionRequest,
    ui_bridge: UIBridge | None = None,
) -> dict[str, Any]:
    """Handle a UI action request by forwarding to UIBridge.

    Args:
        request: The UI action request
        ui_bridge: Optional UIBridge instance (for dependency injection in tests)

    Returns:
        dict with status and optional message
    """
    bridge = ui_bridge or get_ui_bridge()

    if request.action not in VALID_UI_ACTIONS:
        return {
            "status": "error",
            "message": f"Unknown action '{request.action}'. Valid actions: {sorted(VALID_UI_ACTIONS)}",
        }

    if request.action == "navigate":
        page = request.params.get("page", "/")
        await bridge.send_navigation(page)
    elif request.action == "highlight":
        assets = request.params.get("assets", [])
        await bridge.send_highlight(assets)
    elif request.action == "chart":
        chart_data = request.params.get("chart_data", {})
        await bridge.send_chart(chart_data)
    elif request.action == "timeline":
        timeline_data = request.params.get("timeline_data", {})
        await bridge.send_timeline(timeline_data)

    return {"status": "ok", "action": request.action}


@router.post("/v1/ui/action")
async def ui_action_endpoint(request: UIActionRequest) -> dict[str, Any]:
    """POST /api/v1/ui/action - Forward UI commands to the MCP WS Server.

    Accepts action payloads and forwards them via UIBridge.
    """
    return await handle_ui_action(request)
