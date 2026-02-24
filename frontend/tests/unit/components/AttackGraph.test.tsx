/**
 * Tests for AttackGraph Component
 * UT-034: Renders Cytoscape canvas with nodes/edges
 * UT-038: Visualization updates from WebSocket events
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AttackGraph } from '../../../src/components/demo/AttackGraph';
import type { GraphData } from '../../../src/components/Graph/types';

// Mock cytoscape since it needs a real DOM canvas
vi.mock('cytoscape', () => ({
  default: vi.fn(() => ({
    on: vi.fn(),
    destroy: vi.fn(),
    getElementById: vi.fn(() => ({ length: 0 })),
    add: vi.fn(),
    layout: vi.fn(() => ({ run: vi.fn() })),
  })),
}));

const emptyGraph: GraphData = { nodes: [], edges: [] };

const graphWithData: GraphData = {
  nodes: [
    { data: { id: 'node-1', label: 'WS-FIN-042', type: 'asset', color: '#06b6d4' } },
    { data: { id: 'node-2', label: 'Malware.exe', type: 'incident', color: '#ef4444' } },
  ],
  edges: [
    { data: { id: 'edge-1', source: 'node-1', target: 'node-2', label: 'compromised' } },
  ],
};

describe('UT-034: AttackGraph renders Cytoscape canvas', () => {
  it('should render the graph container', () => {
    render(<AttackGraph graphData={emptyGraph} />);
    expect(screen.getByTestId('attack-graph')).toBeInTheDocument();
  });

  it('should render cytoscape container', () => {
    render(<AttackGraph graphData={emptyGraph} />);
    expect(screen.getByTestId('cytoscape-container')).toBeInTheDocument();
  });

  it('should show empty state message when no nodes', () => {
    render(<AttackGraph graphData={emptyGraph} />);
    expect(screen.getByText('Start a simulation to see the attack graph')).toBeInTheDocument();
  });

  it('should not show empty state when nodes exist', () => {
    render(<AttackGraph graphData={graphWithData} />);
    expect(screen.queryByText('Start a simulation to see the attack graph')).not.toBeInTheDocument();
  });
});

describe('UT-038: Visualization updates from WebSocket events', () => {
  it('should render with updated graph data', () => {
    const { rerender } = render(<AttackGraph graphData={emptyGraph} />);
    rerender(<AttackGraph graphData={graphWithData} />);
    expect(screen.queryByText('Start a simulation to see the attack graph')).not.toBeInTheDocument();
  });

  it('should accept onNodeClick callback', () => {
    const onNodeClick = vi.fn();
    render(<AttackGraph graphData={graphWithData} onNodeClick={onNodeClick} />);
    expect(screen.getByTestId('attack-graph')).toBeInTheDocument();
  });
});
