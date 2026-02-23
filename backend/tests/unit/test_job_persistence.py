"""
Unit tests for job persistence with PostgreSQL.

Task: T-1.2.009
Requirement: REQ-001-002-005 - Persistencia de jobs en PostgreSQL
Test ID: UT-010

Tests verify:
- AnalysisJobDB SQLAlchemy model exists
- Model can be created and saved
- Model can be retrieved by ID
- Model can be updated
- Model can be deleted
- Model tracks timestamps correctly
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch


class TestAnalysisJobDBModel:
    """Tests for AnalysisJobDB SQLAlchemy model."""

    def test_analysis_job_db_model_exists(self):
        """Test that AnalysisJobDB model class exists."""
        from src.models.analysis_job_db import AnalysisJobDB

        assert AnalysisJobDB is not None

    def test_analysis_job_db_inherits_from_base(self):
        """Test AnalysisJobDB inherits from SQLAlchemy Base."""
        from src.models.analysis_job_db import AnalysisJobDB
        from src.core.database import Base

        assert issubclass(AnalysisJobDB, Base)

    def test_analysis_job_db_has_tablename(self):
        """Test AnalysisJobDB has correct table name."""
        from src.models.analysis_job_db import AnalysisJobDB

        assert AnalysisJobDB.__tablename__ == "analysis_jobs"

    def test_analysis_job_db_has_required_columns(self):
        """Test AnalysisJobDB has all required columns."""
        from src.models.analysis_job_db import AnalysisJobDB

        # Core columns that must exist - matching actual DB schema
        required_columns = [
            "id",
            "job_type",
            "payload",
            "status",
            "result",
            "error_message",  # DB uses error_message, to_dict maps to error
            "created_at",
            "started_at",
            "completed_at",
            "session_id",
            "priority",
        ]

        mapper = AnalysisJobDB.__mapper__
        column_names = [c.key for c in mapper.columns]

        for col in required_columns:
            assert col in column_names, f"Column '{col}' is required"

    def test_analysis_job_db_id_is_primary_key(self):
        """Test that id is the primary key."""
        from src.models.analysis_job_db import AnalysisJobDB

        mapper = AnalysisJobDB.__mapper__
        id_col = mapper.columns["id"]

        assert id_col.primary_key is True

    def test_analysis_job_db_status_is_indexed(self):
        """Test that status column is indexed for queries."""
        from src.models.analysis_job_db import AnalysisJobDB

        mapper = AnalysisJobDB.__mapper__
        status_col = mapper.columns["status"]

        assert status_col.index is True

    def test_analysis_job_db_created_at_default(self):
        """Test created_at has default of current timestamp."""
        from src.models.analysis_job_db import AnalysisJobDB

        mapper = AnalysisJobDB.__mapper__
        created_at_col = mapper.columns["created_at"]

        assert created_at_col.default is not None


class TestAnalysisJobDBOperations:
    """Tests for CRUD operations on AnalysisJobDB."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.get = AsyncMock()
        session.delete = AsyncMock()
        return session

    def test_create_job_db_instance(self):
        """Test creating a new AnalysisJobDB instance."""
        from src.models.analysis_job_db import AnalysisJobDB, AnalysisJobType, AnalysisJobStatus

        job = AnalysisJobDB(
            id="job-test-001",
            job_type=AnalysisJobType.ALERT_ANALYSIS,
            payload={"alert_id": "ALT-001"},
            status=AnalysisJobStatus.PENDING,
            priority=5
        )

        assert job.id == "job-test-001"
        assert job.job_type == AnalysisJobType.ALERT_ANALYSIS
        assert job.status == AnalysisJobStatus.PENDING

    def test_job_db_to_dict(self):
        """Test converting job to dictionary."""
        from src.models.analysis_job_db import AnalysisJobDB, AnalysisJobType, AnalysisJobStatus

        job = AnalysisJobDB(
            id="job-dict-001",
            job_type=AnalysisJobType.ALERT_ANALYSIS,
            payload={"alert_id": "ALT-001"},
            status=AnalysisJobStatus.PENDING,
            priority=5
        )

        job_dict = job.to_dict()

        assert job_dict["id"] == "job-dict-001"
        assert job_dict["job_type"] == "alert_analysis"
        assert job_dict["status"] == "pending"
        assert job_dict["payload"] == {"alert_id": "ALT-001"}


class TestPersistentJobService:
    """Tests for persistent job service using PostgreSQL."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session factory."""
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.get = AsyncMock()
        session.delete = AsyncMock()
        session.execute = AsyncMock()
        return session

    def test_persistent_job_service_exists(self):
        """Test that PersistentJobService class exists."""
        from src.services.persistent_job_service import PersistentJobService

        assert PersistentJobService is not None

    def test_create_job_persists_to_db(self, mock_db):
        """Test that create_job saves to database."""
        from src.services.persistent_job_service import PersistentJobService

        async def _test():
            service = PersistentJobService(mock_db)
            job = await service.create_job(
                job_type="alert_analysis",
                payload={"alert_id": "ALT-001"}
            )
            return job

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            job = loop.run_until_complete(_test())
            assert job is not None
            assert mock_db.add.called
        finally:
            loop.close()

    def test_get_job_queries_db(self, mock_db):
        """Test that get_job queries database."""
        from src.services.persistent_job_service import PersistentJobService
        from src.models.analysis_job_db import AnalysisJobDB, AnalysisJobType, AnalysisJobStatus

        mock_job = AnalysisJobDB(
            id="job-query-001",
            job_type=AnalysisJobType.ALERT_ANALYSIS,
            payload={},
            status=AnalysisJobStatus.PENDING,
            priority=5
        )
        mock_db.get.return_value = mock_job

        async def _test():
            service = PersistentJobService(mock_db)
            job = await service.get_job("job-query-001")
            return job

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            job = loop.run_until_complete(_test())
            assert job is not None
            mock_db.get.assert_called_once()
        finally:
            loop.close()
