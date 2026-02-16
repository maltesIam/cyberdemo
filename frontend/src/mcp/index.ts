/**
 * MCP Module Exports
 */

// Types
export type {
  MCPMessage,
  MCPResponse,
  MCPToolHandler,
  MCPToolRegistry,
  MCPContext,
  DemoState,
  ChartData,
  ChartState,
  AlertTimelineEntry,
  AlertTimelineState,
  ShowSimulationInput,
  ShowSimulationOutput,
  GenerateChartInput,
  GenerateChartOutput,
  RunDemoScenarioInput,
  RunDemoScenarioOutput,
  GetDemoStateInput,
  GetDemoStateOutput,
  UpdateDashboardInput,
  UpdateDashboardOutput,
  ShowAlertTimelineInput,
  ShowAlertTimelineOutput,
  HighlightAssetInput,
  HighlightAssetOutput,
  ShowPostmortemInput,
  ShowPostmortemOutput,
} from "./types";

export { SCENARIOS } from "./types";

// Handler
export { createMCPHandler, parseMessage, serializeResponse } from "./handler";
export type { MCPHandler } from "./handler";

// Tools
export { createToolRegistry } from "./tools";
export {
  showSimulation,
  generateChart,
  runDemoScenario,
  getDemoState,
  updateDashboard,
  showAlertTimeline,
  highlightAsset,
  showPostmortem,
} from "./tools";

// React Context
export { MCPProvider, useMCP, useDemoState, useMCPConnection } from "./context";
export type { MCPProviderProps } from "./context";
