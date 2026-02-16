/**
 * MCP Context Provider
 *
 * React context that manages MCP state and WebSocket connection.
 */

import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from "react";
import type { DemoState, MCPContext as MCPContextType, MCPResponse } from "./types";
import { createMCPHandler, parseMessage, serializeResponse } from "./handler";
import { createToolRegistry } from "./tools";

// Initial demo state
const initialDemoState: DemoState = {
  activeScenario: null,
  simulationRunning: false,
  highlightedAssets: [],
  currentView: "dashboard",
  charts: [],
  timeline: null,
};

interface MCPProviderState {
  demoState: DemoState;
  connected: boolean;
  error: string | null;
}

interface MCPProviderContextValue extends MCPProviderState {
  setDemoState: React.Dispatch<React.SetStateAction<DemoState>>;
  reconnect: () => void;
}

const MCPProviderContext = createContext<MCPProviderContextValue | null>(null);

export interface MCPProviderProps {
  children: React.ReactNode;
  wsUrl?: string;
  autoConnect?: boolean;
}

const MCP_WS_PORT = 3001;

export function MCPProvider({
  children,
  wsUrl = `ws://localhost:${MCP_WS_PORT}`,
  autoConnect = true,
}: MCPProviderProps) {
  const [demoState, setDemoState] = useState<DemoState>(initialDemoState);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const handlerRef = useRef<ReturnType<typeof createMCPHandler> | null>(null);

  // Create MCP context for tool handlers
  const mcpContext: MCPContextType = {
    setState: setDemoState,
    getState: () => demoState,
  };

  // Initialize handler
  useEffect(() => {
    const toolRegistry = createToolRegistry();
    handlerRef.current = createMCPHandler(toolRegistry, mcpContext);
  }, []); // Only initialize once

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setConnected(true);
        setError(null);
        console.log("[MCP] Connected to WebSocket server");
      };

      ws.onclose = () => {
        setConnected(false);
        console.log("[MCP] Disconnected from WebSocket server");
      };

      ws.onerror = (event) => {
        setError("WebSocket connection error");
        console.error("[MCP] WebSocket error:", event);
      };

      ws.onmessage = async (event) => {
        const message = parseMessage(event.data);

        if (!message) {
          const errorResponse: MCPResponse = {
            id: "",
            success: false,
            error: "Failed to parse message",
          };
          ws.send(serializeResponse(errorResponse));
          return;
        }

        if (handlerRef.current) {
          const response = await handlerRef.current.handleMessage(message);
          ws.send(serializeResponse(response));
        }
      };

      wsRef.current = ws;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to connect");
      console.error("[MCP] Connection error:", err);
    }
  }, [wsUrl]);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      wsRef.current?.close();
    };
  }, [autoConnect, connect]);

  const reconnect = useCallback(() => {
    wsRef.current?.close();
    connect();
  }, [connect]);

  const value: MCPProviderContextValue = {
    demoState,
    connected,
    error,
    setDemoState,
    reconnect,
  };

  return <MCPProviderContext.Provider value={value}>{children}</MCPProviderContext.Provider>;
}

/**
 * Hook to access MCP context.
 */
export function useMCP(): MCPProviderContextValue {
  const context = useContext(MCPProviderContext);

  if (!context) {
    throw new Error("useMCP must be used within an MCPProvider");
  }

  return context;
}

/**
 * Hook to access just the demo state.
 */
export function useDemoState(): DemoState {
  const { demoState } = useMCP();
  return demoState;
}

/**
 * Hook to check MCP connection status.
 */
export function useMCPConnection(): {
  connected: boolean;
  error: string | null;
  reconnect: () => void;
} {
  const { connected, error, reconnect } = useMCP();
  return { connected, error, reconnect };
}
