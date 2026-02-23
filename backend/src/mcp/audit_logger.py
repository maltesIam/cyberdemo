"""
Audit Logger for MCP Tool Invocations.

Implements audit logging for all MCP tool invocations.
Requirement: REQ-014 - Audit logging de todas las invocaciones.

Features:
- Records all tool invocations with full context
- Masks sensitive fields (passwords, API keys)
- Provides query capabilities for audit analysis
- Immutable log entries
- Session and tool filtering
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import asyncio
from dataclasses import dataclass, field


# =============================================================================
# Constants
# =============================================================================

# Fields that should be masked in logs
SENSITIVE_FIELDS = {
    "password", "secret", "api_key", "apikey", "token",
    "authorization", "auth", "credential", "private_key"
}


# =============================================================================
# Audit Log Entry
# =============================================================================

@dataclass
class AuditLogEntry:
    """Represents an immutable audit log entry."""
    id: str
    timestamp: str
    tool_name: str
    session_id: str
    arguments: Dict[str, Any]
    result_summary: Optional[str]
    status: str  # "success" or "error"
    error_message: Optional[str]
    duration_ms: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "tool_name": self.tool_name,
            "session_id": self.session_id,
            "arguments": self.arguments,
            "result_summary": self.result_summary,
            "status": self.status,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms
        }


# =============================================================================
# Audit Logger
# =============================================================================

class AuditLogger:
    """
    Audit logger for MCP tool invocations.

    Maintains an in-memory log of all tool invocations with
    sensitive field masking and query capabilities.

    Note: In production, this would persist to a database or
    external logging service.
    """

    def __init__(self, max_entries: int = 10000):
        """
        Initialize the audit logger.

        Args:
            max_entries: Maximum number of entries to keep in memory
        """
        self._logs: List[AuditLogEntry] = []
        self._max_entries = max_entries
        self._lock = asyncio.Lock()

    async def log_invocation(
        self,
        tool_name: str,
        session_id: str,
        arguments: Dict[str, Any],
        result: Optional[Any],
        status: str,
        duration_ms: int,
        error_message: Optional[str] = None
    ) -> str:
        """
        Log a tool invocation.

        Args:
            tool_name: Name of the invoked tool
            session_id: Session identifier
            arguments: Tool arguments (sensitive fields will be masked)
            result: Tool result (will be summarized)
            status: "success" or "error"
            duration_ms: Execution duration in milliseconds
            error_message: Error message if status is "error"

        Returns:
            The log entry ID
        """
        async with self._lock:
            # Generate unique ID and timestamp
            entry_id = str(uuid.uuid4())
            timestamp = datetime.now(timezone.utc).isoformat()

            # Mask sensitive arguments
            masked_args = self._mask_sensitive_fields(arguments)

            # Create result summary (avoid storing large results)
            result_summary = None
            if result is not None:
                result_str = str(result)
                result_summary = result_str[:200] + "..." if len(result_str) > 200 else result_str

            # Create immutable entry
            entry = AuditLogEntry(
                id=entry_id,
                timestamp=timestamp,
                tool_name=tool_name,
                session_id=session_id,
                arguments=masked_args,
                result_summary=result_summary,
                status=status,
                error_message=error_message,
                duration_ms=duration_ms
            )

            # Add to logs (FIFO if at capacity)
            self._logs.append(entry)
            if len(self._logs) > self._max_entries:
                self._logs.pop(0)

            return entry_id

    async def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the most recent log entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of log entries as dictionaries
        """
        async with self._lock:
            entries = self._logs[-limit:]
            return [e.to_dict() for e in reversed(entries)]

    async def get_logs_by_session(
        self,
        session_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get log entries for a specific session.

        Args:
            session_id: Session to filter by
            limit: Maximum number of entries

        Returns:
            List of matching log entries
        """
        async with self._lock:
            matching = [e for e in self._logs if e.session_id == session_id]
            return [e.to_dict() for e in matching[-limit:]]

    async def get_logs_by_tool(
        self,
        tool_name: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get log entries for a specific tool.

        Args:
            tool_name: Tool to filter by
            limit: Maximum number of entries

        Returns:
            List of matching log entries
        """
        async with self._lock:
            matching = [e for e in self._logs if e.tool_name == tool_name]
            return [e.to_dict() for e in matching[-limit:]]

    async def get_audit_summary(self) -> Dict[str, Any]:
        """
        Get aggregated statistics from the audit log.

        Returns:
            Dictionary with summary statistics
        """
        async with self._lock:
            total = len(self._logs)
            success_count = sum(1 for e in self._logs if e.status == "success")
            error_count = sum(1 for e in self._logs if e.status == "error")

            # Tool usage counts
            tool_counts: Dict[str, int] = {}
            for entry in self._logs:
                tool_counts[entry.tool_name] = tool_counts.get(entry.tool_name, 0) + 1

            # Average duration
            total_duration = sum(e.duration_ms for e in self._logs)
            avg_duration = total_duration / total if total > 0 else 0

            return {
                "total_invocations": total,
                "success_count": success_count,
                "error_count": error_count,
                "success_rate": success_count / total if total > 0 else 0,
                "tool_usage": tool_counts,
                "average_duration_ms": avg_duration
            }

    async def clear_logs(self) -> None:
        """Clear all log entries (for testing)."""
        async with self._lock:
            self._logs.clear()

    def _mask_sensitive_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mask sensitive fields in a dictionary.

        Args:
            data: Dictionary potentially containing sensitive data

        Returns:
            Dictionary with sensitive fields masked
        """
        if not data:
            return {}

        masked = {}
        for key, value in data.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in SENSITIVE_FIELDS):
                masked[key] = "[REDACTED]"
            elif isinstance(value, dict):
                masked[key] = self._mask_sensitive_fields(value)
            else:
                masked[key] = value
        return masked


# =============================================================================
# Default Audit Logger Instance
# =============================================================================

_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """
    Get the default audit logger instance (singleton).

    Returns:
        The global AuditLogger instance
    """
    global _audit_logger

    if _audit_logger is None:
        _audit_logger = AuditLogger()

    return _audit_logger


def reset_audit_logger() -> None:
    """Reset the audit logger (useful for testing)."""
    global _audit_logger
    _audit_logger = None
