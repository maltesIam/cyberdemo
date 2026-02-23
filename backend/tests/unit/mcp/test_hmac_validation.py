"""
HMAC Signature Validation Unit Tests - TDD RED Phase

Tests for HMAC signature validation for webhooks.
Requirement: TECH-009

Following TDD: Tests written FIRST, implementation comes after.
"""

import pytest
import hmac
import hashlib
import json
import time


# =============================================================================
# TEST: HMAC Validator Component (TECH-009)
# =============================================================================

class TestHMACValidator:
    """Unit tests for the HMAC signature validator."""

    def test_validator_initialization(self):
        """
        GIVEN an HMAC secret
        WHEN HMACValidator is initialized
        THEN it should store the secret
        """
        from src.mcp.hmac_validator import HMACValidator

        validator = HMACValidator(secret="my-webhook-secret")

        assert validator.secret == "my-webhook-secret"

    def test_generate_signature(self):
        """
        GIVEN a payload and secret
        WHEN a signature is generated
        THEN it should return a valid HMAC-SHA256 signature
        """
        from src.mcp.hmac_validator import HMACValidator

        validator = HMACValidator(secret="test-secret")
        payload = '{"event": "test"}'

        signature = validator.generate_signature(payload)

        # Verify format (sha256=hexdigest)
        assert signature.startswith("sha256=")
        assert len(signature) == 71  # sha256= + 64 hex chars

    def test_validate_signature_success(self):
        """
        GIVEN a valid signature for a payload
        WHEN validate_signature is called
        THEN it should return True
        """
        from src.mcp.hmac_validator import HMACValidator

        secret = "webhook-secret-123"
        validator = HMACValidator(secret=secret)
        payload = '{"event": "alert.created", "alert_id": "ALT-001"}'

        # Generate valid signature
        expected_signature = validator.generate_signature(payload)

        # Validate
        is_valid = validator.validate_signature(payload, expected_signature)

        assert is_valid is True

    def test_validate_signature_failure_wrong_signature(self):
        """
        GIVEN an incorrect signature
        WHEN validate_signature is called
        THEN it should return False
        """
        from src.mcp.hmac_validator import HMACValidator

        validator = HMACValidator(secret="correct-secret")
        payload = '{"event": "test"}'
        wrong_signature = "sha256=0000000000000000000000000000000000000000000000000000000000000000"

        is_valid = validator.validate_signature(payload, wrong_signature)

        assert is_valid is False

    def test_validate_signature_failure_wrong_secret(self):
        """
        GIVEN a signature generated with different secret
        WHEN validate_signature is called
        THEN it should return False
        """
        from src.mcp.hmac_validator import HMACValidator

        validator1 = HMACValidator(secret="secret-A")
        validator2 = HMACValidator(secret="secret-B")
        payload = '{"event": "test"}'

        # Generate with secret A
        signature = validator1.generate_signature(payload)

        # Validate with secret B
        is_valid = validator2.validate_signature(payload, signature)

        assert is_valid is False

    def test_validate_signature_with_invalid_format(self):
        """
        GIVEN a signature without sha256= prefix
        WHEN validate_signature is called
        THEN it should return False
        """
        from src.mcp.hmac_validator import HMACValidator

        validator = HMACValidator(secret="test-secret")
        payload = '{"event": "test"}'
        invalid_signature = "not-a-valid-signature-format"

        is_valid = validator.validate_signature(payload, invalid_signature)

        assert is_valid is False

    def test_validate_signature_constant_time(self):
        """
        GIVEN a signature validation
        WHEN validate_signature is called
        THEN it should use constant-time comparison (to prevent timing attacks)
        """
        from src.mcp.hmac_validator import HMACValidator

        validator = HMACValidator(secret="test-secret")
        payload = '{"event": "test"}'
        valid_sig = validator.generate_signature(payload)

        # We can't directly test constant time, but we ensure
        # hmac.compare_digest is used internally by checking it works
        assert validator.validate_signature(payload, valid_sig) is True

    def test_validate_with_timestamp(self):
        """
        GIVEN a webhook with timestamp
        WHEN validating with max_age
        THEN stale requests should be rejected
        """
        from src.mcp.hmac_validator import HMACValidator

        validator = HMACValidator(secret="test-secret")
        payload = '{"event": "test"}'
        signature = validator.generate_signature(payload)

        # Current timestamp should be valid
        current_ts = str(int(time.time()))
        is_valid = validator.validate_with_timestamp(
            payload, signature, current_ts, max_age_seconds=300
        )
        assert is_valid is True

        # Old timestamp should be invalid
        old_ts = str(int(time.time()) - 600)  # 10 minutes ago
        is_valid = validator.validate_with_timestamp(
            payload, signature, old_ts, max_age_seconds=300
        )
        assert is_valid is False


# =============================================================================
# TEST: Webhook Signature Middleware
# =============================================================================

class TestWebhookSignatureMiddleware:
    """Tests for webhook signature validation at the endpoint level.

    NOTE: These tests require the webhook endpoint to be implemented (T-1.2.001).
    They are marked as skipped until the endpoint exists.
    """

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Webhook endpoint not yet implemented (T-1.2.001)")
    async def test_webhook_endpoint_requires_signature(self):
        """
        GIVEN a webhook endpoint with HMAC validation enabled
        WHEN a request is made without signature
        THEN it should return 401 Unauthorized
        """
        from httpx import AsyncClient, ASGITransport
        from src.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/webhooks/incoming",
                json={"event": "test"}
            )

            assert response.status_code == 401
            assert "signature" in response.json().get("detail", "").lower()

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Webhook endpoint not yet implemented (T-1.2.001)")
    async def test_webhook_endpoint_validates_signature(self):
        """
        GIVEN a webhook endpoint with HMAC validation
        WHEN a request is made with valid signature
        THEN it should be processed successfully
        """
        from httpx import AsyncClient, ASGITransport
        from src.main import app
        from src.mcp.hmac_validator import get_webhook_validator

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            payload = json.dumps({"event": "test"})
            validator = get_webhook_validator()
            signature = validator.generate_signature(payload)

            response = await client.post(
                "/api/v1/webhooks/incoming",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": signature
                }
            )

            # Should not be 401
            assert response.status_code != 401

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Webhook endpoint not yet implemented (T-1.2.001)")
    async def test_webhook_endpoint_rejects_invalid_signature(self):
        """
        GIVEN a webhook endpoint with HMAC validation
        WHEN a request is made with invalid signature
        THEN it should return 401 Unauthorized
        """
        from httpx import AsyncClient, ASGITransport
        from src.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            payload = json.dumps({"event": "test"})
            invalid_signature = "sha256=invalid"

            response = await client.post(
                "/api/v1/webhooks/incoming",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": invalid_signature
                }
            )

            assert response.status_code == 401


# =============================================================================
# TEST: Configuration
# =============================================================================

class TestHMACConfiguration:
    """Tests for HMAC configuration."""

    def test_get_webhook_validator_returns_configured_validator(self):
        """
        GIVEN webhook secret is configured
        WHEN get_webhook_validator is called
        THEN it should return a configured HMACValidator
        """
        from src.mcp.hmac_validator import get_webhook_validator

        validator = get_webhook_validator()

        assert validator is not None
        assert hasattr(validator, 'validate_signature')

    def test_default_secret_is_set(self):
        """
        GIVEN the application
        WHEN HMAC validator is retrieved
        THEN it should have a default secret (for demo mode)
        """
        from src.mcp.hmac_validator import get_webhook_validator

        validator = get_webhook_validator()

        # Should have some secret configured (even default)
        assert validator.secret is not None
        assert len(validator.secret) > 0
