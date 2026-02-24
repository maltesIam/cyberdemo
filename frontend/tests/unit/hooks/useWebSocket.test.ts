/**
 * Tests for useWebSocket hook
 * IT-INT-005: WebSocket connection for simulation events
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useWebSocket } from '../../../src/hooks/useWebSocket';

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  url: string;
  readyState: number = MockWebSocket.CONNECTING;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: Event) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    // Simulate async connection
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      this.onopen?.(new Event('open'));
    }, 0);
  }

  send = vi.fn();
  close = vi.fn(() => {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.(new Event('close'));
  });
}

describe('useWebSocket', () => {
  let originalWebSocket: typeof WebSocket;

  beforeEach(() => {
    originalWebSocket = global.WebSocket;
    (global as any).WebSocket = MockWebSocket;
    vi.useFakeTimers();
  });

  afterEach(() => {
    global.WebSocket = originalWebSocket;
    vi.useRealTimers();
  });

  it('should start with disconnected status when autoConnect is false', () => {
    const { result } = renderHook(() =>
      useWebSocket({ url: 'ws://test', autoConnect: false })
    );
    expect(result.current.status).toBe('disconnected');
  });

  it('should connect when autoConnect is true', async () => {
    const { result } = renderHook(() =>
      useWebSocket({ url: 'ws://test', autoConnect: true })
    );

    expect(result.current.status).toBe('connecting');

    await act(async () => {
      vi.advanceTimersByTime(10);
    });

    expect(result.current.status).toBe('connected');
  });

  it('should call onOpen when connected', async () => {
    const onOpen = vi.fn();
    renderHook(() =>
      useWebSocket({ url: 'ws://test', autoConnect: true, onOpen })
    );

    await act(async () => {
      vi.advanceTimersByTime(10);
    });

    expect(onOpen).toHaveBeenCalledTimes(1);
  });

  it('should disconnect when disconnect is called', async () => {
    const { result } = renderHook(() =>
      useWebSocket({ url: 'ws://test', autoConnect: true, reconnect: false })
    );

    await act(async () => {
      vi.advanceTimersByTime(10);
    });

    expect(result.current.status).toBe('connected');

    act(() => {
      result.current.disconnect();
    });

    expect(result.current.status).toBe('disconnected');
  });

  it('should have null lastMessage initially', () => {
    const { result } = renderHook(() =>
      useWebSocket({ url: 'ws://test', autoConnect: false })
    );
    expect(result.current.lastMessage).toBeNull();
  });

  it('should expose send, connect, disconnect functions', () => {
    const { result } = renderHook(() =>
      useWebSocket({ url: 'ws://test', autoConnect: false })
    );
    expect(typeof result.current.send).toBe('function');
    expect(typeof result.current.connect).toBe('function');
    expect(typeof result.current.disconnect).toBe('function');
  });
});
