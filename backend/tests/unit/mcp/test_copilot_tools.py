"""
Copilot MCP Tools Unit Tests - TDD

Tests for the copilot tools that provide proactive assistance to SOC analysts:
- copilot_get_suggestion (REQ-004-002-001)
- copilot_explain_why (REQ-004-002-002)
- copilot_auto_complete (REQ-004-002-003)

Test IDs:
- UT-044: Test ActionContext schema (REQ-004-001-003)
- UT-046: Test copilot_get_suggestion tool (REQ-004-002-001)
- UT-047: Test copilot_explain_why tool (REQ-004-002-002)
- UT-048: Test copilot_auto_complete tool (REQ-004-002-003)
"""

import pytest
import asyncio
from typing import Dict, Any
from datetime import datetime

from src.mcp.tools.copilot import (
    COPILOT_TOOLS,
    copilot_handlers,
    handle_copilot_get_suggestion,
    handle_copilot_explain_why,
    handle_copilot_auto_complete,
)
from src.models.copilot import ActionContext


# =============================================================================
# TEST: ActionContext Schema (REQ-004-001-003 / UT-044)
# =============================================================================

class TestActionContextSchema:
    """Unit tests for ActionContext schema validation."""

    def test_action_context_has_required_fields(self):
        """
        GIVEN the ActionContext schema
        WHEN we create an ActionContext
        THEN it must have all required fields
        """
        context = ActionContext(
            session_id="sess-001",
            timestamp=datetime.utcnow(),
            page="alerts",
            selected_entity="ALERT-001",
            recent_actions=["view_alert", "expand_details"],
            user_role="analyst"
        )

        assert context.session_id == "sess-001"
        assert context.page == "alerts"
        assert context.selected_entity == "ALERT-001"
        assert isinstance(context.recent_actions, list)
        assert context.user_role == "analyst"

    def test_action_context_selected_entity_optional(self):
        """
        GIVEN the ActionContext schema
        WHEN we create an ActionContext without selected_entity
        THEN it should be valid with None
        """
        context = ActionContext(
            session_id="sess-001",
            timestamp=datetime.utcnow(),
            page="dashboard",
            selected_entity=None,
            recent_actions=[],
            user_role="analyst"
        )

        assert context.selected_entity is None

    def test_action_context_recent_actions_max_10(self):
        """
        GIVEN the ActionContext schema
        WHEN we check recent_actions field
        THEN it should hold up to 10 recent actions
        """
        actions = [f"action_{i}" for i in range(10)]
        context = ActionContext(
            session_id="sess-001",
            timestamp=datetime.utcnow(),
            page="alerts",
            selected_entity=None,
            recent_actions=actions,
            user_role="analyst"
        )

        assert len(context.recent_actions) == 10


# =============================================================================
# TEST: Copilot Tool Definitions
# =============================================================================

class TestCopilotToolDefinitions:
    """Test that all copilot tools are properly defined."""

    def test_copilot_get_suggestion_tool_exists(self):
        """Test copilot_get_suggestion tool is defined."""
        tool_names = [t["name"] for t in COPILOT_TOOLS]
        assert "copilot_get_suggestion" in tool_names

    def test_copilot_explain_why_tool_exists(self):
        """Test copilot_explain_why tool is defined."""
        tool_names = [t["name"] for t in COPILOT_TOOLS]
        assert "copilot_explain_why" in tool_names

    def test_copilot_auto_complete_tool_exists(self):
        """Test copilot_auto_complete tool is defined."""
        tool_names = [t["name"] for t in COPILOT_TOOLS]
        assert "copilot_auto_complete" in tool_names

    def test_all_tools_have_required_fields(self):
        """Test all tools have name, description, and inputSchema."""
        for tool in COPILOT_TOOLS:
            assert "name" in tool, f"Tool missing name"
            assert "description" in tool, f"Tool {tool.get('name', 'unknown')} missing description"
            assert "inputSchema" in tool, f"Tool {tool.get('name', 'unknown')} missing inputSchema"


# =============================================================================
# TEST: copilot_get_suggestion Tool (REQ-004-002-001 / UT-046)
# =============================================================================

class TestCopilotGetSuggestionTool:
    """Unit tests for copilot_get_suggestion MCP tool."""

    def test_tool_schema_has_required_fields(self):
        """
        GIVEN the copilot_get_suggestion tool definition
        WHEN we inspect its schema
        THEN it must have name, description, and inputSchema
        """
        tool = next(
            (t for t in COPILOT_TOOLS if t["name"] == "copilot_get_suggestion"),
            None
        )

        assert tool is not None, "copilot_get_suggestion tool not found"
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool
        assert tool["inputSchema"]["type"] == "object"

    def test_tool_requires_context(self):
        """
        GIVEN the copilot_get_suggestion tool
        WHEN we check its input schema
        THEN context must be a required parameter
        """
        tool = next(
            (t for t in COPILOT_TOOLS if t["name"] == "copilot_get_suggestion"),
            None
        )

        assert "required" in tool["inputSchema"]
        assert "context" in tool["inputSchema"]["required"]

    def test_get_suggestion_with_valid_context(self):
        """
        GIVEN a valid context with page and selected_entity
        WHEN copilot_get_suggestion is invoked
        THEN it should return suggestions with action, description, confidence
        """
        args = {
            "context": {
                "page": "alerts",
                "selected_entity": "ALERT-001",
                "recent_actions": ["view_alert"]
            }
        }
        result = asyncio.run(handle_copilot_get_suggestion(args))

        assert "suggestions" in result
        assert isinstance(result["suggestions"], list)
        assert len(result["suggestions"]) > 0

        # Each suggestion should have required fields
        for suggestion in result["suggestions"]:
            assert "action" in suggestion
            assert "description" in suggestion
            assert "confidence" in suggestion
            assert "reasoning" in suggestion
            assert 0 <= suggestion["confidence"] <= 1.0

    def test_get_suggestion_returns_multiple_suggestions(self):
        """
        GIVEN a valid context
        WHEN copilot_get_suggestion is invoked
        THEN it should return multiple suggestions ordered by confidence
        """
        args = {
            "context": {
                "page": "alerts",
                "selected_entity": "ALERT-001",
                "recent_actions": ["view_alert", "expand_details"]
            }
        }
        result = asyncio.run(handle_copilot_get_suggestion(args))

        assert len(result["suggestions"]) >= 1
        # Suggestions should be ordered by confidence (highest first)
        if len(result["suggestions"]) > 1:
            for i in range(len(result["suggestions"]) - 1):
                assert result["suggestions"][i]["confidence"] >= result["suggestions"][i + 1]["confidence"]

    def test_get_suggestion_without_context_raises_error(self):
        """
        GIVEN no context
        WHEN copilot_get_suggestion is invoked
        THEN it should raise ValueError
        """
        args = {}
        with pytest.raises(ValueError, match="context is required"):
            asyncio.run(handle_copilot_get_suggestion(args))

    def test_get_suggestion_context_based_on_page(self):
        """
        GIVEN a context with specific page
        WHEN copilot_get_suggestion is invoked
        THEN suggestions should be relevant to that page
        """
        # Test alerts page
        args = {
            "context": {
                "page": "alerts",
                "selected_entity": "ALERT-001",
                "recent_actions": []
            }
        }
        result = asyncio.run(handle_copilot_get_suggestion(args))

        # Suggestions should be alert-related
        assert any("alert" in s["action"].lower() or "analyze" in s["action"].lower()
                   for s in result["suggestions"])

    def test_get_suggestion_includes_timestamp(self):
        """
        GIVEN a valid context
        WHEN copilot_get_suggestion is invoked
        THEN it should include a timestamp in the response
        """
        args = {
            "context": {
                "page": "dashboard",
                "selected_entity": None,
                "recent_actions": []
            }
        }
        result = asyncio.run(handle_copilot_get_suggestion(args))

        assert "timestamp" in result


# =============================================================================
# TEST: copilot_explain_why Tool (REQ-004-002-002 / UT-047)
# =============================================================================

class TestCopilotExplainWhyTool:
    """Unit tests for copilot_explain_why MCP tool."""

    def test_tool_schema_has_required_fields(self):
        """
        GIVEN the copilot_explain_why tool definition
        WHEN we inspect its schema
        THEN it must have name, description, and inputSchema
        """
        tool = next(
            (t for t in COPILOT_TOOLS if t["name"] == "copilot_explain_why"),
            None
        )

        assert tool is not None, "copilot_explain_why tool not found"
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool

    def test_tool_requires_action_and_context(self):
        """
        GIVEN the copilot_explain_why tool
        WHEN we check its input schema
        THEN action and context must be required parameters
        """
        tool = next(
            (t for t in COPILOT_TOOLS if t["name"] == "copilot_explain_why"),
            None
        )

        assert "required" in tool["inputSchema"]
        assert "action" in tool["inputSchema"]["required"]
        assert "context" in tool["inputSchema"]["required"]

    def test_explain_why_with_valid_inputs(self):
        """
        GIVEN a valid action and context
        WHEN copilot_explain_why is invoked
        THEN it should return an explanation with evidence and confidence
        """
        args = {
            "action": "analyze_alert",
            "context": {
                "page": "alerts",
                "selected_entity": "ALERT-001",
                "recent_actions": ["view_alert"]
            }
        }
        result = asyncio.run(handle_copilot_explain_why(args))

        assert "explanation" in result
        assert isinstance(result["explanation"], str)
        assert len(result["explanation"]) > 0
        assert "evidence" in result
        assert isinstance(result["evidence"], list)
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1.0

    def test_explain_why_returns_alternatives(self):
        """
        GIVEN a valid action and context
        WHEN copilot_explain_why is invoked
        THEN it should return alternative actions that were considered
        """
        args = {
            "action": "contain_host",
            "context": {
                "page": "alerts",
                "selected_entity": "ALERT-001",
                "recent_actions": ["view_alert", "analyze_ioc"]
            }
        }
        result = asyncio.run(handle_copilot_explain_why(args))

        assert "alternatives" in result
        assert isinstance(result["alternatives"], list)

    def test_explain_why_without_action_raises_error(self):
        """
        GIVEN no action
        WHEN copilot_explain_why is invoked
        THEN it should raise ValueError
        """
        args = {
            "context": {
                "page": "alerts",
                "selected_entity": "ALERT-001",
                "recent_actions": []
            }
        }
        with pytest.raises(ValueError, match="action is required"):
            asyncio.run(handle_copilot_explain_why(args))

    def test_explain_why_without_context_raises_error(self):
        """
        GIVEN no context
        WHEN copilot_explain_why is invoked
        THEN it should raise ValueError
        """
        args = {
            "action": "analyze_alert"
        }
        with pytest.raises(ValueError, match="context is required"):
            asyncio.run(handle_copilot_explain_why(args))

    def test_explain_why_provides_detailed_reasoning(self):
        """
        GIVEN a specific action and context
        WHEN copilot_explain_why is invoked
        THEN explanation should reference the action and context
        """
        args = {
            "action": "investigate_ioc",
            "context": {
                "page": "alerts",
                "selected_entity": "ALERT-002",
                "recent_actions": ["view_alert"]
            }
        }
        result = asyncio.run(handle_copilot_explain_why(args))

        # Explanation should be substantive
        assert len(result["explanation"]) > 20
        # Evidence should have at least one item
        assert len(result["evidence"]) >= 1


# =============================================================================
# TEST: copilot_auto_complete Tool (REQ-004-002-003 / UT-048)
# =============================================================================

class TestCopilotAutoCompleteTool:
    """Unit tests for copilot_auto_complete MCP tool."""

    def test_tool_schema_has_required_fields(self):
        """
        GIVEN the copilot_auto_complete tool definition
        WHEN we inspect its schema
        THEN it must have name, description, and inputSchema
        """
        tool = next(
            (t for t in COPILOT_TOOLS if t["name"] == "copilot_auto_complete"),
            None
        )

        assert tool is not None, "copilot_auto_complete tool not found"
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool

    def test_tool_requires_partial_input_and_field_type(self):
        """
        GIVEN the copilot_auto_complete tool
        WHEN we check its input schema
        THEN partial_input and field_type must be required
        """
        tool = next(
            (t for t in COPILOT_TOOLS if t["name"] == "copilot_auto_complete"),
            None
        )

        assert "required" in tool["inputSchema"]
        assert "partial_input" in tool["inputSchema"]["required"]
        assert "field_type" in tool["inputSchema"]["required"]

    def test_auto_complete_with_valid_inputs(self):
        """
        GIVEN a valid partial_input and field_type
        WHEN copilot_auto_complete is invoked
        THEN it should return completions with value, confidence, source
        """
        args = {
            "partial_input": "192.168",
            "field_type": "ip_address",
            "context": {
                "page": "search",
                "selected_entity": None,
                "recent_actions": []
            }
        }
        result = asyncio.run(handle_copilot_auto_complete(args))

        assert "completions" in result
        assert isinstance(result["completions"], list)
        assert len(result["completions"]) > 0

        # Each completion should have required fields
        for completion in result["completions"]:
            assert "value" in completion
            assert "confidence" in completion
            assert "source" in completion
            assert 0 <= completion["confidence"] <= 1.0

    def test_auto_complete_for_hostname(self):
        """
        GIVEN a partial hostname input
        WHEN copilot_auto_complete is invoked
        THEN it should return matching hostnames
        """
        args = {
            "partial_input": "WS-FIN",
            "field_type": "hostname",
            "context": {}
        }
        result = asyncio.run(handle_copilot_auto_complete(args))

        assert len(result["completions"]) >= 1
        # Completions should start with the partial input
        for completion in result["completions"]:
            assert completion["value"].upper().startswith("WS-FIN")

    def test_auto_complete_for_username(self):
        """
        GIVEN a partial username input
        WHEN copilot_auto_complete is invoked
        THEN it should return matching usernames
        """
        args = {
            "partial_input": "DOMAIN\\admin",
            "field_type": "username",
            "context": {}
        }
        result = asyncio.run(handle_copilot_auto_complete(args))

        assert len(result["completions"]) >= 1

    def test_auto_complete_for_hash(self):
        """
        GIVEN a partial hash input
        WHEN copilot_auto_complete is invoked
        THEN it should return matching hashes from known IOCs
        """
        args = {
            "partial_input": "abc123",
            "field_type": "hash",
            "context": {}
        }
        result = asyncio.run(handle_copilot_auto_complete(args))

        assert "completions" in result

    def test_auto_complete_without_partial_input_raises_error(self):
        """
        GIVEN no partial_input
        WHEN copilot_auto_complete is invoked
        THEN it should raise ValueError
        """
        args = {
            "field_type": "ip_address",
            "context": {}
        }
        with pytest.raises(ValueError, match="partial_input is required"):
            asyncio.run(handle_copilot_auto_complete(args))

    def test_auto_complete_without_field_type_raises_error(self):
        """
        GIVEN no field_type
        WHEN copilot_auto_complete is invoked
        THEN it should raise ValueError
        """
        args = {
            "partial_input": "192.168",
            "context": {}
        }
        with pytest.raises(ValueError, match="field_type is required"):
            asyncio.run(handle_copilot_auto_complete(args))

    def test_auto_complete_returns_ordered_by_confidence(self):
        """
        GIVEN a valid partial input
        WHEN copilot_auto_complete is invoked
        THEN completions should be ordered by confidence (highest first)
        """
        args = {
            "partial_input": "192.168.1",
            "field_type": "ip_address",
            "context": {}
        }
        result = asyncio.run(handle_copilot_auto_complete(args))

        if len(result["completions"]) > 1:
            for i in range(len(result["completions"]) - 1):
                assert result["completions"][i]["confidence"] >= result["completions"][i + 1]["confidence"]

    def test_auto_complete_no_matches_returns_empty(self):
        """
        GIVEN a partial input with no matches
        WHEN copilot_auto_complete is invoked
        THEN it should return an empty completions list
        """
        args = {
            "partial_input": "zzz-no-match-xyz",
            "field_type": "hostname",
            "context": {}
        }
        result = asyncio.run(handle_copilot_auto_complete(args))

        assert "completions" in result
        assert len(result["completions"]) == 0


# =============================================================================
# TEST: Tool Registration
# =============================================================================

class TestCopilotToolsRegistration:
    """Tests that copilot tools are properly registered."""

    def test_all_copilot_tools_registered(self):
        """
        GIVEN the MCP tools registry
        WHEN we get all tools
        THEN copilot tools should be present
        """
        from src.mcp.tools import get_all_tools

        tools = get_all_tools()
        tool_names = {t["name"] for t in tools}

        expected_tools = {
            "copilot_get_suggestion",
            "copilot_explain_why",
            "copilot_auto_complete",
        }

        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Missing tool: {tool_name}"

    def test_all_copilot_handlers_registered(self):
        """
        GIVEN the MCP tool handlers
        WHEN we get all handlers
        THEN copilot handlers should be present
        """
        from src.mcp.tools import get_tool_handlers

        handlers = get_tool_handlers()

        expected_handlers = [
            "copilot_get_suggestion",
            "copilot_explain_why",
            "copilot_auto_complete",
        ]

        for handler_name in expected_handlers:
            assert handler_name in handlers, f"Missing handler: {handler_name}"

    def test_handlers_are_callable(self):
        """Test that all handlers are callable async functions."""
        assert callable(handle_copilot_get_suggestion)
        assert callable(handle_copilot_explain_why)
        assert callable(handle_copilot_auto_complete)
