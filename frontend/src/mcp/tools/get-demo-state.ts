/**
 * Tool: get_demo_state
 *
 * Returns the current demo state.
 */

import type { GetDemoStateInput, GetDemoStateOutput, MCPContext } from "../types";

export async function getDemoState(
  _input: GetDemoStateInput,
  context: { getState: MCPContext["getState"] },
): Promise<GetDemoStateOutput> {
  const state = context.getState();

  return {
    success: true,
    state,
  };
}
