# Frontend MCP Server Implementation Plan

## Overview

Build a WebSocket-based MCP (Model Context Protocol) Server for CyberDemo frontend that allows Claude to control the UI in real-time through 8 specialized tools.

## Functional Specification

### Purpose

Enable bidirectional communication between Claude (via MCP protocol) and the CyberDemo React frontend, allowing Claude to:

- Display simulations and demos
- Generate and display charts
- Update dashboard in real-time
- Highlight assets on the graph
- Show alert timelines and postmortems

### Port

- WebSocket Server: Port 3001

## Requirements

### 8 WebSocket Tools

1. **show_simulation** - Display simulation on UI
   - Input: `{ simulation_id: string, type: string, data: object }`
   - Output: `{ success: boolean, message: string }`

2. **generate_chart** - Generate and display charts
   - Input: `{ chart_type: 'bar' | 'line' | 'pie', data: ChartData, title: string }`
   - Output: `{ success: boolean, chart_id: string }`

3. **run_demo_scenario** - Trigger demo scenarios 1/2/3
   - Input: `{ scenario: 1 | 2 | 3 }`
   - Output: `{ success: boolean, scenario_name: string }`

4. **get_demo_state** - Get current demo state
   - Input: `{}`
   - Output: `{ state: DemoState }`

5. **update_dashboard** - Update dashboard in real-time
   - Input: `{ kpis?: DashboardKPIs, charts?: ChartUpdate[] }`
   - Output: `{ success: boolean }`

6. **show_alert_timeline** - Show alert timeline
   - Input: `{ incident_id: string, alerts: AlertTimelineEntry[] }`
   - Output: `{ success: boolean }`

7. **highlight_asset** - Highlight specific asset on graph
   - Input: `{ asset_id: string, highlight_type: 'pulse' | 'glow' | 'zoom' }`
   - Output: `{ success: boolean }`

8. **show_postmortem** - Display postmortem view
   - Input: `{ postmortem_id: string }`
   - Output: `{ success: boolean }`

## Architecture

```
                  +------------------+
                  |   Claude/MCP     |
                  +--------+---------+
                           |
                           | WebSocket (port 3001)
                           |
                  +--------v---------+
                  |   MCP Server     |
                  | (server.ts)      |
                  +--------+---------+
                           |
                  +--------v---------+
                  |  Message Handler |
                  | (handler.ts)     |
                  +--------+---------+
                           |
         +-----------------+-----------------+
         |                 |                 |
   +-----v-----+    +------v------+   +------v------+
   |  Tool 1   |    |   Tool 2    |   |   Tool N    |
   +-----+-----+    +------+------+   +------+------+
         |                 |                 |
         +--------+--------+-----------------+
                  |
         +--------v---------+
         |  MCPContext      |
         |  (React Provider)|
         +--------+---------+
                  |
         +--------v---------+
         |  React Components|
         +------------------+
```

## File Structure

```
CyberDemo/frontend/src/mcp/
├── types.ts          # Type definitions
├── server.ts         # WebSocket MCP server
├── handler.ts        # Message handler/router
├── context.tsx       # React context provider
└── tools/
    ├── index.ts      # Export all tools
    ├── show-simulation.ts
    ├── generate-chart.ts
    ├── run-demo-scenario.ts
    ├── get-demo-state.ts
    ├── update-dashboard.ts
    ├── show-alert-timeline.ts
    ├── highlight-asset.ts
    └── show-postmortem.ts

CyberDemo/frontend/tests/
└── mcp-server.spec.ts  # All MCP tests (TDD)
```

## EPICs

### EPIC 1: Test Suite (TDD)

- [ ] Write unit tests for all 8 tools
- [ ] Write integration tests for WebSocket server
- [ ] Write tests for message handler routing
- [ ] Write tests for React context integration

### EPIC 2: Type Definitions

- [ ] Define MCP message types
- [ ] Define tool input/output types
- [ ] Define demo state types

### EPIC 3: Core Server Implementation

- [ ] Implement WebSocket server (port 3001)
- [ ] Implement message handler
- [ ] Implement tool registry

### EPIC 4: Tool Handlers

- [ ] Implement show_simulation
- [ ] Implement generate_chart
- [ ] Implement run_demo_scenario
- [ ] Implement get_demo_state
- [ ] Implement update_dashboard
- [ ] Implement show_alert_timeline
- [ ] Implement highlight_asset
- [ ] Implement show_postmortem

### EPIC 5: React Integration

- [ ] Create MCPContext provider
- [ ] Create useMCP hook
- [ ] Integrate with existing components

## TDD Approach

1. Write failing tests first
2. Implement minimum code to pass tests
3. Refactor while keeping tests green
