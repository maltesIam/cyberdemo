"""
Simulation State Persistence Module.

Provides file-based persistence for attack simulation state.
Implements REQ-002-002-006 and REQ-013.

Features:
- Save simulation state to JSON files
- Load simulation state from files
- Auto-save on state changes
- Cleanup of old state files
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.mcp.tools.attack_simulation import SimulationStateManager


class SimulationStatePersistence:
    """Handles persistence of simulation state to files.

    Attributes:
        state_dir: Directory where state files are stored
        auto_save: If True, state is saved automatically on changes
        max_state_files: Maximum number of state files to keep
    """

    def __init__(
        self,
        state_dir: Optional[str] = None,
        auto_save: bool = False,
        max_state_files: int = 10,
    ):
        """Initialize persistence handler.

        Args:
            state_dir: Directory for state files. Defaults to ./simulation_state
            auto_save: Enable automatic state saving on changes
            max_state_files: Maximum number of state files to retain
        """
        if state_dir is None:
            state_dir = os.path.join(os.getcwd(), "simulation_state")

        self.state_dir = state_dir
        self.auto_save = auto_save
        self.max_state_files = max_state_files
        self._lock = asyncio.Lock()

        # Create state directory if it doesn't exist
        os.makedirs(self.state_dir, exist_ok=True)

    async def save_state(
        self,
        manager: "SimulationStateManager",
    ) -> Optional[str]:
        """Save the current simulation state to a file.

        Args:
            manager: The SimulationStateManager to save state from

        Returns:
            Path to the saved state file, or None if no active simulation
        """
        async with self._lock:
            # Get current state
            state = await manager.get_state()

            # Add persistence metadata
            state["saved_at"] = datetime.now(timezone.utc).isoformat()

            # Include injected events
            state["injected_events"] = [
                {
                    "event_id": evt.get("event_id", ""),
                    "type": evt.get("type", ""),
                    "data": evt.get("data", {}),
                    "timestamp": evt.get("timestamp", ""),
                    "injected": evt.get("injected", True),
                    "mitre_tactic": evt.get("mitre_tactic"),
                    "mitre_technique": evt.get("mitre_technique"),
                }
                for evt in manager.pending_events
            ]

            # Generate filename with timestamp
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"simulation_state_{timestamp}.json"
            filepath = os.path.join(self.state_dir, filename)

            # Write state to file
            with open(filepath, "w") as f:
                json.dump(state, f, indent=2, default=str)

            return filepath

    async def load_state(
        self,
        manager: "SimulationStateManager",
        filepath: str,
    ) -> bool:
        """Load simulation state from a file.

        Args:
            manager: The SimulationStateManager to restore state to
            filepath: Path to the state file to load

        Returns:
            True if state was loaded successfully, False otherwise
        """
        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, "r") as f:
                state_data = json.load(f)

            # Restore state to manager
            await manager.restore_from_dict(state_data)

            return True
        except (json.JSONDecodeError, IOError, KeyError) as e:
            # Log error in production
            return False

    def get_latest_state_file(self) -> Optional[str]:
        """Get the path to the most recent state file.

        Returns:
            Path to the latest state file, or None if no files exist
        """
        state_files = self._get_state_files()

        if not state_files:
            return None

        # Sort by modification time, most recent last
        state_files.sort(key=lambda f: os.path.getmtime(f))

        return state_files[-1]

    def cleanup_old_state_files(self) -> int:
        """Remove old state files, keeping only max_state_files.

        Returns:
            Number of files removed
        """
        state_files = self._get_state_files()

        if len(state_files) <= self.max_state_files:
            return 0

        # Sort by modification time, oldest first
        state_files.sort(key=lambda f: os.path.getmtime(f))

        # Calculate how many to remove
        files_to_remove = state_files[:-self.max_state_files]

        removed_count = 0
        for filepath in files_to_remove:
            try:
                os.remove(filepath)
                removed_count += 1
            except OSError:
                pass

        return removed_count

    def _get_state_files(self) -> List[str]:
        """Get all state files in the state directory.

        Returns:
            List of state file paths
        """
        if not os.path.exists(self.state_dir):
            return []

        state_files = []
        for filename in os.listdir(self.state_dir):
            if filename.startswith("simulation_state_") and filename.endswith(".json"):
                state_files.append(os.path.join(self.state_dir, filename))

        return state_files


# =============================================================================
# Helper function for auto-save integration
# =============================================================================

async def auto_save_state_callback(
    manager: "SimulationStateManager",
    persistence: SimulationStatePersistence,
) -> None:
    """Callback for auto-saving state on changes.

    Args:
        manager: The SimulationStateManager
        persistence: The persistence handler
    """
    if persistence.auto_save:
        await persistence.save_state(manager)
        persistence.cleanup_old_state_files()
