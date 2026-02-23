"""
Rate Limiter for MCP Endpoints.

Implements a sliding window rate limiter that tracks requests per session.
Requirement: TECH-008 - Rate limiting of 100 requests per minute per session.

Features:
- Sliding window algorithm
- Per-session tracking
- Thread-safe implementation
- Configurable limits
"""

import time
from typing import Dict, Optional
import asyncio
from dataclasses import dataclass, field


@dataclass
class SessionRateInfo:
    """Tracks rate limiting info for a single session."""
    requests: list = field(default_factory=list)  # List of timestamps
    window_start: float = 0.0


class RateLimiter:
    """
    Token bucket rate limiter implementation.

    Tracks requests per session using a sliding window algorithm.

    Attributes:
        max_requests: Maximum number of requests allowed per window
        window_seconds: Time window in seconds (default 60 for 1 minute)
    """

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize the rate limiter.

        Args:
            max_requests: Maximum requests per window (default: 100)
            window_seconds: Window duration in seconds (default: 60)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._sessions: Dict[str, SessionRateInfo] = {}
        self._lock = asyncio.Lock()

    async def check_rate_limit(self, session_id: str) -> bool:
        """
        Check if a request should be allowed and record it.

        Args:
            session_id: Unique identifier for the session

        Returns:
            True if the request is allowed, False if rate limited
        """
        async with self._lock:
            current_time = time.time()

            # Initialize session if not exists
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionRateInfo()

            session = self._sessions[session_id]

            # Remove requests outside the current window
            window_start = current_time - self.window_seconds
            session.requests = [
                ts for ts in session.requests
                if ts > window_start
            ]

            # Check if we're at the limit
            if len(session.requests) >= self.max_requests:
                return False

            # Record this request
            session.requests.append(current_time)
            return True

    async def get_remaining_requests(self, session_id: str) -> int:
        """
        Get the number of remaining requests for a session.

        Args:
            session_id: Unique identifier for the session

        Returns:
            Number of requests remaining in the current window
        """
        async with self._lock:
            if session_id not in self._sessions:
                return self.max_requests

            current_time = time.time()
            window_start = current_time - self.window_seconds

            session = self._sessions[session_id]

            # Count requests in current window
            valid_requests = len([
                ts for ts in session.requests
                if ts > window_start
            ])

            return max(0, self.max_requests - valid_requests)

    async def get_reset_time(self, session_id: str) -> Optional[float]:
        """
        Get the time until the rate limit resets.

        Args:
            session_id: Unique identifier for the session

        Returns:
            Seconds until the oldest request expires, or None if no requests
        """
        async with self._lock:
            if session_id not in self._sessions:
                return None

            session = self._sessions[session_id]

            if not session.requests:
                return None

            current_time = time.time()
            window_start = current_time - self.window_seconds

            # Find the oldest valid request
            valid_requests = [ts for ts in session.requests if ts > window_start]

            if not valid_requests:
                return None

            oldest_request = min(valid_requests)
            reset_time = (oldest_request + self.window_seconds) - current_time

            return max(0, reset_time)

    async def clear_session(self, session_id: str) -> None:
        """
        Clear rate limit tracking for a session.

        Args:
            session_id: Unique identifier for the session
        """
        async with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]

    async def get_usage_stats(self, session_id: str) -> Dict:
        """
        Get detailed usage statistics for a session.

        Args:
            session_id: Unique identifier for the session

        Returns:
            Dictionary with usage statistics
        """
        remaining = await self.get_remaining_requests(session_id)
        reset_time = await self.get_reset_time(session_id)

        return {
            "limit": self.max_requests,
            "remaining": remaining,
            "reset_in_seconds": reset_time,
            "window_seconds": self.window_seconds
        }


# =============================================================================
# Default Rate Limiter Instance
# =============================================================================

_default_rate_limiter: Optional[RateLimiter] = None


def get_default_rate_limiter() -> RateLimiter:
    """
    Get the default rate limiter instance.

    Returns:
        RateLimiter configured with 100 requests per minute
    """
    global _default_rate_limiter

    if _default_rate_limiter is None:
        _default_rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

    return _default_rate_limiter


def reset_default_rate_limiter() -> None:
    """Reset the default rate limiter (useful for testing)."""
    global _default_rate_limiter
    _default_rate_limiter = None
