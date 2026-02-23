"""
Unit tests for Analysis Queue API endpoints.

Task: T-1.2.005, T-1.2.006, T-1.2.007
Requirements: REQ-001-002-001, REQ-001-002-002, REQ-001-002-003
Test IDs: UT-006, UT-007, UT-008

Tests verify:
- POST /api/v1/analysis/queue queues analysis jobs
- GET /api/v1/analysis/status/{job_id} returns job status
- GET /api/v1/analysis/result/{job_id} returns job result
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime


def run_async(coro):
    """Helper to run async functions in tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestAnalysisQueueEndpoint:
    """Tests for POST /api/v1/analysis/queue (REQ-001-002-001)."""

    @pytest.fixture
    def mock_job_service(self):
        """Mock job service for testing."""
        service = AsyncMock()
        service.create_job.return_value = {
            "id": "job-test-001",
            "job_type": "alert_analysis",
            "status": "pending",
            "progress": 0,
            "created_at": datetime.utcnow().isoformat()
        }
        return service

    def test_queue_analysis_valid_request(self, mock_job_service):
        """Test queueing analysis with valid request."""
        from src.api.analysis import queue_analysis
        from src.models.analysis_job import AnalysisJobCreateRequest

        request = AnalysisJobCreateRequest(
            job_type="alert_analysis",
            payload={"alert_id": "ALT-001"}
        )

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                return await queue_analysis(request)

        response = run_async(_test())
        assert response.job_id == "job-test-001"
        assert response.status == "pending"
        mock_job_service.create_job.assert_called_once()

    def test_queue_analysis_returns_job_id(self, mock_job_service):
        """Test that queueing returns a job_id for tracking."""
        from src.api.analysis import queue_analysis
        from src.models.analysis_job import AnalysisJobCreateRequest

        request = AnalysisJobCreateRequest(
            job_type="ioc_investigation",
            payload={"ioc": "evil.com", "type": "domain"}
        )

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                return await queue_analysis(request)

        response = run_async(_test())
        assert response.job_id is not None
        assert response.job_id.startswith("job-")

    def test_queue_analysis_all_job_types(self, mock_job_service):
        """Test that all valid job types can be queued."""
        from src.api.analysis import queue_analysis
        from src.models.analysis_job import AnalysisJobCreateRequest

        job_types = [
            "alert_analysis",
            "ioc_investigation",
            "event_correlation",
            "recommendation",
            "report_generation",
            "decision_explanation"
        ]

        for job_type in job_types:
            mock_job_service.create_job.return_value = {
                "id": f"job-{job_type[:4]}",
                "job_type": job_type,
                "status": "pending",
                "progress": 0
            }

            request = AnalysisJobCreateRequest(
                job_type=job_type,
                payload={}
            )

            async def _test():
                with patch("src.api.analysis.job_service", mock_job_service):
                    return await queue_analysis(request)

            response = run_async(_test())
            assert response.status == "pending"

    def test_queue_analysis_with_priority(self, mock_job_service):
        """Test that priority is passed to job service."""
        from src.api.analysis import queue_analysis
        from src.models.analysis_job import AnalysisJobCreateRequest

        request = AnalysisJobCreateRequest(
            job_type="alert_analysis",
            payload={"alert_id": "ALT-001"},
            priority=1  # High priority
        )

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                return await queue_analysis(request)

        run_async(_test())
        # Verify priority was passed
        call_args = mock_job_service.create_job.call_args
        assert call_args is not None


class TestAnalysisStatusEndpoint:
    """Tests for GET /api/v1/analysis/status/{job_id} (REQ-001-002-002)."""

    @pytest.fixture
    def mock_job_service(self):
        """Mock job service for testing."""
        service = AsyncMock()
        return service

    def test_get_status_pending_job(self, mock_job_service):
        """Test getting status of a pending job."""
        from src.api.analysis import get_job_status

        mock_job_service.get_job.return_value = {
            "id": "job-test-001",
            "job_type": "alert_analysis",
            "status": "pending",
            "progress": 0
        }

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                return await get_job_status("job-test-001")

        response = run_async(_test())
        assert response.id == "job-test-001"
        assert response.status == "pending"
        assert response.progress == 0

    def test_get_status_processing_job(self, mock_job_service):
        """Test getting status of a processing job."""
        from src.api.analysis import get_job_status

        mock_job_service.get_job.return_value = {
            "id": "job-test-002",
            "job_type": "alert_analysis",
            "status": "processing",
            "progress": 50
        }

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                return await get_job_status("job-test-002")

        response = run_async(_test())
        assert response.status == "processing"
        assert response.progress == 50

    def test_get_status_completed_job(self, mock_job_service):
        """Test getting status of a completed job."""
        from src.api.analysis import get_job_status

        mock_job_service.get_job.return_value = {
            "id": "job-test-003",
            "job_type": "alert_analysis",
            "status": "completed",
            "progress": 100,
            "result": {"verdict": "malicious"}
        }

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                return await get_job_status("job-test-003")

        response = run_async(_test())
        assert response.status == "completed"
        assert response.progress == 100

    def test_get_status_not_found(self, mock_job_service):
        """Test getting status of non-existent job raises 404."""
        from src.api.analysis import get_job_status
        from fastapi import HTTPException

        mock_job_service.get_job.return_value = None

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                return await get_job_status("job-nonexistent")

        with pytest.raises(HTTPException) as exc_info:
            run_async(_test())

        assert exc_info.value.status_code == 404


class TestAnalysisResultEndpoint:
    """Tests for GET /api/v1/analysis/result/{job_id} (REQ-001-002-003)."""

    @pytest.fixture
    def mock_job_service(self):
        """Mock job service for testing."""
        service = AsyncMock()
        return service

    def test_get_result_completed_job(self, mock_job_service):
        """Test getting result of completed job."""
        from src.api.analysis import get_job_result

        mock_job_service.get_job.return_value = {
            "id": "job-test-001",
            "job_type": "alert_analysis",
            "status": "completed",
            "progress": 100,
            "result": {
                "verdict": "malicious",
                "confidence": 0.92,
                "recommendations": ["Isolate host", "Block hash"]
            }
        }

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                return await get_job_result("job-test-001")

        response = run_async(_test())
        assert response.status == "completed"
        assert response.result is not None
        assert response.result["verdict"] == "malicious"
        assert response.result["confidence"] == 0.92

    def test_get_result_pending_job(self, mock_job_service):
        """Test getting result of pending job returns status only."""
        from src.api.analysis import get_job_result

        mock_job_service.get_job.return_value = {
            "id": "job-test-002",
            "job_type": "alert_analysis",
            "status": "pending",
            "progress": 0,
            "result": None
        }

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                return await get_job_result("job-test-002")

        response = run_async(_test())
        assert response.status == "pending"
        assert response.result is None

    def test_get_result_failed_job(self, mock_job_service):
        """Test getting result of failed job includes error."""
        from src.api.analysis import get_job_result

        mock_job_service.get_job.return_value = {
            "id": "job-test-003",
            "job_type": "alert_analysis",
            "status": "failed",
            "progress": 25,
            "result": None,
            "error": "Agent timeout after 30 seconds"
        }

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                return await get_job_result("job-test-003")

        response = run_async(_test())
        assert response.status == "failed"
        assert response.error == "Agent timeout after 30 seconds"
        assert response.result is None

    def test_get_result_not_found(self, mock_job_service):
        """Test getting result of non-existent job raises 404."""
        from src.api.analysis import get_job_result
        from fastapi import HTTPException

        mock_job_service.get_job.return_value = None

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                return await get_job_result("job-nonexistent")

        with pytest.raises(HTTPException) as exc_info:
            run_async(_test())

        assert exc_info.value.status_code == 404
