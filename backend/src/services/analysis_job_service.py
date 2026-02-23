"""
Analysis Job Service.

Task: T-1.2.005, T-1.2.006, T-1.2.007, T-1.2.009
Requirements: REQ-001-002-001 to REQ-001-002-005

Provides business logic for managing analysis jobs in the queue.
Jobs are stored in-memory initially, with PostgreSQL persistence added later.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

from src.models.analysis_job import AnalysisJob, JobStatus


class AnalysisJobService:
    """
    Service for managing analysis jobs.
    
    Handles job creation, status tracking, and result retrieval.
    Initial implementation uses in-memory storage.
    """

    def __init__(self):
        """Initialize the job service with in-memory storage."""
        self._jobs: Dict[str, Dict[str, Any]] = {}

    async def create_job(
        self,
        job_type: str,
        payload: Dict[str, Any],
        priority: int = 5,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new analysis job.

        Args:
            job_type: Type of analysis to perform
            payload: Input data for the analysis
            priority: Job priority (1-10, 1 is highest)
            session_id: Optional session identifier

        Returns:
            Created job data as dict
        """
        job_id = f"job-{uuid4().hex[:12]}"
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=24)

        job = {
            "id": job_id,
            "job_type": job_type,
            "payload": payload,
            "status": JobStatus.PENDING.value,
            "result": None,
            "error": None,
            "progress": 0,
            "created_at": now.isoformat(),
            "started_at": None,
            "completed_at": None,
            "expires_at": expires_at.isoformat(),
            "session_id": session_id,
            "priority": priority,
        }

        self._jobs[job_id] = job
        return job

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a job by ID.

        Args:
            job_id: The job identifier

        Returns:
            Job data as dict, or None if not found
        """
        return self._jobs.get(job_id)

    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: int = None,
        result: Dict[str, Any] = None,
        error: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update job status and optionally result/error.

        Args:
            job_id: The job identifier
            status: New job status
            progress: Optional progress percentage (0-100)
            result: Optional result data (for completed jobs)
            error: Optional error message (for failed jobs)

        Returns:
            Updated job data, or None if not found
        """
        job = self._jobs.get(job_id)
        if not job:
            return None

        job["status"] = status.value
        
        if progress is not None:
            job["progress"] = progress

        if status == JobStatus.PROCESSING and job["started_at"] is None:
            job["started_at"] = datetime.utcnow().isoformat()

        if status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            job["completed_at"] = datetime.utcnow().isoformat()
            job["progress"] = 100 if status == JobStatus.COMPLETED else job["progress"]

        if result is not None:
            job["result"] = result

        if error is not None:
            job["error"] = error

        return job

    async def list_jobs(
        self,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List jobs, optionally filtered by status.

        Args:
            status: Optional status filter
            limit: Maximum number of jobs to return

        Returns:
            List of job data dicts
        """
        jobs = list(self._jobs.values())
        
        if status:
            jobs = [j for j in jobs if j["status"] == status]
        
        # Sort by created_at descending (newest first)
        jobs.sort(key=lambda j: j["created_at"], reverse=True)
        
        return jobs[:limit]

    async def delete_job(self, job_id: str) -> bool:
        """
        Delete a job by ID.

        Args:
            job_id: The job identifier

        Returns:
            True if deleted, False if not found
        """
        if job_id in self._jobs:
            del self._jobs[job_id]
            return True
        return False

    async def cleanup_expired_jobs(self) -> int:
        """
        Remove jobs older than 24 hours.

        REQ-001-002-006

        Returns:
            Number of jobs removed
        """
        now = datetime.utcnow()
        expired_ids = []

        for job_id, job in self._jobs.items():
            expires_at = datetime.fromisoformat(job["expires_at"])
            if expires_at < now:
                expired_ids.append(job_id)

        for job_id in expired_ids:
            del self._jobs[job_id]

        return len(expired_ids)


# Global singleton instance
job_service = AnalysisJobService()
