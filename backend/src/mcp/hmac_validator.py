"""
HMAC Signature Validator for Webhooks.

Implements HMAC-SHA256 signature validation for webhook requests.
Requirement: TECH-009 - Autenticacion de webhooks con HMAC signature.

Features:
- HMAC-SHA256 signature generation and validation
- Constant-time comparison to prevent timing attacks
- Timestamp validation to prevent replay attacks
- Configurable webhook secrets
"""

import hmac
import hashlib
import time
from typing import Optional
import os


class HMACValidator:
    """
    HMAC-SHA256 signature validator for webhooks.

    Provides secure signature generation and validation using
    HMAC-SHA256 with constant-time comparison.

    Attributes:
        secret: The shared secret used for HMAC signature
    """

    def __init__(self, secret: str):
        """
        Initialize the HMAC validator.

        Args:
            secret: The shared secret for HMAC signing
        """
        self.secret = secret

    def generate_signature(self, payload: str) -> str:
        """
        Generate an HMAC-SHA256 signature for a payload.

        Args:
            payload: The payload string to sign

        Returns:
            Signature string in format 'sha256=<hex_digest>'
        """
        signature = hmac.new(
            key=self.secret.encode('utf-8'),
            msg=payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        return f"sha256={signature}"

    def validate_signature(self, payload: str, signature: str) -> bool:
        """
        Validate an HMAC-SHA256 signature using constant-time comparison.

        Args:
            payload: The payload string that was signed
            signature: The signature to validate (format: sha256=<hex>)

        Returns:
            True if signature is valid, False otherwise
        """
        # Check signature format
        if not signature.startswith("sha256="):
            return False

        # Generate expected signature
        expected_signature = self.generate_signature(payload)

        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected_signature, signature)

    def validate_with_timestamp(
        self,
        payload: str,
        signature: str,
        timestamp: str,
        max_age_seconds: int = 300
    ) -> bool:
        """
        Validate signature with timestamp check to prevent replay attacks.

        Args:
            payload: The payload string that was signed
            signature: The signature to validate
            timestamp: Unix timestamp when request was sent
            max_age_seconds: Maximum allowed age of request (default: 5 minutes)

        Returns:
            True if signature and timestamp are valid, False otherwise
        """
        # First validate the signature
        if not self.validate_signature(payload, signature):
            return False

        # Check timestamp
        try:
            request_time = int(timestamp)
            current_time = int(time.time())
            age = current_time - request_time

            # Reject if too old or in the future
            if age < 0 or age > max_age_seconds:
                return False

            return True
        except (ValueError, TypeError):
            return False

    def generate_signed_payload(self, payload: str) -> dict:
        """
        Generate a payload with signature and timestamp.

        Args:
            payload: The payload string to sign

        Returns:
            Dictionary with payload, signature, and timestamp
        """
        timestamp = str(int(time.time()))
        signature = self.generate_signature(payload)

        return {
            "payload": payload,
            "signature": signature,
            "timestamp": timestamp
        }


# =============================================================================
# Default Webhook Validator
# =============================================================================

_webhook_validator: Optional[HMACValidator] = None


def get_webhook_validator() -> HMACValidator:
    """
    Get the default webhook validator instance.

    Uses WEBHOOK_SECRET environment variable or a default secret for demo mode.

    Returns:
        HMACValidator configured with webhook secret
    """
    global _webhook_validator

    if _webhook_validator is None:
        # Get secret from environment or use default for demo
        secret = os.getenv(
            "WEBHOOK_SECRET",
            "cyberdemo-default-webhook-secret-change-in-production"
        )
        _webhook_validator = HMACValidator(secret=secret)

    return _webhook_validator


def reset_webhook_validator() -> None:
    """Reset the webhook validator (useful for testing)."""
    global _webhook_validator
    _webhook_validator = None


def set_webhook_secret(secret: str) -> HMACValidator:
    """
    Set a new webhook secret and return the validator.

    Args:
        secret: The new webhook secret

    Returns:
        New HMACValidator with the given secret
    """
    global _webhook_validator
    _webhook_validator = HMACValidator(secret=secret)
    return _webhook_validator
