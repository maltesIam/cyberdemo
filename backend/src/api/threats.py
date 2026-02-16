"""Threats API endpoints for IOC and threat actor management."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional


router = APIRouter(tags=["Threats"])


class IOCList(BaseModel):
    data: list[dict]
    total: int
    page: int
    page_size: int
    total_pages: int = 0


class GeoMap(BaseModel):
    countries: list[dict] = []
    total_iocs: int = 0


class MitreMap(BaseModel):
    techniques: list[dict] = []
    total_detections: int = 0


@router.get("", response_model=IOCList)
async def list_iocs(
    ioc_type: Optional[str] = Query(None, description="Filter by type: filehash, ip, domain"),
    verdict: Optional[str] = Query(None, description="Filter by verdict: malicious, suspicious, benign"),
    risk_min: Optional[int] = Query(None, description="Minimum confidence/risk score"),
    search: Optional[str] = Query(None, description="Search in indicator value"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """List threat intelligence IOCs with filters."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    query = {"bool": {"must": []}}

    if ioc_type:
        query["bool"]["must"].append({"term": {"indicator_type": ioc_type}})
    if verdict:
        query["bool"]["must"].append({"term": {"verdict": verdict}})
    if risk_min is not None:
        query["bool"]["must"].append({"range": {"confidence": {"gte": risk_min}}})
    if search:
        query["bool"]["must"].append({"wildcard": {"indicator_value": f"*{search}*"}})

    if not query["bool"]["must"]:
        query = {"match_all": {}}

    try:
        response = await client.search(
            index="threat-intel-v1",
            body={
                "query": query,
                "from": (page - 1) * page_size,
                "size": page_size,
                "sort": [{"last_seen": "desc"}]
            }
        )

        iocs = [hit["_source"] for hit in response["hits"]["hits"]]
        total = response["hits"]["total"]["value"]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return IOCList(
            data=iocs,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    except Exception:
        return IOCList(data=[], total=0, page=page, page_size=page_size, total_pages=0)


@router.get("/iocs/{ioc_id}")
async def get_ioc(ioc_id: str):
    """Get single IOC detail by indicator value."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="threat-intel-v1",
            body={"query": {"term": {"indicator_value": ioc_id}}}
        )

        if response["hits"]["total"]["value"] == 0:
            raise HTTPException(status_code=404, detail=f"IOC {ioc_id} not found")

        return response["hits"]["hits"][0]["_source"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/map", response_model=GeoMap)
async def get_threat_map():
    """Geo aggregation for world map from IOC data."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        # Aggregate IOCs by source field (as proxy for country/geo data)
        response = await client.search(
            index="threat-intel-v1",
            body={
                "size": 0,
                "query": {"term": {"verdict": "malicious"}},
                "aggs": {
                    "by_source": {
                        "terms": {"field": "source", "size": 50}
                    }
                }
            }
        )

        total_iocs = response["hits"]["total"]["value"]
        countries = [
            {"name": b["key"], "count": b["doc_count"]}
            for b in response["aggregations"]["by_source"]["buckets"]
        ]

        return GeoMap(countries=countries, total_iocs=total_iocs)
    except Exception:
        return GeoMap(countries=[], total_iocs=0)


@router.get("/actors/{actor_name}")
async def get_actor_iocs(actor_name: str):
    """Get IOCs linked to a specific threat actor via labels."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="threat-intel-v1",
            body={
                "query": {
                    "bool": {
                        "should": [
                            {"term": {"labels": actor_name}},
                            {"term": {"tags": actor_name}},
                            {"term": {"malware_family": actor_name}},
                        ],
                        "minimum_should_match": 1,
                    }
                },
                "size": 100,
                "sort": [{"last_seen": "desc"}]
            }
        )

        iocs = [hit["_source"] for hit in response["hits"]["hits"]]
        return {
            "actor": actor_name,
            "iocs": iocs,
            "total": response["hits"]["total"]["value"],
        }
    except Exception:
        return {"actor": actor_name, "iocs": [], "total": 0}


@router.get("/mitre", response_model=MitreMap)
async def get_mitre_coverage():
    """ATT&CK technique coverage from EDR detections."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="edr-detections-v1",
            body={
                "size": 0,
                "aggs": {
                    "by_technique": {
                        "terms": {"field": "technique_id", "size": 100},
                        "aggs": {
                            "technique_name": {
                                "terms": {"field": "technique_name.keyword", "size": 1}
                            },
                            "by_severity": {
                                "terms": {"field": "severity"}
                            }
                        }
                    }
                }
            }
        )

        total_detections = response["hits"]["total"]["value"]
        techniques = []

        for bucket in response["aggregations"]["by_technique"]["buckets"]:
            name_buckets = bucket.get("technique_name", {}).get("buckets", [])
            technique_name = name_buckets[0]["key"] if name_buckets else bucket["key"]

            severity_dist = {
                b["key"]: b["doc_count"]
                for b in bucket.get("by_severity", {}).get("buckets", [])
            }

            techniques.append({
                "technique_id": bucket["key"],
                "technique_name": technique_name,
                "detection_count": bucket["doc_count"],
                "severity_distribution": severity_dist,
            })

        return MitreMap(techniques=techniques, total_detections=total_detections)
    except Exception:
        return MitreMap(techniques=[], total_detections=0)
