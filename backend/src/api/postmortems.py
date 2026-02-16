"""Postmortems API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["Postmortems"])


class PostmortemList(BaseModel):
    data: list[dict]
    total: int
    page: int
    page_size: int
    total_pages: int = 0


@router.get("", response_model=PostmortemList)
async def list_postmortems(
    incident_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    """List postmortem reports."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    query = {"bool": {"must": []}}
    if incident_id:
        query["bool"]["must"].append({"term": {"incident_id": incident_id}})

    if not query["bool"]["must"]:
        query = {"match_all": {}}

    try:
        response = await client.search(
            index="postmortems-v1",
            body={
                "query": query,
                "from": (page - 1) * page_size,
                "size": page_size,
                "sort": [{"created_at": "desc"}]
            }
        )

        postmortems = [hit["_source"] for hit in response["hits"]["hits"]]
        total = response["hits"]["total"]["value"]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return PostmortemList(
            data=postmortems,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception:
        return PostmortemList(data=[], total=0, page=page, page_size=page_size, total_pages=0)


@router.get("/{postmortem_id}")
async def get_postmortem(postmortem_id: str):
    """Get a specific postmortem report."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="postmortems-v1",
            body={"query": {"term": {"postmortem_id": postmortem_id}}}
        )

        if response["hits"]["total"]["value"] == 0:
            raise HTTPException(status_code=404, detail=f"Postmortem {postmortem_id} not found")

        return response["hits"]["hits"][0]["_source"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
