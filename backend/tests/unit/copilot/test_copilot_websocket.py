"""
Unit tests for Copilot WebSocket endpoint.

REQ-004-001-004: WebSocket /ws/copilot/actions para enviar stream de acciones

Tests follow TDD methodology - written BEFORE implementation.
"""
import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone


class TestCopilotServiceExists:
    """Tests to verify CopilotService exists with correct structure."""

    def test_copilot_service_can_be_imported(self):
        """Test that CopilotService can be imported."""
        from src.services.copilot_service import CopilotService
        assert CopilotService is not None

    def test_get_copilot_service_can_be_imported(self):
        """Test that get_copilot_service singleton can be imported."""
        from src.services.copilot_service import get_copilot_service
        assert get_copilot_service is not None

    def test_copilot_service_has_subscribe_method(self):
        """Test that CopilotService has subscribe method."""
        from src.services.copilot_service import CopilotService
        assert hasattr(CopilotService, "subscribe")

    def test_copilot_service_has_unsubscribe_method(self):
        """Test that CopilotService has unsubscribe method."""
        from src.services.copilot_service import CopilotService
        assert hasattr(CopilotService, "unsubscribe")

    def test_copilot_service_has_process_action_method(self):
        """Test that CopilotService has process_action method."""
        from src.services.copilot_service import CopilotService
        assert hasattr(CopilotService, "process_action")


class TestCopilotServiceFunctionality:
    """Tests for CopilotService functionality."""

    def _run_async(self, coro):
        """Helper to run async code in tests."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def test_subscribe_returns_queue(self):
        """Test that subscribe returns an asyncio.Queue."""
        from src.services.copilot_service import CopilotService

        async def run_test():
            service = CopilotService()
            queue = await service.subscribe("test-session-001")
            return isinstance(queue, asyncio.Queue)

        assert self._run_async(run_test())

    def test_subscribe_creates_session_entry(self):
        """Test that subscribe creates session in internal tracking."""
        from src.services.copilot_service import CopilotService

        async def run_test():
            service = CopilotService()
            await service.subscribe("test-session-002")
            return "test-session-002" in service._sessions

        assert self._run_async(run_test())

    def test_multiple_subscribers_to_same_session(self):
        """Test that multiple clients can subscribe to same session."""
        from src.services.copilot_service import CopilotService

        async def run_test():
            service = CopilotService()
            queue1 = await service.subscribe("shared-session")
            queue2 = await service.subscribe("shared-session")
            return (
                queue1 is not queue2 and
                len(service._sessions.get("shared-session", [])) == 2
            )

        assert self._run_async(run_test())

    def test_unsubscribe_removes_queue(self):
        """Test that unsubscribe removes the queue from session."""
        from src.services.copilot_service import CopilotService

        async def run_test():
            service = CopilotService()
            queue = await service.subscribe("test-session-003")
            await service.unsubscribe("test-session-003", queue)
            queues = service._sessions.get("test-session-003", [])
            return queue not in queues

        assert self._run_async(run_test())

    def test_unsubscribe_cleans_up_empty_session(self):
        """Test that unsubscribe cleans up session when no subscribers remain."""
        from src.services.copilot_service import CopilotService

        async def run_test():
            service = CopilotService()
            queue = await service.subscribe("cleanup-session")
            await service.unsubscribe("cleanup-session", queue)
            return "cleanup-session" not in service._sessions

        assert self._run_async(run_test())

    def test_process_action_broadcasts_to_subscribers(self):
        """Test that process_action sends action to all subscribers."""
        from src.services.copilot_service import CopilotService
        from src.models.copilot import CopilotActionContext, CopilotActionType

        async def run_test():
            service = CopilotService()
            queue = await service.subscribe("broadcast-session")

            action = CopilotActionContext(
                action=CopilotActionType.CLICK,
                element="button",
                session_id="broadcast-session",
            )

            await service.process_action(action)
            received = queue.get_nowait()
            return received["action"] == "click" and received["element"] == "button"

        assert self._run_async(run_test())

    def test_process_action_updates_total_actions(self):
        """Test that process_action updates total actions count."""
        from src.services.copilot_service import CopilotService
        from src.models.copilot import CopilotActionContext, CopilotActionType

        async def run_test():
            service = CopilotService()
            await service.subscribe("action-count-session")

            action = CopilotActionContext(
                action=CopilotActionType.SELECT,
                element="alert-row",
                session_id="action-count-session",
            )

            await service.process_action(action)
            state = service.get_session_state("action-count-session")
            return state.total_actions == 1

        assert self._run_async(run_test())


class TestCopilotSessionState:
    """Tests for session state management."""

    def _run_async(self, coro):
        """Helper to run async code in tests."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def test_get_session_state_returns_state(self):
        """Test that get_session_state returns session state."""
        from src.services.copilot_service import CopilotService
        from src.models.copilot import CopilotSessionState

        async def run_test():
            service = CopilotService()
            await service.subscribe("state-session")
            state = service.get_session_state("state-session")
            return (
                isinstance(state, CopilotSessionState) and
                state.session_id == "state-session"
            )

        assert self._run_async(run_test())

    def test_track_suggestion_accepted(self):
        """Test tracking accepted suggestions."""
        from src.services.copilot_service import CopilotService

        async def run_test():
            service = CopilotService()
            await service.subscribe("tracking-session")

            service.track_suggestion_response(
                "tracking-session",
                suggestion_id="sug-001",
                accepted=True,
            )

            state = service.get_session_state("tracking-session")
            return state.accepted_suggestions == 1

        assert self._run_async(run_test())

    def test_track_suggestion_rejected(self):
        """Test tracking rejected suggestions."""
        from src.services.copilot_service import CopilotService

        async def run_test():
            service = CopilotService()
            await service.subscribe("reject-session")

            service.track_suggestion_response(
                "reject-session",
                suggestion_id="sug-001",
                accepted=False,
            )

            state = service.get_session_state("reject-session")
            return state.rejected_suggestions == 1

        assert self._run_async(run_test())


class TestCopilotWebSocketRouterExists:
    """Tests to verify copilot WebSocket router exists."""

    def test_copilot_router_can_be_imported(self):
        """Test that copilot router can be imported."""
        from src.api.copilot import router
        assert router is not None

    def test_copilot_router_has_websocket_endpoint(self):
        """Test that router has websocket endpoint defined."""
        from src.api.copilot import router

        # Check for WebSocket route
        ws_routes = [
            route for route in router.routes
            if hasattr(route, "path") and "ws" in route.path
        ]
        assert len(ws_routes) > 0

    def test_websocket_copilot_actions_function_exists(self):
        """Test that websocket_copilot_actions function exists."""
        from src.api.copilot import websocket_copilot_actions
        assert websocket_copilot_actions is not None
        assert callable(websocket_copilot_actions)


class TestCopilotWebSocketSuggestions:
    """Tests for suggestion broadcasting via WebSocket."""

    def _run_async(self, coro):
        """Helper to run async code in tests."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def test_broadcast_suggestion_to_session(self):
        """Test broadcasting a suggestion to session subscribers."""
        from src.services.copilot_service import CopilotService
        from src.models.copilot import CopilotSuggestionResponse

        async def run_test():
            service = CopilotService()
            queue = await service.subscribe("suggestion-session")

            suggestion = CopilotSuggestionResponse(
                suggestion_id="sug-001",
                content="Investigate related alerts",
                confidence=0.85,
                action_type="investigate",
            )

            await service.broadcast_suggestion("suggestion-session", suggestion)

            received = queue.get_nowait()
            return (
                received["event"] == "suggestion" and
                received["suggestion_id"] == "sug-001" and
                received["confidence"] == 0.85
            )

        assert self._run_async(run_test())


class TestCopilotAPIEndpoints:
    """Tests for HTTP API endpoints."""

    def test_session_state_response_model_exists(self):
        """Test that SessionStateResponse model exists."""
        from src.api.copilot import SessionStateResponse
        assert SessionStateResponse is not None

    def test_suggestion_feedback_request_model_exists(self):
        """Test that SuggestionFeedbackRequest model exists."""
        from src.api.copilot import SuggestionFeedbackRequest
        assert SuggestionFeedbackRequest is not None

    def test_get_session_state_endpoint_exists(self):
        """Test that get_session_state endpoint function exists."""
        from src.api.copilot import get_session_state
        assert get_session_state is not None
        assert callable(get_session_state)

    def test_submit_suggestion_feedback_endpoint_exists(self):
        """Test that submit_suggestion_feedback endpoint function exists."""
        from src.api.copilot import submit_suggestion_feedback
        assert submit_suggestion_feedback is not None
        assert callable(submit_suggestion_feedback)
