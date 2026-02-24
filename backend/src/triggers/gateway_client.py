"""Gateway Client for communicating with the OpenClaw gateway agent.

This client handles communication with the OpenClaw gateway via the
Chat Completions API, including cooldown and deduplication mechanisms.
"""
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)

GATEWAY_URL = os.environ.get("OPENCLAW_GATEWAY_URL", "http://localhost:18789")
GATEWAY_TOKEN = os.environ.get("OPENCLAW_GATEWAY_TOKEN", "")


@dataclass
class CommandResult:
    """Result of a command send attempt."""
    success: bool
    content: Optional[str] = None
    message_id: Optional[str] = None
    blocked_by_cooldown: bool = False
    blocked_by_dedup: bool = False
    error: Optional[str] = None


@dataclass
class AgentResponse:
    """Response from the OpenClaw agent."""
    content: str
    model: str = ""
    finish_reason: str = ""
    agent_id: str = "main"


class GatewayClient:
    """Client for communicating with the OpenClaw gateway agent.

    Uses the OpenAI-compatible Chat Completions API at /v1/chat/completions.
    Also supports direct tool invocation via /tools/invoke.
    """

    def __init__(
        self,
        gateway_url: str = "",
        gateway_token: str = "",
        default_cooldown_seconds: int = 60
    ):
        self.gateway_url = gateway_url or GATEWAY_URL
        self.gateway_token = gateway_token or GATEWAY_TOKEN
        self.default_cooldown_seconds = default_cooldown_seconds
        self._cooldown_cache: dict[str, datetime] = {}
        self._dedup_cache: set[str] = set()

    async def chat(
        self,
        message: str,
        system_prompt: str = "",
        agent_id: str = "main",
        max_tokens: int = 500,
        session_key: str = ""
    ) -> AgentResponse:
        """Send a chat message to the OpenClaw agent via Chat Completions API.

        Args:
            message: The user message to send
            system_prompt: Optional system prompt for context
            agent_id: Agent ID (default: "main")
            max_tokens: Maximum response tokens
            session_key: Optional session key for conversation continuity

        Returns:
            AgentResponse with the agent's reply
        """
        import httpx

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        headers = {
            "Content-Type": "application/json",
            "x-openclaw-agent-id": agent_id,
        }
        if self.gateway_token:
            headers["Authorization"] = f"Bearer {self.gateway_token}"
        if session_key:
            headers["x-openclaw-session-key"] = session_key

        payload = {
            "model": f"openclaw:{agent_id}",
            "messages": messages,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.gateway_url}/v1/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()

            choices = data.get("choices", [])
            if choices:
                choice = choices[0]
                return AgentResponse(
                    content=choice["message"]["content"],
                    model=data.get("model", ""),
                    finish_reason=choice.get("finish_reason", ""),
                    agent_id=agent_id,
                )
            return AgentResponse(content="No response from agent", agent_id=agent_id)

        except httpx.HTTPStatusError as e:
            logger.error(f"Gateway HTTP error: {e.response.status_code} - {e.response.text[:200]}")
            raise
        except Exception as e:
            logger.error(f"Gateway connection error: {e}")
            raise

    async def invoke_tool(
        self,
        tool: str,
        args: dict[str, Any] | None = None,
        action: str = "",
        session_key: str = "main"
    ) -> dict[str, Any]:
        """Invoke a tool directly on the OpenClaw gateway.

        Args:
            tool: Tool name to invoke
            args: Tool-specific arguments
            action: Optional action parameter
            session_key: Target session key

        Returns:
            Tool result dict
        """
        import httpx

        headers = {"Content-Type": "application/json"}
        if self.gateway_token:
            headers["Authorization"] = f"Bearer {self.gateway_token}"

        payload: dict[str, Any] = {"tool": tool, "args": args or {}}
        if action:
            payload["action"] = action
        if session_key:
            payload["sessionKey"] = session_key

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.gateway_url}/tools/invoke",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        if data.get("ok"):
            return data.get("result", {})
        else:
            error = data.get("error", {})
            raise RuntimeError(f"Tool invocation failed: {error.get('message', 'Unknown error')}")

    async def send_command(
        self,
        command: str,
        cooldown_key: str,
        dedup_key: str,
        metadata: dict[str, Any],
        cooldown_seconds: Optional[int] = None
    ) -> CommandResult:
        """Send a command to the gateway agent (with cooldown/dedup).

        Args:
            command: The command/message to send
            cooldown_key: Key for cooldown tracking
            dedup_key: Key for deduplication
            metadata: Additional context metadata
            cooldown_seconds: Override default cooldown period

        Returns:
            CommandResult with success status and agent response
        """
        cooldown = cooldown_seconds or self.default_cooldown_seconds

        if self._is_on_cooldown(cooldown_key, cooldown):
            return CommandResult(success=False, blocked_by_cooldown=True)

        if self._is_duplicate(dedup_key):
            return CommandResult(success=False, blocked_by_dedup=True)

        try:
            context = "\n".join(f"{k}: {v}" for k, v in metadata.items()) if metadata else ""
            full_message = f"{command}\n\nContext:\n{context}" if context else command

            response = await self.chat(message=full_message)

            self._set_cooldown(cooldown_key)
            self._mark_as_sent(dedup_key)

            return CommandResult(
                success=True,
                content=response.content,
            )

        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            return CommandResult(success=False, error=str(e))

    def _is_on_cooldown(self, key: str, cooldown_seconds: int) -> bool:
        if key not in self._cooldown_cache:
            return False
        expiry = self._cooldown_cache[key]
        if datetime.now() >= expiry:
            del self._cooldown_cache[key]
            return False
        return True

    def _set_cooldown(self, key: str) -> None:
        self._cooldown_cache[key] = datetime.now() + timedelta(
            seconds=self.default_cooldown_seconds
        )

    def _is_duplicate(self, key: str) -> bool:
        return key in self._dedup_cache

    def _mark_as_sent(self, key: str) -> None:
        self._dedup_cache.add(key)

    def clear_caches(self) -> None:
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


__all__ = ["GatewayClient", "CommandResult", "AgentResponse", "get_gateway_client"]
