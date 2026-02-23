"""
Narration API endpoints for real-time agent reasoning.

REQ-003-002-001: WebSocket /ws/narration para streaming
REQ-003-002-004: API GET /api/v1/narration/history/{session_id}

Provides:
- WebSocket endpoint for real-time narration streaming
- HTTP endpoint for retrieving narration history
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime, timezone
import asyncio
import json
from uuid import uuid4

from ..services.narration_service import (
    get_narration_service,
    NarrationMessageSchema,
)
from ..models.narration import confidence_from_score, ConfidenceLevel

router = APIRouter(tags=["narration"])


# Response Schemas
class NarrationHistoryResponse(BaseModel):
    """Response schema for narration history endpoint."""

    session_id: str = Field(..., description="Session identifier")
    messages: list[dict] = Field(
        default_factory=list,
        description="List of narration messages"
    )
    total: int = Field(..., description="Total number of messages returned")


class NarrationBroadcastMessage(BaseModel):
    """Schema for WebSocket broadcast messages."""

    event: str = Field(
        default="narration",
        description="Event type for WebSocket message"
    )
    type: Literal["thinking", "finding", "decision", "action"] = Field(
        ..., description="Type of narration message"
    )
    content: str = Field(..., description="Narration content")
    confidence: Literal["low", "medium", "high"] = Field(
        ..., description="Confidence level"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score"
    )
    timestamp: str = Field(..., description="ISO timestamp")
    message_id: Optional[str] = Field(None, description="Message identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")


def create_narration_message(
    msg_type: str,
    content: str,
    confidence_score: float,
    session_id: str,
    message_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    incident_id: Optional[str] = None,
) -> NarrationMessageSchema:
    """Create a narration message with auto-generated fields.

    Args:
        msg_type: Type of message (thinking, finding, decision, action)
        content: Message content
        confidence_score: Confidence score 0.0-1.0
        session_id: Session identifier
        message_id: Optional message ID (auto-generated if not provided)
        agent_id: Optional agent identifier
        incident_id: Optional incident identifier

    Returns:
        NarrationMessageSchema with all fields populated
    """
    # Auto-generate message ID if not provided
    if message_id is None:
        message_id = str(uuid4())

    # Calculate confidence level from score
    confidence_level = confidence_from_score(confidence_score)

    # Generate timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    return NarrationMessageSchema(
        type=msg_type,
        content=content,
        confidence=confidence_level.value,
        confidence_score=confidence_score,
        timestamp=timestamp,
        message_id=message_id,
        session_id=session_id,
        agent_id=agent_id,
        incident_id=incident_id,
    )


# HTTP Endpoints
@router.get("/history/{session_id}", response_model=NarrationHistoryResponse)
async def get_narration_history(
    session_id: str,
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of messages to return"
    ),
):
    """Get narration history for a session (REQ-003-002-004).

    Returns the most recent narration messages for the specified session,
    up to the specified limit. Messages are ordered chronologically.
    """
    service = get_narration_service()
    messages = service.get_history(session_id, limit=limit)

    return NarrationHistoryResponse(
        session_id=session_id,
        messages=messages,
        total=len(messages),
    )


# WebSocket Endpoint
@router.websocket("/ws/{session_id}")
async def websocket_narration(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time narration streaming (REQ-003-002-001).

    Clients connect to receive real-time narration messages for a session.
    Messages are broadcast to all connected clients for the same session.

    Protocol:
    - Server sends: {"event": "connected", "session_id": "..."}
    - Server sends narration: {"event": "narration", "type": "...", ...}
    - Client can send: {"type": "ping"} -> Server responds: {"type": "pong"}
    """
    await websocket.accept()

    service = get_narration_service()
    queue = await service.subscribe(session_id)

    try:
        # Send connection confirmation
        await websocket.send_json({
            "event": "connected",
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        while True:
            try:
                # Check for incoming messages with timeout
                try:
                    data = await asyncio.wait_for(
                        websocket.receive_text(),
                        timeout=0.1,
                    )
                    message = json.loads(data)

                    # Handle ping
                    if message.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})

                except asyncio.TimeoutError:
                    pass

                # Check for narration messages
                try:
                    msg = queue.get_nowait()
                    msg["event"] = "narration"
                    await websocket.send_json(msg)
                except asyncio.QueueEmpty:
                    pass

            except Exception:
                # Connection error or client disconnect
                break

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        await service.unsubscribe(session_id, queue)
