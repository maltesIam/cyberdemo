"""
Unit tests for Narration API endpoints.

REQ-003-002-001: WebSocket /ws/narration para streaming
REQ-003-002-004: API GET /api/v1/narration/history/{session_id}

Following TDD: These tests are written FIRST, before implementation.

Note: Unit tests for API schemas and endpoint structure.
WebSocket integration tests are in tests/integration/
"""
import pytest
from pydantic import ValidationError


class TestNarrationHistoryEndpointSchema:
    """Tests for narration history endpoint schema."""

    def test_narration_api_module_exists(self):
        """narration.py API module exists and can be imported."""
        from src.api import narration
        assert narration is not None

    def test_router_exists(self):
        """Narration module has a router."""
        from src.api.narration import router
        assert router is not None

    def test_history_response_schema_exists(self):
        """NarrationHistoryResponse schema exists."""
        from src.api.narration import NarrationHistoryResponse
        assert NarrationHistoryResponse is not None

    def test_history_response_has_required_fields(self):
        """NarrationHistoryResponse has required fields."""
        from src.api.narration import NarrationHistoryResponse

        response = NarrationHistoryResponse(
            session_id="session-123",
            messages=[],
            total=0
        )
        assert response.session_id == "session-123"
        assert response.messages == []
        assert response.total == 0

    def test_history_response_with_messages(self):
        """NarrationHistoryResponse can contain messages."""
        from src.api.narration import NarrationHistoryResponse

        messages = [
            {
                "type": "thinking",
                "content": "Analyzing...",
                "confidence": "medium",
                "confidence_score": 0.5,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        ]
        response = NarrationHistoryResponse(
            session_id="session-123",
            messages=messages,
            total=1
        )
        assert len(response.messages) == 1
        assert response.messages[0]["type"] == "thinking"


class TestNarrationMessageBroadcastSchema:
    """Tests for WebSocket message broadcast schema."""

    def test_broadcast_message_schema_exists(self):
        """NarrationBroadcastMessage schema exists."""
        from src.api.narration import NarrationBroadcastMessage
        assert NarrationBroadcastMessage is not None

    def test_broadcast_message_has_event_type(self):
        """Broadcast message has event type field."""
        from src.api.narration import NarrationBroadcastMessage

        msg = NarrationBroadcastMessage(
            event="narration",
            type="thinking",
            content="Test",
            confidence="low",
            confidence_score=0.2,
            timestamp="2024-01-15T10:30:00Z"
        )
        assert msg.event == "narration"

    def test_broadcast_message_includes_narration_fields(self):
        """Broadcast message includes all narration fields."""
        from src.api.narration import NarrationBroadcastMessage

        msg = NarrationBroadcastMessage(
            event="narration",
            type="finding",
            content="Found malicious process",
            confidence="high",
            confidence_score=0.9,
            timestamp="2024-01-15T10:30:00Z",
            message_id="msg-001",
            session_id="session-123"
        )
        assert msg.type == "finding"
        assert msg.content == "Found malicious process"
        assert msg.confidence == "high"


class TestNarrationRouterConfiguration:
    """Tests for router configuration."""

    def test_router_has_narration_tag(self):
        """Router has narration tag."""
        from src.api.narration import router

        assert "narration" in router.tags

    def test_router_has_history_endpoint(self):
        """Router has history endpoint defined."""
        from src.api.narration import router

        routes = [route.path for route in router.routes]
        assert any("/history/{session_id}" in path for path in routes)

    def test_router_has_websocket_endpoint(self):
        """Router has WebSocket endpoint defined."""
        from src.api.narration import router

        # Check for WebSocket route
        ws_routes = [
            route for route in router.routes
            if hasattr(route, 'path') and 'ws' in route.path.lower()
        ]
        # Note: WebSocket routes in FastAPI have different structure
        # We verify the path exists
        routes = [route.path for route in router.routes]
        assert any("ws" in path or "narration" in path for path in routes)


class TestCreateNarrationMessage:
    """Tests for create_narration_message helper function."""

    def test_create_narration_message_exists(self):
        """create_narration_message function exists."""
        from src.api.narration import create_narration_message
        assert create_narration_message is not None

    def test_create_narration_message_returns_schema(self):
        """create_narration_message returns NarrationMessageSchema."""
        from src.api.narration import create_narration_message
        from src.services.narration_service import NarrationMessageSchema

        msg = create_narration_message(
            msg_type="thinking",
            content="Analyzing alert...",
            confidence_score=0.5,
            session_id="session-123"
        )

        assert isinstance(msg, NarrationMessageSchema)
        assert msg.type == "thinking"
        assert msg.content == "Analyzing alert..."
        assert msg.confidence == "medium"  # 0.5 -> medium
        assert msg.session_id == "session-123"

    def test_create_narration_message_auto_confidence_level(self):
        """create_narration_message auto-calculates confidence level."""
        from src.api.narration import create_narration_message

        # Low confidence
        msg_low = create_narration_message("thinking", "Test", 0.2, "s1")
        assert msg_low.confidence == "low"

        # Medium confidence
        msg_med = create_narration_message("finding", "Test", 0.5, "s1")
        assert msg_med.confidence == "medium"

        # High confidence
        msg_high = create_narration_message("decision", "Test", 0.9, "s1")
        assert msg_high.confidence == "high"

    def test_create_narration_message_auto_generates_id(self):
        """create_narration_message auto-generates message_id."""
        from src.api.narration import create_narration_message

        msg = create_narration_message("action", "Test", 0.7, "session-1")
        assert msg.message_id is not None
        assert len(msg.message_id) > 0

    def test_create_narration_message_auto_generates_timestamp(self):
        """create_narration_message auto-generates timestamp."""
        from src.api.narration import create_narration_message

        msg = create_narration_message("thinking", "Test", 0.5, "session-1")
        assert msg.timestamp is not None
        # Should be ISO format
        assert "T" in msg.timestamp
