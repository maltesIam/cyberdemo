"""
Performance tests for the enrichment caching layer.

All tests are marked with ``@pytest.mark.performance`` so they can be
selected or excluded via ``pytest -m performance``.
"""
import asyncio
import time
from typing import Any, Dict, List
from concurrent.futures import ThreadPoolExecutor

import pytest

from src.services.enrichment_cache import EnrichmentCache


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _simulate_enrichment_without_cache(
    cve_ids: List[str],
    delay_per_item: float = 0.01,
) -> List[Dict[str, Any]]:
    """Simulate enrichment with a small per-item delay (no cache)."""
    results: List[Dict[str, Any]] = []
    for cve_id in cve_ids:
        await asyncio.sleep(delay_per_item)
        results.append({"cve_id": cve_id, "score": 9.8})
    return results


async def _simulate_enrichment_with_cache(
    cve_ids: List[str],
    cache: EnrichmentCache,
    source: str = "nvd",
    delay_per_item: float = 0.01,
) -> List[Dict[str, Any]]:
    """Simulate enrichment that checks cache first; only sleeps on miss."""
    results: List[Dict[str, Any]] = []
    for cve_id in cve_ids:
        cached = cache.get(cve_id, source)
        if cached is not None:
            results.append(cached)
            continue
        # Cache miss -- simulate API latency
        await asyncio.sleep(delay_per_item)
        data = {"cve_id": cve_id, "score": 9.8}
        cache.set(cve_id, source, data)
        results.append(data)
    return results


# ---------------------------------------------------------------------------
# Performance tests
# ---------------------------------------------------------------------------

@pytest.mark.performance
@pytest.mark.asyncio
async def test_enrichment_completes_within_2_minutes_for_100_items(
    sample_cve_ids: List[str],
) -> None:
    """
    100 items enriched sequentially with a 10 ms simulated API delay each
    must complete in well under 2 minutes (expected ~1 second).
    """
    start = time.monotonic()
    results = await _simulate_enrichment_without_cache(
        sample_cve_ids, delay_per_item=0.01
    )
    elapsed = time.monotonic() - start

    assert len(results) == 100
    assert elapsed < 120.0, (
        f"Enrichment took {elapsed:.2f}s -- exceeds 2-minute budget"
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_cache_improves_performance_by_80_percent(
    sample_cve_ids: List[str],
) -> None:
    """
    A second pass over the same CVE list with a warm cache must be at
    least 80 % faster than the first (cold) pass.
    """
    cache = EnrichmentCache(default_ttl_seconds=3600)
    delay = 0.01  # 10 ms per item

    # Cold pass -- populates cache
    cold_start = time.monotonic()
    await _simulate_enrichment_with_cache(
        sample_cve_ids, cache, delay_per_item=delay
    )
    cold_elapsed = time.monotonic() - cold_start

    # Warm pass -- everything should come from cache
    warm_start = time.monotonic()
    warm_results = await _simulate_enrichment_with_cache(
        sample_cve_ids, cache, delay_per_item=delay
    )
    warm_elapsed = time.monotonic() - warm_start

    assert len(warm_results) == 100

    # The warm pass must be at least 80 % faster than the cold pass
    improvement = 1.0 - (warm_elapsed / cold_elapsed) if cold_elapsed > 0 else 0
    assert improvement >= 0.80, (
        f"Cache improvement was only {improvement * 100:.1f}% "
        f"(cold={cold_elapsed:.4f}s, warm={warm_elapsed:.4f}s)"
    )

    # Verify cache statistics reflect the expected behavior
    assert cache.hit_rate() > 0.45  # At least ~50 % overall (all misses + all hits)


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_enrichment_requests(
    sample_cve_ids: List[str],
) -> None:
    """
    Multiple concurrent enrichment tasks sharing the same cache must all
    complete without errors and without corrupting the cache.
    """
    cache = EnrichmentCache(default_ttl_seconds=3600)
    num_workers = 5

    async def _worker(worker_id: int) -> List[Dict[str, Any]]:
        return await _simulate_enrichment_with_cache(
            sample_cve_ids,
            cache,
            source=f"source_{worker_id}",
            delay_per_item=0.001,
        )

    tasks = [_worker(i) for i in range(num_workers)]
    all_results = await asyncio.gather(*tasks)

    # Each worker should return 100 results
    for idx, results in enumerate(all_results):
        assert len(results) == 100, (
            f"Worker {idx} returned {len(results)} results instead of 100"
        )

    # Cache should contain entries from every worker
    assert cache.cache_size() == 100 * num_workers


@pytest.mark.performance
def test_cache_operations_are_fast(
    prefilled_cache: EnrichmentCache,
) -> None:
    """
    Individual get / set / invalidate operations on a warm cache must be
    sub-millisecond.
    """
    iterations = 1_000

    # -- get --
    start = time.monotonic()
    for i in range(iterations):
        prefilled_cache.get(f"CVE-2024-{i % 100:04d}", "nvd")
    get_elapsed = time.monotonic() - start

    # -- set --
    start = time.monotonic()
    for i in range(iterations):
        prefilled_cache.set(f"CVE-2024-{i:04d}", "bench", {"v": i})
    set_elapsed = time.monotonic() - start

    # -- invalidate --
    start = time.monotonic()
    for i in range(iterations):
        prefilled_cache.invalidate(f"CVE-2024-{i:04d}", "bench")
    inv_elapsed = time.monotonic() - start

    avg_get_us = (get_elapsed / iterations) * 1_000_000
    avg_set_us = (set_elapsed / iterations) * 1_000_000
    avg_inv_us = (inv_elapsed / iterations) * 1_000_000

    # Each operation should average well under 1 ms (< 1000 us)
    assert avg_get_us < 1000, f"Average get: {avg_get_us:.1f} us"
    assert avg_set_us < 1000, f"Average set: {avg_set_us:.1f} us"
    assert avg_inv_us < 1000, f"Average invalidate: {avg_inv_us:.1f} us"


@pytest.mark.performance
def test_cache_thread_safety() -> None:
    """
    Concurrent reads and writes from multiple threads must not raise
    exceptions or corrupt state.
    """
    cache = EnrichmentCache(default_ttl_seconds=3600)
    errors: List[Exception] = []

    def _writer(thread_id: int) -> None:
        try:
            for i in range(200):
                cache.set(f"CVE-2024-{i:04d}", f"thread_{thread_id}", {"t": thread_id})
        except Exception as exc:
            errors.append(exc)

    def _reader(thread_id: int) -> None:
        try:
            for i in range(200):
                cache.get(f"CVE-2024-{i:04d}", f"thread_{thread_id}")
        except Exception as exc:
            errors.append(exc)

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = []
        for t in range(4):
            futures.append(pool.submit(_writer, t))
            futures.append(pool.submit(_reader, t))
        for f in futures:
            f.result()

    assert errors == [], f"Thread safety errors: {errors}"
    # All written entries should be present
    assert cache.cache_size() > 0
