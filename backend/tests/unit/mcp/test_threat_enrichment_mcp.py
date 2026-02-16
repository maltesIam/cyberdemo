"""
MCP Threat Enrichment Tools Tests - TDD RED Phase

Tests the MCP tools for threat enrichment that enable AI agents
to enrich IOCs with threat intelligence.

Tools tested:
- enrichment_threats: Enrich IOCs with threat intel
- threats_query: Query enriched threats
- threats_map: Get map visualization data
"""

import pytest
from typing import Any, Dict


class TestMCPThreatEnrichmentToolRegistration:
    """Tests for MCP threat enrichment tool registration."""

    def test_mcp_enrichment_threats_tool_exists(self):
        """
        GIVEN the MCP tools registry
        WHEN we get all tools
        THEN enrichment_threats tool should be registered
        """
        from src.mcp.tools import get_all_tools

        tools = get_all_tools()
        tool_names = {t["name"] for t in tools}

        assert "enrichment_threats" in tool_names, "enrichment_threats tool should be registered"

    def test_mcp_threats_query_tool_exists(self):
        """
        GIVEN the MCP tools registry
        WHEN we get all tools
        THEN threats_query tool should be registered
        """
        from src.mcp.tools import get_all_tools

        tools = get_all_tools()
        tool_names = {t["name"] for t in tools}

        assert "threats_query" in tool_names, "threats_query tool should be registered"

    def test_mcp_threats_map_tool_exists(self):
        """
        GIVEN the MCP tools registry
        WHEN we get all tools
        THEN threats_map tool should be registered
        """
        from src.mcp.tools import get_all_tools

        tools = get_all_tools()
        tool_names = {t["name"] for t in tools}

        assert "threats_map" in tool_names, "threats_map tool should be registered"


class TestMCPThreatEnrichmentToolSchemas:
    """Tests for MCP threat enrichment tool schemas."""

    def test_enrichment_threats_has_valid_schema(self):
        """
        GIVEN the enrichment_threats tool
        WHEN we inspect its schema
        THEN it should have proper inputSchema with indicators field
        """
        from src.mcp.tools import get_all_tools

        tools = get_all_tools()
        tool = next((t for t in tools if t["name"] == "enrichment_threats"), None)

        assert tool is not None, "enrichment_threats tool not found"
        assert "inputSchema" in tool, "Tool should have inputSchema"
        assert "properties" in tool["inputSchema"], "Schema should have properties"
        assert "indicators" in tool["inputSchema"]["properties"], "Schema should have indicators property"

    def test_threats_query_has_valid_schema(self):
        """
        GIVEN the threats_query tool
        WHEN we inspect its schema
        THEN it should have proper inputSchema with query parameters
        """
        from src.mcp.tools import get_all_tools

        tools = get_all_tools()
        tool = next((t for t in tools if t["name"] == "threats_query"), None)

        assert tool is not None, "threats_query tool not found"
        assert "inputSchema" in tool, "Tool should have inputSchema"
        assert "properties" in tool["inputSchema"], "Schema should have properties"

    def test_threats_map_has_valid_schema(self):
        """
        GIVEN the threats_map tool
        WHEN we inspect its schema
        THEN it should have proper inputSchema
        """
        from src.mcp.tools import get_all_tools

        tools = get_all_tools()
        tool = next((t for t in tools if t["name"] == "threats_map"), None)

        assert tool is not None, "threats_map tool not found"
        assert "inputSchema" in tool, "Tool should have inputSchema"


class TestMCPThreatEnrichmentHandlers:
    """Tests for MCP threat enrichment tool handlers."""

    @pytest.mark.asyncio
    async def test_mcp_enrichment_returns_valid_schema(self):
        """
        GIVEN the enrichment_threats handler
        WHEN called with valid indicators
        THEN it should return enriched data with proper schema
        """
        from src.mcp.tools import get_tool_handlers

        handlers = get_tool_handlers()
        assert "enrichment_threats" in handlers, "enrichment_threats handler not registered"

        handler = handlers["enrichment_threats"]
        result = await handler({
            "indicators": [
                {"type": "ip", "value": "192.168.1.100"},
                {"type": "domain", "value": "evil.example.com"}
            ]
        })

        # Verify result structure
        assert isinstance(result, dict), "Result should be a dict"
        assert "job_id" in result, "Result should have job_id"
        assert "enriched_indicators" in result, "Result should have enriched_indicators"
        assert isinstance(result["enriched_indicators"], list), "enriched_indicators should be a list"

        # Verify at least one enriched indicator
        if len(result["enriched_indicators"]) > 0:
            indicator = result["enriched_indicators"][0]
            assert "type" in indicator, "Indicator should have type"
            assert "value" in indicator, "Indicator should have value"
            assert "risk_score" in indicator, "Indicator should have risk_score"
            assert "risk_level" in indicator, "Indicator should have risk_level"

    @pytest.mark.asyncio
    async def test_mcp_handles_invalid_input(self):
        """
        GIVEN the enrichment_threats handler
        WHEN called with invalid input (missing required fields)
        THEN it should raise ValueError with descriptive message
        """
        from src.mcp.tools import get_tool_handlers

        handlers = get_tool_handlers()
        handler = handlers["enrichment_threats"]

        # Call with invalid indicator (missing value)
        with pytest.raises(ValueError) as exc_info:
            await handler({
                "indicators": [
                    {"type": "ip"}  # Missing 'value'
                ]
            })

        assert "value" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_mcp_threats_query_handler(self):
        """
        GIVEN the threats_query handler
        WHEN called with query parameters
        THEN it should return matching threats
        """
        from src.mcp.tools import get_tool_handlers

        handlers = get_tool_handlers()
        assert "threats_query" in handlers, "threats_query handler not registered"

        handler = handlers["threats_query"]
        result = await handler({
            "risk_level": "high",
            "limit": 10
        })

        assert isinstance(result, dict), "Result should be a dict"
        assert "threats" in result, "Result should have threats list"
        assert isinstance(result["threats"], list), "threats should be a list"

    @pytest.mark.asyncio
    async def test_mcp_threats_map_handler(self):
        """
        GIVEN the threats_map handler
        WHEN called
        THEN it should return map visualization data
        """
        from src.mcp.tools import get_tool_handlers

        handlers = get_tool_handlers()
        assert "threats_map" in handlers, "threats_map handler not registered"

        handler = handlers["threats_map"]
        result = await handler({})

        assert isinstance(result, dict), "Result should be a dict"
        assert "countries" in result, "Result should have countries"
        assert "attack_lines" in result, "Result should have attack_lines"
        assert isinstance(result["countries"], list), "countries should be a list"
        assert isinstance(result["attack_lines"], list), "attack_lines should be a list"


class TestMCPThreatEnrichmentIntegration:
    """Integration tests for MCP threat enrichment with the server."""

    @pytest.mark.asyncio
    async def test_enrichment_limits_to_100_items(self):
        """
        GIVEN the enrichment_threats handler
        WHEN called with more than 100 indicators
        THEN it should limit processing to 100 items
        """
        from src.mcp.tools import get_tool_handlers

        handlers = get_tool_handlers()
        handler = handlers["enrichment_threats"]

        # Create 150 indicators
        indicators = [
            {"type": "ip", "value": f"192.168.1.{i}"}
            for i in range(150)
        ]

        result = await handler({"indicators": indicators})

        # Should be limited to 100
        assert result["total_items"] <= 100, "Should limit to 100 items"

    @pytest.mark.asyncio
    async def test_enrichment_with_empty_indicators(self):
        """
        GIVEN the enrichment_threats handler
        WHEN called with empty indicators
        THEN it should return valid response with zero items
        """
        from src.mcp.tools import get_tool_handlers

        handlers = get_tool_handlers()
        handler = handlers["enrichment_threats"]

        result = await handler({"indicators": []})

        assert result["total_items"] == 0, "Total items should be 0"
        assert result["enriched_indicators"] == [], "Should have empty enriched list"
