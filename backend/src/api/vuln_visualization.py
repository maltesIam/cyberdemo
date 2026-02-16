"""Vulnerability Visualization API endpoints for dashboard visualizations.

Provides endpoints for:
- Overview KPIs (bottom bar)
- Risk Terrain visualization
- Calendar Heatmap
- CWE Sunburst
- Priority Bubbles
- Temporal Trends
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional


router = APIRouter(tags=["Vulnerability Visualization"])


# ============================================================================
# Response Models
# ============================================================================


class OverviewResponse(BaseModel):
    """Response model for vulnerability overview KPIs."""
    total_cves: int = 0
    critical_count: int = 0
    high_count: int = 0
    kev_count: int = 0
    avg_risk_score: float = 0.0
    act_count: int = 0
    attend_count: int = 0
    remediated_last_7d: int = 0


class TerrainCell(BaseModel):
    """Single cell in the risk terrain grid."""
    x: int
    y: int
    risk_score: float
    cve_count: int
    severity: str


class TerrainResponse(BaseModel):
    """Response model for risk terrain visualization."""
    cells: list[TerrainCell] = []
    x_axis: list[str] = ["Low", "Medium", "High", "Critical"]
    y_axis: list[str] = ["none", "poc", "active"]


class HeatmapItem(BaseModel):
    """Single data point in the calendar heatmap."""
    date: str
    count: int
    max_severity: str


class HeatmapResponse(BaseModel):
    """Response model for calendar heatmap visualization."""
    data: list[HeatmapItem] = []


class SunburstChild(BaseModel):
    """Child node in sunburst hierarchy."""
    name: str
    value: int
    children: list["SunburstChild"] = []


class SunburstResponse(BaseModel):
    """Response model for CWE sunburst visualization."""
    name: str = "CWEs"
    children: list[SunburstChild] = []


class BubbleItem(BaseModel):
    """Single bubble in the priority bubbles visualization."""
    cve_id: str
    risk_score: float
    severity: str
    radius: float
    color: str


class BubblesResponse(BaseModel):
    """Response model for priority bubbles visualization."""
    bubbles: list[BubbleItem] = []


class TrendItem(BaseModel):
    """Single data point in trends."""
    date: str
    count: int


class TrendsResponse(BaseModel):
    """Response model for temporal trends visualization."""
    data: list[TrendItem] = []


# ============================================================================
# Helper Functions
# ============================================================================


def get_severity_color(severity: str) -> str:
    """Return color hex code for severity level."""
    colors = {
        "Critical": "#FF0000",
        "High": "#FF6600",
        "Medium": "#FFCC00",
        "Low": "#00CC00",
    }
    return colors.get(severity, "#999999")


def calculate_bubble_radius(risk_score: float, min_radius: float = 10, max_radius: float = 50) -> float:
    """Calculate bubble radius based on risk score (0-100)."""
    # Scale risk score to radius range
    return min_radius + (risk_score / 100) * (max_radius - min_radius)


# ============================================================================
# Endpoints
# ============================================================================


@router.get("/overview", response_model=OverviewResponse)
async def get_vulnerabilities_overview():
    """
    Get vulnerability overview KPIs for the bottom bar.

    Returns:
        OverviewResponse with total_cves, critical_count, high_count,
        kev_count, avg_risk_score, act_count, attend_count, remediated_last_7d
    """
    from ..opensearch.client import get_opensearch_client

    try:
        client = await get_opensearch_client()

        response = await client.search(
            index="ctem-findings-v1",
            body={
                "size": 0,
                "aggs": {
                    "critical_count": {
                        "filter": {"term": {"severity": "Critical"}}
                    },
                    "high_count": {
                        "filter": {"term": {"severity": "High"}}
                    },
                    "kev_count": {
                        "filter": {"term": {"in_kev": True}}
                    },
                    "avg_risk_score": {
                        "avg": {"field": "risk_score"}
                    },
                    "act_count": {
                        "filter": {"term": {"ssvc_decision": "Act"}}
                    },
                    "attend_count": {
                        "filter": {"term": {"ssvc_decision": "Attend"}}
                    },
                    "remediated_last_7d": {
                        "filter": {
                            "bool": {
                                "must": [
                                    {"term": {"status": "remediated"}},
                                    {"range": {"remediated_at": {"gte": "now-7d/d"}}}
                                ]
                            }
                        }
                    },
                }
            }
        )

        total_cves = response["hits"]["total"]["value"]
        aggs = response["aggregations"]

        return OverviewResponse(
            total_cves=total_cves,
            critical_count=aggs["critical_count"]["doc_count"],
            high_count=aggs["high_count"]["doc_count"],
            kev_count=aggs["kev_count"]["doc_count"],
            avg_risk_score=round(aggs["avg_risk_score"]["value"] or 0.0, 2),
            act_count=aggs["act_count"]["doc_count"],
            attend_count=aggs["attend_count"]["doc_count"],
            remediated_last_7d=aggs["remediated_last_7d"]["doc_count"],
        )
    except Exception:
        return OverviewResponse()


@router.get("/terrain", response_model=TerrainResponse)
async def get_vulnerabilities_terrain():
    """
    Get risk terrain data for terrain visualization.

    Returns terrain cells grouped by severity (x-axis) and exploitation status (y-axis).
    Each cell contains risk score average and CVE count.
    """
    from ..opensearch.client import get_opensearch_client

    try:
        client = await get_opensearch_client()

        response = await client.search(
            index="ctem-findings-v1",
            body={
                "size": 0,
                "aggs": {
                    "by_severity": {
                        "terms": {"field": "severity", "size": 10},
                        "aggs": {
                            "by_exploitation": {
                                "terms": {"field": "exploitation_status", "size": 10},
                                "aggs": {
                                    "avg_risk": {"avg": {"field": "risk_score"}}
                                }
                            }
                        }
                    }
                }
            }
        )

        x_axis = ["Low", "Medium", "High", "Critical"]
        y_axis = ["none", "poc", "active"]

        cells = []
        severity_buckets = response["aggregations"]["by_severity"]["buckets"]

        for severity_bucket in severity_buckets:
            severity = severity_bucket["key"]
            x_idx = x_axis.index(severity) if severity in x_axis else -1

            if x_idx == -1:
                continue

            exploitation_buckets = severity_bucket["by_exploitation"]["buckets"]
            for exp_bucket in exploitation_buckets:
                exploitation = exp_bucket["key"]
                y_idx = y_axis.index(exploitation) if exploitation in y_axis else -1

                if y_idx == -1:
                    continue

                cells.append(TerrainCell(
                    x=x_idx,
                    y=y_idx,
                    risk_score=round(exp_bucket["avg_risk"]["value"] or 0.0, 2),
                    cve_count=exp_bucket["doc_count"],
                    severity=severity,
                ))

        return TerrainResponse(cells=cells, x_axis=x_axis, y_axis=y_axis)
    except Exception:
        return TerrainResponse()


@router.get("/heatmap", response_model=HeatmapResponse)
async def get_vulnerabilities_heatmap():
    """
    Get calendar heatmap data for CVEs by date.

    Returns data points for each date with CVE count and max severity.
    """
    from ..opensearch.client import get_opensearch_client

    try:
        client = await get_opensearch_client()

        response = await client.search(
            index="ctem-findings-v1",
            body={
                "size": 0,
                "aggs": {
                    "by_date": {
                        "date_histogram": {
                            "field": "discovered_at",
                            "calendar_interval": "day",
                            "format": "yyyy-MM-dd"
                        },
                        "aggs": {
                            "max_severity": {
                                "terms": {
                                    "field": "severity",
                                    "size": 1,
                                    "order": {"_key": "desc"}
                                }
                            }
                        }
                    }
                }
            }
        )

        data = []
        date_buckets = response["aggregations"]["by_date"]["buckets"]

        for bucket in date_buckets:
            max_severity = "Low"
            severity_buckets = bucket.get("max_severity", {}).get("buckets", [])
            if severity_buckets:
                max_severity = severity_buckets[0]["key"]

            data.append(HeatmapItem(
                date=bucket["key_as_string"],
                count=bucket["doc_count"],
                max_severity=max_severity,
            ))

        return HeatmapResponse(data=data)
    except Exception:
        return HeatmapResponse()


@router.get("/sunburst", response_model=SunburstResponse)
async def get_vulnerabilities_sunburst():
    """
    Get CWE sunburst data for hierarchical CWE visualization.

    Returns hierarchical structure with CWE categories as first level
    and individual CWEs as second level.
    """
    from ..opensearch.client import get_opensearch_client

    try:
        client = await get_opensearch_client()

        response = await client.search(
            index="ctem-findings-v1",
            body={
                "size": 0,
                "aggs": {
                    "by_cwe_category": {
                        "terms": {"field": "cwe_category", "size": 20},
                        "aggs": {
                            "by_cwe": {
                                "terms": {"field": "cwe_id", "size": 20}
                            }
                        }
                    }
                }
            }
        )

        children = []
        category_buckets = response["aggregations"]["by_cwe_category"]["buckets"]

        for cat_bucket in category_buckets:
            cwe_children = []
            cwe_buckets = cat_bucket["by_cwe"]["buckets"]

            for cwe_bucket in cwe_buckets:
                cwe_children.append(SunburstChild(
                    name=cwe_bucket["key"],
                    value=cwe_bucket["doc_count"],
                    children=[],
                ))

            children.append(SunburstChild(
                name=cat_bucket["key"],
                value=cat_bucket["doc_count"],
                children=cwe_children,
            ))

        return SunburstResponse(name="CWEs", children=children)
    except Exception:
        return SunburstResponse()


@router.get("/bubbles", response_model=BubblesResponse)
async def get_vulnerabilities_bubbles(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of bubbles to return"),
):
    """
    Get priority bubbles data for bubble visualization.

    Returns bubbles sized by risk score and colored by severity.
    """
    from ..opensearch.client import get_opensearch_client

    try:
        client = await get_opensearch_client()

        response = await client.search(
            index="ctem-findings-v1",
            body={
                "size": limit,
                "sort": [{"risk_score": "desc"}],
                "_source": ["cve_id", "risk_score", "severity", "title"],
            }
        )

        bubbles = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            risk_score = source.get("risk_score", 0) or 0
            severity = source.get("severity", "Low")

            bubbles.append(BubbleItem(
                cve_id=source.get("cve_id", "Unknown"),
                risk_score=risk_score,
                severity=severity,
                radius=calculate_bubble_radius(risk_score),
                color=get_severity_color(severity),
            ))

        return BubblesResponse(bubbles=bubbles)
    except Exception:
        return BubblesResponse()


@router.get("/trends", response_model=TrendsResponse)
async def get_vulnerabilities_trends(
    interval: str = Query("week", description="Time interval: day, week, month"),
):
    """
    Get temporal trends data for CVE counts over time.

    Args:
        interval: Time bucket interval (day, week, month)
    """
    from ..opensearch.client import get_opensearch_client

    try:
        client = await get_opensearch_client()

        # Map interval to calendar_interval
        interval_map = {
            "day": "day",
            "week": "week",
            "month": "month",
        }
        calendar_interval = interval_map.get(interval, "week")

        response = await client.search(
            index="ctem-findings-v1",
            body={
                "size": 0,
                "aggs": {
                    "by_date": {
                        "date_histogram": {
                            "field": "discovered_at",
                            "calendar_interval": calendar_interval,
                            "format": "yyyy-MM-dd"
                        }
                    }
                }
            }
        )

        data = []
        date_buckets = response["aggregations"]["by_date"]["buckets"]

        for bucket in date_buckets:
            data.append(TrendItem(
                date=bucket["key_as_string"],
                count=bucket["doc_count"],
            ))

        return TrendsResponse(data=data)
    except Exception:
        return TrendsResponse()
