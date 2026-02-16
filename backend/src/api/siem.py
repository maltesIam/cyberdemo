"""SIEM API endpoints for incident management."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(tags=["SIEM"])


class IncidentBase(BaseModel):
    incident_id: str
    title: str
    description: str
    severity: str
    status: str
    created_at: datetime
    related_detections: list[str] = []
    related_assets: list[str] = []


class IncidentList(BaseModel):
    data: list[dict]
    total: int
    page: int
    page_size: int
    total_pages: int = 0


class Comment(BaseModel):
    message: str
    author: str = "system"


class CommentResponse(BaseModel):
    comment_id: str
    incident_id: str
    message: str
    author: str
    created_at: datetime


@router.get("/incidents", response_model=IncidentList)
async def list_incidents(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """List SIEM incidents with optional filters."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    query = {"bool": {"must": []}}

    if status:
        query["bool"]["must"].append({"term": {"status": status}})
    if severity:
        query["bool"]["must"].append({"term": {"severity": severity}})

    if not query["bool"]["must"]:
        query = {"match_all": {}}

    try:
        response = await client.search(
            index="siem-incidents-v1",
            body={
                "query": query,
                "from": (page - 1) * page_size,
                "size": page_size,
                "sort": [{"created_at": "desc"}]
            }
        )

        incidents = [hit["_source"] for hit in response["hits"]["hits"]]
        total = response["hits"]["total"]["value"]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return IncidentList(
            data=incidents,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        # Return empty list if index doesn't exist yet
        return IncidentList(data=[], total=0, page=page, page_size=page_size, total_pages=0)


@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Get detailed incident information."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="siem-incidents-v1",
            body={"query": {"term": {"incident_id": incident_id}}}
        )

        if response["hits"]["total"]["value"] == 0:
            raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

        return response["hits"]["hits"][0]["_source"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incidents/{incident_id}/entities")
async def get_incident_entities(incident_id: str):
    """Get entities associated with an incident."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="siem-entities-v1",
            body={"query": {"term": {"incident_id": incident_id}}, "size": 100}
        )

        entities = [hit["_source"] for hit in response["hits"]["hits"]]
        return {"incident_id": incident_id, "entities": entities}
    except Exception:
        return {"incident_id": incident_id, "entities": []}


@router.get("/incidents/{incident_id}/comments")
async def get_incident_comments(incident_id: str):
    """Get comments for an incident."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="siem-comments-v1",
            body={
                "query": {"term": {"incident_id": incident_id}},
                "sort": [{"created_at": "asc"}],
                "size": 100
            }
        )

        comments = [hit["_source"] for hit in response["hits"]["hits"]]
        return {"incident_id": incident_id, "comments": comments}
    except Exception:
        return {"incident_id": incident_id, "comments": []}


@router.post("/incidents/{incident_id}/comments", response_model=CommentResponse)
async def add_comment(incident_id: str, comment: Comment):
    """Add a comment to an incident."""
    from ..opensearch.client import get_opensearch_client
    import uuid

    client = await get_opensearch_client()

    comment_doc = {
        "comment_id": f"CMT-{uuid.uuid4().hex[:8].upper()}",
        "incident_id": incident_id,
        "message": comment.message,
        "author": comment.author,
        "created_at": datetime.utcnow().isoformat()
    }

    try:
        await client.index(
            index="siem-comments-v1",
            body=comment_doc,
            refresh=True
        )
        return CommentResponse(**comment_doc, created_at=datetime.utcnow())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/incidents/{incident_id}")
async def update_incident(incident_id: str, status: Optional[str] = None):
    """Update incident status (e.g., close)."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        # Find the document
        response = await client.search(
            index="siem-incidents-v1",
            body={"query": {"term": {"incident_id": incident_id}}}
        )

        if response["hits"]["total"]["value"] == 0:
            raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

        doc_id = response["hits"]["hits"][0]["_id"]

        update_body = {}
        if status:
            update_body["status"] = status

        await client.update(
            index="siem-incidents-v1",
            id=doc_id,
            body={"doc": update_body},
            refresh=True
        )

        return {"incident_id": incident_id, "updated": update_body}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
