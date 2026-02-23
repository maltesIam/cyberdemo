"""
Persistent Job Service using PostgreSQL.

Task: T-1.2.009
Requirement: REQ-001-002-005 - Job persistence in PostgreSQL

Provides database-backed job management with persistence.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.models.analysis_job_db import AnalysisJobDB, AnalysisJobStatus, AnalysisJobType


def utcnow() -> datetime:
    """Return current UTC time as a naive datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


# Mapping from string job types to enum values
JOB_TYPE_MAP = {
    "alert_analysis": AnalysisJobType.ALERT_ANALYSIS,
    "ioc_investigation": AnalysisJobType.IOC_INVESTIGATION,
    "event_correlation": AnalysisJobType.EVENT_CORRELATION,
    "report_generation": AnalysisJobType.REPORT_GENERATION,
    "recommendation": AnalysisJobType.ACTION_RECOMMENDATION,
    "action_recommendation": AnalysisJobType.ACTION_RECOMMENDATION,
    "decision_explanation": AnalysisJobType.ALERT_ANALYSIS,  # Map to closest
}


class PersistentJobService:
    """
    Database-backed job service.

    Manages analysis jobs with PostgreSQL persistence.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize with database session.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def create_job(
        self,
        job_type: str,
        payload: Dict[str, Any],
        priority: int = 5,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create and persist a new analysis job.

        Args:
            job_type: Type of analysis to perform
            payload: Input data for the analysis
            priority: Job priority (1-10, 1 is highest)
            session_id: Optional session identifier

        Returns:
            Created job data as dict
        """
        # Convert string job type to enum
        job_type_enum = JOB_TYPE_MAP.get(job_type, AnalysisJobType.ALERT_ANALYSIS)

        job = AnalysisJobDB(
            id=str(uuid4()),
            job_type=job_type_enum,
            payload=payload,
            status=AnalysisJobStatus.PENDING,
            priority=priority,
            session_id=session_id,
        )

        self._session.add(job)
        await self._session.flush()
        await self._session.refresh(job)

        return job.to_dict()

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a job by ID from database.

        Args:
            job_id: The job identifier

        Returns:
            Job data as dict, or None if not found
        """
        job = await self._session.get(AnalysisJobDB, job_id)
        if job:
            return job.to_dict()
        return None

    async def update_job_status(
        self,
        job_id: str,
        status: AnalysisJobStatus,
        result: Dict[str, Any] = None,
        error: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update job status in database.

        Args:
            job_id: The job identifier
            status: New job status
            result: Optional result data (for completed jobs)
            error: Optional error message (for failed jobs)

        Returns:
            Updated job data, or None if not found
        """
        job = await self._session.get(AnalysisJobDB, job_id)
        if not job:
            return None

        job.status = status

        if status == AnalysisJobStatus.PROCESSING and job.started_at is None:
            job.started_at = utcnow()

        if status in (AnalysisJobStatus.COMPLETED, AnalysisJobStatus.FAILED, AnalysisJobStatus.CANCELLED):
            job.completed_at = utcnow()

        if result is not None:
            job.result = result

        if error is not None:
            job.error_message = error

        await self._session.flush()
        return job.to_dict()

    async def list_jobs(
        self,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List jobs from database.

        Args:
            status: Optional status filter
            limit: Maximum number of jobs to return

        Returns:
            List of job data dicts
        """
        query = select(AnalysisJobDB).order_by(AnalysisJobDB.created_at.desc()).limit(limit)

        if status:
            status_enum = AnalysisJobStatus(status)
            query = query.where(AnalysisJobDB.status == status_enum)

        result = await self._session.execute(query)
        jobs = result.scalars().all()

        return [job.to_dict() for job in jobs]

    async def delete_job(self, job_id: str) -> bool:
        """
        Delete a job from database.

        Args:
            job_id: The job identifier

        Returns:
            True if deleted, False if not found
        """
        job = await self._session.get(AnalysisJobDB, job_id)
        if job:
            await self._session.delete(job)
            await self._session.flush()
            return True
        return False

    async def cleanup_expired_jobs(self, max_age_hours: int = 24) -> int:
        """
        Remove jobs older than specified age.

        REQ-001-002-006

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            Number of jobs removed
        """
        from datetime import timedelta

        cutoff = utcnow() - timedelta(hours=max_age_hours)

        stmt = delete(AnalysisJobDB).where(AnalysisJobDB.created_at < cutoff)
        result = await self._session.execute(stmt)

        return result.rowcount
