"""
Vulnerability Enrichment Service.

Main orchestrator for enriching CVEs with data from multiple sources:
- NVD: CVSS scores, CWE, CPE (existing client)
- EPSS: Exploit prediction scores (existing client)
- KEV: Known Exploited Vulnerabilities (existing client)
- OSV: Open Source Vulnerabilities (existing client)
- GHSA: GitHub Security Advisories (synthetic if not ready)
- ExploitDB: Exploit information (synthetic if not ready)

Key constraints:
- MAX_ITEMS_PER_SOURCE = 100 (never process more than 100 CVEs at once)
- CircuitBreaker for each API source
- Never fail entire enrichment if one source fails
- Support force_refresh to bypass cache
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from .circuit_breaker import CircuitBreaker, CircuitBreakerOpenError

# Module-level imports for clients (tests patch these names)
from ..clients.nvd_client import NVDClient
from ..clients.epss_client import EPSSClient
from ..clients.kev_client import KEVClient
from ..clients.osv_client import OSVClient

logger = logging.getLogger(__name__)

# CRITICAL: Limit to 100 items per source to avoid rate limits and timeouts
MAX_ITEMS_PER_SOURCE = 100

# Default sources for vulnerability enrichment
DEFAULT_SOURCES = ['nvd', 'epss', 'kev']


async def get_db():
    """Get a database session async context manager.

    Tests patch this function at 'src.services.vuln_enrichment_service.get_db'.
    """
    from ..core.database import async_session_maker
    return async_session_maker()


class VulnerabilityEnrichmentService:
    """
    Service for enriching CVE vulnerabilities with data from multiple sources.

    Handles:
    - Limiting to MAX_ITEMS_PER_SOURCE (100)
    - Graceful degradation when sources fail
    - Circuit breaker for failing APIs
    - Caching API responses
    - Job tracking and status updates
    - SSVC decision calculation
    - Risk score calculation
    """

    MAX_ITEMS_PER_SOURCE = MAX_ITEMS_PER_SOURCE

    def __init__(self):
        """Initialize enrichment service with circuit breakers for each source."""
        # Circuit breakers for each source
        self.circuit_breakers: Dict[str, CircuitBreaker] = {
            'nvd': CircuitBreaker(failure_threshold=5, timeout_seconds=60),
            'epss': CircuitBreaker(failure_threshold=5, timeout_seconds=60),
            'kev': CircuitBreaker(failure_threshold=5, timeout_seconds=60),
            'osv': CircuitBreaker(failure_threshold=5, timeout_seconds=60),
            'ghsa': CircuitBreaker(failure_threshold=5, timeout_seconds=60),
            'exploitdb': CircuitBreaker(failure_threshold=5, timeout_seconds=60),
        }

        # In-memory job store for tracking without database
        self._jobs: Dict[str, Dict[str, Any]] = {}

        # In-memory cache (simple key-value store)
        self._cache: Dict[str, Dict[str, Any]] = {}

    async def enrich_vulnerabilities(
        self,
        cve_ids: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Main enrichment method.

        Args:
            cve_ids: List of CVE IDs to enrich. If None, get pending CVEs from DB.
            sources: List of sources to use. If None, use default sources.
            force_refresh: If True, bypass cache and fetch fresh data.

        Returns:
            {
                "job_id": "uuid",
                "total_items": int,
                "successful_sources": int,
                "failed_sources": int,
                "sources": {
                    "nvd": {"status": "success", "enriched_count": 50},
                    "epss": {"status": "success", "enriched_count": 50},
                    "kev": {"status": "failed", "error": "timeout"}
                },
                "errors": [
                    {"source": "kev", "error": "timeout", "recoverable": True}
                ],
                "enriched_cves": [...]  # List of EnrichedCVE objects
            }
        """
        # If no CVE IDs provided, get pending from database
        if cve_ids is None:
            cve_ids = await self._get_pending_cves(limit=MAX_ITEMS_PER_SOURCE)

        # CRITICAL: Limit to MAX_ITEMS_PER_SOURCE
        if len(cve_ids) > MAX_ITEMS_PER_SOURCE:
            logger.warning(
                f"Limiting CVE enrichment from {len(cve_ids)} to {MAX_ITEMS_PER_SOURCE} items"
            )
            cve_ids = cve_ids[:MAX_ITEMS_PER_SOURCE]

        # Default sources
        if not sources:
            sources = DEFAULT_SOURCES.copy()

        # Create enrichment job
        job_id = await self._create_job(
            job_type='vulnerability',
            total_items=len(cve_ids),
            job_metadata={'sources': sources, 'force_refresh': force_refresh}
        )

        results: Dict[str, Any] = {
            "job_id": str(job_id),
            "total_items": len(cve_ids),
            "enriched_cves": [],
            "sources": {},
            "errors": [],
            "successful_sources": 0,
            "failed_sources": 0,
        }

        # Collect enrichment data from each source
        enrichment_data: Dict[str, Dict[str, Any]] = {}  # source -> {cve_id -> data}

        # Enrich from each source independently (graceful degradation)
        for source in sources:
            try:
                # Check cache first (unless force_refresh)
                if not force_refresh:
                    cached = self._get_from_cache(source, cve_ids)
                    if cached:
                        results["sources"][source] = {
                            "status": "success",
                            "enriched_count": cached.get("count", 0),
                            "failed_count": cached.get("failed", 0),
                        }
                        results["successful_sources"] += 1
                        enrichment_data[source] = cached.get("data", {})
                        continue

                enriched = await self._enrich_from_source(
                    source=source,
                    cve_ids=cve_ids,
                    force_refresh=force_refresh
                )

                results["sources"][source] = {
                    "status": "success",
                    "enriched_count": enriched.get("count", 0),
                    "failed_count": enriched.get("failed", 0)
                }
                results["successful_sources"] += 1

                enrichment_data[source] = enriched.get("data", {})

            except CircuitBreakerOpenError as e:
                logger.warning(f"Source {source} circuit breaker is open: {str(e)}")
                results["sources"][source] = {
                    "status": "failed",
                    "error": "Circuit breaker open - too many recent failures",
                    "enriched_count": 0
                }
                results["failed_sources"] += 1
                results["errors"].append({
                    "source": source,
                    "error": str(e),
                    "recoverable": True
                })

            except Exception as e:
                logger.error(f"Source {source} failed: {str(e)}", exc_info=True)
                results["sources"][source] = {
                    "status": "failed",
                    "error": str(e),
                    "enriched_count": 0
                }
                results["failed_sources"] += 1
                results["errors"].append({
                    "source": source,
                    "error": str(e),
                    "recoverable": True
                })

        # Merge enrichment data for each CVE
        for cve_id in cve_ids:
            cve_enrichments = {
                source: data.get(cve_id, {})
                for source, data in enrichment_data.items()
                if data.get(cve_id)
            }

            merged = self._merge_enrichments(cve_id, cve_enrichments)
            results["enriched_cves"].append(merged)

        # Update job status
        final_status = "completed" if results["successful_sources"] > 0 else "failed"
        await self._update_job(
            job_id=job_id,
            status=final_status,
            processed_items=len(results["enriched_cves"]),
            failed_items=len(cve_ids) - len(results["enriched_cves"])
        )

        return results

    async def enrich_single_cve(
        self,
        cve_id: str,
        sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Enrich a single CVE with full detail.

        Args:
            cve_id: The CVE ID to enrich
            sources: List of sources to use. If None, use all available.

        Returns:
            Complete enrichment data for the CVE.
        """
        result = await self.enrich_vulnerabilities(
            cve_ids=[cve_id],
            sources=sources,
            force_refresh=True  # Always get fresh data for single CVE
        )

        if result.get("enriched_cves"):
            return result["enriched_cves"][0]

        return {
            "cve_id": cve_id,
            "enriched_at": datetime.now().isoformat(),
            "enrichment_sources": [],
            "error": "No enrichment data available"
        }

    async def _enrich_from_source(
        self,
        source: str,
        cve_ids: List[str],
        force_refresh: bool
    ) -> Dict[str, Any]:
        """
        Enrich from a specific source with circuit breaker protection.

        Args:
            source: Source name (nvd, epss, kev, etc.)
            cve_ids: CVE IDs to enrich
            force_refresh: Skip cache if True

        Returns:
            {"count": int, "failed": int, "data": {cve_id: {...}}}
        """
        circuit_breaker = self.circuit_breakers.get(source)
        if not circuit_breaker:
            raise ValueError(f"Unknown source: {source}")

        async def _do_enrich():
            if source == 'nvd':
                client = NVDClient()
                try:
                    data = await client.fetch_cves(cve_ids)
                    processed = [cve_id for cve_id, d in data.items() if d is not None]
                    return {
                        "count": len(processed),
                        "failed": len(cve_ids) - len(processed),
                        "data": data,
                    }
                finally:
                    await client.close()

            elif source == 'epss':
                client = EPSSClient()
                try:
                    data = await client.fetch_scores(cve_ids)
                    processed = [cve_id for cve_id, d in data.items() if d is not None]
                    return {
                        "count": len(processed),
                        "failed": len(cve_ids) - len(processed),
                        "data": data,
                    }
                finally:
                    await client.close()

            elif source == 'kev':
                client = KEVClient()
                try:
                    data = await client.get_kev_for_cves(cve_ids)
                    # Count how many are in KEV
                    kev_count = sum(1 for d in data.values() if d is not None)
                    return {
                        "count": len(cve_ids),  # All checked
                        "failed": 0,
                        "data": data,
                    }
                finally:
                    await client.close()

            elif source == 'osv':
                client = OSVClient()
                try:
                    data = {}
                    for cve_id in cve_ids:
                        osv_data = await client.query_by_cve(cve_id)
                        if osv_data:
                            data[cve_id] = osv_data
                    return {
                        "count": len(data),
                        "failed": len(cve_ids) - len(data),
                        "data": data,
                    }
                finally:
                    await client.close()

            elif source in ['ghsa', 'exploitdb']:
                # Synthetic data for sources not yet ready
                return self._generate_synthetic_vuln_data(source, cve_ids)

            else:
                # Default: treat as successful pass-through with synthetic data
                return self._generate_synthetic_vuln_data(source, cve_ids)

        return await circuit_breaker.call(_do_enrich)

    async def _get_pending_cves(self, limit: int) -> List[str]:
        """
        Get CVEs that need enrichment from DB.

        Args:
            limit: Maximum number of CVEs to return

        Returns:
            List of CVE IDs that need enrichment
        """
        try:
            session_ctx = await get_db()
            async with session_ctx as session:
                from sqlalchemy import select, text
                # Query for CVEs that haven't been enriched recently
                result = await session.execute(
                    text("""
                        SELECT cve_id FROM vulnerability_enrichment
                        WHERE enriched_at IS NULL OR enriched_at < NOW() - INTERVAL '7 days'
                        LIMIT :limit
                    """),
                    {"limit": limit}
                )
                rows = result.fetchall()
                return [row[0] for row in rows]
        except Exception as e:
            logger.debug(f"Database unavailable for pending CVEs: {e}")
            return []

    def _merge_enrichments(self, cve_id: str, enrichments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge enrichment data from multiple sources.

        Args:
            cve_id: The CVE ID
            enrichments: Dict of {source: data}

        Returns:
            Merged enrichment data
        """
        merged = {
            "cve_id": cve_id,
            "enriched_at": datetime.now().isoformat(),
            "enrichment_sources": list(enrichments.keys()),
        }

        # Merge NVD data
        nvd_data = enrichments.get("nvd", {})
        if nvd_data:
            merged["cvss_v3_score"] = nvd_data.get("cvss_v3_score")
            merged["cvss_v3_vector"] = nvd_data.get("cvss_v3_vector")
            merged["cvss_v2_score"] = nvd_data.get("cvss_v2_score")
            merged["cwe_ids"] = nvd_data.get("cwe_ids", [])
            merged["cpe_uris"] = nvd_data.get("cpe_uris", [])
            merged["description"] = nvd_data.get("description", "")

        # Merge EPSS data
        epss_data = enrichments.get("epss", {})
        if epss_data:
            merged["epss_score"] = epss_data.get("epss_score")
            merged["epss_percentile"] = epss_data.get("epss_percentile")

        # Merge KEV data
        kev_data = enrichments.get("kev", {})
        if kev_data:
            merged["is_kev"] = kev_data.get("is_kev", False)
            merged["kev_date_added"] = kev_data.get("date_added")
            merged["ransomware_use"] = kev_data.get("ransomware_use", False)
        else:
            merged["is_kev"] = False

        # Merge OSV data
        osv_data = enrichments.get("osv", {})
        if osv_data:
            if isinstance(osv_data, list):
                merged["osv_data"] = osv_data
                # Extract affected packages
                affected_packages = []
                for osv_entry in osv_data:
                    for affected in osv_entry.get("affected", []):
                        pkg = affected.get("package", {})
                        if pkg:
                            affected_packages.append({
                                "ecosystem": pkg.get("ecosystem"),
                                "name": pkg.get("name"),
                            })
                merged["affected_packages"] = affected_packages
            else:
                merged["osv_data"] = osv_data

        # Calculate SSVC decision
        merged["ssvc_decision"] = self._calculate_ssvc_decision(
            is_kev=merged.get("is_kev", False),
            epss_score=merged.get("epss_score", 0.0),
            cvss_score=merged.get("cvss_v3_score", 0.0)
        )

        # Calculate risk score
        merged["risk_score"] = self._calculate_risk_score(
            is_kev=merged.get("is_kev", False),
            epss_score=merged.get("epss_score", 0.0),
            cvss_score=merged.get("cvss_v3_score", 0.0)
        )

        return merged

    def _calculate_ssvc_decision(
        self,
        is_kev: bool,
        epss_score: float,
        cvss_score: float
    ) -> str:
        """
        Calculate SSVC (Stakeholder-Specific Vulnerability Categorization) decision.

        SSVC decisions:
        - immediate: Patch immediately (high exploit, high impact)
        - out-of-cycle: Patch soon (moderate exploit/impact)
        - scheduled: Patch in normal cycle (low exploit/impact)
        - defer: Monitor only (minimal risk)

        Args:
            is_kev: Is this CVE in CISA KEV catalog
            epss_score: EPSS exploit prediction score (0.0-1.0)
            cvss_score: CVSS v3 base score (0.0-10.0)

        Returns:
            SSVC decision string
        """
        epss_score = epss_score or 0.0
        cvss_score = cvss_score or 0.0

        # KEV = active exploitation = immediate
        if is_kev:
            return "immediate"

        # High EPSS + High CVSS = out-of-cycle
        if epss_score >= 0.5 and cvss_score >= 7.0:
            return "out-of-cycle"

        # High EPSS or High CVSS = out-of-cycle
        if epss_score >= 0.7 or cvss_score >= 9.0:
            return "out-of-cycle"

        # Moderate EPSS + Moderate CVSS = scheduled
        if epss_score >= 0.1 or cvss_score >= 4.0:
            return "scheduled"

        # Low risk = defer
        return "defer"

    def _calculate_risk_score(
        self,
        is_kev: bool,
        epss_score: float,
        cvss_score: float
    ) -> int:
        """
        Calculate combined risk score (0-100).

        Weights:
        - KEV status: 30 points if in KEV
        - EPSS score: 30 points max (scaled from 0-1)
        - CVSS score: 40 points max (scaled from 0-10)

        Args:
            is_kev: Is this CVE in CISA KEV catalog
            epss_score: EPSS exploit prediction score (0.0-1.0)
            cvss_score: CVSS v3 base score (0.0-10.0)

        Returns:
            Risk score 0-100
        """
        epss_score = epss_score or 0.0
        cvss_score = cvss_score or 0.0

        score = 0

        # KEV status: 30 points
        if is_kev:
            score += 30

        # EPSS score: 30 points max
        score += int(epss_score * 30)

        # CVSS score: 40 points max (scaled from 0-10)
        score += int((cvss_score / 10) * 40)

        return min(score, 100)

    def _generate_synthetic_vuln_data(
        self,
        source: str,
        cve_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Generate synthetic vulnerability data for sources not yet ready.

        Args:
            source: Source name
            cve_ids: List of CVE IDs

        Returns:
            {"count": int, "failed": int, "data": {cve_id: {...}}}
        """
        import random
        import hashlib

        data = {}
        for cve_id in cve_ids:
            # Use hash for deterministic but varied results
            seed = int(hashlib.md5(f"{source}{cve_id}".encode()).hexdigest()[:8], 16)
            random.seed(seed)

            if source == 'ghsa':
                data[cve_id] = {
                    "ghsa_id": f"GHSA-{random.choice('abcdef0123456789')}{random.choice('abcdef0123456789')}{random.choice('abcdef0123456789')}{random.choice('abcdef0123456789')}-{cve_id[-4:]}",
                    "severity": random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
                    "published_at": datetime.now().isoformat(),
                }
            elif source == 'exploitdb':
                data[cve_id] = {
                    "exploit_available": random.random() > 0.7,
                    "exploit_count": random.randint(0, 5),
                    "exploit_type": random.choice(["local", "remote", "webapps", "dos"]),
                }
            else:
                data[cve_id] = {
                    "source": source,
                    "synthetic": True,
                }

        return {
            "count": len(data),
            "failed": 0,
            "data": data,
        }

    def _get_from_cache(
        self,
        source: str,
        cve_ids: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Get enrichment data from cache if available.

        Returns None by default (no cache hit). Tests may patch this method.
        """
        cache_key = f"{source}:{','.join(sorted(cve_ids))}"
        cached = self._cache.get(cache_key)
        if cached:
            # Check if cache is still valid (1 hour TTL)
            cached_at = cached.get("cached_at")
            if cached_at:
                cache_age = (datetime.now() - datetime.fromisoformat(cached_at)).total_seconds()
                if cache_age < 3600:  # 1 hour
                    return cached
        return None

    def _set_cache(
        self,
        source: str,
        cve_ids: List[str],
        data: Dict[str, Any]
    ):
        """Set enrichment data in cache."""
        cache_key = f"{source}:{','.join(sorted(cve_ids))}"
        self._cache[cache_key] = {
            **data,
            "cached_at": datetime.now().isoformat(),
        }

    async def _create_job(
        self,
        job_type: str,
        total_items: int,
        job_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create an enrichment job record in memory and optionally in database."""
        job_id = str(uuid.uuid4())

        # Store in memory
        self._jobs[job_id] = {
            "id": job_id,
            "type": job_type,
            "status": "pending",
            "total_items": total_items,
            "processed_items": 0,
            "failed_items": 0,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "error_message": None,
            "job_metadata": job_metadata,
        }

        # Persist to database if available
        try:
            session_ctx = await get_db()
            async with session_ctx as session:
                from ..models.enrichment import EnrichmentJob
                job = EnrichmentJob(
                    id=uuid.UUID(job_id),
                    type=job_type,
                    status="pending",
                    total_items=total_items,
                    job_metadata=job_metadata,
                )
                session.add(job)
                await session.commit()
        except Exception:
            logger.debug("Database unavailable for job creation, using in-memory tracking")

        return job_id

    async def _update_job(
        self,
        job_id: str,
        status: str,
        processed_items: int,
        failed_items: int = 0,
        error_message: Optional[str] = None
    ):
        """Update an enrichment job in memory and optionally in database."""
        # Update in-memory record
        if job_id in self._jobs:
            self._jobs[job_id]["status"] = status
            self._jobs[job_id]["processed_items"] = processed_items
            self._jobs[job_id]["failed_items"] = failed_items
            if error_message:
                self._jobs[job_id]["error_message"] = error_message
            if status in ["completed", "failed"]:
                self._jobs[job_id]["completed_at"] = datetime.now().isoformat()

        # Persist to database if available
        try:
            session_ctx = await get_db()
            async with session_ctx as session:
                from sqlalchemy import select
                from ..models.enrichment import EnrichmentJob
                result = await session.execute(
                    select(EnrichmentJob).where(EnrichmentJob.id == uuid.UUID(job_id))
                )
                job = result.scalar_one_or_none()
                if job:
                    job.status = status
                    job.processed_items = processed_items
                    job.failed_items = failed_items
                    if error_message:
                        job.error_message = error_message
                    if status in ["completed", "failed"]:
                        job.completed_at = datetime.now()
                    await session.commit()
        except Exception:
            logger.debug("Database unavailable for job update, using in-memory tracking")

    async def get_enrichment_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get status of an enrichment job.

        Args:
            job_id: UUID of the job

        Returns:
            Job status information
        """
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        progress = 0.0
        if job["total_items"] > 0:
            progress = job["processed_items"] / job["total_items"]

        return {
            "job_id": job_id,
            "status": job["status"],
            "progress": progress,
            "processed_items": job["processed_items"],
            "total_items": job["total_items"],
            "failed_items": job.get("failed_items", 0),
            "started_at": job.get("started_at"),
            "completed_at": job.get("completed_at"),
            "error_message": job.get("error_message"),
        }
