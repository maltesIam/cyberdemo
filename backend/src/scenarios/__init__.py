"""
Scenario Scripts Registry.

Provides a registry of available attack scenarios that can be loaded
by the ScenarioStateManager. Each scenario is a Python module that
exports phase definitions with SIEM incidents, EDR detections, and IOCs.

Architecture:
- Each scenario is a separate .py file in this directory
- Scenarios export APT29_PHASES (or similar), APT29_METADATA, and cumulative helpers
- The registry maps scenario IDs to their modules
"""

from typing import Dict, Any, Optional

# Registry of available scenarios
_SCENARIO_REGISTRY: Dict[str, Any] = {}


def register_scenario(scenario_id: str, module: Any) -> None:
    """Register a scenario module in the registry."""
    _SCENARIO_REGISTRY[scenario_id] = module


def get_scenario(scenario_id: str) -> Optional[Any]:
    """Get a registered scenario module by ID."""
    return _SCENARIO_REGISTRY.get(scenario_id)


def list_scenarios() -> Dict[str, Dict[str, Any]]:
    """List all registered scenarios with their metadata."""
    result = {}
    for sid, mod in _SCENARIO_REGISTRY.items():
        metadata = getattr(mod, f"{sid.upper()}_METADATA", {})
        result[sid] = metadata
    return result


# Auto-register scenarios on import
def _auto_register():
    """Auto-register all scenario modules."""
    try:
        from . import apt29
        register_scenario("apt29", apt29)
    except ImportError:
        pass


_auto_register()
