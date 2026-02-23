"""
Attack Simulation MCP Tools.

Tools for controlling attack simulations:
- attack_start_scenario: Start an attack simulation scenario (REQ-002-002-001)
- attack_pause/resume: Pause and resume simulations (REQ-002-002-002)
- attack_speed: Control simulation speed (REQ-002-002-003)
- attack_jump_to_stage: Jump to a specific MITRE stage (REQ-002-002-004)
- attack_inject_event: Inject custom events (REQ-002-002-005)

These tools enable interactive attack simulations for demos and training.
"""

import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import asyncio
from dataclasses import dataclass, field


# =============================================================================
# Attack Scenarios Definition
# =============================================================================

SCENARIOS: Dict[str, Dict[str, Any]] = {
    "apt29": {
        "name": "APT29 (Cozy Bear)",
        "description": "Russian espionage group targeting government and diplomatic entities",
        "mitre_tactics": [
            {"id": "TA0001", "name": "Initial Access", "techniques": ["T1566.001"]},
            {"id": "TA0002", "name": "Execution", "techniques": ["T1059.001", "T1204.002"]},
            {"id": "TA0003", "name": "Persistence", "techniques": ["T1547.001"]},
            {"id": "TA0005", "name": "Defense Evasion", "techniques": ["T1027", "T1070.004"]},
            {"id": "TA0007", "name": "Discovery", "techniques": ["T1083", "T1057"]},
            {"id": "TA0009", "name": "Collection", "techniques": ["T1560", "T1039"]},
            {"id": "TA0010", "name": "Exfiltration", "techniques": ["T1041"]},
            {"id": "TA0011", "name": "Command and Control", "techniques": ["T1071.001"]}
        ],
        "total_stages": 8
    },
    "fin7": {
        "name": "FIN7",
        "description": "Financially motivated threat group targeting hospitality and retail",
        "mitre_tactics": [
            {"id": "TA0001", "name": "Initial Access", "techniques": ["T1566.001", "T1566.002"]},
            {"id": "TA0002", "name": "Execution", "techniques": ["T1059.003", "T1059.005"]},
            {"id": "TA0003", "name": "Persistence", "techniques": ["T1053.005"]},
            {"id": "TA0006", "name": "Credential Access", "techniques": ["T1555", "T1003"]},
            {"id": "TA0009", "name": "Collection", "techniques": ["T1213", "T1005"]},
            {"id": "TA0010", "name": "Exfiltration", "techniques": ["T1567"]}
        ],
        "total_stages": 6
    },
    "lazarus": {
        "name": "Lazarus Group",
        "description": "North Korean state-sponsored group with destructive capabilities",
        "mitre_tactics": [
            {"id": "TA0001", "name": "Initial Access", "techniques": ["T1566.001"]},
            {"id": "TA0002", "name": "Execution", "techniques": ["T1059.007"]},
            {"id": "TA0003", "name": "Persistence", "techniques": ["T1543.003"]},
            {"id": "TA0005", "name": "Defense Evasion", "techniques": ["T1027", "T1140"]},
            {"id": "TA0040", "name": "Impact", "techniques": ["T1485", "T1486"]}
        ],
        "total_stages": 5
    },
    "revil": {
        "name": "REvil Ransomware",
        "description": "Ransomware-as-a-Service operation targeting enterprise networks",
        "mitre_tactics": [
            {"id": "TA0001", "name": "Initial Access", "techniques": ["T1190", "T1133"]},
            {"id": "TA0002", "name": "Execution", "techniques": ["T1059.001"]},
            {"id": "TA0008", "name": "Lateral Movement", "techniques": ["T1021.002"]},
            {"id": "TA0005", "name": "Defense Evasion", "techniques": ["T1562.001"]},
            {"id": "TA0040", "name": "Impact", "techniques": ["T1486", "T1490"]}
        ],
        "total_stages": 5
    },
    "solarwinds": {
        "name": "SolarWinds-style Supply Chain",
        "description": "Supply chain attack compromising trusted software updates",
        "mitre_tactics": [
            {"id": "TA0001", "name": "Initial Access", "techniques": ["T1195.002"]},
            {"id": "TA0002", "name": "Execution", "techniques": ["T1072"]},
            {"id": "TA0003", "name": "Persistence", "techniques": ["T1098.001"]},
            {"id": "TA0007", "name": "Discovery", "techniques": ["T1087", "T1482"]},
            {"id": "TA0008", "name": "Lateral Movement", "techniques": ["T1550.001"]},
            {"id": "TA0011", "name": "Command and Control", "techniques": ["T1102"]}
        ],
        "total_stages": 6
    },
    "insider": {
        "name": "Insider Threat",
        "description": "Malicious insider exfiltrating sensitive data",
        "mitre_tactics": [
            {"id": "TA0007", "name": "Discovery", "techniques": ["T1083", "T1135"]},
            {"id": "TA0009", "name": "Collection", "techniques": ["T1560.001", "T1005"]},
            {"id": "TA0010", "name": "Exfiltration", "techniques": ["T1567.002", "T1048"]}
        ],
        "total_stages": 3
    }
}


# =============================================================================
# Simulation State Manager
# =============================================================================

@dataclass
class SimulationState:
    """Current state of the attack simulation."""
    simulation_id: str = ""
    scenario_name: Optional[str] = None
    is_running: bool = False
    is_paused: bool = False
    current_stage: int = 1
    speed: float = 1.0
    seed: Optional[int] = None
    started_at: Optional[str] = None
    events_generated: int = 0


class SimulationStateManager:
    """Manages the state of attack simulations."""

    def __init__(self):
        """Initialize the simulation state manager."""
        self._state = SimulationState()
        self._lock = asyncio.Lock()
        self._injected_events: List[Dict[str, Any]] = []

    @property
    def current_scenario(self) -> Optional[str]:
        """Get the current scenario name."""
        return self._state.scenario_name

    @property
    def is_running(self) -> bool:
        """Check if simulation is running (not paused)."""
        return self._state.is_running and not self._state.is_paused

    @property
    def current_stage(self) -> int:
        """Get current stage number."""
        return self._state.current_stage

    @property
    def total_stages(self) -> int:
        """Get total stages in current scenario."""
        if self._state.scenario_name and self._state.scenario_name in SCENARIOS:
            return SCENARIOS[self._state.scenario_name]["total_stages"]
        return 0

    @property
    def speed(self) -> float:
        """Get current speed multiplier."""
        return self._state.speed

    @property
    def pending_events(self) -> List[Dict[str, Any]]:
        """Get pending events."""
        return self._injected_events

    async def start_scenario(self, scenario_name: str, seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Start a new attack scenario.

        Args:
            scenario_name: Name of the scenario to start
            seed: Optional seed for reproducibility

        Returns:
            Dictionary with simulation status
        """
        async with self._lock:
            # Check if simulation is already running
            if self._state.scenario_name and self._state.is_running:
                return {
                    "status": "error",
                    "message": f"Simulation already running: {self._state.scenario_name}"
                }

            if scenario_name not in SCENARIOS:
                return {
                    "status": "error",
                    "message": f"Unknown scenario: {scenario_name}"
                }

            scenario = SCENARIOS[scenario_name]

            self._state = SimulationState(
                simulation_id=str(uuid.uuid4()),
                scenario_name=scenario_name,
                is_running=True,
                is_paused=False,
                current_stage=1,
                speed=1.0,
                seed=seed,
                started_at=datetime.now(timezone.utc).isoformat(),
                events_generated=0
            )

            result = {
                "status": "started",
                "scenario": scenario_name,
                "simulation_id": self._state.simulation_id,
                "seed": seed,
                "mitre_tactics": scenario["mitre_tactics"],
                "total_stages": scenario["total_stages"]
            }

        # Notify persistence outside lock to avoid deadlock
        await self._notify_persistence()
        return result

    async def pause(self) -> Dict[str, Any]:
        """Pause the current simulation."""
        async with self._lock:
            if not self._state.scenario_name:
                return {
                    "status": "error",
                    "message": "No active simulation to pause"
                }

            self._state.is_paused = True
            return {
                "status": "paused",
                "simulation_id": self._state.simulation_id,
                "scenario": self._state.scenario_name
            }

    async def resume(self) -> Dict[str, Any]:
        """Resume a paused simulation."""
        async with self._lock:
            if not self._state.scenario_name:
                return {
                    "status": "error",
                    "message": "No active simulation to resume"
                }

            self._state.is_paused = False
            return {
                "status": "running",
                "simulation_id": self._state.simulation_id,
                "scenario": self._state.scenario_name
            }

    async def set_speed(self, multiplier: float) -> Dict[str, Any]:
        """
        Set the simulation speed.

        Args:
            multiplier: Speed multiplier (0.5 to 4.0)
        """
        async with self._lock:
            if not self._state.scenario_name:
                return {
                    "status": "error",
                    "message": "No active simulation"
                }

            if multiplier < 0.5 or multiplier > 4.0:
                return {
                    "status": "error",
                    "message": "Speed multiplier must be between 0.5 and 4.0"
                }

            self._state.speed = multiplier
            return {
                "status": "success",
                "speed": multiplier
            }

    async def jump_to_stage(self, stage_number: int) -> Dict[str, Any]:
        """
        Jump to a specific stage in the simulation.

        Args:
            stage_number: Stage number to jump to
        """
        async with self._lock:
            if not self._state.scenario_name:
                return {
                    "status": "error",
                    "message": "No active simulation"
                }

            scenario = SCENARIOS.get(self._state.scenario_name)
            if not scenario:
                return {
                    "status": "error",
                    "message": "Scenario not found"
                }

            if stage_number < 1 or stage_number > scenario["total_stages"]:
                return {
                    "status": "error",
                    "message": f"Invalid stage. Valid range: 1-{scenario['total_stages']}"
                }

            self._state.current_stage = stage_number
            tactic = scenario["mitre_tactics"][stage_number - 1] if stage_number <= len(scenario["mitre_tactics"]) else None

            return {
                "status": "success",
                "current_stage": stage_number,
                "tactic": tactic
            }

    async def inject_event(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Inject a custom event into the simulation.

        Args:
            event_type: Type of event to inject
            data: Event data
        """
        async with self._lock:
            if not self._state.scenario_name:
                return {
                    "status": "error",
                    "message": "No active simulation"
                }

            event_id = f"EVT-INJ-{uuid.uuid4().hex[:8]}"
            event = {
                "event_id": event_id,
                "type": event_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": data,
                "injected": True,
                "mitre_tactic": _get_mitre_for_event_type(event_type),
                "mitre_technique": _get_technique_for_event_type(event_type)
            }

            self._injected_events.append(event)
            self._state.events_generated += 1

            return {
                "status": "success",
                "event_id": event_id,
                "mitre_tactic": event["mitre_tactic"],
                "mitre_technique": event["mitre_technique"]
            }

    async def get_state(self) -> Dict[str, Any]:
        """Get the current simulation state."""
        async with self._lock:
            return {
                "simulation_id": self._state.simulation_id,
                "scenario": self._state.scenario_name,
                "is_running": self._state.is_running,
                "is_paused": self._state.is_paused,
                "current_stage": self._state.current_stage,
                "speed": self._state.speed,
                "seed": self._state.seed,
                "events_generated": self._state.events_generated
            }

    async def restore_from_dict(self, state_dict: Dict[str, Any]) -> None:
        """Restore simulation state from a dictionary.

        Args:
            state_dict: Dictionary containing simulation state

        This is used for persistence/recovery functionality.
        """
        async with self._lock:
            self._state = SimulationState(
                simulation_id=state_dict.get("simulation_id", ""),
                scenario_name=state_dict.get("scenario"),
                is_running=state_dict.get("is_running", False),
                is_paused=state_dict.get("is_paused", False),
                current_stage=state_dict.get("current_stage", 1),
                speed=state_dict.get("speed", 1.0),
                seed=state_dict.get("seed"),
                started_at=state_dict.get("started_at"),
                events_generated=state_dict.get("events_generated", 0)
            )

            # Restore injected events if present
            injected_events = state_dict.get("injected_events", [])
            self._injected_events = injected_events

    def register_persistence(self, persistence: Any) -> None:
        """Register a persistence handler for auto-save functionality.

        Args:
            persistence: SimulationStatePersistence instance

        When registered with auto_save=True, state will be saved
        automatically on significant changes.
        """
        self._persistence = persistence

    async def _notify_persistence(self) -> None:
        """Notify persistence handler of state change."""
        if hasattr(self, "_persistence") and self._persistence:
            from src.mcp.tools.simulation_persistence import auto_save_state_callback
            await auto_save_state_callback(self, self._persistence)


# =============================================================================
# Helper Functions
# =============================================================================

def _get_mitre_for_event_type(event_type: str) -> str:
    """Get MITRE tactic ID for an event type."""
    tactic_map = {
        "malware_execution": "TA0002",
        "process_execution": "TA0002",
        "network_connection": "TA0011",
        "file_creation": "TA0005",
        "registry_modification": "TA0003",
        "credential_access": "TA0006",
        "discovery": "TA0007",
        "lateral_movement": "TA0008",
        "collection": "TA0009",
        "exfiltration": "TA0010"
    }
    return tactic_map.get(event_type, "TA0002")


def _get_technique_for_event_type(event_type: str) -> str:
    """Get MITRE technique ID for an event type."""
    technique_map = {
        "malware_execution": "T1204",
        "process_execution": "T1059",
        "network_connection": "T1071",
        "file_creation": "T1027",
        "registry_modification": "T1547.001",
        "credential_access": "T1003",
        "discovery": "T1083",
        "lateral_movement": "T1021",
        "collection": "T1560",
        "exfiltration": "T1041"
    }
    return technique_map.get(event_type, "T1204")


# =============================================================================
# Global State Manager
# =============================================================================

_simulation_manager: Optional[SimulationStateManager] = None


def get_simulation_manager() -> SimulationStateManager:
    """Get the global simulation state manager."""
    global _simulation_manager
    if _simulation_manager is None:
        _simulation_manager = SimulationStateManager()
    return _simulation_manager


def reset_simulation_manager() -> None:
    """Reset the simulation manager (useful for testing)."""
    global _simulation_manager
    _simulation_manager = None


# =============================================================================
# Tool Definitions
# =============================================================================

ATTACK_SIMULATION_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "attack_start_scenario",
        "description": """Start an attack simulation scenario.

Available scenarios:
- apt29: APT29 (Cozy Bear) - Russian espionage
- fin7: FIN7 - Financial crime
- lazarus: Lazarus Group - North Korean destructive
- revil: REvil ransomware
- solarwinds: Supply chain attack
- insider: Insider threat

Returns scenario details including MITRE ATT&CK mapping.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scenario_name": {
                    "type": "string",
                    "description": "Name of the scenario to start (e.g., apt29, fin7)"
                },
                "seed": {
                    "type": "integer",
                    "description": "Optional seed for reproducible event generation"
                }
            },
            "required": ["scenario_name"]
        }
    },
    {
        "name": "attack_pause",
        "description": "Pause the current attack simulation. Event generation will stop but state is preserved.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "attack_resume",
        "description": "Resume a paused attack simulation. Continues from where it was paused.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "attack_speed",
        "description": """Control the speed of the attack simulation.

Speed multiplier range: 0.5x (slow) to 4.0x (fast).
Default is 1.0x (real-time).""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "multiplier": {
                    "type": "number",
                    "description": "Speed multiplier (0.5 to 4.0)",
                    "minimum": 0.5,
                    "maximum": 4.0
                }
            },
            "required": ["multiplier"]
        }
    },
    {
        "name": "attack_jump_to_stage",
        "description": """Jump to a specific stage in the attack scenario.

Each stage corresponds to a MITRE ATT&CK tactic in the attack chain.
Use this to skip to interesting parts of the demo.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "stage_number": {
                    "type": "integer",
                    "description": "Stage number to jump to (1-based index)"
                }
            },
            "required": ["stage_number"]
        }
    },
    {
        "name": "attack_inject_event",
        "description": """Inject a custom event into the simulation.

Event types: malware_execution, process_execution, network_connection,
file_creation, registry_modification, credential_access, discovery,
lateral_movement, collection, exfiltration.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_type": {
                    "type": "string",
                    "description": "Type of event to inject"
                },
                "data": {
                    "type": "object",
                    "description": "Event-specific data"
                }
            },
            "required": ["event_type"]
        }
    }
]


# =============================================================================
# Tool Handlers
# =============================================================================

async def handle_attack_start_scenario(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle attack_start_scenario tool call."""
    scenario_name = args.get("scenario_name")
    seed = args.get("seed")

    if not scenario_name:
        raise ValueError("scenario_name is required")

    manager = get_simulation_manager()
    return await manager.start_scenario(scenario_name, seed)


async def handle_attack_pause(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle attack_pause tool call."""
    manager = get_simulation_manager()
    return await manager.pause()


async def handle_attack_resume(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle attack_resume tool call."""
    manager = get_simulation_manager()
    return await manager.resume()


async def handle_attack_speed(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle attack_speed tool call."""
    multiplier = args.get("multiplier")

    if multiplier is None:
        raise ValueError("multiplier is required")

    manager = get_simulation_manager()
    return await manager.set_speed(multiplier)


async def handle_attack_jump_to_stage(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle attack_jump_to_stage tool call."""
    stage_number = args.get("stage_number")

    if stage_number is None:
        raise ValueError("stage_number is required")

    manager = get_simulation_manager()
    return await manager.jump_to_stage(stage_number)


async def handle_attack_inject_event(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle attack_inject_event tool call."""
    event_type = args.get("event_type")
    data = args.get("data", {})

    if not event_type:
        raise ValueError("event_type is required")

    manager = get_simulation_manager()
    return await manager.inject_event(event_type, data)


# =============================================================================
# Handler Mapping
# =============================================================================

attack_simulation_handlers = {
    "attack_start_scenario": handle_attack_start_scenario,
    "attack_pause": handle_attack_pause,
    "attack_resume": handle_attack_resume,
    "attack_speed": handle_attack_speed,
    "attack_jump_to_stage": handle_attack_jump_to_stage,
    "attack_inject_event": handle_attack_inject_event,
}
