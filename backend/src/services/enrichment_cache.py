"""
In-memory cache with TTL for enrichment data.

Stores enrichment results keyed by (item_id, source) with configurable
time-to-live. No external dependencies -- uses a plain dict with timestamps.
"""
import logging
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

CacheKey = Tuple[str, str]  # (item_id, source)


class EnrichmentCache:
    """
    Thread-safe in-memory cache with per-entry TTL.

    Each entry is stored as ``{key: (value, expires_at)}`` so lookups
    are O(1) and expiration is checked lazily on access.

    Usage::

        cache = EnrichmentCache(default_ttl_seconds=3600)
        cache.set("CVE-2024-0001", "nvd", {"score": 9.8})
        data = cache.get("CVE-2024-0001", "nvd")
    """

    def __init__(self, default_ttl_seconds: int = 3600) -> None:
        self._default_ttl = timedelta(seconds=default_ttl_seconds)
        self._store: Dict[CacheKey, Tuple[Any, datetime]] = {}
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, item_id: str, source: str) -> Optional[Any]:
        """Return cached value or ``None`` if missing / expired."""
        key = (item_id, source)
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                self._misses += 1
                return None

            value, expires_at = entry
            if datetime.now() >= expires_at:
                # Expired -- evict lazily
                del self._store[key]
                self._misses += 1
                return None

            self._hits += 1
            return value

    def set(
        self,
        item_id: str,
        source: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Store *value* under *(item_id, source)* with optional custom TTL."""
        ttl = timedelta(seconds=ttl_seconds) if ttl_seconds is not None else self._default_ttl
        expires_at = datetime.now() + ttl
        key = (item_id, source)
        with self._lock:
            self._store[key] = (value, expires_at)

    def invalidate(self, item_id: str, source: Optional[str] = None) -> int:
        """
        Remove entries for *item_id*.

        If *source* is given, remove only that specific entry.
        Otherwise remove all sources for the item.

        Returns the number of entries removed.
        """
        removed = 0
        with self._lock:
            if source is not None:
                key = (item_id, source)
                if key in self._store:
                    del self._store[key]
                    removed = 1
            else:
                keys_to_remove = [k for k in self._store if k[0] == item_id]
                for k in keys_to_remove:
                    del self._store[k]
                removed = len(keys_to_remove)
        return removed

    def clear(self) -> None:
        """Drop all entries and reset statistics."""
        with self._lock:
            self._store.clear()
            self._hits = 0
            self._misses = 0

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def hit_rate(self) -> float:
        """Return cache hit rate as a float between 0.0 and 1.0.

        Returns 0.0 when no lookups have been performed yet.
        """
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total

    def cache_size(self) -> int:
        """Return the number of entries currently stored (including expired)."""
        return len(self._store)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _evict_expired(self) -> int:
        """Remove all expired entries. Returns the count of evicted items."""
        now = datetime.now()
        evicted = 0
        with self._lock:
            expired_keys = [k for k, (_, exp) in self._store.items() if now >= exp]
            for k in expired_keys:
                del self._store[k]
                evicted += 1
        return evicted

    def stats(self) -> Dict[str, Any]:
        """Return a snapshot of cache statistics."""
        return {
            "size": self.cache_size(),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self.hit_rate(),
        }
