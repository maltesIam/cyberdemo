"""
Unit tests for WebhookConfigDB SQLAlchemy model (TECH-005).

Tests for the database schema for webhook_configs table as specified in
the functional spec REQ-001-001-001 to REQ-001-001-005.

Task: T-1.1.002
Agent: build-1
TDD Phase: Tests written before implementation.
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import inspect
from unittest.mock import MagicMock, patch


class TestWebhookConfigDBModelExists:
    """Tests to verify WebhookConfigDB model exists with correct structure."""

    def test_webhook_config_db_model_can_be_imported(self):
        """Test that WebhookConfigDB model can be imported from models."""
        from src.models.webhook_config_db import WebhookConfigDB
        assert WebhookConfigDB is not None

    def test_webhook_event_type_enum_can_be_imported(self):
        """Test that WebhookEventType enum can be imported."""
        from src.models.webhook_config_db import WebhookEventType
        assert WebhookEventType is not None


class TestWebhookEventTypeEnum:
    """Tests for WebhookEventType enum values."""

    def test_event_type_has_critical_alert(self):
        """Test that event type enum has CRITICAL_ALERT value."""
        from src.models.webhook_config_db import WebhookEventType
        assert WebhookEventType.CRITICAL_ALERT == "critical_alert"

    def test_event_type_has_high_severity_alert(self):
        """Test that event type enum has HIGH_SEVERITY_ALERT value."""
        from src.models.webhook_config_db import WebhookEventType
        assert WebhookEventType.HIGH_SEVERITY_ALERT == "high_severity_alert"

    def test_event_type_has_incident_created(self):
        """Test that event type enum has INCIDENT_CREATED value."""
        from src.models.webhook_config_db import WebhookEventType
        assert WebhookEventType.INCIDENT_CREATED == "incident_created"

    def test_event_type_has_analysis_request(self):
        """Test that event type enum has ANALYSIS_REQUEST value."""
        from src.models.webhook_config_db import WebhookEventType
        assert WebhookEventType.ANALYSIS_REQUEST == "analysis_request"

    def test_event_type_has_correlation_found(self):
        """Test that event type enum has CORRELATION_FOUND value."""
        from src.models.webhook_config_db import WebhookEventType
        assert WebhookEventType.CORRELATION_FOUND == "correlation_found"


class TestWebhookConfigDBTableSchema:
    """Tests for WebhookConfigDB table schema."""

    def test_webhook_config_db_has_correct_tablename(self):
        """Test that WebhookConfigDB has correct tablename."""
        from src.models.webhook_config_db import WebhookConfigDB
        assert WebhookConfigDB.__tablename__ == "webhook_configs"

    def test_webhook_config_db_has_id_column(self):
        """Test that WebhookConfigDB has id column as primary key."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        assert "id" in mapper.columns
        assert mapper.columns["id"].primary_key

    def test_webhook_config_db_has_name_column(self):
        """Test that WebhookConfigDB has name column."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        assert "name" in mapper.columns

    def test_webhook_config_db_has_url_column(self):
        """Test that WebhookConfigDB has url column."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        assert "url" in mapper.columns

    def test_webhook_config_db_has_event_types_column(self):
        """Test that WebhookConfigDB has event_types column (JSON array)."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        assert "event_types" in mapper.columns

    def test_webhook_config_db_has_secret_column(self):
        """Test that WebhookConfigDB has secret column for HMAC."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        assert "secret" in mapper.columns

    def test_webhook_config_db_has_timeout_seconds_column(self):
        """Test that WebhookConfigDB has timeout_seconds column."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        assert "timeout_seconds" in mapper.columns

    def test_webhook_config_db_has_max_retries_column(self):
        """Test that WebhookConfigDB has max_retries column."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        assert "max_retries" in mapper.columns

    def test_webhook_config_db_has_retry_delay_seconds_column(self):
        """Test that WebhookConfigDB has retry_delay_seconds column."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        assert "retry_delay_seconds" in mapper.columns

    def test_webhook_config_db_has_is_active_column(self):
        """Test that WebhookConfigDB has is_active column."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        assert "is_active" in mapper.columns

    def test_webhook_config_db_has_headers_column(self):
        """Test that WebhookConfigDB has headers column (JSON)."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        assert "headers" in mapper.columns

    def test_webhook_config_db_has_created_at_column(self):
        """Test that WebhookConfigDB has created_at column."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        assert "created_at" in mapper.columns

    def test_webhook_config_db_has_updated_at_column(self):
        """Test that WebhookConfigDB has updated_at column."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        assert "updated_at" in mapper.columns

    def test_webhook_config_db_has_last_triggered_at_column(self):
        """Test that WebhookConfigDB has last_triggered_at column."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        assert "last_triggered_at" in mapper.columns

    def test_webhook_config_db_has_last_success_at_column(self):
        """Test that WebhookConfigDB has last_success_at column."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        assert "last_success_at" in mapper.columns

    def test_webhook_config_db_has_last_failure_at_column(self):
        """Test that WebhookConfigDB has last_failure_at column."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        assert "last_failure_at" in mapper.columns

    def test_webhook_config_db_has_failure_count_column(self):
        """Test that WebhookConfigDB has failure_count column."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        assert "failure_count" in mapper.columns


class TestWebhookConfigDBDefaults:
    """Tests for WebhookConfigDB default values."""

    def test_default_timeout_seconds_is_30(self):
        """Test that timeout_seconds column has 30 as default (BR-002)."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        timeout_col = mapper.columns["timeout_seconds"]
        assert timeout_col.default is not None
        assert timeout_col.default.arg == 30

    def test_default_max_retries_is_3(self):
        """Test that max_retries column has 3 as default (REQ-001-001-003)."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        max_retries_col = mapper.columns["max_retries"]
        assert max_retries_col.default is not None
        assert max_retries_col.default.arg == 3

    def test_default_retry_delay_seconds_is_5(self):
        """Test that retry_delay_seconds column has 5 as default."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        retry_delay_col = mapper.columns["retry_delay_seconds"]
        assert retry_delay_col.default is not None
        assert retry_delay_col.default.arg == 5

    def test_default_is_active_is_true(self):
        """Test that is_active column has True as default."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        is_active_col = mapper.columns["is_active"]
        assert is_active_col.default is not None
        assert is_active_col.default.arg is True

    def test_default_failure_count_is_0(self):
        """Test that failure_count column has 0 as default."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        failure_count_col = mapper.columns["failure_count"]
        assert failure_count_col.default is not None
        assert failure_count_col.default.arg == 0


class TestWebhookConfigDBIndexes:
    """Tests for WebhookConfigDB table indexes."""

    def test_name_column_is_unique(self):
        """Test that name column is unique."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        name_col = mapper.columns["name"]
        assert name_col.unique is True

    def test_is_active_column_is_indexed(self):
        """Test that is_active column is indexed for filtering active webhooks."""
        from src.models.webhook_config_db import WebhookConfigDB
        mapper = inspect(WebhookConfigDB)
        is_active_col = mapper.columns["is_active"]
        assert is_active_col.index is True


class TestWebhookConfigDBCreation:
    """Tests for WebhookConfigDB instance creation."""

    def test_create_webhook_config_with_required_fields(self):
        """Test creating WebhookConfigDB with minimum required fields."""
        from src.models.webhook_config_db import WebhookConfigDB
        webhook = WebhookConfigDB(
            name="test-webhook",
            url="https://agent.example.com/webhook",
            event_types=["critical_alert", "high_severity_alert"]
        )
        assert webhook.name == "test-webhook"
        assert webhook.url == "https://agent.example.com/webhook"
        assert webhook.event_types == ["critical_alert", "high_severity_alert"]

    def test_create_webhook_config_with_all_fields(self):
        """Test creating WebhookConfigDB with all fields."""
        from src.models.webhook_config_db import WebhookConfigDB
        webhook = WebhookConfigDB(
            name="test-webhook",
            url="https://agent.example.com/webhook",
            event_types=["critical_alert"],
            secret="my-secret-key",
            headers={"Authorization": "Bearer token123"}
        )
        webhook.timeout_seconds = 60
        webhook.max_retries = 5
        webhook.is_active = True

        assert webhook.name == "test-webhook"
        assert webhook.url == "https://agent.example.com/webhook"
        assert webhook.secret == "my-secret-key"
        assert webhook.timeout_seconds == 60
        assert webhook.max_retries == 5
        assert webhook.headers == {"Authorization": "Bearer token123"}


class TestWebhookConfigDBMethods:
    """Tests for WebhookConfigDB methods."""

    def test_should_retry_returns_true_when_under_max(self):
        """Test should_retry returns True when failure_count < max_retries."""
        from src.models.webhook_config_db import WebhookConfigDB
        webhook = WebhookConfigDB(
            name="test",
            url="https://example.com",
            event_types=[]
        )
        webhook.failure_count = 1
        webhook.max_retries = 3
        assert webhook.should_retry() is True

    def test_should_retry_returns_false_when_at_max(self):
        """Test should_retry returns False when failure_count >= max_retries."""
        from src.models.webhook_config_db import WebhookConfigDB
        webhook = WebhookConfigDB(
            name="test",
            url="https://example.com",
            event_types=[]
        )
        webhook.failure_count = 3
        webhook.max_retries = 3
        assert webhook.should_retry() is False

    def test_get_retry_delay_with_exponential_backoff(self):
        """Test get_retry_delay returns exponential backoff delay."""
        from src.models.webhook_config_db import WebhookConfigDB
        webhook = WebhookConfigDB(
            name="test",
            url="https://example.com",
            event_types=[]
        )
        webhook.retry_delay_seconds = 5
        webhook.failure_count = 2
        # Should be base_delay * 2^(failure_count-1) = 5 * 2^1 = 10
        assert webhook.get_retry_delay() == 10

    def test_increment_failure_count(self):
        """Test increment_failure_count increases failure_count."""
        from src.models.webhook_config_db import WebhookConfigDB
        from datetime import timezone
        webhook = WebhookConfigDB(
            name="test",
            url="https://example.com",
            event_types=[]
        )
        webhook.failure_count = 0
        webhook.increment_failure_count()
        assert webhook.failure_count == 1
        assert webhook.last_failure_at is not None

    def test_reset_failure_count(self):
        """Test reset_failure_count resets failure_count to 0."""
        from src.models.webhook_config_db import WebhookConfigDB
        from datetime import timezone
        webhook = WebhookConfigDB(
            name="test",
            url="https://example.com",
            event_types=[]
        )
        webhook.failure_count = 5
        webhook.reset_failure_count()
        assert webhook.failure_count == 0
        assert webhook.last_success_at is not None
