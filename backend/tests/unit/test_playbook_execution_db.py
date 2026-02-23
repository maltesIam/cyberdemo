"""
Unit tests for PlaybookExecutionDB SQLAlchemy model (TECH-006).

Tests for the database schema for playbook_executions table as specified
in the functional spec REQ-005-001-006.

Task: T-2.3.001
Agent: build-3
TDD Phase: Tests written before implementation.
"""
import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlalchemy import inspect


# Test that model exists and can be imported
class TestPlaybookExecutionDBModelExists:
    """Tests to verify PlaybookExecutionDB model exists with correct structure."""

    def test_playbook_execution_db_model_can_be_imported(self):
        """Test that PlaybookExecutionDB model can be imported from models."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        assert PlaybookExecutionDB is not None

    def test_playbook_execution_status_enum_can_be_imported(self):
        """Test that PlaybookExecutionStatus enum can be imported."""
        from src.models.playbook_execution_db import PlaybookExecutionStatus
        assert PlaybookExecutionStatus is not None


class TestPlaybookExecutionStatusEnum:
    """Tests for PlaybookExecutionStatus enum values."""

    def test_status_enum_has_pending_value(self):
        """Test that status enum has PENDING value."""
        from src.models.playbook_execution_db import PlaybookExecutionStatus
        assert PlaybookExecutionStatus.PENDING == "pending"

    def test_status_enum_has_running_value(self):
        """Test that status enum has RUNNING value."""
        from src.models.playbook_execution_db import PlaybookExecutionStatus
        assert PlaybookExecutionStatus.RUNNING == "running"

    def test_status_enum_has_paused_value(self):
        """Test that status enum has PAUSED value for REQ-005-001-002."""
        from src.models.playbook_execution_db import PlaybookExecutionStatus
        assert PlaybookExecutionStatus.PAUSED == "paused"

    def test_status_enum_has_completed_value(self):
        """Test that status enum has COMPLETED value."""
        from src.models.playbook_execution_db import PlaybookExecutionStatus
        assert PlaybookExecutionStatus.COMPLETED == "completed"

    def test_status_enum_has_failed_value(self):
        """Test that status enum has FAILED value."""
        from src.models.playbook_execution_db import PlaybookExecutionStatus
        assert PlaybookExecutionStatus.FAILED == "failed"

    def test_status_enum_has_rolled_back_value(self):
        """Test that status enum has ROLLED_BACK value for REQ-005-001-004."""
        from src.models.playbook_execution_db import PlaybookExecutionStatus
        assert PlaybookExecutionStatus.ROLLED_BACK == "rolled_back"

    def test_status_enum_has_cancelled_value(self):
        """Test that status enum has CANCELLED value."""
        from src.models.playbook_execution_db import PlaybookExecutionStatus
        assert PlaybookExecutionStatus.CANCELLED == "cancelled"


class TestPlaybookExecutionDBTableSchema:
    """Tests for PlaybookExecutionDB table schema."""

    def test_playbook_execution_db_has_correct_tablename(self):
        """Test that PlaybookExecutionDB has correct tablename."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        assert PlaybookExecutionDB.__tablename__ == "playbook_executions"

    def test_playbook_execution_db_has_id_column(self):
        """Test that PlaybookExecutionDB has id column as primary key."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        assert "id" in mapper.columns
        assert mapper.columns["id"].primary_key

    def test_playbook_execution_db_has_playbook_id_column(self):
        """Test that PlaybookExecutionDB has playbook_id column."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        assert "playbook_id" in mapper.columns

    def test_playbook_execution_db_has_playbook_name_column(self):
        """Test that PlaybookExecutionDB has playbook_name column."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        assert "playbook_name" in mapper.columns

    def test_playbook_execution_db_has_status_column(self):
        """Test that PlaybookExecutionDB has status column."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        assert "status" in mapper.columns

    def test_playbook_execution_db_has_current_step_column(self):
        """Test that PlaybookExecutionDB has current_step column for pause/resume."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        assert "current_step" in mapper.columns

    def test_playbook_execution_db_has_total_steps_column(self):
        """Test that PlaybookExecutionDB has total_steps column."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        assert "total_steps" in mapper.columns

    def test_playbook_execution_db_has_context_column(self):
        """Test that PlaybookExecutionDB has context column (JSON)."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        assert "context" in mapper.columns

    def test_playbook_execution_db_has_step_results_column(self):
        """Test that PlaybookExecutionDB has step_results column (JSON)."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        assert "step_results" in mapper.columns

    def test_playbook_execution_db_has_rollback_data_column(self):
        """Test that PlaybookExecutionDB has rollback_data column for REQ-005-001-004."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        assert "rollback_data" in mapper.columns

    def test_playbook_execution_db_has_error_message_column(self):
        """Test that PlaybookExecutionDB has error_message column."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        assert "error_message" in mapper.columns

    def test_playbook_execution_db_has_triggered_by_column(self):
        """Test that PlaybookExecutionDB has triggered_by column."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        assert "triggered_by" in mapper.columns

    def test_playbook_execution_db_has_session_id_column(self):
        """Test that PlaybookExecutionDB has session_id column."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        assert "session_id" in mapper.columns

    def test_playbook_execution_db_has_created_at_column(self):
        """Test that PlaybookExecutionDB has created_at column."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        assert "created_at" in mapper.columns

    def test_playbook_execution_db_has_updated_at_column(self):
        """Test that PlaybookExecutionDB has updated_at column."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        assert "updated_at" in mapper.columns

    def test_playbook_execution_db_has_started_at_column(self):
        """Test that PlaybookExecutionDB has started_at column."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        assert "started_at" in mapper.columns

    def test_playbook_execution_db_has_paused_at_column(self):
        """Test that PlaybookExecutionDB has paused_at column for REQ-005-001-002."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        assert "paused_at" in mapper.columns

    def test_playbook_execution_db_has_completed_at_column(self):
        """Test that PlaybookExecutionDB has completed_at column."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        assert "completed_at" in mapper.columns


class TestPlaybookExecutionDBDefaults:
    """Tests for PlaybookExecutionDB default values."""

    def test_default_status_is_pending(self):
        """Test that status column has PENDING as default."""
        from src.models.playbook_execution_db import PlaybookExecutionDB, PlaybookExecutionStatus
        mapper = inspect(PlaybookExecutionDB)
        status_col = mapper.columns["status"]
        assert status_col.default is not None
        assert status_col.default.arg == PlaybookExecutionStatus.PENDING

    def test_default_current_step_is_0(self):
        """Test that current_step column has 0 as default."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        current_step_col = mapper.columns["current_step"]
        assert current_step_col.default is not None
        assert current_step_col.default.arg == 0


class TestPlaybookExecutionDBIndexes:
    """Tests for PlaybookExecutionDB table indexes."""

    def test_playbook_id_column_is_indexed(self):
        """Test that playbook_id column is indexed for quick lookups."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        playbook_id_col = mapper.columns["playbook_id"]
        assert playbook_id_col.index is True

    def test_status_column_is_indexed(self):
        """Test that status column is indexed for filtering."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        status_col = mapper.columns["status"]
        assert status_col.index is True

    def test_session_id_column_is_indexed(self):
        """Test that session_id column is indexed for quick lookups."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        mapper = inspect(PlaybookExecutionDB)
        session_id_col = mapper.columns["session_id"]
        assert session_id_col.index is True


class TestPlaybookExecutionDBCreation:
    """Tests for PlaybookExecutionDB instance creation."""

    def test_create_playbook_execution_db_with_required_fields(self):
        """Test creating PlaybookExecutionDB with minimum required fields."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        execution = PlaybookExecutionDB(
            playbook_id="pb-ransomware-001",
            playbook_name="Ransomware Response",
            context={"incident_id": "INC-001"},
            total_steps=5
        )
        assert execution.playbook_id == "pb-ransomware-001"
        assert execution.playbook_name == "Ransomware Response"
        assert execution.context == {"incident_id": "INC-001"}
        assert execution.total_steps == 5

    def test_create_playbook_execution_db_with_explicit_values(self):
        """Test creating PlaybookExecutionDB with explicitly set values."""
        from src.models.playbook_execution_db import PlaybookExecutionDB, PlaybookExecutionStatus
        execution = PlaybookExecutionDB(
            playbook_id="pb-phishing-002",
            playbook_name="Phishing Investigation",
            context={"email_id": "EMAIL-123"},
            total_steps=7,
            session_id="session-456"
        )
        execution.status = PlaybookExecutionStatus.RUNNING
        execution.current_step = 3

        assert execution.playbook_id == "pb-phishing-002"
        assert execution.status == PlaybookExecutionStatus.RUNNING
        assert execution.current_step == 3
        assert execution.session_id == "session-456"


class TestPlaybookExecutionDBMethods:
    """Tests for PlaybookExecutionDB methods."""

    def test_can_pause_when_running(self):
        """Test can_pause returns True when status is RUNNING."""
        from src.models.playbook_execution_db import PlaybookExecutionDB, PlaybookExecutionStatus
        execution = PlaybookExecutionDB(
            playbook_id="pb-test",
            playbook_name="Test",
            context={},
            total_steps=5
        )
        execution.status = PlaybookExecutionStatus.RUNNING
        assert execution.can_pause() is True

    def test_cannot_pause_when_paused(self):
        """Test can_pause returns False when status is PAUSED."""
        from src.models.playbook_execution_db import PlaybookExecutionDB, PlaybookExecutionStatus
        execution = PlaybookExecutionDB(
            playbook_id="pb-test",
            playbook_name="Test",
            context={},
            total_steps=5
        )
        execution.status = PlaybookExecutionStatus.PAUSED
        assert execution.can_pause() is False

    def test_cannot_pause_when_completed(self):
        """Test can_pause returns False when status is COMPLETED."""
        from src.models.playbook_execution_db import PlaybookExecutionDB, PlaybookExecutionStatus
        execution = PlaybookExecutionDB(
            playbook_id="pb-test",
            playbook_name="Test",
            context={},
            total_steps=5
        )
        execution.status = PlaybookExecutionStatus.COMPLETED
        assert execution.can_pause() is False

    def test_can_resume_when_paused(self):
        """Test can_resume returns True when status is PAUSED."""
        from src.models.playbook_execution_db import PlaybookExecutionDB, PlaybookExecutionStatus
        execution = PlaybookExecutionDB(
            playbook_id="pb-test",
            playbook_name="Test",
            context={},
            total_steps=5
        )
        execution.status = PlaybookExecutionStatus.PAUSED
        assert execution.can_resume() is True

    def test_cannot_resume_when_running(self):
        """Test can_resume returns False when status is RUNNING."""
        from src.models.playbook_execution_db import PlaybookExecutionDB, PlaybookExecutionStatus
        execution = PlaybookExecutionDB(
            playbook_id="pb-test",
            playbook_name="Test",
            context={},
            total_steps=5
        )
        execution.status = PlaybookExecutionStatus.RUNNING
        assert execution.can_resume() is False

    def test_can_rollback_when_completed(self):
        """Test can_rollback returns True when status is COMPLETED and has rollback data."""
        from src.models.playbook_execution_db import PlaybookExecutionDB, PlaybookExecutionStatus
        execution = PlaybookExecutionDB(
            playbook_id="pb-test",
            playbook_name="Test",
            context={},
            total_steps=5
        )
        execution.status = PlaybookExecutionStatus.COMPLETED
        execution.rollback_data = [{"action": "contain_host", "undo": "release_host"}]
        assert execution.can_rollback() is True

    def test_cannot_rollback_when_no_rollback_data(self):
        """Test can_rollback returns False when no rollback_data exists."""
        from src.models.playbook_execution_db import PlaybookExecutionDB, PlaybookExecutionStatus
        execution = PlaybookExecutionDB(
            playbook_id="pb-test",
            playbook_name="Test",
            context={},
            total_steps=5
        )
        execution.status = PlaybookExecutionStatus.COMPLETED
        execution.rollback_data = None
        assert execution.can_rollback() is False

    def test_cannot_rollback_when_already_rolled_back(self):
        """Test can_rollback returns False when already rolled back."""
        from src.models.playbook_execution_db import PlaybookExecutionDB, PlaybookExecutionStatus
        execution = PlaybookExecutionDB(
            playbook_id="pb-test",
            playbook_name="Test",
            context={},
            total_steps=5
        )
        execution.status = PlaybookExecutionStatus.ROLLED_BACK
        execution.rollback_data = [{"action": "contain_host", "undo": "release_host"}]
        assert execution.can_rollback() is False

    def test_progress_percentage_calculation(self):
        """Test progress percentage calculation."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        execution = PlaybookExecutionDB(
            playbook_id="pb-test",
            playbook_name="Test",
            context={},
            total_steps=10
        )
        execution.current_step = 3
        assert execution.get_progress_percentage() == 30

    def test_progress_percentage_zero_when_not_started(self):
        """Test progress percentage is 0 when not started."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        execution = PlaybookExecutionDB(
            playbook_id="pb-test",
            playbook_name="Test",
            context={},
            total_steps=10
        )
        execution.current_step = 0
        assert execution.get_progress_percentage() == 0

    def test_progress_percentage_handles_zero_total_steps(self):
        """Test progress percentage handles zero total steps gracefully."""
        from src.models.playbook_execution_db import PlaybookExecutionDB
        execution = PlaybookExecutionDB(
            playbook_id="pb-test",
            playbook_name="Test",
            context={},
            total_steps=0
        )
        execution.current_step = 0
        assert execution.get_progress_percentage() == 0

    def test_to_dict_method(self):
        """Test to_dict returns correct dictionary representation."""
        from src.models.playbook_execution_db import PlaybookExecutionDB, PlaybookExecutionStatus
        from datetime import timezone
        execution = PlaybookExecutionDB(
            playbook_id="pb-test",
            playbook_name="Test Playbook",
            context={"key": "value"},
            total_steps=5
        )
        execution.status = PlaybookExecutionStatus.RUNNING
        execution.current_step = 2
        execution.created_at = datetime(2026, 2, 23, 12, 0, 0)

        result = execution.to_dict()

        assert result["playbook_id"] == "pb-test"
        assert result["playbook_name"] == "Test Playbook"
        assert result["status"] == "running"
        assert result["current_step"] == 2
        assert result["total_steps"] == 5
        assert result["context"] == {"key": "value"}
        assert result["progress"] == 40
