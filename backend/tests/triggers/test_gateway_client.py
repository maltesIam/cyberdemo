"""Unit tests for Gateway Client.

Tests the gateway client's ability to send commands with proper
cooldown and deduplication mechanisms.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import asyncio

from src.triggers.gateway_client import GatewayClient, CommandResult


class TestGatewayClient:
    """Tests for the GatewayClient class."""

    @pytest.fixture
    def client(self):
        """Create a gateway client for testing."""
        return GatewayClient(
            gateway_url="http://localhost:18789",
            default_cooldown_seconds=60
        )

    @pytest.mark.asyncio
    async def test_send_command_success(self, client):
        """Test: Successfully send a command to the gateway."""
        with patch.object(client, '_http_post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {"status": "ok", "message_id": "msg-123"}

            result = await client.send_command(
                command="/investigate INC-001",
                cooldown_key="incident:INC-001",
                dedup_key="investigate:INC-001",
                metadata={"incident_id": "INC-001", "severity": "high"}
            )

            assert result.success is True
            assert result.message_id == "msg-123"
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_cooldown_prevents_duplicate_commands(self, client):
        """Test: Cooldown mechanism prevents sending same command too frequently."""
        with patch.object(client, '_http_post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {"status": "ok", "message_id": "msg-123"}

            # First command should succeed
            result1 = await client.send_command(
                command="/investigate INC-001",
                cooldown_key="incident:INC-001",
                dedup_key="investigate:INC-001:1",
                metadata={}
            )
            assert result1.success is True

            # Second command with same cooldown_key should be blocked
            result2 = await client.send_command(
                command="/investigate INC-001",
                cooldown_key="incident:INC-001",
                dedup_key="investigate:INC-001:2",
                metadata={}
            )
            assert result2.success is False
            assert result2.blocked_by_cooldown is True

            # Only one call to the gateway
            assert mock_post.call_count == 1

    @pytest.mark.asyncio
    async def test_deduplication_prevents_duplicate_commands(self, client):
        """Test: Deduplication prevents sending identical commands."""
        with patch.object(client, '_http_post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {"status": "ok", "message_id": "msg-123"}

            # First command should succeed
            result1 = await client.send_command(
                command="/investigate INC-001",
                cooldown_key="incident:INC-001:a",
                dedup_key="investigate:INC-001",
                metadata={}
            )
            assert result1.success is True

            # Second command with same dedup_key should be blocked
            result2 = await client.send_command(
                command="/investigate INC-001",
                cooldown_key="incident:INC-001:b",
                dedup_key="investigate:INC-001",
                metadata={}
            )
            assert result2.success is False
            assert result2.blocked_by_dedup is True

    @pytest.mark.asyncio
    async def test_error_handling_graceful_failure(self, client):
        """Test: Client handles errors gracefully without crashing."""
        with patch.object(client, '_http_post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("Connection refused")

            result = await client.send_command(
                command="/investigate INC-001",
                cooldown_key="incident:INC-001",
                dedup_key="investigate:INC-001",
                metadata={}
            )

            assert result.success is False
            assert result.error is not None
            assert "Connection refused" in result.error
