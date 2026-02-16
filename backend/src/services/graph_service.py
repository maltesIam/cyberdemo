"""
Graph Service for Cytoscape.js visualization.

Provides graph data in Cytoscape-compatible format for visualizing
incidents, assets, detections, and their relationships.
"""

from typing import Optional, List, Dict, Any


def node_to_cytoscape(
    id: str,
    label: str,
    node_type: str,
    data: Optional[Dict[str, Any]] = None,
    color: Optional[str] = None
) -> Dict[str, Any]:
    """Convert node data to Cytoscape format.

    Args:
        id: Unique node identifier
        label: Display label
        node_type: Node type (incident, detection, asset, process, hash, user)
        data: Additional data to include
        color: Node color (optional)

    Returns:
        Cytoscape-formatted node
    """
    node_data = {
        "id": id,
        "label": label,
        "type": node_type,
    }

    if color:
        node_data["color"] = color

    if data:
        node_data.update(data)

    return {"data": node_data}


def edge_to_cytoscape(
    source: str,
    target: str,
    relation: str,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convert edge data to Cytoscape format.

    Args:
        source: Source node ID
        target: Target node ID
        relation: Relationship type
        data: Additional data to include

    Returns:
        Cytoscape-formatted edge
    """
    edge_data = {
        "source": source,
        "target": target,
        "relation": relation,
    }

    if data:
        edge_data.update(data)

    return {"data": edge_data}


def risk_to_color(risk: str) -> str:
    """Map risk level to display color.

    Args:
        risk: Risk level or status

    Returns:
        Color string for display
    """
    mapping = {
        "green": "green",
        "Green": "green",
        "low": "green",
        "normal": "green",
        "yellow": "yellow",
        "Yellow": "yellow",
        "medium": "yellow",
        "warning": "yellow",
        "red": "red",
        "Red": "red",
        "high": "red",
        "critical": "red",
        "blue": "blue",
        "contained": "blue",
        "isolated": "blue",
    }
    return mapping.get(risk, "gray")


class GraphService:
    """Service for building graph visualizations."""

    def __init__(self, opensearch_client=None):
        """Initialize graph service.

        Args:
            opensearch_client: Optional OpenSearch client for data retrieval
        """
        self.os_client = opensearch_client

        # Mock data for demo - in production, this comes from OpenSearch
        self._incidents = {
            "INC-ANCHOR-001": {
                "incident_id": "INC-ANCHOR-001",
                "title": "Malware Detection - WS-FIN-042",
                "severity": "critical",
                "status": "open",
                "detection_ids": ["DET-001"],
                "asset_ids": ["ASSET-WS-FIN-042"],
            },
            "INC-ANCHOR-002": {
                "incident_id": "INC-ANCHOR-002",
                "title": "Suspicious Activity - LAPTOP-CFO-01",
                "severity": "high",
                "status": "pending_approval",
                "detection_ids": ["DET-002"],
                "asset_ids": ["ASSET-LAPTOP-CFO-01"],
            },
            "INC-ANCHOR-003": {
                "incident_id": "INC-ANCHOR-003",
                "title": "Script Execution - SRV-DEV-03",
                "severity": "low",
                "status": "closed",
                "detection_ids": ["DET-003"],
                "asset_ids": ["ASSET-SRV-DEV-03"],
            },
        }

        self._detections = {
            "DET-001": {
                "detection_id": "DET-001",
                "technique_id": "T1059.001",
                "process_hash": "abc123def456",
                "asset_id": "ASSET-WS-FIN-042",
                "severity": "critical",
            },
            "DET-002": {
                "detection_id": "DET-002",
                "technique_id": "T1003",
                "process_hash": "abc123def456",
                "asset_id": "ASSET-LAPTOP-CFO-01",
                "severity": "high",
            },
            "DET-003": {
                "detection_id": "DET-003",
                "technique_id": "T1059.001",
                "process_hash": "xyz789",
                "asset_id": "ASSET-SRV-DEV-03",
                "severity": "low",
            },
        }

        self._assets = {
            "ASSET-WS-FIN-042": {
                "asset_id": "ASSET-WS-FIN-042",
                "hostname": "WS-FIN-042",
                "risk_color": "Red",
                "tags": ["standard-user", "finance"],
                "containment": "normal",
            },
            "ASSET-LAPTOP-CFO-01": {
                "asset_id": "ASSET-LAPTOP-CFO-01",
                "hostname": "LAPTOP-CFO-01",
                "risk_color": "Red",
                "tags": ["vip", "executive"],
                "containment": "normal",
            },
            "ASSET-SRV-DEV-03": {
                "asset_id": "ASSET-SRV-DEV-03",
                "hostname": "SRV-DEV-03",
                "risk_color": "Green",
                "tags": ["server", "development"],
                "containment": "normal",
            },
        }

    async def build_incident_graph(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Build a graph for a specific incident.

        Args:
            incident_id: The incident identifier

        Returns:
            Dict with nodes and edges in Cytoscape format, or None if not found
        """
        incident = self._incidents.get(incident_id)
        if not incident:
            return None

        nodes = []
        edges = []

        # Add incident node
        nodes.append(node_to_cytoscape(
            id=incident_id,
            label=incident["title"],
            node_type="incident",
            color=risk_to_color(incident["severity"])
        ))

        # Add detection nodes and edges
        for det_id in incident.get("detection_ids", []):
            detection = self._detections.get(det_id, {})
            nodes.append(node_to_cytoscape(
                id=det_id,
                label=f"Detection: {detection.get('technique_id', 'Unknown')}",
                node_type="detection",
                color=risk_to_color(detection.get("severity", "medium"))
            ))
            edges.append(edge_to_cytoscape(
                source=incident_id,
                target=det_id,
                relation="triggered_by"
            ))

            # Add hash node
            hash_value = detection.get("process_hash")
            if hash_value:
                hash_id = f"hash-{hash_value[:8]}"
                if not any(n["data"]["id"] == hash_id for n in nodes):
                    nodes.append(node_to_cytoscape(
                        id=hash_id,
                        label=f"Hash: {hash_value[:8]}...",
                        node_type="hash",
                        color="orange"
                    ))
                edges.append(edge_to_cytoscape(
                    source=det_id,
                    target=hash_id,
                    relation="process_hash"
                ))

        # Add asset nodes and edges
        for asset_id in incident.get("asset_ids", []):
            asset = self._assets.get(asset_id, {})
            containment = asset.get("containment", "normal")
            if containment == "contained":
                color = "blue"
            else:
                color = risk_to_color(asset.get("risk_color", "green"))

            nodes.append(node_to_cytoscape(
                id=asset_id,
                label=asset.get("hostname", asset_id),
                node_type="asset",
                color=color,
                data={
                    "tags": asset.get("tags", []),
                    "risk": asset.get("risk_color", "green"),
                }
            ))

            # Connect detections to assets
            for det_id in incident.get("detection_ids", []):
                det = self._detections.get(det_id, {})
                if det.get("asset_id") == asset_id:
                    edges.append(edge_to_cytoscape(
                        source=det_id,
                        target=asset_id,
                        relation="detected_on"
                    ))

        return {
            "nodes": nodes,
            "edges": edges,
            "incident_id": incident_id,
        }

    async def build_system_graph(self, limit: int = 50) -> Dict[str, Any]:
        """Build an overview graph of the system.

        Args:
            limit: Maximum number of nodes to include

        Returns:
            Dict with nodes and edges in Cytoscape format
        """
        nodes = []
        edges = []

        # Add source nodes (simulated data sources)
        sources = [
            ("source-siem", "SIEM", "source"),
            ("source-edr", "EDR", "source"),
            ("source-intel", "Intel", "source"),
        ]

        for src_id, label, stype in sources:
            nodes.append(node_to_cytoscape(
                id=src_id,
                label=label,
                node_type=stype,
                color="purple"
            ))

        # Add incident nodes
        for inc_id, incident in list(self._incidents.items())[:limit]:
            nodes.append(node_to_cytoscape(
                id=inc_id,
                label=incident["title"][:30],
                node_type="incident",
                color=risk_to_color(incident["severity"])
            ))
            # Connect to sources
            edges.append(edge_to_cytoscape(
                source="source-siem",
                target=inc_id,
                relation="reported"
            ))

            # Add connected assets
            for asset_id in incident.get("asset_ids", []):
                asset = self._assets.get(asset_id, {})
                if not any(n["data"]["id"] == asset_id for n in nodes):
                    nodes.append(node_to_cytoscape(
                        id=asset_id,
                        label=asset.get("hostname", asset_id),
                        node_type="asset",
                        color=risk_to_color(asset.get("risk_color", "green"))
                    ))
                edges.append(edge_to_cytoscape(
                    source=inc_id,
                    target=asset_id,
                    relation="affects"
                ))

        return {
            "nodes": nodes,
            "edges": edges,
        }


# Singleton instance
_service_instance: Optional[GraphService] = None


def get_graph_service() -> GraphService:
    """Get or create the Graph service singleton."""
    global _service_instance
    if _service_instance is None:
        _service_instance = GraphService()
    return _service_instance
