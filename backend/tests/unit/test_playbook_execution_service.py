"""
Unit tests for PlaybookExecutionService (REQ-005-001-006).

Tests for playbook state persistence in PostgreSQL.

Task: T-2.3.007
Agent: build-3
TDD Phase: Tests written before implementation.
"""
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock


class TestPlaybookExecutionServiceExists:
    """Tests to verify PlaybookExecutionService exists with correct structure."""

    def test_playbook_execution_service_can_be_imported(self):
        """Test that PlaybookExecutionService can be imported."""
        from src.services.playbook_execution_service import PlaybookExecutionService
        assert PlaybookExecutionService is not None

    def test_playbook_execution_error_can_be_imported(self):
        """Test that PlaybookExecutionError can be imported."""
        from src.services.playbook_execution_service import PlaybookExecutionError
        assert PlaybookExecutionError is not None

    def test_playbook_execution_not_found_error_can_be_imported(self):
        """Test that PlaybookExecutionNotFoundError can be imported."""
        from src.services.playbook_execution_service import PlaybookExecutionNotFoundError
        assert PlaybookExecutionNotFoundError is not None

    def test_get_playbook_execution_service_can_be_imported(self):
        """Test that get_playbook_execution_service can be imported."""
        from src.services.playbook_execution_service import get_playbook_execution_service
        assert get_playbook_execution_service is not None


class TestPlaybookExecutionServiceMethods:
    """Tests for PlaybookExecutionService methods."""

    def test_service_has_execute_playbook_method(self):
        """Test that service has execute_playbook method."""
        from src.services.playbook_execution_service import PlaybookExecutionService
        mock_db_session = MagicMock()
        mock_playbook_service = MagicMock()
        service = PlaybookExecutionService(
            db_session=mock_db_session,
            playbook_service=mock_playbook_service
        )
        assert hasattr(service, 'execute_playbook')
        assert callable(service.execute_playbook)

    def test_service_has_pause_execution_method(self):
        """Test that service has pause_execution method."""
        from src.services.playbook_execution_service import PlaybookExecutionService
        mock_db_session = MagicMock()
        mock_playbook_service = MagicMock()
        service = PlaybookExecutionService(
            db_session=mock_db_session,
            playbook_service=mock_playbook_service
        )
        assert hasattr(service, 'pause_execution')
        assert callable(service.pause_execution)

    def test_service_has_resume_execution_method(self):
        """Test that service has resume_execution method."""
        from src.services.playbook_execution_service import PlaybookExecutionService
        mock_db_session = MagicMock()
        mock_playbook_service = MagicMock()
        service = PlaybookExecutionService(
            db_session=mock_db_session,
            playbook_service=mock_playbook_service
        )
        assert hasattr(service, 'resume_execution')
        assert callable(service.resume_execution)

    def test_service_has_rollback_execution_method(self):
        """Test that service has rollback_execution method."""
        from src.services.playbook_execution_service import PlaybookExecutionService
        mock_db_session = MagicMock()
        mock_playbook_service = MagicMock()
        service = PlaybookExecutionService(
            db_session=mock_db_session,
            playbook_service=mock_playbook_service
        )
        assert hasattr(service, 'rollback_execution')
        assert callable(service.rollback_execution)

    def test_service_has_get_execution_method(self):
        """Test that service has get_execution method."""
        from src.services.playbook_execution_service import PlaybookExecutionService
        mock_db_session = MagicMock()
        mock_playbook_service = MagicMock()
        service = PlaybookExecutionService(
            db_session=mock_db_session,
            playbook_service=mock_playbook_service
        )
        assert hasattr(service, 'get_execution')
        assert callable(service.get_execution)

    def test_service_has_list_executions_method(self):
        """Test that service has list_executions method."""
        from src.services.playbook_execution_service import PlaybookExecutionService
        mock_db_session = MagicMock()
        mock_playbook_service = MagicMock()
        service = PlaybookExecutionService(
            db_session=mock_db_session,
            playbook_service=mock_playbook_service
        )
        assert hasattr(service, 'list_executions')
        assert callable(service.list_executions)


class TestPlaybookExecutionServiceAsync:
    """Tests to verify service methods are async."""

    def test_execute_playbook_is_async(self):
        """Test that execute_playbook is an async method."""
        from src.services.playbook_execution_service import PlaybookExecutionService
        assert asyncio.iscoroutinefunction(PlaybookExecutionService.execute_playbook)

    def test_pause_execution_is_async(self):
        """Test that pause_execution is an async method."""
        from src.services.playbook_execution_service import PlaybookExecutionService
        assert asyncio.iscoroutinefunction(PlaybookExecutionService.pause_execution)

    def test_resume_execution_is_async(self):
        """Test that resume_execution is an async method."""
        from src.services.playbook_execution_service import PlaybookExecutionService
        assert asyncio.iscoroutinefunction(PlaybookExecutionService.resume_execution)

    def test_rollback_execution_is_async(self):
        """Test that rollback_execution is an async method."""
        from src.services.playbook_execution_service import PlaybookExecutionService
        assert asyncio.iscoroutinefunction(PlaybookExecutionService.rollback_execution)

    def test_get_execution_is_async(self):
        """Test that get_execution is an async method."""
        from src.services.playbook_execution_service import PlaybookExecutionService
        assert asyncio.iscoroutinefunction(PlaybookExecutionService.get_execution)

    def test_list_executions_is_async(self):
        """Test that list_executions is an async method."""
        from src.services.playbook_execution_service import PlaybookExecutionService
        assert asyncio.iscoroutinefunction(PlaybookExecutionService.list_executions)


class TestPlaybookExecutionExceptions:
    """Tests for playbook execution exceptions."""

    def test_playbook_execution_error_is_exception(self):
        """Test that PlaybookExecutionError is an Exception."""
        from src.services.playbook_execution_service import PlaybookExecutionError
        assert issubclass(PlaybookExecutionError, Exception)

    def test_playbook_execution_not_found_error_is_playbook_execution_error(self):
        """Test that PlaybookExecutionNotFoundError inherits from PlaybookExecutionError."""
        from src.services.playbook_execution_service import (
            PlaybookExecutionError,
            PlaybookExecutionNotFoundError
        )
        assert issubclass(PlaybookExecutionNotFoundError, PlaybookExecutionError)

    def test_playbook_execution_error_can_be_raised(self):
        """Test that PlaybookExecutionError can be raised with a message."""
        from src.services.playbook_execution_service import PlaybookExecutionError
        with pytest.raises(PlaybookExecutionError) as exc_info:
            raise PlaybookExecutionError("Test error message")
        assert "Test error message" in str(exc_info.value)

    def test_playbook_execution_not_found_error_can_be_raised(self):
        """Test that PlaybookExecutionNotFoundError can be raised with a message."""
        from src.services.playbook_execution_service import PlaybookExecutionNotFoundError
        with pytest.raises(PlaybookExecutionNotFoundError) as exc_info:
            raise PlaybookExecutionNotFoundError("Execution not found: exec-123")
        assert "exec-123" in str(exc_info.value)


class TestPlaybookExecutionServiceInitialization:
    """Tests for PlaybookExecutionService initialization."""

    def test_service_can_be_initialized_with_db_session(self):
        """Test that service can be initialized with a db session."""
        from src.services.playbook_execution_service import PlaybookExecutionService
        mock_db_session = MagicMock()
        service = PlaybookExecutionService(db_session=mock_db_session)
        assert service._db == mock_db_session

    def test_service_can_be_initialized_with_playbook_service(self):
        """Test that service can be initialized with a playbook service."""
        from src.services.playbook_execution_service import PlaybookExecutionService
        mock_db_session = MagicMock()
        mock_playbook_service = MagicMock()
        service = PlaybookExecutionService(
            db_session=mock_db_session,
            playbook_service=mock_playbook_service
        )
        assert service._playbook_service == mock_playbook_service


class TestGetPlaybookExecutionServiceFunction:
    """Tests for get_playbook_execution_service function."""

    def test_get_playbook_execution_service_is_callable(self):
        """Test that get_playbook_execution_service is callable."""
        from src.services.playbook_execution_service import get_playbook_execution_service
        assert callable(get_playbook_execution_service)

    def test_reset_playbook_execution_service_exists(self):
        """Test that reset_playbook_execution_service function exists."""
        from src.services.playbook_execution_service import reset_playbook_execution_service
        assert callable(reset_playbook_execution_service)
