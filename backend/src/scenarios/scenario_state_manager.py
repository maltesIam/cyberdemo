"""
ScenarioStateManager - Manages cumulative simulation state for scenarios.

Singleton class that maintains the current scenario state including:
- Active scenario and current phase
- Cumulative event data (incidents, detections, IOCs)
- Agent mutations (containment, closures, comments, tickets)

This manager is queried by all 25 SOC tool handlers when a scenario is active.
When no scenario is active, tool handlers fall through to their static data.

Requirements:
- REQ-002-001-001: Singleton with start/advance/reset
- REQ-002-001-002: Cumulative phase data
- REQ-002-001-003: Agent mutation persistence
- REQ-002-001-005: Only one scenario active at a time
- BR-009: Data is always cumulative
- BR-010: Mutations are immediate
- BR-013: No future-phase data
"""

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


class ScenarioStateManager:
    """Manages cumulative simulation state for attack scenarios.

    Thread-safe singleton that provides phase-aware data retrieval
    and mutation tracking for tool handlers.
    """

    def __init__(self):
        self._active_scenario_id: Optional[str] = None
        self._current_phase: int = 0
        self._scenario_module: Optional[Any] = None
        self._lock = asyncio.Lock()

        # Mutation state
        self._contained_hosts: List[str] = []
        self._closed_incidents: List[str] = []
        self._comments: Dict[str, List[Dict[str, Any]]] = {}
        self._tickets: List[Dict[str, Any]] = []

    def is_active(self) -> bool:
        """Check if a scenario is currently active."""
        return self._active_scenario_id is not None and self._current_phase > 0

    @property
    def current_phase(self) -> int:
        """Get the current phase number."""
        return self._current_phase

    @property
    def scenario_id(self) -> Optional[str]:
        """Get the active scenario ID."""
        return self._active_scenario_id

    async def start_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """Start a new scenario, resetting any previous state.

        Args:
            scenario_id: The scenario identifier (e.g., 'apt29').

        Returns:
            Dict with start status.
        """
        async with self._lock:
            # Reset previous state
            self._reset_internal()

            # Load scenario module
            from src.scenarios import get_scenario
            module = get_scenario(scenario_id)
            if module is None:
                return {"status": "error", "message": f"Unknown scenario: {scenario_id}"}

            self._active_scenario_id = scenario_id
            self._scenario_module = module
            self._current_phase = 1

            return {
                "status": "started",
                "scenario": scenario_id,
                "phase": 1,
            }

    async def advance_to_phase(self, phase: int) -> Dict[str, Any]:
        """Advance to a specific phase (cumulative).

        Args:
            phase: Target phase number.

        Returns:
            Dict with advance status.
        """
        async with self._lock:
            if not self._active_scenario_id:
                return {"status": "error", "message": "No active scenario"}

            metadata = self._get_metadata()
            total = metadata.get("total_phases", 8)
            if phase < 1 or phase > total:
                return {
                    "status": "error",
                    "message": f"Invalid phase {phase}. Valid: 1-{total}",
                }

            self._current_phase = phase
            return {"status": "advanced", "phase": phase}

    async def reset(self) -> Dict[str, Any]:
        """Reset the scenario state completely."""
        async with self._lock:
            self._reset_internal()
            return {"status": "reset"}

    def _reset_internal(self):
        """Internal reset without lock."""
        self._active_scenario_id = None
        self._current_phase = 0
        self._scenario_module = None
        self._contained_hosts = []
        self._closed_incidents = []
        self._comments = {}
        self._tickets = []

    # ------------------------------------------------------------------
    # Data retrieval (cumulative, phase-aware)
    # ------------------------------------------------------------------

    def get_incidents(self, severity: Optional[str] = None,
                      status: Optional[str] = None,
                      limit: int = 50) -> List[Dict[str, Any]]:
        """Get cumulative SIEM incidents up to the current phase.

        Applies mutations (closed incidents, containment status).
        """
        if not self.is_active() or not self._scenario_module:
            return []

        incidents = self._scenario_module.get_cumulative_incidents(self._current_phase)

        # Apply mutations
        enriched = []
        for inc in incidents:
            inc_copy = dict(inc)
            # Apply containment status
            asset = inc_copy.get("asset", "")
            if asset in self._contained_hosts:
                inc_copy["containment_status"] = "contained"
            # Apply closure status
            if inc_copy["id"] in self._closed_incidents:
                inc_copy["status"] = "closed"
            # Apply comments
            if inc_copy["id"] in self._comments:
                inc_copy["comments"] = self._comments[inc_copy["id"]]
            enriched.append(inc_copy)

        # Apply filters
        if severity:
            enriched = [i for i in enriched if i["severity"] == severity]
        if status:
            enriched = [i for i in enriched if i["status"] == status]

        return enriched[:limit]

    def get_incident_by_id(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific incident by ID from cumulative data."""
        if not self.is_active() or not self._scenario_module:
            return None

        incidents = self._scenario_module.get_cumulative_incidents(self._current_phase)
        for inc in incidents:
            if inc["id"] == incident_id:
                inc_copy = dict(inc)
                # Apply mutations
                asset = inc_copy.get("asset", "")
                if asset in self._contained_hosts:
                    inc_copy["containment_status"] = "contained"
                if inc_copy["id"] in self._closed_incidents:
                    inc_copy["status"] = "closed"
                if inc_copy["id"] in self._comments:
                    inc_copy["comments"] = self._comments[inc_copy["id"]]
                return inc_copy
        return None

    def get_detections(self, severity: Optional[str] = None,
                       limit: int = 50) -> List[Dict[str, Any]]:
        """Get cumulative EDR detections up to the current phase."""
        if not self.is_active() or not self._scenario_module:
            return []

        detections = self._scenario_module.get_cumulative_detections(self._current_phase)

        enriched = []
        for det in detections:
            det_copy = dict(det)
            host = det_copy.get("host", "")
            if host in self._contained_hosts:
                det_copy["host_status"] = "contained"
            enriched.append(det_copy)

        if severity:
            enriched = [d for d in enriched if d["severity"] == severity]

        return enriched[:limit]

    def get_detection_by_id(self, detection_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific detection by ID from cumulative data."""
        if not self.is_active() or not self._scenario_module:
            return None

        detections = self._scenario_module.get_cumulative_detections(self._current_phase)
        for det in detections:
            if det["id"] == detection_id:
                det_copy = dict(det)
                host = det_copy.get("host", "")
                if host in self._contained_hosts:
                    det_copy["host_status"] = "contained"
                return det_copy
        return None

    def get_iocs(self) -> List[Dict[str, Any]]:
        """Get cumulative IOCs up to the current phase."""
        if not self.is_active() or not self._scenario_module:
            return []
        return self._scenario_module.get_cumulative_iocs(self._current_phase)

    def get_ioc_by_value(self, indicator_type: str,
                         value: str) -> Optional[Dict[str, Any]]:
        """Get a specific IOC by type and value from cumulative data."""
        if not self.is_active() or not self._scenario_module:
            return None

        iocs = self._scenario_module.get_cumulative_iocs(self._current_phase)
        for ioc in iocs:
            if ioc["type"] == indicator_type and ioc["value"] == value:
                return dict(ioc)
        return None

    def get_tickets_for_incident(self, incident_id: Optional[str] = None,
                                 limit: int = 20) -> List[Dict[str, Any]]:
        """Get tickets, optionally filtered by incident."""
        if not self.is_active():
            return []
        tickets = self._tickets
        if incident_id:
            tickets = [t for t in tickets if t.get("incident_id") == incident_id]
        return tickets[:limit]

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def contain_host(self, device_id: str) -> None:
        """Record that a host has been contained."""
        if device_id not in self._contained_hosts:
            self._contained_hosts.append(device_id)

    def lift_containment(self, device_id: str) -> None:
        """Record that containment has been lifted from a host."""
        if device_id in self._contained_hosts:
            self._contained_hosts.remove(device_id)

    def close_incident(self, incident_id: str) -> None:
        """Record that an incident has been closed."""
        if incident_id not in self._closed_incidents:
            self._closed_incidents.append(incident_id)

    def add_comment(self, incident_id: str, comment: str) -> str:
        """Add a comment to an incident. Returns comment ID."""
        if incident_id not in self._comments:
            self._comments[incident_id] = []
        comment_id = f"CMT-{incident_id[-3:]}-{len(self._comments[incident_id]) + 1:03d}"
        self._comments[incident_id].append({
            "id": comment_id,
            "text": comment,
            "author": "vega-agent",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return comment_id

    def create_ticket(self, ticket_data: Dict[str, Any]) -> str:
        """Create a ticket and store it in state. Returns ticket ID."""
        ticket_id = f"TKT-{len(self._tickets) + 1:03d}"
        ticket = {
            "ticket_id": ticket_id,
            "title": ticket_data.get("title", ""),
            "description": ticket_data.get("description", ""),
            "incident_id": ticket_data.get("incident_id", ""),
            "priority": ticket_data.get("priority", "high"),
            "status": "open",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._tickets.append(ticket)
        return ticket_id

    # ------------------------------------------------------------------
    # State introspection
    # ------------------------------------------------------------------

    def get_current_state(self) -> Dict[str, Any]:
        """Get current state summary for introspection/debugging."""
        return {
            "scenario_id": self._active_scenario_id,
            "current_phase": self._current_phase,
            "is_active": self.is_active(),
            "contained_hosts": list(self._contained_hosts),
            "closed_incidents": list(self._closed_incidents),
            "comments": dict(self._comments),
            "tickets": list(self._tickets),
        }

    def _get_metadata(self) -> Dict[str, Any]:
        """Get scenario metadata."""
        if not self._scenario_module:
            return {}
        attr_name = f"{self._active_scenario_id.upper()}_METADATA"
        return getattr(self._scenario_module, attr_name, {})


# =============================================================================
# Global singleton management
# =============================================================================

_scenario_manager: Optional[ScenarioStateManager] = None


def get_scenario_manager() -> ScenarioStateManager:
    """Get the global ScenarioStateManager singleton."""
    global _scenario_manager
    if _scenario_manager is None:
        _scenario_manager = ScenarioStateManager()
    return _scenario_manager


def reset_scenario_manager() -> None:
    """Reset the global ScenarioStateManager (for testing)."""
    global _scenario_manager
    _scenario_manager = None
