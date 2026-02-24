/**
 * useAssetHighlight - Highlight Cytoscape nodes based on MCP state
 *
 * REQ-001-001-003: When state includes `highlightedAssets` array,
 * highlight those nodes on the graph page using Cytoscape.
 */

import { useEffect, useCallback, useMemo, useRef } from 'react';
import type { McpHighlightedAsset, HighlightMode } from '../types/mcpState';

/** CSS class names for highlight modes */
const HIGHLIGHT_CLASS_MAP: Record<HighlightMode, string> = {
  pulse: 'mcp-highlight-pulse',
  glow: 'mcp-highlight-glow',
  zoom: 'mcp-highlight-zoom',
};

/** All highlight classes for removal */
const ALL_HIGHLIGHT_CLASSES = Object.values(HIGHLIGHT_CLASS_MAP).join(' ');

export interface UseAssetHighlightReturn {
  /** List of currently highlighted asset IDs */
  highlightedIds: string[];
  /** Clear all highlights */
  clearHighlights: () => void;
}

/**
 * Hook that applies Cytoscape highlight classes to nodes based on
 * the highlightedAssets array from MCP state.
 */
export function useAssetHighlight(
  highlightedAssets: McpHighlightedAsset[] | undefined
): UseAssetHighlightReturn {
  const prevHighlightedRef = useRef<string[]>([]);

  const highlightedIds = useMemo(
    () => (highlightedAssets ?? []).map((a) => a.assetId),
    [highlightedAssets]
  );

  const getCy = useCallback((): any | null => {
    return (window as any).cy ?? null;
  }, []);

  const clearHighlights = useCallback(() => {
    const cy = getCy();
    if (!cy) return;

    try {
      const allNodes = cy.nodes();
      if (allNodes && allNodes.forEach) {
        allNodes.forEach((node: any) => {
          ALL_HIGHLIGHT_CLASSES.split(' ').forEach((cls) => {
            node.removeClass(cls);
          });
        });
      }
    } catch {
      // Cytoscape instance may not be ready
    }
  }, [getCy]);

  useEffect(() => {
    const cy = getCy();
    if (!cy) return;

    try {
      // Remove old highlights
      prevHighlightedRef.current.forEach((id) => {
        const nodes = cy.$(`node[id="${id}"]`);
        if (nodes && nodes.forEach) {
          nodes.forEach((node: any) => {
            ALL_HIGHLIGHT_CLASSES.split(' ').forEach((cls) => {
              node.removeClass(cls);
            });
          });
        }
      });

      // Apply new highlights
      if (highlightedAssets) {
        highlightedAssets.forEach((asset) => {
          const cls = HIGHLIGHT_CLASS_MAP[asset.mode];
          const nodes = cy.$(`node[id="${asset.assetId}"]`);
          if (nodes && nodes.forEach) {
            nodes.forEach((node: any) => {
              node.addClass(cls);
            });
          }
        });
      }
    } catch {
      // Cytoscape instance may not be ready
    }

    prevHighlightedRef.current = highlightedIds;
  }, [highlightedAssets, highlightedIds, getCy]);

  return {
    highlightedIds,
    clearHighlights,
  };
}
