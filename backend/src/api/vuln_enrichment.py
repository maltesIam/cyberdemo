"""
API endpoints for Vulnerability Enrichment operations.

Provides REST API for:
- POST /api/enrichment/vulnerabilities - Start enrichment job
- GET /api/enrichment/vulnerabilities/status/{job_id} - Job status
- GET /api/vulnerabilities/enriched - List enriched CVEs (paginated, filters)
- GET /api/vulnerabilities/enriched/{cve_id} - Full CVE detail
- GET /api/vulnerabilities/enriched/{cve_id}/assets - Affected assets
- GET /api/vulnerabilities/enriched/{cve_id}/exploits - Known exploits
- GET /api/vulnerabilities/enriched/{cve_id}/chain - Attack chain
- POST /api/vulnerabilities/enriched/{cve_id}/enrich - Trigger enrichment
"""
import hashlib
import random
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..services.vuln_enrichment_service import VulnerabilityEnrichmentService


# ============================================================================
# Pydantic Models
# ============================================================================


class EnrichVulnerabilitiesRequest(BaseModel):
    """Request to start vulnerability enrichment job."""
    cve_ids: Optional[List[str]] = Field(
        default=None,
        description="List of CVE IDs to enrich. If empty, enriches pending CVEs."
    )
    sources: Optional[List[str]] = Field(
        default=None,
        description="Sources to use: nvd, epss, kev, osv, ghsa, exploitdb"
    )
    force_refresh: bool = Field(
        default=False,
        description="If true, bypass cache and fetch fresh data."
    )


class EnrichmentJobResponse(BaseModel):
    """Response for enrichment job creation."""
    job_id: str
    status: str
    total_items: int
    successful_sources: int
    failed_sources: int
    sources: Dict[str, Any]
    errors: List[Dict[str, Any]] = []


class EnrichmentStatusResponse(BaseModel):
    """Response for job status query."""
    job_id: str
    status: str
    progress: float = Field(..., ge=0.0, le=1.0)
    processed_items: int
    total_items: int
    failed_items: int
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class EnrichedCVEListResponse(BaseModel):
    """Response for listing enriched CVEs."""
    data: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int = 0


class AffectedAssetsResponse(BaseModel):
    """Response for affected assets list."""
    assets: List[Dict[str, Any]]
    total: int
    page: int = 1
    page_size: int = 50


class ExploitsResponse(BaseModel):
    """Response for known exploits list."""
    exploits: List[Dict[str, Any]]
    total: int


class AttackChainResponse(BaseModel):
    """Response for attack chain data."""
    cve_id: str
    mitre_techniques: List[Dict[str, Any]] = []
    mitre_tactics: List[Dict[str, Any]] = []
    typical_actors: List[str] = []
    threat_actors: List[Dict[str, Any]] = []
    malware_families: List[str] = []
    campaigns: List[str] = []
    kill_chain_phases: List[str] = []


class TriggerEnrichmentRequest(BaseModel):
    """Request to trigger single CVE enrichment."""
    sources: Optional[List[str]] = Field(
        default=None,
        description="Sources to use for enrichment."
    )


# ============================================================================
# Router Definition
# ============================================================================


router = APIRouter(tags=["vulnerability-enrichment"])


# ============================================================================
# Synthetic Data Generation (for demo purposes)
# ============================================================================


def _generate_synthetic_enriched_cve(cve_id: str) -> Dict[str, Any]:
    """Generate synthetic enriched CVE data for demo purposes."""
    # Use hash for deterministic but varied results
    seed = int(hashlib.md5(cve_id.encode()).hexdigest()[:8], 16)
    random.seed(seed)

    cvss_score = round(random.uniform(4.0, 10.0), 1)
    epss_score = round(random.uniform(0.1, 0.99), 2)
    is_kev = random.random() > 0.7

    severities = ["Low", "Medium", "High", "Critical"]
    if cvss_score >= 9.0:
        severity = "Critical"
    elif cvss_score >= 7.0:
        severity = "High"
    elif cvss_score >= 4.0:
        severity = "Medium"
    else:
        severity = "Low"

    ssvc_decisions = ["Act", "Attend", "Track*", "Track"]
    if is_kev:
        ssvc_decision = "Act"
    elif epss_score >= 0.5 and cvss_score >= 7.0:
        ssvc_decision = "Attend"
    elif epss_score >= 0.1 or cvss_score >= 4.0:
        ssvc_decision = "Track*"
    else:
        ssvc_decision = "Track"

    # Calculate risk score (0-100)
    risk_score = 0
    if is_kev:
        risk_score += 30
    risk_score += int(epss_score * 30)
    risk_score += int((cvss_score / 10) * 40)
    risk_score = min(risk_score, 100)

    cwe_options = [
        ("CWE-79", "Cross-site Scripting"),
        ("CWE-89", "SQL Injection"),
        ("CWE-94", "Improper Control of Generation of Code"),
        ("CWE-200", "Information Exposure"),
        ("CWE-502", "Deserialization of Untrusted Data"),
        ("CWE-787", "Out-of-bounds Write"),
    ]
    selected_cwe = random.choice(cwe_options)

    return {
        "cve_id": cve_id,
        "title": f"Security vulnerability in {random.choice(['Apache', 'Microsoft', 'Linux', 'OpenSSL', 'Log4j'])} component",
        "description": f"A vulnerability exists that could allow remote code execution or unauthorized access.",
        "published_date": "2024-01-01T00:00:00",
        "last_modified_date": datetime.now().isoformat(),
        "cvss_v3_score": cvss_score,
        "cvss_v3_vector": f"CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "cvss_v2_score": round(cvss_score * 0.8, 1),
        "epss_score": epss_score,
        "epss_percentile": round(random.uniform(0.5, 0.99), 2),
        "risk_score": risk_score,
        "severity": severity,
        "cwe_ids": [selected_cwe[0]],
        "cwe_names": [selected_cwe[1]],
        "cpe_uris": [f"cpe:2.3:a:vendor:product:*:*:*:*:*:*:*:*"],
        "is_kev": is_kev,
        "kev_date_added": "2024-01-02" if is_kev else None,
        "kev_due_date": "2024-01-16" if is_kev else None,
        "kev_required_action": "Apply vendor patches" if is_kev else None,
        "kev_ransomware_use": is_kev and random.random() > 0.5,
        "exploit_count": random.randint(0, 10),
        "exploit_maturity": random.choice(["weaponized", "poc", "unproven", "none"]),
        "has_nuclei_template": random.random() > 0.6,
        "ssvc_decision": ssvc_decision,
        "affected_asset_count": random.randint(1, 100),
        "affected_critical_assets": random.randint(0, 20),
        "patch_available": random.random() > 0.3,
        "enrichment_level": "full",
        "enrichment_sources": ["nvd", "epss", "kev", "exploitdb"],
        "last_enriched_at": datetime.now().isoformat(),
    }


def _generate_synthetic_assets(cve_id: str, count: int = 10) -> List[Dict[str, Any]]:
    """Generate synthetic affected assets."""
    seed = int(hashlib.md5(cve_id.encode()).hexdigest()[:8], 16)
    random.seed(seed)

    assets = []
    asset_types = ["server", "database", "application", "workstation", "network"]
    criticalities = ["critical", "high", "medium", "low"]
    departments = ["Engineering", "Operations", "Finance", "HR", "Marketing"]

    for i in range(count):
        assets.append({
            "asset_id": f"ASSET-{random.randint(100, 999)}",
            "hostname": f"{random.choice(['web', 'app', 'db', 'api'])}-server-{i+1:02d}",
            "ip": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
            "asset_type": random.choice(asset_types),
            "criticality": random.choice(criticalities),
            "department": random.choice(departments),
            "installed_version": f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            "patched": random.random() > 0.7,
            "last_scanned": datetime.now().isoformat(),
        })

    return assets


def _generate_synthetic_exploits(cve_id: str) -> List[Dict[str, Any]]:
    """Generate synthetic exploit data."""
    seed = int(hashlib.md5(cve_id.encode()).hexdigest()[:8], 16)
    random.seed(seed)

    exploits = []
    sources = ["exploitdb", "metasploit", "github_poc", "nuclei"]
    types = ["remote", "local", "webapps", "dos"]
    platforms = ["linux", "windows", "multi", "any"]

    count = random.randint(0, 5)
    for i in range(count):
        source = random.choice(sources)
        exploits.append({
            "source": source,
            "exploit_id": f"{source.upper()}-{random.randint(10000, 99999)}",
            "title": f"Exploit for {cve_id}",
            "type": random.choice(types),
            "platform": random.choice(platforms),
            "verified": random.random() > 0.3,
            "url": f"https://example.com/exploits/{random.randint(1000, 9999)}",
            "date_published": "2024-01-10",
        })

    return exploits


def _generate_synthetic_attack_chain(cve_id: str) -> Dict[str, Any]:
    """Generate synthetic attack chain data."""
    seed = int(hashlib.md5(cve_id.encode()).hexdigest()[:8], 16)
    random.seed(seed)

    techniques = [
        {"id": "T1190", "name": "Exploit Public-Facing Application"},
        {"id": "T1059.004", "name": "Unix Shell"},
        {"id": "T1105", "name": "Ingress Tool Transfer"},
        {"id": "T1071", "name": "Application Layer Protocol"},
    ]

    tactics = [
        {"id": "TA0001", "name": "Initial Access"},
        {"id": "TA0002", "name": "Execution"},
        {"id": "TA0003", "name": "Persistence"},
        {"id": "TA0011", "name": "Command and Control"},
    ]

    actors = [
        {
            "name": "APT29",
            "aliases": ["Cozy Bear", "The Dukes"],
            "country": "Russia",
            "motivation": "espionage",
            "sophistication": "advanced",
        },
        {
            "name": "Lazarus Group",
            "aliases": ["Hidden Cobra", "Guardians of Peace"],
            "country": "North Korea",
            "motivation": "financial",
            "sophistication": "advanced",
        },
    ]

    return {
        "cve_id": cve_id,
        "mitre_techniques": random.sample(techniques, min(len(techniques), random.randint(1, 3))),
        "mitre_tactics": random.sample(tactics, min(len(tactics), random.randint(1, 3))),
        "typical_actors": ["APT29", "Lazarus Group"],
        "threat_actors": random.sample(actors, min(len(actors), random.randint(1, 2))),
        "malware_families": random.sample(["Cobalt Strike", "Mimikatz", "PowerShell Empire", "Metasploit"], 2),
        "campaigns": [f"{cve_id} Exploitation Campaign"],
        "kill_chain_phases": ["reconnaissance", "weaponization", "delivery", "exploitation"],
    }


def _is_known_cve(cve_id: str) -> bool:
    """Check if a CVE ID follows valid format (for demo, we accept most CVE patterns)."""
    # For demo purposes, accept any CVE that doesn't end with 9999-0000
    return not cve_id.endswith("9999-0000")


# ============================================================================
# Enrichment Job Endpoints
# ============================================================================


@router.post("/enrichment/vulnerabilities", response_model=EnrichmentJobResponse)
async def start_vulnerability_enrichment(
    request: EnrichVulnerabilitiesRequest
) -> EnrichmentJobResponse:
    """
    Start a vulnerability enrichment job.

    Enriches CVEs with data from multiple sources:
    - NVD: CVSS scores, CWE, CPE
    - EPSS: Exploit prediction scores
    - KEV: CISA Known Exploited Vulnerabilities
    - OSV: Open Source Vulnerabilities
    - ExploitDB: Exploit information

    **Limitation:** Maximum 100 CVEs per request.
    """
    service = VulnerabilityEnrichmentService()

    try:
        result = await service.enrich_vulnerabilities(
            cve_ids=request.cve_ids,
            sources=request.sources,
            force_refresh=request.force_refresh
        )

        return EnrichmentJobResponse(
            job_id=result["job_id"],
            status="completed" if result["successful_sources"] > 0 else "failed",
            total_items=result["total_items"],
            successful_sources=result["successful_sources"],
            failed_sources=result["failed_sources"],
            sources=result["sources"],
            errors=result["errors"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")


@router.get("/enrichment/vulnerabilities/status/{job_id}", response_model=EnrichmentStatusResponse)
async def get_vulnerability_enrichment_status(job_id: str) -> EnrichmentStatusResponse:
    """
    Get status of a vulnerability enrichment job.

    Returns progress, timestamps, and error details if failed.
    """
    service = VulnerabilityEnrichmentService()

    try:
        status = await service.get_enrichment_status(job_id)

        return EnrichmentStatusResponse(
            job_id=status["job_id"],
            status=status["status"],
            progress=status["progress"],
            processed_items=status["processed_items"],
            total_items=status["total_items"],
            failed_items=status["failed_items"],
            started_at=status.get("started_at"),
            completed_at=status.get("completed_at"),
            error_message=status.get("error_message")
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


# ============================================================================
# Enriched CVE Endpoints
# ============================================================================


@router.get("/vulnerabilities/enriched", response_model=EnrichedCVEListResponse)
async def list_enriched_cves(
    severity: Optional[str] = Query(None, description="Filter by severity: Critical, High, Medium, Low"),
    cvss_min: Optional[float] = Query(None, ge=0.0, le=10.0, description="Minimum CVSS score"),
    cvss_max: Optional[float] = Query(None, ge=0.0, le=10.0, description="Maximum CVSS score"),
    is_kev: Optional[bool] = Query(None, description="Filter by KEV status"),
    ssvc_decision: Optional[str] = Query(None, description="Filter by SSVC decision: Act, Attend, Track*, Track"),
    search: Optional[str] = Query(None, description="Search in CVE ID or title"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
) -> EnrichedCVEListResponse:
    """
    List enriched CVEs with pagination and filters.

    Returns CVEs that have been enriched with vulnerability intelligence
    from multiple sources (NVD, EPSS, KEV, etc.).
    """
    # Generate synthetic demo data
    sample_cves = [
        "CVE-2024-1234",
        "CVE-2024-5678",
        "CVE-2024-9012",
        "CVE-2023-44487",
        "CVE-2021-44228",
        "CVE-2021-45046",
        "CVE-2022-22965",
        "CVE-2023-27350",
        "CVE-2024-3400",
        "CVE-2024-21762",
    ]

    enriched_cves = [_generate_synthetic_enriched_cve(cve_id) for cve_id in sample_cves]

    # Apply filters
    if severity:
        enriched_cves = [cve for cve in enriched_cves if cve["severity"] == severity]
    if cvss_min is not None:
        enriched_cves = [cve for cve in enriched_cves if cve["cvss_v3_score"] >= cvss_min]
    if cvss_max is not None:
        enriched_cves = [cve for cve in enriched_cves if cve["cvss_v3_score"] <= cvss_max]
    if is_kev is not None:
        enriched_cves = [cve for cve in enriched_cves if cve["is_kev"] == is_kev]
    if ssvc_decision:
        enriched_cves = [cve for cve in enriched_cves if cve["ssvc_decision"] == ssvc_decision]
    if search:
        search_lower = search.lower()
        enriched_cves = [
            cve for cve in enriched_cves
            if search_lower in cve["cve_id"].lower() or search_lower in cve["title"].lower()
        ]

    total = len(enriched_cves)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    # Apply pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated = enriched_cves[start:end]

    return EnrichedCVEListResponse(
        data=paginated,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/vulnerabilities/enriched/{cve_id}")
async def get_enriched_cve_detail(cve_id: str) -> Dict[str, Any]:
    """
    Get full enriched CVE detail.

    Returns comprehensive vulnerability information including:
    - Core data (title, description, dates)
    - Scoring (CVSS, EPSS, risk score)
    - KEV status and details
    - Exploit information
    - SSVC decision
    - Asset impact summary
    - Enrichment metadata
    """
    if not _is_known_cve(cve_id):
        raise HTTPException(status_code=404, detail=f"CVE {cve_id} not found")

    return _generate_synthetic_enriched_cve(cve_id)


@router.get("/vulnerabilities/enriched/{cve_id}/assets", response_model=AffectedAssetsResponse)
async def get_affected_assets(
    cve_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> AffectedAssetsResponse:
    """
    Get assets affected by a specific CVE.

    Returns list of affected assets with:
    - Asset identification (ID, hostname, IP)
    - Asset type and criticality
    - Department ownership
    - Patch status
    - Last scan timestamp
    """
    if not _is_known_cve(cve_id):
        raise HTTPException(status_code=404, detail=f"CVE {cve_id} not found")

    # Generate more assets than page_size to simulate pagination
    all_assets = _generate_synthetic_assets(cve_id, count=25)
    total = len(all_assets)

    # Apply pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated = all_assets[start:end]

    return AffectedAssetsResponse(
        assets=paginated,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/vulnerabilities/enriched/{cve_id}/exploits", response_model=ExploitsResponse)
async def get_known_exploits(cve_id: str) -> ExploitsResponse:
    """
    Get known exploits for a specific CVE.

    Returns list of exploits from:
    - ExploitDB
    - Metasploit
    - GitHub PoCs
    - Nuclei templates
    """
    if not _is_known_cve(cve_id):
        raise HTTPException(status_code=404, detail=f"CVE {cve_id} not found")

    exploits = _generate_synthetic_exploits(cve_id)

    return ExploitsResponse(
        exploits=exploits,
        total=len(exploits)
    )


@router.get("/vulnerabilities/enriched/{cve_id}/chain", response_model=AttackChainResponse)
async def get_attack_chain(cve_id: str) -> AttackChainResponse:
    """
    Get attack chain information for a CVE.

    Returns MITRE ATT&CK mapping and threat intelligence:
    - ATT&CK techniques and tactics
    - Known threat actors
    - Malware families
    - Campaigns
    - Kill chain phases
    """
    if not _is_known_cve(cve_id):
        raise HTTPException(status_code=404, detail=f"CVE {cve_id} not found")

    chain_data = _generate_synthetic_attack_chain(cve_id)

    return AttackChainResponse(**chain_data)


@router.post("/vulnerabilities/enriched/{cve_id}/enrich")
async def trigger_single_cve_enrichment(
    cve_id: str,
    request: Optional[TriggerEnrichmentRequest] = None
) -> Dict[str, Any]:
    """
    Trigger enrichment for a single CVE.

    Forces a fresh enrichment with the latest data from all sources.
    Returns the enriched CVE data.
    """
    service = VulnerabilityEnrichmentService()

    try:
        sources = request.sources if request else None
        result = await service.enrich_single_cve(cve_id, sources=sources)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")
