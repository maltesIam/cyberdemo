"""
Unit tests for Agent Orchestration MCP Tools.

Test IDs:
- UT-012: Test agent_analyze_alert tool invocation (REQ-001-003-001)
- UT-013: Test agent_investigate_ioc tool invocation (REQ-001-003-002)
- UT-014: Test agent_recommend_action tool invocation (REQ-001-003-003)
- UT-015: Test agent_generate_report tool invocation (REQ-001-003-004)
"""

import pytest
from typing import Dict, Any
from datetime import datetime

from src.mcp.tools.agent_orchestration import (
    AGENT_ORCHESTRATION_TOOLS,
    agent_orchestration_handlers,
    handle_agent_analyze_alert,
    handle_agent_investigate_ioc,
    handle_agent_recommend_action,
    handle_agent_generate_report,
)


class TestAgentOrchestrationToolDefinitions:
    """Test that all agent orchestration tools are properly defined."""

    def test_agent_analyze_alert_tool_exists(self):
        """Test agent_analyze_alert tool is defined."""
        tool_names = [t["name"] for t in AGENT_ORCHESTRATION_TOOLS]
        assert "agent_analyze_alert" in tool_names

    def test_agent_investigate_ioc_tool_exists(self):
        """Test agent_investigate_ioc tool is defined."""
        tool_names = [t["name"] for t in AGENT_ORCHESTRATION_TOOLS]
        assert "agent_investigate_ioc" in tool_names

    def test_agent_recommend_action_tool_exists(self):
        """Test agent_recommend_action tool is defined."""
        tool_names = [t["name"] for t in AGENT_ORCHESTRATION_TOOLS]
        assert "agent_recommend_action" in tool_names

    def test_agent_generate_report_tool_exists(self):
        """Test agent_generate_report tool is defined."""
        tool_names = [t["name"] for t in AGENT_ORCHESTRATION_TOOLS]
        assert "agent_generate_report" in tool_names

    def test_all_tools_have_required_fields(self):
        """Test all tools have name, description, and inputSchema."""
        for tool in AGENT_ORCHESTRATION_TOOLS:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            assert tool["inputSchema"]["type"] == "object"

    def test_all_tools_have_handlers(self):
        """Test all defined tools have corresponding handlers."""
        tool_names = [t["name"] for t in AGENT_ORCHESTRATION_TOOLS]
        for name in tool_names:
            assert name in agent_orchestration_handlers


class TestAgentAnalyzeAlertTool:
    """Test agent_analyze_alert tool (UT-012, REQ-001-003-001)."""

    @pytest.mark.asyncio
    async def test_analyze_alert_returns_analysis(self):
        """Test analyzing an alert returns analysis results."""
        result = await handle_agent_analyze_alert({"alert_id": "ALERT-001"})

        assert "alert_id" in result
        assert "analysis" in result
        assert "severity_assessment" in result
        assert "confidence_score" in result

    @pytest.mark.asyncio
    async def test_analyze_alert_includes_threat_intel(self):
        """Test analysis includes threat intelligence."""
        result = await handle_agent_analyze_alert({"alert_id": "ALERT-001"})

        assert "threat_intel" in result
        # Should have indicators about the threat
        assert isinstance(result["threat_intel"], dict)

    @pytest.mark.asyncio
    async def test_analyze_alert_includes_mitre_mapping(self):
        """Test analysis includes MITRE ATT&CK mapping."""
        result = await handle_agent_analyze_alert({"alert_id": "ALERT-001"})

        assert "mitre_mapping" in result
        assert isinstance(result["mitre_mapping"], list)
        # Each mapping should have tactic and technique
        if result["mitre_mapping"]:
            mapping = result["mitre_mapping"][0]
            assert "tactic_id" in mapping
            assert "technique_id" in mapping

    @pytest.mark.asyncio
    async def test_analyze_alert_includes_recommendations(self):
        """Test analysis includes action recommendations."""
        result = await handle_agent_analyze_alert({"alert_id": "ALERT-001"})

        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)

    @pytest.mark.asyncio
    async def test_analyze_alert_requires_alert_id(self):
        """Test that alert_id is required."""
        with pytest.raises(ValueError, match="alert_id is required"):
            await handle_agent_analyze_alert({})

    @pytest.mark.asyncio
    async def test_analyze_alert_handles_unknown_alert(self):
        """Test handling of unknown alert IDs."""
        result = await handle_agent_analyze_alert({"alert_id": "UNKNOWN-ALERT"})

        assert "status" in result
        assert result["status"] == "not_found" or "alert_id" in result


class TestAgentInvestigateIocTool:
    """Test agent_investigate_ioc tool (UT-013, REQ-001-003-002)."""

    @pytest.mark.asyncio
    async def test_investigate_ip_address(self):
        """Test investigating an IP address IOC."""
        result = await handle_agent_investigate_ioc({
            "ioc": "185.234.72.199",
            "type": "ip"
        })

        assert "ioc" in result
        assert result["ioc"] == "185.234.72.199"
        assert "type" in result
        assert "reputation" in result
        assert "threat_score" in result

    @pytest.mark.asyncio
    async def test_investigate_domain(self):
        """Test investigating a domain IOC."""
        result = await handle_agent_investigate_ioc({
            "ioc": "malware-c2.evil.com",
            "type": "domain"
        })

        assert "ioc" in result
        assert "type" in result
        assert result["type"] == "domain"
        assert "reputation" in result

    @pytest.mark.asyncio
    async def test_investigate_file_hash(self):
        """Test investigating a file hash IOC."""
        result = await handle_agent_investigate_ioc({
            "ioc": "abc123def456789abcdef123456789ab",
            "type": "hash"
        })

        assert "ioc" in result
        assert "type" in result
        assert result["type"] == "hash"
        assert "reputation" in result

    @pytest.mark.asyncio
    async def test_investigate_ioc_returns_geo_info(self):
        """Test IP investigation includes geographic information."""
        result = await handle_agent_investigate_ioc({
            "ioc": "185.234.72.199",
            "type": "ip"
        })

        assert "geo_info" in result
        geo = result["geo_info"]
        assert "country" in geo or "country_code" in geo

    @pytest.mark.asyncio
    async def test_investigate_ioc_returns_related_indicators(self):
        """Test investigation returns related indicators."""
        result = await handle_agent_investigate_ioc({
            "ioc": "185.234.72.199",
            "type": "ip"
        })

        assert "related_indicators" in result
        assert isinstance(result["related_indicators"], list)

    @pytest.mark.asyncio
    async def test_investigate_ioc_requires_ioc_value(self):
        """Test that ioc value is required."""
        with pytest.raises(ValueError, match="ioc is required"):
            await handle_agent_investigate_ioc({"type": "ip"})

    @pytest.mark.asyncio
    async def test_investigate_ioc_requires_type(self):
        """Test that type is required."""
        with pytest.raises(ValueError, match="type is required"):
            await handle_agent_investigate_ioc({"ioc": "185.234.72.199"})


class TestAgentRecommendActionTool:
    """Test agent_recommend_action tool (UT-014, REQ-001-003-003)."""

    @pytest.mark.asyncio
    async def test_recommend_action_returns_recommendations(self):
        """Test getting action recommendations."""
        result = await handle_agent_recommend_action({
            "context": {
                "incident_id": "INC-001",
                "severity": "critical",
                "asset_type": "workstation"
            }
        })

        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_recommend_action_includes_priority(self):
        """Test recommendations include priority."""
        result = await handle_agent_recommend_action({
            "context": {
                "incident_id": "INC-001",
                "severity": "critical"
            }
        })

        # Each recommendation should have priority
        for rec in result["recommendations"]:
            assert "priority" in rec
            assert rec["priority"] in ["low", "medium", "high", "critical"]

    @pytest.mark.asyncio
    async def test_recommend_action_includes_reasoning(self):
        """Test recommendations include reasoning."""
        result = await handle_agent_recommend_action({
            "context": {
                "incident_id": "INC-001"
            }
        })

        for rec in result["recommendations"]:
            assert "action" in rec
            assert "reasoning" in rec

    @pytest.mark.asyncio
    async def test_recommend_action_includes_risk_assessment(self):
        """Test recommendations include risk assessment."""
        result = await handle_agent_recommend_action({
            "context": {
                "incident_id": "INC-001"
            }
        })

        assert "risk_assessment" in result
        assert "current_risk" in result["risk_assessment"]

    @pytest.mark.asyncio
    async def test_recommend_action_requires_context(self):
        """Test that context is required."""
        with pytest.raises(ValueError, match="context is required"):
            await handle_agent_recommend_action({})

    @pytest.mark.asyncio
    async def test_recommend_action_for_ransomware(self):
        """Test recommendations for ransomware context."""
        result = await handle_agent_recommend_action({
            "context": {
                "incident_id": "INC-001",
                "threat_type": "ransomware",
                "severity": "critical"
            }
        })

        # Should recommend containment for ransomware
        actions = [r["action"] for r in result["recommendations"]]
        assert any("contain" in a.lower() or "isolate" in a.lower() for a in actions)


class TestAgentGenerateReportTool:
    """Test agent_generate_report tool (UT-015, REQ-001-003-004)."""

    @pytest.mark.asyncio
    async def test_generate_report_json_format(self):
        """Test generating a report in JSON format."""
        result = await handle_agent_generate_report({
            "incident_id": "INC-001",
            "format": "json"
        })

        assert "report" in result
        assert "format" in result
        assert result["format"] == "json"
        assert isinstance(result["report"], dict)

    @pytest.mark.asyncio
    async def test_generate_report_markdown_format(self):
        """Test generating a report in Markdown format."""
        result = await handle_agent_generate_report({
            "incident_id": "INC-001",
            "format": "markdown"
        })

        assert "report" in result
        assert "format" in result
        assert result["format"] == "markdown"
        # Markdown should be a string
        assert isinstance(result["report"], str)
        # Should contain markdown headers
        assert "#" in result["report"]

    @pytest.mark.asyncio
    async def test_generate_report_includes_executive_summary(self):
        """Test report includes executive summary."""
        result = await handle_agent_generate_report({
            "incident_id": "INC-001",
            "format": "json"
        })

        report = result["report"]
        assert "executive_summary" in report

    @pytest.mark.asyncio
    async def test_generate_report_includes_timeline(self):
        """Test report includes incident timeline."""
        result = await handle_agent_generate_report({
            "incident_id": "INC-001",
            "format": "json"
        })

        report = result["report"]
        assert "timeline" in report
        assert isinstance(report["timeline"], list)

    @pytest.mark.asyncio
    async def test_generate_report_includes_iocs(self):
        """Test report includes IOCs."""
        result = await handle_agent_generate_report({
            "incident_id": "INC-001",
            "format": "json"
        })

        report = result["report"]
        assert "indicators_of_compromise" in report

    @pytest.mark.asyncio
    async def test_generate_report_includes_recommendations(self):
        """Test report includes recommendations."""
        result = await handle_agent_generate_report({
            "incident_id": "INC-001",
            "format": "json"
        })

        report = result["report"]
        assert "recommendations" in report

    @pytest.mark.asyncio
    async def test_generate_report_requires_incident_id(self):
        """Test that incident_id is required."""
        with pytest.raises(ValueError, match="incident_id is required"):
            await handle_agent_generate_report({"format": "json"})

    @pytest.mark.asyncio
    async def test_generate_report_defaults_to_json(self):
        """Test format defaults to json if not specified."""
        result = await handle_agent_generate_report({
            "incident_id": "INC-001"
        })

        assert result["format"] == "json"

    @pytest.mark.asyncio
    async def test_generate_report_handles_unknown_incident(self):
        """Test handling unknown incident ID."""
        result = await handle_agent_generate_report({
            "incident_id": "UNKNOWN-INC",
            "format": "json"
        })

        # Should still return a report structure, possibly empty or with error
        assert "report" in result or "status" in result
