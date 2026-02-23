"""
Job Cleanup Scheduler.

Task: T-1.2.010
Requirement: REQ-001-002-006 - Limpieza automatica de jobs > 24h

Provides scheduled cleanup of expired analysis jobs.
"""

import asyncio
import logging
from typing import Optional

from src.services.analysis_job_service import AnalysisJobService

logger = logging.getLogger(__name__)


class JobCleanupScheduler:
    """
    Scheduler for cleaning up expired analysis jobs.

    Runs periodically to remove jobs older than configured max age.
    Default is to run every hour and remove jobs older than 24 hours.
    """

    def __init__(
        self,
        interval_seconds: int = 3600,
        max_age_hours: int = 24
    ):
        """
        Initialize the cleanup scheduler.

        Args:
            interval_seconds: How often to run cleanup (default 1 hour)
            max_age_hours: Remove jobs older than this (default 24 hours)
        """
        self.interval_seconds = interval_seconds
        self.max_age_hours = max_age_hours
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def cleanup_expired_jobs(
        self,
        job_service: AnalysisJobService
    ) -> int:
        """
        Run a single cleanup of expired jobs.

        Args:
            job_service: The job service to use for cleanup

        Returns:
            Number of jobs removed
        """
        try:
            removed = await job_service.cleanup_expired_jobs(self.max_age_hours)
            if removed > 0:
                logger.info(f"Cleaned up {removed} expired jobs")
            return removed
        except Exception as e:
            logger.error(f"Error during job cleanup: {e}")
            return 0

    async def _run_loop(self, job_service: AnalysisJobService):
        """Internal loop that runs cleanup periodically."""
        while self._running:
            try:
                await self.cleanup_expired_jobs(job_service)
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

            await asyncio.sleep(self.interval_seconds)

    async def start(self, job_service: AnalysisJobService):
        """
        Start the cleanup scheduler.

        Args:
            job_service: The job service to use for cleanup
        """
        if self._running:
            logger.warning("Cleanup scheduler already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop(job_service))
        logger.info(
            f"Started job cleanup scheduler "
            f"(interval={self.interval_seconds}s, max_age={self.max_age_hours}h)"
        )

    async def stop(self):
        """Stop the cleanup scheduler."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        logger.info("Stopped job cleanup scheduler")

    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running


# Global singleton instance
cleanup_scheduler = JobCleanupScheduler()
