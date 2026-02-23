"""
aIP Assist Service for action processing and suggestion generation.

REQ-004-001-004: WebSocket /ws/aip-assist/actions support
REQ-004-002-005: Tracking de aceptacion/rechazo por sesion

aIP = Artificial Intelligence Person

This service manages:
- WebSocket session subscriptions
- Action processing and broadcasting
- Suggestion generation and broadcasting
- Session state tracking for acceptance/rejection
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timezone

from ..models.aip_assist import (
    AipActionContext,
    AipActionBatch,
    AipSuggestionResponse,
    AipSessionState,
)


class AipAssistService:
    """
    Service for managing aIP Assist WebSocket connections and processing.

    Handles:
    - Session subscription/unsubscription
    - Action processing and broadcasting
    - Suggestion generation and delivery
    - Session state tracking
    """

    def __init__(self):
        """Initialize the AipAssistService."""
        # Maps session_id -> list of subscriber queues
        self._sessions: Dict[str, List[asyncio.Queue]] = {}
        # Maps session_id -> session state
        self._session_states: Dict[str, AipSessionState] = {}
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    async def subscribe(self, session_id: str) -> asyncio.Queue:
        """
        Subscribe to actions for a session.

        Args:
            session_id: The session to subscribe to

        Returns:
            An asyncio.Queue that will receive action and suggestion events
        """
        queue = asyncio.Queue()

        async with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = []
                # Initialize session state
                self._session_states[session_id] = AipSessionState(
                    session_id=session_id
                )

            self._sessions[session_id].append(queue)

        return queue

    async def unsubscribe(self, session_id: str, queue: asyncio.Queue) -> None:
        """
        Unsubscribe from a session.

        Args:
            session_id: The session to unsubscribe from
            queue: The queue to remove
        """
        async with self._lock:
            if session_id in self._sessions:
                queues = self._sessions[session_id]
                if queue in queues:
                    queues.remove(queue)

                # Clean up empty session
                if not queues:
                    del self._sessions[session_id]
                    # Keep session state for a while (could add TTL cleanup)

    async def process_action(self, action: AipActionContext) -> None:
        """
        Process an action and broadcast to subscribers.

        Args:
            action: The action to process
        """
        session_id = action.session_id

        # Convert action to dict for broadcasting
        action_data = action.model_dump()

        # Update session state
        if session_id in self._session_states:
            self._session_states[session_id].total_actions += 1

        # Broadcast to all subscribers
        await self._broadcast(session_id, action_data)

    async def broadcast_suggestion(
        self,
        session_id: str,
        suggestion: AipSuggestionResponse
    ) -> None:
        """
        Broadcast a suggestion to all session subscribers.

        Args:
            session_id: The session to broadcast to
            suggestion: The suggestion to broadcast
        """
        suggestion_data = {
            "event": "suggestion",
            **suggestion.model_dump()
        }

        await self._broadcast(session_id, suggestion_data)

    async def _broadcast(self, session_id: str, data: dict) -> None:
        """
        Broadcast data to all subscribers of a session.

        Args:
            session_id: The session to broadcast to
            data: The data to send
        """
        if session_id not in self._sessions:
            return

        for queue in self._sessions[session_id]:
            try:
                await queue.put(data)
            except Exception:
                # Queue may be full or closed
                pass

    def get_session_state(self, session_id: str) -> AipSessionState:
        """
        Get the current state of a session.

        Args:
            session_id: The session to get state for

        Returns:
            The session state, or a new empty state if session not found
        """
        if session_id not in self._session_states:
            self._session_states[session_id] = AipSessionState(
                session_id=session_id
            )

        return self._session_states[session_id]

    def track_suggestion_response(
        self,
        session_id: str,
        suggestion_id: str,
        accepted: bool
    ) -> None:
        """
        Track whether a suggestion was accepted or rejected.

        REQ-004-002-005: Tracking de aceptacion/rechazo por sesion

        Args:
            session_id: The session
            suggestion_id: The suggestion ID
            accepted: Whether the suggestion was accepted
        """
        if session_id not in self._session_states:
            self._session_states[session_id] = AipSessionState(
                session_id=session_id
            )

        state = self._session_states[session_id]
        if accepted:
            state.accepted_suggestions += 1
        else:
            state.rejected_suggestions += 1


# Singleton instance
_aip_assist_service: Optional[AipAssistService] = None


def get_aip_assist_service() -> AipAssistService:
    """
    Get the singleton AipAssistService instance.

    Returns:
        The AipAssistService singleton
    """
    global _aip_assist_service
    if _aip_assist_service is None:
        _aip_assist_service = AipAssistService()
    return _aip_assist_service


def reset_aip_assist_service() -> None:
    """Reset the singleton instance (for testing)."""
    global _aip_assist_service
    _aip_assist_service = None


# =============================================================================
# Backwards Compatibility Aliases
# =============================================================================

CopilotService = AipAssistService
get_copilot_service = get_aip_assist_service
