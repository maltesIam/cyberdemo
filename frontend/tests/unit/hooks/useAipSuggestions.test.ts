/**
 * Tests for useAipSuggestions hook
 * UT-TECH-004: WebSocket for AI suggestions with read tracking
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useAipSuggestions } from '../../../src/hooks/useAipSuggestions';

// Mock useWebSocket
vi.mock('../../../src/hooks/useWebSocket', () => ({
  useWebSocket: vi.fn(() => ({
    status: 'disconnected',
    send: vi.fn(),
    connect: vi.fn(),
    disconnect: vi.fn(),
    lastMessage: null,
  })),
}));

describe('useAipSuggestions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should have correct initial state', () => {
    const { result } = renderHook(() => useAipSuggestions(null));
    expect(result.current.suggestions).toEqual([]);
    expect(result.current.isExpanded).toBe(false);
    expect(result.current.isEnabled).toBe(true);
    expect(result.current.isThinking).toBe(false);
    expect(result.current.unreadCount).toBe(0);
    expect(result.current.connectionStatus).toBe('disconnected');
  });

  it('should toggle expanded state', () => {
    const { result } = renderHook(() => useAipSuggestions(null));

    act(() => {
      result.current.toggleExpanded();
    });

    expect(result.current.isExpanded).toBe(true);
  });

  it('should toggle enabled state', () => {
    const { result } = renderHook(() => useAipSuggestions(null));

    act(() => {
      result.current.toggleEnabled();
    });

    expect(result.current.isEnabled).toBe(false);
  });

  it('should have correct initial stats', () => {
    const { result } = renderHook(() => useAipSuggestions(null));
    expect(result.current.stats.totalSuggestions).toBe(0);
    expect(result.current.stats.acceptedCount).toBe(0);
    expect(result.current.stats.rejectedCount).toBe(0);
    expect(result.current.stats.acceptanceRate).toBe(0);
  });

  it('should report disconnected when no session', () => {
    const { result } = renderHook(() => useAipSuggestions(null));
    expect(result.current.connectionStatus).toBe('disconnected');
  });

  it('should expose accept and reject functions', () => {
    const { result } = renderHook(() => useAipSuggestions(null));
    expect(typeof result.current.acceptSuggestion).toBe('function');
    expect(typeof result.current.rejectSuggestion).toBe('function');
    expect(typeof result.current.markAsRead).toBe('function');
  });
});
