/**
 * Tool: run_demo_scenario
 *
 * Triggers one of 3 predefined demo scenarios.
 */

import type { RunDemoScenarioInput, RunDemoScenarioOutput, MCPContext } from "../types";
import { SCENARIOS } from "../types";

export async function runDemoScenario(
  input: RunDemoScenarioInput,
  context: { setState: MCPContext["setState"] },
): Promise<RunDemoScenarioOutput> {
  // Validate scenario number
  if (![1, 2, 3].includes(input.scenario)) {
    return {
      success: false,
      error: `Invalid scenario: ${input.scenario}. Must be 1, 2, or 3.`,
    };
  }

  const scenarioInfo = SCENARIOS[input.scenario];

  // Update state to run the scenario
  context.setState((prev) => ({
    ...prev,
    activeScenario: input.scenario,
    simulationRunning: true,
    currentView: "dashboard",
  }));

  return {
    success: true,
    scenario_name: scenarioInfo.name,
  };
}
