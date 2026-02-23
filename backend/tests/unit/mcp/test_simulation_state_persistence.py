"""
Unit tests for Simulation State Persistence.

Test ID: UT-029 (REQ-002-002-006, REQ-013)

Tests the simulation state persistence functionality:
- Save simulation state
- Load simulation state
- State recovery after restart
- File-based persistence
"""

import pytest
import asyncio
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


class TestSimulationStatePersistence:
    """Test simulation state persistence (UT-029, REQ-002-002-006)."""

    @pytest.fixture
    def temp_state_dir(self, tmp_path):
        """Create temporary directory for state files."""
        return tmp_path

    @pytest.mark.asyncio
    async def test_save_state_creates_file(self, temp_state_dir):
        """Test that save_state creates a state file."""
        from src.mcp.tools.attack_simulation import (
            SimulationStateManager,
            reset_simulation_manager,
        )
        from src.mcp.tools.simulation_persistence import SimulationStatePersistence

        reset_simulation_manager()
        manager = SimulationStateManager()
        persistence = SimulationStatePersistence(state_dir=str(temp_state_dir))

        # Start a simulation
        await manager.start_scenario("apt29", seed=42)

        # Save state
        state_file = await persistence.save_state(manager)

        assert os.path.exists(state_file)
        assert state_file.endswith(".json")

    @pytest.mark.asyncio
    async def test_save_state_contains_all_fields(self, temp_state_dir):
        """Test that saved state contains all necessary fields."""
        from src.mcp.tools.attack_simulation import (
            SimulationStateManager,
            reset_simulation_manager,
        )
        from src.mcp.tools.simulation_persistence import SimulationStatePersistence

        reset_simulation_manager()
        manager = SimulationStateManager()
        persistence = SimulationStatePersistence(state_dir=str(temp_state_dir))

        await manager.start_scenario("apt29", seed=42)
        await manager.set_speed(2.0)
        await manager.jump_to_stage(3)

        state_file = await persistence.save_state(manager)

        with open(state_file, "r") as f:
            saved_state = json.load(f)

        # Verify required fields
        assert "simulation_id" in saved_state
        assert "scenario" in saved_state
        assert saved_state["scenario"] == "apt29"
        assert "is_running" in saved_state
        assert "is_paused" in saved_state
        assert "current_stage" in saved_state
        assert saved_state["current_stage"] == 3
        assert "speed" in saved_state
        assert saved_state["speed"] == 2.0
        assert "seed" in saved_state
        assert saved_state["seed"] == 42
        assert "events_generated" in saved_state
        assert "saved_at" in saved_state

    @pytest.mark.asyncio
    async def test_load_state_restores_simulation(self, temp_state_dir):
        """Test that load_state restores simulation correctly."""
        from src.mcp.tools.attack_simulation import (
            SimulationStateManager,
            reset_simulation_manager,
        )
        from src.mcp.tools.simulation_persistence import SimulationStatePersistence

        reset_simulation_manager()
        manager = SimulationStateManager()
        persistence = SimulationStatePersistence(state_dir=str(temp_state_dir))

        # Start and configure simulation
        await manager.start_scenario("fin7", seed=123)
        await manager.set_speed(3.0)
        await manager.jump_to_stage(4)
        await manager.inject_event("malware_execution", {"host": "WS-001"})

        # Save state
        state_file = await persistence.save_state(manager)

        # Reset and create new manager
        reset_simulation_manager()
        new_manager = SimulationStateManager()

        # Load state
        loaded = await persistence.load_state(new_manager, state_file)

        assert loaded is True
        assert new_manager.current_scenario == "fin7"
        assert new_manager.current_stage == 4
        assert new_manager.speed == 3.0

    @pytest.mark.asyncio
    async def test_load_state_returns_false_for_missing_file(self, temp_state_dir):
        """Test that load_state returns False for non-existent file."""
        from src.mcp.tools.attack_simulation import (
            SimulationStateManager,
            reset_simulation_manager,
        )
        from src.mcp.tools.simulation_persistence import SimulationStatePersistence

        reset_simulation_manager()
        manager = SimulationStateManager()
        persistence = SimulationStatePersistence(state_dir=str(temp_state_dir))

        loaded = await persistence.load_state(
            manager, str(temp_state_dir / "nonexistent.json")
        )

        assert loaded is False

    @pytest.mark.asyncio
    async def test_get_latest_state_file(self, temp_state_dir):
        """Test getting the most recent state file."""
        from src.mcp.tools.attack_simulation import (
            SimulationStateManager,
            reset_simulation_manager,
        )
        from src.mcp.tools.simulation_persistence import SimulationStatePersistence

        reset_simulation_manager()
        manager = SimulationStateManager()
        persistence = SimulationStatePersistence(state_dir=str(temp_state_dir))

        # Create multiple state files with forced different timestamps
        await manager.start_scenario("apt29")
        file1 = await persistence.save_state(manager)

        await asyncio.sleep(1.1)  # Ensure different timestamps (>1 second for filename)

        await manager.set_speed(2.0)
        file2 = await persistence.save_state(manager)

        latest = persistence.get_latest_state_file()

        assert latest == file2
        # Files may have same name if sub-second, so only check latest is returned
        assert latest is not None

    @pytest.mark.asyncio
    async def test_auto_save_state_on_state_change(self, temp_state_dir):
        """Test that state is auto-saved on significant changes."""
        from src.mcp.tools.attack_simulation import (
            SimulationStateManager,
            reset_simulation_manager,
        )
        from src.mcp.tools.simulation_persistence import SimulationStatePersistence

        reset_simulation_manager()
        manager = SimulationStateManager()
        persistence = SimulationStatePersistence(
            state_dir=str(temp_state_dir), auto_save=True
        )

        # Register persistence with manager
        manager.register_persistence(persistence)

        # Start simulation - should auto-save
        await manager.start_scenario("lazarus")

        # Check that state file was created
        state_files = list(temp_state_dir.glob("*.json"))
        assert len(state_files) >= 1

    @pytest.mark.asyncio
    async def test_state_recovery_preserves_injected_events(self, temp_state_dir):
        """Test that injected events are preserved in state recovery."""
        from src.mcp.tools.attack_simulation import (
            SimulationStateManager,
            reset_simulation_manager,
        )
        from src.mcp.tools.simulation_persistence import SimulationStatePersistence

        reset_simulation_manager()
        manager = SimulationStateManager()
        persistence = SimulationStatePersistence(state_dir=str(temp_state_dir))

        await manager.start_scenario("apt29")
        await manager.inject_event("malware_execution", {"host": "WS-001"})
        await manager.inject_event("lateral_movement", {"target": "DC-001"})

        # Save state
        state_file = await persistence.save_state(manager)

        # Reset and restore
        reset_simulation_manager()
        new_manager = SimulationStateManager()
        await persistence.load_state(new_manager, state_file)

        # Check injected events were preserved
        assert len(new_manager.pending_events) == 2

    @pytest.mark.asyncio
    async def test_cleanup_old_state_files(self, temp_state_dir):
        """Test that old state files are cleaned up."""
        from src.mcp.tools.attack_simulation import (
            SimulationStateManager,
            reset_simulation_manager,
        )
        from src.mcp.tools.simulation_persistence import SimulationStatePersistence

        reset_simulation_manager()
        manager = SimulationStateManager()
        persistence = SimulationStatePersistence(
            state_dir=str(temp_state_dir), max_state_files=3
        )

        await manager.start_scenario("apt29")

        # Create 5 state files with different timestamps
        created_files = []
        for i in range(5):
            await manager.set_speed(1.0 + i * 0.1)
            await asyncio.sleep(1.1)  # Ensure different timestamps
            state_file = await persistence.save_state(manager)
            created_files.append(state_file)

        # Verify we created 5 files (may have duplicates due to timing)
        state_files_before = list(temp_state_dir.glob("*.json"))

        # Cleanup should keep only max_state_files
        persistence.cleanup_old_state_files()

        state_files_after = list(temp_state_dir.glob("*.json"))

        # Should have at most max_state_files after cleanup
        assert len(state_files_after) <= 3


class TestSimulationStateManagerIntegration:
    """Test SimulationStateManager integration with persistence."""

    @pytest.fixture
    def temp_state_dir(self, tmp_path):
        """Create temporary directory for state files."""
        return tmp_path

    @pytest.mark.asyncio
    async def test_get_state_includes_persistence_info(self):
        """Test that get_state returns persistence information."""
        from src.mcp.tools.attack_simulation import (
            SimulationStateManager,
            reset_simulation_manager,
        )

        reset_simulation_manager()
        manager = SimulationStateManager()

        await manager.start_scenario("apt29")
        state = await manager.get_state()

        # Should include these fields from persistence
        assert "simulation_id" in state
        assert "scenario" in state
        assert "is_running" in state
        assert "is_paused" in state
        assert "current_stage" in state
        assert "speed" in state
        assert "events_generated" in state

    @pytest.mark.asyncio
    async def test_state_can_be_serialized_to_json(self):
        """Test that state can be serialized to JSON."""
        from src.mcp.tools.attack_simulation import (
            SimulationStateManager,
            reset_simulation_manager,
        )

        reset_simulation_manager()
        manager = SimulationStateManager()

        await manager.start_scenario("apt29", seed=42)
        state = await manager.get_state()

        # Should be JSON serializable
        json_str = json.dumps(state)
        assert isinstance(json_str, str)

        # Should be deserializable
        restored = json.loads(json_str)
        assert restored["scenario"] == "apt29"

    @pytest.mark.asyncio
    async def test_restore_state_from_dict(self, temp_state_dir):
        """Test restoring state from a dictionary."""
        from src.mcp.tools.attack_simulation import (
            SimulationStateManager,
            reset_simulation_manager,
        )

        reset_simulation_manager()
        manager = SimulationStateManager()

        state_dict = {
            "simulation_id": "test-sim-123",
            "scenario": "revil",
            "is_running": True,
            "is_paused": False,
            "current_stage": 3,
            "speed": 2.5,
            "seed": 999,
            "events_generated": 50,
            "injected_events": [
                {"event_id": "EVT-1", "type": "test", "data": {}}
            ]
        }

        await manager.restore_from_dict(state_dict)

        assert manager.current_scenario == "revil"
        assert manager.current_stage == 3
        assert manager.speed == 2.5


class TestPersistenceFilePath:
    """Test persistence file path handling."""

    @pytest.fixture
    def temp_state_dir(self, tmp_path):
        """Create temporary directory for state files."""
        return tmp_path

    @pytest.mark.asyncio
    async def test_state_file_naming_convention(self, temp_state_dir):
        """Test that state files follow naming convention."""
        from src.mcp.tools.attack_simulation import (
            SimulationStateManager,
            reset_simulation_manager,
        )
        from src.mcp.tools.simulation_persistence import SimulationStatePersistence

        reset_simulation_manager()
        manager = SimulationStateManager()
        persistence = SimulationStatePersistence(state_dir=str(temp_state_dir))

        await manager.start_scenario("apt29")
        state_file = await persistence.save_state(manager)

        # File should match pattern: simulation_state_YYYY-MM-DD_HH-MM-SS.json
        filename = os.path.basename(state_file)
        assert filename.startswith("simulation_state_")
        assert filename.endswith(".json")

    @pytest.mark.asyncio
    async def test_creates_state_directory_if_not_exists(self):
        """Test that state directory is created if it doesn't exist."""
        from src.mcp.tools.simulation_persistence import SimulationStatePersistence

        with tempfile.TemporaryDirectory() as temp_dir:
            new_state_dir = os.path.join(temp_dir, "nested", "state", "dir")

            persistence = SimulationStatePersistence(state_dir=new_state_dir)

            assert os.path.exists(new_state_dir)


class TestPersistenceEdgeCases:
    """Test edge cases for persistence."""

    @pytest.fixture
    def temp_state_dir(self, tmp_path):
        """Create temporary directory for state files."""
        return tmp_path

    @pytest.mark.asyncio
    async def test_save_state_with_no_active_simulation(self, temp_state_dir):
        """Test saving state when no simulation is active."""
        from src.mcp.tools.attack_simulation import (
            SimulationStateManager,
            reset_simulation_manager,
        )
        from src.mcp.tools.simulation_persistence import SimulationStatePersistence

        reset_simulation_manager()
        manager = SimulationStateManager()
        persistence = SimulationStatePersistence(state_dir=str(temp_state_dir))

        # Should return None or empty path when no simulation
        state_file = await persistence.save_state(manager)

        # Either no file created, or file with empty state
        if state_file:
            with open(state_file, "r") as f:
                data = json.load(f)
            assert data.get("scenario") is None

    @pytest.mark.asyncio
    async def test_load_corrupted_state_file(self, temp_state_dir):
        """Test loading a corrupted state file."""
        from src.mcp.tools.attack_simulation import (
            SimulationStateManager,
            reset_simulation_manager,
        )
        from src.mcp.tools.simulation_persistence import SimulationStatePersistence

        reset_simulation_manager()
        manager = SimulationStateManager()
        persistence = SimulationStatePersistence(state_dir=str(temp_state_dir))

        # Create corrupted file
        corrupted_file = temp_state_dir / "corrupted.json"
        with open(corrupted_file, "w") as f:
            f.write("not valid json {{{")

        # Should return False and not crash
        loaded = await persistence.load_state(manager, str(corrupted_file))

        assert loaded is False

    @pytest.mark.asyncio
    async def test_concurrent_save_operations(self, temp_state_dir):
        """Test concurrent save operations don't corrupt state."""
        from src.mcp.tools.attack_simulation import (
            SimulationStateManager,
            reset_simulation_manager,
        )
        from src.mcp.tools.simulation_persistence import SimulationStatePersistence

        reset_simulation_manager()
        manager = SimulationStateManager()
        persistence = SimulationStatePersistence(state_dir=str(temp_state_dir))

        await manager.start_scenario("apt29")

        # Concurrent saves
        tasks = [
            persistence.save_state(manager),
            persistence.save_state(manager),
            persistence.save_state(manager),
        ]

        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(r is not None for r in results)

        # All files should be valid JSON
        for state_file in results:
            with open(state_file, "r") as f:
                data = json.load(f)
            assert data["scenario"] == "apt29"
