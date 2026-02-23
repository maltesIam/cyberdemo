"""
Integration tests for Analysis Queue API.

Task: T-1.4.002
Requirements: REQ-001-002-001, REQ-001-002-002, REQ-001-002-003
Test ID: IT-002

Tests verify end-to-end flow:
- POST /api/v1/analysis/queue queues jobs correctly
- GET /api/v1/analysis/status/{job_id} returns correct status
- GET /api/v1/analysis/result/{job_id} returns correct result
- Full job lifecycle works (queue -> processing -> complete)
"""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock


# Helper to run async tests
def run_async(coro):
    """Helper to run async functions in tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestAnalysisQueueAPIIntegration:
    """Integration tests for analysis queue API endpoints."""

    @pytest.fixture
    def app(self):
        """Create FastAPI app instance."""
        from src.api.analysis import router
        from fastapi import FastAPI

        app = FastAPI()
        # Router already has prefix="/api/v1/analysis"
        app.include_router(router)
        return app

    @pytest.fixture
    def mock_job_service(self):
        """Mock job service for integration tests."""
        from datetime import datetime

        service = AsyncMock()
        # Default return for create_job
        service.create_job.return_value = {
            "id": "job-int-001",
            "job_type": "alert_analysis",
            "status": "pending",
            "progress": 0,
            "created_at": datetime.utcnow().isoformat()
        }
        return service

    def test_queue_analysis_endpoint_returns_job_id(self, app, mock_job_service):
        """Test POST /api/v1/analysis/queue returns job_id."""

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/analysis/queue",
                        json={
                            "job_type": "alert_analysis",
                            "payload": {"alert_id": "ALT-INT-001"}
                        }
                    )
                    return response

        response = run_async(_test())

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"

    def test_queue_analysis_with_all_job_types(self, app, mock_job_service):
        """Test queueing works for all valid job types."""
        job_types = [
            "alert_analysis",
            "ioc_investigation",
            "event_correlation",
            "recommendation",
            "report_generation",
        ]

        async def _test():
            results = []
            with patch("src.api.analysis.job_service", mock_job_service):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    for jt in job_types:
                        mock_job_service.create_job.return_value = {
                            "id": f"job-{jt[:4]}",
                            "job_type": jt,
                            "status": "pending",
                            "progress": 0
                        }
                        response = await client.post(
                            "/api/v1/analysis/queue",
                            json={"job_type": jt, "payload": {}}
                        )
                        results.append((jt, response.status_code))
            return results

        results = run_async(_test())

        for job_type, status_code in results:
            assert status_code == 200, f"Failed for job_type: {job_type}"

    def test_get_status_pending_job(self, app, mock_job_service):
        """Test GET /api/v1/analysis/status returns pending status."""
        mock_job_service.get_job.return_value = {
            "id": "job-int-001",
            "job_type": "alert_analysis",
            "status": "pending",
            "progress": 0
        }

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get("/api/v1/analysis/status/job-int-001")
                    return response

        response = run_async(_test())

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "job-int-001"
        assert data["status"] == "pending"
        assert data["progress"] == 0

    def test_get_status_processing_job(self, app, mock_job_service):
        """Test GET /api/v1/analysis/status returns processing status."""
        mock_job_service.get_job.return_value = {
            "id": "job-int-002",
            "job_type": "alert_analysis",
            "status": "processing",
            "progress": 50
        }

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get("/api/v1/analysis/status/job-int-002")
                    return response

        response = run_async(_test())

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
        assert data["progress"] == 50

    def test_get_status_not_found(self, app, mock_job_service):
        """Test GET /api/v1/analysis/status returns 404 for non-existent job."""
        mock_job_service.get_job.return_value = None

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get("/api/v1/analysis/status/job-nonexistent")
                    return response

        response = run_async(_test())

        assert response.status_code == 404

    def test_get_result_completed_job(self, app, mock_job_service):
        """Test GET /api/v1/analysis/result returns result for completed job."""
        mock_job_service.get_job.return_value = {
            "id": "job-int-003",
            "job_type": "alert_analysis",
            "status": "completed",
            "progress": 100,
            "result": {
                "verdict": "malicious",
                "confidence": 0.95,
                "recommendations": ["Isolate host", "Block hash"]
            }
        }

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get("/api/v1/analysis/result/job-int-003")
                    return response

        response = run_async(_test())

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["result"]["verdict"] == "malicious"
        assert data["result"]["confidence"] == 0.95

    def test_get_result_pending_job(self, app, mock_job_service):
        """Test GET /api/v1/analysis/result returns null result for pending job."""
        mock_job_service.get_job.return_value = {
            "id": "job-int-004",
            "job_type": "alert_analysis",
            "status": "pending",
            "progress": 0,
            "result": None
        }

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get("/api/v1/analysis/result/job-int-004")
                    return response

        response = run_async(_test())

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["result"] is None

    def test_get_result_failed_job(self, app, mock_job_service):
        """Test GET /api/v1/analysis/result returns error for failed job."""
        mock_job_service.get_job.return_value = {
            "id": "job-int-005",
            "job_type": "alert_analysis",
            "status": "failed",
            "progress": 25,
            "result": None,
            "error": "Agent timeout after 30 seconds"
        }

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get("/api/v1/analysis/result/job-int-005")
                    return response

        response = run_async(_test())

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["error"] == "Agent timeout after 30 seconds"

    def test_get_result_not_found(self, app, mock_job_service):
        """Test GET /api/v1/analysis/result returns 404 for non-existent job."""
        mock_job_service.get_job.return_value = None

        async def _test():
            with patch("src.api.analysis.job_service", mock_job_service):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get("/api/v1/analysis/result/job-nonexistent")
                    return response

        response = run_async(_test())

        assert response.status_code == 404


class TestAnalysisQueueJobLifecycle:
    """Integration tests for full job lifecycle."""

    @pytest.fixture
    def app(self):
        """Create FastAPI app instance."""
        from src.api.analysis import router
        from fastapi import FastAPI

        app = FastAPI()
        # Router already has prefix="/api/v1/analysis"
        app.include_router(router)
        return app

    def test_full_job_lifecycle(self, app):
        """Test complete job lifecycle: queue -> status check -> result."""
        from src.services.analysis_job_service import AnalysisJobService

        # Use real service (in-memory)
        service = AnalysisJobService()

        async def _test():
            with patch("src.api.analysis.job_service", service):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    # Step 1: Queue a job
                    queue_response = await client.post(
                        "/api/v1/analysis/queue",
                        json={
                            "job_type": "alert_analysis",
                            "payload": {"alert_id": "ALT-LIFECYCLE-001"}
                        }
                    )
                    assert queue_response.status_code == 200
                    job_id = queue_response.json()["job_id"]

                    # Step 2: Check status (should be pending)
                    status_response = await client.get(f"/api/v1/analysis/status/{job_id}")
                    assert status_response.status_code == 200
                    assert status_response.json()["status"] == "pending"

                    # Step 3: Simulate job completion
                    from src.models.analysis_job import JobStatus
                    await service.update_job_status(
                        job_id, JobStatus.COMPLETED,
                        result={"verdict": "benign", "confidence": 0.88}
                    )

                    # Step 4: Check result
                    result_response = await client.get(f"/api/v1/analysis/result/{job_id}")
                    assert result_response.status_code == 200
                    result_data = result_response.json()
                    assert result_data["status"] == "completed"
                    assert result_data["result"]["verdict"] == "benign"

                    return True

        result = run_async(_test())
        assert result is True

    def test_job_priority_handling(self, app):
        """Test that jobs are created with priority."""
        from src.services.analysis_job_service import AnalysisJobService

        service = AnalysisJobService()

        async def _test():
            with patch("src.api.analysis.job_service", service):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    # Create high priority job
                    response = await client.post(
                        "/api/v1/analysis/queue",
                        json={
                            "job_type": "alert_analysis",
                            "payload": {"alert_id": "ALT-PRIORITY-001"},
                            "priority": 1
                        }
                    )
                    assert response.status_code == 200
                    job_id = response.json()["job_id"]

                    # Verify job was created
                    status_response = await client.get(f"/api/v1/analysis/status/{job_id}")
                    assert status_response.status_code == 200

                    return True

        result = run_async(_test())
        assert result is True


class TestAnalysisQueueErrorHandling:
    """Integration tests for error handling."""

    @pytest.fixture
    def app(self):
        """Create FastAPI app instance."""
        from src.api.analysis import router
        from fastapi import FastAPI

        app = FastAPI()
        # Router already has prefix="/api/v1/analysis"
        app.include_router(router)
        return app

    def test_invalid_job_type_rejected(self, app):
        """Test that invalid job types are rejected."""
        from src.services.analysis_job_service import AnalysisJobService

        service = AnalysisJobService()

        async def _test():
            with patch("src.api.analysis.job_service", service):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/analysis/queue",
                        json={
                            "job_type": "invalid_type_xyz",
                            "payload": {}
                        }
                    )
                    return response

        response = run_async(_test())
        # Should fail validation (422) or be rejected (400)
        assert response.status_code in [400, 422]

    def test_missing_job_type_rejected(self, app):
        """Test that missing job_type is rejected."""

        async def _test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/analysis/queue",
                    json={"payload": {"test": "data"}}
                    # Missing job_type
                )
                return response

        response = run_async(_test())
        # Should fail validation - job_type is required
        assert response.status_code == 422
