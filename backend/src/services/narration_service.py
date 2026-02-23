"""
Narration Service for real-time agent reasoning streaming.

REQ-003-002-001: WebSocket /ws/narration para streaming
REQ-003-002-002: Formato de mensaje {type, content, confidence, timestamp}
REQ-003-002-003: Buffer de ultimos 100 mensajes
REQ-003-002-004: API GET /api/v1/narration/history/{session_id}

Provides:
- Message format schema with validation
- Circular buffer for 100 messages per session
- Pub/sub mechanism for WebSocket streaming
- History retrieval for session replay
"""
from collections import deque
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
import asyncio
from datetime import datetime


# Message type literals
NarrationTypeValues = Literal["thinking", "finding", "decision", "action"]
ConfidenceLevelValues = Literal["low", "medium", "high"]


class NarrationMessageSchema(BaseModel):
    """Schema for narration messages (REQ-003-002-002).

    Format: {type, content, confidence, timestamp}
    """

    # Required fields
    type: NarrationTypeValues = Field(
        ...,
        description="Type of narration: thinking, finding, decision, or action"
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Content of the narration message"
    )
    confidence: ConfidenceLevelValues = Field(
        ...,
        description="Confidence level: low, medium, or high"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )
    timestamp: str = Field(
        ...,
        description="ISO 8601 timestamp when the message was generated"
    )

    # Optional metadata fields
    message_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the message"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session identifier for grouping messages"
    )
    agent_id: Optional[str] = Field(
        default=None,
        description="Agent that generated the message"
    )
    incident_id: Optional[str] = Field(
        default=None,
        description="Related incident ID if applicable"
    )

    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow additional fields


class NarrationBuffer:
    """Circular buffer for narration messages (REQ-003-002-003).

    Maintains the last N messages (default 100) per session.
    Oldest messages are automatically removed when buffer is full.
    """

    def __init__(self, max_size: int = 100):
        """Initialize buffer with max size.

        Args:
            max_size: Maximum number of messages to keep (default 100)
        """
        self.max_size = max_size
        self._messages: deque[NarrationMessageSchema] = deque(maxlen=max_size)

    def add(self, message: NarrationMessageSchema) -> None:
        """Add a message to the buffer.

        If buffer is full, oldest message is automatically removed.

        Args:
            message: The narration message to add
        """
        self._messages.append(message)

    def get_all(self) -> list[NarrationMessageSchema]:
        """Get all messages in the buffer.

        Returns:
            List of messages in chronological order (oldest first)
        """
        return list(self._messages)

    def clear(self) -> None:
        """Clear all messages from the buffer."""
        self._messages.clear()

    def __len__(self) -> int:
        """Return the number of messages in the buffer."""
        return len(self._messages)


class NarrationService:
    """Service for managing narration messages and subscriptions.

    Provides:
    - Per-session message buffering (100 messages)
    - Pub/sub for WebSocket streaming
    - History retrieval for session replay
    """

    def __init__(self):
        """Initialize the narration service."""
        # Session ID -> NarrationBuffer
        self._session_buffers: dict[str, NarrationBuffer] = {}
        # Session ID -> List of asyncio.Queue (subscribers)
        self._subscribers: dict[str, list[asyncio.Queue]] = {}

    def _get_or_create_buffer(self, session_id: str) -> NarrationBuffer:
        """Get or create buffer for session.

        Args:
            session_id: The session identifier

        Returns:
            NarrationBuffer for the session
        """
        if session_id not in self._session_buffers:
            self._session_buffers[session_id] = NarrationBuffer()
        return self._session_buffers[session_id]

    def publish(
        self,
        session_id: str,
        message: NarrationMessageSchema
    ) -> NarrationMessageSchema:
        """Publish a message to the session buffer (synchronous).

        Args:
            session_id: The session to publish to
            message: The narration message

        Returns:
            The published message
        """
        buffer = self._get_or_create_buffer(session_id)
        buffer.add(message)
        return message

    async def publish_async(
        self,
        session_id: str,
        message: NarrationMessageSchema
    ) -> NarrationMessageSchema:
        """Publish a message and notify subscribers (async).

        Args:
            session_id: The session to publish to
            message: The narration message

        Returns:
            The published message
        """
        # Add to buffer
        self.publish(session_id, message)

        # Notify all subscribers for this session
        if session_id in self._subscribers:
            message_dict = message.model_dump()
            for queue in self._subscribers[session_id]:
                try:
                    queue.put_nowait(message_dict)
                except asyncio.QueueFull:
                    # Skip if queue is full (slow consumer)
                    pass

        return message

    async def subscribe(self, session_id: str) -> asyncio.Queue:
        """Subscribe to narration messages for a session.

        Args:
            session_id: The session to subscribe to

        Returns:
            asyncio.Queue that will receive messages
        """
        queue: asyncio.Queue = asyncio.Queue()

        if session_id not in self._subscribers:
            self._subscribers[session_id] = []
        self._subscribers[session_id].append(queue)

        return queue

    async def unsubscribe(self, session_id: str, queue: asyncio.Queue) -> None:
        """Unsubscribe from narration messages.

        Args:
            session_id: The session to unsubscribe from
            queue: The queue to remove
        """
        if session_id in self._subscribers:
            if queue in self._subscribers[session_id]:
                self._subscribers[session_id].remove(queue)

    def get_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> list[dict]:
        """Get message history for a session (REQ-003-002-004).

        Args:
            session_id: The session to get history for
            limit: Optional limit on number of messages (returns most recent)

        Returns:
            List of message dicts in chronological order
        """
        if session_id not in self._session_buffers:
            return []

        buffer = self._session_buffers[session_id]
        messages = buffer.get_all()

        # Convert to dicts
        result = [msg.model_dump() for msg in messages]

        # Apply limit (return most recent)
        if limit is not None and limit < len(result):
            result = result[-limit:]

        return result


# Singleton instance
_narration_service: Optional[NarrationService] = None


def get_narration_service() -> NarrationService:
    """Get the singleton NarrationService instance.

    Returns:
        The global NarrationService instance
    """
    global _narration_service
    if _narration_service is None:
        _narration_service = NarrationService()
    return _narration_service
