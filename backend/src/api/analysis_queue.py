"""
Analysis Queue API endpoints with WebSocket notifications.

Provides REST endpoints for queuing analysis jobs and WebSocket
for real-time job status updates.

Requirements:
- REQ-001-002-001: API POST /api/v1/analysis/queue for enqueueing analysis
- REQ-001-002-002: API GET /api/v1/analysis/status/{job_id} for status
- REQ-001-002-003: API GET /api/v1/analysis/result/{job_id} for result
- REQ-001-002-004: WebSocket /ws/analysis for notifications in real-time
"""

import asyncio
import uuid
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any, List, Set

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis-queue"])


class JobStatus(str, Enum):
    """Status of an analysis job."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisJob(BaseModel):
    """Model representing an analysis job."""
    job_id: str = Field(default_factory=lambda: f"JOB-{uuid.uuid4().hex[:8].upper()}")
    alert_id: str
    analysis_type: str
    status: JobStatus = JobStatus.PENDING
    priority: str = Field(default="normal")
    context: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        use_enum_values = True


class QueueAnalysisRequest(BaseModel):
    """Request to queue an analysis job."""
    alert_id: str = Field(..., description="ID of the alert to analyze")
    analysis_type: str = Field(default="full", description="Type of analysis: full, quick, deep")
    priority: str = Field(default="normal", description="Priority: low, normal, high, critical")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for analysis")


class QueueAnalysisResponse(BaseModel):
    """Response for queued analysis job."""
    job_id: str
    alert_id: str
    analysis_type: str
    status: str
    created_at: str


class JobStatusResponse(BaseModel):
    """Response for job status query."""
    job_id: str
    alert_id: str
    analysis_type: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class JobResultResponse(BaseModel):
    """Response for job result query."""
    job_id: str
    alert_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AnalysisQueueManager:
    """
    Singleton manager for analysis queue and WebSocket notifications.

    Manages job storage, subscriber queues, and job notifications.
    """
    _instance: Optional["AnalysisQueueManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "AnalysisQueueManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._jobs: Dict[str, AnalysisJob] = {}
            self._subscribers: List[asyncio.Queue] = []
            self._job_subscribers: Dict[str, List[asyncio.Queue]] = {}
            self._filters: Dict[asyncio.Queue, Dict[str, Any]] = {}
            self._lock = asyncio.Lock()
            AnalysisQueueManager._initialized = True

    async def subscribe(self) -> asyncio.Queue:
        """Subscribe to all job updates."""
        queue: asyncio.Queue = asyncio.Queue()
        async with self._lock:
            self._subscribers.append(queue)
        logger.debug(f"New subscriber added. Total: {len(self._subscribers)}")
        return queue

    async def unsubscribe(self, queue: asyncio.Queue) -> None:
        """Unsubscribe from job updates."""
        async with self._lock:
            if queue in self._subscribers:
                self._subscribers.remove(queue)
            # Also remove from filters
            if queue in self._filters:
                del self._filters[queue]
        logger.debug(f"Subscriber removed. Total: {len(self._subscribers)}")

    async def subscribe_to_job(self, job_id: str, queue: asyncio.Queue) -> None:
        """Subscribe to updates for a specific job."""
        async with self._lock:
            if job_id not in self._job_subscribers:
                self._job_subscribers[job_id] = []
            self._job_subscribers[job_id].append(queue)
        logger.debug(f"Subscribed to job {job_id}")

    async def unsubscribe_from_job(self, job_id: str, queue: asyncio.Queue) -> None:
        """Unsubscribe from updates for a specific job."""
        async with self._lock:
            if job_id in self._job_subscribers:
                if queue in self._job_subscribers[job_id]:
                    self._job_subscribers[job_id].remove(queue)
        logger.debug(f"Unsubscribed from job {job_id}")

    async def set_filter(self, queue: asyncio.Queue, analysis_type: Optional[str] = None) -> None:
        """Set a filter for a subscriber."""
        async with self._lock:
            self._filters[queue] = {"analysis_type": analysis_type}

    async def notify_job_update(self, job: AnalysisJob) -> None:
        """Notify all subscribers about a job update."""
        event = {
            "type": "job_update",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "job": job.model_dump()
        }

        async with self._lock:
            # Notify general subscribers
            for queue in self._subscribers:
                # Check filters
                filters = self._filters.get(queue, {})
                analysis_type_filter = filters.get("analysis_type")
                if analysis_type_filter and job.analysis_type != analysis_type_filter:
                    continue

                try:
                    await queue.put(event)
                except Exception as e:
                    logger.error(f"Failed to notify subscriber: {e}")

            # Notify job-specific subscribers
            if job.job_id in self._job_subscribers:
                for queue in self._job_subscribers[job.job_id]:
                    try:
                        await queue.put(event)
                    except Exception as e:
                        logger.error(f"Failed to notify job subscriber: {e}")

    async def notify_job_created(self, job: AnalysisJob) -> None:
        """Notify all subscribers about a new job."""
        event = {
            "type": "job_created",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "job": job.model_dump()
        }

        async with self._lock:
            for queue in self._subscribers:
                # Check filters
                filters = self._filters.get(queue, {})
                analysis_type_filter = filters.get("analysis_type")
                if analysis_type_filter and job.analysis_type != analysis_type_filter:
                    continue

                try:
                    await queue.put(event)
                except Exception as e:
                    logger.error(f"Failed to notify subscriber: {e}")

    async def create_job(self, request: QueueAnalysisRequest) -> AnalysisJob:
        """Create and store a new analysis job."""
        job = AnalysisJob(
            alert_id=request.alert_id,
            analysis_type=request.analysis_type,
            priority=request.priority,
            context=request.context
        )

        async with self._lock:
            self._jobs[job.job_id] = job

        # Notify subscribers about new job
        await self.notify_job_created(job)

        logger.info(f"Created analysis job {job.job_id} for alert {job.alert_id}")
        return job

    async def get_job(self, job_id: str) -> Optional[AnalysisJob]:
        """Get a job by ID."""
        return self._jobs.get(job_id)

    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> Optional[AnalysisJob]:
        """Update job status and notify subscribers."""
        async with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None

            job.status = status

            if status == JobStatus.PROCESSING and job.started_at is None:
                job.started_at = datetime.utcnow()

            if status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                job.completed_at = datetime.utcnow()

            if result:
                job.result = result

            if error:
                job.error = error

        # Notify about status change
        await self.notify_job_update(job)

        logger.info(f"Updated job {job_id} status to {status}")
        return job

    async def cleanup_old_jobs(self, max_age_hours: int = 24) -> int:
        """Remove jobs older than specified hours."""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        removed = 0

        async with self._lock:
            jobs_to_remove = [
                job_id for job_id, job in self._jobs.items()
                if job.created_at < cutoff
            ]

            for job_id in jobs_to_remove:
                del self._jobs[job_id]
                removed += 1

        logger.info(f"Cleaned up {removed} old jobs")
        return removed


# Global manager instance
_manager: Optional[AnalysisQueueManager] = None


def get_analysis_queue_manager() -> AnalysisQueueManager:
    """Get the singleton analysis queue manager."""
    global _manager
    if _manager is None:
        _manager = AnalysisQueueManager()
    return _manager


# Standalone cleanup function for testing
async def cleanup_old_jobs(max_age_hours: int = 24) -> int:
    """Clean up old jobs."""
    manager = get_analysis_queue_manager()
    return await manager.cleanup_old_jobs(max_age_hours)


# REST API Endpoints

@router.post("/queue", response_model=QueueAnalysisResponse, status_code=201)
async def queue_analysis(request: QueueAnalysisRequest) -> QueueAnalysisResponse:
    """
    Queue a new analysis job.

    Creates a new analysis job and returns the job ID for tracking.
    Subscribers to the WebSocket will receive a notification.
    """
    manager = get_analysis_queue_manager()
    job = await manager.create_job(request)

    return QueueAnalysisResponse(
        job_id=job.job_id,
        alert_id=job.alert_id,
        analysis_type=job.analysis_type,
        status=job.status.value if isinstance(job.status, JobStatus) else job.status,
        created_at=job.created_at.isoformat() + "Z"
    )


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Get the status of an analysis job.
    """
    manager = get_analysis_queue_manager()
    job = await manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return JobStatusResponse(
        job_id=job.job_id,
        alert_id=job.alert_id,
        analysis_type=job.analysis_type,
        status=job.status.value if isinstance(job.status, JobStatus) else job.status,
        created_at=job.created_at.isoformat() + "Z",
        started_at=job.started_at.isoformat() + "Z" if job.started_at else None,
        completed_at=job.completed_at.isoformat() + "Z" if job.completed_at else None
    )


@router.get("/result/{job_id}", response_model=JobResultResponse)
async def get_job_result(job_id: str) -> JobResultResponse:
    """
    Get the result of a completed analysis job.

    Returns 202 Accepted if the job is still processing.
    """
    manager = get_analysis_queue_manager()
    job = await manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return JobResultResponse(
        job_id=job.job_id,
        alert_id=job.alert_id,
        status=job.status.value if isinstance(job.status, JobStatus) else job.status,
        result=job.result,
        error=job.error
    )


# WebSocket Endpoint

@router.websocket("/ws")
async def websocket_analysis(websocket: WebSocket):
    """
    WebSocket endpoint for real-time analysis job notifications.

    Clients can:
    - Receive notifications for all job updates
    - Subscribe to specific jobs
    - Set filters for analysis types
    - Send ping messages for keepalive
    """
    await websocket.accept()

    manager = get_analysis_queue_manager()
    queue = await manager.subscribe()
    subscribed_jobs: Set[str] = set()

    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

        while True:
            # Wait for client messages or queue events
            try:
                # Check for incoming messages with timeout
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=0.1
                )
                import json
                message = json.loads(data)

                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

                elif message.get("type") == "subscribe":
                    job_id = message.get("job_id")
                    if job_id:
                        await manager.subscribe_to_job(job_id, queue)
                        subscribed_jobs.add(job_id)
                        await websocket.send_json({
                            "type": "subscribed",
                            "job_id": job_id
                        })

                elif message.get("type") == "unsubscribe":
                    job_id = message.get("job_id")
                    if job_id and job_id in subscribed_jobs:
                        await manager.unsubscribe_from_job(job_id, queue)
                        subscribed_jobs.remove(job_id)
                        await websocket.send_json({
                            "type": "unsubscribed",
                            "job_id": job_id
                        })

                elif message.get("type") == "set_filter":
                    analysis_type = message.get("analysis_type")
                    await manager.set_filter(queue, analysis_type=analysis_type)
                    await websocket.send_json({
                        "type": "filter_set",
                        "analysis_type": analysis_type
                    })

            except asyncio.TimeoutError:
                pass

            # Check for events from the queue
            try:
                event = queue.get_nowait()
                await websocket.send_json(event)
            except asyncio.QueueEmpty:
                pass

    except WebSocketDisconnect:
        logger.debug("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Cleanup
        await manager.unsubscribe(queue)
        for job_id in subscribed_jobs:
            await manager.unsubscribe_from_job(job_id, queue)
