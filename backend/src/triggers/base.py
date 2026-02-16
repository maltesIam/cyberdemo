"""Base class for all trigger handlers."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TriggerEvent:
    """Represents an event that can trigger an action."""

    event_type: str
    source: str
    timestamp: datetime
    data: Dict[str, Any]
    severity: Optional[str] = None
    entity_id: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)


@dataclass
class TriggerResult:
    """Result of processing a trigger event."""

    triggered: bool
    command: Optional[str] = None
    message: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BaseTriggerHandler(ABC):
    """Abstract base class for all trigger handlers.

    Trigger handlers evaluate events and determine if they should
    trigger a command to be sent to the MCP gateway.
    """

    def __init__(self, gateway_client: Optional["GatewayClient"] = None):
        self.gateway_client = gateway_client
        self._enabled = True

    @property
    @abstractmethod
    def trigger_name(self) -> str:
        """Unique name identifying this trigger."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this trigger does."""
        pass

    @property
    @abstractmethod
    def event_types(self) -> list[str]:
        """List of event types this trigger responds to."""
        pass

    @abstractmethod
    def should_trigger(self, event: TriggerEvent) -> bool:
        """Evaluate if the event should trigger this handler.

        Args:
            event: The event to evaluate

        Returns:
            True if the event should trigger the handler
        """
        pass

    @abstractmethod
    def get_command(self, event: TriggerEvent) -> str:
        """Get the command to send when triggered.

        Args:
            event: The triggering event

        Returns:
            The command string to send to the gateway
        """
        pass

    def get_context(self, event: TriggerEvent) -> Dict[str, Any]:
        """Get additional context for the command.

        Override this method to provide additional context
        that should be included with the command.

        Args:
            event: The triggering event

        Returns:
            Dictionary of context data
        """
        return {
            "trigger": self.trigger_name,
            "event_type": event.event_type,
            "source": event.source,
            "timestamp": event.timestamp.isoformat(),
        }

    def get_cooldown_key(self, event: TriggerEvent) -> str:
        """Get the cooldown key for this trigger/event combination.

        Override for custom cooldown behavior.

        Args:
            event: The triggering event

        Returns:
            A string key for cooldown tracking
        """
        entity = event.entity_id or event.data.get("entity_id", "default")
        return f"{self.trigger_name}:{entity}"

    def get_dedup_key(self, event: TriggerEvent) -> str:
        """Get the deduplication key for this trigger/event combination.

        Override for custom deduplication behavior.

        Args:
            event: The triggering event

        Returns:
            A string key for deduplication
        """
        command = self.get_command(event)
        return f"{self.trigger_name}:{hash(command)}"

    async def process(self, event: TriggerEvent) -> TriggerResult:
        """Process an event and potentially send a command.

        Args:
            event: The event to process

        Returns:
            TriggerResult indicating what action was taken
        """
        if not self._enabled:
            return TriggerResult(
                triggered=False,
                message="Trigger is disabled"
            )

        if event.event_type not in self.event_types:
            return TriggerResult(
                triggered=False,
                message=f"Event type {event.event_type} not handled"
            )

        if not self.should_trigger(event):
            return TriggerResult(
                triggered=False,
                message="Trigger conditions not met"
            )

        command = self.get_command(event)
        context = self.get_context(event)

        if self.gateway_client:
            try:
                cooldown_key = self.get_cooldown_key(event)
                dedup_key = self.get_dedup_key(event)

                await self.gateway_client.send_command(
                    command=command,
                    cooldown_key=cooldown_key,
                    dedup_key=dedup_key,
                    metadata=context
                )
            except Exception as e:
                return TriggerResult(
                    triggered=True,
                    command=command,
                    context=context,
                    error=str(e)
                )

        return TriggerResult(
            triggered=True,
            command=command,
            context=context,
            message=f"Triggered command: {command}"
        )

    def enable(self):
        """Enable this trigger."""
        self._enabled = True

    def disable(self):
        """Disable this trigger."""
        self._enabled = False

    @property
    def is_enabled(self) -> bool:
        """Check if this trigger is enabled."""
        return self._enabled


# Forward reference for type hint
from .gateway_client import GatewayClient

__all__ = ["BaseTriggerHandler", "TriggerEvent", "TriggerResult"]
