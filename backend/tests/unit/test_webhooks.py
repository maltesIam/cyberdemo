"""
Unit tests for Webhook Configuration API (REQ-001-001-001).

Tests for the webhook configuration endpoint POST /api/v1/webhooks/configure.

Task: T-1.2.001
Agent: build-1
TDD Phase: Tests written before implementation.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime


class TestWebhookAPIModuleExists:
    """Tests to verify webhook API module exists."""

    def test_webhook_router_can_be_imported(self):
        """Test that webhook router can be imported."""
        from src.api.webhooks import router
        assert router is not None

    def test_webhook_service_can_be_imported(self):
        """Test that WebhookService can be imported."""
        from src.services.webhook_service import WebhookService
        assert WebhookService is not None


class TestWebhookSchemas:
    """Tests for webhook Pydantic schemas."""

    def test_webhook_config_create_schema_exists(self):
        """Test that WebhookConfigCreate schema exists."""
        from src.api.webhooks import WebhookConfigCreate
        assert WebhookConfigCreate is not None

    def test_webhook_config_create_validates_url(self):
        """Test that WebhookConfigCreate validates URL format."""
        from src.api.webhooks import WebhookConfigCreate
        from pydantic import ValidationError

        # Valid URL should pass
        config = WebhookConfigCreate(
            name="test-webhook",
            url="https://example.com/webhook",
            event_types=["critical_alert"]
        )
        assert str(config.url) == "https://example.com/webhook"

        # Invalid URL should fail
        with pytest.raises(ValidationError):
            WebhookConfigCreate(
                name="test-webhook",
                url="not-a-valid-url",
                event_types=["critical_alert"]
            )

    def test_webhook_config_create_validates_event_types(self):
        """Test that WebhookConfigCreate validates event_types."""
        from src.api.webhooks import WebhookConfigCreate
        from pydantic import ValidationError

        # Valid event types should pass
        config = WebhookConfigCreate(
            name="test-webhook",
            url="https://example.com/webhook",
            event_types=["critical_alert", "high_severity_alert"]
        )
        assert len(config.event_types) == 2

        # Invalid event type should fail
        with pytest.raises(ValidationError):
            WebhookConfigCreate(
                name="test-webhook",
                url="https://example.com/webhook",
                event_types=["invalid_event_type"]
            )

    def test_webhook_config_response_schema_exists(self):
        """Test that WebhookConfigResponse schema exists."""
        from src.api.webhooks import WebhookConfigResponse
        assert WebhookConfigResponse is not None


class TestWebhookEndpoints:
    """Tests for webhook API endpoints."""

    @pytest.mark.asyncio
    async def test_create_webhook_endpoint_exists(self):
        """Test that POST /api/v1/webhooks/configure endpoint exists."""
        from src.api.webhooks import router
        routes = [route.path for route in router.routes]
        assert "/configure" in routes or any("/configure" in r for r in routes)

    @pytest.mark.asyncio
    async def test_get_webhook_endpoint_exists(self):
        """Test that GET /api/v1/webhooks/{webhook_id} endpoint exists."""
        from src.api.webhooks import router
        routes = [route.path for route in router.routes]
        assert "/{webhook_id}" in routes or any("/{webhook_id}" in r for r in routes)

    @pytest.mark.asyncio
    async def test_list_webhooks_endpoint_exists(self):
        """Test that GET /api/v1/webhooks endpoint exists."""
        from src.api.webhooks import router
        routes = [route.path for route in router.routes]
        # The route path is "/webhooks/" (with prefix applied)
        assert any("/webhooks/" in r or r == "/" for r in routes)

    @pytest.mark.asyncio
    async def test_update_webhook_endpoint_exists(self):
        """Test that PUT /api/v1/webhooks/{webhook_id} endpoint exists."""
        from src.api.webhooks import router
        routes = [route.path for route in router.routes]
        assert "/{webhook_id}" in routes or any("/{webhook_id}" in r for r in routes)

    @pytest.mark.asyncio
    async def test_delete_webhook_endpoint_exists(self):
        """Test that DELETE /api/v1/webhooks/{webhook_id} endpoint exists."""
        from src.api.webhooks import router
        routes = [route.path for route in router.routes]
        assert "/{webhook_id}" in routes or any("/{webhook_id}" in r for r in routes)

    @pytest.mark.asyncio
    async def test_test_webhook_endpoint_exists(self):
        """Test that POST /api/v1/webhooks/{webhook_id}/test endpoint exists."""
        from src.api.webhooks import router
        routes = [route.path for route in router.routes]
        assert any("/test" in r for r in routes)


class TestWebhookService:
    """Tests for WebhookService."""

    @pytest.mark.asyncio
    async def test_create_webhook_returns_webhook_config(self):
        """Test that create_webhook returns a WebhookConfigDB instance."""
        from src.services.webhook_service import WebhookService

        mock_session = AsyncMock()
        service = WebhookService(mock_session)

        result = await service.create_webhook(
            name="test-webhook",
            url="https://example.com/webhook",
            event_types=["critical_alert"]
        )

        assert result is not None
        assert result.name == "test-webhook"
        assert result.url == "https://example.com/webhook"

    @pytest.mark.asyncio
    async def test_get_webhook_returns_none_if_not_found(self):
        """Test that get_webhook returns None if webhook not found."""
        from src.services.webhook_service import WebhookService

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        service = WebhookService(mock_session)
        result = await service.get_webhook("nonexistent-id")

        assert result is None

    @pytest.mark.asyncio
    async def test_list_webhooks_returns_list(self):
        """Test that list_webhooks returns a list of webhooks."""
        from src.services.webhook_service import WebhookService

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        service = WebhookService(mock_session)
        result = await service.list_webhooks()

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_update_webhook_updates_fields(self):
        """Test that update_webhook updates specified fields."""
        from src.services.webhook_service import WebhookService
        from src.models.webhook_config_db import WebhookConfigDB

        mock_webhook = WebhookConfigDB(
            name="test-webhook",
            url="https://example.com/webhook",
            event_types=["critical_alert"]
        )
        mock_webhook.id = "test-id"

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_webhook
        mock_session.execute.return_value = mock_result

        service = WebhookService(mock_session)
        result = await service.update_webhook(
            webhook_id="test-id",
            url="https://new-url.com/webhook"
        )

        assert result is not None
        assert result.url == "https://new-url.com/webhook"

    @pytest.mark.asyncio
    async def test_delete_webhook_returns_true_on_success(self):
        """Test that delete_webhook returns True on successful deletion."""
        from src.services.webhook_service import WebhookService
        from src.models.webhook_config_db import WebhookConfigDB

        mock_webhook = WebhookConfigDB(
            name="test-webhook",
            url="https://example.com/webhook",
            event_types=["critical_alert"]
        )

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_webhook
        mock_session.execute.return_value = mock_result

        service = WebhookService(mock_session)
        result = await service.delete_webhook("test-id")

        assert result is True
        mock_session.delete.assert_called_once_with(mock_webhook)

    @pytest.mark.asyncio
    async def test_delete_webhook_returns_false_if_not_found(self):
        """Test that delete_webhook returns False if webhook not found."""
        from src.services.webhook_service import WebhookService

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        service = WebhookService(mock_session)
        result = await service.delete_webhook("nonexistent-id")

        assert result is False


class TestWebhookValidation:
    """Tests for webhook configuration validation."""

    def test_timeout_must_be_positive(self):
        """Test that timeout_seconds must be positive."""
        from src.api.webhooks import WebhookConfigCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            WebhookConfigCreate(
                name="test-webhook",
                url="https://example.com/webhook",
                event_types=["critical_alert"],
                timeout_seconds=-1
            )

    def test_timeout_has_maximum(self):
        """Test that timeout_seconds has a maximum of 120 seconds."""
        from src.api.webhooks import WebhookConfigCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            WebhookConfigCreate(
                name="test-webhook",
                url="https://example.com/webhook",
                event_types=["critical_alert"],
                timeout_seconds=300
            )

    def test_max_retries_has_maximum(self):
        """Test that max_retries has a maximum of 10."""
        from src.api.webhooks import WebhookConfigCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            WebhookConfigCreate(
                name="test-webhook",
                url="https://example.com/webhook",
                event_types=["critical_alert"],
                max_retries=20
            )

    def test_name_cannot_be_empty(self):
        """Test that name cannot be empty."""
        from src.api.webhooks import WebhookConfigCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            WebhookConfigCreate(
                name="",
                url="https://example.com/webhook",
                event_types=["critical_alert"]
            )
