"""
Analysis Queue API endpoints.

Task: T-1.2.005, T-1.2.006, T-1.2.007
Requirements: REQ-001-002-001, REQ-001-002-002, REQ-001-002-003

Provides endpoints for queueing analysis jobs and retrieving their status/results.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List

from src.models.analysis_job import (
    AnalysisJobCreateRequest,
    AnalysisJobResponse,
    AnalysisJobQueueResponse,
)
from src.services.analysis_job_service import job_service


router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


async def queue_analysis(request: AnalysisJobCreateRequest) -> AnalysisJobQueueResponse:
    """
    Queue a new analysis job (REQ-001-002-001).

    Creates a new analysis job in the queue and returns a job_id for tracking.
    The job will be processed asynchronously by the agent.

    Args:
        request: Job creation request with type and payload

    Returns:
        Response with job_id and initial status
    """
    job = await job_service.create_job(
        job_type=request.job_type,
        payload=request.payload,
        priority=request.priority,
        session_id=request.session_id
    )

    return AnalysisJobQueueResponse(
        job_id=job["id"],
        status=job["status"],
        message="Analysis job queued successfully"
    )


async def get_job_status(job_id: str) -> AnalysisJobResponse:
    """
    Get the status of an analysis job (REQ-001-002-002).

    Returns the current status and progress of a job.

    Args:
        job_id: The job identifier

    Returns:
        Job status response

    Raises:
        HTTPException: 404 if job not found
    """
    job = await job_service.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    return AnalysisJobResponse(
        id=job["id"],
        job_type=job["job_type"],
        status=job["status"],
        progress=job["progress"],
        payload=job.get("payload"),
        created_at=job.get("created_at"),
        started_at=job.get("started_at"),
        completed_at=job.get("completed_at")
    )


async def get_job_result(job_id: str) -> AnalysisJobResponse:
    """
    Get the result of an analysis job (REQ-001-002-003).

    Returns the full job data including result (if completed) or error (if failed).

    Args:
        job_id: The job identifier

    Returns:
        Job response with result or error

    Raises:
        HTTPException: 404 if job not found
    """
    job = await job_service.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    return AnalysisJobResponse(
        id=job["id"],
        job_type=job["job_type"],
        status=job["status"],
        progress=job["progress"],
        payload=job.get("payload"),
        result=job.get("result"),
        error=job.get("error"),
        created_at=job.get("created_at"),
        started_at=job.get("started_at"),
        completed_at=job.get("completed_at")
    )


async def list_jobs(
    status_filter: str = None,
    limit: int = 100
) -> List[AnalysisJobResponse]:
    """
    List all analysis jobs.

    Args:
        status_filter: Optional status to filter by
        limit: Maximum number of jobs to return

    Returns:
        List of job responses
    """
    jobs = await job_service.list_jobs(status=status_filter, limit=limit)

    return [
        AnalysisJobResponse(
            id=job["id"],
            job_type=job["job_type"],
            status=job["status"],
            progress=job["progress"],
            created_at=job.get("created_at"),
            started_at=job.get("started_at"),
            completed_at=job.get("completed_at")
        )
        for job in jobs
    ]


async def cancel_job(job_id: str) -> AnalysisJobResponse:
    """
    Cancel a pending or processing job.

    Args:
        job_id: The job identifier

    Returns:
        Updated job response

    Raises:
        HTTPException: 404 if job not found, 400 if already completed
    """
    from src.models.analysis_job import JobStatus

    job = await job_service.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    if job["status"] in ("completed", "failed", "cancelled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job in status: {job['status']}"
        )

    updated_job = await job_service.update_job_status(
        job_id=job_id,
        status=JobStatus.CANCELLED
    )

    return AnalysisJobResponse(
        id=updated_job["id"],
        job_type=updated_job["job_type"],
        status=updated_job["status"],
        progress=updated_job["progress"],
        created_at=updated_job.get("created_at"),
        completed_at=updated_job.get("completed_at")
    )


# Register routes on the router
@router.post("/queue", response_model=AnalysisJobQueueResponse)
async def queue_analysis_endpoint(request: AnalysisJobCreateRequest):
    """Queue a new analysis job."""
    return await queue_analysis(request)


@router.get("/status/{job_id}", response_model=AnalysisJobResponse)
async def get_status_endpoint(job_id: str):
    """Get job status."""
    return await get_job_status(job_id)


@router.get("/result/{job_id}", response_model=AnalysisJobResponse)
async def get_result_endpoint(job_id: str):
    """Get job result."""
    return await get_job_result(job_id)


@router.get("/jobs", response_model=List[AnalysisJobResponse])
async def list_jobs_endpoint(status: str = None, limit: int = 100):
    """List all jobs."""
    return await list_jobs(status_filter=status, limit=limit)


@router.post("/cancel/{job_id}", response_model=AnalysisJobResponse)
async def cancel_job_endpoint(job_id: str):
    """Cancel a job."""
    return await cancel_job(job_id)
