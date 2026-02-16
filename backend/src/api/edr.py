"""EDR API endpoints for detection management."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(tags=["EDR"])


class DetectionList(BaseModel):
    data: list[dict]
    total: int
    page: int
    page_size: int
    total_pages: int = 0


class ContainRequest(BaseModel):
    reason: str


class ContainResponse(BaseModel):
    action_id: str
    device_id: str
    status: str
    reason: str
    timestamp: datetime


@router.get("/detections", response_model=DetectionList)
async def list_detections(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    asset_id: Optional[str] = Query(None, description="Filter by asset"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """List EDR detections with optional filters."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    query = {"bool": {"must": []}}

    if severity:
        query["bool"]["must"].append({"term": {"severity": severity}})
    if asset_id:
        query["bool"]["must"].append({"term": {"asset_id": asset_id}})

    if not query["bool"]["must"]:
        query = {"match_all": {}}

    try:
        response = await client.search(
            index="edr-detections-v1",
            body={
                "query": query,
                "from": (page - 1) * page_size,
                "size": page_size,
                "sort": [{"detected_at": "desc"}]
            }
        )

        detections = [hit["_source"] for hit in response["hits"]["hits"]]
        total = response["hits"]["total"]["value"]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return DetectionList(
            data=detections,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception:
        return DetectionList(data=[], total=0, page=page, page_size=page_size, total_pages=0)


@router.get("/detections/{detection_id}")
async def get_detection(detection_id: str):
    """Get detailed detection information."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="edr-detections-v1",
            body={"query": {"term": {"detection_id": detection_id}}}
        )

        if response["hits"]["total"]["value"] == 0:
            raise HTTPException(status_code=404, detail=f"Detection {detection_id} not found")

        return response["hits"]["hits"][0]["_source"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detections/{detection_id}/process-tree")
async def get_process_tree(detection_id: str):
    """Get process tree for a detection."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="edr-process-trees-v1",
            body={"query": {"term": {"detection_id": detection_id}}}
        )

        if response["hits"]["total"]["value"] == 0:
            raise HTTPException(status_code=404, detail=f"Process tree for {detection_id} not found")

        return response["hits"]["hits"][0]["_source"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hunt/hash/{sha256}")
async def hunt_hash(sha256: str):
    """Search for propagation of a hash across the organization."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="edr-detections-v1",
            body={
                "query": {"term": {"file.sha256": sha256}},
                "size": 100
            }
        )

        detections = [hit["_source"] for hit in response["hits"]["hits"]]

        # Get unique hosts
        hosts = list(set(d.get("asset_id") for d in detections if d.get("asset_id")))

        return {
            "sha256": sha256,
            "total_detections": len(detections),
            "total_hosts_found": len(hosts),
            "hosts": hosts,
            "detections": detections
        }
    except Exception:
        return {
            "sha256": sha256,
            "total_detections": 0,
            "total_hosts_found": 0,
            "hosts": [],
            "detections": []
        }


@router.get("/devices/{device_id}")
async def get_device(device_id: str):
    """Get device information from assets."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="assets-inventory-v1",
            body={"query": {"term": {"asset_id": device_id}}}
        )

        if response["hits"]["total"]["value"] == 0:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

        return response["hits"]["hits"][0]["_source"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/devices/{device_id}/contain", response_model=ContainResponse)
async def contain_host(device_id: str, request: ContainRequest):
    """Execute network containment on a host."""
    from ..opensearch.client import get_opensearch_client
    import uuid

    client = await get_opensearch_client()

    action_id = f"ACT-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.utcnow()

    # Log the containment action
    action_doc = {
        "action_id": action_id,
        "device_id": device_id,
        "action_type": "contain",
        "reason": request.reason,
        "status": "success",
        "timestamp": timestamp.isoformat()
    }

    try:
        # Index the action
        await client.index(
            index="edr-host-actions-v1",
            body=action_doc,
            refresh=True
        )

        # Update asset containment status
        response = await client.search(
            index="assets-inventory-v1",
            body={"query": {"term": {"asset_id": device_id}}}
        )

        if response["hits"]["total"]["value"] > 0:
            doc_id = response["hits"]["hits"][0]["_id"]
            await client.update(
                index="assets-inventory-v1",
                id=doc_id,
                body={"doc": {"edr": {"containment_status": "contained"}}},
                refresh=True
            )

        return ContainResponse(
            action_id=action_id,
            device_id=device_id,
            status="success",
            reason=request.reason,
            timestamp=timestamp
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/devices/{device_id}/lift-containment")
async def lift_containment(device_id: str):
    """Lift network containment on a host."""
    from ..opensearch.client import get_opensearch_client
    import uuid

    client = await get_opensearch_client()

    action_id = f"ACT-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.utcnow()

    action_doc = {
        "action_id": action_id,
        "device_id": device_id,
        "action_type": "lift_containment",
        "reason": "Manual lift",
        "status": "success",
        "timestamp": timestamp.isoformat()
    }

    try:
        await client.index(
            index="edr-host-actions-v1",
            body=action_doc,
            refresh=True
        )

        # Update asset containment status
        response = await client.search(
            index="assets-inventory-v1",
            body={"query": {"term": {"asset_id": device_id}}}
        )

        if response["hits"]["total"]["value"] > 0:
            doc_id = response["hits"]["hits"][0]["_id"]
            await client.update(
                index="assets-inventory-v1",
                id=doc_id,
                body={"doc": {"edr": {"containment_status": "normal"}}},
                refresh=True
            )

        return {"action_id": action_id, "device_id": device_id, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
