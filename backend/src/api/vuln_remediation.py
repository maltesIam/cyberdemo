"""Vulnerability Remediation API endpoints for remediation stats and flow visualization."""
from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(tags=["Vulnerabilities"])


class RemediationStats(BaseModel):
    """Response model for remediation statistics."""

    total_open: int = 0
    in_progress: int = 0
    remediated: int = 0
    accepted_risk: int = 0
    false_positive: int = 0
    by_severity: dict = {}
    mttr_days: dict = {}
    sla_compliance: dict = {}
    remediated_last_7_days: int = 0
    remediated_last_30_days: int = 0


class SankeyNode(BaseModel):
    """Node in Sankey diagram."""

    id: str
    name: str


class SankeyLink(BaseModel):
    """Link in Sankey diagram."""

    source: str
    target: str
    value: int


class SankeyFlow(BaseModel):
    """Response model for Sankey flow visualization."""

    nodes: list[dict] = []
    links: list[dict] = []


# Predefined nodes for the remediation workflow
WORKFLOW_NODES = [
    {"id": "discovered", "name": "Discovered"},
    {"id": "triaged", "name": "Triaged"},
    {"id": "assigned", "name": "Assigned"},
    {"id": "in_progress", "name": "In Progress"},
    {"id": "remediated", "name": "Remediated"},
    {"id": "verified", "name": "Verified"},
    {"id": "accepted_risk", "name": "Accepted Risk"},
    {"id": "false_positive", "name": "False Positive"},
]


@router.get("/remediation/stats", response_model=RemediationStats)
async def get_remediation_stats():
    """Get remediation statistics for vulnerabilities."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="ctem-findings-v1",
            body={
                "size": 0,
                "aggs": {
                    "by_status": {"terms": {"field": "status"}},
                    "by_severity_status": {
                        "terms": {"field": "severity"},
                        "aggs": {
                            "status_breakdown": {"terms": {"field": "status"}}
                        },
                    },
                    "mttr_by_severity": {
                        "terms": {"field": "severity"},
                        "aggs": {
                            "avg_remediation_days": {"avg": {"field": "remediation_days"}}
                        },
                    },
                    "sla_compliance": {"terms": {"field": "sla_status"}},
                    "remediated_last_7_days": {
                        "filter": {
                            "bool": {
                                "must": [
                                    {"term": {"status": "remediated"}},
                                    {"range": {"remediated_at": {"gte": "now-7d"}}},
                                ]
                            }
                        }
                    },
                    "remediated_last_30_days": {
                        "filter": {
                            "bool": {
                                "must": [
                                    {"term": {"status": "remediated"}},
                                    {"range": {"remediated_at": {"gte": "now-30d"}}},
                                ]
                            }
                        }
                    },
                },
            },
        )

        aggs = response.get("aggregations", {})

        # Parse status counts
        status_counts = {
            b["key"]: b["doc_count"]
            for b in aggs.get("by_status", {}).get("buckets", [])
        }

        # Parse severity breakdown
        by_severity = {}
        for bucket in aggs.get("by_severity_status", {}).get("buckets", []):
            severity = bucket["key"]
            status_breakdown = {
                sb["key"]: sb["doc_count"]
                for sb in bucket.get("status_breakdown", {}).get("buckets", [])
            }
            by_severity[severity] = {
                "open": status_breakdown.get("open", 0),
                "remediated": status_breakdown.get("remediated", 0),
            }

        # Parse MTTR by severity
        mttr_days = {}
        for bucket in aggs.get("mttr_by_severity", {}).get("buckets", []):
            severity = bucket["key"]
            avg_days = bucket.get("avg_remediation_days", {}).get("value")
            if avg_days is not None:
                mttr_days[severity] = round(avg_days, 1)

        # Parse SLA compliance
        sla_compliance = {
            b["key"]: b["doc_count"]
            for b in aggs.get("sla_compliance", {}).get("buckets", [])
        }

        # Parse time-based metrics
        remediated_7d = aggs.get("remediated_last_7_days", {}).get("doc_count", 0)
        remediated_30d = aggs.get("remediated_last_30_days", {}).get("doc_count", 0)

        return RemediationStats(
            total_open=status_counts.get("open", 0),
            in_progress=status_counts.get("in_progress", 0),
            remediated=status_counts.get("remediated", 0),
            accepted_risk=status_counts.get("accepted_risk", 0),
            false_positive=status_counts.get("false_positive", 0),
            by_severity=by_severity,
            mttr_days=mttr_days,
            sla_compliance=sla_compliance,
            remediated_last_7_days=remediated_7d,
            remediated_last_30_days=remediated_30d,
        )
    except Exception:
        return RemediationStats()


@router.get("/remediation/flow", response_model=SankeyFlow)
async def get_remediation_flow():
    """Get Sankey flow data for remediation visualization."""
    from ..opensearch.client import get_opensearch_client

    client = await get_opensearch_client()

    try:
        response = await client.search(
            index="ctem-findings-v1",
            body={
                "size": 0,
                "aggs": {
                    "flow_transitions": {
                        "terms": {"field": "current_status"},
                        "aggs": {
                            "next_status": {"terms": {"field": "next_status"}}
                        },
                    }
                },
            },
        )

        aggs = response.get("aggregations", {})

        # Build links from aggregation buckets
        links = []
        for bucket in aggs.get("flow_transitions", {}).get("buckets", []):
            source = bucket["key"]
            for next_bucket in bucket.get("next_status", {}).get("buckets", []):
                target = next_bucket["key"]
                value = next_bucket["doc_count"]
                links.append({"source": source, "target": target, "value": value})

        return SankeyFlow(nodes=WORKFLOW_NODES, links=links)
    except Exception:
        return SankeyFlow(nodes=WORKFLOW_NODES, links=[])
