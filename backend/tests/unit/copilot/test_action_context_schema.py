"""
Unit tests for Copilot Action Context Schema.

REQ-004-001-003: Context includes: action, element, visible data

Tests follow TDD methodology - written BEFORE implementation.
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4


class TestActionContextSchema:
    """Test suite for CopilotActionContext Pydantic model."""

    def test_import_action_context_schema(self):
        """Test that CopilotActionContext can be imported."""
        from src.models.copilot import CopilotActionContext
        assert CopilotActionContext is not None

    def test_import_action_type_enum(self):
        """Test that CopilotActionType enum can be imported."""
        from src.models.copilot import CopilotActionType
        assert CopilotActionType is not None

    def test_action_type_enum_values(self):
        """Test that CopilotActionType has required enum values."""
        from src.models.copilot import CopilotActionType

        # Verify required action types exist
        assert hasattr(CopilotActionType, "CLICK")
        assert hasattr(CopilotActionType, "VIEW")
        assert hasattr(CopilotActionType, "SEARCH")
        assert hasattr(CopilotActionType, "FILTER")
        assert hasattr(CopilotActionType, "SELECT")
        assert hasattr(CopilotActionType, "EXPAND")
        assert hasattr(CopilotActionType, "NAVIGATE")
        assert hasattr(CopilotActionType, "SUBMIT")
        assert hasattr(CopilotActionType, "HOVER")

    def test_create_minimal_action_context(self):
        """Test creating action context with minimal required fields."""
        from src.models.copilot import (
            CopilotActionContext,
            CopilotActionType,
        )

        context = CopilotActionContext(
            action=CopilotActionType.CLICK,
            element="alert-row",
            session_id="test-session-123",
        )

        assert context.action == CopilotActionType.CLICK
        assert context.element == "alert-row"
        assert context.session_id == "test-session-123"

    def test_create_full_action_context(self):
        """Test creating action context with all fields."""
        from src.models.copilot import (
            CopilotActionContext,
            CopilotActionType,
        )

        visible_data = {
            "alert_id": "ALT-001",
            "severity": "critical",
            "status": "new",
        }
        metadata = {
            "user_id": "analyst-01",
            "viewport_width": 1920,
        }

        context = CopilotActionContext(
            action=CopilotActionType.SELECT,
            element="alert-detail-panel",
            session_id="session-456",
            visible_data=visible_data,
            metadata=metadata,
            element_id="alert-ALT-001",
            page="alerts",
            timestamp="2026-02-23T10:00:00Z",
        )

        assert context.action == CopilotActionType.SELECT
        assert context.element == "alert-detail-panel"
        assert context.session_id == "session-456"
        assert context.visible_data == visible_data
        assert context.metadata == metadata
        assert context.element_id == "alert-ALT-001"
        assert context.page == "alerts"
        assert context.timestamp == "2026-02-23T10:00:00Z"

    def test_action_context_requires_action(self):
        """Test that action field is required."""
        from src.models.copilot import CopilotActionContext
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            CopilotActionContext(
                element="button",
                session_id="session-123",
            )

        assert "action" in str(exc_info.value)

    def test_action_context_requires_element(self):
        """Test that element field is required."""
        from src.models.copilot import (
            CopilotActionContext,
            CopilotActionType,
        )
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            CopilotActionContext(
                action=CopilotActionType.CLICK,
                session_id="session-123",
            )

        assert "element" in str(exc_info.value)

    def test_action_context_requires_session_id(self):
        """Test that session_id field is required."""
        from src.models.copilot import (
            CopilotActionContext,
            CopilotActionType,
        )
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            CopilotActionContext(
                action=CopilotActionType.CLICK,
                element="button",
            )

        assert "session_id" in str(exc_info.value)

    def test_action_context_json_serialization(self):
        """Test that action context serializes to JSON correctly."""
        from src.models.copilot import (
            CopilotActionContext,
            CopilotActionType,
        )

        context = CopilotActionContext(
            action=CopilotActionType.NAVIGATE,
            element="sidebar-link",
            session_id="session-789",
            visible_data={"page": "dashboard"},
        )

        json_data = context.model_dump()

        assert json_data["action"] == "navigate"
        assert json_data["element"] == "sidebar-link"
        assert json_data["session_id"] == "session-789"
        assert json_data["visible_data"] == {"page": "dashboard"}

    def test_action_context_from_dict(self):
        """Test creating action context from dictionary."""
        from src.models.copilot import CopilotActionContext

        data = {
            "action": "click",
            "element": "button",
            "session_id": "session-001",
            "visible_data": {"button_label": "Investigate"},
        }

        context = CopilotActionContext.model_validate(data)

        assert context.action.value == "click"
        assert context.element == "button"
        assert context.session_id == "session-001"

    def test_action_context_optional_visible_data_defaults_to_none(self):
        """Test that visible_data defaults to None when not provided."""
        from src.models.copilot import (
            CopilotActionContext,
            CopilotActionType,
        )

        context = CopilotActionContext(
            action=CopilotActionType.VIEW,
            element="panel",
            session_id="session-123",
        )

        assert context.visible_data is None

    def test_action_context_optional_metadata_defaults_to_none(self):
        """Test that metadata defaults to None when not provided."""
        from src.models.copilot import (
            CopilotActionContext,
            CopilotActionType,
        )

        context = CopilotActionContext(
            action=CopilotActionType.VIEW,
            element="panel",
            session_id="session-123",
        )

        assert context.metadata is None


class TestCopilotActionBatch:
    """Test suite for batched action context for WebSocket transmission."""

    def test_import_action_batch(self):
        """Test that CopilotActionBatch can be imported."""
        from src.models.copilot import CopilotActionBatch
        assert CopilotActionBatch is not None

    def test_create_action_batch(self):
        """Test creating a batch of actions."""
        from src.models.copilot import (
            CopilotActionBatch,
            CopilotActionContext,
            CopilotActionType,
        )

        actions = [
            CopilotActionContext(
                action=CopilotActionType.CLICK,
                element="button",
                session_id="session-123",
            ),
            CopilotActionContext(
                action=CopilotActionType.VIEW,
                element="panel",
                session_id="session-123",
            ),
        ]

        batch = CopilotActionBatch(
            session_id="session-123",
            actions=actions,
        )

        assert batch.session_id == "session-123"
        assert len(batch.actions) == 2

    def test_action_batch_has_timestamp(self):
        """Test that action batch has a timestamp field."""
        from src.models.copilot import (
            CopilotActionBatch,
            CopilotActionContext,
            CopilotActionType,
        )

        batch = CopilotActionBatch(
            session_id="session-123",
            actions=[
                CopilotActionContext(
                    action=CopilotActionType.CLICK,
                    element="button",
                    session_id="session-123",
                )
            ],
            batch_timestamp="2026-02-23T10:00:00Z",
        )

        assert batch.batch_timestamp == "2026-02-23T10:00:00Z"


class TestCopilotSuggestionResponse:
    """Test suite for suggestion response schema."""

    def test_import_suggestion_response(self):
        """Test that CopilotSuggestionResponse can be imported."""
        from src.models.copilot import CopilotSuggestionResponse
        assert CopilotSuggestionResponse is not None

    def test_create_suggestion_response(self):
        """Test creating a suggestion response."""
        from src.models.copilot import CopilotSuggestionResponse

        response = CopilotSuggestionResponse(
            suggestion_id="sug-001",
            content="You should investigate the related IP addresses",
            confidence=0.85,
            action_type="investigate",
        )

        assert response.suggestion_id == "sug-001"
        assert "investigate" in response.content.lower()
        assert response.confidence == 0.85
        assert response.action_type == "investigate"

    def test_suggestion_response_optional_reason(self):
        """Test that reason field is optional."""
        from src.models.copilot import CopilotSuggestionResponse

        response = CopilotSuggestionResponse(
            suggestion_id="sug-002",
            content="Check the process tree",
            confidence=0.75,
            action_type="analyze",
        )

        assert response.reason is None

    def test_suggestion_response_with_reason(self):
        """Test creating suggestion with reason."""
        from src.models.copilot import CopilotSuggestionResponse

        response = CopilotSuggestionResponse(
            suggestion_id="sug-003",
            content="Correlate with firewall logs",
            confidence=0.9,
            action_type="correlate",
            reason="Similar attack pattern detected in last 24 hours",
        )

        assert response.reason == "Similar attack pattern detected in last 24 hours"


class TestCopilotSessionTracking:
    """Test suite for session tracking schema."""

    def test_import_session_state(self):
        """Test that CopilotSessionState can be imported."""
        from src.models.copilot import CopilotSessionState
        assert CopilotSessionState is not None

    def test_create_session_state(self):
        """Test creating session state."""
        from src.models.copilot import CopilotSessionState

        state = CopilotSessionState(
            session_id="session-123",
            accepted_suggestions=5,
            rejected_suggestions=2,
            total_actions=100,
        )

        assert state.session_id == "session-123"
        assert state.accepted_suggestions == 5
        assert state.rejected_suggestions == 2
        assert state.total_actions == 100

    def test_session_state_defaults(self):
        """Test that session state has sensible defaults."""
        from src.models.copilot import CopilotSessionState

        state = CopilotSessionState(session_id="session-new")

        assert state.accepted_suggestions == 0
        assert state.rejected_suggestions == 0
        assert state.total_actions == 0

    def test_session_state_calculates_acceptance_rate(self):
        """Test that session state can calculate acceptance rate."""
        from src.models.copilot import CopilotSessionState

        state = CopilotSessionState(
            session_id="session-123",
            accepted_suggestions=8,
            rejected_suggestions=2,
        )

        # Acceptance rate = accepted / (accepted + rejected)
        assert state.acceptance_rate == 0.8

    def test_session_state_acceptance_rate_zero_when_no_suggestions(self):
        """Test acceptance rate is 0 when no suggestions made."""
        from src.models.copilot import CopilotSessionState

        state = CopilotSessionState(session_id="session-empty")

        assert state.acceptance_rate == 0.0
