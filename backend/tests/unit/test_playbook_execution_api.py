"""
Unit tests for Playbook Execution API endpoints (EPIC-005).

Tests for:
- REQ-005-001-001: POST /api/v1/playbooks/execute/{playbook_id}
- REQ-005-001-002: POST /api/v1/playbooks/{execution_id}/pause
- REQ-005-001-003: POST /api/v1/playbooks/{execution_id}/resume
- REQ-005-001-004: POST /api/v1/playbooks/{execution_id}/rollback
- REQ-005-001-005: GET /api/v1/playbooks/{execution_id}/status

Tasks: T-2.3.002, T-2.3.003, T-2.3.004, T-2.3.005, T-2.3.006
Agent: build-3
TDD Phase: Tests written before implementation.
"""
import pytest


class TestPlaybookExecutionAPIModuleExists:
    """Tests to verify playbook execution API module exists."""

    def test_playbook_api_router_can_be_imported(self):
        """Test that playbook API router can be imported."""
        from src.api.playbooks import router
        assert router is not None

    def test_playbook_execution_service_can_be_imported(self):
        """Test that PlaybookExecutionService can be imported."""
        from src.services.playbook_execution_service import PlaybookExecutionService
        assert PlaybookExecutionService is not None


class TestPlaybookExecutionRequestModels:
    """Tests for playbook execution request/response models."""

    def test_execute_playbook_request_model_exists(self):
        """Test that ExecutePlaybookRequest model exists."""
        from src.api.playbooks import ExecutePlaybookRequest
        assert ExecutePlaybookRequest is not None

    def test_execute_playbook_request_has_context_field(self):
        """Test that ExecutePlaybookRequest has context field."""
        from src.api.playbooks import ExecutePlaybookRequest
        request = ExecutePlaybookRequest(context={"incident_id": "INC-001"})
        assert request.context == {"incident_id": "INC-001"}

    def test_execute_playbook_request_context_defaults_to_empty_dict(self):
        """Test that context defaults to empty dict."""
        from src.api.playbooks import ExecutePlaybookRequest
        request = ExecutePlaybookRequest()
        assert request.context == {}

    def test_playbook_execution_response_model_exists(self):
        """Test that PlaybookExecutionResponse model exists."""
        from src.api.playbooks import PlaybookExecutionResponse
        assert PlaybookExecutionResponse is not None

    def test_playbook_execution_response_has_required_fields(self):
        """Test that PlaybookExecutionResponse has all required fields."""
        from src.api.playbooks import PlaybookExecutionResponse
        response = PlaybookExecutionResponse(
            id="exec-123",
            playbook_id="pb-001",
            playbook_name="Test Playbook",
            status="running",
            current_step=1,
            total_steps=5,
            progress=20,
            context={},
            created_at="2026-02-23T12:00:00"
        )
        assert response.id == "exec-123"
        assert response.playbook_id == "pb-001"
        assert response.status == "running"
        assert response.progress == 20


class TestExecutePlaybookEndpoint:
    """Tests for POST /api/v1/playbooks/execute/{playbook_id} (REQ-005-001-001)."""

    def test_execute_endpoint_exists(self):
        """Test that execute endpoint function exists."""
        from src.api.playbooks import execute_playbook
        assert execute_playbook is not None
        assert callable(execute_playbook)

    def test_execute_endpoint_is_async(self):
        """Test that execute endpoint is an async function."""
        import asyncio
        from src.api.playbooks import execute_playbook
        assert asyncio.iscoroutinefunction(execute_playbook)


class TestPausePlaybookEndpoint:
    """Tests for POST /api/v1/playbooks/{execution_id}/pause (REQ-005-001-002)."""

    def test_pause_endpoint_exists(self):
        """Test that pause endpoint function exists."""
        from src.api.playbooks import pause_playbook
        assert pause_playbook is not None
        assert callable(pause_playbook)

    def test_pause_endpoint_is_async(self):
        """Test that pause endpoint is an async function."""
        import asyncio
        from src.api.playbooks import pause_playbook
        assert asyncio.iscoroutinefunction(pause_playbook)


class TestResumePlaybookEndpoint:
    """Tests for POST /api/v1/playbooks/{execution_id}/resume (REQ-005-001-003)."""

    def test_resume_endpoint_exists(self):
        """Test that resume endpoint function exists."""
        from src.api.playbooks import resume_playbook
        assert resume_playbook is not None
        assert callable(resume_playbook)

    def test_resume_endpoint_is_async(self):
        """Test that resume endpoint is an async function."""
        import asyncio
        from src.api.playbooks import resume_playbook
        assert asyncio.iscoroutinefunction(resume_playbook)


class TestRollbackPlaybookEndpoint:
    """Tests for POST /api/v1/playbooks/{execution_id}/rollback (REQ-005-001-004)."""

    def test_rollback_endpoint_exists(self):
        """Test that rollback endpoint function exists."""
        from src.api.playbooks import rollback_playbook
        assert rollback_playbook is not None
        assert callable(rollback_playbook)

    def test_rollback_endpoint_is_async(self):
        """Test that rollback endpoint is an async function."""
        import asyncio
        from src.api.playbooks import rollback_playbook
        assert asyncio.iscoroutinefunction(rollback_playbook)


class TestGetStatusEndpoint:
    """Tests for GET /api/v1/playbooks/{execution_id}/status (REQ-005-001-005)."""

    def test_get_status_endpoint_exists(self):
        """Test that get_status endpoint function exists."""
        from src.api.playbooks import get_playbook_status
        assert get_playbook_status is not None
        assert callable(get_playbook_status)

    def test_get_status_endpoint_is_async(self):
        """Test that get_status endpoint is an async function."""
        import asyncio
        from src.api.playbooks import get_playbook_status
        assert asyncio.iscoroutinefunction(get_playbook_status)


class TestListPlaybookExecutions:
    """Tests for GET /api/v1/playbooks/executions (list all executions)."""

    def test_list_executions_endpoint_exists(self):
        """Test that list_executions endpoint function exists."""
        from src.api.playbooks import list_playbook_executions
        assert list_playbook_executions is not None
        assert callable(list_playbook_executions)

    def test_list_executions_endpoint_is_async(self):
        """Test that list_executions endpoint is an async function."""
        import asyncio
        from src.api.playbooks import list_playbook_executions
        assert asyncio.iscoroutinefunction(list_playbook_executions)


class TestPlaybookExecutionListResponse:
    """Tests for PlaybookExecutionListResponse model."""

    def test_playbook_execution_list_response_exists(self):
        """Test that PlaybookExecutionListResponse model exists."""
        from src.api.playbooks import PlaybookExecutionListResponse
        assert PlaybookExecutionListResponse is not None

    def test_playbook_execution_list_response_has_executions_field(self):
        """Test that PlaybookExecutionListResponse has executions field."""
        from src.api.playbooks import PlaybookExecutionListResponse, PlaybookExecutionResponse
        response = PlaybookExecutionListResponse(
            executions=[
                PlaybookExecutionResponse(
                    id="exec-1",
                    playbook_id="pb-1",
                    playbook_name="Test",
                    status="running",
                    current_step=0,
                    total_steps=5,
                    progress=0,
                    context={}
                )
            ],
            total=1
        )
        assert len(response.executions) == 1
        assert response.total == 1
