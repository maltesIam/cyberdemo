"""Assets API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["Assets"])


class AssetList(BaseModel):
    data: list[dict]
    total: int
    page: int
    page_size: int
    total_pages: int = 0


@router.get("", response_model=AssetList)
async def list_assets(
    asset_type: Optional[str] = Query(None, description="Filter by type (workstation, server, mobile, other)"),
    os: Optional[str] = Query(None, description="Filter by OS"),
    site: Optional[str] = Query(None, description="Filter by site"),
    risk: Optional[str] = Query(None, description="Filter by risk color"),
    tags: Optional[str] = Query(None, description="Filter by tag"),
    search: Optional[str] = Query(None, description="Search in hostname"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """List assets with optional filters."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    query = {"bool": {"must": []}}

    if asset_type:
        query["bool"]["must"].append({"term": {"asset_type": asset_type}})
    if os:
        query["bool"]["must"].append({"match": {"os": os}})
    if site:
        query["bool"]["must"].append({"term": {"site": site}})
    if risk:
        query["bool"]["must"].append({"term": {"ctem.risk_color": risk}})
    if tags:
        query["bool"]["must"].append({"term": {"tags": tags}})
    if search:
        query["bool"]["must"].append({"wildcard": {"hostname": f"*{search.upper()}*"}})

    if not query["bool"]["must"]:
        query = {"match_all": {}}

    try:
        response = await client.search(
            index="assets-inventory-v1",
            body={
                "query": query,
                "from": (page - 1) * page_size,
                "size": page_size,
                "sort": [{"hostname": "asc"}]
            }
        )

        assets = [hit["_source"] for hit in response["hits"]["hits"]]
        total = response["hits"]["total"]["value"]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return AssetList(
            data=assets,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception:
        return AssetList(data=[], total=0, page=page, page_size=page_size, total_pages=0)


@router.get("/{asset_id}")
async def get_asset(asset_id: str):
    """Get detailed asset information."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="assets-inventory-v1",
            body={"query": {"term": {"asset_id": asset_id}}}
        )

        if response["hits"]["total"]["value"] == 0:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")

        return response["hits"]["hits"][0]["_source"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{asset_id}/detections")
async def get_asset_detections(asset_id: str):
    """Get all EDR detections for an asset."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="edr-detections-v1",
            body={
                "query": {"term": {"asset_id": asset_id}},
                "sort": [{"timestamp": "desc"}],
                "size": 100
            }
        )

        detections = [hit["_source"] for hit in response["hits"]["hits"]]
        return {"asset_id": asset_id, "detections": detections}
    except Exception:
        return {"asset_id": asset_id, "detections": []}


@router.get("/{asset_id}/incidents")
async def get_asset_incidents(asset_id: str):
    """Get all SIEM incidents involving an asset."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="siem-incidents-v1",
            body={
                "query": {"term": {"related_assets": asset_id}},
                "sort": [{"created_at": "desc"}],
                "size": 100
            }
        )

        incidents = [hit["_source"] for hit in response["hits"]["hits"]]
        return {"asset_id": asset_id, "incidents": incidents}
    except Exception:
        return {"asset_id": asset_id, "incidents": []}


@router.get("/summary/stats")
async def get_assets_summary():
    """Get asset inventory summary statistics."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="assets-inventory-v1",
            body={
                "size": 0,
                "aggs": {
                    "by_type": {
                        "terms": {"field": "asset_type"}
                    },
                    "by_os": {
                        "terms": {"field": "os.keyword", "size": 10}
                    },
                    "by_site": {
                        "terms": {"field": "site"}
                    },
                    "by_risk": {
                        "terms": {"field": "ctem.risk_color"}
                    },
                    "total": {
                        "value_count": {"field": "asset_id"}
                    }
                }
            }
        )

        return {
            "total": response["aggregations"]["total"]["value"],
            "by_type": {
                b["key"]: b["doc_count"]
                for b in response["aggregations"]["by_type"]["buckets"]
            },
            "by_os": {
                b["key"]: b["doc_count"]
                for b in response["aggregations"]["by_os"]["buckets"]
            },
            "by_site": {
                b["key"]: b["doc_count"]
                for b in response["aggregations"]["by_site"]["buckets"]
            },
            "by_risk": {
                b["key"]: b["doc_count"]
                for b in response["aggregations"]["by_risk"]["buckets"]
            }
        }
    except Exception:
        return {
            "total": 0,
            "by_type": {},
            "by_os": {},
            "by_site": {},
            "by_risk": {}
        }
