/**
 * useAipAssist Hook - Capture and stream user actions to aIP Assist.
 *
 * aIP = Artificial Intelligence Person
 *
 * REQ-004-001-001: Hook en componentes React para capturar acciones
 * REQ-004-001-002: Throttling de eventos (max 10/segundo)
 * REQ-004-001-003: Contexto incluye: accion, elemento, datos visibles
 *
 * This hook provides:
 * - Action tracking for UI interactions
 * - Rate limiting (max 10 actions/second by default)
 * - WebSocket connection to aIP Assist backend
 * - Session state management
 */
import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Types of user actions that can be captured.
 */
export enum AipActionType {
  CLICK = "click",
  VIEW = "view",
  SEARCH = "search",
  FILTER = "filter",
  SELECT = "select",
  EXPAND = "expand",
  NAVIGATE = "navigate",
  SUBMIT = "submit",
  HOVER = "hover",
  SCROLL = "scroll",
  SORT = "sort",
  EDIT = "edit",
}

/**
 * Context for a user action.
 */
export interface AipActionContext {
  action: AipActionType;
  element: string;
  elementId?: string;
  page?: string;
  visibleData?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  timestamp?: string;
}

/**
 * Options for the useAipAssist hook.
 */
export interface UseAipAssistOptions {
  /** Session identifier */
  sessionId: string;
  /** Maximum actions per second (default: 10) */
  maxActionsPerSecond?: number;
  /** Callback when an action is tracked */
  onAction?: (context: AipActionContext & { sessionId: string }) => void;
  /** WebSocket URL for aIP Assist backend */
  wsUrl?: string;
  /** Whether to auto-connect to WebSocket */
  autoConnect?: boolean;
}

/**
 * Return type for useAipAssist hook.
 */
export interface UseAipAssistReturn {
  /** Function to track a user action */
  trackAction: (action: Omit<AipActionContext, "timestamp">) => void;
  /** Whether connected to the aIP Assist backend */
  isConnected: boolean;
  /** Number of actions tracked in this session */
  actionCount: number;
  /** Whether rate limited */
  isRateLimited: boolean;
  /** Connect to aIP Assist WebSocket */
  connect: () => void;
  /** Disconnect from aIP Assist WebSocket */
  disconnect: () => void;
}

/**
 * Hook to capture and stream user actions to the aIP Assist backend.
 *
 * @param options - Configuration options
 * @returns Object with trackAction function and state
 */
export function useAipAssist(
  options: UseAipAssistOptions
): UseAipAssistReturn {
  const {
    sessionId,
    maxActionsPerSecond = 10,
    onAction,
    wsUrl,
    autoConnect = false,
  } = options;

  // State
  const [isConnected, setIsConnected] = useState(false);
  const [actionCount, setActionCount] = useState(0);
  const [isRateLimited, setIsRateLimited] = useState(false);

  // Refs for rate limiting
  const actionTimestamps = useRef<number[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  // Cleanup old timestamps (older than 1 second)
  const cleanupTimestamps = useCallback(() => {
    const now = Date.now();
    actionTimestamps.current = actionTimestamps.current.filter(
      (ts) => now - ts < 1000
    );
  }, []);

  // Check if rate limited
  const checkRateLimit = useCallback(() => {
    cleanupTimestamps();
    const limited = actionTimestamps.current.length >= maxActionsPerSecond;
    setIsRateLimited(limited);
    return limited;
  }, [cleanupTimestamps, maxActionsPerSecond]);

  // Track action
  const trackAction = useCallback(
    (action: Omit<AipActionContext, "timestamp">) => {
      // Check rate limit
      if (checkRateLimit()) {
        return;
      }

      // Record timestamp for rate limiting
      actionTimestamps.current.push(Date.now());

      // Create full context with timestamp
      const context: AipActionContext & { sessionId: string } = {
        ...action,
        sessionId,
        timestamp: new Date().toISOString(),
      };

      // Increment action count
      setActionCount((prev) => prev + 1);

      // Call onAction callback if provided
      if (onAction) {
        onAction(context);
      }

      // Send to WebSocket if connected
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            type: "action",
            ...context,
          })
        );
      }

      // Update rate limit status
      checkRateLimit();
    },
    [sessionId, onAction, checkRateLimit]
  );

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current) {
      return;
    }

    const url = wsUrl || `ws://localhost:8000/api/v1/aip-assist/ws/${sessionId}`;

    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onclose = () => {
        setIsConnected(false);
        wsRef.current = null;
      };

      ws.onerror = () => {
        setIsConnected(false);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          // Handle incoming messages (suggestions, etc.)
          console.log("aIP Assist message:", data);
        } catch {
          // Ignore parse errors
        }
      };

      wsRef.current = ws;
    } catch {
      setIsConnected(false);
    }
  }, [wsUrl, sessionId]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      setIsConnected(false);
    }
  }, []);

  // Auto-connect effect
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  // Reset rate limit periodically
  useEffect(() => {
    const interval = setInterval(() => {
      cleanupTimestamps();
      if (actionTimestamps.current.length < maxActionsPerSecond) {
        setIsRateLimited(false);
      }
    }, 100);

    return () => clearInterval(interval);
  }, [cleanupTimestamps, maxActionsPerSecond]);

  return {
    trackAction,
    isConnected,
    actionCount,
    isRateLimited,
    connect,
    disconnect,
  };
}

// =============================================================================
// Backwards Compatibility Aliases
// =============================================================================

/** @deprecated Use AipActionType instead */
export const CopilotActionType = AipActionType;

/** @deprecated Use AipActionContext instead */
export type CopilotActionContext = AipActionContext;

/** @deprecated Use UseAipAssistOptions instead */
export type UseCopilotActionsOptions = UseAipAssistOptions;

/** @deprecated Use UseAipAssistReturn instead */
export type UseCopilotActionsReturn = UseAipAssistReturn;

/** @deprecated Use useAipAssist instead */
export const useCopilotActions = useAipAssist;
