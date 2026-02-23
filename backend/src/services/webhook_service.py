"""
WebhookService for managing webhook configurations.

This service implements CRUD operations for webhook configurations
and provides functionality for webhook management.

Task: T-1.2.001
Agent: build-1
Requirements: REQ-001-001-001 - API endpoint POST /api/v1/webhooks/configure
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.webhook_config_db import WebhookConfigDB, WebhookEventType


class WebhookService:
    """Service for managing webhook configurations.

    Provides CRUD operations and validation for webhook configurations.
    Implements REQ-001-001-001.
    """

    def __init__(self, session: AsyncSession):
        """Initialize the service with a database session.

        Args:
            session: Async SQLAlchemy session for database operations.
        """
        self.session = session

    async def create_webhook(
        self,
        name: str,
        url: str,
        event_types: List[str],
        secret: Optional[str] = None,
        timeout_seconds: int = 30,
        max_retries: int = 3,
        retry_delay_seconds: int = 5,
        headers: Optional[dict] = None
    ) -> WebhookConfigDB:
        """Create a new webhook configuration.

        Args:
            name: Human-readable name for the webhook (unique).
            url: Target URL for the webhook.
            event_types: List of event types that trigger this webhook.
            secret: Optional secret for HMAC signature validation.
            timeout_seconds: Timeout in seconds (default 30s per BR-002).
            max_retries: Maximum retry attempts (default 3 per REQ-001-001-003).
            retry_delay_seconds: Base delay between retries.
            headers: Optional custom headers to include in requests.

        Returns:
            The created WebhookConfigDB instance.
        """
        webhook = WebhookConfigDB(
            name=name,
            url=url,
            event_types=event_types,
            secret=secret,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            retry_delay_seconds=retry_delay_seconds,
            headers=headers
        )

        self.session.add(webhook)
        await self.session.flush()
        await self.session.refresh(webhook)

        return webhook

    async def get_webhook(self, webhook_id: str) -> Optional[WebhookConfigDB]:
        """Get a webhook configuration by ID.

        Args:
            webhook_id: The webhook's UUID.

        Returns:
            The WebhookConfigDB instance if found, None otherwise.
        """
        stmt = select(WebhookConfigDB).where(WebhookConfigDB.id == webhook_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_webhook_by_name(self, name: str) -> Optional[WebhookConfigDB]:
        """Get a webhook configuration by name.

        Args:
            name: The webhook's name.

        Returns:
            The WebhookConfigDB instance if found, None otherwise.
        """
        stmt = select(WebhookConfigDB).where(WebhookConfigDB.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_webhooks(
        self,
        active_only: bool = False,
        event_type: Optional[str] = None
    ) -> List[WebhookConfigDB]:
        """List all webhook configurations.

        Args:
            active_only: If True, only return active webhooks.
            event_type: If provided, filter by event type.

        Returns:
            List of WebhookConfigDB instances.
        """
        stmt = select(WebhookConfigDB)

        if active_only:
            stmt = stmt.where(WebhookConfigDB.is_active == True)

        result = await self.session.execute(stmt)
        webhooks = result.scalars().all()

        # Filter by event_type in Python (JSON column filtering)
        if event_type:
            webhooks = [
                w for w in webhooks
                if event_type in (w.event_types or [])
            ]

        return list(webhooks)

    async def update_webhook(
        self,
        webhook_id: str,
        name: Optional[str] = None,
        url: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        secret: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        max_retries: Optional[int] = None,
        retry_delay_seconds: Optional[int] = None,
        is_active: Optional[bool] = None,
        headers: Optional[dict] = None
    ) -> Optional[WebhookConfigDB]:
        """Update a webhook configuration.

        Args:
            webhook_id: The webhook's UUID.
            name: New name (optional).
            url: New URL (optional).
            event_types: New event types (optional).
            secret: New secret (optional).
            timeout_seconds: New timeout (optional).
            max_retries: New max retries (optional).
            retry_delay_seconds: New retry delay (optional).
            is_active: New active status (optional).
            headers: New headers (optional).

        Returns:
            The updated WebhookConfigDB instance if found, None otherwise.
        """
        webhook = await self.get_webhook(webhook_id)
        if webhook is None:
            return None

        if name is not None:
            webhook.name = name
        if url is not None:
            webhook.url = url
        if event_types is not None:
            webhook.event_types = event_types
        if secret is not None:
            webhook.secret = secret
        if timeout_seconds is not None:
            webhook.timeout_seconds = timeout_seconds
        if max_retries is not None:
            webhook.max_retries = max_retries
        if retry_delay_seconds is not None:
            webhook.retry_delay_seconds = retry_delay_seconds
        if is_active is not None:
            webhook.is_active = is_active
        if headers is not None:
            webhook.headers = headers

        await self.session.flush()
        await self.session.refresh(webhook)

        return webhook

    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook configuration.

        Args:
            webhook_id: The webhook's UUID.

        Returns:
            True if deleted, False if not found.
        """
        webhook = await self.get_webhook(webhook_id)
        if webhook is None:
            return False

        await self.session.delete(webhook)
        return True

    async def get_webhooks_for_event(self, event_type: str) -> List[WebhookConfigDB]:
        """Get all active webhooks that should be triggered for an event type.

        Args:
            event_type: The event type to filter by.

        Returns:
            List of active WebhookConfigDB instances configured for this event.
        """
        return await self.list_webhooks(active_only=True, event_type=event_type)
