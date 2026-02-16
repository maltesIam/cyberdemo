/**
 * MCP WebSocket Server
 *
 * Standalone WebSocket server that handles MCP messages from Claude.
 * This runs as a separate Node.js process.
 *
 * Usage: npx ts-node src/mcp/server.ts
 * Or: node --loader ts-node/esm src/mcp/server.ts
 */

import { WebSocketServer, WebSocket } from "ws";
import type { DemoState, MCPContext, MCPResponse } from "./types";
import { createMCPHandler, parseMessage, serializeResponse } from "./handler";
import { createToolRegistry } from "./tools";

const MCP_PORT = 3001;

// In-memory state for demo (in production, this would sync with React)
let demoState: DemoState = {
  activeScenario: null,
  simulationRunning: false,
  highlightedAssets: [],
  currentView: "dashboard",
  charts: [],
  timeline: null,
};

// Connected React clients for state sync
const reactClients: Set<WebSocket> = new Set();

function broadcastStateUpdate() {
  const message = JSON.stringify({
    type: "state_update",
    state: demoState,
  });

  for (const client of reactClients) {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  }
}

// Create MCP context
const mcpContext: MCPContext = {
  setState: (updater) => {
    demoState = updater(demoState);
    broadcastStateUpdate();
  },
  getState: () => demoState,
};

// Create handler with all tools
const toolRegistry = createToolRegistry();
const handler = createMCPHandler(toolRegistry, mcpContext);

// Create WebSocket server
const wss = new WebSocketServer({ port: MCP_PORT });

console.log(`[MCP Server] Starting on port ${MCP_PORT}...`);

wss.on("connection", (ws, request) => {
  const clientType = request.headers["x-client-type"] || "unknown";
  console.log(`[MCP Server] Client connected: ${clientType}`);

  if (clientType === "react") {
    reactClients.add(ws);
  }

  ws.on("message", async (data) => {
    const rawMessage = data.toString();
    console.log(`[MCP Server] Received: ${rawMessage}`);

    const message = parseMessage(rawMessage);

    if (!message) {
      const errorResponse: MCPResponse = {
        id: "",
        success: false,
        error: "Failed to parse message as JSON",
      };
      ws.send(serializeResponse(errorResponse));
      return;
    }

    const response = await handler.handleMessage(message);
    const responseStr = serializeResponse(response);

    console.log(`[MCP Server] Response: ${responseStr}`);
    ws.send(responseStr);
  });

  ws.on("close", () => {
    console.log(`[MCP Server] Client disconnected: ${clientType}`);
    reactClients.delete(ws);
  });

  ws.on("error", (error) => {
    console.error(`[MCP Server] WebSocket error:`, error);
    reactClients.delete(ws);
  });

  // Send current state to new React clients
  if (clientType === "react") {
    ws.send(
      JSON.stringify({
        type: "state_update",
        state: demoState,
      }),
    );
  }
});

wss.on("listening", () => {
  console.log(`[MCP Server] Listening on ws://localhost:${MCP_PORT}`);
  console.log(`[MCP Server] Available tools: ${toolRegistry.listTools().join(", ")}`);
});

wss.on("error", (error) => {
  console.error(`[MCP Server] Server error:`, error);
});

// Handle graceful shutdown
process.on("SIGINT", () => {
  console.log("\n[MCP Server] Shutting down...");
  wss.close(() => {
    console.log("[MCP Server] Closed");
    process.exit(0);
  });
});

export { wss, demoState, mcpContext };
