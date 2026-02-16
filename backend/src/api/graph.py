"""
Graph API Endpoints for Cytoscape.js visualization.

Provides REST API for retrieving graph data in Cytoscape-compatible format.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from ..services.graph_service import get_graph_service

router = APIRouter()


# ============================================================================
# Response Models
# ============================================================================

class NodeData(BaseModel):
    """Cytoscape node data."""
    id: str
    label: str
    type: str
    color: Optional[str] = None

    class Config:
        extra = "allow"  # Allow additional fields


class EdgeData(BaseModel):
    """Cytoscape edge data."""
    source: str
    target: str
    relation: str

    class Config:
        extra = "allow"


class CytoscapeNode(BaseModel):
    """Cytoscape node format."""
    data: Dict[str, Any]


class CytoscapeEdge(BaseModel):
    """Cytoscape edge format."""
    data: Dict[str, Any]


class GraphResponse(BaseModel):
    """Response model for graph data."""
    nodes: List[CytoscapeNode]
    edges: List[CytoscapeEdge]
    incident_id: Optional[str] = None


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/incident/{incident_id}", response_model=GraphResponse)
async def get_incident_graph(incident_id: str) -> GraphResponse:
    """
    Get graph data for a specific incident.

    Returns nodes and edges in Cytoscape.js format for visualization:
    - **nodes**: Incident, detections, assets, processes, hashes
    - **edges**: Relationships between nodes

    Node colors indicate risk/status:
    - Green: Normal/Low risk
    - Yellow: Medium risk
    - Red: High/Critical risk
    - Blue: Contained/Isolated
    """
    service = get_graph_service()
    result = await service.build_incident_graph(incident_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Incident not found: {incident_id}"
        )

    return GraphResponse(**result)


@router.get("/system", response_model=GraphResponse)
async def get_system_graph(
    limit: int = Query(50, ge=1, le=500, description="Maximum nodes to return")
) -> GraphResponse:
    """
    Get system overview graph.

    Returns a high-level graph showing:
    - Data sources (SIEM, EDR, Intel)
    - Recent incidents
    - Affected assets

    Useful for dashboard visualization.
    """
    service = get_graph_service()
    result = await service.build_system_graph(limit=limit)

    return GraphResponse(**result)
