"""
ScenarioStateManager - Singleton managing cumulative phase-aware mock data.

REQ-002-001-001: Singleton with start_scenario, advance_to_phase, reset methods
REQ-002-001-002: Cumulative phase data (phase N includes all data from 1..N)
REQ-002-001-003: Agent mutations persist in state
REQ-002-001-004: Thread-safe state with asyncio Lock
REQ-002-001-005: Only one scenario active at a time
TECH-008: ScenarioStateManager singleton class with async-safe state
"""

import asyncio
import logging
from typing import Any

from ..models.scenario_types import (
    AgentComment,
    PhaseEvents,
    ScenarioState,
)

logger = logging.getLogger(__name__)


class ScenarioStateManager:
    """Singleton manager for cumulative scenario state.

    Provides methods to:
    - start_scenario: Load a scenario and its phase data
    - advance_to_phase: Move to a phase, accumulating all events 1..N
    - get_current_state: Get the current cumulative state
    - reset: Clear all state
    - contain_host: Mark a host as contained (agent mutation)
    - close_incident: Mark an incident as closed (agent mutation)
    - add_comment: Add an agent comment (agent mutation)

    Thread-safe via asyncio.Lock on all state mutations.
    """

    _instance: "ScenarioStateManager | None" = None

    def __init__(self) -> None:
        self._state: ScenarioState | None = None
        self._phases: dict[int, PhaseEvents] = {}
        self._lock = asyncio.Lock()

    @classmethod
    def get_instance(cls) -> "ScenarioStateManager":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def start_scenario(
        self,
        scenario_id: str,
        scenario_name: str,
        phases: dict[int, PhaseEvents],
    ) -> None:
        """Start a new scenario, resetting any previous one.

        REQ-002-001-005: Only one scenario active at a time.
        Starting a new scenario resets the previous one first.

        Args:
            scenario_id: Unique identifier for the scenario (e.g., 'apt29')
            scenario_name: Human-readable name (e.g., 'APT29 - Cozy Bear')
            phases: Dictionary mapping phase numbers to PhaseEvents
        """
        async with self._lock:
            # Reset any existing scenario
            self._state = ScenarioState(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                current_phase=0,
                total_phases=len(phases),
            )
            self._phases = dict(phases)
            logger.info(
                "Scenario started: %s (%d phases)",
                scenario_id,
                len(phases),
            )

    async def advance_to_phase(self, phase_number: int) -> None:
        """Advance to a specific phase, accumulating all events from 1..phase_number.

        REQ-002-001-002: Cumulative phase data.

        Args:
            phase_number: The phase to advance to (1-based)
        """
        async with self._lock:
            if self._state is None:
                raise ValueError("No scenario is active. Call start_scenario first.")

            if phase_number < 1 or phase_number > self._state.total_phases:
                raise ValueError(
                    f"Phase {phase_number} is out of range (1-{self._state.total_phases})"
                )

            # Reset cumulative data and rebuild from phase 1 to phase_number
            incidents = []
            detections = []
            iocs = []

            for p in range(1, phase_number + 1):
                phase_data = self._phases.get(p)
                if phase_data:
                    incidents.extend(phase_data.incidents)
                    detections.extend(phase_data.detections)
                    iocs.extend(phase_data.iocs)

            self._state.current_phase = phase_number
            self._state.incidents = incidents
            self._state.detections = detections
            self._state.iocs = iocs

            # Re-apply agent mutations (contained hosts affect incident status)
            for inc in self._state.incidents:
                if inc.id in self._state.closed_incidents:
                    inc.status = "closed"

            logger.info(
                "Advanced to phase %d/%d (incidents=%d, detections=%d, iocs=%d)",
                phase_number,
                self._state.total_phases,
                len(incidents),
                len(detections),
                len(iocs),
            )

    async def get_current_state(self) -> ScenarioState | None:
        """Get the current cumulative scenario state.

        NFR-006: Must respond in under 10ms.

        Returns:
            The current ScenarioState, or None if no scenario is active.
        """
        return self._state

    async def reset(self) -> None:
        """Reset all state, clearing the active scenario."""
        async with self._lock:
            self._state = None
            self._phases = {}
            logger.info("Scenario state reset")

    async def contain_host(self, host_id: str) -> None:
        """Mark a host as contained (agent mutation).

        REQ-002-001-003: Agent mutations persist in state.

        Args:
            host_id: The host ID to contain
        """
        async with self._lock:
            if self._state is None:
                return
            self._state.contained_hosts.add(host_id)
            logger.info("Host contained: %s", host_id)

    async def close_incident(self, incident_id: str) -> None:
        """Mark an incident as closed (agent mutation).

        REQ-002-001-003: Agent mutations persist in state.

        Args:
            incident_id: The incident ID to close
        """
        async with self._lock:
            if self._state is None:
                return
            self._state.closed_incidents.add(incident_id)
            # Update status in the incidents list
            for inc in self._state.incidents:
                if inc.id == incident_id:
                    inc.status = "closed"
            logger.info("Incident closed: %s", incident_id)

    async def add_comment(self, comment: AgentComment) -> None:
        """Add an agent comment (agent mutation).

        REQ-002-001-003: Agent mutations persist in state.

        Args:
            comment: The AgentComment to add
        """
        async with self._lock:
            if self._state is None:
                return
            self._state.comments.append(comment)
            logger.info("Comment added to incident %s", comment.incident_id)

    def is_scenario_active(self) -> bool:
        """Check if a scenario is currently active."""
        return self._state is not None

    def get_active_scenario_id(self) -> str | None:
        """Get the ID of the currently active scenario."""
        if self._state is not None:
            return self._state.scenario_id
        return None
