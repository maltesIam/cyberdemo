"""
SSVC and Classification API endpoints for vulnerability management.

Endpoints:
- GET /ssvc/summary - Distribution of SSVC decisions
- GET /ssvc/tree - Decision tree data for visualization
- GET /cwes - List CWEs with stats
- GET /cwes/{cwe_id} - CWE detail with CVE list
- GET /packages - Vulnerable packages with CVE count
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional


router = APIRouter(tags=["Vulnerabilities SSVC"])


# ============================================================================
# Response Models
# ============================================================================


class SSVCSummaryResponse(BaseModel):
    """Response model for SSVC summary endpoint."""
    decisions: dict = {}
    total: int = 0
    act_percentage: float = 0.0
    critical_requires_action: int = 0


class SSVCTreeNode(BaseModel):
    """Node in the SSVC decision tree."""
    name: str
    count: int = 0
    children: list = []
    decision: Optional[str] = None


class SSVCTreeResponse(BaseModel):
    """Response model for SSVC tree endpoint."""
    name: str = "SSVC Decision Tree"
    children: list = []


class CWEItem(BaseModel):
    """CWE item with statistics."""
    cwe_id: str
    name: str = ""
    cve_count: int = 0
    critical_count: int = 0
    high_count: int = 0


class CWEListResponse(BaseModel):
    """Response model for CWEs list endpoint."""
    cwes: list[CWEItem] = []
    total: int = 0


class CWEDetailResponse(BaseModel):
    """Response model for CWE detail endpoint."""
    cwe_id: str
    name: str = ""
    description: str = ""
    cves: list[str] = []
    severity_breakdown: dict = {}


class PackageItem(BaseModel):
    """Vulnerable package item."""
    ecosystem: str
    name: str
    cve_count: int = 0
    critical_count: int = 0


class PackageListResponse(BaseModel):
    """Response model for packages endpoint."""
    packages: list[PackageItem] = []
    total: int = 0


# ============================================================================
# CWE Name Mapping (static data for common CWEs)
# ============================================================================

CWE_NAMES = {
    "CWE-79": "Cross-site Scripting (XSS)",
    "CWE-89": "SQL Injection",
    "CWE-78": "OS Command Injection",
    "CWE-22": "Path Traversal",
    "CWE-94": "Code Injection",
    "CWE-287": "Improper Authentication",
    "CWE-306": "Missing Authentication",
    "CWE-502": "Deserialization of Untrusted Data",
    "CWE-434": "Unrestricted Upload of File",
    "CWE-918": "Server-Side Request Forgery (SSRF)",
    "CWE-352": "Cross-Site Request Forgery (CSRF)",
    "CWE-119": "Buffer Overflow",
    "CWE-20": "Improper Input Validation",
    "CWE-200": "Exposure of Sensitive Information",
    "CWE-611": "XXE",
}

CWE_DESCRIPTIONS = {
    "CWE-79": "The software does not neutralize or incorrectly neutralizes user-controllable input before it is placed in output that is used as a web page that is served to other users.",
    "CWE-89": "The software constructs all or part of an SQL command using externally-influenced input, but it does not neutralize special elements that could modify the intended SQL command.",
    "CWE-78": "The software constructs all or part of an OS command using externally-influenced input, but it does not neutralize special elements that could modify the intended OS command.",
    "CWE-22": "The software uses external input to construct a pathname that should be within a restricted directory, but it does not properly neutralize sequences that can resolve to a location that is outside of that directory.",
}


# ============================================================================
# SSVC Endpoints
# ============================================================================


@router.get("/ssvc/summary", response_model=SSVCSummaryResponse)
async def get_ssvc_summary():
    """
    Get distribution of SSVC decisions.

    Returns counts for each SSVC decision type (Act, Attend, Track*, Track),
    total count, act percentage, and count of critical vulnerabilities requiring action.
    """
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="ctem-findings-v1",
            body={
                "size": 0,
                "aggs": {
                    "ssvc_decisions": {
                        "terms": {"field": "ssvc_decision.keyword", "size": 10}
                    },
                    "critical_requires_action": {
                        "filter": {
                            "bool": {
                                "must": [
                                    {"term": {"severity": "Critical"}},
                                    {"term": {"ssvc_decision.keyword": "Act"}}
                                ]
                            }
                        }
                    }
                }
            }
        )

        aggs = response.get("aggregations", {})

        # Parse decision counts
        decisions = {}
        for bucket in aggs.get("ssvc_decisions", {}).get("buckets", []):
            decisions[bucket["key"]] = bucket["doc_count"]

        # Calculate total and percentage
        total = sum(decisions.values())
        act_count = decisions.get("Act", 0)
        act_percentage = round((act_count / total * 100), 1) if total > 0 else 0.0

        # Get critical requires action count
        critical_requires_action = aggs.get("critical_requires_action", {}).get("doc_count", 0)

        return SSVCSummaryResponse(
            decisions=decisions,
            total=total,
            act_percentage=act_percentage,
            critical_requires_action=critical_requires_action
        )

    except Exception:
        return SSVCSummaryResponse(
            decisions={},
            total=0,
            act_percentage=0.0,
            critical_requires_action=0
        )


@router.get("/ssvc/tree", response_model=SSVCTreeResponse)
async def get_ssvc_tree():
    """
    Get SSVC decision tree data for visualization.

    Returns hierarchical tree structure grouped by:
    - Exploitation status (active, poc, none)
    - For active: automatable (true/false)
    - For poc: technical impact (total/partial)
    """
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="ctem-findings-v1",
            body={
                "size": 0,
                "aggs": {
                    "exploitation_status": {
                        "terms": {"field": "ssvc_exploitation.keyword", "size": 10},
                        "aggs": {
                            "automatable": {
                                "terms": {"field": "ssvc_automatable", "size": 5}
                            },
                            "technical_impact": {
                                "terms": {"field": "ssvc_technical_impact.keyword", "size": 5}
                            }
                        }
                    }
                }
            }
        )

        aggs = response.get("aggregations", {})
        children = []

        for bucket in aggs.get("exploitation_status", {}).get("buckets", []):
            exploitation = bucket["key"]
            count = bucket["doc_count"]

            node = {
                "name": f"Exploitation: {exploitation}",
                "count": count,
                "children": []
            }

            if exploitation == "active":
                # For active exploitation, group by automatable
                for auto_bucket in bucket.get("automatable", {}).get("buckets", []):
                    auto_value = auto_bucket.get("key_as_string", str(auto_bucket["key"]))
                    auto_count = auto_bucket["doc_count"]
                    decision = "Act" if auto_value in ["true", "1", True] else "Attend"
                    node["children"].append({
                        "name": f"Automatable: {auto_value}",
                        "count": auto_count,
                        "decision": decision
                    })

            elif exploitation == "poc":
                # For POC, group by technical impact
                for impact_bucket in bucket.get("technical_impact", {}).get("buckets", []):
                    impact = impact_bucket["key"]
                    impact_count = impact_bucket["doc_count"]
                    decision = "Attend" if impact == "total" else "Track*"
                    node["children"].append({
                        "name": f"Impact: {impact}",
                        "count": impact_count,
                        "decision": decision
                    })

            else:
                # For none, decision is Track
                node["decision"] = "Track"

            children.append(node)

        return SSVCTreeResponse(
            name="SSVC Decision Tree",
            children=children
        )

    except Exception:
        return SSVCTreeResponse(
            name="SSVC Decision Tree",
            children=[]
        )


# ============================================================================
# Classification Endpoints
# ============================================================================


@router.get("/cwes", response_model=CWEListResponse)
async def get_cwes_list():
    """
    Get list of CWEs with statistics.

    Returns unique CWEs with CVE count and severity breakdown.
    """
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="ctem-findings-v1",
            body={
                "size": 0,
                "aggs": {
                    "cwes": {
                        "terms": {"field": "cwe_id.keyword", "size": 100},
                        "aggs": {
                            "severity_breakdown": {
                                "terms": {"field": "severity", "size": 5}
                            }
                        }
                    }
                }
            }
        )

        aggs = response.get("aggregations", {})
        cwes = []

        for bucket in aggs.get("cwes", {}).get("buckets", []):
            cwe_id = bucket["key"]
            cve_count = bucket["doc_count"]

            # Parse severity breakdown
            severity_counts = {}
            for sev_bucket in bucket.get("severity_breakdown", {}).get("buckets", []):
                severity_counts[sev_bucket["key"]] = sev_bucket["doc_count"]

            cwes.append(CWEItem(
                cwe_id=cwe_id,
                name=CWE_NAMES.get(cwe_id, "Unknown"),
                cve_count=cve_count,
                critical_count=severity_counts.get("Critical", 0),
                high_count=severity_counts.get("High", 0)
            ))

        return CWEListResponse(
            cwes=cwes,
            total=len(cwes)
        )

    except Exception:
        return CWEListResponse(cwes=[], total=0)


@router.get("/cwes/{cwe_id}", response_model=CWEDetailResponse)
async def get_cwe_detail(cwe_id: str):
    """
    Get detail for a specific CWE.

    Returns CWE metadata, list of affected CVEs, and severity breakdown.
    """
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="ctem-findings-v1",
            body={
                "query": {"term": {"cwe_id.keyword": cwe_id}},
                "size": 100,
                "_source": ["cve_id", "severity"],
                "aggs": {
                    "severity_breakdown": {
                        "terms": {"field": "severity", "size": 5}
                    }
                }
            }
        )

        total = response.get("hits", {}).get("total", {}).get("value", 0)

        if total == 0:
            raise HTTPException(status_code=404, detail=f"CWE {cwe_id} not found")

        # Extract CVE IDs
        cves = list(set(
            hit["_source"]["cve_id"]
            for hit in response.get("hits", {}).get("hits", [])
            if "cve_id" in hit.get("_source", {})
        ))

        # Parse severity breakdown
        severity_breakdown = {}
        for bucket in response.get("aggregations", {}).get("severity_breakdown", {}).get("buckets", []):
            severity_breakdown[bucket["key"]] = bucket["doc_count"]

        return CWEDetailResponse(
            cwe_id=cwe_id,
            name=CWE_NAMES.get(cwe_id, "Unknown"),
            description=CWE_DESCRIPTIONS.get(cwe_id, "No description available."),
            cves=cves,
            severity_breakdown=severity_breakdown
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/packages", response_model=PackageListResponse)
async def get_packages_list():
    """
    Get list of vulnerable packages.

    Returns packages with CVE count and critical count.
    """
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="ctem-findings-v1",
            body={
                "size": 0,
                "aggs": {
                    "packages": {
                        "terms": {"field": "package.keyword", "size": 100},
                        "aggs": {
                            "critical_count": {
                                "filter": {"term": {"severity": "Critical"}}
                            }
                        }
                    }
                }
            }
        )

        aggs = response.get("aggregations", {})
        packages = []

        for bucket in aggs.get("packages", {}).get("buckets", []):
            package_key = bucket["key"]
            cve_count = bucket["doc_count"]
            critical_count = bucket.get("critical_count", {}).get("doc_count", 0)

            # Parse ecosystem:name format
            if ":" in package_key:
                ecosystem, name = package_key.split(":", 1)
            else:
                ecosystem = "unknown"
                name = package_key

            packages.append(PackageItem(
                ecosystem=ecosystem,
                name=name,
                cve_count=cve_count,
                critical_count=critical_count
            ))

        return PackageListResponse(
            packages=packages,
            total=len(packages)
        )

    except Exception:
        return PackageListResponse(packages=[], total=0)
