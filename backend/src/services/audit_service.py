"""
Audit Service for compliance logging and reporting.

Provides audit event logging, querying, and export functionality.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import csv
import io
import json

from ..models.audit import (
    AuditLog,
    AuditLogFilter,
    AuditActionType,
    AuditOutcome,
    AuditExportFormat,
)


class AuditService:
    """Service for audit log operations."""

    def __init__(self, opensearch_client=None):
        """Initialize audit service.

        Args:
            opensearch_client: Optional OpenSearch client for persistence
        """
        self.os_client = opensearch_client
        self._audit_store: Dict[str, Dict[str, Any]] = {}
        self._index_name = "audit-logs-v1"

    async def log_event(
        self,
        user: str,
        action_type: AuditActionType,
        target: str,
        outcome: AuditOutcome,
        target_type: str = "",
        details: Optional[Dict[str, Any]] = None,
        policy_decision: Optional[str] = None,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> AuditLog:
        """Log an audit event.

        Args:
            user: User who performed the action
            action_type: Type of action
            target: Target of the action
            outcome: Outcome of the action
            target_type: Type of target (asset, incident, etc.)
            details: Additional details
            policy_decision: Policy engine decision if applicable
            ip_address: User's IP address
            session_id: Session ID

        Returns:
            Created AuditLog entry
        """
        audit_id = f"audit-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow()

        audit_log = AuditLog(
            id=audit_id,
            timestamp=timestamp,
            user=user,
            action_type=action_type,
            target=target,
            target_type=target_type,
            details=details or {},
            policy_decision=policy_decision,
            outcome=outcome,
            ip_address=ip_address,
            session_id=session_id,
        )

        # Store in memory
        self._audit_store[audit_id] = audit_log.model_dump()

        # Persist to OpenSearch if client available
        if self.os_client:
            await self._persist_log(audit_log)

        return audit_log

    async def get_logs(
        self,
        filters: Optional[AuditLogFilter] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[List[AuditLog], int]:
        """Get audit logs with filtering and pagination.

        Args:
            filters: Optional filters
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Tuple of (logs list, total count)
        """
        # Try OpenSearch first
        if self.os_client:
            return await self._query_opensearch(filters, page, page_size)

        # Fallback to in-memory store
        logs = list(self._audit_store.values())

        # Apply filters
        if filters:
            if filters.date_from:
                logs = [
                    log for log in logs
                    if datetime.fromisoformat(str(log["timestamp"]).replace("Z", "")) >= filters.date_from
                ]
            if filters.date_to:
                logs = [
                    log for log in logs
                    if datetime.fromisoformat(str(log["timestamp"]).replace("Z", "")) <= filters.date_to
                ]
            if filters.user:
                logs = [log for log in logs if log["user"].lower() == filters.user.lower()]
            if filters.action_type:
                logs = [log for log in logs if log["action_type"] == filters.action_type]
            if filters.target:
                logs = [log for log in logs if filters.target.lower() in log["target"].lower()]
            if filters.outcome:
                logs = [log for log in logs if log["outcome"] == filters.outcome]

        # Sort by timestamp descending
        logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        total = len(logs)

        # Paginate
        start = (page - 1) * page_size
        end = start + page_size
        paginated_logs = logs[start:end]

        return [AuditLog(**log) for log in paginated_logs], total

    async def export_logs(
        self,
        format: AuditExportFormat,
        filters: Optional[AuditLogFilter] = None,
    ) -> tuple[str, str]:
        """Export audit logs in the specified format.

        Args:
            format: Export format (CSV or JSON)
            filters: Optional filters

        Returns:
            Tuple of (exported data string, content type)
        """
        # Get all matching logs (no pagination for export)
        logs, _ = await self.get_logs(filters, page=1, page_size=10000)

        if format == AuditExportFormat.CSV:
            return self._export_csv(logs), "text/csv"
        else:
            return self._export_json(logs), "application/json"

    def _export_csv(self, logs: List[AuditLog]) -> str:
        """Export logs as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "ID", "Timestamp", "User", "Action Type", "Target",
            "Target Type", "Policy Decision", "Outcome", "IP Address",
            "Session ID", "Details"
        ])

        # Data rows
        for log in logs:
            writer.writerow([
                log.id,
                log.timestamp.isoformat(),
                log.user,
                log.action_type.value,
                log.target,
                log.target_type,
                log.policy_decision or "",
                log.outcome.value,
                log.ip_address or "",
                log.session_id or "",
                json.dumps(log.details),
            ])

        return output.getvalue()

    def _export_json(self, logs: List[AuditLog]) -> str:
        """Export logs as JSON."""
        data = [
            {
                **log.model_dump(),
                "timestamp": log.timestamp.isoformat(),
                "action_type": log.action_type.value,
                "outcome": log.outcome.value,
            }
            for log in logs
        ]
        return json.dumps(data, indent=2)

    async def get_users(self) -> List[str]:
        """Get list of unique users in audit logs."""
        if self.os_client:
            return await self._get_unique_users_opensearch()

        users = set(log["user"] for log in self._audit_store.values())
        return sorted(users)

    async def _persist_log(self, log: AuditLog) -> None:
        """Persist audit log to OpenSearch."""
        if not self.os_client:
            return

        try:
            doc = log.model_dump()
            doc["timestamp"] = log.timestamp.isoformat()
            doc["action_type"] = log.action_type.value
            doc["outcome"] = log.outcome.value

            await self.os_client.index(
                index=self._index_name,
                id=log.id,
                body=doc
            )
        except Exception:
            # Log error but don't fail the operation
            pass

    async def _query_opensearch(
        self,
        filters: Optional[AuditLogFilter],
        page: int,
        page_size: int,
    ) -> tuple[List[AuditLog], int]:
        """Query audit logs from OpenSearch."""
        if not self.os_client:
            return [], 0

        query = {"bool": {"must": []}}

        if filters:
            if filters.date_from or filters.date_to:
                range_query = {"range": {"timestamp": {}}}
                if filters.date_from:
                    range_query["range"]["timestamp"]["gte"] = filters.date_from.isoformat()
                if filters.date_to:
                    range_query["range"]["timestamp"]["lte"] = filters.date_to.isoformat()
                query["bool"]["must"].append(range_query)

            if filters.user:
                query["bool"]["must"].append({"term": {"user": filters.user}})

            if filters.action_type:
                query["bool"]["must"].append({"term": {"action_type": filters.action_type.value}})

            if filters.target:
                query["bool"]["must"].append({"wildcard": {"target": f"*{filters.target.lower()}*"}})

            if filters.outcome:
                query["bool"]["must"].append({"term": {"outcome": filters.outcome.value}})

        if not query["bool"]["must"]:
            query = {"match_all": {}}

        try:
            response = await self.os_client.search(
                index=self._index_name,
                body={
                    "query": query,
                    "from": (page - 1) * page_size,
                    "size": page_size,
                    "sort": [{"timestamp": "desc"}]
                }
            )

            logs = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                source["action_type"] = AuditActionType(source["action_type"])
                source["outcome"] = AuditOutcome(source["outcome"])
                source["timestamp"] = datetime.fromisoformat(source["timestamp"].replace("Z", ""))
                logs.append(AuditLog(**source))

            total = response["hits"]["total"]["value"]
            return logs, total

        except Exception:
            return [], 0

    async def _get_unique_users_opensearch(self) -> List[str]:
        """Get unique users from OpenSearch."""
        if not self.os_client:
            return []

        try:
            response = await self.os_client.search(
                index=self._index_name,
                body={
                    "size": 0,
                    "aggs": {
                        "unique_users": {
                            "terms": {"field": "user", "size": 1000}
                        }
                    }
                }
            )

            buckets = response.get("aggregations", {}).get("unique_users", {}).get("buckets", [])
            return sorted([b["key"] for b in buckets])

        except Exception:
            return []


# Singleton instance
_service_instance: Optional[AuditService] = None


def get_audit_service() -> AuditService:
    """Get or create the audit service singleton."""
    global _service_instance
    if _service_instance is None:
        _service_instance = AuditService()
    return _service_instance
