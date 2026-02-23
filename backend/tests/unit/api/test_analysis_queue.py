"""
Unit tests for Analysis Queue models and manager.
Test ID: UT-009 (REQ-001-002-004)

These tests verify the Pydantic models and in-memory queue manager
WITHOUT any infrastructure dependencies (no FastAPI app, no DB, no network).

For API endpoint tests, see: tests/integration/test_analysis_queue_api.py
"""

import pytest
import asyncio
from datetime import datetime

from src.api.analysis_queue import AnalysisQueueManager, AnalysisJob, JobStatus


class TestAnalysisJob:
    """Test AnalysisJob model - pure unit tests without infrastructure."""

    def test_create_analysis_job_with_defaults(self):
        """Test creating an analysis job with default values."""
        job = AnalysisJob(
            alert_id="ALERT-001",
            analysis_type="full"
        )

        assert job.job_id is not None
        assert job.alert_id == "ALERT-001"
        assert job.analysis_type == "full"
        assert job.status == JobStatus.PENDING
        assert job.created_at is not None
        assert job.result is None
        assert job.error is None

    def test_create_analysis_job_with_custom_id(self):
        """Test creating an analysis job with custom job_id."""
        job = AnalysisJob(
            job_id="JOB-CUSTOM-001",
            alert_id="ALERT-002",
            analysis_type="quick"
        )

        assert job.job_id == "JOB-CUSTOM-001"
        assert job.alert_id == "ALERT-002"
        assert job.analysis_type == "quick"

    def test_analysis_job_status_transitions(self):
        """Test job status can be changed."""
        job = AnalysisJob(
            alert_id="ALERT-003",
            analysis_type="full"
        )

        assert job.status == JobStatus.PENDING

        job.status = JobStatus.PROCESSING
        assert job.status == JobStatus.PROCESSING

        job.status = JobStatus.COMPLETED
        assert job.status == JobStatus.COMPLETED

    def test_analysis_job_serialization(self):
        """Test job can be serialized to dict."""
        job = AnalysisJob(
            job_id="JOB-001",
            alert_id="ALERT-001",
            analysis_type="full"
        )

        job_dict = job.model_dump()

        assert job_dict["job_id"] == "JOB-001"
        assert job_dict["alert_id"] == "ALERT-001"
        assert job_dict["analysis_type"] == "full"
        assert job_dict["status"] == "pending"


class TestAnalysisQueueManager:
    """Test AnalysisQueueManager singleton - pure async tests without infrastructure."""

    def test_queue_manager_singleton(self):
        """Test that AnalysisQueueManager is a singleton."""
        manager1 = AnalysisQueueManager()
        manager2 = AnalysisQueueManager()

        assert manager1 is manager2

    @pytest.mark.asyncio
    async def test_subscribe_creates_queue(self):
        """Test subscribing creates a queue for the client."""
        manager = AnalysisQueueManager()

        queue = await manager.subscribe()

        assert isinstance(queue, asyncio.Queue)

        # Cleanup
        await manager.unsubscribe(queue)

    @pytest.mark.asyncio
    async def test_unsubscribe_removes_queue(self):
        """Test unsubscribing removes the queue."""
        manager = AnalysisQueueManager()

        queue = await manager.subscribe()
        initial_count = len(manager._subscribers)

        await manager.unsubscribe(queue)

        assert len(manager._subscribers) == initial_count - 1

    @pytest.mark.asyncio
    async def test_notify_job_update_sends_to_all_subscribers(self):
        """Test notification is sent to all subscribers."""
        manager = AnalysisQueueManager()

        queue1 = await manager.subscribe()
        queue2 = await manager.subscribe()

        job = AnalysisJob(
            job_id="JOB-001",
            alert_id="ALERT-001",
            analysis_type="full"
        )

        await manager.notify_job_update(job)

        # Both queues should have the update
        event1 = await asyncio.wait_for(queue1.get(), timeout=1.0)
        event2 = await asyncio.wait_for(queue2.get(), timeout=1.0)

        assert event1["type"] == "job_update"
        assert event1["job"]["job_id"] == "JOB-001"
        assert event2["type"] == "job_update"
        assert event2["job"]["job_id"] == "JOB-001"

        # Cleanup
        await manager.unsubscribe(queue1)
        await manager.unsubscribe(queue2)

    @pytest.mark.asyncio
    async def test_notify_job_completed(self):
        """Test notification for job completion."""
        manager = AnalysisQueueManager()

        queue = await manager.subscribe()

        job = AnalysisJob(
            job_id="JOB-002",
            alert_id="ALERT-002",
            analysis_type="full",
            status=JobStatus.COMPLETED,
            result={"findings": ["malware_detected"]}
        )

        await manager.notify_job_update(job)

        event = await asyncio.wait_for(queue.get(), timeout=1.0)

        assert event["type"] == "job_update"
        assert event["job"]["status"] == "completed"
        assert event["job"]["result"]["findings"] == ["malware_detected"]

        # Cleanup
        await manager.unsubscribe(queue)

    @pytest.mark.asyncio
    async def test_notify_job_failed(self):
        """Test notification for job failure."""
        manager = AnalysisQueueManager()

        queue = await manager.subscribe()

        job = AnalysisJob(
            job_id="JOB-003",
            alert_id="ALERT-003",
            analysis_type="full",
            status=JobStatus.FAILED,
            error="Analysis timeout"
        )

        await manager.notify_job_update(job)

        event = await asyncio.wait_for(queue.get(), timeout=1.0)

        assert event["type"] == "job_update"
        assert event["job"]["status"] == "failed"
        assert event["job"]["error"] == "Analysis timeout"

        # Cleanup
        await manager.unsubscribe(queue)


# NOTE: API endpoint tests (TestAnalysisQueueEndpoints, TestAnalysisWebSocket,
# TestJobPersistence, TestJobCleanup) have been moved to:
# tests/integration/test_analysis_queue_api.py
#
# Unit tests should NOT import from src.main or use TestClient(app) as this
# creates dependencies on infrastructure (PostgreSQL, OpenSearch, etc.)
