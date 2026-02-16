"""Vulnerabilities API endpoints for CVE management."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional


router = APIRouter(tags=["Vulnerabilities"])


class VulnerabilityList(BaseModel):
    data: list[dict]
    total: int
    page: int
    page_size: int
    total_pages: int = 0


class VulnerabilitySummary(BaseModel):
    by_severity: dict = {}
    by_exposure: dict = {}
    kev_count: int = 0
    exploit_available_count: int = 0
    avg_cvss: float = 0.0
    top_cves: list[dict] = []


@router.get("", response_model=VulnerabilityList)
async def list_vulnerabilities(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    cvss_min: Optional[float] = Query(None, description="Minimum CVSS score"),
    cvss_max: Optional[float] = Query(None, description="Maximum CVSS score"),
    epss_min: Optional[float] = Query(None, description="Minimum EPSS score"),
    epss_max: Optional[float] = Query(None, description="Maximum EPSS score"),
    kev: Optional[bool] = Query(None, description="Filter KEV entries (exploit_available)"),
    exploit_available: Optional[bool] = Query(None, description="Filter by exploit availability"),
    search: Optional[str] = Query(None, description="Search in CVE ID or title"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """List vulnerability findings with filters."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    query = {"bool": {"must": []}}

    if severity:
        query["bool"]["must"].append({"term": {"severity": severity}})
    if cvss_min is not None:
        query["bool"]["must"].append({"range": {"cvss_score": {"gte": cvss_min}}})
    if cvss_max is not None:
        query["bool"]["must"].append({"range": {"cvss_score": {"lte": cvss_max}}})
    if epss_min is not None:
        query["bool"]["must"].append({"range": {"epss_score": {"gte": epss_min}}})
    if epss_max is not None:
        query["bool"]["must"].append({"range": {"epss_score": {"lte": epss_max}}})
    if kev is not None:
        query["bool"]["must"].append({"term": {"exploit_available": kev}})
    if exploit_available is not None:
        query["bool"]["must"].append({"term": {"exploit_available": exploit_available}})
    if search:
        query["bool"]["must"].append({
            "bool": {
                "should": [
                    {"wildcard": {"cve_id": f"*{search.upper()}*"}},
                    {"match": {"title": search}},
                ],
                "minimum_should_match": 1,
            }
        })

    if not query["bool"]["must"]:
        query = {"match_all": {}}

    try:
        response = await client.search(
            index="ctem-findings-v1",
            body={
                "query": query,
                "from": (page - 1) * page_size,
                "size": page_size,
                "sort": [{"cvss_score": "desc"}]
            }
        )

        findings = [hit["_source"] for hit in response["hits"]["hits"]]
        total = response["hits"]["total"]["value"]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return VulnerabilityList(
            data=findings,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    except Exception:
        return VulnerabilityList(data=[], total=0, page=page, page_size=page_size, total_pages=0)


@router.get("/summary", response_model=VulnerabilitySummary)
async def get_vulnerability_summary():
    """Aggregation stats for vulnerabilities."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="ctem-findings-v1",
            body={
                "size": 0,
                "aggs": {
                    "by_severity": {
                        "terms": {"field": "severity"}
                    },
                    "by_exposure": {
                        "terms": {"field": "exposure"}
                    },
                    "kev_count": {
                        "filter": {"term": {"exploit_available": True}}
                    },
                    "exploit_available_count": {
                        "filter": {"term": {"exploit_available": True}}
                    },
                    "avg_cvss": {
                        "avg": {"field": "cvss_score"}
                    },
                    "top_cves": {
                        "top_hits": {
                            "size": 5,
                            "sort": [{"cvss_score": "desc"}],
                            "_source": ["cve_id", "title", "severity", "cvss_score", "exploit_available"]
                        }
                    }
                }
            }
        )

        aggs = response["aggregations"]

        by_severity = {
            b["key"]: b["doc_count"]
            for b in aggs["by_severity"]["buckets"]
        }
        by_exposure = {
            b["key"]: b["doc_count"]
            for b in aggs.get("by_exposure", {}).get("buckets", [])
        }
        kev_count = aggs["kev_count"]["doc_count"]
        exploit_count = aggs["exploit_available_count"]["doc_count"]
        avg_cvss = aggs["avg_cvss"]["value"] or 0.0
        top_cves = [hit["_source"] for hit in aggs["top_cves"]["hits"]["hits"]]

        return VulnerabilitySummary(
            by_severity=by_severity,
            by_exposure=by_exposure,
            kev_count=kev_count,
            exploit_available_count=exploit_count,
            avg_cvss=round(avg_cvss, 2),
            top_cves=top_cves,
        )
    except Exception:
        return VulnerabilitySummary(
            by_severity={},
            by_exposure={},
            kev_count=0,
            exploit_available_count=0,
            avg_cvss=0.0,
            top_cves=[],
        )


@router.get("/cves/{cve_id}")
async def get_cve(cve_id: str):
    """Get single CVE detail from findings."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="ctem-findings-v1",
            body={"query": {"term": {"cve_id": cve_id}}, "size": 10}
        )

        if response["hits"]["total"]["value"] == 0:
            raise HTTPException(status_code=404, detail=f"CVE {cve_id} not found")

        # Return the first match plus info about affected assets
        findings = [hit["_source"] for hit in response["hits"]["hits"]]
        primary = findings[0]
        affected_assets = list(set(f.get("asset_id") for f in findings if f.get("asset_id")))

        return {
            **primary,
            "affected_asset_count": len(affected_assets),
            "affected_assets": affected_assets,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
