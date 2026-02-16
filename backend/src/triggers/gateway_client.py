"""Gateway Client for sending commands to the Moltbot gateway.

This client handles communication with the gateway, including
cooldown and deduplication mechanisms to prevent command spam.
"""
from dataclasses import dataclass
from typing import Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of a command send attempt."""
    success: bool
    message_id: Optional[str] = None
    blocked_by_cooldown: bool = False
    blocked_by_dedup: bool = False
    error: Optional[str] = None


class GatewayClient:
    """Client for sending commands to the Moltbot gateway.

    Features:
    - Cooldown mechanism to prevent sending same command too frequently
    - Deduplication to prevent identical commands
    - Graceful error handling
    """

    def __init__(
        self,
        gateway_url: str = "http://localhost:18789",
        default_cooldown_seconds: int = 60
    ):
        """Initialize the gateway client.

        Args:
            gateway_url: URL of the gateway endpoint
            default_cooldown_seconds: Default cooldown period in seconds
        """
        self.gateway_url = gateway_url
        self.default_cooldown_seconds = default_cooldown_seconds

        # Internal state for cooldown and dedup
        self._cooldown_cache: dict[str, datetime] = {}
        self._dedup_cache: set[str] = set()

    async def send_command(
        self,
        command: str,
        cooldown_key: str,
        dedup_key: str,
        metadata: dict[str, Any],
        cooldown_seconds: Optional[int] = None
    ) -> CommandResult:
        """Send a command to the gateway.

        Args:
            command: The command to send (e.g., "/investigate INC-001")
            cooldown_key: Key for cooldown tracking (e.g., "incident:INC-001")
            dedup_key: Key for deduplication (e.g., "investigate:INC-001")
            metadata: Additional metadata to send with the command
            cooldown_seconds: Override default cooldown period

        Returns:
            CommandResult with success status and details
        """
        cooldown = cooldown_seconds or self.default_cooldown_seconds

        # Check cooldown
        if self._is_on_cooldown(cooldown_key, cooldown):
            logger.debug(f"Command blocked by cooldown: {cooldown_key}")
            return CommandResult(
                success=False,
                blocked_by_cooldown=True
            )

        # Check deduplication
        if self._is_duplicate(dedup_key):
            logger.debug(f"Command blocked by deduplication: {dedup_key}")
            return CommandResult(
                success=False,
                blocked_by_dedup=True
            )

        # Attempt to send command
        try:
            response = await self._http_post(command, metadata)

            # Update caches on success
            self._set_cooldown(cooldown_key)
            self._mark_as_sent(dedup_key)

            logger.info(f"Command sent successfully: {command[:50]}...")
            return CommandResult(
                success=True,
                message_id=response.get("message_id")
            )

        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            return CommandResult(
                success=False,
                error=str(e)
            )

    async def _http_post(self, command: str, metadata: dict[str, Any]) -> dict[str, Any]:
        """Send HTTP POST to gateway. Override in tests.

        Args:
            command: Command string to send
            metadata: Additional metadata

        Returns:
            Response dict from gateway
        """
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.gateway_url}/message/send",
                json={
                    "text": command,
                    "metadata": metadata
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    def _is_on_cooldown(self, key: str, cooldown_seconds: int) -> bool:
        """Check if a key is currently on cooldown."""
        if key not in self._cooldown_cache:
            return False

        expiry = self._cooldown_cache[key]
        if datetime.now() >= expiry:
            del self._cooldown_cache[key]
            return False

        return True

    def _set_cooldown(self, key: str) -> None:
        """Set cooldown for a key."""
        self._cooldown_cache[key] = datetime.now() + timedelta(
            seconds=self.default_cooldown_seconds
        )

    def _is_duplicate(self, key: str) -> bool:
        """Check if a command has already been sent."""
        return key in self._dedup_cache

    def _mark_as_sent(self, key: str) -> None:
        """Mark a command as sent for deduplication."""
        self._dedup_cache.add(key)

    def clear_caches(self) -> None:
        """Clear all cooldown and dedup caches. Useful for testing."""
        self._cooldown_cache.clear()
        self._dedup_cache.clear()


# Singleton instance
_gateway_client: Optional[GatewayClient] = None


def get_gateway_client() -> GatewayClient:
    """Get or create the gateway client singleton."""
    global _gateway_client
    if _gateway_client is None:
        _gateway_client = GatewayClient()
    return _gateway_client


__all__ = ["GatewayClient", "CommandResult", "get_gateway_client"]
