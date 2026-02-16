"""
Unit tests for CollabService.

Following TDD: Write tests FIRST, then implement functionality.
"""
import pytest
from unittest.mock import AsyncMock, patch
import asyncio

try:
    from src.services.collab_service import CollabService, get_collab_service
except ImportError:
    pass


class TestCollabServiceMentionParsing:
    """Tests for mention parsing functionality."""

    def test_parse_user_mentions(self):
        """Test parsing @user mentions from content."""
        service = CollabService()

        content = "Hey @john and @jane, please check this alert"
        mentions = service.parse_mentions(content)

        assert "users" in mentions
        assert "john" in mentions["users"]
        assert "jane" in mentions["users"]
        assert len(mentions["users"]) == 2

    def test_parse_asset_mentions(self):
        """Test parsing @ASSET-123 mentions from content."""
        service = CollabService()

        content = "Investigating @ASSET-12345 and @HOST-PROD-WEB-01"
        mentions = service.parse_mentions(content)

        assert "assets" in mentions
        assert "ASSET-12345" in mentions["assets"]
        assert "HOST-PROD-WEB-01" in mentions["assets"]
        assert len(mentions["assets"]) == 2

    def test_parse_mixed_mentions(self):
        """Test parsing both user and asset mentions."""
        service = CollabService()

        content = "@analyst please check @ASSET-001 urgently"
        mentions = service.parse_mentions(content)

        assert "analyst" in mentions["users"]
        assert "ASSET-001" in mentions["assets"]

    def test_parse_no_mentions(self):
        """Test content with no mentions."""
        service = CollabService()

        content = "This is a regular message without mentions"
        mentions = service.parse_mentions(content)

        assert mentions["users"] == []
        assert mentions["assets"] == []

    def test_parse_duplicate_mentions(self):
        """Test that duplicate mentions are deduplicated."""
        service = CollabService()

        content = "@john @john @ASSET-001 @ASSET-001"
        mentions = service.parse_mentions(content)

        assert len(mentions["users"]) == 1
        assert len(mentions["assets"]) == 1


class TestCollabServiceChannels:
    """Tests for channel management."""

    @pytest.mark.asyncio
    async def test_create_channel(self):
        """Test creating a new collaboration channel."""
        service = CollabService()

        channel = await service.create_channel(
            name="Incident INC-2024-001",
            incident_id="INC-2024-001",
            description="Discussion for incident INC-2024-001",
            channel_type="incident",
            created_by="soc-analyst",
        )

        assert channel["name"] == "Incident INC-2024-001"
        assert channel["incident_id"] == "INC-2024-001"
        assert channel["channel_type"] == "incident"
        assert channel["created_by"] == "soc-analyst"
        assert "id" in channel
        assert "created_at" in channel

    @pytest.mark.asyncio
    async def test_get_channel(self):
        """Test retrieving a channel by ID."""
        service = CollabService()

        created = await service.create_channel(name="Test Channel")
        retrieved = await service.get_channel(created["id"])

        assert retrieved is not None
        assert retrieved["id"] == created["id"]
        assert retrieved["name"] == "Test Channel"

    @pytest.mark.asyncio
    async def test_get_nonexistent_channel(self):
        """Test retrieving a non-existent channel."""
        service = CollabService()

        channel = await service.get_channel("nonexistent-id")
        assert channel is None

    @pytest.mark.asyncio
    async def test_list_channels(self):
        """Test listing all channels."""
        service = CollabService()

        await service.create_channel(name="Channel 1")
        await service.create_channel(name="Channel 2")

        channels = await service.list_channels()

        # Should include default "general" channel plus 2 created
        assert len(channels) >= 2

    @pytest.mark.asyncio
    async def test_list_channels_by_incident(self):
        """Test listing channels filtered by incident ID."""
        service = CollabService()

        await service.create_channel(name="Inc 1", incident_id="INC-001")
        await service.create_channel(name="Inc 2", incident_id="INC-002")

        channels = await service.list_channels(incident_id="INC-001")

        assert len(channels) == 1
        assert channels[0]["incident_id"] == "INC-001"

    @pytest.mark.asyncio
    async def test_default_general_channel_exists(self):
        """Test that default general channel is created."""
        service = CollabService()

        channel = await service.get_channel("general")
        assert channel is not None
        assert channel["name"] == "General"
        assert channel["channel_type"] == "general"


class TestCollabServiceMessages:
    """Tests for message management."""

    @pytest.mark.asyncio
    async def test_create_message(self):
        """Test creating a new message."""
        service = CollabService()

        message = await service.create_message(
            content="This is a test message",
            user="soc-analyst",
        )

        assert message["content"] == "This is a test message"
        assert message["user"] == "soc-analyst"
        assert "id" in message
        assert message["id"].startswith("MSG-")
        assert "created_at" in message
        assert message["is_deleted"] is False

    @pytest.mark.asyncio
    async def test_create_message_with_mentions(self):
        """Test that mentions are parsed when creating message."""
        service = CollabService()

        message = await service.create_message(
            content="@john check @ASSET-123",
            user="analyst",
        )

        assert "mentions" in message
        assert "john" in message["mentions"]["users"]
        assert "ASSET-123" in message["mentions"]["assets"]

    @pytest.mark.asyncio
    async def test_create_message_with_incident(self):
        """Test creating message associated with incident."""
        service = CollabService()

        message = await service.create_message(
            content="Initial triage complete",
            user="analyst",
            incident_id="INC-2024-001",
        )

        assert message["incident_id"] == "INC-2024-001"
        # Should have created an incident channel automatically
        assert message["channel_id"] is not None

    @pytest.mark.asyncio
    async def test_create_message_with_attachments(self):
        """Test creating message with attachments."""
        service = CollabService()

        attachments = [
            {"filename": "screenshot.png", "type": "image", "size": 12345},
            {"filename": "logs.txt", "type": "log", "size": 5678},
        ]

        message = await service.create_message(
            content="Evidence attached",
            user="analyst",
            attachments=attachments,
        )

        assert len(message["attachments"]) == 2
        assert message["attachments"][0]["filename"] == "screenshot.png"

    @pytest.mark.asyncio
    async def test_get_message(self):
        """Test retrieving a message by ID."""
        service = CollabService()

        created = await service.create_message(content="Test", user="user")
        retrieved = await service.get_message(created["id"])

        assert retrieved is not None
        assert retrieved["id"] == created["id"]

    @pytest.mark.asyncio
    async def test_list_messages(self):
        """Test listing messages."""
        service = CollabService()

        await service.create_message(content="Message 1", user="user1")
        await service.create_message(content="Message 2", user="user2")

        messages = await service.list_messages()

        assert len(messages) >= 2

    @pytest.mark.asyncio
    async def test_list_messages_by_incident(self):
        """Test listing messages filtered by incident."""
        service = CollabService()

        await service.create_message(content="Inc 1 msg", user="user", incident_id="INC-001")
        await service.create_message(content="Inc 2 msg", user="user", incident_id="INC-002")

        messages = await service.list_messages(incident_id="INC-001")

        assert len(messages) == 1
        assert messages[0]["incident_id"] == "INC-001"

    @pytest.mark.asyncio
    async def test_delete_message(self):
        """Test soft deleting a message."""
        service = CollabService()

        message = await service.create_message(content="To delete", user="user")
        result = await service.delete_message(message["id"], "admin")

        assert result is True

        # Message should be marked as deleted
        deleted = await service.get_message(message["id"])
        assert deleted["is_deleted"] is True

    @pytest.mark.asyncio
    async def test_delete_nonexistent_message(self):
        """Test deleting a non-existent message."""
        service = CollabService()

        result = await service.delete_message("nonexistent", "admin")
        assert result is False

    @pytest.mark.asyncio
    async def test_deleted_messages_excluded_from_list(self):
        """Test that deleted messages are excluded from list."""
        service = CollabService()

        msg = await service.create_message(content="Delete me", user="user")
        await service.delete_message(msg["id"], "admin")

        messages = await service.list_messages()
        message_ids = [m["id"] for m in messages]

        assert msg["id"] not in message_ids


class TestCollabServiceReactions:
    """Tests for reaction management."""

    @pytest.mark.asyncio
    async def test_add_reaction(self):
        """Test adding a reaction to a message."""
        service = CollabService()

        message = await service.create_message(content="React to me", user="user")
        reactions = await service.add_reaction(message["id"], "thumbsup", "analyst")

        assert "thumbsup" in reactions
        assert "analyst" in reactions["thumbsup"]

    @pytest.mark.asyncio
    async def test_add_multiple_reactions(self):
        """Test adding multiple reactions from different users."""
        service = CollabService()

        message = await service.create_message(content="Popular message", user="user")
        await service.add_reaction(message["id"], "thumbsup", "user1")
        await service.add_reaction(message["id"], "thumbsup", "user2")
        reactions = await service.add_reaction(message["id"], "heart", "user1")

        assert len(reactions["thumbsup"]) == 2
        assert "user1" in reactions["thumbsup"]
        assert "user2" in reactions["thumbsup"]
        assert "heart" in reactions

    @pytest.mark.asyncio
    async def test_add_reaction_idempotent(self):
        """Test that same user can't add same reaction twice."""
        service = CollabService()

        message = await service.create_message(content="Test", user="user")
        await service.add_reaction(message["id"], "thumbsup", "analyst")
        reactions = await service.add_reaction(message["id"], "thumbsup", "analyst")

        # Should still be only one entry
        assert len(reactions["thumbsup"]) == 1

    @pytest.mark.asyncio
    async def test_add_reaction_nonexistent_message(self):
        """Test adding reaction to non-existent message."""
        service = CollabService()

        with pytest.raises(ValueError) as exc_info:
            await service.add_reaction("nonexistent", "thumbsup", "user")

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_remove_reaction(self):
        """Test removing a reaction."""
        service = CollabService()

        message = await service.create_message(content="Test", user="user")
        await service.add_reaction(message["id"], "thumbsup", "analyst")
        reactions = await service.remove_reaction(message["id"], "thumbsup", "analyst")

        # Emoji should be removed when no users left
        assert "thumbsup" not in reactions

    @pytest.mark.asyncio
    async def test_remove_reaction_partial(self):
        """Test removing one user's reaction leaves others."""
        service = CollabService()

        message = await service.create_message(content="Test", user="user")
        await service.add_reaction(message["id"], "thumbsup", "user1")
        await service.add_reaction(message["id"], "thumbsup", "user2")
        reactions = await service.remove_reaction(message["id"], "thumbsup", "user1")

        assert "thumbsup" in reactions
        assert "user2" in reactions["thumbsup"]
        assert "user1" not in reactions["thumbsup"]


class TestCollabServiceSearch:
    """Tests for message search functionality."""

    @pytest.mark.asyncio
    async def test_search_messages(self):
        """Test searching messages by content."""
        service = CollabService()

        await service.create_message(content="Malware detected on server", user="analyst")
        await service.create_message(content="Normal traffic observed", user="analyst")

        results = await service.search_messages("malware")

        assert len(results) == 1
        assert "malware" in results[0]["content"].lower()

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self):
        """Test that search is case insensitive."""
        service = CollabService()

        await service.create_message(content="CRITICAL ALERT", user="analyst")

        results = await service.search_messages("critical")
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_with_filters(self):
        """Test search with incident filter."""
        service = CollabService()

        await service.create_message(content="Alert on INC-001", user="analyst", incident_id="INC-001")
        await service.create_message(content="Alert on INC-002", user="analyst", incident_id="INC-002")

        results = await service.search_messages("Alert", incident_id="INC-001")

        assert len(results) == 1
        assert results[0]["incident_id"] == "INC-001"

    @pytest.mark.asyncio
    async def test_search_excludes_deleted(self):
        """Test that search excludes deleted messages."""
        service = CollabService()

        msg = await service.create_message(content="Delete this alert", user="analyst")
        await service.delete_message(msg["id"], "admin")

        results = await service.search_messages("delete")
        assert len(results) == 0


class TestCollabServiceWebSocket:
    """Tests for WebSocket subscription functionality."""

    @pytest.mark.asyncio
    async def test_subscribe_to_channel(self):
        """Test subscribing to a channel."""
        service = CollabService()

        queue = await service.subscribe("general")

        assert queue is not None
        assert "general" in service._subscribers

    @pytest.mark.asyncio
    async def test_unsubscribe_from_channel(self):
        """Test unsubscribing from a channel."""
        service = CollabService()

        queue = await service.subscribe("general")
        await service.unsubscribe("general", queue)

        assert queue not in service._subscribers.get("general", set())

    @pytest.mark.asyncio
    async def test_broadcast_on_message_create(self):
        """Test that creating message broadcasts to subscribers."""
        service = CollabService()

        queue = await service.subscribe("general")

        await service.create_message(content="Test broadcast", user="user")

        # Should have received the broadcast
        event = await asyncio.wait_for(queue.get(), timeout=1.0)

        assert event["type"] == "message_created"
        assert event["data"]["content"] == "Test broadcast"

    @pytest.mark.asyncio
    async def test_broadcast_on_message_delete(self):
        """Test that deleting message broadcasts to subscribers."""
        service = CollabService()

        msg = await service.create_message(content="Delete me", user="user")
        queue = await service.subscribe(msg["channel_id"])

        await service.delete_message(msg["id"], "admin")

        event = await asyncio.wait_for(queue.get(), timeout=1.0)

        assert event["type"] == "message_deleted"
        assert event["data"]["message_id"] == msg["id"]

    @pytest.mark.asyncio
    async def test_broadcast_on_reaction_add(self):
        """Test that adding reaction broadcasts to subscribers."""
        service = CollabService()

        msg = await service.create_message(content="React", user="user")
        queue = await service.subscribe(msg["channel_id"])

        await service.add_reaction(msg["id"], "thumbsup", "analyst")

        event = await asyncio.wait_for(queue.get(), timeout=1.0)

        assert event["type"] == "reaction_added"
        assert event["data"]["emoji"] == "thumbsup"


class TestCollabServiceSingleton:
    """Tests for singleton pattern."""

    def test_get_collab_service_singleton(self):
        """Test that get_collab_service returns singleton."""
        service1 = get_collab_service()
        service2 = get_collab_service()

        assert service1 is service2


class TestCollabServiceMessageTypes:
    """Tests for different message types."""

    @pytest.mark.asyncio
    async def test_create_system_message(self):
        """Test creating a system message."""
        service = CollabService()

        message = await service.create_message(
            content="Incident status changed to In Progress",
            user="system",
            message_type="system",
        )

        assert message["message_type"] == "system"

    @pytest.mark.asyncio
    async def test_create_evidence_message(self):
        """Test creating an evidence message."""
        service = CollabService()

        message = await service.create_message(
            content="Evidence collected from host",
            user="analyst",
            message_type="evidence",
            attachments=[{"filename": "memory_dump.raw", "type": "file"}],
        )

        assert message["message_type"] == "evidence"

    @pytest.mark.asyncio
    async def test_create_action_message(self):
        """Test creating an action message."""
        service = CollabService()

        message = await service.create_message(
            content="Executed containment on HOST-PROD-01",
            user="soar-agent",
            message_type="action",
        )

        assert message["message_type"] == "action"


class TestCollabServiceThreading:
    """Tests for threaded replies."""

    @pytest.mark.asyncio
    async def test_create_threaded_reply(self):
        """Test creating a reply in a thread."""
        service = CollabService()

        parent = await service.create_message(content="Parent message", user="user1")
        reply = await service.create_message(
            content="Reply to parent",
            user="user2",
            thread_id=parent["id"],
        )

        assert reply["thread_id"] == parent["id"]

    @pytest.mark.asyncio
    async def test_list_messages_in_thread(self):
        """Test listing messages with thread filter."""
        service = CollabService()

        parent = await service.create_message(content="Parent", user="user")
        await service.create_message(content="Reply 1", user="user", thread_id=parent["id"])
        await service.create_message(content="Reply 2", user="user", thread_id=parent["id"])
        await service.create_message(content="Other message", user="user")

        # Thread filtering would need to be implemented in list_messages
        # For now, verify replies have thread_id set
        messages = await service.list_messages()
        thread_messages = [m for m in messages if m.get("thread_id") == parent["id"]]

        assert len(thread_messages) == 2
