"""
Unit tests for UIBridge silent failure - UT-009
Requirement: REQ-001-002-003
Description: When WS Server is unavailable, UIBridge must silently fail -
no exceptions propagated, operations continue normally.

BR-006: Failed UI actions must not affect backend operation.
"""
import pytest
from unittest.mock import AsyncMock, patch


class TestUIBridgeSilentFailureOnConnect:
    """Test that UIBridge silently handles connection failures."""

    @pytest.mark.asyncio
    async def test_send_navigation_silent_on_connection_failure(self):
        """send_navigation does not raise when WS Server is down."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge(ws_url="ws://localhost:99999")

        connect_mock = AsyncMock(side_effect=ConnectionRefusedError("Connection refused"))
        with patch("src.services.ui_bridge.websockets_connect", connect_mock):
            # Should NOT raise - silently fails
            await bridge.send_navigation("/siem")

    @pytest.mark.asyncio
    async def test_send_highlight_silent_on_connection_failure(self):
        """send_highlight does not raise when WS Server is down."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge()

        connect_mock = AsyncMock(side_effect=OSError("Network unreachable"))
        with patch("src.services.ui_bridge.websockets_connect", connect_mock):
            await bridge.send_highlight(["ASSET-001"])

    @pytest.mark.asyncio
    async def test_send_chart_silent_on_connection_failure(self):
        """send_chart does not raise when WS Server is down."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge()

        connect_mock = AsyncMock(side_effect=TimeoutError("Connection timed out"))
        with patch("src.services.ui_bridge.websockets_connect", connect_mock):
            await bridge.send_chart({"type": "bar", "data": []})

    @pytest.mark.asyncio
    async def test_send_timeline_silent_on_connection_failure(self):
        """send_timeline does not raise when WS Server is down."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge()

        connect_mock = AsyncMock(side_effect=Exception("Unexpected error"))
        with patch("src.services.ui_bridge.websockets_connect", connect_mock):
            await bridge.send_timeline({"entries": []})


class TestUIBridgeSilentFailureOnSend:
    """Test that UIBridge silently handles send failures."""

    @pytest.mark.asyncio
    async def test_send_navigation_silent_on_send_failure(self):
        """send_navigation handles send() errors silently."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge()
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock(side_effect=ConnectionResetError("Connection reset"))

        connect_mock = AsyncMock(return_value=mock_ws)
        with patch("src.services.ui_bridge.websockets_connect", connect_mock):
            # Should NOT raise
            await bridge.send_navigation("/siem")

    @pytest.mark.asyncio
    async def test_connection_reset_after_send_failure(self):
        """After a send failure, the connection is reset so next call retries."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge()

        # First connection succeeds but send fails
        mock_ws_bad = AsyncMock()
        mock_ws_bad.send = AsyncMock(side_effect=ConnectionResetError("reset"))
        mock_ws_bad.close = AsyncMock()

        # Second connection succeeds
        mock_ws_good = AsyncMock()
        mock_ws_good.send = AsyncMock()

        connect_mock = AsyncMock(side_effect=[mock_ws_bad, mock_ws_good])
        with patch("src.services.ui_bridge.websockets_connect", connect_mock):
            await bridge.send_navigation("/siem")  # Fails silently
            await bridge.send_navigation("/edr")  # Should reconnect

            # Should have connected twice (retry after failure)
            assert connect_mock.await_count == 2
            # The second send should have succeeded
            mock_ws_good.send.assert_called_once()


class TestUIBridgeSilentFailureReturnValues:
    """Test that all methods return normally even on failure."""

    @pytest.mark.asyncio
    async def test_all_methods_return_none_on_failure(self):
        """All send methods return None regardless of failure."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge()

        connect_mock = AsyncMock(side_effect=ConnectionRefusedError())
        with patch("src.services.ui_bridge.websockets_connect", connect_mock):
            result1 = await bridge.send_navigation("/siem")
            result2 = await bridge.send_highlight(["ASSET-001"])
            result3 = await bridge.send_chart({"type": "bar"})
            result4 = await bridge.send_timeline({"entries": []})

            assert result1 is None
            assert result2 is None
            assert result3 is None
            assert result4 is None

    @pytest.mark.asyncio
    async def test_ws_stays_none_after_connection_failure(self):
        """After connection failure, _ws remains None."""
        from src.services.ui_bridge import UIBridge

        bridge = UIBridge()

        connect_mock = AsyncMock(side_effect=ConnectionRefusedError())
        with patch("src.services.ui_bridge.websockets_connect", connect_mock):
            await bridge.send_navigation("/siem")
            assert bridge._ws is None
