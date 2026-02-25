/**
 * AttackGraph Component
 *
 * Interactive attack graph using Cytoscape.js for the center column
 * of the Simulation page. Renders nodes (hosts/IOCs) and edges
 * (propagation) and updates in real-time from WebSocket events.
 *
 * Requirements:
 * - REQ-003-001-004: Attack graph center column
 * - REQ-003-001-008: Real-time visualization updates
 */

import { useEffect, useRef, useCallback } from 'react';
import type { GraphData, CytoscapeNode, CytoscapeEdge } from '../Graph/types';

export interface AttackGraphProps {
  graphData: GraphData;
  onNodeClick?: (nodeId: string) => void;
}

export function AttackGraph({ graphData, onNodeClick }: AttackGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<any>(null);

  // Initialize Cytoscape
  useEffect(() => {
    if (!containerRef.current) return;

    const initCytoscape = async () => {
      try {
        const cytoscape = (await import('cytoscape')).default;

        const cy = cytoscape({
          container: containerRef.current,
          elements: [
            ...graphData.nodes.map((n) => ({ data: n.data, group: 'nodes' as const })),
            ...graphData.edges.map((e) => ({ data: e.data, group: 'edges' as const })),
          ],
          style: [
            {
              selector: 'node',
              style: {
                'background-color': 'data(color)',
                label: 'data(label)',
                'text-valign': 'bottom',
                'text-halign': 'center',
                color: '#e5e7eb',
                'font-size': '10px',
                width: 30,
                height: 30,
              },
            },
            {
              selector: 'edge',
              style: {
                width: 2,
                'line-color': '#4b5563',
                'target-arrow-color': '#4b5563',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
              },
            },
            {
              selector: 'node:selected',
              style: {
                'border-color': '#06b6d4',
                'border-width': 3,
              },
            },
          ],
          layout: { name: 'grid' },
        });

        cy.on('tap', 'node', (evt: any) => {
          const nodeId = evt.target.id();
          onNodeClick?.(nodeId);
        });

        cyRef.current = cy;
      } catch {
        // Cytoscape not available in test environment
      }
    };

    initCytoscape();

    return () => {
      cyRef.current?.destroy();
      cyRef.current = null;
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Update graph data when it changes
  useEffect(() => {
    if (!cyRef.current) return;
    const cy = cyRef.current;

    // Add new nodes
    graphData.nodes.forEach((node) => {
      if (!cy.getElementById(node.data.id).length) {
        cy.add({ data: node.data, group: 'nodes' });
      } else {
        // Update existing node data
        const el = cy.getElementById(node.data.id);
        el.data(node.data);
      }
    });

    // Add new edges
    graphData.edges.forEach((edge) => {
      if (!cy.getElementById(edge.data.id).length) {
        cy.add({ data: edge.data, group: 'edges' });
      }
    });

    // Run layout
    cy.layout({ name: 'grid', animate: true }).run();
  }, [graphData]);

  return (
    <div data-testid="attack-graph" className="relative w-full h-full">
      <div
        ref={containerRef}
        data-testid="cytoscape-container"
        className="w-full h-full bg-primary rounded-lg"
      />
      {graphData.nodes.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center">
          <p className="text-sm text-tertiary">Start a simulation to see the attack graph</p>
        </div>
      )}
    </div>
  );
}
