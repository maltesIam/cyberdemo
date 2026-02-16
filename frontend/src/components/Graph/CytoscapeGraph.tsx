/**
 * CytoscapeGraph Component
 *
 * Main graph visualization component using Cytoscape.js.
 * Renders nodes and edges with interactive features.
 */

import { useEffect, useRef, useCallback } from "react";
import cytoscape, { Core, NodeSingular } from "cytoscape";
import type { GraphData, NodeData } from "./types";

// Cytoscape styles for different node types and colors
// Using cytoscape.Stylesheet type assertion for proper styling
const cytoscapeStyles = [
  {
    selector: "node",
    style: {
      label: "data(label)",
      "text-valign": "bottom",
      "text-halign": "center",
      "font-size": "10px",
      "text-margin-y": 5,
      width: 40,
      height: 40,
    },
  },
  {
    selector: "node[type='incident']",
    style: {
      shape: "diamond",
      width: 50,
      height: 50,
    },
  },
  {
    selector: "node[type='asset']",
    style: {
      shape: "rectangle",
      "border-width": 2,
    },
  },
  {
    selector: "node[type='detection']",
    style: {
      shape: "hexagon",
    },
  },
  {
    selector: "node[type='process']",
    style: {
      shape: "ellipse",
    },
  },
  {
    selector: "node[type='hash']",
    style: {
      shape: "octagon",
    },
  },
  // Color styles
  {
    selector: "node[color='green']",
    style: {
      "background-color": "#22c55e",
      "border-color": "#16a34a",
    },
  },
  {
    selector: "node[color='yellow']",
    style: {
      "background-color": "#eab308",
      "border-color": "#ca8a04",
    },
  },
  {
    selector: "node[color='red']",
    style: {
      "background-color": "#ef4444",
      "border-color": "#dc2626",
    },
  },
  {
    selector: "node[color='blue']",
    style: {
      "background-color": "#3b82f6",
      "border-color": "#2563eb",
    },
  },
  {
    selector: "node.highlighted",
    style: {
      "border-width": 4,
      "border-color": "#8b5cf6",
      "box-shadow": "0 0 10px #8b5cf6",
    },
  },
  {
    selector: "node:selected",
    style: {
      "border-width": 3,
      "border-color": "#1e40af",
    },
  },
  {
    selector: "edge",
    style: {
      width: 2,
      "line-color": "#94a3b8",
      "target-arrow-color": "#94a3b8",
      "target-arrow-shape": "triangle",
      "curve-style": "bezier",
      label: "data(relation)",
      "font-size": "8px",
      "text-rotation": "autorotate",
    },
  },
];

interface CytoscapeGraphProps {
  data: GraphData;
  onNodeSelect?: (node: NodeData | null) => void;
  className?: string;
}

export function CytoscapeGraph({ data, onNodeSelect, className = "" }: CytoscapeGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  // Initialize Cytoscape
  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      elements: {
        nodes: data.nodes,
        edges: data.edges,
      },
      style: cytoscapeStyles as any,
      layout: {
        name: "dagre",
        rankDir: "TB",
        padding: 30,
        spacingFactor: 1.5,
      } as any,
      minZoom: 0.2,
      maxZoom: 3,
      wheelSensitivity: 0.3,
    });

    // Store reference for external access (e.g., tests)
    cyRef.current = cy;
    (window as any).cy = cy;

    // Node selection handler
    cy.on("tap", "node", (event) => {
      const node = event.target as NodeSingular;
      const nodeData = node.data() as NodeData;
      onNodeSelect?.(nodeData);
    });

    // Background tap deselects
    cy.on("tap", (event) => {
      if (event.target === cy) {
        onNodeSelect?.(null);
      }
    });

    return () => {
      cy.destroy();
      cyRef.current = null;
      delete (window as any).cy;
    };
  }, []);

  // Update data when it changes
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.elements().remove();
    cy.add(data.nodes);
    cy.add(data.edges);

    cy.layout({
      name: "dagre",
      rankDir: "TB",
      padding: 30,
      spacingFactor: 1.5,
    } as any).run();
  }, [data]);

  const zoomIn = useCallback(() => {
    cyRef.current?.zoom(cyRef.current.zoom() * 1.2);
    cyRef.current?.center();
  }, []);

  const zoomOut = useCallback(() => {
    cyRef.current?.zoom(cyRef.current.zoom() * 0.8);
    cyRef.current?.center();
  }, []);

  const fitToScreen = useCallback(() => {
    cyRef.current?.fit();
  }, []);

  const runLayout = useCallback(() => {
    cyRef.current
      ?.layout({
        name: "dagre",
        rankDir: "TB",
        padding: 30,
        spacingFactor: 1.5,
        animate: true,
        animationDuration: 500,
      } as any)
      .run();
  }, []);

  // Expose controls via ref
  useEffect(() => {
    (window as any).graphControls = {
      zoomIn,
      zoomOut,
      fitToScreen,
      runLayout,
    };
  }, [zoomIn, zoomOut, fitToScreen, runLayout]);

  return (
    <div
      ref={containerRef}
      data-testid="cytoscape-graph"
      className={`w-full h-full min-h-[400px] bg-slate-900 rounded-lg ${className}`}
    />
  );
}
