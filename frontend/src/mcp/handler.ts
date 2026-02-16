/**
 * MCP Message Handler
 *
 * Routes incoming MCP messages to the appropriate tool handlers.
 */

import type { MCPMessage, MCPResponse, MCPToolRegistry, MCPContext } from "./types";

export interface MCPHandler {
  handleMessage(message: MCPMessage): Promise<MCPResponse>;
}

/**
 * Creates an MCP message handler that routes tool calls to registered handlers.
 */
export function createMCPHandler(toolRegistry: MCPToolRegistry, context: MCPContext): MCPHandler {
  return {
    async handleMessage(message: MCPMessage): Promise<MCPResponse> {
      // Validate message has an id
      if (!message.id) {
        return {
          id: "",
          success: false,
          error: "Message missing required id field",
        };
      }

      // Validate message type
      if (
        message.type !== "tool_call" &&
        message.type !== "ping" &&
        message.type !== "list_tools"
      ) {
        return {
          id: message.id,
          success: false,
          error: `Invalid message type: ${message.type}`,
        };
      }

      // Handle ping
      if (message.type === "ping") {
        return {
          id: message.id,
          success: true,
          result: { pong: true },
        };
      }

      // Handle list_tools
      if (message.type === "list_tools") {
        return {
          id: message.id,
          success: true,
          result: { tools: toolRegistry.listTools() },
        };
      }

      // Handle tool_call
      if (!message.tool) {
        return {
          id: message.id,
          success: false,
          error: "tool_call message missing tool field",
        };
      }

      const handler = toolRegistry.get(message.tool);

      if (!handler) {
        return {
          id: message.id,
          success: false,
          error: `Unknown tool: ${message.tool}`,
        };
      }

      try {
        const result = await handler(message.params ?? {}, context);
        return {
          id: message.id,
          success: true,
          result: result as Record<string, unknown>,
        };
      } catch (error) {
        return {
          id: message.id,
          success: false,
          error: error instanceof Error ? error.message : "Unknown error",
        };
      }
    },
  };
}

/**
 * Parse a raw WebSocket message into an MCPMessage.
 */
export function parseMessage(data: string): MCPMessage | null {
  try {
    const parsed = JSON.parse(data);
    return parsed as MCPMessage;
  } catch {
    return null;
  }
}

/**
 * Serialize an MCPResponse to a string for WebSocket transmission.
 */
export function serializeResponse(response: MCPResponse): string {
  return JSON.stringify(response);
}
