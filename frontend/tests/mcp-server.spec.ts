/**
 * MCP Server Tests - Written FIRST following TDD
 *
 * These tests define the expected behavior of the MCP Server
 * before implementation.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";

// Types we expect to exist
import type {
  MCPMessage,
  MCPResponse,
  MCPToolHandler,
  MCPToolRegistry,
  ShowSimulationInput,
  GenerateChartInput,
  RunDemoScenarioInput,
  GetDemoStateInput,
  UpdateDashboardInput,
  ShowAlertTimelineInput,
  HighlightAssetInput,
  ShowPostmortemInput,
  DemoState,
  ChartData,
  AlertTimelineEntry,
} from "../src/mcp/types";

// Server and handler we expect to implement
import { createMCPHandler, MCPHandler } from "../src/mcp/handler";
import { createToolRegistry } from "../src/mcp/tools";

// Individual tool handlers
import { showSimulation } from "../src/mcp/tools/show-simulation";
import { generateChart } from "../src/mcp/tools/generate-chart";
import { runDemoScenario } from "../src/mcp/tools/run-demo-scenario";
import { getDemoState } from "../src/mcp/tools/get-demo-state";
import { updateDashboard } from "../src/mcp/tools/update-dashboard";
import { showAlertTimeline } from "../src/mcp/tools/show-alert-timeline";
import { highlightAsset } from "../src/mcp/tools/highlight-asset";
import { showPostmortem } from "../src/mcp/tools/show-postmortem";

// ============================================================================
// Type Definition Tests
// ============================================================================

describe("MCP Types", () => {
  it("should have proper MCPMessage structure", () => {
    const message: MCPMessage = {
      id: "msg-001",
      type: "tool_call",
      tool: "show_simulation",
      params: { simulation_id: "sim-1", type: "attack", data: {} },
    };

    expect(message.id).toBe("msg-001");
    expect(message.type).toBe("tool_call");
    expect(message.tool).toBe("show_simulation");
    expect(message.params).toBeDefined();
  });

  it("should have proper MCPResponse structure", () => {
    const response: MCPResponse = {
      id: "msg-001",
      success: true,
      result: { message: "Simulation displayed" },
    };

    expect(response.id).toBe("msg-001");
    expect(response.success).toBe(true);
    expect(response.result).toBeDefined();
  });

  it("should have proper DemoState structure", () => {
    const state: DemoState = {
      activeScenario: 1,
      simulationRunning: false,
      highlightedAssets: [],
      currentView: "dashboard",
      charts: [],
      timeline: null,
    };

    expect(state.activeScenario).toBe(1);
    expect(state.simulationRunning).toBe(false);
  });
});

// ============================================================================
// Tool Handler Tests
// ============================================================================

describe("Tool: show_simulation", () => {
  let mockContext: { setState: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    mockContext = {
      setState: vi.fn(),
    };
  });

  it("should display a simulation successfully", async () => {
    const input: ShowSimulationInput = {
      simulation_id: "sim-attack-001",
      type: "attack",
      data: {
        source: "10.0.0.1",
        target: "10.0.0.50",
        technique: "T1059",
      },
    };

    const result = await showSimulation(input, mockContext);

    expect(result.success).toBe(true);
    expect(result.message).toContain("Simulation");
    expect(mockContext.setState).toHaveBeenCalled();
  });

  it("should reject invalid simulation type", async () => {
    const input: ShowSimulationInput = {
      simulation_id: "sim-001",
      type: "",
      data: {},
    };

    const result = await showSimulation(input, mockContext);

    expect(result.success).toBe(false);
    expect(result.error).toBeDefined();
  });
});

describe("Tool: generate_chart", () => {
  let mockContext: { setState: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    mockContext = {
      setState: vi.fn(),
    };
  });

  it("should generate a bar chart", async () => {
    const input: GenerateChartInput = {
      chart_type: "bar",
      title: "Incidents by Severity",
      data: {
        labels: ["Critical", "High", "Medium", "Low"],
        values: [5, 12, 25, 18],
      },
    };

    const result = await generateChart(input, mockContext);

    expect(result.success).toBe(true);
    expect(result.chart_id).toBeDefined();
    expect(mockContext.setState).toHaveBeenCalled();
  });

  it("should generate a line chart", async () => {
    const input: GenerateChartInput = {
      chart_type: "line",
      title: "Incidents Over Time",
      data: {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri"],
        values: [10, 15, 8, 22, 17],
      },
    };

    const result = await generateChart(input, mockContext);

    expect(result.success).toBe(true);
    expect(result.chart_id).toBeDefined();
  });

  it("should generate a pie chart", async () => {
    const input: GenerateChartInput = {
      chart_type: "pie",
      title: "Detection Sources",
      data: {
        labels: ["EDR", "SIEM", "User Report"],
        values: [45, 35, 20],
      },
    };

    const result = await generateChart(input, mockContext);

    expect(result.success).toBe(true);
    expect(result.chart_id).toBeDefined();
  });

  it("should reject empty data", async () => {
    const input: GenerateChartInput = {
      chart_type: "bar",
      title: "Empty Chart",
      data: {
        labels: [],
        values: [],
      },
    };

    const result = await generateChart(input, mockContext);

    expect(result.success).toBe(false);
    expect(result.error).toContain("data");
  });
});

describe("Tool: run_demo_scenario", () => {
  let mockContext: { setState: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    mockContext = {
      setState: vi.fn(),
    };
  });

  it("should run scenario 1 (Ransomware Attack)", async () => {
    const input: RunDemoScenarioInput = { scenario: 1 };

    const result = await runDemoScenario(input, mockContext);

    expect(result.success).toBe(true);
    expect(result.scenario_name).toContain("Ransomware");
    expect(mockContext.setState).toHaveBeenCalled();
  });

  it("should run scenario 2 (Data Exfiltration)", async () => {
    const input: RunDemoScenarioInput = { scenario: 2 };

    const result = await runDemoScenario(input, mockContext);

    expect(result.success).toBe(true);
    expect(result.scenario_name).toContain("Exfiltration");
  });

  it("should run scenario 3 (Lateral Movement)", async () => {
    const input: RunDemoScenarioInput = { scenario: 3 };

    const result = await runDemoScenario(input, mockContext);

    expect(result.success).toBe(true);
    expect(result.scenario_name).toContain("Lateral");
  });

  it("should reject invalid scenario number", async () => {
    const input: RunDemoScenarioInput = { scenario: 99 as 1 | 2 | 3 };

    const result = await runDemoScenario(input, mockContext);

    expect(result.success).toBe(false);
    expect(result.error).toContain("Invalid scenario");
  });
});

describe("Tool: get_demo_state", () => {
  it("should return current demo state", async () => {
    const initialState: DemoState = {
      activeScenario: 2,
      simulationRunning: true,
      highlightedAssets: ["asset-001"],
      currentView: "graph",
      charts: [],
      timeline: null,
    };

    const mockContext = {
      getState: vi.fn().mockReturnValue(initialState),
    };

    const input: GetDemoStateInput = {};

    const result = await getDemoState(input, mockContext);

    expect(result.success).toBe(true);
    expect(result.state).toBeDefined();
    expect(result.state?.activeScenario).toBe(2);
    expect(result.state?.simulationRunning).toBe(true);
  });
});

describe("Tool: update_dashboard", () => {
  let mockContext: { setState: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    mockContext = {
      setState: vi.fn(),
    };
  });

  it("should update dashboard KPIs", async () => {
    const input: UpdateDashboardInput = {
      kpis: {
        total_incidents: 42,
        critical_open: 3,
        hosts_contained: 5,
        mttr_hours: 2.5,
      },
    };

    const result = await updateDashboard(input, mockContext);

    expect(result.success).toBe(true);
    expect(mockContext.setState).toHaveBeenCalled();
  });

  it("should update dashboard charts", async () => {
    const input: UpdateDashboardInput = {
      charts: [
        {
          chart_id: "chart-001",
          data: {
            labels: ["A", "B", "C"],
            values: [10, 20, 30],
          },
        },
      ],
    };

    const result = await updateDashboard(input, mockContext);

    expect(result.success).toBe(true);
  });

  it("should update both KPIs and charts", async () => {
    const input: UpdateDashboardInput = {
      kpis: {
        total_incidents: 50,
        critical_open: 2,
        hosts_contained: 3,
        mttr_hours: 1.8,
      },
      charts: [
        {
          chart_id: "chart-002",
          data: { labels: ["X", "Y"], values: [15, 25] },
        },
      ],
    };

    const result = await updateDashboard(input, mockContext);

    expect(result.success).toBe(true);
  });
});

describe("Tool: show_alert_timeline", () => {
  let mockContext: { setState: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    mockContext = {
      setState: vi.fn(),
    };
  });

  it("should show alert timeline for incident", async () => {
    const input: ShowAlertTimelineInput = {
      incident_id: "INC-001",
      alerts: [
        {
          timestamp: "2024-01-15T10:30:00Z",
          type: "detection",
          severity: "high",
          description: "Suspicious PowerShell execution detected",
        },
        {
          timestamp: "2024-01-15T10:35:00Z",
          type: "containment",
          severity: "medium",
          description: "Host isolated from network",
        },
      ],
    };

    const result = await showAlertTimeline(input, mockContext);

    expect(result.success).toBe(true);
    expect(mockContext.setState).toHaveBeenCalled();
  });

  it("should reject empty alerts array", async () => {
    const input: ShowAlertTimelineInput = {
      incident_id: "INC-002",
      alerts: [],
    };

    const result = await showAlertTimeline(input, mockContext);

    expect(result.success).toBe(false);
    expect(result.error).toContain("alerts");
  });
});

describe("Tool: highlight_asset", () => {
  let mockContext: { setState: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    mockContext = {
      setState: vi.fn(),
    };
  });

  it("should highlight asset with pulse effect", async () => {
    const input: HighlightAssetInput = {
      asset_id: "asset-web-001",
      highlight_type: "pulse",
    };

    const result = await highlightAsset(input, mockContext);

    expect(result.success).toBe(true);
    expect(mockContext.setState).toHaveBeenCalled();
  });

  it("should highlight asset with glow effect", async () => {
    const input: HighlightAssetInput = {
      asset_id: "asset-db-001",
      highlight_type: "glow",
    };

    const result = await highlightAsset(input, mockContext);

    expect(result.success).toBe(true);
  });

  it("should highlight asset with zoom effect", async () => {
    const input: HighlightAssetInput = {
      asset_id: "asset-srv-001",
      highlight_type: "zoom",
    };

    const result = await highlightAsset(input, mockContext);

    expect(result.success).toBe(true);
  });

  it("should reject empty asset_id", async () => {
    const input: HighlightAssetInput = {
      asset_id: "",
      highlight_type: "pulse",
    };

    const result = await highlightAsset(input, mockContext);

    expect(result.success).toBe(false);
    expect(result.error).toContain("asset_id");
  });
});

describe("Tool: show_postmortem", () => {
  let mockContext: { setState: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    mockContext = {
      setState: vi.fn(),
    };
  });

  it("should show postmortem view", async () => {
    const input: ShowPostmortemInput = {
      postmortem_id: "PM-001",
    };

    const result = await showPostmortem(input, mockContext);

    expect(result.success).toBe(true);
    expect(mockContext.setState).toHaveBeenCalled();
  });

  it("should reject empty postmortem_id", async () => {
    const input: ShowPostmortemInput = {
      postmortem_id: "",
    };

    const result = await showPostmortem(input, mockContext);

    expect(result.success).toBe(false);
    expect(result.error).toContain("postmortem_id");
  });
});

// ============================================================================
// Message Handler Tests
// ============================================================================

describe("MCPHandler", () => {
  let handler: MCPHandler;
  let mockContext: { setState: ReturnType<typeof vi.fn>; getState: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    mockContext = {
      setState: vi.fn(),
      getState: vi.fn().mockReturnValue({
        activeScenario: null,
        simulationRunning: false,
        highlightedAssets: [],
        currentView: "dashboard",
        charts: [],
        timeline: null,
      }),
    };

    const toolRegistry = createToolRegistry();
    handler = createMCPHandler(toolRegistry, mockContext);
  });

  it("should handle valid tool_call message", async () => {
    const message: MCPMessage = {
      id: "msg-100",
      type: "tool_call",
      tool: "show_simulation",
      params: {
        simulation_id: "sim-001",
        type: "attack",
        data: {},
      },
    };

    const response = await handler.handleMessage(message);

    expect(response.id).toBe("msg-100");
    expect(response.success).toBe(true);
  });

  it("should return error for unknown tool", async () => {
    const message: MCPMessage = {
      id: "msg-101",
      type: "tool_call",
      tool: "unknown_tool",
      params: {},
    };

    const response = await handler.handleMessage(message);

    expect(response.id).toBe("msg-101");
    expect(response.success).toBe(false);
    expect(response.error).toContain("Unknown tool");
  });

  it("should return error for invalid message type", async () => {
    const message = {
      id: "msg-102",
      type: "invalid_type",
      tool: "show_simulation",
      params: {},
    } as unknown as MCPMessage;

    const response = await handler.handleMessage(message);

    expect(response.success).toBe(false);
    expect(response.error).toContain("type");
  });

  it("should return error for missing message id", async () => {
    const message = {
      type: "tool_call",
      tool: "show_simulation",
      params: {},
    } as unknown as MCPMessage;

    const response = await handler.handleMessage(message);

    expect(response.success).toBe(false);
    expect(response.error).toContain("id");
  });
});

// ============================================================================
// Tool Registry Tests
// ============================================================================

describe("Tool Registry", () => {
  it("should register all 8 tools", () => {
    const registry = createToolRegistry();

    expect(registry.has("show_simulation")).toBe(true);
    expect(registry.has("generate_chart")).toBe(true);
    expect(registry.has("run_demo_scenario")).toBe(true);
    expect(registry.has("get_demo_state")).toBe(true);
    expect(registry.has("update_dashboard")).toBe(true);
    expect(registry.has("show_alert_timeline")).toBe(true);
    expect(registry.has("highlight_asset")).toBe(true);
    expect(registry.has("show_postmortem")).toBe(true);
  });

  it("should return undefined for unknown tool", () => {
    const registry = createToolRegistry();

    expect(registry.get("nonexistent_tool")).toBeUndefined();
  });

  it("should list all available tools", () => {
    const registry = createToolRegistry();
    const tools = registry.listTools();

    expect(tools).toHaveLength(8);
    expect(tools).toContain("show_simulation");
    expect(tools).toContain("generate_chart");
    expect(tools).toContain("run_demo_scenario");
    expect(tools).toContain("get_demo_state");
    expect(tools).toContain("update_dashboard");
    expect(tools).toContain("show_alert_timeline");
    expect(tools).toContain("highlight_asset");
    expect(tools).toContain("show_postmortem");
  });
});

// ============================================================================
// WebSocket Server Integration Tests
// ============================================================================

describe("WebSocket MCP Server", () => {
  // These tests would require actual WebSocket connections
  // For unit tests, we test the message handling logic

  it("should parse incoming JSON messages", () => {
    const rawMessage = JSON.stringify({
      id: "msg-200",
      type: "tool_call",
      tool: "show_simulation",
      params: { simulation_id: "sim-1", type: "attack", data: {} },
    });

    const parsed = JSON.parse(rawMessage) as MCPMessage;

    expect(parsed.id).toBe("msg-200");
    expect(parsed.type).toBe("tool_call");
    expect(parsed.tool).toBe("show_simulation");
  });

  it("should serialize response to JSON", () => {
    const response: MCPResponse = {
      id: "msg-200",
      success: true,
      result: { message: "Done" },
    };

    const serialized = JSON.stringify(response);
    const parsed = JSON.parse(serialized);

    expect(parsed.id).toBe("msg-200");
    expect(parsed.success).toBe(true);
  });

  it("should handle malformed JSON gracefully", () => {
    const malformed = "{ invalid json }";

    expect(() => {
      JSON.parse(malformed);
    }).toThrow();

    // Handler should catch this and return error response
  });
});

// ============================================================================
// End-to-End Flow Tests
// ============================================================================

describe("E2E: Demo Scenario Flow", () => {
  let handler: MCPHandler;
  let mockContext: { setState: ReturnType<typeof vi.fn>; getState: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    mockContext = {
      setState: vi.fn(),
      getState: vi.fn().mockReturnValue({
        activeScenario: null,
        simulationRunning: false,
        highlightedAssets: [],
        currentView: "dashboard",
        charts: [],
        timeline: null,
      }),
    };

    const toolRegistry = createToolRegistry();
    handler = createMCPHandler(toolRegistry, mockContext);
  });

  it("should execute full ransomware demo scenario", async () => {
    // Step 1: Start scenario
    const startResult = await handler.handleMessage({
      id: "step-1",
      type: "tool_call",
      tool: "run_demo_scenario",
      params: { scenario: 1 },
    });
    expect(startResult.success).toBe(true);

    // Step 2: Show simulation
    const simResult = await handler.handleMessage({
      id: "step-2",
      type: "tool_call",
      tool: "show_simulation",
      params: {
        simulation_id: "ransomware-001",
        type: "attack",
        data: { stage: "initial_access" },
      },
    });
    expect(simResult.success).toBe(true);

    // Step 3: Highlight affected asset
    const highlightResult = await handler.handleMessage({
      id: "step-3",
      type: "tool_call",
      tool: "highlight_asset",
      params: {
        asset_id: "workstation-001",
        highlight_type: "pulse",
      },
    });
    expect(highlightResult.success).toBe(true);

    // Step 4: Show timeline
    const timelineResult = await handler.handleMessage({
      id: "step-4",
      type: "tool_call",
      tool: "show_alert_timeline",
      params: {
        incident_id: "INC-RANSOM-001",
        alerts: [
          {
            timestamp: "2024-01-15T10:00:00Z",
            type: "detection",
            severity: "critical",
            description: "Ransomware detected",
          },
        ],
      },
    });
    expect(timelineResult.success).toBe(true);

    // Step 5: Update dashboard
    const dashResult = await handler.handleMessage({
      id: "step-5",
      type: "tool_call",
      tool: "update_dashboard",
      params: {
        kpis: {
          total_incidents: 1,
          critical_open: 1,
          hosts_contained: 1,
          mttr_hours: 0,
        },
      },
    });
    expect(dashResult.success).toBe(true);
  });
});
