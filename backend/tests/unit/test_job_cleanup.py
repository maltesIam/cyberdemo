"""
Unit tests for job cleanup scheduler.

Task: T-1.2.010
Requirement: REQ-001-002-006 - Limpieza automatica de jobs > 24h
Test ID: UT-011

Tests verify:
- JobCleanupScheduler class exists
- Scheduler can clean up expired jobs
- Scheduler runs on configured interval
- Cleanup removes only jobs older than 24 hours
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock


class TestJobCleanupScheduler:
    """Tests for job cleanup scheduler."""

    def test_job_cleanup_scheduler_exists(self):
        """Test that JobCleanupScheduler class exists."""
        from src.services.job_cleanup_scheduler import JobCleanupScheduler

        assert JobCleanupScheduler is not None

    def test_cleanup_scheduler_has_interval_config(self):
        """Test scheduler has configurable interval."""
        from src.services.job_cleanup_scheduler import JobCleanupScheduler

        scheduler = JobCleanupScheduler(interval_seconds=3600)
        assert scheduler.interval_seconds == 3600

    def test_cleanup_scheduler_default_interval_1_hour(self):
        """Test scheduler defaults to 1 hour interval."""
        from src.services.job_cleanup_scheduler import JobCleanupScheduler

        scheduler = JobCleanupScheduler()
        assert scheduler.interval_seconds == 3600  # 1 hour

    def test_cleanup_scheduler_max_age_hours_config(self):
        """Test scheduler has configurable max age."""
        from src.services.job_cleanup_scheduler import JobCleanupScheduler

        scheduler = JobCleanupScheduler(max_age_hours=24)
        assert scheduler.max_age_hours == 24


class TestJobCleanupExecution:
    """Tests for cleanup execution."""

    @pytest.fixture
    def mock_job_service(self):
        """Mock job service for testing."""
        service = AsyncMock()
        service.cleanup_expired_jobs = AsyncMock(return_value=5)
        return service

    def test_cleanup_calls_job_service(self, mock_job_service):
        """Test cleanup calls job service cleanup method."""
        from src.services.job_cleanup_scheduler import JobCleanupScheduler

        async def _test():
            scheduler = JobCleanupScheduler()
            result = await scheduler.cleanup_expired_jobs(mock_job_service)
            return result

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(_test())
            mock_job_service.cleanup_expired_jobs.assert_called_once_with(24)
            assert result == 5
        finally:
            loop.close()

    def test_cleanup_uses_configured_max_age(self, mock_job_service):
        """Test cleanup uses configured max age."""
        from src.services.job_cleanup_scheduler import JobCleanupScheduler

        async def _test():
            scheduler = JobCleanupScheduler(max_age_hours=48)
            await scheduler.cleanup_expired_jobs(mock_job_service)

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_test())
            mock_job_service.cleanup_expired_jobs.assert_called_once_with(48)
        finally:
            loop.close()


class TestCleanupFunctionInMemoryService:
    """Tests for cleanup in the in-memory job service."""

    def test_in_memory_service_has_cleanup_method(self):
        """Test in-memory service has cleanup_expired_jobs method."""
        from src.services.analysis_job_service import AnalysisJobService

        service = AnalysisJobService()
        assert hasattr(service, "cleanup_expired_jobs")

    def test_cleanup_removes_expired_jobs(self):
        """Test cleanup removes jobs older than max age."""
        from src.services.analysis_job_service import AnalysisJobService
        from datetime import datetime, timedelta

        service = AnalysisJobService()

        async def _test():
            # Create an old job
            old_job = await service.create_job("alert_analysis", {})

            # Manually set expires_at to the past
            old_id = old_job["id"]
            service._jobs[old_id]["expires_at"] = (
                datetime.utcnow() - timedelta(hours=1)
            ).isoformat()

            # Create a new job
            new_job = await service.create_job("alert_analysis", {})
            new_id = new_job["id"]

            # Run cleanup
            removed = await service.cleanup_expired_jobs()

            # Old job should be removed, new job should remain
            assert removed == 1
            assert await service.get_job(old_id) is None
            assert await service.get_job(new_id) is not None

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_test())
        finally:
            loop.close()

    def test_cleanup_returns_count_of_removed_jobs(self):
        """Test cleanup returns count of removed jobs."""
        from src.services.analysis_job_service import AnalysisJobService
        from datetime import datetime, timedelta

        service = AnalysisJobService()

        async def _test():
            # Create 3 old jobs
            for _ in range(3):
                job = await service.create_job("alert_analysis", {})
                job_id = job["id"]
                service._jobs[job_id]["expires_at"] = (
                    datetime.utcnow() - timedelta(hours=1)
                ).isoformat()

            # Run cleanup
            removed = await service.cleanup_expired_jobs()
            return removed

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(_test())
            assert result == 3
        finally:
            loop.close()

    def test_cleanup_does_not_remove_valid_jobs(self):
        """Test cleanup keeps non-expired jobs."""
        from src.services.analysis_job_service import AnalysisJobService

        service = AnalysisJobService()

        async def _test():
            # Create a valid (non-expired) job
            job = await service.create_job("alert_analysis", {})
            job_id = job["id"]

            # Run cleanup
            removed = await service.cleanup_expired_jobs()

            # Job should still exist
            assert removed == 0
            assert await service.get_job(job_id) is not None

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_test())
        finally:
            loop.close()
