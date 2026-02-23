"""
aIP Assist API endpoints for real-time action streaming.

REQ-004-001-004: WebSocket /ws/aip-assist/actions para enviar stream de acciones

aIP = Artificial Intelligence Person

Provides:
- WebSocket endpoint for real-time action streaming
- Action context processing
- Suggestion delivery to connected clients
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
from datetime import datetime, timezone
import asyncio
import json

from ..services.aip_assist_service import get_aip_assist_service
from ..models.aip_assist import (
    AipActionContext,
    AipActionType,
    AipSessionState,
)

router = APIRouter(tags=["aip-assist"])


# Response Schemas
class SessionStateResponse(BaseModel):
    """Response schema for session state endpoint."""
    session_id: str
    accepted_suggestions: int
    rejected_suggestions: int
    total_actions: int
    acceptance_rate: float


class SuggestionFeedbackRequest(BaseModel):
    """Request schema for suggestion feedback."""
    suggestion_id: str = Field(..., description="Suggestion ID")
    accepted: bool = Field(..., description="Whether the suggestion was accepted")


# HTTP Endpoints
@router.get("/session/{session_id}/state", response_model=SessionStateResponse)
async def get_session_state(session_id: str):
    """
    Get the current state of an aIP Assist session.

    Returns statistics about actions and suggestion acceptance/rejection.
    """
    service = get_aip_assist_service()
    state = service.get_session_state(session_id)

    return SessionStateResponse(
        session_id=state.session_id,
        accepted_suggestions=state.accepted_suggestions,
        rejected_suggestions=state.rejected_suggestions,
        total_actions=state.total_actions,
        acceptance_rate=state.acceptance_rate,
    )


@router.post("/session/{session_id}/feedback")
async def submit_suggestion_feedback(
    session_id: str,
    request: SuggestionFeedbackRequest
):
    """
    Submit feedback on an aIP Assist suggestion.

    REQ-004-002-005: Tracking de aceptacion/rechazo por sesion
    """
    service = get_aip_assist_service()
    service.track_suggestion_response(
        session_id=session_id,
        suggestion_id=request.suggestion_id,
        accepted=request.accepted,
    )

    return {
        "status": "recorded",
        "suggestion_id": request.suggestion_id,
        "accepted": request.accepted,
    }


# WebSocket Endpoint
@router.websocket("/ws/{session_id}")
async def websocket_aip_assist_actions(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time aIP Assist action streaming.

    REQ-004-001-004: WebSocket /ws/aip-assist/actions para enviar stream

    Protocol:
    - Server sends: {"event": "connected", "session_id": "..."}
    - Client sends actions: {"type": "action", "action": "click", ...}
    - Server broadcasts actions and suggestions to all subscribers
    - Client can send: {"type": "ping"} -> Server responds: {"type": "pong"}
    - Client can send feedback: {"type": "feedback", "suggestion_id": "...", "accepted": true}

    Args:
        websocket: The WebSocket connection
        session_id: The session to connect to
    """
    await websocket.accept()

    service = get_aip_assist_service()
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
                    await _handle_websocket_message(service, session_id, message, websocket)

                except asyncio.TimeoutError:
                    pass

                # Check for outgoing messages (actions/suggestions from other sources)
                try:
                    outgoing = queue.get_nowait()
                    await websocket.send_json(outgoing)
                except asyncio.QueueEmpty:
                    pass

            except json.JSONDecodeError:
                # Invalid JSON, ignore
                pass
            except Exception as e:
                # Connection error or unexpected error
                if "disconnect" in str(e).lower():
                    break

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        await service.unsubscribe(session_id, queue)


async def _handle_websocket_message(
    service,
    session_id: str,
    message: dict,
    websocket: WebSocket
):
    """
    Handle incoming WebSocket messages.

    Args:
        service: The AipAssistService instance
        session_id: Current session ID
        message: The parsed message
        websocket: The WebSocket connection
    """
    msg_type = message.get("type")

    if msg_type == "ping":
        await websocket.send_json({"type": "pong"})

    elif msg_type == "action":
        # Process incoming action
        try:
            # Ensure session_id is set correctly
            message["session_id"] = session_id

            # Validate and create action context
            action = AipActionContext.model_validate(message)
            await service.process_action(action)

        except ValidationError:
            await websocket.send_json({
                "event": "error",
                "message": "Invalid action format",
            })

    elif msg_type == "feedback":
        # Process suggestion feedback
        suggestion_id = message.get("suggestion_id")
        accepted = message.get("accepted", False)

        if suggestion_id:
            service.track_suggestion_response(
                session_id=session_id,
                suggestion_id=suggestion_id,
                accepted=accepted,
            )
            await websocket.send_json({
                "event": "feedback_recorded",
                "suggestion_id": suggestion_id,
            })

    elif msg_type == "batch":
        # Process batch of actions
        actions = message.get("actions", [])
        for action_data in actions:
            try:
                action_data["session_id"] = session_id
                action = AipActionContext.model_validate(action_data)
                await service.process_action(action)
            except ValidationError:
                pass  # Skip invalid actions in batch
