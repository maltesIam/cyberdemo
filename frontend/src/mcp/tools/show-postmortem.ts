/**
 * Tool: show_postmortem
 *
 * Displays the postmortem view for a specific incident.
 */

import type { ShowPostmortemInput, ShowPostmortemOutput, MCPContext } from "../types";

export async function showPostmortem(
  input: ShowPostmortemInput,
  context: { setState: MCPContext["setState"] },
): Promise<ShowPostmortemOutput> {
  // Validate input
  if (!input.postmortem_id || input.postmortem_id.trim() === "") {
    return {
      success: false,
      error: "postmortem_id is required and cannot be empty",
    };
  }

  // Update state to show postmortem view
  context.setState((prev) => ({
    ...prev,
    currentView: "postmortem",
  }));

  return {
    success: true,
  };
}
