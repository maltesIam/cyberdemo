"""Approvals API for Human-in-the-Loop decisions."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(tags=["Approvals"])


class ApprovalRequest(BaseModel):
    action_type: str  # contain, kill_process, etc.
    target_id: str  # device_id or process_id
    reason: str
    requester: str = "system"
    card_data: Optional[dict] = None


class ApprovalDecision(BaseModel):
    decision: str  # approved, rejected
    decided_by: str
    notes: Optional[str] = None


class ApprovalStatus(BaseModel):
    approval_id: str
    incident_id: str
    status: str  # pending, approved, rejected
    action_type: str
    target_id: str
    reason: str
    requester: str
    decided_by: Optional[str] = None
    decision_notes: Optional[str] = None
    created_at: datetime
    decided_at: Optional[datetime] = None


@router.get("/{incident_id}", response_model=ApprovalStatus)
async def get_approval(incident_id: str):
    """Get approval status for an incident."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="approvals-v1",
            body={
                "query": {"term": {"incident_id": incident_id}},
                "sort": [{"created_at": "desc"}],
                "size": 1
            }
        )

        if response["hits"]["total"]["value"] == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No approval request found for incident {incident_id}"
            )

        return ApprovalStatus(**response["hits"]["hits"][0]["_source"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{incident_id}/request", response_model=ApprovalStatus)
async def request_approval(incident_id: str, request: ApprovalRequest):
    """Request human approval for an action."""
    from ..opensearch.client import get_opensearch_client
    import uuid

    client = await get_opensearch_client()

    approval_id = f"APR-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.utcnow()

    approval_doc = {
        "approval_id": approval_id,
        "incident_id": incident_id,
        "status": "pending",
        "action_type": request.action_type,
        "target_id": request.target_id,
        "reason": request.reason,
        "requester": request.requester,
        "card_data": request.card_data,
        "created_at": timestamp.isoformat(),
        "decided_by": None,
        "decision_notes": None,
        "decided_at": None
    }

    try:
        await client.index(
            index="approvals-v1",
            body=approval_doc,
            refresh=True
        )

        return ApprovalStatus(**{**approval_doc, "created_at": timestamp})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{incident_id}", response_model=ApprovalStatus)
async def set_approval(incident_id: str, decision: ApprovalDecision):
    """Approve or reject an action request."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        # Find the latest pending approval for this incident
        response = await client.search(
            index="approvals-v1",
            body={
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"incident_id": incident_id}},
                            {"term": {"status": "pending"}}
                        ]
                    }
                },
                "sort": [{"created_at": "desc"}],
                "size": 1
            }
        )

        if response["hits"]["total"]["value"] == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No pending approval found for incident {incident_id}"
            )

        doc_id = response["hits"]["hits"][0]["_id"]
        approval_doc = response["hits"]["hits"][0]["_source"]

        timestamp = datetime.utcnow()

        update_body = {
            "status": decision.decision,
            "decided_by": decision.decided_by,
            "decision_notes": decision.notes,
            "decided_at": timestamp.isoformat()
        }

        await client.update(
            index="approvals-v1",
            id=doc_id,
            body={"doc": update_body},
            refresh=True
        )

        approval_doc.update(update_body)
        return ApprovalStatus(**{
            **approval_doc,
            "created_at": datetime.fromisoformat(approval_doc["created_at"]),
            "decided_at": timestamp
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending/list")
async def list_pending_approvals():
    """List all pending approval requests."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="approvals-v1",
            body={
                "query": {"term": {"status": "pending"}},
                "sort": [{"created_at": "asc"}],
                "size": 100
            }
        )

        approvals = [hit["_source"] for hit in response["hits"]["hits"]]
        return {"approvals": approvals, "total": len(approvals)}
    except Exception:
        return {"approvals": [], "total": 0}
