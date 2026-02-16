"""
Collaboration API endpoints for SOC team communication.

Provides REST endpoints for messages, channels, reactions, and WebSocket
for real-time updates.
"""

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import asyncio
import json

router = APIRouter(tags=["collaboration"])


# Pydantic models for API
class CreateMessageRequest(BaseModel):
    """Request to create a new message."""
    content: str = Field(..., min_length=1, max_length=5000)
    user: str = Field(default="soc-analyst")
    incident_id: Optional[str] = None
    channel_id: Optional[str] = None
    message_type: str = Field(default="text")
    attachments: Optional[List[dict]] = None
    thread_id: Optional[str] = None


class MessageResponse(BaseModel):
    """Response for a single message."""
    id: str
    channel_id: str
    incident_id: Optional[str]
    user: str
    content: str
    message_type: str
    mentions: dict
    attachments: list
    reactions: dict
    thread_id: Optional[str]
    is_edited: bool
    is_deleted: bool
    created_at: str
    updated_at: str


class MessageListResponse(BaseModel):
    """Response for listing messages."""
    data: List[dict]
    total: int
    has_more: bool


class CreateChannelRequest(BaseModel):
    """Request to create a new channel."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    incident_id: Optional[str] = None
    channel_type: str = Field(default="general")
    created_by: str = Field(default="system")


class ChannelResponse(BaseModel):
    """Response for a single channel."""
    id: str
    name: str
    description: Optional[str]
    incident_id: Optional[str]
    channel_type: str
    created_by: str
    created_at: str
    is_archived: bool


class AddReactionRequest(BaseModel):
    """Request to add a reaction."""
    emoji: str = Field(..., min_length=1, max_length=10)
    user: str = Field(default="soc-analyst")


class SearchRequest(BaseModel):
    """Request to search messages."""
    query: str = Field(..., min_length=1)
    incident_id: Optional[str] = None
    channel_id: Optional[str] = None
    user: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=200)


# Message endpoints
@router.post("/messages", response_model=MessageResponse)
async def create_message(request: CreateMessageRequest):
    """Create a new collaboration message."""
    from ..services.collab_service import get_collab_service

    service = get_collab_service()

    message = await service.create_message(
        content=request.content,
        user=request.user,
        channel_id=request.channel_id,
        incident_id=request.incident_id,
        message_type=request.message_type,
        attachments=request.attachments,
        thread_id=request.thread_id,
    )

    return message


@router.get("/messages", response_model=MessageListResponse)
async def list_messages(
    incident_id: Optional[str] = Query(None, description="Filter by incident ID"),
    channel_id: Optional[str] = Query(None, description="Filter by channel ID"),
    limit: int = Query(100, ge=1, le=500, description="Maximum messages to return"),
    before: Optional[str] = Query(None, description="Get messages before this timestamp"),
    after: Optional[str] = Query(None, description="Get messages after this timestamp"),
):
    """List collaboration messages with optional filters."""
    from ..services.collab_service import get_collab_service

    service = get_collab_service()

    messages = await service.list_messages(
        incident_id=incident_id,
        channel_id=channel_id,
        limit=limit + 1,  # Get one extra to check has_more
        before=before,
        after=after,
    )

    has_more = len(messages) > limit
    if has_more:
        messages = messages[:limit]

    return MessageListResponse(
        data=messages,
        total=len(messages),
        has_more=has_more,
    )


@router.get("/messages/{message_id}")
async def get_message(message_id: str):
    """Get a specific message by ID."""
    from ..services.collab_service import get_collab_service

    service = get_collab_service()
    message = await service.get_message(message_id)

    if not message:
        raise HTTPException(status_code=404, detail=f"Message {message_id} not found")

    return message


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    deleted_by: str = Query(default="soc-analyst", description="User deleting the message"),
):
    """Soft delete a message."""
    from ..services.collab_service import get_collab_service

    service = get_collab_service()
    deleted = await service.delete_message(message_id, deleted_by)

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Message {message_id} not found")

    return {"message_id": message_id, "deleted": True}


# Reaction endpoints
@router.post("/messages/{message_id}/reactions")
async def add_reaction(message_id: str, request: AddReactionRequest):
    """Add a reaction to a message."""
    from ..services.collab_service import get_collab_service

    service = get_collab_service()

    try:
        reactions = await service.add_reaction(
            message_id=message_id,
            emoji=request.emoji,
            user=request.user,
        )
        return {"message_id": message_id, "reactions": reactions}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/messages/{message_id}/reactions/{emoji}")
async def remove_reaction(
    message_id: str,
    emoji: str,
    user: str = Query(default="soc-analyst", description="User removing the reaction"),
):
    """Remove a reaction from a message."""
    from ..services.collab_service import get_collab_service

    service = get_collab_service()

    try:
        reactions = await service.remove_reaction(
            message_id=message_id,
            emoji=emoji,
            user=user,
        )
        return {"message_id": message_id, "reactions": reactions}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Channel endpoints
@router.get("/channels", response_model=List[ChannelResponse])
async def list_channels(
    incident_id: Optional[str] = Query(None, description="Filter by incident ID"),
    include_archived: bool = Query(False, description="Include archived channels"),
):
    """List collaboration channels."""
    from ..services.collab_service import get_collab_service

    service = get_collab_service()
    channels = await service.list_channels(
        incident_id=incident_id,
        include_archived=include_archived,
    )

    return channels


@router.post("/channels", response_model=ChannelResponse)
async def create_channel(request: CreateChannelRequest):
    """Create a new collaboration channel."""
    from ..services.collab_service import get_collab_service

    service = get_collab_service()
    channel = await service.create_channel(
        name=request.name,
        description=request.description,
        incident_id=request.incident_id,
        channel_type=request.channel_type,
        created_by=request.created_by,
    )

    return channel


@router.get("/channels/{channel_id}")
async def get_channel(channel_id: str):
    """Get a specific channel by ID."""
    from ..services.collab_service import get_collab_service

    service = get_collab_service()
    channel = await service.get_channel(channel_id)

    if not channel:
        raise HTTPException(status_code=404, detail=f"Channel {channel_id} not found")

    return channel


# Search endpoint
@router.post("/messages/search")
async def search_messages(request: SearchRequest):
    """Search messages by content."""
    from ..services.collab_service import get_collab_service

    service = get_collab_service()
    messages = await service.search_messages(
        query=request.query,
        incident_id=request.incident_id,
        channel_id=request.channel_id,
        user=request.user,
        limit=request.limit,
    )

    return {"query": request.query, "results": messages, "total": len(messages)}


# WebSocket endpoint for real-time updates
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time collaboration updates."""
    from ..services.collab_service import get_collab_service

    await websocket.accept()

    service = get_collab_service()
    subscribed_channels: dict[str, asyncio.Queue] = {}

    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

        while True:
            # Wait for client messages or channel events
            try:
                # Check for incoming messages with timeout
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=0.1,
                )
                message = json.loads(data)

                # Handle subscription requests
                if message.get("type") == "subscribe":
                    channel_id = message.get("channel_id", "general")
                    if channel_id not in subscribed_channels:
                        queue = await service.subscribe(channel_id)
                        subscribed_channels[channel_id] = queue
                        await websocket.send_json({
                            "type": "subscribed",
                            "channel_id": channel_id,
                        })

                elif message.get("type") == "unsubscribe":
                    channel_id = message.get("channel_id")
                    if channel_id in subscribed_channels:
                        await service.unsubscribe(channel_id, subscribed_channels[channel_id])
                        del subscribed_channels[channel_id]
                        await websocket.send_json({
                            "type": "unsubscribed",
                            "channel_id": channel_id,
                        })

                elif message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

            except asyncio.TimeoutError:
                pass

            # Check for events from subscribed channels
            for channel_id, queue in list(subscribed_channels.items()):
                try:
                    event = queue.get_nowait()
                    event["channel_id"] = channel_id
                    await websocket.send_json(event)
                except asyncio.QueueEmpty:
                    pass

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        # Cleanup subscriptions
        for channel_id, queue in subscribed_channels.items():
            await service.unsubscribe(channel_id, queue)


@router.websocket("/ws/{channel_id}")
async def websocket_channel_endpoint(websocket: WebSocket, channel_id: str):
    """WebSocket endpoint for a specific channel."""
    from ..services.collab_service import get_collab_service

    await websocket.accept()

    service = get_collab_service()
    queue = await service.subscribe(channel_id)

    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "channel_id": channel_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

        while True:
            try:
                # Wait for events with timeout
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                event["channel_id"] = channel_id
                await websocket.send_json(event)
            except asyncio.TimeoutError:
                # Send keepalive ping
                await websocket.send_json({"type": "ping"})

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        await service.unsubscribe(channel_id, queue)
