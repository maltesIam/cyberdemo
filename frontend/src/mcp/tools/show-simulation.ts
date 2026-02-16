/**
 * Tool: show_simulation
 *
 * Displays a simulation on the UI.
 */

import type { ShowSimulationInput, ShowSimulationOutput, MCPContext } from "../types";

export async function showSimulation(
  input: ShowSimulationInput,
  context: { setState: MCPContext["setState"] },
): Promise<ShowSimulationOutput> {
  // Validate input
  if (!input.type || input.type.trim() === "") {
    return {
      success: false,
      error: "Invalid simulation type: type cannot be empty",
    };
  }

  if (!input.simulation_id) {
    return {
      success: false,
      error: "Invalid simulation_id: cannot be empty",
    };
  }

  // Update state to show simulation
  context.setState((prev) => ({
    ...prev,
    simulationRunning: true,
    currentView: "graph",
  }));

  return {
    success: true,
    message: `Simulation ${input.simulation_id} of type ${input.type} displayed successfully`,
  };
}
