"""Agent Timeline (Actions) API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["Timeline"])


class AgentActionList(BaseModel):
    data: list[dict]
    total: int
    page: int
    page_size: int
    total_pages: int = 0


@router.get("", response_model=AgentActionList)
async def list_agent_actions(
    incident_id: Optional[str] = Query(None),
    action_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    """List agent actions timeline."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    query = {"bool": {"must": []}}
    if incident_id:
        query["bool"]["must"].append({"term": {"incident_id": incident_id}})
    if action_type:
        query["bool"]["must"].append({"term": {"action_type": action_type}})
    if status:
        query["bool"]["must"].append({"term": {"status": status}})

    if not query["bool"]["must"]:
        query = {"match_all": {}}

    try:
        response = await client.search(
            index="agent-actions-v1",
            body={
                "query": query,
                "from": (page - 1) * page_size,
                "size": page_size,
                "sort": [{"timestamp": "desc"}]
            }
        )

        actions = [hit["_source"] for hit in response["hits"]["hits"]]
        total = response["hits"]["total"]["value"]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return AgentActionList(
            data=actions,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception:
        return AgentActionList(data=[], total=0, page=page, page_size=page_size, total_pages=0)


@router.get("/{action_id}")
async def get_agent_action(action_id: str):
    """Get a specific agent action."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="agent-actions-v1",
            body={"query": {"term": {"action_id": action_id}}}
        )

        if response["hits"]["total"]["value"] == 0:
            raise HTTPException(status_code=404, detail=f"Action {action_id} not found")

        return response["hits"]["hits"][0]["_source"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
