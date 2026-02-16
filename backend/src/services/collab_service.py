"""
Collaboration Service for SOC team communication.

Provides message management, mention parsing, and WebSocket broadcasting
for real-time collaboration during incident response.
"""

from typing import Optional, List, Dict, Any, Set
from datetime import datetime
import uuid
import re
import asyncio


# Mention patterns
# Asset pattern matches: @ASSET-123, @HOST-PROD-01, @DEV-001 (uppercase with hyphen)
ASSET_MENTION_PATTERN = re.compile(r'@([A-Z]+-[A-Z0-9-]+)')
# User pattern matches: @john, @analyst1 (lowercase usernames)
USER_MENTION_PATTERN = re.compile(r'@([a-z][a-z0-9_]*)', re.IGNORECASE)


class CollabService:
    """Service for collaboration channel operations."""

    def __init__(self, opensearch_client=None):
        """Initialize collaboration service.

        Args:
            opensearch_client: Optional OpenSearch client for persistence
        """
        self.os_client = opensearch_client
        self._messages: Dict[str, Dict[str, Any]] = {}
        self._channels: Dict[str, Dict[str, Any]] = {}
        self._reactions: Dict[str, Dict[str, List[str]]] = {}  # message_id -> {emoji: [users]}
        self._subscribers: Dict[str, Set[asyncio.Queue]] = {}  # channel_id -> set of queues

        # Initialize default general channel
        self._ensure_default_channel()

    def _ensure_default_channel(self):
        """Ensure default general channel exists."""
        if "general" not in self._channels:
            self._channels["general"] = {
                "id": "general",
                "name": "General",
                "description": "General SOC team discussions",
                "incident_id": None,
                "channel_type": "general",
                "created_by": "system",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "is_archived": False,
            }

    def parse_mentions(self, content: str) -> Dict[str, List[str]]:
        """Parse @mentions from message content.

        Args:
            content: Message content to parse

        Returns:
            Dict with 'users' and 'assets' mention lists
        """
        # Find assets first (uppercase with hyphens like ASSET-123, HOST-PROD-01)
        assets = ASSET_MENTION_PATTERN.findall(content)
        asset_set = set(assets)

        # Find users (lowercase usernames)
        users = USER_MENTION_PATTERN.findall(content)

        # Filter out asset patterns from user mentions
        # Also filter users that look like asset prefixes (all uppercase)
        users = [
            u for u in users
            if u not in asset_set and not u.isupper()
        ]

        return {
            "users": list(set(users)),
            "assets": list(set(assets)),
        }

    async def create_channel(
        self,
        name: str,
        incident_id: Optional[str] = None,
        description: Optional[str] = None,
        channel_type: str = "incident",
        created_by: str = "system",
    ) -> Dict[str, Any]:
        """Create a new collaboration channel.

        Args:
            name: Channel name
            incident_id: Optional associated incident ID
            description: Optional channel description
            channel_type: Type of channel (incident, general, team)
            created_by: User who created the channel

        Returns:
            Created channel data
        """
        channel_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"

        channel = {
            "id": channel_id,
            "name": name,
            "description": description,
            "incident_id": incident_id,
            "channel_type": channel_type,
            "created_by": created_by,
            "created_at": timestamp,
            "updated_at": timestamp,
            "is_archived": False,
        }

        self._channels[channel_id] = channel

        # Persist to OpenSearch if client available
        if self.os_client:
            await self._persist_channel(channel)

        return channel

    async def get_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get channel by ID.

        Args:
            channel_id: Channel identifier

        Returns:
            Channel data or None if not found
        """
        return self._channels.get(channel_id)

    async def list_channels(
        self,
        incident_id: Optional[str] = None,
        include_archived: bool = False,
    ) -> List[Dict[str, Any]]:
        """List collaboration channels.

        Args:
            incident_id: Optional filter by incident
            include_archived: Whether to include archived channels

        Returns:
            List of channels
        """
        channels = list(self._channels.values())

        if incident_id:
            channels = [c for c in channels if c.get("incident_id") == incident_id]

        if not include_archived:
            channels = [c for c in channels if not c.get("is_archived", False)]

        return sorted(channels, key=lambda x: x.get("created_at", ""), reverse=True)

    async def create_message(
        self,
        content: str,
        user: str,
        channel_id: Optional[str] = None,
        incident_id: Optional[str] = None,
        message_type: str = "text",
        attachments: Optional[List[Dict[str, Any]]] = None,
        thread_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new collaboration message.

        Args:
            content: Message content
            user: User who sent the message
            channel_id: Channel ID (uses incident channel or general if not provided)
            incident_id: Associated incident ID
            message_type: Type of message (text, system, evidence, action)
            attachments: Optional list of attachment objects
            thread_id: Optional thread ID for replies

        Returns:
            Created message data
        """
        message_id = f"MSG-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Parse mentions from content
        mentions = self.parse_mentions(content)

        # Determine channel
        if not channel_id:
            if incident_id:
                # Find or create incident channel
                incident_channels = [
                    c for c in self._channels.values()
                    if c.get("incident_id") == incident_id
                ]
                if incident_channels:
                    channel_id = incident_channels[0]["id"]
                else:
                    channel = await self.create_channel(
                        name=f"Incident {incident_id}",
                        incident_id=incident_id,
                        channel_type="incident",
                    )
                    channel_id = channel["id"]
            else:
                channel_id = "general"

        message = {
            "id": message_id,
            "channel_id": channel_id,
            "incident_id": incident_id,
            "user": user,
            "content": content,
            "message_type": message_type,
            "mentions": mentions,
            "attachments": attachments or [],
            "reactions": {},
            "thread_id": thread_id,
            "is_edited": False,
            "is_deleted": False,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        self._messages[message_id] = message
        self._reactions[message_id] = {}

        # Persist to OpenSearch if client available
        if self.os_client:
            await self._persist_message(message)

        # Broadcast to subscribers
        await self._broadcast(channel_id, {
            "type": "message_created",
            "data": message,
        })

        return message

    async def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get message by ID.

        Args:
            message_id: Message identifier

        Returns:
            Message data or None if not found
        """
        return self._messages.get(message_id)

    async def list_messages(
        self,
        incident_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        limit: int = 100,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List messages with filters.

        Args:
            incident_id: Filter by incident ID
            channel_id: Filter by channel ID
            limit: Maximum messages to return
            before: Get messages before this timestamp
            after: Get messages after this timestamp

        Returns:
            List of messages
        """
        messages = list(self._messages.values())

        # Filter deleted messages
        messages = [m for m in messages if not m.get("is_deleted", False)]

        if incident_id:
            messages = [m for m in messages if m.get("incident_id") == incident_id]

        if channel_id:
            messages = [m for m in messages if m.get("channel_id") == channel_id]

        if before:
            messages = [m for m in messages if m.get("created_at", "") < before]

        if after:
            messages = [m for m in messages if m.get("created_at", "") > after]

        # Sort by timestamp ascending (oldest first)
        messages.sort(key=lambda x: x.get("created_at", ""))

        # Return limited results
        return messages[-limit:] if len(messages) > limit else messages

    async def delete_message(self, message_id: str, deleted_by: str) -> bool:
        """Soft delete a message.

        Args:
            message_id: Message to delete
            deleted_by: User who deleted the message

        Returns:
            True if deleted, False if not found
        """
        if message_id not in self._messages:
            return False

        message = self._messages[message_id]
        message["is_deleted"] = True
        message["deleted_by"] = deleted_by
        message["deleted_at"] = datetime.utcnow().isoformat() + "Z"
        message["updated_at"] = datetime.utcnow().isoformat() + "Z"

        # Broadcast to subscribers
        channel_id = message.get("channel_id", "general")
        await self._broadcast(channel_id, {
            "type": "message_deleted",
            "data": {"message_id": message_id, "deleted_by": deleted_by},
        })

        return True

    async def add_reaction(
        self,
        message_id: str,
        emoji: str,
        user: str,
    ) -> Dict[str, Any]:
        """Add a reaction to a message.

        Args:
            message_id: Message to react to
            emoji: Emoji to add
            user: User adding the reaction

        Returns:
            Updated reactions dict

        Raises:
            ValueError: If message not found
        """
        if message_id not in self._messages:
            raise ValueError(f"Message {message_id} not found")

        if message_id not in self._reactions:
            self._reactions[message_id] = {}

        if emoji not in self._reactions[message_id]:
            self._reactions[message_id][emoji] = []

        if user not in self._reactions[message_id][emoji]:
            self._reactions[message_id][emoji].append(user)

        # Update message reactions
        self._messages[message_id]["reactions"] = self._reactions[message_id]

        # Broadcast to subscribers
        channel_id = self._messages[message_id].get("channel_id", "general")
        await self._broadcast(channel_id, {
            "type": "reaction_added",
            "data": {
                "message_id": message_id,
                "emoji": emoji,
                "user": user,
                "reactions": self._reactions[message_id],
            },
        })

        return self._reactions[message_id]

    async def remove_reaction(
        self,
        message_id: str,
        emoji: str,
        user: str,
    ) -> Dict[str, Any]:
        """Remove a reaction from a message.

        Args:
            message_id: Message ID
            emoji: Emoji to remove
            user: User removing the reaction

        Returns:
            Updated reactions dict

        Raises:
            ValueError: If message not found
        """
        if message_id not in self._messages:
            raise ValueError(f"Message {message_id} not found")

        if message_id in self._reactions and emoji in self._reactions[message_id]:
            if user in self._reactions[message_id][emoji]:
                self._reactions[message_id][emoji].remove(user)

                # Remove emoji key if no users left
                if not self._reactions[message_id][emoji]:
                    del self._reactions[message_id][emoji]

        # Update message reactions
        reactions = self._reactions.get(message_id, {})
        self._messages[message_id]["reactions"] = reactions

        # Broadcast to subscribers
        channel_id = self._messages[message_id].get("channel_id", "general")
        await self._broadcast(channel_id, {
            "type": "reaction_removed",
            "data": {
                "message_id": message_id,
                "emoji": emoji,
                "user": user,
                "reactions": reactions,
            },
        })

        return reactions

    async def search_messages(
        self,
        query: str,
        incident_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        user: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search messages by content.

        Args:
            query: Search query
            incident_id: Optional filter by incident
            channel_id: Optional filter by channel
            user: Optional filter by user
            limit: Maximum results

        Returns:
            List of matching messages
        """
        messages = list(self._messages.values())

        # Filter deleted
        messages = [m for m in messages if not m.get("is_deleted", False)]

        # Filter by query (case-insensitive)
        query_lower = query.lower()
        messages = [m for m in messages if query_lower in m.get("content", "").lower()]

        if incident_id:
            messages = [m for m in messages if m.get("incident_id") == incident_id]

        if channel_id:
            messages = [m for m in messages if m.get("channel_id") == channel_id]

        if user:
            messages = [m for m in messages if m.get("user") == user]

        # Sort by relevance (for now, just by recency)
        messages.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return messages[:limit]

    async def subscribe(self, channel_id: str) -> asyncio.Queue:
        """Subscribe to channel updates.

        Args:
            channel_id: Channel to subscribe to

        Returns:
            Queue that will receive channel events
        """
        if channel_id not in self._subscribers:
            self._subscribers[channel_id] = set()

        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers[channel_id].add(queue)
        return queue

    async def unsubscribe(self, channel_id: str, queue: asyncio.Queue):
        """Unsubscribe from channel updates.

        Args:
            channel_id: Channel to unsubscribe from
            queue: Queue to remove
        """
        if channel_id in self._subscribers:
            self._subscribers[channel_id].discard(queue)

    async def _broadcast(self, channel_id: str, event: Dict[str, Any]):
        """Broadcast event to all channel subscribers.

        Args:
            channel_id: Channel to broadcast to
            event: Event data to send
        """
        if channel_id not in self._subscribers:
            return

        # Add timestamp to event
        event["timestamp"] = datetime.utcnow().isoformat() + "Z"

        # Send to all subscribers (non-blocking)
        for queue in list(self._subscribers[channel_id]):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                # Remove slow subscribers
                self._subscribers[channel_id].discard(queue)

    async def _persist_channel(self, channel: Dict[str, Any]) -> None:
        """Persist channel to OpenSearch."""
        if not self.os_client:
            return

        try:
            await self.os_client.index(
                index="collab-channels-v1",
                id=channel["id"],
                body=channel,
                refresh=True,
            )
        except Exception:
            pass

    async def _persist_message(self, message: Dict[str, Any]) -> None:
        """Persist message to OpenSearch."""
        if not self.os_client:
            return

        try:
            await self.os_client.index(
                index="collab-messages-v1",
                id=message["id"],
                body=message,
                refresh=True,
            )
        except Exception:
            pass


# Singleton instance
_service_instance: Optional[CollabService] = None


def get_collab_service() -> CollabService:
    """Get or create the collaboration service singleton."""
    global _service_instance
    if _service_instance is None:
        _service_instance = CollabService()
    return _service_instance
