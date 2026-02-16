"""Surface WOW Command Center API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


router = APIRouter(tags=["Surface"])


class SurfaceOverview(BaseModel):
    total_assets: int = 0
    critical_assets: int = 0
    active_detections: int = 0
    open_incidents: int = 0
    critical_incidents: int = 0
    contained_hosts: int = 0
    critical_cves: int = 0
    kev_cves: int = 0
    high_risk_iocs: int = 0
    timestamp: str = ""


class NodeList(BaseModel):
    total: int = 0
    nodes: list[dict] = []


class ConnectionList(BaseModel):
    connections: list[dict] = []


@router.get("/overview", response_model=SurfaceOverview)
async def get_overview():
    """Aggregated KPIs for the Bottom Bar."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()
    now = datetime.utcnow().isoformat()

    total_assets = 0
    critical_assets = 0
    active_detections = 0
    open_incidents = 0
    critical_incidents = 0
    contained_hosts = 0
    critical_cves = 0
    kev_cves = 0
    high_risk_iocs = 0

    # Total assets and critical assets (risk_score >= 80 in ctem-asset-risk-v1)
    try:
        resp = await client.search(
            index="assets-inventory-v1",
            body={"size": 0, "aggs": {"total": {"value_count": {"field": "asset_id"}}}}
        )
        total_assets = resp["hits"]["total"]["value"]
    except Exception:
        pass

    try:
        resp = await client.search(
            index="ctem-asset-risk-v1",
            body={
                "size": 0,
                "query": {"range": {"risk_score": {"gte": 80}}},
                "aggs": {"count": {"value_count": {"field": "asset_id"}}}
            }
        )
        critical_assets = resp["hits"]["total"]["value"]
    except Exception:
        pass

    # Active detections
    try:
        resp = await client.search(
            index="edr-detections-v1",
            body={"size": 0, "query": {"match_all": {}}}
        )
        active_detections = resp["hits"]["total"]["value"]
    except Exception:
        pass

    # Open incidents and critical incidents
    try:
        resp = await client.search(
            index="siem-incidents-v1",
            body={
                "size": 0,
                "query": {
                    "bool": {
                        "must_not": [{"terms": {"status": ["closed", "resolved"]}}]
                    }
                },
                "aggs": {
                    "critical": {
                        "filter": {"term": {"severity": "Critical"}}
                    }
                }
            }
        )
        open_incidents = resp["hits"]["total"]["value"]
        critical_incidents = resp["aggregations"]["critical"]["doc_count"]
    except Exception:
        pass

    # Contained hosts
    try:
        resp = await client.search(
            index="assets-inventory-v1",
            body={
                "size": 0,
                "query": {"term": {"edr.containment_status": "contained"}}
            }
        )
        contained_hosts = resp["hits"]["total"]["value"]
    except Exception:
        pass

    # Critical CVEs (cvss_score >= 9)
    try:
        resp = await client.search(
            index="ctem-findings-v1",
            body={
                "size": 0,
                "query": {"range": {"cvss_score": {"gte": 9.0}}}
            }
        )
        critical_cves = resp["hits"]["total"]["value"]
    except Exception:
        pass

    # KEV CVEs (exploit_available == true as proxy for KEV)
    try:
        resp = await client.search(
            index="ctem-findings-v1",
            body={
                "size": 0,
                "query": {"term": {"exploit_available": True}}
            }
        )
        kev_cves = resp["hits"]["total"]["value"]
    except Exception:
        pass

    # High risk IOCs (confidence >= 80 and verdict malicious)
    try:
        resp = await client.search(
            index="threat-intel-v1",
            body={
                "size": 0,
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"verdict": "malicious"}},
                            {"range": {"confidence": {"gte": 80}}}
                        ]
                    }
                }
            }
        )
        high_risk_iocs = resp["hits"]["total"]["value"]
    except Exception:
        pass

    return SurfaceOverview(
        total_assets=total_assets,
        critical_assets=critical_assets,
        active_detections=active_detections,
        open_incidents=open_incidents,
        critical_incidents=critical_incidents,
        contained_hosts=contained_hosts,
        critical_cves=critical_cves,
        kev_cves=kev_cves,
        high_risk_iocs=high_risk_iocs,
        timestamp=now,
    )


@router.get("/nodes", response_model=NodeList)
async def get_nodes(
    page: int = Query(1, ge=1),
    page_size: int = Query(200, ge=1, le=500),
    time_range: Optional[str] = Query(None, description="Time range: 1h, 6h, 24h, 7d, 30d"),
    asset_type: Optional[str] = Query(None, description="Filter by asset type"),
    risk_min: Optional[int] = Query(None, description="Minimum risk score"),
    risk_max: Optional[int] = Query(None, description="Maximum risk score"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    search: Optional[str] = Query(None, description="Search in hostname"),
):
    """Enriched assets with layer data for canvas visualization."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    # Build asset query
    query = {"bool": {"must": []}}

    if asset_type:
        query["bool"]["must"].append({"term": {"asset_type": asset_type}})
    if search:
        query["bool"]["must"].append({"wildcard": {"hostname": f"*{search.upper()}*"}})

    if not query["bool"]["must"]:
        query = {"match_all": {}}

    try:
        # Fetch assets
        resp = await client.search(
            index="assets-inventory-v1",
            body={
                "query": query,
                "from": (page - 1) * page_size,
                "size": page_size,
                "sort": [{"hostname": "asc"}]
            }
        )

        assets = [hit["_source"] for hit in resp["hits"]["hits"]]
        total = resp["hits"]["total"]["value"]

        if not assets:
            return NodeList(total=0, nodes=[])

        # Collect asset_ids for enrichment queries
        asset_ids = [a.get("asset_id") for a in assets if a.get("asset_id")]

        # Fetch detection counts per asset
        detection_counts = {}
        detection_max_severity = {}
        try:
            det_resp = await client.search(
                index="edr-detections-v1",
                body={
                    "size": 0,
                    "query": {"terms": {"asset_id": asset_ids}},
                    "aggs": {
                        "by_asset": {
                            "terms": {"field": "asset_id", "size": len(asset_ids)},
                            "aggs": {
                                "max_sev": {"terms": {"field": "severity", "size": 1, "order": {"_key": "desc"}}}
                            }
                        }
                    }
                }
            )
            for bucket in det_resp["aggregations"]["by_asset"]["buckets"]:
                aid = bucket["key"]
                detection_counts[aid] = bucket["doc_count"]
                sev_buckets = bucket.get("max_sev", {}).get("buckets", [])
                detection_max_severity[aid] = sev_buckets[0]["key"] if sev_buckets else "Low"
        except Exception:
            pass

        # Fetch incident counts per asset
        incident_counts = {}
        incident_status = {}
        try:
            inc_resp = await client.search(
                index="siem-incidents-v1",
                body={
                    "size": 0,
                    "query": {"terms": {"related_assets": asset_ids}},
                    "aggs": {
                        "by_asset": {
                            "terms": {"field": "related_assets", "size": len(asset_ids)},
                            "aggs": {
                                "latest_status": {"terms": {"field": "status", "size": 1}}
                            }
                        }
                    }
                }
            )
            for bucket in inc_resp["aggregations"]["by_asset"]["buckets"]:
                aid = bucket["key"]
                incident_counts[aid] = bucket["doc_count"]
                status_buckets = bucket.get("latest_status", {}).get("buckets", [])
                incident_status[aid] = status_buckets[0]["key"] if status_buckets else "unknown"
        except Exception:
            pass

        # Fetch CTEM risk per asset
        ctem_risk = {}
        ctem_risk_score = {}
        ctem_findings_count = {}
        try:
            ctem_resp = await client.search(
                index="ctem-asset-risk-v1",
                body={
                    "size": len(asset_ids),
                    "query": {"terms": {"asset_id": asset_ids}},
                }
            )
            for hit in ctem_resp["hits"]["hits"]:
                src = hit["_source"]
                aid = src.get("asset_id")
                if aid:
                    risk_color = src.get("risk_color", "Green")
                    ctem_risk[aid] = risk_color
                    ctem_findings_count[aid] = src.get("vulnerability_count", src.get("finding_count", 0))
                    # Derive numeric risk_score from risk_color + finding_count
                    base_score = {"Red": 80, "Yellow": 50, "Green": 20}.get(risk_color, 30)
                    findings = ctem_findings_count[aid]
                    ctem_risk_score[aid] = min(100, base_score + min(findings * 2, 20))
        except Exception:
            pass

        # Fetch vulnerability counts per asset
        vuln_counts = {}
        vuln_critical = {}
        vuln_kev = {}
        try:
            vuln_resp = await client.search(
                index="ctem-findings-v1",
                body={
                    "size": 0,
                    "query": {"terms": {"asset_id": asset_ids}},
                    "aggs": {
                        "by_asset": {
                            "terms": {"field": "asset_id", "size": len(asset_ids)},
                            "aggs": {
                                "critical": {"filter": {"range": {"cvss_score": {"gte": 9.0}}}},
                                "kev": {"filter": {"term": {"exploit_available": True}}}
                            }
                        }
                    }
                }
            )
            for bucket in vuln_resp["aggregations"]["by_asset"]["buckets"]:
                aid = bucket["key"]
                vuln_counts[aid] = bucket["doc_count"]
                vuln_critical[aid] = bucket.get("critical", {}).get("doc_count", 0)
                vuln_kev[aid] = bucket.get("kev", {}).get("doc_count", 0)
        except Exception:
            pass

        # Fetch threat intel linked to assets (via IPs)
        threat_counts = {}
        threat_actors = {}
        try:
            asset_ips = [a.get("ip") for a in assets if a.get("ip")]
            if asset_ips:
                threat_resp = await client.search(
                    index="threat-intel-v1",
                    body={
                        "size": 0,
                        "query": {
                            "bool": {
                                "must": [{"terms": {"indicator_value": asset_ips}}]
                            }
                        },
                        "aggs": {
                            "by_ip": {
                                "terms": {"field": "indicator_value", "size": len(asset_ips)},
                                "aggs": {
                                    "actors": {"terms": {"field": "labels", "size": 5}}
                                }
                            }
                        }
                    }
                )
                for bucket in threat_resp["aggregations"]["by_ip"]["buckets"]:
                    ip_val = bucket["key"]
                    # Map IP back to asset_id
                    for a in assets:
                        if a.get("ip") == ip_val:
                            a_id = a.get("asset_id", "")
                            threat_counts[a_id] = threat_counts.get(a_id, 0) + bucket["doc_count"]
                            actor_names = [b["key"] for b in bucket.get("actors", {}).get("buckets", [])]
                            if a_id not in threat_actors:
                                threat_actors[a_id] = []
                            threat_actors[a_id].extend(actor_names)
        except Exception:
            pass

        # Build enriched nodes
        nodes = []
        for asset in assets:
            aid = asset.get("asset_id", "")
            edr_data = asset.get("edr", {}) or {}
            ctem_data = asset.get("ctem", {}) or {}

            det_count = detection_counts.get(aid, 0)
            inc_count = incident_counts.get(aid, 0)
            containment_status = edr_data.get("containment_status", "normal")
            is_contained = containment_status == "contained"

            node = {
                "id": aid,
                "hostname": asset.get("hostname", ""),
                "ip": asset.get("ip", ""),
                "type": asset.get("asset_type", ""),
                "os": asset.get("os", ""),
                "owner": asset.get("owner", ""),
                "department": asset.get("department", ""),
                "risk_score": ctem_risk_score.get(aid, 30),
                "criticality": asset.get("criticality", "medium"),
                "layers": {
                    "base": True,
                    "edr": {
                        "active": edr_data.get("agent_version") is not None,
                        "detection_count": det_count,
                        "max_severity": detection_max_severity.get(aid, "Low"),
                    },
                    "siem": {
                        "active": inc_count > 0,
                        "incident_count": inc_count,
                        "status": incident_status.get(aid, "none"),
                    },
                    "ctem": {
                        "active": ctem_data.get("finding_count", 0) > 0,
                        "risk_level": ctem_risk.get(aid, ctem_data.get("risk_color", "Green")),
                        "findings_count": ctem_findings_count.get(aid, ctem_data.get("finding_count", 0)),
                    },
                    "vulnerabilities": {
                        "active": vuln_counts.get(aid, 0) > 0,
                        "cve_count": vuln_counts.get(aid, 0),
                        "critical_count": vuln_critical.get(aid, 0),
                        "kev_count": vuln_kev.get(aid, 0),
                    },
                    "threats": {
                        "active": threat_counts.get(aid, 0) > 0,
                        "ioc_count": threat_counts.get(aid, 0),
                        "actors": list(set(threat_actors.get(aid, []))),
                    },
                    "containment": {
                        "active": is_contained,
                        "is_contained": is_contained,
                        "contained_at": edr_data.get("last_seen") if is_contained else None,
                    },
                    "relations": {
                        "active": inc_count > 0,
                        "connection_count": inc_count,
                    },
                },
            }

            # Apply risk_min/risk_max filter (post-query since risk_score is computed)
            if risk_min is not None and node["risk_score"] < risk_min:
                continue
            if risk_max is not None and node["risk_score"] > risk_max:
                continue

            nodes.append(node)

        return NodeList(total=total, nodes=nodes)

    except Exception:
        return NodeList(total=0, nodes=[])


@router.get("/connections", response_model=ConnectionList)
async def get_connections(
    asset_ids: Optional[str] = Query(None, description="Comma-separated asset IDs"),
    type: Optional[str] = Query(None, description="Connection type: lateral_movement, c2_communication, data_exfil, shared_ioc"),
):
    """Relationships between assets based on shared incidents/detections."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        # Build query for incidents with multiple related assets
        query: dict = {"bool": {"must": []}}

        if asset_ids:
            id_list = [aid.strip() for aid in asset_ids.split(",")]
            query["bool"]["must"].append({"terms": {"related_assets": id_list}})

        if not query["bool"]["must"]:
            query = {"match_all": {}}

        resp = await client.search(
            index="siem-incidents-v1",
            body={
                "query": query,
                "size": 200,
                "sort": [{"created_at": "desc"}]
            }
        )

        incidents = [hit["_source"] for hit in resp["hits"]["hits"]]

        # Build connections from incidents with multiple related assets
        connections = []
        seen_pairs = set()

        connection_types = ["lateral_movement", "c2_communication", "data_exfil", "shared_ioc"]

        for incident in incidents:
            related = incident.get("related_assets", [])
            if not related or len(related) < 2:
                continue

            severity = incident.get("severity", "Medium")
            strength_map = {"Critical": 1.0, "High": 0.8, "Medium": 0.5, "Low": 0.3}
            strength = strength_map.get(severity, 0.5)

            # Determine connection type based on incident title/description
            title = (incident.get("title", "") or "").lower()
            if "lateral" in title or "movement" in title:
                conn_type = "lateral_movement"
            elif "c2" in title or "command" in title or "beacon" in title:
                conn_type = "c2_communication"
            elif "exfil" in title or "data" in title:
                conn_type = "data_exfil"
            else:
                conn_type = "shared_ioc"

            if type and conn_type != type:
                continue

            # Create pairwise connections
            for i in range(len(related)):
                for j in range(i + 1, len(related)):
                    pair_key = tuple(sorted([related[i], related[j]]))
                    if pair_key in seen_pairs:
                        continue
                    seen_pairs.add(pair_key)

                    connections.append({
                        "source_id": related[i],
                        "target_id": related[j],
                        "type": conn_type,
                        "strength": strength,
                        "timestamp": incident.get("created_at", ""),
                    })

        return ConnectionList(connections=connections)

    except Exception:
        return ConnectionList(connections=[])
