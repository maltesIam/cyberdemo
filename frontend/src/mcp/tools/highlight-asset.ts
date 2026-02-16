/**
 * Tool: highlight_asset
 *
 * Highlights a specific asset on the graph view.
 */

import type { HighlightAssetInput, HighlightAssetOutput, MCPContext } from "../types";

export async function highlightAsset(
  input: HighlightAssetInput,
  context: { setState: MCPContext["setState"] },
): Promise<HighlightAssetOutput> {
  // Validate input
  if (!input.asset_id || input.asset_id.trim() === "") {
    return {
      success: false,
      error: "asset_id is required and cannot be empty",
    };
  }

  const validHighlightTypes = ["pulse", "glow", "zoom"];
  if (!validHighlightTypes.includes(input.highlight_type)) {
    return {
      success: false,
      error: `Invalid highlight_type: ${input.highlight_type}. Must be one of: ${validHighlightTypes.join(", ")}`,
    };
  }

  // Update state to highlight the asset
  context.setState((prev) => ({
    ...prev,
    highlightedAssets: [
      ...prev.highlightedAssets.filter((id) => id !== input.asset_id),
      input.asset_id,
    ],
    currentView: "graph",
  }));

  return {
    success: true,
  };
}
