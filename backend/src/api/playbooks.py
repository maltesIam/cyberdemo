"""
Playbook API Endpoints.

REST API for managing and executing SOAR playbooks.

Implements:
- REQ-005-001-001: POST /api/v1/playbooks/execute/{playbook_id}
- REQ-005-001-002: POST /api/v1/playbooks/{execution_id}/pause
- REQ-005-001-003: POST /api/v1/playbooks/{execution_id}/resume
- REQ-005-001-004: POST /api/v1/playbooks/{execution_id}/rollback
- REQ-005-001-005: GET /api/v1/playbooks/{execution_id}/status
- REQ-005-001-006: State persistence in PostgreSQL

Tasks: T-2.3.002, T-2.3.003, T-2.3.004, T-2.3.005, T-2.3.006
Agent: build-3
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.playbook_service import (
    get_playbook_service,
    PlaybookNotFoundError,
    PlaybookError,
)
from ..services.playbook_execution_service import (
    PlaybookExecutionService,
    PlaybookExecutionError,
    PlaybookExecutionNotFoundError,
    get_playbook_execution_service,
)
from ..core.database import get_db


router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class PlaybookStepModel(BaseModel):
    """Model for a playbook step."""
    action: str = Field(..., description="Action to execute (e.g., 'edr.contain_host')")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the action")
    timeout: int = Field(default=120, description="Timeout in seconds")
    on_error: str = Field(default="fail", description="Error handling: fail, continue, notify_human")


class PlaybookModel(BaseModel):
    """Model for a playbook."""
    id: str
    name: str
    description: str
    triggers: List[str]
    steps: List[PlaybookStepModel]
    enabled: bool = True


class PlaybookListResponse(BaseModel):
    """Response for listing playbooks."""
    playbooks: List[PlaybookModel]
    total: int


class PlaybookCreateRequest(BaseModel):
    """Request to create a new playbook."""
    name: str = Field(..., description="Unique playbook name")
    description: str = Field(..., description="Description of the playbook")
    triggers: List[str] = Field(default_factory=list, description="Events that trigger this playbook")
    steps: List[PlaybookStepModel] = Field(..., description="Steps to execute")
    enabled: bool = Field(default=True, description="Whether the playbook is active")


class PlaybookRunRequest(BaseModel):
    """Request to execute a playbook."""
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Context data for variable interpolation"
    )
    triggered_by: Optional[str] = Field(None, description="What triggered this run")


class StepResultModel(BaseModel):
    """Model for a step execution result."""
    step_index: int
    action: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: Optional[int] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class PlaybookRunModel(BaseModel):
    """Model for a playbook run."""
    id: str
    playbook_id: str
    playbook_name: str
    status: str
    context: Dict[str, Any]
    step_results: List[StepResultModel]
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    triggered_by: Optional[str] = None
    error: Optional[str] = None


class PlaybookRunListResponse(BaseModel):
    """Response for listing playbook runs."""
    runs: List[PlaybookRunModel]
    total: int


# ============================================================================
# Playbook Execution Models (for PostgreSQL-persisted executions)
# ============================================================================

class ExecutePlaybookRequest(BaseModel):
    """Request to execute a playbook with persistence (REQ-005-001-001)."""
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Context data for variable interpolation"
    )
    triggered_by: Optional[str] = Field(None, description="What triggered this execution")
    session_id: Optional[str] = Field(None, description="Session ID for grouping executions")


class PlaybookExecutionResponse(BaseModel):
    """Response for playbook execution endpoints."""
    id: str
    playbook_id: str
    playbook_name: str
    status: str
    current_step: int
    total_steps: int
    progress: int
    context: Dict[str, Any] = Field(default_factory=dict)
    step_results: Optional[List[Dict[str, Any]]] = None
    rollback_data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    triggered_by: Optional[str] = None
    session_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    started_at: Optional[str] = None
    paused_at: Optional[str] = None
    completed_at: Optional[str] = None


class PlaybookExecutionListResponse(BaseModel):
    """Response for listing playbook executions."""
    executions: List[PlaybookExecutionResponse]
    total: int


# ============================================================================
# Helper Functions
# ============================================================================

def playbook_to_model(playbook) -> PlaybookModel:
    """Convert a Playbook to API model."""
    return PlaybookModel(
        id=playbook.id,
        name=playbook.name,
        description=playbook.description,
        triggers=playbook.triggers,
        steps=[
            PlaybookStepModel(
                action=step.action,
                params=step.params,
                timeout=step.timeout,
                on_error=step.on_error
            )
            for step in playbook.steps
        ],
        enabled=playbook.enabled
    )


def run_to_model(run) -> PlaybookRunModel:
    """Convert a PlaybookRun to API model."""
    return PlaybookRunModel(
        id=run.id,
        playbook_id=run.playbook_id,
        playbook_name=run.playbook_name,
        status=run.status.value,
        context=run.context,
        step_results=[
            StepResultModel(
                step_index=r.step_index,
                action=r.action,
                status=r.status.value,
                result=r.result,
                error=r.error,
                duration_ms=r.duration_ms,
                started_at=r.started_at.isoformat() if r.started_at else None,
                completed_at=r.completed_at.isoformat() if r.completed_at else None
            )
            for r in run.step_results
        ],
        started_at=run.started_at.isoformat() if run.started_at else None,
        completed_at=run.completed_at.isoformat() if run.completed_at else None,
        triggered_by=run.triggered_by,
        error=run.error
    )


# ============================================================================
# Endpoints
# ============================================================================

@router.get("", response_model=PlaybookListResponse)
async def list_playbooks(
    trigger: Optional[str] = Query(None, description="Filter by trigger event")
) -> PlaybookListResponse:
    """
    List all available playbooks.

    Optionally filter by trigger event to find playbooks that would be
    triggered by a specific event type.
    """
    service = get_playbook_service()

    if trigger:
        playbooks = service.get_playbooks_by_trigger(trigger)
    else:
        playbooks = service.list_playbooks()

    return PlaybookListResponse(
        playbooks=[playbook_to_model(p) for p in playbooks],
        total=len(playbooks)
    )


@router.post("", response_model=PlaybookModel, status_code=201)
async def create_playbook(request: PlaybookCreateRequest) -> PlaybookModel:
    """
    Create a new playbook.

    The playbook will be saved to the playbooks directory as a YAML file
    and immediately available for execution.
    """
    service = get_playbook_service()

    try:
        playbook = service.create_playbook(
            name=request.name,
            description=request.description,
            triggers=request.triggers,
            steps=[step.model_dump() for step in request.steps],
            enabled=request.enabled
        )
        return playbook_to_model(playbook)

    except PlaybookError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{playbook_id}", response_model=PlaybookModel)
async def get_playbook(playbook_id: str) -> PlaybookModel:
    """
    Get a specific playbook by ID.
    """
    service = get_playbook_service()

    try:
        playbook = service.get_playbook_by_id(playbook_id)
        return playbook_to_model(playbook)

    except PlaybookNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{playbook_id}/runs", response_model=PlaybookRunListResponse)
async def list_playbook_runs(
    playbook_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Maximum results to return")
) -> PlaybookRunListResponse:
    """
    Get execution history for a specific playbook.

    Returns all runs for the playbook, sorted by start time descending.
    """
    service = get_playbook_service()

    # Verify playbook exists
    try:
        service.get_playbook_by_id(playbook_id)
    except PlaybookNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    runs = service.list_runs(playbook_id=playbook_id, limit=limit)

    return PlaybookRunListResponse(
        runs=[run_to_model(r) for r in runs],
        total=len(runs)
    )


@router.post("/{playbook_id}/run", response_model=PlaybookRunModel, status_code=201)
async def execute_playbook(
    playbook_id: str,
    request: PlaybookRunRequest
) -> PlaybookRunModel:
    """
    Execute a playbook with the given context.

    The context dictionary is used for variable interpolation in playbook steps.
    For example, if a step has params like {"reason": "${incident.title}"},
    the context should contain {"incident": {"title": "Malware detected"}}.

    Returns the execution result including status and step results.
    """
    service = get_playbook_service()

    try:
        run = await service.execute_playbook_by_id(
            playbook_id=playbook_id,
            context=request.context,
            triggered_by=request.triggered_by
        )
        return run_to_model(run)

    except PlaybookNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@router.get("/runs/{run_id}", response_model=PlaybookRunModel)
async def get_playbook_run(run_id: str) -> PlaybookRunModel:
    """
    Get details of a specific playbook run.
    """
    service = get_playbook_service()

    run = service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")

    return run_to_model(run)


# ============================================================================
# Persistent Playbook Execution Endpoints (PostgreSQL-backed)
# ============================================================================

def _dict_to_execution_response(data: Dict[str, Any]) -> PlaybookExecutionResponse:
    """Convert execution dictionary to response model."""
    return PlaybookExecutionResponse(
        id=data.get("id", ""),
        playbook_id=data.get("playbook_id", ""),
        playbook_name=data.get("playbook_name", ""),
        status=data.get("status", "unknown"),
        current_step=data.get("current_step", 0),
        total_steps=data.get("total_steps", 0),
        progress=data.get("progress", 0),
        context=data.get("context", {}),
        step_results=data.get("step_results"),
        rollback_data=data.get("rollback_data"),
        error=data.get("error"),
        triggered_by=data.get("triggered_by"),
        session_id=data.get("session_id"),
        created_at=data.get("created_at"),
        updated_at=data.get("updated_at"),
        started_at=data.get("started_at"),
        paused_at=data.get("paused_at"),
        completed_at=data.get("completed_at"),
    )


@router.post("/execute/{playbook_id}", response_model=PlaybookExecutionResponse, status_code=201)
async def execute_playbook(
    playbook_id: str,
    request: ExecutePlaybookRequest,
    db: AsyncSession = Depends(get_db)
) -> PlaybookExecutionResponse:
    """
    Execute a playbook with persistent state tracking (REQ-005-001-001).

    Creates a new execution record in PostgreSQL and starts execution.
    The execution state persists between sessions (BR-019).

    Args:
        playbook_id: ID of the playbook to execute.
        request: Execution request with context and options.

    Returns:
        The execution record with status and progress.
    """
    playbook_service = get_playbook_service()
    execution_service = PlaybookExecutionService(
        db_session=db,
        playbook_service=playbook_service
    )

    try:
        result = await execution_service.execute_playbook(
            playbook_id=playbook_id,
            context=request.context,
            triggered_by=request.triggered_by,
            session_id=request.session_id
        )
        return _dict_to_execution_response(result)

    except PlaybookExecutionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/executions/{execution_id}/pause", response_model=PlaybookExecutionResponse)
async def pause_playbook(
    execution_id: str,
    db: AsyncSession = Depends(get_db)
) -> PlaybookExecutionResponse:
    """
    Pause a running playbook execution (REQ-005-001-002).

    The execution can be resumed later with the resume endpoint.
    The current state is persisted in PostgreSQL.

    Args:
        execution_id: ID of the execution to pause.

    Returns:
        The updated execution record with status=paused.

    Raises:
        HTTPException: If execution is not running or not found.
    """
    playbook_service = get_playbook_service()
    execution_service = PlaybookExecutionService(
        db_session=db,
        playbook_service=playbook_service
    )

    try:
        result = await execution_service.pause_execution(execution_id)
        return _dict_to_execution_response(result)

    except PlaybookExecutionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except PlaybookExecutionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/executions/{execution_id}/resume", response_model=PlaybookExecutionResponse)
async def resume_playbook(
    execution_id: str,
    db: AsyncSession = Depends(get_db)
) -> PlaybookExecutionResponse:
    """
    Resume a paused playbook execution (REQ-005-001-003).

    Continues execution from where it was paused.

    Args:
        execution_id: ID of the execution to resume.

    Returns:
        The updated execution record with status=running.

    Raises:
        HTTPException: If execution is not paused or not found.
    """
    playbook_service = get_playbook_service()
    execution_service = PlaybookExecutionService(
        db_session=db,
        playbook_service=playbook_service
    )

    try:
        result = await execution_service.resume_execution(execution_id)
        return _dict_to_execution_response(result)

    except PlaybookExecutionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except PlaybookExecutionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/executions/{execution_id}/rollback", response_model=PlaybookExecutionResponse)
async def rollback_playbook(
    execution_id: str,
    db: AsyncSession = Depends(get_db)
) -> PlaybookExecutionResponse:
    """
    Rollback a completed playbook execution (REQ-005-001-004).

    Executes undo actions for all completed steps in reverse order.
    Implements BR-018: Destructive actions require human approval.

    Args:
        execution_id: ID of the execution to rollback.

    Returns:
        The updated execution record with status=rolled_back.

    Raises:
        HTTPException: If execution cannot be rolled back or not found.
    """
    playbook_service = get_playbook_service()
    execution_service = PlaybookExecutionService(
        db_session=db,
        playbook_service=playbook_service
    )

    try:
        result = await execution_service.rollback_execution(execution_id)
        return _dict_to_execution_response(result)

    except PlaybookExecutionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except PlaybookExecutionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/executions/{execution_id}/status", response_model=PlaybookExecutionResponse)
async def get_playbook_status(
    execution_id: str,
    db: AsyncSession = Depends(get_db)
) -> PlaybookExecutionResponse:
    """
    Get the status of a playbook execution (REQ-005-001-005).

    Returns full execution details including progress, step results,
    and rollback data.

    Args:
        execution_id: ID of the execution.

    Returns:
        The execution record with full status details.

    Raises:
        HTTPException: If execution not found.
    """
    playbook_service = get_playbook_service()
    execution_service = PlaybookExecutionService(
        db_session=db,
        playbook_service=playbook_service
    )

    try:
        result = await execution_service.get_execution(execution_id)
        return _dict_to_execution_response(result)

    except PlaybookExecutionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/executions", response_model=PlaybookExecutionListResponse)
async def list_playbook_executions(
    playbook_id: Optional[str] = Query(None, description="Filter by playbook ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    db: AsyncSession = Depends(get_db)
) -> PlaybookExecutionListResponse:
    """
    List all playbook executions with optional filtering.

    Args:
        playbook_id: Filter by playbook ID.
        status: Filter by execution status.
        session_id: Filter by session ID.
        limit: Maximum number of results.

    Returns:
        List of execution records.
    """
    playbook_service = get_playbook_service()
    execution_service = PlaybookExecutionService(
        db_session=db,
        playbook_service=playbook_service
    )

    executions = await execution_service.list_executions(
        playbook_id=playbook_id,
        status=status,
        session_id=session_id,
        limit=limit
    )

    return PlaybookExecutionListResponse(
        executions=[_dict_to_execution_response(e) for e in executions],
        total=len(executions)
    )
