"""Audit API endpoints for compliance tracking."""
from fastapi import APIRouter, Query, Response
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime
import io

from ..models.audit import (
    AuditLogResponse,
    AuditLogFilter,
    AuditActionType,
    AuditOutcome,
    AuditExportFormat,
)
from ..services.audit_service import get_audit_service

router = APIRouter(tags=["Audit"])


@router.get("/logs", response_model=AuditLogResponse)
async def list_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter until date"),
    user: Optional[str] = Query(None, description="Filter by user"),
    action_type: Optional[AuditActionType] = Query(None, description="Filter by action type"),
    target: Optional[str] = Query(None, description="Filter by target (partial match)"),
    outcome: Optional[AuditOutcome] = Query(None, description="Filter by outcome"),
):
    """List audit logs with filtering and pagination."""
    service = get_audit_service()

    filters = AuditLogFilter(
        date_from=date_from,
        date_to=date_to,
        user=user,
        action_type=action_type,
        target=target,
        outcome=outcome,
    )

    logs, total = await service.get_logs(filters, page, page_size)

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return AuditLogResponse(
        data=logs,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/logs/export")
async def export_audit_logs(
    format: AuditExportFormat = Query(AuditExportFormat.CSV, description="Export format"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter until date"),
    user: Optional[str] = Query(None, description="Filter by user"),
    action_type: Optional[AuditActionType] = Query(None, description="Filter by action type"),
    target: Optional[str] = Query(None, description="Filter by target (partial match)"),
    outcome: Optional[AuditOutcome] = Query(None, description="Filter by outcome"),
):
    """Export audit logs as CSV or JSON for compliance."""
    service = get_audit_service()

    filters = AuditLogFilter(
        date_from=date_from,
        date_to=date_to,
        user=user,
        action_type=action_type,
        target=target,
        outcome=outcome,
    )

    data, content_type = await service.export_logs(format, filters)

    # Set filename based on format
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    extension = "csv" if format == AuditExportFormat.CSV else "json"
    filename = f"audit_logs_{timestamp}.{extension}"

    return StreamingResponse(
        io.StringIO(data),
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
        },
    )


@router.get("/users")
async def list_audit_users():
    """Get list of unique users in audit logs for filtering."""
    service = get_audit_service()
    users = await service.get_users()
    return {"users": users}


@router.get("/action-types")
async def list_action_types():
    """Get list of available action types for filtering."""
    return {
        "action_types": [
            {"value": t.value, "label": t.value.replace("_", " ").title()}
            for t in AuditActionType
        ]
    }


@router.get("/outcomes")
async def list_outcomes():
    """Get list of possible outcomes for filtering."""
    return {
        "outcomes": [
            {"value": o.value, "label": o.value.title()}
            for o in AuditOutcome
        ]
    }
