"""
SOAR (Security Orchestration, Automation and Response) API Endpoints.

Provides REST API for executing playbooks and managing actions.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from ..services.soar_service import get_soar_service, validate_action

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class ActionRequest(BaseModel):
    """Request model for executing a SOAR action."""
    action: str = Field(..., description="Action type: contain, kill_process, etc.")
    device_id: str = Field(..., description="Target device identifier")
    reason: str = Field(..., description="Reason for the action")
    process_id: Optional[int] = Field(None, description="Process ID for kill_process action")


class ActionResponse(BaseModel):
    """Response model for action execution."""
    action_id: str
    action: str
    device_id: str
    status: str
    reason: str
    timestamp: str
    actor: str
    process_id: Optional[int] = None
    process_terminated: Optional[bool] = None


class ActionListResponse(BaseModel):
    """Response model for listing actions."""
    actions: List[ActionResponse]
    total: int


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/actions", response_model=ActionResponse, status_code=201)
async def run_playbook(request: ActionRequest) -> ActionResponse:
    """
    Execute a SOAR playbook action.

    Supported actions:
    - **contain**: Network isolation of a host
    - **kill_process**: Terminate a malicious process
    - **isolate**: Full host isolation
    - **scan**: Run AV/EDR scan
    - **collect_logs**: Gather forensic logs
    - **block_hash**: Block file hash org-wide
    - **disable_user**: Disable AD user account

    Returns action result with status.
    """
    service = get_soar_service()

    # Validate action type
    if not validate_action(request.action):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action: {request.action}. Valid actions: contain, kill_process, isolate, scan, collect_logs, block_hash, disable_user"
        )

    try:
        result = await service.execute_action(
            action=request.action,
            device_id=request.device_id,
            reason=request.reason,
            process_id=request.process_id,
            actor="system"
        )
        return ActionResponse(**result)

    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/actions/{action_id}", response_model=ActionResponse)
async def get_action(action_id: str) -> ActionResponse:
    """
    Get details of a specific SOAR action.

    Returns the action details including timestamp, status, and actor.
    """
    service = get_soar_service()
    result = await service.get_action(action_id)

    if not result:
        raise HTTPException(status_code=404, detail=f"Action not found: {action_id}")

    return ActionResponse(**result)


@router.get("/actions", response_model=ActionListResponse)
async def list_actions(
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results")
) -> ActionListResponse:
    """
    List SOAR actions with optional filtering.

    Filter by device_id or action type. Results sorted by timestamp descending.
    """
    service = get_soar_service()
    actions = await service.list_actions(
        device_id=device_id,
        action_type=action,
        limit=limit
    )

    return ActionListResponse(
        actions=[ActionResponse(**a) for a in actions],
        total=len(actions)
    )
