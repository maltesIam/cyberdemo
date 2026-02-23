"""
Attack Simulation MCP Tools Unit Tests - TDD RED Phase

Tests for the attack simulation control tools:
- attack_start_scenario (REQ-002-002-001)
- attack_pause/resume (REQ-002-002-002)
- attack_speed (REQ-002-002-003)
- attack_jump_to_stage (REQ-002-002-004)
- attack_inject_event (REQ-002-002-005)

Following TDD: Tests written FIRST, implementation comes after.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json


# =============================================================================
# TEST: Simulation State Manager
# =============================================================================

class TestSimulationStateManager:
    """Unit tests for the simulation state manager."""

    def test_state_manager_initialization(self):
        """
        GIVEN simulation state manager
        WHEN initialized
        THEN it should be ready to manage simulation state
        """
        from src.mcp.tools.attack_simulation import SimulationStateManager

        manager = SimulationStateManager()

        assert manager is not None
        assert manager.current_scenario is None
        assert manager.is_running is False

    @pytest.mark.asyncio
    async def test_start_scenario_updates_state(self):
        """
        GIVEN a stopped simulation
        WHEN attack_start_scenario is called
        THEN the simulation state should be updated
        """
        from src.mcp.tools.attack_simulation import SimulationStateManager

        manager = SimulationStateManager()

        await manager.start_scenario("apt29")

        assert manager.current_scenario == "apt29"
        assert manager.is_running is True

    @pytest.mark.asyncio
    async def test_pause_updates_state(self):
        """
        GIVEN a running simulation
        WHEN pause is called
        THEN is_running should be False but scenario should remain
        """
        from src.mcp.tools.attack_simulation import SimulationStateManager

        manager = SimulationStateManager()
        await manager.start_scenario("apt29")

        await manager.pause()

        assert manager.is_running is False
        assert manager.current_scenario == "apt29"

    @pytest.mark.asyncio
    async def test_resume_updates_state(self):
        """
        GIVEN a paused simulation
        WHEN resume is called
        THEN is_running should be True
        """
        from src.mcp.tools.attack_simulation import SimulationStateManager

        manager = SimulationStateManager()
        await manager.start_scenario("apt29")
        await manager.pause()

        await manager.resume()

        assert manager.is_running is True


# =============================================================================
# TEST: attack_start_scenario Tool (REQ-002-002-001 / UT-024)
# =============================================================================

class TestAttackStartScenarioTool:
    """Unit tests for attack_start_scenario MCP tool."""

    @pytest.mark.asyncio
    async def test_tool_schema_has_required_fields(self):
        """
        GIVEN the attack_start_scenario tool definition
        WHEN we inspect its schema
        THEN it must have name, description, and inputSchema
        """
        from src.mcp.tools.attack_simulation import ATTACK_SIMULATION_TOOLS

        tool = next(
            (t for t in ATTACK_SIMULATION_TOOLS if t["name"] == "attack_start_scenario"),
            None
        )

        assert tool is not None, "attack_start_scenario tool not found"
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool

    @pytest.mark.asyncio
    async def test_tool_requires_scenario_name(self):
        """
        GIVEN the attack_start_scenario tool
        WHEN we check its input schema
        THEN scenario_name must be required
        """
        from src.mcp.tools.attack_simulation import ATTACK_SIMULATION_TOOLS

        tool = next(
            (t for t in ATTACK_SIMULATION_TOOLS if t["name"] == "attack_start_scenario"),
            None
        )

        assert "required" in tool["inputSchema"]
        assert "scenario_name" in tool["inputSchema"]["required"]

    @pytest.mark.asyncio
    async def test_start_scenario_with_valid_name(self):
        """
        GIVEN a valid scenario name
        WHEN attack_start_scenario is invoked
        THEN it should start the scenario and return status
        """
        from src.mcp.tools.attack_simulation import handle_attack_start_scenario, reset_simulation_manager

        reset_simulation_manager()
        args = {"scenario_name": "apt29"}
        result = await handle_attack_start_scenario(args)

        assert "status" in result
        assert result["status"] == "started"
        assert "scenario" in result
        assert result["scenario"] == "apt29"
        assert "simulation_id" in result

    @pytest.mark.asyncio
    async def test_start_scenario_with_seed(self):
        """
        GIVEN a scenario with seed parameter
        WHEN attack_start_scenario is invoked
        THEN it should use the provided seed for reproducibility
        """
        from src.mcp.tools.attack_simulation import handle_attack_start_scenario, reset_simulation_manager

        reset_simulation_manager()
        args = {"scenario_name": "apt29", "seed": 42}
        result = await handle_attack_start_scenario(args)

        assert result["status"] == "started"
        assert result.get("seed") == 42

    @pytest.mark.asyncio
    async def test_start_scenario_returns_mitre_info(self):
        """
        GIVEN a valid scenario
        WHEN attack_start_scenario is invoked
        THEN it should return MITRE ATT&CK information
        """
        from src.mcp.tools.attack_simulation import handle_attack_start_scenario, reset_simulation_manager

        reset_simulation_manager()
        args = {"scenario_name": "apt29"}
        result = await handle_attack_start_scenario(args)

        assert "mitre_tactics" in result
        assert isinstance(result["mitre_tactics"], list)
        assert len(result["mitre_tactics"]) > 0

    @pytest.mark.asyncio
    async def test_start_invalid_scenario_returns_error(self):
        """
        GIVEN an invalid scenario name
        WHEN attack_start_scenario is invoked
        THEN it should return an error
        """
        from src.mcp.tools.attack_simulation import handle_attack_start_scenario, reset_simulation_manager

        reset_simulation_manager()
        args = {"scenario_name": "nonexistent_scenario"}
        result = await handle_attack_start_scenario(args)

        assert result["status"] == "error"
        assert "message" in result

    @pytest.mark.asyncio
    async def test_start_scenario_without_name_raises_error(self):
        """
        GIVEN no scenario_name
        WHEN attack_start_scenario is invoked
        THEN it should raise ValueError
        """
        from src.mcp.tools.attack_simulation import handle_attack_start_scenario, reset_simulation_manager

        reset_simulation_manager()
        args = {}
        with pytest.raises(ValueError, match="scenario_name is required"):
            await handle_attack_start_scenario(args)


# =============================================================================
# TEST: attack_pause/resume Tools (REQ-002-002-002 / UT-025)
# =============================================================================

class TestAttackPauseResumeTool:
    """Unit tests for attack_pause and attack_resume MCP tools."""

    @pytest.mark.asyncio
    async def test_pause_tool_exists(self):
        """
        GIVEN the attack_pause tool
        WHEN we check the tool list
        THEN it should exist
        """
        from src.mcp.tools.attack_simulation import ATTACK_SIMULATION_TOOLS

        tool = next(
            (t for t in ATTACK_SIMULATION_TOOLS if t["name"] == "attack_pause"),
            None
        )

        assert tool is not None

    @pytest.mark.asyncio
    async def test_resume_tool_exists(self):
        """
        GIVEN the attack_resume tool
        WHEN we check the tool list
        THEN it should exist
        """
        from src.mcp.tools.attack_simulation import ATTACK_SIMULATION_TOOLS

        tool = next(
            (t for t in ATTACK_SIMULATION_TOOLS if t["name"] == "attack_resume"),
            None
        )

        assert tool is not None

    @pytest.mark.asyncio
    async def test_pause_running_simulation(self):
        """
        GIVEN a running simulation
        WHEN attack_pause is invoked
        THEN it should pause the simulation
        """
        from src.mcp.tools.attack_simulation import (
            handle_attack_start_scenario,
            handle_attack_pause,
            reset_simulation_manager
        )

        # Reset and start a simulation first
        reset_simulation_manager()
        await handle_attack_start_scenario({"scenario_name": "apt29"})

        result = await handle_attack_pause({})

        assert result["status"] == "paused"

    @pytest.mark.asyncio
    async def test_resume_paused_simulation(self):
        """
        GIVEN a paused simulation
        WHEN attack_resume is invoked
        THEN it should resume the simulation
        """
        from src.mcp.tools.attack_simulation import (
            handle_attack_start_scenario,
            handle_attack_pause,
            handle_attack_resume,
            reset_simulation_manager
        )

        # Reset, start and pause
        reset_simulation_manager()
        await handle_attack_start_scenario({"scenario_name": "apt29"})
        await handle_attack_pause({})

        result = await handle_attack_resume({})

        assert result["status"] == "running"

    @pytest.mark.asyncio
    async def test_pause_when_no_simulation_returns_error(self):
        """
        GIVEN no active simulation
        WHEN attack_pause is invoked
        THEN it should return an error status
        """
        from src.mcp.tools.attack_simulation import (
            handle_attack_pause,
            get_simulation_manager,
            reset_simulation_manager
        )

        # Reset to ensure no simulation
        reset_simulation_manager()

        result = await handle_attack_pause({})

        assert result["status"] == "error"
        assert "no active simulation" in result["message"].lower()


# =============================================================================
# TEST: attack_speed Tool (REQ-002-002-003 / UT-026)
# =============================================================================

class TestAttackSpeedTool:
    """Unit tests for attack_speed MCP tool."""

    @pytest.mark.asyncio
    async def test_tool_schema_has_multiplier(self):
        """
        GIVEN the attack_speed tool
        WHEN we check its input schema
        THEN multiplier should be a required parameter
        """
        from src.mcp.tools.attack_simulation import ATTACK_SIMULATION_TOOLS

        tool = next(
            (t for t in ATTACK_SIMULATION_TOOLS if t["name"] == "attack_speed"),
            None
        )

        assert tool is not None
        assert "required" in tool["inputSchema"]
        assert "multiplier" in tool["inputSchema"]["required"]

    @pytest.mark.asyncio
    async def test_set_speed_valid_multiplier(self):
        """
        GIVEN a valid speed multiplier
        WHEN attack_speed is invoked
        THEN it should update the simulation speed
        """
        from src.mcp.tools.attack_simulation import (
            handle_attack_start_scenario,
            handle_attack_speed,
            reset_simulation_manager
        )

        reset_simulation_manager()
        await handle_attack_start_scenario({"scenario_name": "apt29"})

        result = await handle_attack_speed({"multiplier": 2.0})

        assert result["status"] == "success"
        assert result["speed"] == 2.0

    @pytest.mark.asyncio
    async def test_speed_multiplier_range(self):
        """
        GIVEN multipliers outside valid range (0.5-4.0)
        WHEN attack_speed is invoked
        THEN it should return error for invalid values
        """
        from src.mcp.tools.attack_simulation import (
            handle_attack_start_scenario,
            handle_attack_speed,
            reset_simulation_manager
        )

        reset_simulation_manager()
        await handle_attack_start_scenario({"scenario_name": "apt29"})

        # Too slow
        result = await handle_attack_speed({"multiplier": 0.1})
        assert result["status"] == "error"

        # Too fast
        result = await handle_attack_speed({"multiplier": 5.0})
        assert result["status"] == "error"


# =============================================================================
# TEST: attack_jump_to_stage Tool (REQ-002-002-004 / UT-027)
# =============================================================================

class TestAttackJumpToStageTool:
    """Unit tests for attack_jump_to_stage MCP tool."""

    @pytest.mark.asyncio
    async def test_tool_schema_has_stage_number(self):
        """
        GIVEN the attack_jump_to_stage tool
        WHEN we check its input schema
        THEN stage_number should be required
        """
        from src.mcp.tools.attack_simulation import ATTACK_SIMULATION_TOOLS

        tool = next(
            (t for t in ATTACK_SIMULATION_TOOLS if t["name"] == "attack_jump_to_stage"),
            None
        )

        assert tool is not None
        assert "required" in tool["inputSchema"]
        assert "stage_number" in tool["inputSchema"]["required"]

    @pytest.mark.asyncio
    async def test_jump_to_valid_stage(self):
        """
        GIVEN a valid stage number
        WHEN attack_jump_to_stage is invoked
        THEN it should jump to that stage
        """
        from src.mcp.tools.attack_simulation import (
            handle_attack_start_scenario,
            handle_attack_jump_to_stage,
            reset_simulation_manager
        )

        reset_simulation_manager()
        await handle_attack_start_scenario({"scenario_name": "apt29"})

        result = await handle_attack_jump_to_stage({"stage_number": 3})

        assert result["status"] == "success"
        assert result["current_stage"] == 3

    @pytest.mark.asyncio
    async def test_jump_to_invalid_stage_returns_error(self):
        """
        GIVEN an invalid stage number
        WHEN attack_jump_to_stage is invoked
        THEN it should return an error
        """
        from src.mcp.tools.attack_simulation import (
            handle_attack_start_scenario,
            handle_attack_jump_to_stage,
            reset_simulation_manager
        )

        reset_simulation_manager()
        await handle_attack_start_scenario({"scenario_name": "apt29"})

        result = await handle_attack_jump_to_stage({"stage_number": 999})

        assert result["status"] == "error"


# =============================================================================
# TEST: attack_inject_event Tool (REQ-002-002-005 / UT-028)
# =============================================================================

class TestAttackInjectEventTool:
    """Unit tests for attack_inject_event MCP tool."""

    @pytest.mark.asyncio
    async def test_tool_schema_has_event_type(self):
        """
        GIVEN the attack_inject_event tool
        WHEN we check its input schema
        THEN event_type should be required
        """
        from src.mcp.tools.attack_simulation import ATTACK_SIMULATION_TOOLS

        tool = next(
            (t for t in ATTACK_SIMULATION_TOOLS if t["name"] == "attack_inject_event"),
            None
        )

        assert tool is not None
        assert "required" in tool["inputSchema"]
        assert "event_type" in tool["inputSchema"]["required"]

    @pytest.mark.asyncio
    async def test_inject_valid_event(self):
        """
        GIVEN a valid event to inject
        WHEN attack_inject_event is invoked
        THEN it should inject the event into the simulation
        """
        from src.mcp.tools.attack_simulation import (
            handle_attack_start_scenario,
            handle_attack_inject_event,
            reset_simulation_manager
        )

        reset_simulation_manager()
        await handle_attack_start_scenario({"scenario_name": "apt29"})

        result = await handle_attack_inject_event({
            "event_type": "malware_execution",
            "data": {
                "host": "WS-HR-001",
                "process": "evil.exe",
                "hash": "abc123"
            }
        })

        assert result["status"] == "success"
        assert "event_id" in result

    @pytest.mark.asyncio
    async def test_inject_event_includes_mitre(self):
        """
        GIVEN an injected event with MITRE mapping
        WHEN attack_inject_event is invoked
        THEN the event should include MITRE tactic/technique
        """
        from src.mcp.tools.attack_simulation import (
            handle_attack_start_scenario,
            handle_attack_inject_event,
            reset_simulation_manager
        )

        reset_simulation_manager()
        await handle_attack_start_scenario({"scenario_name": "apt29"})

        result = await handle_attack_inject_event({
            "event_type": "process_execution",
            "data": {"process": "powershell.exe"}
        })

        assert "mitre_tactic" in result or "mitre_technique" in result


# =============================================================================
# TEST: Tool Registration
# =============================================================================

class TestAttackSimulationToolsRegistration:
    """Tests that attack simulation tools are properly registered."""

    def test_all_attack_simulation_tools_registered(self):
        """
        GIVEN the MCP tools registry
        WHEN we get all tools
        THEN attack simulation tools should be present
        """
        from src.mcp.tools import get_all_tools

        tools = get_all_tools()
        tool_names = {t["name"] for t in tools}

        expected_tools = {
            "attack_start_scenario",
            "attack_pause",
            "attack_resume",
            "attack_speed",
            "attack_jump_to_stage",
            "attack_inject_event",
        }

        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Missing tool: {tool_name}"

    def test_all_attack_simulation_handlers_registered(self):
        """
        GIVEN the MCP tool handlers
        WHEN we get all handlers
        THEN attack simulation handlers should be present
        """
        from src.mcp.tools import get_tool_handlers

        handlers = get_tool_handlers()

        expected_handlers = [
            "attack_start_scenario",
            "attack_pause",
            "attack_resume",
            "attack_speed",
            "attack_jump_to_stage",
            "attack_inject_event",
        ]

        for handler_name in expected_handlers:
            assert handler_name in handlers, f"Missing handler: {handler_name}"
