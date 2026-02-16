/**
 * MCP Tool Registry
 *
 * Registers all available tools for the MCP server.
 */

import type { MCPToolRegistry, MCPToolHandler } from "../types";

import { showSimulation } from "./show-simulation";
import { generateChart } from "./generate-chart";
import { runDemoScenario } from "./run-demo-scenario";
import { getDemoState } from "./get-demo-state";
import { updateDashboard } from "./update-dashboard";
import { showAlertTimeline } from "./show-alert-timeline";
import { highlightAsset } from "./highlight-asset";
import { showPostmortem } from "./show-postmortem";

// Re-export all tools
export {
  showSimulation,
  generateChart,
  runDemoScenario,
  getDemoState,
  updateDashboard,
  showAlertTimeline,
  highlightAsset,
  showPostmortem,
};

/**
 * Creates a tool registry with all available tools registered.
 */
export function createToolRegistry(): MCPToolRegistry {
  const tools = new Map<string, MCPToolHandler>();

  // Register all 8 tools
  tools.set("show_simulation", showSimulation as MCPToolHandler);
  tools.set("generate_chart", generateChart as MCPToolHandler);
  tools.set("run_demo_scenario", runDemoScenario as MCPToolHandler);
  tools.set("get_demo_state", getDemoState as MCPToolHandler);
  tools.set("update_dashboard", updateDashboard as MCPToolHandler);
  tools.set("show_alert_timeline", showAlertTimeline as MCPToolHandler);
  tools.set("highlight_asset", highlightAsset as MCPToolHandler);
  tools.set("show_postmortem", showPostmortem as MCPToolHandler);

  return {
    has(toolName: string): boolean {
      return tools.has(toolName);
    },

    get(toolName: string): MCPToolHandler | undefined {
      return tools.get(toolName);
    },

    listTools(): string[] {
      return Array.from(tools.keys());
    },

    register(toolName: string, handler: MCPToolHandler): void {
      tools.set(toolName, handler);
    },
  };
}
