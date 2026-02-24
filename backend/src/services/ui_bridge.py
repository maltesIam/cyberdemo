"""
UIBridge - Backend to Frontend MCP WS Server Bridge.

Provides an async WebSocket client that lazily connects to the MCP WS Server
(port 3001) and forwards UI control commands. Connection is established on
first use and reused for subsequent calls.

REQ-001-002-001: UIBridge WebSocket client connects to WS Server (lazy, first use)
REQ-001-002-003: Silent failure when WS Server is unavailable (no crash)
TECH-002: UIBridge Python class with async WebSocket client
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Alias for the websockets.connect function, allowing tests to patch it easily
try:
    from websockets.asyncio.client import connect as websockets_connect
except ImportError:
    try:
        from websockets import connect as websockets_connect
    except ImportError:
        websockets_connect = None  # type: ignore[assignment]


class UIBridge:
    """Async WebSocket bridge to the Frontend MCP WS Server.

    Lazily connects to ws://localhost:3001 on first send_* call
    and reuses the connection for all subsequent calls.

    Methods:
        send_navigation(page): Navigate to a page
        send_highlight(assets): Highlight assets on the graph
        send_chart(chart_data): Show a chart overlay
        send_timeline(timeline_data): Show the timeline panel
        disconnect(): Close the WebSocket connection
    """

    def __init__(self, ws_url: str = "ws://localhost:3001") -> None:
        self._ws_url = ws_url
        self._ws: Any = None

    async def _ensure_connected(self) -> bool:
        """Lazily establish WebSocket connection on first use.

        Returns:
            True if connected, False if connection failed (silent failure).
        """
        if self._ws is None:
            try:
                self._ws = await websockets_connect(self._ws_url)
            except Exception:
                logger.warning(
                    "UIBridge: Failed to connect to WS Server at %s",
                    self._ws_url,
                )
                return False
        return True

    async def _send_tool_call(self, tool: str, params: dict[str, Any]) -> None:
        """Send a tool_call message to the WS Server.

        Silently fails if connection or send fails (REQ-001-002-003, BR-006).

        Args:
            tool: The MCP tool name to call
            params: The parameters for the tool call
        """
        if not await self._ensure_connected():
            return

        message = json.dumps({
            "type": "tool_call",
            "tool": tool,
            "params": params,
        })
        try:
            await self._ws.send(message)
        except Exception:
            logger.warning(
                "UIBridge: Failed to send %s command, resetting connection",
                tool,
            )
            # Reset connection so next call attempts to reconnect
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None

    async def send_navigation(self, page: str) -> None:
        """Navigate the UI to the specified page.

        Args:
            page: The page path to navigate to (e.g., '/siem', '/edr')
        """
        await self._send_tool_call("navigate_to_page", {"page": page})

    async def send_highlight(self, assets: list[str]) -> None:
        """Highlight specified assets on the graph page.

        Args:
            assets: List of asset IDs to highlight
        """
        await self._send_tool_call("highlight_assets", {"assets": assets})

    async def send_chart(self, chart_data: dict[str, Any]) -> None:
        """Show a chart overlay in the UI.

        Args:
            chart_data: Chart configuration with type, title, and data
        """
        await self._send_tool_call("show_chart", {"chart_data": chart_data})

    async def send_timeline(self, timeline_data: dict[str, Any]) -> None:
        """Show the timeline panel in the UI.

        Args:
            timeline_data: Timeline configuration with entries list
        """
        await self._send_tool_call("show_timeline", {"timeline_data": timeline_data})

    async def disconnect(self) -> None:
        """Close the WebSocket connection if open."""
        if self._ws is not None:
            try:
                await self._ws.close()
            except Exception:
                logger.warning("UIBridge: Error closing WebSocket connection")
            finally:
                self._ws = None
