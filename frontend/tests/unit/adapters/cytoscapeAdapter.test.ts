/**
 * Tests for Cytoscape adapter
 * UT-TECH-005: Standard interface for attack visualization
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { createCytoscapeAdapter, type CytoscapeAdapter } from '../../../src/adapters/cytoscapeAdapter';

describe('cytoscapeAdapter', () => {
  let adapter: CytoscapeAdapter;

  beforeEach(() => {
    adapter = createCytoscapeAdapter();
  });

  it('should start with empty graph data', () => {
    const data = adapter.getGraphData();
    expect(data.nodes).toEqual([]);
    expect(data.edges).toEqual([]);
  });

  it('should add a node', () => {
    adapter.addNode({
      data: { id: 'n1', label: 'Server', type: 'asset', color: 'blue' },
    });
    const data = adapter.getGraphData();
    expect(data.nodes).toHaveLength(1);
    expect(data.nodes[0].data.id).toBe('n1');
  });

  it('should not add duplicate nodes', () => {
    adapter.addNode({
      data: { id: 'n1', label: 'Server', type: 'asset', color: 'blue' },
    });
    adapter.addNode({
      data: { id: 'n1', label: 'Server 2', type: 'asset', color: 'red' },
    });
    const data = adapter.getGraphData();
    expect(data.nodes).toHaveLength(1);
  });

  it('should add an edge', () => {
    adapter.addNode({
      data: { id: 'n1', label: 'A', type: 'asset', color: 'blue' },
    });
    adapter.addNode({
      data: { id: 'n2', label: 'B', type: 'detection', color: 'red' },
    });
    adapter.addEdge({
      data: { id: 'e1', source: 'n1', target: 'n2', relation: 'detected_by' },
    });
    const data = adapter.getGraphData();
    expect(data.edges).toHaveLength(1);
    expect(data.edges[0].data.relation).toBe('detected_by');
  });

  it('should not add duplicate edges', () => {
    adapter.addEdge({
      data: { id: 'e1', source: 'n1', target: 'n2', relation: 'a' },
    });
    adapter.addEdge({
      data: { id: 'e1', source: 'n1', target: 'n2', relation: 'b' },
    });
    const data = adapter.getGraphData();
    expect(data.edges).toHaveLength(1);
  });

  it('should update node color', () => {
    adapter.addNode({
      data: { id: 'n1', label: 'Server', type: 'asset', color: 'blue' },
    });
    adapter.updateNodeColor('n1', 'red');
    const data = adapter.getGraphData();
    expect(data.nodes[0].data.color).toBe('red');
  });

  it('should remove node and associated edges', () => {
    adapter.addNode({
      data: { id: 'n1', label: 'A', type: 'asset', color: 'blue' },
    });
    adapter.addNode({
      data: { id: 'n2', label: 'B', type: 'asset', color: 'blue' },
    });
    adapter.addEdge({
      data: { id: 'e1', source: 'n1', target: 'n2', relation: 'r' },
    });

    adapter.removeNode('n1');
    const data = adapter.getGraphData();
    expect(data.nodes).toHaveLength(1);
    expect(data.edges).toHaveLength(0);
  });

  it('should reset graph data', () => {
    adapter.addNode({
      data: { id: 'n1', label: 'A', type: 'asset', color: 'blue' },
    });
    adapter.reset();
    const data = adapter.getGraphData();
    expect(data.nodes).toEqual([]);
    expect(data.edges).toEqual([]);
  });

  it('should apply node_add event', () => {
    adapter.applyEvent({
      type: 'node_add',
      nodeId: 'srv-1',
      label: 'Server 1',
      nodeType: 'asset',
      color: 'blue',
    });
    const data = adapter.getGraphData();
    expect(data.nodes).toHaveLength(1);
    expect(data.nodes[0].data.label).toBe('Server 1');
  });

  it('should apply node_update event', () => {
    adapter.applyEvent({
      type: 'node_add',
      nodeId: 'srv-1',
      label: 'Server 1',
      nodeType: 'asset',
      color: 'blue',
    });
    adapter.applyEvent({
      type: 'node_update',
      nodeId: 'srv-1',
      color: 'red',
    });
    const data = adapter.getGraphData();
    expect(data.nodes[0].data.color).toBe('red');
  });

  it('should apply edge_add event', () => {
    adapter.applyEvent({
      type: 'node_add',
      nodeId: 'n1',
      label: 'A',
      nodeType: 'asset',
      color: 'blue',
    });
    adapter.applyEvent({
      type: 'node_add',
      nodeId: 'n2',
      label: 'B',
      nodeType: 'detection',
      color: 'red',
    });
    adapter.applyEvent({
      type: 'edge_add',
      sourceId: 'n1',
      targetId: 'n2',
      relation: 'triggered',
    });
    const data = adapter.getGraphData();
    expect(data.edges).toHaveLength(1);
    expect(data.edges[0].data.relation).toBe('triggered');
  });

  it('should handle phase_change event without error', () => {
    const data = adapter.applyEvent({ type: 'phase_change', phase: 3 });
    expect(data.nodes).toEqual([]);
    expect(data.edges).toEqual([]);
  });

  it('should return immutable graph data copies', () => {
    adapter.addNode({
      data: { id: 'n1', label: 'A', type: 'asset', color: 'blue' },
    });
    const data1 = adapter.getGraphData();
    const data2 = adapter.getGraphData();
    expect(data1).not.toBe(data2);
    expect(data1.nodes).not.toBe(data2.nodes);
  });
});
