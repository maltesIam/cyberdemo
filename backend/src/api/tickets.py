"""Tickets API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["Tickets"])


class TicketList(BaseModel):
    data: list[dict]
    total: int
    page: int
    page_size: int
    total_pages: int = 0


@router.get("", response_model=TicketList)
async def list_tickets(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    incident_id: Optional[str] = Query(None),
    system: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    """List tickets."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    query = {"bool": {"must": []}}
    if status:
        query["bool"]["must"].append({"term": {"status": status}})
    if priority:
        query["bool"]["must"].append({"term": {"priority": priority}})
    if incident_id:
        query["bool"]["must"].append({"term": {"incident_id": incident_id}})
    if system:
        query["bool"]["must"].append({"term": {"system": system}})

    if not query["bool"]["must"]:
        query = {"match_all": {}}

    try:
        response = await client.search(
            index="tickets-v1",
            body={
                "query": query,
                "from": (page - 1) * page_size,
                "size": page_size,
                "sort": [{"created_at": "desc"}]
            }
        )

        tickets = [hit["_source"] for hit in response["hits"]["hits"]]
        total = response["hits"]["total"]["value"]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return TicketList(
            data=tickets,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception:
        return TicketList(data=[], total=0, page=page, page_size=page_size, total_pages=0)


@router.get("/{ticket_id}")
async def get_ticket(ticket_id: str):
    """Get a specific ticket."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="tickets-v1",
            body={"query": {"term": {"ticket_id": ticket_id}}}
        )

        if response["hits"]["total"]["value"] == 0:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")

        return response["hits"]["hits"][0]["_source"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
