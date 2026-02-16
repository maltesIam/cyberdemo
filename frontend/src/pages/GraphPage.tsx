/**
 * GraphPage - Incident Graph Visualization
 *
 * Displays an interactive graph of incident relationships
 * using Cytoscape.js with a side panel for node details.
 */

import { useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import { CytoscapeGraph, GraphControls, NodeDetailPanel, useGraphData } from "../components/Graph";
import type { NodeData, SelectedNode } from "../components/Graph/types";

export function GraphPage() {
  const { incidentId } = useParams<{ incidentId: string }>();
  const { data: graphData, isLoading, error } = useGraphData(incidentId);

  const [selectedNode, setSelectedNode] = useState<SelectedNode | null>(null);

  const handleNodeSelect = useCallback((node: NodeData | null) => {
    if (!node) {
      setSelectedNode(null);
      return;
    }

    // In a real app, we would fetch additional details here
    // For now, we create mock data for demonstration
    const selected: SelectedNode = {
      ...node,
      assetInfo:
        node.type === "asset"
          ? {
              hostname: node.label,
              ip: `10.0.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
              os: "Windows 11 Enterprise",
              tags: (node.metadata?.tags as string[]) ?? ["standard-user"],
              owner: "John Doe",
              department: "Finance",
              lastSeen: new Date().toISOString(),
            }
          : undefined,
      threatInfo:
        node.type === "detection" || node.type === "hash"
          ? {
              threatType: "Malware - Cobalt Strike Beacon",
              severity: node.color === "red" ? "critical" : "high",
              confidence: node.color === "red" ? 95 : 75,
              indicators: ["powershell.exe -enc ...", "Connection to C2: 185.x.x.x"],
              mitreTechniques: ["T1059.001", "T1071.001"],
            }
          : undefined,
      recommendation: {
        action: node.color === "red" ? "Immediate Containment Required" : "Monitor and Investigate",
        reason:
          node.color === "red"
            ? "High confidence malware detected with active C2 communication"
            : "Suspicious activity detected, requires further analysis",
        urgency: node.color === "red" ? "immediate" : "medium",
        steps:
          node.color === "red"
            ? [
                "Isolate the host from network",
                "Preserve memory dump for forensics",
                "Hunt for lateral movement indicators",
                "Create incident ticket for tracking",
              ]
            : [
                "Review process tree for suspicious activity",
                "Check network connections",
                "Consult threat intelligence",
              ],
      },
      statusInfo: {
        containmentStatus:
          node.color === "blue" ? "contained" : node.color === "red" ? "pending" : "none",
        ticketId: node.color === "red" || node.color === "blue" ? "JIRA-1234" : undefined,
        ticketStatus: node.color === "blue" ? "In Progress" : undefined,
        approvalStatus: (node.metadata?.tags as string[])?.includes("vip") ? "requested" : "none",
      },
    };

    setSelectedNode(selected);
  }, []);

  const handleClosePanel = useCallback(() => {
    setSelectedNode(null);
  }, []);

  // Graph control handlers
  const handleZoomIn = useCallback(() => {
    (window as any).graphControls?.zoomIn?.();
  }, []);

  const handleZoomOut = useCallback(() => {
    (window as any).graphControls?.zoomOut?.();
  }, []);

  const handleFitToScreen = useCallback(() => {
    (window as any).graphControls?.fitToScreen?.();
  }, []);

  const handleAutoLayout = useCallback(() => {
    (window as any).graphControls?.runLayout?.();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-red-500 text-center">
          <p className="text-lg font-semibold">Error loading graph</p>
          <p className="text-sm">{(error as Error).message}</p>
        </div>
      </div>
    );
  }

  if (!graphData || graphData.nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-slate-400 text-center">
          <p className="text-lg">No graph data available</p>
          <p className="text-sm">Select an incident to view its graph</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full">
      {/* Main Graph Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 bg-slate-800 border-b border-slate-700">
          <div>
            <h1 className="text-xl font-semibold text-white">Incident Graph</h1>
            {incidentId && <p className="text-sm text-slate-400">Incident: {incidentId}</p>}
          </div>
          <GraphControls
            onZoomIn={handleZoomIn}
            onZoomOut={handleZoomOut}
            onFitToScreen={handleFitToScreen}
            onAutoLayout={handleAutoLayout}
          />
        </div>

        {/* Graph Container */}
        <div className="flex-1 relative">
          <CytoscapeGraph
            data={graphData}
            onNodeSelect={handleNodeSelect}
            className="absolute inset-0"
          />
        </div>

        {/* Legend */}
        <div className="flex items-center gap-6 p-3 bg-slate-800 border-t border-slate-700 text-xs text-slate-400">
          <span className="font-medium">Legend:</span>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-green-500" />
            <span>Normal</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-yellow-500" />
            <span>Suspicious</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-red-500" />
            <span>Critical</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-blue-500" />
            <span>Contained</span>
          </div>
          <span className="ml-4">|</span>
          <div className="flex items-center gap-1">
            <span className="w-4 h-4 bg-slate-600 rotate-45" />
            <span>Incident</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-4 h-4 bg-slate-600" />
            <span>Asset</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-4 h-4 bg-slate-600 clip-hexagon" />
            <span>Detection</span>
          </div>
        </div>
      </div>

      {/* Side Panel */}
      <NodeDetailPanel node={selectedNode} onClose={handleClosePanel} />
    </div>
  );
}
