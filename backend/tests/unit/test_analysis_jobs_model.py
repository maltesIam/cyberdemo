"""
Unit tests for AnalysisJobDB SQLAlchemy model (TECH-004).

Tests for the database schema for analysis_jobs table as specified in
the functional spec REQ-001-002-005.

Task: T-1.1.001
Agent: build-1
TDD Phase: Tests written before implementation.
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from sqlalchemy import inspect
from unittest.mock import MagicMock, patch


# Test that model exists and can be imported
class TestAnalysisJobDBModelExists:
    """Tests to verify AnalysisJobDB model exists with correct structure."""

    def test_analysis_job_db_model_can_be_imported(self):
        """Test that AnalysisJobDB model can be imported from models."""
        from src.models.analysis_job_db import AnalysisJobDB
        assert AnalysisJobDB is not None

    def test_analysis_job_status_enum_can_be_imported(self):
        """Test that AnalysisJobStatus enum can be imported."""
        from src.models.analysis_job_db import AnalysisJobStatus
        assert AnalysisJobStatus is not None

    def test_analysis_job_type_enum_can_be_imported(self):
        """Test that AnalysisJobType enum can be imported."""
        from src.models.analysis_job_db import AnalysisJobType
        assert AnalysisJobType is not None


class TestAnalysisJobStatusEnum:
    """Tests for AnalysisJobStatus enum values."""

    def test_status_enum_has_pending_value(self):
        """Test that status enum has PENDING value."""
        from src.models.analysis_job_db import AnalysisJobStatus
        assert AnalysisJobStatus.PENDING == "pending"

    def test_status_enum_has_processing_value(self):
        """Test that status enum has PROCESSING value."""
        from src.models.analysis_job_db import AnalysisJobStatus
        assert AnalysisJobStatus.PROCESSING == "processing"

    def test_status_enum_has_completed_value(self):
        """Test that status enum has COMPLETED value."""
        from src.models.analysis_job_db import AnalysisJobStatus
        assert AnalysisJobStatus.COMPLETED == "completed"

    def test_status_enum_has_failed_value(self):
        """Test that status enum has FAILED value."""
        from src.models.analysis_job_db import AnalysisJobStatus
        assert AnalysisJobStatus.FAILED == "failed"

    def test_status_enum_has_cancelled_value(self):
        """Test that status enum has CANCELLED value."""
        from src.models.analysis_job_db import AnalysisJobStatus
        assert AnalysisJobStatus.CANCELLED == "cancelled"


class TestAnalysisJobTypeEnum:
    """Tests for AnalysisJobType enum values."""

    def test_type_enum_has_alert_analysis_value(self):
        """Test that type enum has ALERT_ANALYSIS value."""
        from src.models.analysis_job_db import AnalysisJobType
        assert AnalysisJobType.ALERT_ANALYSIS == "alert_analysis"

    def test_type_enum_has_ioc_investigation_value(self):
        """Test that type enum has IOC_INVESTIGATION value."""
        from src.models.analysis_job_db import AnalysisJobType
        assert AnalysisJobType.IOC_INVESTIGATION == "ioc_investigation"

    def test_type_enum_has_event_correlation_value(self):
        """Test that type enum has EVENT_CORRELATION value."""
        from src.models.analysis_job_db import AnalysisJobType
        assert AnalysisJobType.EVENT_CORRELATION == "event_correlation"

    def test_type_enum_has_report_generation_value(self):
        """Test that type enum has REPORT_GENERATION value."""
        from src.models.analysis_job_db import AnalysisJobType
        assert AnalysisJobType.REPORT_GENERATION == "report_generation"

    def test_type_enum_has_action_recommendation_value(self):
        """Test that type enum has ACTION_RECOMMENDATION value."""
        from src.models.analysis_job_db import AnalysisJobType
        assert AnalysisJobType.ACTION_RECOMMENDATION == "action_recommendation"


class TestAnalysisJobDBTableSchema:
    """Tests for AnalysisJobDB table schema."""

    def test_analysis_job_db_has_correct_tablename(self):
        """Test that AnalysisJobDB has correct tablename."""
        from src.models.analysis_job_db import AnalysisJobDB
        assert AnalysisJobDB.__tablename__ == "analysis_jobs"

    def test_analysis_job_db_has_id_column(self):
        """Test that AnalysisJobDB has id column as primary key."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        assert "id" in mapper.columns
        assert mapper.columns["id"].primary_key

    def test_analysis_job_db_has_job_type_column(self):
        """Test that AnalysisJobDB has job_type column."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        assert "job_type" in mapper.columns

    def test_analysis_job_db_has_status_column(self):
        """Test that AnalysisJobDB has status column."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        assert "status" in mapper.columns

    def test_analysis_job_db_has_payload_column(self):
        """Test that AnalysisJobDB has payload column (JSON)."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        assert "payload" in mapper.columns

    def test_analysis_job_db_has_result_column(self):
        """Test that AnalysisJobDB has result column (JSON)."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        assert "result" in mapper.columns

    def test_analysis_job_db_has_error_message_column(self):
        """Test that AnalysisJobDB has error_message column."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        assert "error_message" in mapper.columns

    def test_analysis_job_db_has_priority_column(self):
        """Test that AnalysisJobDB has priority column."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        assert "priority" in mapper.columns

    def test_analysis_job_db_has_retry_count_column(self):
        """Test that AnalysisJobDB has retry_count column."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        assert "retry_count" in mapper.columns

    def test_analysis_job_db_has_max_retries_column(self):
        """Test that AnalysisJobDB has max_retries column."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        assert "max_retries" in mapper.columns

    def test_analysis_job_db_has_timeout_seconds_column(self):
        """Test that AnalysisJobDB has timeout_seconds column."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        assert "timeout_seconds" in mapper.columns

    def test_analysis_job_db_has_session_id_column(self):
        """Test that AnalysisJobDB has session_id column."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        assert "session_id" in mapper.columns

    def test_analysis_job_db_has_created_at_column(self):
        """Test that AnalysisJobDB has created_at column."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        assert "created_at" in mapper.columns

    def test_analysis_job_db_has_updated_at_column(self):
        """Test that AnalysisJobDB has updated_at column."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        assert "updated_at" in mapper.columns

    def test_analysis_job_db_has_started_at_column(self):
        """Test that AnalysisJobDB has started_at column."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        assert "started_at" in mapper.columns

    def test_analysis_job_db_has_completed_at_column(self):
        """Test that AnalysisJobDB has completed_at column."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        assert "completed_at" in mapper.columns


class TestAnalysisJobDBDefaults:
    """Tests for AnalysisJobDB default values.

    Note: SQLAlchemy 2.0 mapped_column defaults are applied at INSERT time,
    not at object instantiation. We verify defaults are configured in the
    column definitions.
    """

    def test_default_status_is_pending(self):
        """Test that status column has PENDING as default."""
        from src.models.analysis_job_db import AnalysisJobDB, AnalysisJobStatus
        mapper = inspect(AnalysisJobDB)
        status_col = mapper.columns["status"]
        # Verify the default is configured correctly
        assert status_col.default is not None
        assert status_col.default.arg == AnalysisJobStatus.PENDING

    def test_default_priority_is_5(self):
        """Test that priority column has 5 as default."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        priority_col = mapper.columns["priority"]
        assert priority_col.default is not None
        assert priority_col.default.arg == 5

    def test_default_retry_count_is_0(self):
        """Test that retry_count column has 0 as default."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        retry_count_col = mapper.columns["retry_count"]
        assert retry_count_col.default is not None
        assert retry_count_col.default.arg == 0

    def test_default_max_retries_is_3(self):
        """Test that max_retries column has 3 as default."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        max_retries_col = mapper.columns["max_retries"]
        assert max_retries_col.default is not None
        assert max_retries_col.default.arg == 3

    def test_default_timeout_seconds_is_30(self):
        """Test that timeout_seconds column has 30 as default (as per BR-002)."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        timeout_seconds_col = mapper.columns["timeout_seconds"]
        assert timeout_seconds_col.default is not None
        assert timeout_seconds_col.default.arg == 30


class TestAnalysisJobDBIndexes:
    """Tests for AnalysisJobDB table indexes."""

    def test_session_id_column_is_indexed(self):
        """Test that session_id column is indexed for quick lookups."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        session_id_col = mapper.columns["session_id"]
        assert session_id_col.index is True

    def test_status_column_is_indexed(self):
        """Test that status column is indexed for filtering."""
        from src.models.analysis_job_db import AnalysisJobDB
        mapper = inspect(AnalysisJobDB)
        status_col = mapper.columns["status"]
        # Status should be part of an index for filtering pending jobs
        assert status_col.index is True or any(
            "status" in str(idx.columns) for idx in AnalysisJobDB.__table__.indexes
        )


class TestAnalysisJobDBCreation:
    """Tests for AnalysisJobDB instance creation."""

    def test_create_analysis_job_db_with_required_fields(self):
        """Test creating AnalysisJobDB with minimum required fields."""
        from src.models.analysis_job_db import AnalysisJobDB, AnalysisJobType
        job = AnalysisJobDB(
            job_type=AnalysisJobType.ALERT_ANALYSIS,
            payload={"alert_id": "ALT-001"}
        )
        assert job.job_type == AnalysisJobType.ALERT_ANALYSIS
        assert job.payload == {"alert_id": "ALT-001"}

    def test_create_analysis_job_db_with_explicit_values(self):
        """Test creating AnalysisJobDB with explicitly set values."""
        from src.models.analysis_job_db import AnalysisJobDB, AnalysisJobType, AnalysisJobStatus
        job = AnalysisJobDB(
            job_type=AnalysisJobType.IOC_INVESTIGATION,
            payload={"ioc": "192.168.1.1", "type": "ip"},
            session_id="session-123"
        )
        # Set explicit values (as SQLAlchemy defaults are DB-level)
        job.status = AnalysisJobStatus.PROCESSING
        job.priority = 10
        job.timeout_seconds = 60

        assert job.job_type == AnalysisJobType.IOC_INVESTIGATION
        assert job.status == AnalysisJobStatus.PROCESSING
        assert job.priority == 10
        assert job.timeout_seconds == 60
        assert job.session_id == "session-123"


class TestAnalysisJobDBMethods:
    """Tests for AnalysisJobDB methods."""

    def test_analysis_job_db_can_retry_when_under_max(self):
        """Test can_retry returns True when retry_count < max_retries."""
        from src.models.analysis_job_db import AnalysisJobDB, AnalysisJobType
        job = AnalysisJobDB(
            job_type=AnalysisJobType.ALERT_ANALYSIS,
            payload={}
        )
        # Explicitly set values to test logic
        job.retry_count = 1
        job.max_retries = 3
        assert job.can_retry() is True

    def test_analysis_job_db_cannot_retry_when_at_max(self):
        """Test can_retry returns False when retry_count >= max_retries."""
        from src.models.analysis_job_db import AnalysisJobDB, AnalysisJobType
        job = AnalysisJobDB(
            job_type=AnalysisJobType.ALERT_ANALYSIS,
            payload={}
        )
        # Explicitly set values to test logic
        job.retry_count = 3
        job.max_retries = 3
        assert job.can_retry() is False

    def test_analysis_job_db_is_expired_when_old(self):
        """Test is_expired returns True for jobs older than 24 hours."""
        from src.models.analysis_job_db import AnalysisJobDB, AnalysisJobType
        from datetime import timezone
        job = AnalysisJobDB(
            job_type=AnalysisJobType.ALERT_ANALYSIS,
            payload={}
        )
        # Explicitly set created_at to be old
        job.created_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=25)
        assert job.is_expired() is True

    def test_analysis_job_db_is_not_expired_when_recent(self):
        """Test is_expired returns False for jobs less than 24 hours old."""
        from src.models.analysis_job_db import AnalysisJobDB, AnalysisJobType
        from datetime import timezone
        job = AnalysisJobDB(
            job_type=AnalysisJobType.ALERT_ANALYSIS,
            payload={}
        )
        # Explicitly set created_at to be recent
        job.created_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1)
        assert job.is_expired() is False
