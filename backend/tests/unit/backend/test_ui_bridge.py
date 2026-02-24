"""
Unit tests for UIBridge - UT-007
Requirement: REQ-001-002-001
Description: UIBridge WebSocket client connects to WS Server and sends commands.

The UIBridge class provides async WebSocket client that lazily connects
to the MCP WS Server (port 3001) on first use and reuses the connection.
Methods: send_navigation, send_highlight, send_chart, send_timeline.
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock


def _make_mock_ws():
    """Create a mock WebSocket object."""
    mock_ws = AsyncMock()
    mock_ws.send = AsyncMock()
    mock_ws.close = AsyncMock()
    return mock_ws


class TestUIBridgeInit:
    """Test UIBridge initialization and lazy connection."""

    def test_ui_bridge_can_be_instantiated(self):
        """UIBridge can be created without a connection being opened."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge()
        assert bridge is not None
        assert bridge._ws is None  # No connection until first use

    def test_ui_bridge_default_url(self):
        """UIBridge uses default WS URL ws://localhost:3001."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge()
        assert bridge._ws_url == "ws://localhost:3001"

    def test_ui_bridge_custom_url(self):
        """UIBridge accepts a custom WS URL."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge(ws_url="ws://custom:9999")
        assert bridge._ws_url == "ws://custom:9999"


class TestUIBridgeSendNavigation:
    """Test send_navigation method."""

    @pytest.mark.asyncio
    async def test_send_navigation_connects_lazily(self):
        """First call to send_navigation opens a WS connection."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge()
        mock_ws = _make_mock_ws()

        connect_mock = AsyncMock(return_value=mock_ws)
        with patch("src.services.ui_bridge.websockets_connect", connect_mock):
            await bridge.send_navigation("/siem")
            # Connection should be established
            assert bridge._ws is not None

    @pytest.mark.asyncio
    async def test_send_navigation_sends_correct_payload(self):
        """send_navigation sends MCP tool_call with navigate_to_page."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge()
        mock_ws = _make_mock_ws()

        connect_mock = AsyncMock(return_value=mock_ws)
        with patch("src.services.ui_bridge.websockets_connect", connect_mock):
            await bridge.send_navigation("/siem")

            mock_ws.send.assert_called_once()
            sent_data = json.loads(mock_ws.send.call_args[0][0])
            assert sent_data["type"] == "tool_call"
            assert sent_data["tool"] == "navigate_to_page"
            assert sent_data["params"]["page"] == "/siem"

    @pytest.mark.asyncio
    async def test_send_navigation_reuses_connection(self):
        """Subsequent calls reuse the same WS connection."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge()
        mock_ws = _make_mock_ws()

        connect_mock = AsyncMock(return_value=mock_ws)
        with patch("src.services.ui_bridge.websockets_connect", connect_mock):
            await bridge.send_navigation("/siem")
            await bridge.send_navigation("/edr")

            # Should only connect once
            assert connect_mock.await_count == 1
            # But send twice
            assert mock_ws.send.await_count == 2


class TestUIBridgeSendHighlight:
    """Test send_highlight method."""

    @pytest.mark.asyncio
    async def test_send_highlight_sends_correct_payload(self):
        """send_highlight sends MCP tool_call with highlight_assets."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge()
        mock_ws = _make_mock_ws()

        connect_mock = AsyncMock(return_value=mock_ws)
        with patch("src.services.ui_bridge.websockets_connect", connect_mock):
            assets = ["WS-FIN-042", "SRV-DEV-03"]
            await bridge.send_highlight(assets)

            sent_data = json.loads(mock_ws.send.call_args[0][0])
            assert sent_data["type"] == "tool_call"
            assert sent_data["tool"] == "highlight_assets"
            assert sent_data["params"]["assets"] == assets


class TestUIBridgeSendChart:
    """Test send_chart method."""

    @pytest.mark.asyncio
    async def test_send_chart_sends_correct_payload(self):
        """send_chart sends MCP tool_call with show_chart."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge()
        mock_ws = _make_mock_ws()

        connect_mock = AsyncMock(return_value=mock_ws)
        with patch("src.services.ui_bridge.websockets_connect", connect_mock):
            chart_data = {
                "type": "bar",
                "title": "Alert Distribution",
                "data": [{"label": "Critical", "value": 5}],
            }
            await bridge.send_chart(chart_data)

            sent_data = json.loads(mock_ws.send.call_args[0][0])
            assert sent_data["type"] == "tool_call"
            assert sent_data["tool"] == "show_chart"
            assert sent_data["params"]["chart_data"] == chart_data


class TestUIBridgeSendTimeline:
    """Test send_timeline method."""

    @pytest.mark.asyncio
    async def test_send_timeline_sends_correct_payload(self):
        """send_timeline sends MCP tool_call with show_timeline."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge()
        mock_ws = _make_mock_ws()

        connect_mock = AsyncMock(return_value=mock_ws)
        with patch("src.services.ui_bridge.websockets_connect", connect_mock):
            timeline_data = {
                "entries": [
                    {"time": "10:30", "event": "Initial Access detected"},
                    {"time": "10:35", "event": "Lateral movement observed"},
                ]
            }
            await bridge.send_timeline(timeline_data)

            sent_data = json.loads(mock_ws.send.call_args[0][0])
            assert sent_data["type"] == "tool_call"
            assert sent_data["tool"] == "show_timeline"
            assert sent_data["params"]["timeline_data"] == timeline_data


class TestUIBridgeDisconnect:
    """Test UIBridge disconnect/cleanup."""

    @pytest.mark.asyncio
    async def test_disconnect_closes_connection(self):
        """disconnect() closes the WebSocket connection."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge()
        mock_ws = _make_mock_ws()

        connect_mock = AsyncMock(return_value=mock_ws)
        with patch("src.services.ui_bridge.websockets_connect", connect_mock):
            await bridge.send_navigation("/siem")
            await bridge.disconnect()

            mock_ws.close.assert_called_once()
            assert bridge._ws is None

    @pytest.mark.asyncio
    async def test_disconnect_when_not_connected_is_noop(self):
        """disconnect() when not connected does nothing."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge()
        # Should not raise
        await bridge.disconnect()
        assert bridge._ws is None
