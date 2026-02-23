"""
Unit tests for NarrationService.

REQ-003-002-001: WebSocket /ws/narration para streaming
REQ-003-002-002: Formato de mensaje {type, content, confidence, timestamp}
REQ-003-002-003: Buffer de ultimos 100 mensajes

Following TDD: These tests are written FIRST, before implementation.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
import asyncio

# Configure anyio to use asyncio only (trio not installed)
@pytest.fixture
def anyio_backend():
    return 'asyncio'


class TestNarrationMessageSchema:
    """Tests for NarrationMessageSchema Pydantic model (REQ-003-002-002)."""

    def test_schema_import(self):
        """NarrationMessageSchema can be imported."""
        from src.services.narration_service import NarrationMessageSchema
        assert NarrationMessageSchema is not None

    def test_schema_required_fields(self):
        """Schema requires type, content, confidence, timestamp."""
        from src.services.narration_service import NarrationMessageSchema

        # Valid message should work
        msg = NarrationMessageSchema(
            type="thinking",
            content="Analyzing the alert...",
            confidence="medium",
            confidence_score=0.55,
            timestamp="2024-01-15T10:30:00Z"
        )
        assert msg.type == "thinking"
        assert msg.content == "Analyzing the alert..."
        assert msg.confidence == "medium"
        assert msg.confidence_score == 0.55

    def test_schema_validates_type_values(self):
        """Schema validates message type values."""
        from src.services.narration_service import NarrationMessageSchema
        from pydantic import ValidationError

        # Valid types
        for t in ["thinking", "finding", "decision", "action"]:
            msg = NarrationMessageSchema(
                type=t,
                content="test",
                confidence="low",
                confidence_score=0.1,
                timestamp="2024-01-15T10:30:00Z"
            )
            assert msg.type == t

        # Invalid type
        with pytest.raises(ValidationError):
            NarrationMessageSchema(
                type="invalid_type",
                content="test",
                confidence="low",
                confidence_score=0.1,
                timestamp="2024-01-15T10:30:00Z"
            )

    def test_schema_validates_confidence_values(self):
        """Schema validates confidence level values."""
        from src.services.narration_service import NarrationMessageSchema
        from pydantic import ValidationError

        # Valid confidence levels
        for c in ["low", "medium", "high"]:
            msg = NarrationMessageSchema(
                type="thinking",
                content="test",
                confidence=c,
                confidence_score=0.5,
                timestamp="2024-01-15T10:30:00Z"
            )
            assert msg.confidence == c

        # Invalid confidence
        with pytest.raises(ValidationError):
            NarrationMessageSchema(
                type="thinking",
                content="test",
                confidence="invalid_confidence",
                confidence_score=0.5,
                timestamp="2024-01-15T10:30:00Z"
            )

    def test_schema_has_optional_fields(self):
        """Schema has optional fields for metadata."""
        from src.services.narration_service import NarrationMessageSchema

        msg = NarrationMessageSchema(
            type="finding",
            content="Found malicious process",
            confidence="high",
            confidence_score=0.85,
            timestamp="2024-01-15T10:30:00Z",
            message_id="msg-123",
            session_id="session-456",
            agent_id="agent-001",
            incident_id="INC-789"
        )
        assert msg.message_id == "msg-123"
        assert msg.session_id == "session-456"
        assert msg.agent_id == "agent-001"
        assert msg.incident_id == "INC-789"

    def test_schema_to_dict(self):
        """Schema can be converted to dict for JSON serialization."""
        from src.services.narration_service import NarrationMessageSchema

        msg = NarrationMessageSchema(
            type="decision",
            content="Recommend containment",
            confidence="high",
            confidence_score=0.9,
            timestamp="2024-01-15T10:30:00Z"
        )
        data = msg.model_dump()
        assert isinstance(data, dict)
        assert data["type"] == "decision"
        assert data["content"] == "Recommend containment"


class TestNarrationBuffer:
    """Tests for NarrationBuffer - 100 message circular buffer (REQ-003-002-003)."""

    def test_buffer_import(self):
        """NarrationBuffer can be imported."""
        from src.services.narration_service import NarrationBuffer
        assert NarrationBuffer is not None

    def test_buffer_default_max_size(self):
        """Buffer has default max size of 100."""
        from src.services.narration_service import NarrationBuffer

        buffer = NarrationBuffer()
        assert buffer.max_size == 100

    def test_buffer_custom_max_size(self):
        """Buffer accepts custom max size."""
        from src.services.narration_service import NarrationBuffer

        buffer = NarrationBuffer(max_size=50)
        assert buffer.max_size == 50

    def test_buffer_add_message(self):
        """Buffer can add messages."""
        from src.services.narration_service import NarrationBuffer, NarrationMessageSchema

        buffer = NarrationBuffer()
        msg = NarrationMessageSchema(
            type="thinking",
            content="Test message",
            confidence="low",
            confidence_score=0.2,
            timestamp="2024-01-15T10:30:00Z"
        )
        buffer.add(msg)
        assert len(buffer) == 1

    def test_buffer_get_all_messages(self):
        """Buffer returns all messages in order."""
        from src.services.narration_service import NarrationBuffer, NarrationMessageSchema

        buffer = NarrationBuffer()
        for i in range(5):
            msg = NarrationMessageSchema(
                type="finding",
                content=f"Message {i}",
                confidence="medium",
                confidence_score=0.5,
                timestamp=f"2024-01-15T10:30:0{i}Z"
            )
            buffer.add(msg)

        messages = buffer.get_all()
        assert len(messages) == 5
        assert messages[0].content == "Message 0"
        assert messages[4].content == "Message 4"

    def test_buffer_enforces_max_size(self):
        """Buffer removes oldest messages when max size exceeded."""
        from src.services.narration_service import NarrationBuffer, NarrationMessageSchema

        buffer = NarrationBuffer(max_size=3)
        for i in range(5):
            msg = NarrationMessageSchema(
                type="action",
                content=f"Message {i}",
                confidence="high",
                confidence_score=0.8,
                timestamp=f"2024-01-15T10:30:0{i}Z"
            )
            buffer.add(msg)

        messages = buffer.get_all()
        assert len(messages) == 3
        # Should have messages 2, 3, 4 (oldest 0, 1 removed)
        assert messages[0].content == "Message 2"
        assert messages[1].content == "Message 3"
        assert messages[2].content == "Message 4"

    def test_buffer_clear(self):
        """Buffer can be cleared."""
        from src.services.narration_service import NarrationBuffer, NarrationMessageSchema

        buffer = NarrationBuffer()
        msg = NarrationMessageSchema(
            type="thinking",
            content="Test",
            confidence="low",
            confidence_score=0.1,
            timestamp="2024-01-15T10:30:00Z"
        )
        buffer.add(msg)
        buffer.clear()
        assert len(buffer) == 0

    def test_buffer_100_messages(self):
        """Buffer correctly maintains 100 messages."""
        from src.services.narration_service import NarrationBuffer, NarrationMessageSchema

        buffer = NarrationBuffer()  # Default 100

        # Add 150 messages
        for i in range(150):
            msg = NarrationMessageSchema(
                type="thinking",
                content=f"Message {i}",
                confidence="medium",
                confidence_score=0.5,
                timestamp="2024-01-15T10:30:00Z"
            )
            buffer.add(msg)

        messages = buffer.get_all()
        assert len(messages) == 100
        # Should have messages 50-149 (oldest 0-49 removed)
        assert messages[0].content == "Message 50"
        assert messages[99].content == "Message 149"


class TestNarrationService:
    """Tests for NarrationService main class."""

    def test_service_import(self):
        """NarrationService can be imported."""
        from src.services.narration_service import NarrationService
        assert NarrationService is not None

    def test_service_create_instance(self):
        """NarrationService can be instantiated."""
        from src.services.narration_service import NarrationService

        service = NarrationService()
        assert service is not None

    def test_service_has_session_buffers(self):
        """Service maintains buffers per session."""
        from src.services.narration_service import NarrationService

        service = NarrationService()
        # Should have dict for session buffers
        assert hasattr(service, '_session_buffers')
        assert isinstance(service._session_buffers, dict)

    def test_service_has_subscribers(self):
        """Service maintains WebSocket subscribers per session."""
        from src.services.narration_service import NarrationService

        service = NarrationService()
        assert hasattr(service, '_subscribers')
        assert isinstance(service._subscribers, dict)


class TestNarrationServicePublish:
    """Tests for NarrationService.publish method."""

    @pytest.fixture
    def service(self):
        from src.services.narration_service import NarrationService
        return NarrationService()

    def test_publish_creates_session_buffer(self, service):
        """Publishing to new session creates buffer."""
        from src.services.narration_service import NarrationMessageSchema

        msg = NarrationMessageSchema(
            type="thinking",
            content="Test",
            confidence="low",
            confidence_score=0.1,
            timestamp="2024-01-15T10:30:00Z",
            session_id="session-new"
        )
        service.publish("session-new", msg)

        assert "session-new" in service._session_buffers
        assert len(service._session_buffers["session-new"]) == 1

    def test_publish_adds_to_existing_buffer(self, service):
        """Publishing to existing session adds to buffer."""
        from src.services.narration_service import NarrationMessageSchema

        for i in range(3):
            msg = NarrationMessageSchema(
                type="finding",
                content=f"Message {i}",
                confidence="medium",
                confidence_score=0.5,
                timestamp="2024-01-15T10:30:00Z",
                session_id="session-123"
            )
            service.publish("session-123", msg)

        assert len(service._session_buffers["session-123"]) == 3

    def test_publish_returns_message(self, service):
        """Publish returns the message that was added."""
        from src.services.narration_service import NarrationMessageSchema

        msg = NarrationMessageSchema(
            type="decision",
            content="Test decision",
            confidence="high",
            confidence_score=0.9,
            timestamp="2024-01-15T10:30:00Z",
            session_id="session-123"
        )
        result = service.publish("session-123", msg)

        assert result == msg


class TestNarrationServiceSubscription:
    """Tests for NarrationService subscription management."""

    @pytest.fixture
    def service(self):
        from src.services.narration_service import NarrationService
        return NarrationService()

    @pytest.mark.anyio
    async def test_subscribe_returns_queue(self, service):
        """Subscribe returns an asyncio Queue."""
        queue = await service.subscribe("session-123")

        assert isinstance(queue, asyncio.Queue)

    @pytest.mark.anyio
    async def test_subscribe_registers_subscriber(self, service):
        """Subscribe registers the queue in subscribers."""
        queue = await service.subscribe("session-123")

        assert "session-123" in service._subscribers
        assert queue in service._subscribers["session-123"]

    @pytest.mark.anyio
    async def test_unsubscribe_removes_subscriber(self, service):
        """Unsubscribe removes the queue from subscribers."""
        queue = await service.subscribe("session-123")
        await service.unsubscribe("session-123", queue)

        assert queue not in service._subscribers.get("session-123", [])

    @pytest.mark.anyio
    async def test_multiple_subscribers_same_session(self, service):
        """Multiple subscribers can listen to same session."""
        queue1 = await service.subscribe("session-123")
        queue2 = await service.subscribe("session-123")

        assert len(service._subscribers["session-123"]) == 2
        assert queue1 in service._subscribers["session-123"]
        assert queue2 in service._subscribers["session-123"]


class TestNarrationServiceBroadcast:
    """Tests for broadcasting messages to subscribers."""

    @pytest.fixture
    def service(self):
        from src.services.narration_service import NarrationService
        return NarrationService()

    @pytest.mark.anyio
    async def test_publish_notifies_subscribers(self, service):
        """Publishing notifies all session subscribers."""
        from src.services.narration_service import NarrationMessageSchema

        queue1 = await service.subscribe("session-123")
        queue2 = await service.subscribe("session-123")

        msg = NarrationMessageSchema(
            type="thinking",
            content="Test broadcast",
            confidence="medium",
            confidence_score=0.5,
            timestamp="2024-01-15T10:30:00Z",
            session_id="session-123"
        )

        # Use async publish that notifies subscribers
        await service.publish_async("session-123", msg)

        # Both queues should have the message
        received1 = queue1.get_nowait()
        received2 = queue2.get_nowait()

        assert received1["content"] == "Test broadcast"
        assert received2["content"] == "Test broadcast"

    @pytest.mark.anyio
    async def test_publish_does_not_notify_other_sessions(self, service):
        """Publishing to one session does not notify other sessions."""
        from src.services.narration_service import NarrationMessageSchema

        queue1 = await service.subscribe("session-111")
        queue2 = await service.subscribe("session-222")

        msg = NarrationMessageSchema(
            type="finding",
            content="Session 111 only",
            confidence="high",
            confidence_score=0.9,
            timestamp="2024-01-15T10:30:00Z",
            session_id="session-111"
        )

        await service.publish_async("session-111", msg)

        # Queue1 should have message
        assert not queue1.empty()
        # Queue2 should be empty
        assert queue2.empty()


class TestNarrationServiceHistory:
    """Tests for getting session history (REQ-003-002-004)."""

    @pytest.fixture
    def service(self):
        from src.services.narration_service import NarrationService
        return NarrationService()

    def test_get_history_empty_session(self, service):
        """Getting history for non-existent session returns empty list."""
        history = service.get_history("non-existent-session")
        assert history == []

    def test_get_history_returns_all_messages(self, service):
        """Getting history returns all buffered messages."""
        from src.services.narration_service import NarrationMessageSchema

        for i in range(5):
            msg = NarrationMessageSchema(
                type="thinking",
                content=f"Message {i}",
                confidence="low",
                confidence_score=0.2,
                timestamp="2024-01-15T10:30:00Z",
                session_id="session-123"
            )
            service.publish("session-123", msg)

        history = service.get_history("session-123")
        assert len(history) == 5

    def test_get_history_with_limit(self, service):
        """Getting history respects limit parameter."""
        from src.services.narration_service import NarrationMessageSchema

        for i in range(10):
            msg = NarrationMessageSchema(
                type="finding",
                content=f"Message {i}",
                confidence="medium",
                confidence_score=0.5,
                timestamp="2024-01-15T10:30:00Z",
                session_id="session-123"
            )
            service.publish("session-123", msg)

        history = service.get_history("session-123", limit=3)
        assert len(history) == 3
        # Should return the 3 most recent
        assert history[0]["content"] == "Message 7"
        assert history[2]["content"] == "Message 9"

    def test_get_history_returns_dicts(self, service):
        """Getting history returns list of dicts (for JSON serialization)."""
        from src.services.narration_service import NarrationMessageSchema

        msg = NarrationMessageSchema(
            type="decision",
            content="Test decision",
            confidence="high",
            confidence_score=0.9,
            timestamp="2024-01-15T10:30:00Z",
            session_id="session-123"
        )
        service.publish("session-123", msg)

        history = service.get_history("session-123")
        assert isinstance(history, list)
        assert isinstance(history[0], dict)
        assert history[0]["type"] == "decision"


class TestGetNarrationService:
    """Tests for singleton service accessor."""

    def test_get_narration_service_import(self):
        """get_narration_service can be imported."""
        from src.services.narration_service import get_narration_service
        assert get_narration_service is not None

    def test_get_narration_service_returns_service(self):
        """get_narration_service returns NarrationService instance."""
        from src.services.narration_service import get_narration_service, NarrationService

        service = get_narration_service()
        assert isinstance(service, NarrationService)

    def test_get_narration_service_returns_same_instance(self):
        """get_narration_service returns same instance (singleton)."""
        from src.services.narration_service import get_narration_service

        service1 = get_narration_service()
        service2 = get_narration_service()
        assert service1 is service2
