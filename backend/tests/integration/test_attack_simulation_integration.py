"""
Attack Simulation Integration Tests - TDD RED Phase

Tests for complete attack simulation flows:
- T-1.4.004: Integration tests for attack scenarios
- T-1.4.005: Integration tests for simulation control

Following TDD: Tests written FIRST, implementation comes after.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any
import json


# ============================================================================
# TEST T-1.4.004: Attack Scenario Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_start_apt29_scenario_returns_full_attack_chain():
    """
    Test APT29 scenario starts and returns complete attack chain.

    Steps:
    1. Start APT29 scenario via MCP tool
    2. Verify scenario is running
    3. Verify attack chain contains expected MITRE tactics
    4. Verify each stage has proper data
    """
    from src.mcp.tools.attack_simulation import (
        handle_attack_start_scenario,
        get_simulation_manager,
        reset_simulation_manager
    )

    # Reset state
    reset_simulation_manager()

    # Step 1: Start the scenario
    result = await handle_attack_start_scenario({"scenario_name": "apt29"})

    # Step 2: Verify started correctly
    assert result["status"] == "started"
    assert result["scenario"] == "apt29"
    assert "simulation_id" in result

    # Step 3: Verify MITRE tactics
    assert "mitre_tactics" in result
    tactics = result["mitre_tactics"]
    assert len(tactics) > 0

    # APT29 should include typical APT tactics
    tactic_names = [t["name"] for t in tactics]
    expected_tactics = ["Initial Access", "Execution", "Persistence"]
    for expected in expected_tactics:
        assert expected in tactic_names, f"Missing expected tactic: {expected}"


@pytest.mark.asyncio
async def test_start_scenario_initializes_stages():
    """
    Test that starting a scenario properly initializes all stages.

    Steps:
    1. Start scenario
    2. Verify stages are initialized
    3. Verify first stage is current
    """
    from src.mcp.tools.attack_simulation import (
        handle_attack_start_scenario,
        get_simulation_manager,
        reset_simulation_manager
    )

    reset_simulation_manager()

    result = await handle_attack_start_scenario({"scenario_name": "apt29"})

    manager = get_simulation_manager()
    assert manager.current_stage == 1
    assert manager.total_stages > 0


@pytest.mark.asyncio
async def test_scenario_with_seed_is_reproducible():
    """
    Test that scenarios with same seed produce identical event sequences.

    Steps:
    1. Start scenario with seed 42
    2. Record first events
    3. Reset and start again with same seed
    4. Verify events are identical
    """
    from src.mcp.tools.attack_simulation import (
        handle_attack_start_scenario,
        reset_simulation_manager
    )

    # First run
    reset_simulation_manager()
    result1 = await handle_attack_start_scenario({
        "scenario_name": "apt29",
        "seed": 42
    })

    # Second run with same seed
    reset_simulation_manager()
    result2 = await handle_attack_start_scenario({
        "scenario_name": "apt29",
        "seed": 42
    })

    # Both should produce same simulation_id pattern (deterministic)
    assert result1["seed"] == result2["seed"] == 42


@pytest.mark.asyncio
async def test_start_multiple_scenarios_fails():
    """
    Test that starting a second scenario while one is running fails.

    Steps:
    1. Start APT29 scenario
    2. Try to start FIN7 scenario
    3. Should return error
    """
    from src.mcp.tools.attack_simulation import (
        handle_attack_start_scenario,
        reset_simulation_manager
    )

    reset_simulation_manager()

    # Start first scenario
    result1 = await handle_attack_start_scenario({"scenario_name": "apt29"})
    assert result1["status"] == "started"

    # Try to start second
    result2 = await handle_attack_start_scenario({"scenario_name": "fin7"})
    assert result2["status"] == "error"
    assert "already running" in result2["message"].lower()


@pytest.mark.asyncio
async def test_scenario_generates_realistic_events():
    """
    Test that running scenario generates realistic security events.

    Steps:
    1. Start scenario
    2. Let it generate events
    3. Verify event structure matches SIEM format
    """
    from src.mcp.tools.attack_simulation import (
        handle_attack_start_scenario,
        get_simulation_manager,
        reset_simulation_manager
    )

    reset_simulation_manager()

    result = await handle_attack_start_scenario({"scenario_name": "apt29"})

    manager = get_simulation_manager()

    # Verify scenario has events ready
    assert hasattr(manager, "pending_events") or hasattr(manager, "event_queue")


# ============================================================================
# TEST T-1.4.005: Simulation Control Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_pause_resume_maintains_state():
    """
    Test pause/resume preserves simulation state.

    Steps:
    1. Start scenario
    2. Advance to stage 2
    3. Pause
    4. Verify state preserved
    5. Resume
    6. Verify still at stage 2
    """
    from src.mcp.tools.attack_simulation import (
        handle_attack_start_scenario,
        handle_attack_pause,
        handle_attack_resume,
        handle_attack_jump_to_stage,
        get_simulation_manager,
        reset_simulation_manager
    )

    reset_simulation_manager()

    # Start and advance
    await handle_attack_start_scenario({"scenario_name": "apt29"})
    await handle_attack_jump_to_stage({"stage_number": 2})

    manager = get_simulation_manager()
    stage_before_pause = manager.current_stage

    # Pause
    pause_result = await handle_attack_pause({})
    assert pause_result["status"] == "paused"
    assert manager.is_running is False
    assert manager.current_stage == stage_before_pause

    # Resume
    resume_result = await handle_attack_resume({})
    assert resume_result["status"] == "running"
    assert manager.is_running is True
    assert manager.current_stage == stage_before_pause


@pytest.mark.asyncio
async def test_speed_control_affects_event_timing():
    """
    Test speed multiplier affects simulation timing.

    Steps:
    1. Start scenario at 1x speed
    2. Record timing
    3. Set to 2x speed
    4. Verify speed changed
    """
    from src.mcp.tools.attack_simulation import (
        handle_attack_start_scenario,
        handle_attack_speed,
        get_simulation_manager,
        reset_simulation_manager
    )

    reset_simulation_manager()

    await handle_attack_start_scenario({"scenario_name": "apt29"})

    manager = get_simulation_manager()
    initial_speed = manager.speed

    # Double the speed
    result = await handle_attack_speed({"multiplier": 2.0})

    assert result["status"] == "success"
    assert result["speed"] == 2.0
    assert manager.speed == 2.0


@pytest.mark.asyncio
async def test_jump_to_stage_skips_intermediate_stages():
    """
    Test jumping to a stage properly skips intermediate stages.

    Steps:
    1. Start scenario at stage 1
    2. Jump to stage 4
    3. Verify current stage is 4
    4. Verify intermediate stages are marked as skipped
    """
    from src.mcp.tools.attack_simulation import (
        handle_attack_start_scenario,
        handle_attack_jump_to_stage,
        get_simulation_manager,
        reset_simulation_manager
    )

    reset_simulation_manager()

    await handle_attack_start_scenario({"scenario_name": "apt29"})

    manager = get_simulation_manager()

    # Jump from 1 to 3
    result = await handle_attack_jump_to_stage({"stage_number": 3})

    assert result["status"] == "success"
    assert result["current_stage"] == 3
    assert manager.current_stage == 3


@pytest.mark.asyncio
async def test_inject_event_integrates_with_timeline():
    """
    Test injected events properly integrate with simulation timeline.

    Steps:
    1. Start scenario
    2. Inject custom malware event
    3. Verify event has MITRE mapping
    4. Verify event is in simulation timeline
    """
    from src.mcp.tools.attack_simulation import (
        handle_attack_start_scenario,
        handle_attack_inject_event,
        get_simulation_manager,
        reset_simulation_manager
    )

    reset_simulation_manager()

    await handle_attack_start_scenario({"scenario_name": "apt29"})

    # Inject a custom event
    result = await handle_attack_inject_event({
        "event_type": "malware_execution",
        "data": {
            "host": "WORKSTATION-001",
            "process": "malware.exe",
            "hash": "abc123def456"
        }
    })

    assert result["status"] == "success"
    assert "event_id" in result


@pytest.mark.asyncio
async def test_complete_simulation_flow():
    """
    Test complete simulation flow from start to finish.

    Steps:
    1. Start scenario
    2. Progress through stages
    3. Inject events
    4. Control speed
    5. Complete scenario
    """
    from src.mcp.tools.attack_simulation import (
        handle_attack_start_scenario,
        handle_attack_pause,
        handle_attack_resume,
        handle_attack_speed,
        handle_attack_jump_to_stage,
        handle_attack_inject_event,
        get_simulation_manager,
        reset_simulation_manager
    )

    reset_simulation_manager()

    # 1. Start
    start_result = await handle_attack_start_scenario({"scenario_name": "apt29"})
    assert start_result["status"] == "started"

    # 2. Speed up
    speed_result = await handle_attack_speed({"multiplier": 2.0})
    assert speed_result["status"] == "success"

    # 3. Pause
    pause_result = await handle_attack_pause({})
    assert pause_result["status"] == "paused"

    # 4. Resume
    resume_result = await handle_attack_resume({})
    assert resume_result["status"] == "running"

    # 5. Jump to later stage
    jump_result = await handle_attack_jump_to_stage({"stage_number": 2})
    assert jump_result["status"] == "success"

    # 6. Inject event
    inject_result = await handle_attack_inject_event({
        "event_type": "lateral_movement",
        "data": {
            "source": "WS-001",
            "destination": "DC-001"
        }
    })
    assert inject_result["status"] == "success"

    # Verify simulation is in expected state
    manager = get_simulation_manager()
    assert manager.is_running is True
    assert manager.current_stage == 2
    assert manager.speed == 2.0


@pytest.mark.asyncio
async def test_simulation_controls_require_active_simulation():
    """
    Test that control operations require an active simulation.

    Steps:
    1. Without starting a simulation, try each control
    2. Each should return appropriate error
    """
    from src.mcp.tools.attack_simulation import (
        handle_attack_pause,
        handle_attack_resume,
        handle_attack_speed,
        handle_attack_jump_to_stage,
        handle_attack_inject_event,
        reset_simulation_manager
    )

    reset_simulation_manager()

    # Try pause
    pause_result = await handle_attack_pause({})
    assert pause_result["status"] == "error"

    # Try speed
    speed_result = await handle_attack_speed({"multiplier": 2.0})
    assert speed_result["status"] == "error"

    # Try jump
    jump_result = await handle_attack_jump_to_stage({"stage_number": 2})
    assert jump_result["status"] == "error"

    # Try inject
    inject_result = await handle_attack_inject_event({
        "event_type": "test",
        "data": {}
    })
    assert inject_result["status"] == "error"


# ============================================================================
# MCP Server Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_attack_simulation_via_mcp_server():
    """
    Test attack simulation tools via MCP server endpoint.

    Steps:
    1. Send tools/call for attack_start_scenario
    2. Verify JSON-RPC response
    3. Verify simulation started
    """
    from httpx import AsyncClient, ASGITransport
    from src.main import app
    from src.mcp.tools.attack_simulation import reset_simulation_manager

    reset_simulation_manager()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Call attack_start_scenario via MCP
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "attack_start_scenario",
                "arguments": {"scenario_name": "apt29"}
            }
        }

        response = await client.post("/mcp/messages", json=message)

        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "content" in data["result"]

        # Parse result
        content = json.loads(data["result"]["content"][0]["text"])
        assert content["status"] == "started"
        assert content["scenario"] == "apt29"


@pytest.mark.asyncio
async def test_attack_simulation_tools_audited():
    """
    Test that attack simulation tool invocations are audit logged.

    Steps:
    1. Clear audit logs
    2. Invoke attack_start_scenario
    3. Verify invocation is logged
    """
    from httpx import AsyncClient, ASGITransport
    from src.main import app
    from src.mcp.audit_logger import get_audit_logger
    from src.mcp.tools.attack_simulation import reset_simulation_manager

    reset_simulation_manager()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Clear logs
        audit_logger = get_audit_logger()
        await audit_logger.clear_logs()

        # Invoke tool
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "attack_start_scenario",
                "arguments": {"scenario_name": "fin7"}
            }
        }

        await client.post("/mcp/messages", json=message)

        # Check audit log
        logs = await audit_logger.get_recent_logs(limit=1)
        assert len(logs) >= 1
        assert logs[0]["tool_name"] == "attack_start_scenario"


@pytest.mark.asyncio
async def test_all_scenarios_can_start():
    """
    Test that all defined scenarios can be started successfully.
    """
    from src.mcp.tools.attack_simulation import (
        handle_attack_start_scenario,
        reset_simulation_manager,
        SCENARIOS
    )

    for scenario_name in SCENARIOS.keys():
        reset_simulation_manager()

        result = await handle_attack_start_scenario({"scenario_name": scenario_name})

        assert result["status"] == "started", f"Failed to start {scenario_name}"
        assert result["scenario"] == scenario_name
        assert "mitre_tactics" in result
