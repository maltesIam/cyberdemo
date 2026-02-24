/**
 * useMcpStateSync - WebSocket state sync hook for MCP WS Server
 *
 * REQ-001-001-001: Connect to MCP WS Server on port 3001
 * TECH-001: useMcpStateSync hook interface
 * NFR-002: Auto-reconnect with exponential backoff
 * NFR-004: No memory leaks from WS connections
 * INT-001: WebSocket protocol for React to MCP WS Server
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import type { McpStateUpdate, McpStateSyncReturn } from '../types/mcpState';

type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface UseMcpStateSyncOptions {
  /** WebSocket URL. Defaults to ws://localhost:3001/ws */
  url?: string;
  /** Max reconnect attempts before giving up. Default: 10 */
  maxReconnectAttempts?: number;
  /** Base delay for exponential backoff in ms. Default: 1000 */
  baseReconnectDelay?: number;
  /** Callback when state updates */
  onStateUpdate?: (state: McpStateUpdate) => void;
}

/**
 * Hook that connects to the MCP WS Server, receives JSON state updates,
 * and stores them in React state. Auto-reconnects with exponential backoff.
 */
export function useMcpStateSync(options: UseMcpStateSyncOptions = {}): McpStateSyncReturn {
  const {
    url = `ws://${window.location.hostname}:3001/ws`,
    maxReconnectAttempts = 10,
    baseReconnectDelay = 1000,
    onStateUpdate,
  } = options;

  const [state, setState] = useState<McpStateUpdate>({});
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('connecting');

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isMountedRef = useRef(true);
  const isManualDisconnectRef = useRef(false);
  const onStateUpdateRef = useRef(onStateUpdate);
  onStateUpdateRef.current = onStateUpdate;

  const cleanup = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.onopen = null;
      wsRef.current.onclose = null;
      wsRef.current.onerror = null;
      wsRef.current.onmessage = null;
      if (
        wsRef.current.readyState === WebSocket.OPEN ||
        wsRef.current.readyState === WebSocket.CONNECTING
      ) {
        wsRef.current.close();
      }
      wsRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    cleanup();
    if (!isMountedRef.current) return;

    setConnectionStatus('connecting');
    isManualDisconnectRef.current = false;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!isMountedRef.current) return;
        setConnectionStatus('connected');
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event: MessageEvent) => {
        if (!isMountedRef.current) return;
        try {
          const data = JSON.parse(event.data) as McpStateUpdate;
          setState((prev) => {
            const merged = { ...prev, ...data };
            onStateUpdateRef.current?.(merged);
            return merged;
          });
        } catch {
          // Ignore invalid JSON messages
        }
      };

      ws.onclose = () => {
        if (!isMountedRef.current) return;
        setConnectionStatus('disconnected');

        // Auto-reconnect unless manually disconnected or max attempts reached
        if (
          !isManualDisconnectRef.current &&
          reconnectAttemptsRef.current < maxReconnectAttempts
        ) {
          const delay = baseReconnectDelay * Math.pow(2, reconnectAttemptsRef.current);
          reconnectAttemptsRef.current += 1;
          reconnectTimerRef.current = setTimeout(() => {
            if (isMountedRef.current) {
              connect();
            }
          }, delay);
        }
      };

      ws.onerror = () => {
        if (!isMountedRef.current) return;
        setConnectionStatus('error');
      };
    } catch {
      if (isMountedRef.current) {
        setConnectionStatus('error');
      }
    }
  }, [url, maxReconnectAttempts, baseReconnectDelay, cleanup]);

  const disconnect = useCallback(() => {
    isManualDisconnectRef.current = true;
    reconnectAttemptsRef.current = maxReconnectAttempts; // prevent reconnect
    cleanup();
    setConnectionStatus('disconnected');
  }, [cleanup, maxReconnectAttempts]);

  const reconnect = useCallback(() => {
    reconnectAttemptsRef.current = 0;
    connect();
  }, [connect]);

  // Connect on mount, cleanup on unmount
  useEffect(() => {
    isMountedRef.current = true;
    connect();

    return () => {
      isMountedRef.current = false;
      cleanup();
    };
  }, [connect, cleanup]);

  return {
    state,
    connectionStatus,
    isConnected: connectionStatus === 'connected',
    reconnect,
    disconnect,
  };
}
