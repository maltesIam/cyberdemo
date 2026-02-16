/**
 * useGraphData Hook - Fetches and transforms graph data
 *
 * This hook fetches incident graph data from the API and
 * transforms it into Cytoscape.js compatible format.
 */

import { useQuery } from "@tanstack/react-query";
import { api } from "../../services/api";
import type { GraphData, NodeColor, RiskLevel } from "./types";

interface GraphApiResponse {
  nodes: Array<{
    data: {
      id: string;
      label: string;
      type: string;
      color?: string;
      risk_level?: string;
      metadata?: Record<string, unknown>;
    };
  }>;
  edges: Array<{
    data: {
      id: string;
      source: string;
      target: string;
      relation: string;
      label?: string;
    };
  }>;
}

function mapRiskLevelToColor(riskLevel?: string): NodeColor {
  switch (riskLevel) {
    case "high":
      return "red";
    case "medium":
      return "yellow";
    case "contained":
      return "blue";
    case "low":
    case "none":
    default:
      return "green";
  }
}

function transformApiResponse(response: GraphApiResponse): GraphData {
  return {
    nodes: response.nodes.map((node) => ({
      data: {
        id: node.data.id,
        label: node.data.label,
        type: node.data.type as "incident" | "detection" | "asset" | "process" | "hash",
        color: (node.data.color as NodeColor) || mapRiskLevelToColor(node.data.risk_level),
        riskLevel: node.data.risk_level as RiskLevel | undefined,
        metadata: node.data.metadata,
      },
    })),
    edges: response.edges.map((edge) => ({
      data: {
        id: edge.data.id,
        source: edge.data.source,
        target: edge.data.target,
        relation: edge.data.relation,
        label: edge.data.label,
      },
    })),
  };
}

export function useGraphData(incidentId: string | undefined) {
  return useQuery({
    queryKey: ["graph", "incident", incidentId],
    queryFn: async (): Promise<GraphData> => {
      if (!incidentId) {
        return { nodes: [], edges: [] };
      }
      const response = await api.get<GraphApiResponse>(`/graph/incident/${incidentId}`);
      return transformApiResponse(response.data);
    },
    enabled: !!incidentId,
    staleTime: 30_000,
  });
}

export function useSystemGraph() {
  return useQuery({
    queryKey: ["graph", "system"],
    queryFn: async (): Promise<GraphData> => {
      const response = await api.get<GraphApiResponse>("/graph/system");
      return transformApiResponse(response.data);
    },
    staleTime: 60_000,
  });
}
