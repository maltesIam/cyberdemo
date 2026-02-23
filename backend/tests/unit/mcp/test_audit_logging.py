"""
Audit Logging Unit Tests - TDD RED Phase

Tests for audit logging of all MCP tool invocations.
Requirement: REQ-014

Following TDD: Tests written FIRST, implementation comes after.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import json


# =============================================================================
# TEST: Audit Logger Component (REQ-014)
# =============================================================================

class TestAuditLogger:
    """Unit tests for the audit logger."""

    def test_audit_logger_initialization(self):
        """
        GIVEN audit logger configuration
        WHEN AuditLogger is initialized
        THEN it should be ready to log
        """
        from src.mcp.audit_logger import AuditLogger

        logger = AuditLogger()

        assert logger is not None

    @pytest.mark.asyncio
    async def test_log_tool_invocation(self):
        """
        GIVEN a tool invocation
        WHEN log_invocation is called
        THEN it should record the invocation
        """
        from src.mcp.audit_logger import AuditLogger

        logger = AuditLogger()

        await logger.log_invocation(
            tool_name="siem_list_incidents",
            session_id="session-001",
            arguments={"severity": "critical"},
            result={"data": [], "total": 0},
            status="success",
            duration_ms=150
        )

        # Verify log was recorded
        logs = await logger.get_recent_logs(limit=1)
        assert len(logs) == 1
        assert logs[0]["tool_name"] == "siem_list_incidents"
        assert logs[0]["session_id"] == "session-001"
        assert logs[0]["status"] == "success"

    @pytest.mark.asyncio
    async def test_log_includes_timestamp(self):
        """
        GIVEN a logged invocation
        WHEN the log entry is retrieved
        THEN it should have a timestamp
        """
        from src.mcp.audit_logger import AuditLogger

        logger = AuditLogger()

        await logger.log_invocation(
            tool_name="edr_contain_host",
            session_id="session-002",
            arguments={"device_id": "DEV-001"},
            result={"status": "success"},
            status="success",
            duration_ms=200
        )

        logs = await logger.get_recent_logs(limit=1)
        assert "timestamp" in logs[0]
        # Timestamp should be ISO format
        datetime.fromisoformat(logs[0]["timestamp"].replace("Z", "+00:00"))

    @pytest.mark.asyncio
    async def test_log_failed_invocation(self):
        """
        GIVEN a failed tool invocation
        WHEN log_invocation is called with status=error
        THEN it should record the failure
        """
        from src.mcp.audit_logger import AuditLogger

        logger = AuditLogger()

        await logger.log_invocation(
            tool_name="agent_analyze_alert",
            session_id="session-003",
            arguments={"alert_id": "ALT-001"},
            result=None,
            status="error",
            error_message="Alert not found",
            duration_ms=50
        )

        logs = await logger.get_recent_logs(limit=1)
        assert logs[0]["status"] == "error"
        assert logs[0]["error_message"] == "Alert not found"

    @pytest.mark.asyncio
    async def test_log_includes_duration(self):
        """
        GIVEN a logged invocation
        WHEN the log entry is retrieved
        THEN it should include execution duration
        """
        from src.mcp.audit_logger import AuditLogger

        logger = AuditLogger()

        await logger.log_invocation(
            tool_name="agent_correlate_events",
            session_id="session-004",
            arguments={"event_ids": ["EVT-001", "EVT-002"]},
            result={"correlations": []},
            status="success",
            duration_ms=350
        )

        logs = await logger.get_recent_logs(limit=1)
        assert logs[0]["duration_ms"] == 350

    @pytest.mark.asyncio
    async def test_get_logs_by_session(self):
        """
        GIVEN multiple invocations from different sessions
        WHEN get_logs_by_session is called
        THEN it should return only logs from that session
        """
        from src.mcp.audit_logger import AuditLogger

        logger = AuditLogger()

        await logger.log_invocation(
            tool_name="tool_a",
            session_id="session-A",
            arguments={},
            result={},
            status="success",
            duration_ms=100
        )

        await logger.log_invocation(
            tool_name="tool_b",
            session_id="session-B",
            arguments={},
            result={},
            status="success",
            duration_ms=100
        )

        logs = await logger.get_logs_by_session("session-A")
        assert len(logs) == 1
        assert logs[0]["session_id"] == "session-A"

    @pytest.mark.asyncio
    async def test_get_logs_by_tool(self):
        """
        GIVEN multiple invocations of different tools
        WHEN get_logs_by_tool is called
        THEN it should return only logs for that tool
        """
        from src.mcp.audit_logger import AuditLogger

        logger = AuditLogger()

        await logger.log_invocation(
            tool_name="siem_list_incidents",
            session_id="session-001",
            arguments={},
            result={},
            status="success",
            duration_ms=100
        )

        await logger.log_invocation(
            tool_name="edr_contain_host",
            session_id="session-001",
            arguments={},
            result={},
            status="success",
            duration_ms=100
        )

        logs = await logger.get_logs_by_tool("siem_list_incidents")
        assert len(logs) == 1
        assert logs[0]["tool_name"] == "siem_list_incidents"

    @pytest.mark.asyncio
    async def test_log_entry_structure(self):
        """
        GIVEN a logged invocation
        WHEN the log entry is retrieved
        THEN it should have all required fields
        """
        from src.mcp.audit_logger import AuditLogger

        logger = AuditLogger()

        await logger.log_invocation(
            tool_name="agent_explain_decision",
            session_id="session-005",
            arguments={"decision_id": "DEC-001"},
            result={"decision_id": "DEC-001", "reasoning_chain": []},
            status="success",
            duration_ms=200
        )

        logs = await logger.get_recent_logs(limit=1)
        entry = logs[0]

        # Required fields
        assert "id" in entry
        assert "timestamp" in entry
        assert "tool_name" in entry
        assert "session_id" in entry
        assert "arguments" in entry
        assert "status" in entry
        assert "duration_ms" in entry

    @pytest.mark.asyncio
    async def test_get_audit_summary(self):
        """
        GIVEN multiple logged invocations
        WHEN get_audit_summary is called
        THEN it should return aggregated statistics
        """
        from src.mcp.audit_logger import AuditLogger

        logger = AuditLogger()

        # Log several invocations
        for i in range(5):
            await logger.log_invocation(
                tool_name="siem_list_incidents",
                session_id="session-001",
                arguments={},
                result={},
                status="success",
                duration_ms=100
            )

        await logger.log_invocation(
            tool_name="siem_list_incidents",
            session_id="session-001",
            arguments={},
            result=None,
            status="error",
            error_message="Test error",
            duration_ms=50
        )

        summary = await logger.get_audit_summary()

        assert summary["total_invocations"] >= 6
        assert summary["success_count"] >= 5
        assert summary["error_count"] >= 1


# =============================================================================
# TEST: Audit Logging Integration with MCP
# =============================================================================

class TestAuditLoggingIntegration:
    """Tests for audit logging integration with MCP server."""

    @pytest.mark.asyncio
    async def test_tool_invocation_is_logged(self):
        """
        GIVEN the MCP server with audit logging enabled
        WHEN a tool is invoked
        THEN the invocation should be logged
        """
        from httpx import AsyncClient, ASGITransport
        from src.main import app
        from src.mcp.audit_logger import get_audit_logger

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # Clear logs first
            audit_logger = get_audit_logger()
            await audit_logger.clear_logs()

            # Make a tool invocation
            message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "siem_list_incidents",
                    "arguments": {}
                }
            }
            await client.post("/mcp/messages", json=message)

            # Check audit log
            logs = await audit_logger.get_recent_logs(limit=1)
            assert len(logs) >= 1
            assert logs[0]["tool_name"] == "siem_list_incidents"


# =============================================================================
# TEST: Audit Log Security
# =============================================================================

class TestAuditLogSecurity:
    """Tests for audit log security features."""

    @pytest.mark.asyncio
    async def test_sensitive_arguments_are_masked(self):
        """
        GIVEN an invocation with sensitive data
        WHEN logged
        THEN sensitive fields should be masked
        """
        from src.mcp.audit_logger import AuditLogger

        logger = AuditLogger()

        await logger.log_invocation(
            tool_name="auth_login",
            session_id="session-001",
            arguments={
                "username": "admin",
                "password": "secret123",  # Should be masked
                "api_key": "key-abc-123"  # Should be masked
            },
            result={"token": "jwt-token"},
            status="success",
            duration_ms=100
        )

        logs = await logger.get_recent_logs(limit=1)
        args = logs[0]["arguments"]

        # Sensitive fields should be masked
        assert args.get("password") == "[REDACTED]"
        assert args.get("api_key") == "[REDACTED]"
        # Non-sensitive fields should remain
        assert args.get("username") == "admin"

    @pytest.mark.asyncio
    async def test_audit_logs_are_immutable(self):
        """
        GIVEN a logged invocation
        WHEN attempting to modify it
        THEN the modification should fail or be ignored
        """
        from src.mcp.audit_logger import AuditLogger

        logger = AuditLogger()

        await logger.log_invocation(
            tool_name="test_tool",
            session_id="session-001",
            arguments={},
            result={},
            status="success",
            duration_ms=100
        )

        logs = await logger.get_recent_logs(limit=1)
        original_id = logs[0]["id"]
        original_status = logs[0]["status"]

        # Logs should be read-only (no update method exists)
        assert not hasattr(logger, "update_log")


# =============================================================================
# TEST: Default Audit Logger
# =============================================================================

class TestDefaultAuditLogger:
    """Tests for the default audit logger."""

    def test_get_audit_logger_returns_singleton(self):
        """
        GIVEN the application
        WHEN get_audit_logger is called multiple times
        THEN it should return the same instance
        """
        from src.mcp.audit_logger import get_audit_logger

        logger1 = get_audit_logger()
        logger2 = get_audit_logger()

        assert logger1 is logger2
