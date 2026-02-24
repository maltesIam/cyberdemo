/**
 * Tests for useNarration hook
 * UT-TECH-003: WebSocket for narration stream with message buffer
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useNarration } from '../../../src/hooks/useNarration';

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

describe('useNarration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should have correct initial state', () => {
    const { result } = renderHook(() => useNarration(null));
    expect(result.current.messages).toEqual([]);
    expect(result.current.isExpanded).toBe(false);
    expect(result.current.isEnabled).toBe(true);
    expect(result.current.connectionStatus).toBe('disconnected');
  });

  it('should toggle expanded state', () => {
    const { result } = renderHook(() => useNarration(null));

    act(() => {
      result.current.toggleExpanded();
    });

    expect(result.current.isExpanded).toBe(true);

    act(() => {
      result.current.toggleExpanded();
    });

    expect(result.current.isExpanded).toBe(false);
  });

  it('should toggle enabled state', () => {
    const { result } = renderHook(() => useNarration(null));

    act(() => {
      result.current.toggleEnabled();
    });

    expect(result.current.isEnabled).toBe(false);
  });

  it('should clear messages', () => {
    const { result } = renderHook(() => useNarration(null));

    act(() => {
      result.current.clearMessages();
    });

    expect(result.current.messages).toEqual([]);
  });

  it('should report disconnected status when no session', () => {
    const { result } = renderHook(() => useNarration(null));
    expect(result.current.connectionStatus).toBe('disconnected');
  });
});
