"""CTEM (Continuous Threat Exposure Management) API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["CTEM"])


class AssetRisk(BaseModel):
    asset_id: str
    risk_color: str  # Green, Yellow, Red
    finding_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int


class Finding(BaseModel):
    finding_id: str
    asset_id: str
    cve_id: str
    severity: str
    cvss_score: float
    description: str
    exposure: str  # internal, public, none
    status: str


@router.get("/assets/{asset_id}", response_model=AssetRisk)
async def get_asset_risk(asset_id: str):
    """Get CTEM risk assessment for an asset."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="ctem-asset-risk-v1",
            body={"query": {"term": {"asset_id": asset_id}}}
        )

        if response["hits"]["total"]["value"] == 0:
            raise HTTPException(status_code=404, detail=f"Asset risk for {asset_id} not found")

        return AssetRisk(**response["hits"]["hits"][0]["_source"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assets/{asset_id}/findings")
async def get_asset_findings(asset_id: str, severity: Optional[str] = None):
    """Get vulnerability findings for an asset."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    query = {"bool": {"must": [{"term": {"asset_id": asset_id}}]}}

    if severity:
        query["bool"]["must"].append({"term": {"severity": severity}})

    try:
        response = await client.search(
            index="ctem-findings-v1",
            body={
                "query": query,
                "size": 100,
                "sort": [{"cvss_score": "desc"}]
            }
        )

        findings = [hit["_source"] for hit in response["hits"]["hits"]]
        return {
            "asset_id": asset_id,
            "findings": findings,
            "total": response["hits"]["total"]["value"]
        }
    except Exception:
        return {"asset_id": asset_id, "findings": [], "total": 0}


@router.get("/findings")
async def list_findings(
    severity: Optional[str] = Query(None),
    exposure: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    """List all CTEM findings with filters."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    query = {"bool": {"must": []}}

    if severity:
        query["bool"]["must"].append({"term": {"severity": severity}})
    if exposure:
        query["bool"]["must"].append({"term": {"exposure": exposure}})

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
        return {
            "findings": findings,
            "total": response["hits"]["total"]["value"],
            "page": page,
            "page_size": page_size
        }
    except Exception:
        return {"findings": [], "total": 0, "page": page, "page_size": page_size}


@router.get("/summary")
async def get_ctem_summary():
    """Get CTEM summary statistics."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        # Get findings by severity
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
                    }
                }
            }
        )

        severity_counts = {
            b["key"]: b["doc_count"]
            for b in response["aggregations"]["by_severity"]["buckets"]
        }
        exposure_counts = {
            b["key"]: b["doc_count"]
            for b in response["aggregations"]["by_exposure"]["buckets"]
        }

        # Get risk distribution
        risk_response = await client.search(
            index="ctem-asset-risk-v1",
            body={
                "size": 0,
                "aggs": {
                    "by_risk": {
                        "terms": {"field": "risk_color"}
                    }
                }
            }
        )

        risk_counts = {
            b["key"]: b["doc_count"]
            for b in risk_response["aggregations"]["by_risk"]["buckets"]
        }

        return {
            "severity_distribution": severity_counts,
            "exposure_distribution": exposure_counts,
            "risk_distribution": risk_counts
        }
    except Exception:
        return {
            "severity_distribution": {},
            "exposure_distribution": {},
            "risk_distribution": {}
        }
