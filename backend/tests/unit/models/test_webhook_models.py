"""
Unit tests for Webhook and Analysis Job Pydantic models.

Task: T-1.1.004
Requirement: TECH-001 - Nuevo MCP Server para Agent Orchestration en Python/FastAPI
Test IDs: Part of UT-001 to UT-011 infrastructure

Tests verify:
- WebhookConfig model validates correctly
- AnalysisJob model validates correctly
- JobStatus enum has all required states
- Model validation rejects invalid data
- Models serialize/deserialize correctly
"""

import pytest
from datetime import datetime, timedelta
from uuid import UUID
from pydantic import ValidationError


class TestWebhookConfigModel:
    """Tests for WebhookConfig Pydantic model."""

    def test_webhook_config_valid_creation(self):
        """Test creating a valid WebhookConfig."""
        from src.models.webhook import WebhookConfig

        config = WebhookConfig(
            name="Test Webhook",
            url="https://agent.example.com/webhook",
            events=["alert.created", "alert.critical"],
            enabled=True
        )

        assert config.name == "Test Webhook"
        assert str(config.url) == "https://agent.example.com/webhook"
        assert config.events == ["alert.created", "alert.critical"]
        assert config.enabled is True
        assert config.timeout_seconds == 30  # Default
        assert config.retry_count == 3  # Default

    def test_webhook_config_with_optional_fields(self):
        """Test WebhookConfig with all optional fields."""
        from src.models.webhook import WebhookConfig

        config = WebhookConfig(
            name="Full Webhook",
            url="https://agent.example.com/webhook",
            events=["alert.created"],
            secret="my-secret-key",
            timeout_seconds=60,
            retry_count=5,
            headers={"X-Custom-Header": "value"},
            enabled=False
        )

        assert config.secret == "my-secret-key"
        assert config.timeout_seconds == 60
        assert config.retry_count == 5
        assert config.headers == {"X-Custom-Header": "value"}
        assert config.enabled is False

    def test_webhook_config_invalid_url(self):
        """Test WebhookConfig rejects invalid URL."""
        from src.models.webhook import WebhookConfig

        with pytest.raises(ValidationError) as exc_info:
            WebhookConfig(
                name="Bad Webhook",
                url="not-a-valid-url",
                events=["alert.created"]
            )

        assert "url" in str(exc_info.value).lower()

    def test_webhook_config_empty_events(self):
        """Test WebhookConfig rejects empty events list."""
        from src.models.webhook import WebhookConfig

        with pytest.raises(ValidationError):
            WebhookConfig(
                name="Empty Events",
                url="https://agent.example.com/webhook",
                events=[]
            )

    def test_webhook_config_id_auto_generated(self):
        """Test WebhookConfig generates ID automatically."""
        from src.models.webhook import WebhookConfig

        config = WebhookConfig(
            name="Auto ID Webhook",
            url="https://agent.example.com/webhook",
            events=["alert.created"]
        )

        assert config.id is not None
        # Verify it follows the wh-{hex} format
        assert config.id.startswith("wh-")
        assert len(config.id) > 3  # More than just "wh-"

    def test_webhook_config_serialization(self):
        """Test WebhookConfig serializes to dict correctly."""
        from src.models.webhook import WebhookConfig

        config = WebhookConfig(
            id="wh-test-123",
            name="Serialization Test",
            url="https://agent.example.com/webhook",
            events=["alert.created", "alert.critical"],
            enabled=True
        )

        data = config.model_dump()

        assert data["id"] == "wh-test-123"
        assert data["name"] == "Serialization Test"
        assert data["url"] == "https://agent.example.com/webhook"
        assert data["events"] == ["alert.created", "alert.critical"]
        assert data["enabled"] is True

    def test_webhook_config_timeout_bounds(self):
        """Test WebhookConfig validates timeout bounds."""
        from src.models.webhook import WebhookConfig

        # Valid timeout
        config = WebhookConfig(
            name="Valid Timeout",
            url="https://agent.example.com/webhook",
            events=["alert.created"],
            timeout_seconds=30
        )
        assert config.timeout_seconds == 30

        # Too low timeout should raise
        with pytest.raises(ValidationError):
            WebhookConfig(
                name="Low Timeout",
                url="https://agent.example.com/webhook",
                events=["alert.created"],
                timeout_seconds=0
            )

        # Too high timeout should raise
        with pytest.raises(ValidationError):
            WebhookConfig(
                name="High Timeout",
                url="https://agent.example.com/webhook",
                events=["alert.created"],
                timeout_seconds=600
            )


class TestAnalysisJobModel:
    """Tests for AnalysisJob Pydantic model."""

    def test_analysis_job_status_enum(self):
        """Test JobStatus enum has all required states."""
        from src.models.analysis_job import JobStatus

        assert JobStatus.PENDING == "pending"
        assert JobStatus.PROCESSING == "processing"
        assert JobStatus.COMPLETED == "completed"
        assert JobStatus.FAILED == "failed"
        assert JobStatus.CANCELLED == "cancelled"

    def test_analysis_job_valid_creation(self):
        """Test creating a valid AnalysisJob."""
        from src.models.analysis_job import AnalysisJob, JobStatus

        job = AnalysisJob(
            job_type="alert_analysis",
            payload={"alert_id": "ALT-001"}
        )

        assert job.job_type == "alert_analysis"
        assert job.payload == {"alert_id": "ALT-001"}
        assert job.status == JobStatus.PENDING
        assert job.id is not None
        assert job.created_at is not None

    def test_analysis_job_with_all_fields(self):
        """Test AnalysisJob with all fields populated."""
        from src.models.analysis_job import AnalysisJob, JobStatus

        now = datetime.utcnow()

        job = AnalysisJob(
            id="job-test-123",
            job_type="ioc_investigation",
            payload={"ioc": "evil.com", "type": "domain"},
            status=JobStatus.COMPLETED,
            result={"verdict": "malicious", "confidence": 0.95},
            error=None,
            progress=100,
            created_at=now,
            started_at=now,
            completed_at=now + timedelta(seconds=5)
        )

        assert job.id == "job-test-123"
        assert job.status == JobStatus.COMPLETED
        assert job.result["verdict"] == "malicious"
        assert job.progress == 100
        assert job.completed_at is not None

    def test_analysis_job_id_auto_generated(self):
        """Test AnalysisJob generates ID automatically."""
        from src.models.analysis_job import AnalysisJob

        job = AnalysisJob(
            job_type="alert_analysis",
            payload={}
        )

        assert job.id is not None
        assert job.id.startswith("job-")

    def test_analysis_job_progress_bounds(self):
        """Test AnalysisJob validates progress bounds (0-100)."""
        from src.models.analysis_job import AnalysisJob

        # Valid progress
        job = AnalysisJob(
            job_type="alert_analysis",  # Use valid job type
            payload={},
            progress=50
        )
        assert job.progress == 50

        # Negative progress should raise
        with pytest.raises(ValidationError):
            AnalysisJob(
                job_type="alert_analysis",
                payload={},
                progress=-1
            )

        # Over 100 progress should raise
        with pytest.raises(ValidationError):
            AnalysisJob(
                job_type="alert_analysis",
                payload={},
                progress=101
            )

    def test_analysis_job_serialization(self):
        """Test AnalysisJob serializes correctly."""
        from src.models.analysis_job import AnalysisJob, JobStatus

        job = AnalysisJob(
            id="job-serial-001",
            job_type="alert_analysis",
            payload={"alert_id": "ALT-001"},
            status=JobStatus.PROCESSING,
            progress=50
        )

        data = job.model_dump()

        assert data["id"] == "job-serial-001"
        assert data["job_type"] == "alert_analysis"
        assert data["payload"] == {"alert_id": "ALT-001"}
        assert data["status"] == "processing"
        assert data["progress"] == 50

    def test_analysis_job_failed_with_error(self):
        """Test AnalysisJob can store error message when failed."""
        from src.models.analysis_job import AnalysisJob, JobStatus

        job = AnalysisJob(
            job_type="alert_analysis",
            payload={"alert_id": "ALT-001"},
            status=JobStatus.FAILED,
            error="Connection timeout to agent endpoint"
        )

        assert job.status == JobStatus.FAILED
        assert job.error == "Connection timeout to agent endpoint"
        assert job.result is None


class TestAnalysisJobCreateRequest:
    """Tests for AnalysisJobCreateRequest model (API input)."""

    def test_create_request_valid(self):
        """Test valid AnalysisJobCreateRequest."""
        from src.models.analysis_job import AnalysisJobCreateRequest

        request = AnalysisJobCreateRequest(
            job_type="alert_analysis",
            payload={"alert_id": "ALT-001"}
        )

        assert request.job_type == "alert_analysis"
        assert request.payload == {"alert_id": "ALT-001"}

    def test_create_request_valid_job_types(self):
        """Test AnalysisJobCreateRequest accepts valid job types."""
        from src.models.analysis_job import AnalysisJobCreateRequest

        valid_types = [
            "alert_analysis",
            "ioc_investigation",
            "event_correlation",
            "recommendation",
            "report_generation",
            "decision_explanation"
        ]

        for job_type in valid_types:
            request = AnalysisJobCreateRequest(
                job_type=job_type,
                payload={}
            )
            assert request.job_type == job_type

    def test_create_request_invalid_job_type(self):
        """Test AnalysisJobCreateRequest rejects invalid job type."""
        from src.models.analysis_job import AnalysisJobCreateRequest

        with pytest.raises(ValidationError):
            AnalysisJobCreateRequest(
                job_type="unknown_type",
                payload={}
            )


class TestAnalysisJobResponse:
    """Tests for AnalysisJobResponse model (API output)."""

    def test_response_from_job(self):
        """Test AnalysisJobResponse can be created from AnalysisJob."""
        from src.models.analysis_job import AnalysisJob, AnalysisJobResponse, JobStatus

        job = AnalysisJob(
            id="job-resp-001",
            job_type="alert_analysis",
            payload={"alert_id": "ALT-001"},
            status=JobStatus.COMPLETED,
            result={"verdict": "malicious"},
            progress=100
        )

        response = AnalysisJobResponse.model_validate(job.model_dump())

        assert response.id == "job-resp-001"
        assert response.status == "completed"
        assert response.result == {"verdict": "malicious"}

    def test_response_includes_timestamps(self):
        """Test AnalysisJobResponse includes timestamp fields."""
        from src.models.analysis_job import AnalysisJobResponse

        now = datetime.utcnow()
        response = AnalysisJobResponse(
            id="job-time-001",
            job_type="alert_analysis",
            status="completed",
            progress=100,
            created_at=now,
            started_at=now,
            completed_at=now
        )

        assert response.created_at == now
        assert response.started_at == now
        assert response.completed_at == now


class TestWebhookEventTypes:
    """Tests for valid webhook event types."""

    def test_valid_event_types(self):
        """Test WebhookConfig accepts valid event types."""
        from src.models.webhook import WebhookConfig, VALID_WEBHOOK_EVENTS

        # Verify some expected event types exist
        assert "alert.created" in VALID_WEBHOOK_EVENTS
        assert "alert.critical" in VALID_WEBHOOK_EVENTS
        assert "analysis.completed" in VALID_WEBHOOK_EVENTS

        config = WebhookConfig(
            name="Event Test",
            url="https://agent.example.com/webhook",
            events=["alert.created", "alert.critical"]
        )

        assert len(config.events) == 2
