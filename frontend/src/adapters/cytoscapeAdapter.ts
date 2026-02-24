/**
 * Cytoscape.js Graph Adapter
 *
 * TECH-005: Standard interface for attack visualization
 * Converts simulation events to Cytoscape graph format
 */

import type { GraphData, CytoscapeNode, CytoscapeEdge, NodeColor } from '../components/Graph/types';

export interface SimulationEvent {
  type: 'node_add' | 'node_update' | 'edge_add' | 'phase_change';
  nodeId?: string;
  label?: string;
  nodeType?: 'incident' | 'detection' | 'asset' | 'process' | 'hash';
  color?: NodeColor;
  metadata?: Record<string, unknown>;
  sourceId?: string;
  targetId?: string;
  relation?: string;
  phase?: number;
}

export interface CytoscapeAdapter {
  getGraphData: () => GraphData;
  applyEvent: (event: SimulationEvent) => GraphData;
  reset: () => void;
  addNode: (node: CytoscapeNode) => void;
  addEdge: (edge: CytoscapeEdge) => void;
  updateNodeColor: (nodeId: string, color: NodeColor) => void;
  removeNode: (nodeId: string) => void;
}

export function createCytoscapeAdapter(): CytoscapeAdapter {
  let nodes: CytoscapeNode[] = [];
  let edges: CytoscapeEdge[] = [];

  const getGraphData = (): GraphData => ({
    nodes: [...nodes],
    edges: [...edges],
  });

  const addNode = (node: CytoscapeNode): void => {
    const exists = nodes.some((n) => n.data.id === node.data.id);
    if (!exists) {
      nodes = [...nodes, node];
    }
  };

  const addEdge = (edge: CytoscapeEdge): void => {
    const exists = edges.some((e) => e.data.id === edge.data.id);
    if (!exists) {
      edges = [...edges, edge];
    }
  };

  const updateNodeColor = (nodeId: string, color: NodeColor): void => {
    nodes = nodes.map((n) =>
      n.data.id === nodeId ? { ...n, data: { ...n.data, color } } : n
    );
  };

  const removeNode = (nodeId: string): void => {
    nodes = nodes.filter((n) => n.data.id !== nodeId);
    edges = edges.filter((e) => e.data.source !== nodeId && e.data.target !== nodeId);
  };

  const reset = (): void => {
    nodes = [];
    edges = [];
  };

  const applyEvent = (event: SimulationEvent): GraphData => {
    switch (event.type) {
      case 'node_add':
        if (event.nodeId) {
          addNode({
            data: {
              id: event.nodeId,
              label: event.label ?? event.nodeId,
              type: event.nodeType ?? 'asset',
              color: event.color ?? 'blue',
              metadata: event.metadata,
            },
          });
        }
        break;

      case 'node_update':
        if (event.nodeId && event.color) {
          updateNodeColor(event.nodeId, event.color);
        }
        break;

      case 'edge_add':
        if (event.sourceId && event.targetId) {
          addEdge({
            data: {
              id: `${event.sourceId}-${event.targetId}`,
              source: event.sourceId,
              target: event.targetId,
              relation: event.relation ?? 'related',
            },
          });
        }
        break;

      case 'phase_change':
        // Phase change events are handled by the simulation state, not the graph
        break;
    }

    return getGraphData();
  };

  return { getGraphData, applyEvent, reset, addNode, addEdge, updateNodeColor, removeNode };
}
