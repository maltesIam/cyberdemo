"""
Unit tests for REST endpoint /api/v1/ui/action - UT-008
Requirement: REQ-001-002-002
Description: POST request with action payload returns 200 and forwards command to WS Server.

This endpoint receives UI commands and forwards them via UIBridge to the WS Server.
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock


class TestUIActionEndpointSchema:
    """Test request/response schema validation."""

    def test_ui_action_request_model_exists(self):
        """UIActionRequest Pydantic model is defined."""
        from src.api.ui_actions import UIActionRequest

        req = UIActionRequest(
            action="navigate",
            params={"page": "/siem"},
        )
        assert req.action == "navigate"
        assert req.params == {"page": "/siem"}

    def test_ui_action_request_requires_action(self):
        """UIActionRequest requires the 'action' field."""
        from src.api.ui_actions import UIActionRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            UIActionRequest(params={"page": "/siem"})

    def test_ui_action_request_requires_params(self):
        """UIActionRequest requires the 'params' field."""
        from src.api.ui_actions import UIActionRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            UIActionRequest(action="navigate")

    def test_valid_actions(self):
        """Only valid actions are accepted: navigate, highlight, chart, timeline."""
        from src.api.ui_actions import VALID_UI_ACTIONS

        assert "navigate" in VALID_UI_ACTIONS
        assert "highlight" in VALID_UI_ACTIONS
        assert "chart" in VALID_UI_ACTIONS
        assert "timeline" in VALID_UI_ACTIONS


class TestUIActionEndpointBehavior:
    """Test endpoint behavior using direct function calls with mocked dependencies."""

    @pytest.mark.asyncio
    async def test_navigate_action_calls_send_navigation(self):
        """POST with action='navigate' calls UIBridge.send_navigation."""
        from src.api.ui_actions import UIActionRequest, handle_ui_action

        mock_bridge = AsyncMock()
        mock_bridge.send_navigation = AsyncMock()

        request = UIActionRequest(
            action="navigate",
            params={"page": "/siem"},
        )
        result = await handle_ui_action(request, ui_bridge=mock_bridge)

        mock_bridge.send_navigation.assert_called_once_with("/siem")
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_highlight_action_calls_send_highlight(self):
        """POST with action='highlight' calls UIBridge.send_highlight."""
        from src.api.ui_actions import UIActionRequest, handle_ui_action

        mock_bridge = AsyncMock()
        mock_bridge.send_highlight = AsyncMock()

        request = UIActionRequest(
            action="highlight",
            params={"assets": ["WS-FIN-042", "SRV-DEV-03"]},
        )
        result = await handle_ui_action(request, ui_bridge=mock_bridge)

        mock_bridge.send_highlight.assert_called_once_with(["WS-FIN-042", "SRV-DEV-03"])
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_chart_action_calls_send_chart(self):
        """POST with action='chart' calls UIBridge.send_chart."""
        from src.api.ui_actions import UIActionRequest, handle_ui_action

        mock_bridge = AsyncMock()
        mock_bridge.send_chart = AsyncMock()

        chart_data = {"type": "bar", "title": "Alerts", "data": []}
        request = UIActionRequest(
            action="chart",
            params={"chart_data": chart_data},
        )
        result = await handle_ui_action(request, ui_bridge=mock_bridge)

        mock_bridge.send_chart.assert_called_once_with(chart_data)
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_timeline_action_calls_send_timeline(self):
        """POST with action='timeline' calls UIBridge.send_timeline."""
        from src.api.ui_actions import UIActionRequest, handle_ui_action

        mock_bridge = AsyncMock()
        mock_bridge.send_timeline = AsyncMock()

        timeline_data = {"entries": [{"time": "10:30", "event": "Detection"}]}
        request = UIActionRequest(
            action="timeline",
            params={"timeline_data": timeline_data},
        )
        result = await handle_ui_action(request, ui_bridge=mock_bridge)

        mock_bridge.send_timeline.assert_called_once_with(timeline_data)
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_invalid_action_returns_error(self):
        """POST with unknown action returns error response."""
        from src.api.ui_actions import UIActionRequest, handle_ui_action

        mock_bridge = AsyncMock()

        request = UIActionRequest(
            action="invalid_action",
            params={"something": "value"},
        )
        result = await handle_ui_action(request, ui_bridge=mock_bridge)

        assert result["status"] == "error"
        assert "unknown action" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_router_exists_with_correct_prefix(self):
        """The router is defined and can be included in the app."""
        from src.api.ui_actions import router

        assert router is not None
        # Check that a POST route exists
        routes = [r for r in router.routes if hasattr(r, "methods")]
        post_routes = [r for r in routes if "POST" in r.methods]
        assert len(post_routes) >= 1
