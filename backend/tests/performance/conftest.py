"""
Fixtures for enrichment performance tests.
"""
import pytest
from typing import Dict, Any, List

from src.services.enrichment_cache import EnrichmentCache


@pytest.fixture
def empty_cache() -> EnrichmentCache:
    """Return a fresh cache with 1-hour default TTL."""
    return EnrichmentCache(default_ttl_seconds=3600)


@pytest.fixture
def short_ttl_cache() -> EnrichmentCache:
    """Return a cache with a very short TTL (useful for expiration tests)."""
    return EnrichmentCache(default_ttl_seconds=1)


@pytest.fixture
def sample_cve_ids() -> List[str]:
    """Generate 100 sample CVE IDs."""
    return [f"CVE-2024-{i:04d}" for i in range(100)]


@pytest.fixture
def sample_enrichment_data() -> Dict[str, Any]:
    """Return a representative enrichment result for a single CVE."""
    return {
        "cve_id": "CVE-2024-0001",
        "cvss_score": 9.8,
        "epss_score": 0.75,
        "severity": "CRITICAL",
        "description": "Sample vulnerability description for testing",
        "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-0001"],
    }


@pytest.fixture
def prefilled_cache(
    empty_cache: EnrichmentCache,
    sample_cve_ids: List[str],
    sample_enrichment_data: Dict[str, Any],
) -> EnrichmentCache:
    """Return a cache pre-populated with 100 CVE entries across two sources."""
    for cve_id in sample_cve_ids:
        data = {**sample_enrichment_data, "cve_id": cve_id}
        empty_cache.set(cve_id, "nvd", data)
        empty_cache.set(cve_id, "epss", {"cve_id": cve_id, "epss_score": 0.5})
    return empty_cache
