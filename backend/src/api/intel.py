"""Threat Intelligence API endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["Threat Intel"])


class IndicatorResponse(BaseModel):
    indicator_type: str
    indicator_value: str
    verdict: str
    confidence: int
    vt_score: Optional[str] = None
    labels: list[str] = []
    sources: list[str] = []
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None


@router.get("/indicators/{indicator_type}/{value}", response_model=IndicatorResponse)
async def get_indicator(indicator_type: str, value: str):
    """Get threat intelligence for an indicator (hash, IP, domain)."""
    from ..opensearch.client import get_opensearch_client

    if indicator_type not in ["filehash", "ip", "domain"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid indicator type: {indicator_type}. Must be filehash, ip, or domain"
        )

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="threat-intel-v1",
            body={
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"indicator_type": indicator_type}},
                            {"term": {"indicator_value": value}}
                        ]
                    }
                }
            }
        )

        if response["hits"]["total"]["value"] == 0:
            # Return unknown verdict for unmatched indicators
            return IndicatorResponse(
                indicator_type=indicator_type,
                indicator_value=value,
                verdict="unknown",
                confidence=0,
                vt_score=None,
                labels=[],
                sources=[]
            )

        return IndicatorResponse(**response["hits"]["hits"][0]["_source"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_indicators(
    verdict: Optional[str] = None,
    indicator_type: Optional[str] = None,
    limit: int = 50
):
    """Search threat intelligence indicators."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    query = {"bool": {"must": []}}

    if verdict:
        query["bool"]["must"].append({"term": {"verdict": verdict}})
    if indicator_type:
        query["bool"]["must"].append({"term": {"indicator_type": indicator_type}})

    if not query["bool"]["must"]:
        query = {"match_all": {}}

    try:
        response = await client.search(
            index="threat-intel-v1",
            body={
                "query": query,
                "size": limit,
                "sort": [{"last_seen": "desc"}]
            }
        )

        indicators = [hit["_source"] for hit in response["hits"]["hits"]]
        return {
            "indicators": indicators,
            "total": response["hits"]["total"]["value"]
        }
    except Exception:
        return {"indicators": [], "total": 0}
