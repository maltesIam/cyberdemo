"""
Playbook API Endpoints.

REST API for managing and executing SOAR playbooks.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from ..services.playbook_service import (
    get_playbook_service,
    PlaybookNotFoundError,
    PlaybookError,
)


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
