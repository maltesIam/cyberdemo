"""
API endpoints for enrichment operations.

Provides REST API for:
- Enriching vulnerabilities (CVEs)
- Enriching threat intelligence indicators (IOCs)
- Checking enrichment job status
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.enrichment_service import EnrichmentService
from ..core.database import get_db

router = APIRouter(prefix="/enrichment", tags=["enrichment"])


# Request/Response models
class EnrichVulnerabilitiesRequest(BaseModel):
    """Request to enrich vulnerabilities."""
    cve_ids: Optional[List[str]] = Field(
        default=None,
        description="List of CVE IDs to enrich. If empty, enriches all pending CVEs (limited to 100)."
    )
    sources: Optional[List[str]] = Field(
        default=None,
        description="Sources to use for enrichment. If empty, uses all available sources."
    )
    force_refresh: bool = Field(
        default=False,
        description="If true, bypass cache and fetch fresh data from APIs."
    )


class ThreatIndicator(BaseModel):
    """Threat intelligence indicator."""
    type: str = Field(..., description="Indicator type: 'ip', 'domain', 'url', 'hash'")
    value: str = Field(..., description="Indicator value (e.g., '192.168.1.1', 'evil.com')")


class EnrichThreatsRequest(BaseModel):
    """Request to enrich threat indicators."""
    indicators: Optional[List[ThreatIndicator]] = Field(
        default=None,
        description="List of indicators to enrich. If empty, enriches all pending indicators (limited to 100)."
    )
    sources: Optional[List[str]] = Field(
        default=None,
        description="Sources to use for enrichment."
    )
    force_refresh: bool = Field(default=False)


class EnrichmentJobResponse(BaseModel):
    """Response for enrichment job creation."""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status: pending, running, completed, failed")
    total_items: int = Field(..., description="Total items to enrich")
    estimated_duration_seconds: Optional[int] = Field(
        default=None,
        description="Estimated completion time in seconds"
    )
    successful_sources: int = Field(..., description="Number of sources that succeeded")
    failed_sources: int = Field(..., description="Number of sources that failed")
    sources: Dict[str, Any] = Field(..., description="Per-source status")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Error details")


class EnrichmentStatusResponse(BaseModel):
    """Response for job status query."""
    job_id: str
    status: str
    progress: float = Field(..., ge=0.0, le=1.0, description="Progress (0.0 to 1.0)")
    processed_items: int
    total_items: int
    failed_items: int
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    estimated_completion: Optional[str] = None
    error_message: Optional[str] = None


@router.post("/vulnerabilities", response_model=EnrichmentJobResponse)
async def enrich_vulnerabilities(
    request: EnrichVulnerabilitiesRequest,
    db: AsyncSession = Depends(get_db)
) -> EnrichmentJobResponse:
    """
    Enrich vulnerabilities with data from multiple sources.

    Enriches CVEs with:
    - CVSS scores (NVD)
    - EPSS exploit prediction scores
    - GitHub security advisories
    - Synthetic risk scores and threat actor attribution

    **Limitation:** Maximum 100 CVEs per request to avoid rate limits.

    **Graceful Degradation:** If some sources fail, enrichment continues with available sources.
    """
    service = EnrichmentService()

    try:
        result = await service.enrich_vulnerabilities(
            cve_ids=request.cve_ids,
            sources=request.sources,
            force_refresh=request.force_refresh
        )

        # Estimate duration based on items and sources
        estimated_duration = None
        if result["total_items"] > 0 and request.sources:
            # Rough estimate: 0.5 seconds per item per source
            estimated_duration = int(result["total_items"] * len(request.sources or []) * 0.5)

        return EnrichmentJobResponse(
            job_id=result["job_id"],
            status="completed" if result["successful_sources"] > 0 else "failed",
            total_items=result["total_items"],
            estimated_duration_seconds=estimated_duration,
            successful_sources=result["successful_sources"],
            failed_sources=result["failed_sources"],
            sources=result["sources"],
            errors=result["errors"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")


@router.post("/threats", response_model=EnrichmentJobResponse)
async def enrich_threats(
    request: EnrichThreatsRequest,
    db: AsyncSession = Depends(get_db)
) -> EnrichmentJobResponse:
    """
    Enrich threat intelligence indicators (IOCs).

    Enriches indicators with:
    - IP reputation (AbuseIPDB, GreyNoise)
    - Threat intelligence (AlienVault OTX)
    - Malware analysis (VirusTotal)
    - Synthetic sandbox reports

    **Limitation:** Maximum 100 indicators per request.
    """
    service = EnrichmentService()

    try:
        # Convert Pydantic models to dicts
        indicators_dict = None
        if request.indicators:
            indicators_dict = [ind.model_dump() for ind in request.indicators]

        result = await service.enrich_threats(
            indicators=indicators_dict,
            sources=request.sources,
            force_refresh=request.force_refresh
        )

        return EnrichmentJobResponse(
            job_id=result["job_id"],
            status="pending",  # Threat enrichment returns immediately
            total_items=result["total_items"],
            estimated_duration_seconds=None,
            successful_sources=result.get("successful_sources", 0),
            failed_sources=result.get("failed_sources", 0),
            sources=result.get("sources", {}),
            errors=result.get("errors", [])
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Threat enrichment failed: {str(e)}")


@router.get("/status/{job_id}", response_model=EnrichmentStatusResponse)
async def get_enrichment_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> EnrichmentStatusResponse:
    """
    Get status of an enrichment job.

    Returns:
    - Current status (pending, running, completed, failed)
    - Progress percentage
    - Items processed/failed
    - Timestamps
    - Error details if failed
    """
    service = EnrichmentService()

    try:
        status = await service.get_enrichment_status(job_id)

        # Estimate completion time if running
        estimated_completion = None
        if status["status"] == "running" and status["progress"] > 0:
            # Simple linear extrapolation
            from datetime import datetime, timedelta
            if status["started_at"]:
                started = datetime.fromisoformat(status["started_at"])
                elapsed = (datetime.now() - started).total_seconds()
                if elapsed > 0:
                    total_estimated = elapsed / status["progress"]
                    remaining = total_estimated - elapsed
                    completion = datetime.now() + timedelta(seconds=remaining)
                    estimated_completion = completion.isoformat()

        return EnrichmentStatusResponse(
            job_id=status["job_id"],
            status=status["status"],
            progress=status["progress"],
            processed_items=status["processed_items"],
            total_items=status["total_items"],
            failed_items=status["failed_items"],
            started_at=status["started_at"],
            completed_at=status["completed_at"],
            estimated_completion=estimated_completion,
            error_message=status["error_message"]
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")
