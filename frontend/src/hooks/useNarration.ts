/**
 * useNarration - Hook managing WebSocket connection and message buffer for narration
 *
 * TECH-003: WebSocket connection to /api/v1/narration/ws/{session}
 * Manages message buffer with max 1000 entries
 */

import { useState, useCallback, useRef } from 'react';
import { useWebSocket, type WebSocketStatus } from './useWebSocket';
import {
  type DemoNarrationMessage,
  type NarrationState,
  DEFAULT_NARRATION_STATE,
  addNarrationMessage,
  MAX_NARRATION_MESSAGES,
} from '../types/demo';

// Use current host for WS (Vite proxy forwards to backend), or explicit URL for production
const API_BASE = import.meta.env.VITE_WS_URL || `ws://${window.location.host}`;

export interface UseNarrationReturn {
  messages: DemoNarrationMessage[];
  isExpanded: boolean;
  isEnabled: boolean;
  connectionStatus: WebSocketStatus;
  toggleExpanded: () => void;
  toggleEnabled: () => void;
  clearMessages: () => void;
}

export function useNarration(sessionId: string | null): UseNarrationReturn {
  const [state, setState] = useState<NarrationState>(DEFAULT_NARRATION_STATE);
  const stateRef = useRef(state);
  stateRef.current = state;

  const handleMessage = useCallback((data: unknown) => {
    if (!data || typeof data !== 'object') return;
    const msg = data as Record<string, unknown>;
    const narrationMsg: DemoNarrationMessage = {
      id: (msg.id as string) ?? `msg-${Date.now()}`,
      timestamp: (msg.timestamp as string) ?? new Date().toISOString(),
      type: (['info', 'warning', 'error', 'success'].includes(msg.type as string)
        ? (msg.type as DemoNarrationMessage['type'])
        : 'info'),
      content: (msg.content as string) ?? '',
      source: msg.source as string | undefined,
    };

    setState((prev) => ({
      ...prev,
      messages: addNarrationMessage(prev.messages, narrationMsg),
    }));
  }, []);

  const wsUrl = sessionId ? `${API_BASE}/narration/ws/${sessionId}` : '';
  const { status } = useWebSocket({
    url: wsUrl,
    onMessage: handleMessage,
    autoConnect: !!sessionId && state.isEnabled,
    reconnect: true,
  });

  const toggleExpanded = useCallback(() => {
    setState((prev) => ({ ...prev, isExpanded: !prev.isExpanded }));
  }, []);

  const toggleEnabled = useCallback(() => {
    setState((prev) => ({ ...prev, isEnabled: !prev.isEnabled }));
  }, []);

  const clearMessages = useCallback(() => {
    setState((prev) => ({ ...prev, messages: [] }));
  }, []);

  return {
    messages: state.messages,
    isExpanded: state.isExpanded,
    isEnabled: state.isEnabled,
    connectionStatus: sessionId ? status : 'disconnected',
    toggleExpanded,
    toggleEnabled,
    clearMessages,
  };
}
