"""
Notification Service for the SOC platform.

Provides async, non-blocking notification delivery to multiple channels:
- Slack webhooks
- Microsoft Teams webhooks
- Email via SMTP
- Generic webhooks

All external calls are non-blocking and handle failures gracefully.
"""
import logging
import asyncio
import re
from typing import Optional
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiohttp

from ..models.notification import (
    NotificationChannelType,
    NotificationChannel,
    NotificationResult,
)

logger = logging.getLogger(__name__)

# Default timeout for HTTP requests (seconds)
DEFAULT_TIMEOUT = 10


class NotificationService:
    """
    Service for sending notifications to multiple channels.

    All methods are async and non-blocking. Failures are handled gracefully
    and do not raise exceptions - they return NotificationResult with success=False.
    """

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        """Initialize the notification service.

        Args:
            timeout: HTTP request timeout in seconds.
        """
        self.timeout = timeout

    def render_template(
        self,
        template: str,
        variables: Optional[dict[str, str]] = None,
    ) -> str:
        """Render a template with variable substitution.

        Uses {variable_name} syntax. Missing variables are left as placeholders.

        Args:
            template: Template string with {variable} placeholders.
            variables: Dictionary of variable values.

        Returns:
            Rendered string with variables substituted.
        """
        if not variables:
            return template

        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))

        return result

    async def send_slack_notification(
        self,
        webhook_url: str,
        message: str,
        variables: Optional[dict[str, str]] = None,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None,
    ) -> NotificationResult:
        """Send a notification to Slack via webhook.

        Args:
            webhook_url: Slack incoming webhook URL.
            message: Message text (supports {variable} substitution).
            variables: Variables for template substitution.
            username: Override bot username.
            icon_emoji: Override bot emoji icon (e.g., ":robot_face:").

        Returns:
            NotificationResult with success status and any error info.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        # Validate URL
        if not webhook_url or not webhook_url.startswith("http"):
            return NotificationResult(
                success=False,
                channel=NotificationChannelType.SLACK,
                error="Invalid webhook URL",
                timestamp=timestamp,
            )

        # Render template
        rendered_message = self.render_template(message, variables)

        # Build payload
        payload: dict = {"text": rendered_message}
        if username:
            payload["username"] = username
        if icon_emoji:
            payload["icon_emoji"] = icon_emoji

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    response_text = await response.text()

                    if response.status == 200 and response_text == "ok":
                        logger.info(f"Slack notification sent successfully")
                        return NotificationResult(
                            success=True,
                            channel=NotificationChannelType.SLACK,
                            timestamp=timestamp,
                        )
                    else:
                        error_msg = f"Slack API error: {response.status} - {response_text}"
                        logger.warning(error_msg)
                        return NotificationResult(
                            success=False,
                            channel=NotificationChannelType.SLACK,
                            error=error_msg,
                            timestamp=timestamp,
                        )

        except asyncio.TimeoutError:
            error_msg = "Slack notification timeout"
            logger.warning(error_msg)
            return NotificationResult(
                success=False,
                channel=NotificationChannelType.SLACK,
                error=error_msg,
                timestamp=timestamp,
            )
        except Exception as e:
            error_msg = f"Slack notification failed: {str(e)}"
            logger.error(error_msg)
            return NotificationResult(
                success=False,
                channel=NotificationChannelType.SLACK,
                error=error_msg,
                timestamp=timestamp,
            )

    async def send_teams_notification(
        self,
        webhook_url: str,
        message: str,
        title: Optional[str] = None,
        variables: Optional[dict[str, str]] = None,
        facts: Optional[dict[str, str]] = None,
        theme_color: str = "0076D7",
    ) -> NotificationResult:
        """Send a notification to Microsoft Teams via webhook.

        Uses the MessageCard format for Teams incoming webhooks.

        Args:
            webhook_url: Teams incoming webhook URL.
            message: Message text (supports {variable} substitution).
            title: Card title.
            variables: Variables for template substitution.
            facts: Additional facts to display as key-value pairs.
            theme_color: Card theme color (hex without #).

        Returns:
            NotificationResult with success status and any error info.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        # Validate URL
        if not webhook_url or not webhook_url.startswith("http"):
            return NotificationResult(
                success=False,
                channel=NotificationChannelType.TEAMS,
                error="Invalid webhook URL",
                timestamp=timestamp,
            )

        # Render template
        rendered_message = self.render_template(message, variables)

        # Build MessageCard payload
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": theme_color,
            "summary": title or "SOC Notification",
            "sections": [
                {
                    "activityTitle": title or "SOC Alert",
                    "text": rendered_message,
                }
            ],
        }

        # Add facts if provided
        if facts:
            payload["sections"][0]["facts"] = [
                {"name": k, "value": str(v)} for k, v in facts.items()
            ]

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    response_text = await response.text()

                    # Teams returns "1" on success
                    if response.status == 200:
                        logger.info(f"Teams notification sent successfully")
                        return NotificationResult(
                            success=True,
                            channel=NotificationChannelType.TEAMS,
                            timestamp=timestamp,
                        )
                    else:
                        error_msg = f"Teams API error: {response.status} - {response_text}"
                        logger.warning(error_msg)
                        return NotificationResult(
                            success=False,
                            channel=NotificationChannelType.TEAMS,
                            error=error_msg,
                            timestamp=timestamp,
                        )

        except asyncio.TimeoutError:
            error_msg = "Teams notification timeout"
            logger.warning(error_msg)
            return NotificationResult(
                success=False,
                channel=NotificationChannelType.TEAMS,
                error=error_msg,
                timestamp=timestamp,
            )
        except Exception as e:
            error_msg = f"Teams notification failed: {str(e)}"
            logger.error(error_msg)
            return NotificationResult(
                success=False,
                channel=NotificationChannelType.TEAMS,
                error=error_msg,
                timestamp=timestamp,
            )

    async def send_email_notification(
        self,
        smtp_server: str,
        smtp_port: int,
        from_email: str,
        to_emails: list[str],
        subject: str,
        body: str,
        variables: Optional[dict[str, str]] = None,
        html: bool = False,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
    ) -> NotificationResult:
        """Send an email notification via SMTP.

        Args:
            smtp_server: SMTP server hostname.
            smtp_port: SMTP server port.
            from_email: Sender email address.
            to_emails: List of recipient email addresses.
            subject: Email subject.
            body: Email body (supports {variable} substitution).
            variables: Variables for template substitution.
            html: If True, body is HTML; otherwise plain text.
            username: SMTP authentication username.
            password: SMTP authentication password.
            use_tls: Whether to use TLS.

        Returns:
            NotificationResult with success status and any error info.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        # Render template
        rendered_body = self.render_template(body, variables)
        rendered_subject = self.render_template(subject, variables)

        # Build email message
        if html:
            msg = MIMEMultipart("alternative")
            msg.attach(MIMEText(rendered_body, "html"))
        else:
            msg = MIMEMultipart()
            msg.attach(MIMEText(rendered_body, "plain"))

        msg["Subject"] = rendered_subject
        msg["From"] = from_email
        msg["To"] = ", ".join(to_emails)

        try:
            import aiosmtplib

            await aiosmtplib.send(
                msg,
                hostname=smtp_server,
                port=smtp_port,
                username=username,
                password=password,
                start_tls=use_tls,
                timeout=self.timeout,
            )

            logger.info(f"Email notification sent to {len(to_emails)} recipients")
            return NotificationResult(
                success=True,
                channel=NotificationChannelType.EMAIL,
                timestamp=timestamp,
            )

        except asyncio.TimeoutError:
            error_msg = "Email notification timeout"
            logger.warning(error_msg)
            return NotificationResult(
                success=False,
                channel=NotificationChannelType.EMAIL,
                error=error_msg,
                timestamp=timestamp,
            )
        except Exception as e:
            error_msg = f"Email notification failed: {str(e)}"
            logger.error(error_msg)
            return NotificationResult(
                success=False,
                channel=NotificationChannelType.EMAIL,
                error=error_msg,
                timestamp=timestamp,
            )

    async def send_webhook_notification(
        self,
        url: str,
        payload: dict,
        headers: Optional[dict[str, str]] = None,
        method: str = "POST",
    ) -> NotificationResult:
        """Send a notification to a generic webhook endpoint.

        Args:
            url: Webhook URL.
            payload: JSON payload to send.
            headers: Optional custom headers.
            method: HTTP method (default POST).

        Returns:
            NotificationResult with success status and any error info.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        # Validate URL
        if not url or not url.startswith("http"):
            return NotificationResult(
                success=False,
                channel=NotificationChannelType.WEBHOOK,
                error="Invalid webhook URL",
                timestamp=timestamp,
            )

        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    json=payload,
                    headers=request_headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    response_text = await response.text()

                    if 200 <= response.status < 300:
                        logger.info(f"Webhook notification sent to {url}")
                        return NotificationResult(
                            success=True,
                            channel=NotificationChannelType.WEBHOOK,
                            timestamp=timestamp,
                        )
                    else:
                        error_msg = f"Webhook error: {response.status} - {response_text}"
                        logger.warning(error_msg)
                        return NotificationResult(
                            success=False,
                            channel=NotificationChannelType.WEBHOOK,
                            error=error_msg,
                            timestamp=timestamp,
                        )

        except asyncio.TimeoutError:
            error_msg = "Webhook notification timeout"
            logger.warning(error_msg)
            return NotificationResult(
                success=False,
                channel=NotificationChannelType.WEBHOOK,
                error=error_msg,
                timestamp=timestamp,
            )
        except Exception as e:
            error_msg = f"Webhook notification failed: {str(e)}"
            logger.error(error_msg)
            return NotificationResult(
                success=False,
                channel=NotificationChannelType.WEBHOOK,
                error=error_msg,
                timestamp=timestamp,
            )

    async def send_to_channels(
        self,
        channels: list[NotificationChannel],
        message: str,
        variables: Optional[dict[str, str]] = None,
        title: Optional[str] = None,
    ) -> list[NotificationResult]:
        """Send notification to multiple channels concurrently.

        Args:
            channels: List of channel configurations.
            message: Message to send (supports {variable} substitution).
            variables: Variables for template substitution.
            title: Optional title for channels that support it.

        Returns:
            List of NotificationResult for each channel.
        """
        tasks = []

        for channel in channels:
            if not channel.enabled:
                continue

            if channel.type == NotificationChannelType.SLACK:
                webhook_url = channel.config.get("webhook_url", "")
                tasks.append(
                    self.send_slack_notification(
                        webhook_url=webhook_url,
                        message=message,
                        variables=variables,
                    )
                )

            elif channel.type == NotificationChannelType.TEAMS:
                webhook_url = channel.config.get("webhook_url", "")
                tasks.append(
                    self.send_teams_notification(
                        webhook_url=webhook_url,
                        message=message,
                        title=title,
                        variables=variables,
                    )
                )

            elif channel.type == NotificationChannelType.EMAIL:
                tasks.append(
                    self.send_email_notification(
                        smtp_server=channel.config.get("smtp_server", ""),
                        smtp_port=channel.config.get("smtp_port", 587),
                        from_email=channel.config.get("from_email", ""),
                        to_emails=channel.config.get("to_emails", []),
                        subject=title or "SOC Notification",
                        body=message,
                        variables=variables,
                        username=channel.config.get("username"),
                        password=channel.config.get("password"),
                    )
                )

            elif channel.type == NotificationChannelType.WEBHOOK:
                url = channel.config.get("url", "")
                tasks.append(
                    self.send_webhook_notification(
                        url=url,
                        payload={
                            "message": self.render_template(message, variables),
                            "title": title,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                        headers=channel.config.get("headers"),
                    )
                )

        if not tasks:
            return []

        # Execute all notifications concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert any exceptions to NotificationResult
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    NotificationResult(
                        success=False,
                        channel=channels[i].type,
                        error=str(result),
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    )
                )
            else:
                processed_results.append(result)

        return processed_results


# Re-export for tests
NotificationChannel = NotificationChannel
NotificationResult = NotificationResult
