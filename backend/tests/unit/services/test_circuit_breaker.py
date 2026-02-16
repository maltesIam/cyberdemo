"""
Unit tests for CircuitBreaker.

Following TDD: Tests for circuit breaker state machine.

Circuit Breaker Pattern:
- CLOSED: Normal operation, calls go through
- OPEN: Too many failures, calls are blocked
- HALF_OPEN: Testing recovery, limited calls allowed
"""
import pytest
import asyncio
from datetime import datetime, timedelta

from src.services.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerOpenError
)


class TestCircuitBreakerStates:
    """Tests for circuit breaker state transitions."""

    def test_initial_state_is_closed(self):
        """Circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker(failure_threshold=5, timeout_seconds=60)
        assert cb.state == CircuitState.CLOSED
        assert cb.failures == 0
        assert cb.last_failure_time is None

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_5_failures(self):
        """Circuit opens after reaching failure_threshold (5) consecutive failures."""
        cb = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

        async def failing_func():
            raise Exception("API Error")

        # Initial state
        assert cb.state == CircuitState.CLOSED

        # Fail 5 times
        for i in range(5):
            with pytest.raises(Exception, match="API Error"):
                await cb.call(failing_func)
            assert cb.failures == i + 1

        # Circuit should now be OPEN
        assert cb.state == CircuitState.OPEN
        assert cb.failures == 5
        assert cb.last_failure_time is not None

        # 6th call should be blocked immediately
        with pytest.raises(CircuitBreakerOpenError) as exc_info:
            await cb.call(failing_func)
        assert "OPEN" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_after_timeout(self):
        """Circuit transitions to HALF_OPEN after timeout expires."""
        # Use very short timeout for testing
        cb = CircuitBreaker(failure_threshold=5, timeout_seconds=0.1)

        async def failing_func():
            raise Exception("API Error")

        async def success_func():
            return "success"

        # Open the circuit
        for _ in range(5):
            with pytest.raises(Exception):
                await cb.call(failing_func)

        assert cb.state == CircuitState.OPEN

        # Wait for timeout to expire
        await asyncio.sleep(0.15)

        # Next call should transition to HALF_OPEN and succeed
        result = await cb.call(success_func)
        assert result == "success"
        # Success in HALF_OPEN should close the circuit
        assert cb.state == CircuitState.CLOSED
        assert cb.failures == 0

    @pytest.mark.asyncio
    async def test_circuit_breaker_closes_on_success(self):
        """Circuit closes (resets) when a call succeeds."""
        cb = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

        async def failing_func():
            raise Exception("API Error")

        async def success_func():
            return "success"

        # Fail 3 times (not enough to open)
        for _ in range(3):
            with pytest.raises(Exception):
                await cb.call(failing_func)

        assert cb.failures == 3
        assert cb.state == CircuitState.CLOSED

        # Success should reset failures
        result = await cb.call(success_func)
        assert result == "success"
        assert cb.failures == 0
        assert cb.state == CircuitState.CLOSED


class TestCircuitBreakerFailureCounting:
    """Tests for failure counting behavior."""

    @pytest.mark.asyncio
    async def test_failure_count_increments(self):
        """Each failure increments the failure counter."""
        cb = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

        async def failing_func():
            raise ValueError("Test error")

        for expected_count in range(1, 4):
            with pytest.raises(ValueError):
                await cb.call(failing_func)
            assert cb.failures == expected_count

    @pytest.mark.asyncio
    async def test_success_resets_failure_count(self):
        """A successful call resets the failure counter."""
        cb = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

        async def failing_func():
            raise Exception("Error")

        async def success_func():
            return "ok"

        # Build up some failures
        for _ in range(3):
            with pytest.raises(Exception):
                await cb.call(failing_func)

        assert cb.failures == 3

        # Success resets
        await cb.call(success_func)
        assert cb.failures == 0

    @pytest.mark.asyncio
    async def test_failure_records_timestamp(self):
        """Failures record the last failure timestamp."""
        cb = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

        async def failing_func():
            raise Exception("Error")

        before = datetime.now()
        with pytest.raises(Exception):
            await cb.call(failing_func)
        after = datetime.now()

        assert cb.last_failure_time is not None
        assert before <= cb.last_failure_time <= after


class TestCircuitBreakerBlocking:
    """Tests for call blocking when circuit is open."""

    @pytest.mark.asyncio
    async def test_open_circuit_blocks_calls(self):
        """When OPEN, calls are blocked without executing the function."""
        cb = CircuitBreaker(failure_threshold=2, timeout_seconds=60)
        call_count = 0

        async def failing_func():
            nonlocal call_count
            call_count += 1
            raise Exception("Error")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await cb.call(failing_func)

        assert cb.state == CircuitState.OPEN
        assert call_count == 2

        # Next calls should be blocked (not executed)
        for _ in range(3):
            with pytest.raises(CircuitBreakerOpenError):
                await cb.call(failing_func)

        # Function was not called while circuit was open
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_blocked_call_mentions_timeout(self):
        """Blocked calls indicate when retry is possible."""
        cb = CircuitBreaker(failure_threshold=2, timeout_seconds=60)

        async def failing_func():
            raise Exception("Error")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await cb.call(failing_func)

        # Check error message
        with pytest.raises(CircuitBreakerOpenError) as exc_info:
            await cb.call(failing_func)

        error_msg = str(exc_info.value)
        assert "timeout" in error_msg.lower() or "60" in error_msg


class TestCircuitBreakerReset:
    """Tests for manual reset functionality."""

    def test_manual_reset_closes_circuit(self):
        """Calling reset() closes the circuit and clears state."""
        cb = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

        # Simulate open state
        cb.failures = 5
        cb.state = CircuitState.OPEN
        cb.last_failure_time = datetime.now()

        # Reset
        cb.reset()

        assert cb.state == CircuitState.CLOSED
        assert cb.failures == 0
        assert cb.last_failure_time is None

    @pytest.mark.asyncio
    async def test_reset_allows_calls_after_open(self):
        """After reset, calls go through normally."""
        cb = CircuitBreaker(failure_threshold=2, timeout_seconds=60)

        async def failing_func():
            raise Exception("Error")

        async def success_func():
            return "success"

        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await cb.call(failing_func)

        assert cb.state == CircuitState.OPEN

        # Reset
        cb.reset()

        # Now calls should work
        result = await cb.call(success_func)
        assert result == "success"


class TestCircuitBreakerConfiguration:
    """Tests for circuit breaker configuration."""

    @pytest.mark.asyncio
    async def test_custom_failure_threshold(self):
        """Circuit opens after custom threshold."""
        cb = CircuitBreaker(failure_threshold=3, timeout_seconds=60)

        async def failing_func():
            raise Exception("Error")

        # Should remain closed after 2 failures
        for _ in range(2):
            with pytest.raises(Exception):
                await cb.call(failing_func)
        assert cb.state == CircuitState.CLOSED

        # Should open after 3rd failure
        with pytest.raises(Exception):
            await cb.call(failing_func)
        assert cb.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_custom_timeout(self):
        """Circuit respects custom timeout duration."""
        cb = CircuitBreaker(failure_threshold=2, timeout_seconds=0.05)  # 50ms

        async def failing_func():
            raise Exception("Error")

        async def success_func():
            return "ok"

        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await cb.call(failing_func)

        assert cb.state == CircuitState.OPEN

        # Wait less than timeout - should still be blocked
        await asyncio.sleep(0.02)
        with pytest.raises(CircuitBreakerOpenError):
            await cb.call(success_func)

        # Wait for timeout to expire
        await asyncio.sleep(0.05)

        # Now should work
        result = await cb.call(success_func)
        assert result == "ok"


class TestCircuitBreakerHalfOpen:
    """Tests for HALF_OPEN state behavior."""

    @pytest.mark.asyncio
    async def test_half_open_success_closes_circuit(self):
        """Success in HALF_OPEN state closes the circuit."""
        cb = CircuitBreaker(failure_threshold=2, timeout_seconds=0.05)

        async def failing_func():
            raise Exception("Error")

        async def success_func():
            return "success"

        # Open circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await cb.call(failing_func)

        assert cb.state == CircuitState.OPEN

        # Wait for timeout
        await asyncio.sleep(0.1)

        # Success should close circuit
        result = await cb.call(success_func)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert cb.failures == 0

    @pytest.mark.asyncio
    async def test_half_open_failure_reopens_circuit(self):
        """Failure in HALF_OPEN state reopens the circuit."""
        cb = CircuitBreaker(failure_threshold=2, timeout_seconds=0.05)

        async def failing_func():
            raise Exception("Error")

        # Open circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await cb.call(failing_func)

        assert cb.state == CircuitState.OPEN

        # Wait for timeout
        await asyncio.sleep(0.1)

        # Failure in half-open should re-open
        with pytest.raises(Exception):
            await cb.call(failing_func)

        # Circuit should be open again
        assert cb.state == CircuitState.OPEN


class TestCircuitBreakerAsync:
    """Tests for async function handling."""

    @pytest.mark.asyncio
    async def test_async_function_success(self):
        """Circuit breaker works with async functions that succeed."""
        cb = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

        async def async_func():
            await asyncio.sleep(0.01)
            return "async result"

        result = await cb.call(async_func)
        assert result == "async result"
        assert cb.failures == 0

    @pytest.mark.asyncio
    async def test_async_function_with_args(self):
        """Circuit breaker passes arguments to async functions."""
        cb = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

        async def async_func_with_args(a, b, c=None):
            return f"{a}-{b}-{c}"

        result = await cb.call(async_func_with_args, "x", "y", c="z")
        assert result == "x-y-z"

    @pytest.mark.asyncio
    async def test_different_exception_types(self):
        """Circuit breaker counts all exception types as failures."""
        cb = CircuitBreaker(failure_threshold=3, timeout_seconds=60)
        failures = 0

        async def raise_various():
            nonlocal failures
            failures += 1
            if failures == 1:
                raise ValueError("Value error")
            elif failures == 2:
                raise RuntimeError("Runtime error")
            else:
                raise Exception("Generic error")

        # All exception types count as failures
        with pytest.raises(ValueError):
            await cb.call(raise_various)
        assert cb.failures == 1

        with pytest.raises(RuntimeError):
            await cb.call(raise_various)
        assert cb.failures == 2

        with pytest.raises(Exception):
            await cb.call(raise_various)
        assert cb.failures == 3
        assert cb.state == CircuitState.OPEN
