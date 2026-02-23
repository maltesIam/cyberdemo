"""
Agent Orchestration MCP Tools Unit Tests - TDD RED Phase

Tests for the agent orchestration tools that allow the product to invoke
agent analysis capabilities:
- agent_explain_decision (REQ-001-003-005)
- agent_correlate_events (REQ-001-003-006)

Following TDD: Tests written FIRST, implementation comes after.
"""

import pytest
from typing import Dict, Any
from unittest.mock import AsyncMock, patch, MagicMock
import json


# =============================================================================
# TEST: agent_explain_decision Tool (REQ-001-003-005 / UT-016)
# =============================================================================

class TestAgentExplainDecisionTool:
    """Unit tests for agent_explain_decision MCP tool."""

    @pytest.mark.asyncio
    async def test_tool_schema_has_required_fields(self):
        """
        GIVEN the agent_explain_decision tool definition
        WHEN we inspect its schema
        THEN it must have name, description, and inputSchema
        """
        from src.mcp.tools.agent_orchestration import AGENT_ORCHESTRATION_TOOLS

        tool = next(
            (t for t in AGENT_ORCHESTRATION_TOOLS if t["name"] == "agent_explain_decision"),
            None
        )

        assert tool is not None, "agent_explain_decision tool not found"
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool
        assert tool["inputSchema"]["type"] == "object"

    @pytest.mark.asyncio
    async def test_tool_requires_decision_id(self):
        """
        GIVEN the agent_explain_decision tool
        WHEN we check its input schema
        THEN decision_id must be a required parameter
        """
        from src.mcp.tools.agent_orchestration import AGENT_ORCHESTRATION_TOOLS

        tool = next(
            (t for t in AGENT_ORCHESTRATION_TOOLS if t["name"] == "agent_explain_decision"),
            None
        )

        assert "required" in tool["inputSchema"]
        assert "decision_id" in tool["inputSchema"]["required"]

    @pytest.mark.asyncio
    async def test_explain_decision_with_valid_decision_id(self):
        """
        GIVEN a valid decision_id
        WHEN agent_explain_decision is invoked
        THEN it should return the reasoning chain for that decision
        """
        from src.mcp.tools.agent_orchestration import handle_agent_explain_decision

        args = {"decision_id": "DEC-001"}
        result = await handle_agent_explain_decision(args)

        assert "decision_id" in result
        assert result["decision_id"] == "DEC-001"
        assert "reasoning_chain" in result
        assert isinstance(result["reasoning_chain"], list)
        assert len(result["reasoning_chain"]) > 0
        assert "confidence" in result
        assert result["confidence"] in ["high", "medium", "low"]

    @pytest.mark.asyncio
    async def test_explain_decision_returns_factors(self):
        """
        GIVEN a valid decision_id
        WHEN agent_explain_decision is invoked
        THEN it should return the factors that influenced the decision
        """
        from src.mcp.tools.agent_orchestration import handle_agent_explain_decision

        args = {"decision_id": "DEC-001"}
        result = await handle_agent_explain_decision(args)

        assert "factors" in result
        assert isinstance(result["factors"], list)
        # Each factor should have weight and description
        for factor in result["factors"]:
            assert "name" in factor
            assert "weight" in factor
            assert "description" in factor

    @pytest.mark.asyncio
    async def test_explain_decision_returns_alternative_actions(self):
        """
        GIVEN a valid decision_id
        WHEN agent_explain_decision is invoked
        THEN it should return alternative actions that were considered
        """
        from src.mcp.tools.agent_orchestration import handle_agent_explain_decision

        args = {"decision_id": "DEC-001"}
        result = await handle_agent_explain_decision(args)

        assert "alternatives_considered" in result
        assert isinstance(result["alternatives_considered"], list)

    @pytest.mark.asyncio
    async def test_explain_decision_without_decision_id_raises_error(self):
        """
        GIVEN no decision_id
        WHEN agent_explain_decision is invoked
        THEN it should raise ValueError
        """
        from src.mcp.tools.agent_orchestration import handle_agent_explain_decision

        args = {}
        with pytest.raises(ValueError, match="decision_id is required"):
            await handle_agent_explain_decision(args)

    @pytest.mark.asyncio
    async def test_explain_decision_with_unknown_id_returns_not_found(self):
        """
        GIVEN an unknown decision_id
        WHEN agent_explain_decision is invoked
        THEN it should return a not found response
        """
        from src.mcp.tools.agent_orchestration import handle_agent_explain_decision

        args = {"decision_id": "UNKNOWN-999"}
        result = await handle_agent_explain_decision(args)

        assert "status" in result
        assert result["status"] == "not_found"
        assert "message" in result

    @pytest.mark.asyncio
    async def test_explain_decision_includes_timestamp(self):
        """
        GIVEN a valid decision_id
        WHEN agent_explain_decision is invoked
        THEN it should include the decision timestamp
        """
        from src.mcp.tools.agent_orchestration import handle_agent_explain_decision

        args = {"decision_id": "DEC-001"}
        result = await handle_agent_explain_decision(args)

        assert "decision_timestamp" in result


# =============================================================================
# TEST: agent_correlate_events Tool (REQ-001-003-006 / UT-017)
# =============================================================================

class TestAgentCorrelateEventsTool:
    """Unit tests for agent_correlate_events MCP tool."""

    @pytest.mark.asyncio
    async def test_tool_schema_has_required_fields(self):
        """
        GIVEN the agent_correlate_events tool definition
        WHEN we inspect its schema
        THEN it must have name, description, and inputSchema
        """
        from src.mcp.tools.agent_orchestration import AGENT_ORCHESTRATION_TOOLS

        tool = next(
            (t for t in AGENT_ORCHESTRATION_TOOLS if t["name"] == "agent_correlate_events"),
            None
        )

        assert tool is not None, "agent_correlate_events tool not found"
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool

    @pytest.mark.asyncio
    async def test_tool_requires_event_ids(self):
        """
        GIVEN the agent_correlate_events tool
        WHEN we check its input schema
        THEN event_ids must be a required parameter (array of strings)
        """
        from src.mcp.tools.agent_orchestration import AGENT_ORCHESTRATION_TOOLS

        tool = next(
            (t for t in AGENT_ORCHESTRATION_TOOLS if t["name"] == "agent_correlate_events"),
            None
        )

        assert "required" in tool["inputSchema"]
        assert "event_ids" in tool["inputSchema"]["required"]
        assert tool["inputSchema"]["properties"]["event_ids"]["type"] == "array"

    @pytest.mark.asyncio
    async def test_correlate_events_with_valid_event_ids(self):
        """
        GIVEN a list of valid event_ids
        WHEN agent_correlate_events is invoked
        THEN it should return correlation results
        """
        from src.mcp.tools.agent_orchestration import handle_agent_correlate_events

        args = {"event_ids": ["EVT-001", "EVT-002", "EVT-003"]}
        result = await handle_agent_correlate_events(args)

        assert "correlations" in result
        assert isinstance(result["correlations"], list)
        assert "correlation_score" in result
        assert 0 <= result["correlation_score"] <= 1.0

    @pytest.mark.asyncio
    async def test_correlate_events_returns_common_entities(self):
        """
        GIVEN a list of event_ids
        WHEN agent_correlate_events is invoked
        THEN it should return common entities found across events
        """
        from src.mcp.tools.agent_orchestration import handle_agent_correlate_events

        args = {"event_ids": ["EVT-001", "EVT-002"]}
        result = await handle_agent_correlate_events(args)

        assert "common_entities" in result
        assert isinstance(result["common_entities"], list)

    @pytest.mark.asyncio
    async def test_correlate_events_returns_timeline(self):
        """
        GIVEN a list of event_ids
        WHEN agent_correlate_events is invoked
        THEN it should return events in chronological order (timeline)
        """
        from src.mcp.tools.agent_orchestration import handle_agent_correlate_events

        args = {"event_ids": ["EVT-001", "EVT-002", "EVT-003"]}
        result = await handle_agent_correlate_events(args)

        assert "timeline" in result
        assert isinstance(result["timeline"], list)
        # Timeline should be sorted chronologically
        if len(result["timeline"]) > 1:
            for i in range(len(result["timeline"]) - 1):
                assert result["timeline"][i]["timestamp"] <= result["timeline"][i + 1]["timestamp"]

    @pytest.mark.asyncio
    async def test_correlate_events_returns_attack_pattern(self):
        """
        GIVEN a list of event_ids
        WHEN agent_correlate_events is invoked
        THEN it should identify potential attack patterns (MITRE ATT&CK)
        """
        from src.mcp.tools.agent_orchestration import handle_agent_correlate_events

        args = {"event_ids": ["EVT-001", "EVT-002"]}
        result = await handle_agent_correlate_events(args)

        assert "attack_patterns" in result
        assert isinstance(result["attack_patterns"], list)
        # Each pattern should have MITRE tactic/technique info
        for pattern in result["attack_patterns"]:
            assert "tactic_id" in pattern or "technique_id" in pattern

    @pytest.mark.asyncio
    async def test_correlate_events_without_event_ids_raises_error(self):
        """
        GIVEN no event_ids
        WHEN agent_correlate_events is invoked
        THEN it should raise ValueError
        """
        from src.mcp.tools.agent_orchestration import handle_agent_correlate_events

        args = {}
        with pytest.raises(ValueError, match="event_ids is required"):
            await handle_agent_correlate_events(args)

    @pytest.mark.asyncio
    async def test_correlate_events_with_empty_array_raises_error(self):
        """
        GIVEN an empty event_ids array
        WHEN agent_correlate_events is invoked
        THEN it should raise ValueError
        """
        from src.mcp.tools.agent_orchestration import handle_agent_correlate_events

        args = {"event_ids": []}
        with pytest.raises(ValueError, match="at least one event_id"):
            await handle_agent_correlate_events(args)

    @pytest.mark.asyncio
    async def test_correlate_events_with_single_event(self):
        """
        GIVEN a single event_id
        WHEN agent_correlate_events is invoked
        THEN it should return event info without correlations
        """
        from src.mcp.tools.agent_orchestration import handle_agent_correlate_events

        args = {"event_ids": ["EVT-001"]}
        result = await handle_agent_correlate_events(args)

        assert "correlations" in result
        assert len(result["correlations"]) == 0  # No correlations with single event
        assert result["correlation_score"] == 0

    @pytest.mark.asyncio
    async def test_correlate_events_returns_recommendation(self):
        """
        GIVEN a list of correlated events
        WHEN agent_correlate_events is invoked
        THEN it should return investigation recommendations
        """
        from src.mcp.tools.agent_orchestration import handle_agent_correlate_events

        args = {"event_ids": ["EVT-001", "EVT-002", "EVT-003"]}
        result = await handle_agent_correlate_events(args)

        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)


# =============================================================================
# TEST: Tool Registration
# =============================================================================

class TestAgentOrchestrationToolsRegistration:
    """Tests that agent orchestration tools are properly registered."""

    def test_all_agent_orchestration_tools_registered(self):
        """
        GIVEN the MCP tools registry
        WHEN we get all tools
        THEN agent orchestration tools should be present
        """
        from src.mcp.tools import get_all_tools

        tools = get_all_tools()
        tool_names = {t["name"] for t in tools}

        expected_tools = {
            "agent_explain_decision",
            "agent_correlate_events",
        }

        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Missing tool: {tool_name}"

    def test_all_agent_orchestration_handlers_registered(self):
        """
        GIVEN the MCP tool handlers
        WHEN we get all handlers
        THEN agent orchestration handlers should be present
        """
        from src.mcp.tools import get_tool_handlers

        handlers = get_tool_handlers()

        expected_handlers = [
            "agent_explain_decision",
            "agent_correlate_events",
        ]

        for handler_name in expected_handlers:
            assert handler_name in handlers, f"Missing handler: {handler_name}"
