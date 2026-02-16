"""
Circuit Breaker Pattern Implementation.

Prevents hammering of failing external APIs by temporarily blocking calls
after a threshold of failures is reached.

States:
- CLOSED: Normal operation, calls go through
- OPEN: Too many failures, calls are blocked
- HALF_OPEN: Testing recovery, limited calls allowed
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Blocked due to failures
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and blocks a call."""
    pass


class CircuitBreaker:
    """
    Circuit breaker for protecting against failing external services.

    Usage:
        cb = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

        try:
            result = await cb.call(some_async_function, arg1, arg2)
        except CircuitBreakerOpenError:
            # Circuit is open, handle gracefully
            pass
    """

    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of consecutive failures before opening circuit
            timeout_seconds: Time to wait before transitioning from OPEN to HALF_OPEN
        """
        self.failure_threshold = failure_threshold
        self.timeout = timedelta(seconds=timeout_seconds)
        self.failures = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from func

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: If func raises an exception
        """
        # Check if circuit should transition from OPEN to HALF_OPEN
        if self.state == CircuitState.OPEN:
            if self.last_failure_time and datetime.now() - self.last_failure_time > self.timeout:
                logger.info(f"Circuit breaker transitioning to HALF_OPEN after timeout")
                self.state = CircuitState.HALF_OPEN
            else:
                # Circuit is still open, block the call
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN, skipping call. "
                    f"Will retry after {self.timeout.total_seconds()}s timeout."
                )

        # Try to execute the function
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call - reset failures and close circuit."""
        if self.state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker: HALF_OPEN -> CLOSED (success after timeout)")

        self.failures = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        """Handle failed call - increment failures and open circuit if threshold reached."""
        self.failures += 1
        self.last_failure_time = datetime.now()

        if self.failures >= self.failure_threshold:
            if self.state != CircuitState.OPEN:
                logger.warning(
                    f"Circuit breaker OPENED after {self.failures} failures. "
                    f"Will retry after {self.timeout.total_seconds()}s."
                )
                self.state = CircuitState.OPEN

    def reset(self):
        """Manually reset circuit breaker to CLOSED state."""
        self.failures = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        logger.info("Circuit breaker manually reset to CLOSED")
