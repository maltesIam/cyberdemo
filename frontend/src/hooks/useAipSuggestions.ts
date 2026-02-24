/**
 * useAipSuggestions - Hook managing WebSocket connection and suggestion state
 *
 * TECH-004: WebSocket connection to /api/v1/aip-assist/ws/{session}
 * Manages suggestions with read tracking and unread badge count
 */

import { useState, useCallback, useRef } from 'react';
import { useWebSocket, type WebSocketStatus } from './useWebSocket';
import {
  type DemoAipSuggestion,
  type AipAssistState,
  DEFAULT_AIP_ASSIST_STATE,
  markSuggestionRead,
  countUnread,
} from '../types/demo';
import type { AipSessionStats } from '../components/aip-assist/types';

const API_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export interface UseAipSuggestionsReturn {
  suggestions: DemoAipSuggestion[];
  stats: AipSessionStats;
  isExpanded: boolean;
  isEnabled: boolean;
  isThinking: boolean;
  unreadCount: number;
  connectionStatus: WebSocketStatus;
  toggleExpanded: () => void;
  toggleEnabled: () => void;
  acceptSuggestion: (id: string) => void;
  rejectSuggestion: (id: string) => void;
  markAsRead: (id: string) => void;
}

function computeStats(suggestions: DemoAipSuggestion[]): AipSessionStats {
  const total = suggestions.length;
  const accepted = suggestions.filter((s) => s.status === 'accepted').length;
  const rejected = suggestions.filter((s) => s.status === 'rejected').length;
  const expired = suggestions.filter((s) => s.status === 'expired').length;
  return {
    totalSuggestions: total,
    acceptedCount: accepted,
    rejectedCount: rejected,
    expiredCount: expired,
    acceptanceRate: total > 0 ? Math.round((accepted / total) * 100) : 0,
  };
}

export function useAipSuggestions(sessionId: string | null): UseAipSuggestionsReturn {
  const [state, setState] = useState<AipAssistState>(DEFAULT_AIP_ASSIST_STATE);
  const stateRef = useRef(state);
  stateRef.current = state;

  const handleMessage = useCallback((data: unknown) => {
    if (!data || typeof data !== 'object') return;
    const msg = data as Record<string, unknown>;

    if (msg.type === 'thinking') {
      setState((prev) => ({ ...prev, isThinking: (msg.active as boolean) ?? true }));
      return;
    }

    if (msg.type === 'suggestion') {
      const suggestion: DemoAipSuggestion = {
        id: (msg.id as string) ?? `sug-${Date.now()}`,
        type: (msg.suggestion_type as DemoAipSuggestion['type']) ?? 'action',
        title: (msg.title as string) ?? '',
        description: (msg.description as string) ?? '',
        confidence: (msg.confidence as DemoAipSuggestion['confidence']) ?? 'medium',
        status: 'pending',
        createdAt: (msg.timestamp as string) ?? new Date().toISOString(),
        relatedContext: msg.context as string | undefined,
        reason: msg.reason as string | undefined,
        isRead: false,
      };

      setState((prev) => {
        const newSuggestions = [...prev.suggestions, suggestion];
        return {
          ...prev,
          suggestions: newSuggestions,
          stats: computeStats(newSuggestions),
          unreadCount: countUnread(newSuggestions),
          isThinking: false,
        };
      });
    }
  }, []);

  const wsUrl = sessionId ? `${API_BASE}/api/v1/aip-assist/ws/${sessionId}` : '';
  const { status, send } = useWebSocket({
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

  const acceptSuggestion = useCallback((id: string) => {
    setState((prev) => {
      const newSuggestions = prev.suggestions.map((s) =>
        s.id === id ? { ...s, status: 'accepted' as const } : s
      );
      return {
        ...prev,
        suggestions: newSuggestions,
        stats: computeStats(newSuggestions),
        unreadCount: countUnread(newSuggestions),
      };
    });
    send({ type: 'accept', suggestion_id: id });
  }, [send]);

  const rejectSuggestion = useCallback((id: string) => {
    setState((prev) => {
      const newSuggestions = prev.suggestions.map((s) =>
        s.id === id ? { ...s, status: 'rejected' as const } : s
      );
      return {
        ...prev,
        suggestions: newSuggestions,
        stats: computeStats(newSuggestions),
        unreadCount: countUnread(newSuggestions),
      };
    });
    send({ type: 'reject', suggestion_id: id });
  }, [send]);

  const markAsRead = useCallback((id: string) => {
    setState((prev) => {
      const newSuggestions = markSuggestionRead(prev.suggestions, id);
      return {
        ...prev,
        suggestions: newSuggestions,
        unreadCount: countUnread(newSuggestions),
      };
    });
  }, []);

  return {
    suggestions: state.suggestions,
    stats: state.stats,
    isExpanded: state.isExpanded,
    isEnabled: state.isEnabled,
    isThinking: state.isThinking,
    unreadCount: state.unreadCount,
    connectionStatus: sessionId ? status : 'disconnected',
    toggleExpanded,
    toggleEnabled,
    acceptSuggestion,
    rejectSuggestion,
    markAsRead,
  };
}
