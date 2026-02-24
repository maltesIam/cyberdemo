/**
 * UT-006: Graceful degradation tests
 * REQ-001-001-006: App works normally when WS Server is unavailable
 * NFR-003: Graceful degradation if WS down
 *
 * Tests that useMcpStateSync provides sensible defaults and
 * the app can function without the WS server being available.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useMcpStateSync } from '../../../src/hooks/useMcpStateSync';
import type { McpStateUpdate } from '../../../src/types/mcpState';

// Mock WebSocket that fails immediately
class FailingWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;
  static instances: FailingWebSocket[] = [];

  url: string;
  readyState: number = FailingWebSocket.CONNECTING;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    FailingWebSocket.instances.push(this);
    // Simulate immediate connection failure
    setTimeout(() => {
      this.readyState = FailingWebSocket.CLOSED;
      this.onerror?.(new Event('error'));
      this.onclose?.(new CloseEvent('close'));
    }, 0);
  }

  send = vi.fn();
  close = vi.fn(() => {
    this.readyState = FailingWebSocket.CLOSED;
  });
}

// Mock WebSocket that throws on construction
class ThrowingWebSocket {
  constructor() {
    throw new Error('WebSocket not supported');
  }
}

describe('Graceful Degradation (WS Unavailable)', () => {
  let originalWebSocket: typeof WebSocket;

  beforeEach(() => {
    originalWebSocket = global.WebSocket;
    vi.useFakeTimers();
  });

  afterEach(() => {
    global.WebSocket = originalWebSocket;
    vi.useRealTimers();
  });

  it('should not crash when WS connection fails immediately', () => {
    (global as any).WebSocket = FailingWebSocket;
    FailingWebSocket.instances = [];

    const { result } = renderHook(() => useMcpStateSync({ maxReconnectAttempts: 0 }));

    act(() => {
      vi.advanceTimersByTime(10);
    });

    // Hook should still return valid state
    expect(result.current.state).toEqual({});
    expect(result.current.isConnected).toBe(false);
  });

  it('should not crash when WebSocket constructor throws', () => {
    (global as any).WebSocket = ThrowingWebSocket;

    const { result } = renderHook(() => useMcpStateSync({ maxReconnectAttempts: 0 }));

    // Hook should still return valid state
    expect(result.current.state).toEqual({});
    expect(result.current.connectionStatus).toBe('error');
    expect(result.current.isConnected).toBe(false);
  });

  it('should provide empty default state that allows normal app operation', () => {
    (global as any).WebSocket = FailingWebSocket;
    FailingWebSocket.instances = [];

    const { result } = renderHook(() => useMcpStateSync({ maxReconnectAttempts: 0 }));

    act(() => {
      vi.advanceTimersByTime(10);
    });

    // All state fields should be undefined (empty object), not throwing
    expect(result.current.state.currentPage).toBeUndefined();
    expect(result.current.state.highlightedAssets).toBeUndefined();
    expect(result.current.state.charts).toBeUndefined();
    expect(result.current.state.timeline).toBeUndefined();
    expect(result.current.state.kpiOverrides).toBeUndefined();
  });

  it('should still expose reconnect and disconnect functions when WS fails', () => {
    (global as any).WebSocket = FailingWebSocket;
    FailingWebSocket.instances = [];

    const { result } = renderHook(() => useMcpStateSync({ maxReconnectAttempts: 0 }));

    act(() => {
      vi.advanceTimersByTime(10);
    });

    expect(typeof result.current.reconnect).toBe('function');
    expect(typeof result.current.disconnect).toBe('function');

    // Calling disconnect should not throw
    expect(() => {
      act(() => {
        result.current.disconnect();
      });
    }).not.toThrow();
  });

  it('should allow reconnect attempt after initial failure', () => {
    (global as any).WebSocket = FailingWebSocket;
    FailingWebSocket.instances = [];

    const { result } = renderHook(() => useMcpStateSync({ maxReconnectAttempts: 0 }));

    act(() => {
      vi.advanceTimersByTime(10);
    });

    const instanceCountBefore = FailingWebSocket.instances.length;

    // Manual reconnect should create a new instance
    act(() => {
      result.current.reconnect();
    });

    expect(FailingWebSocket.instances.length).toBe(instanceCountBefore + 1);
  });

  it('should not error when unmounting during failed connection', () => {
    (global as any).WebSocket = FailingWebSocket;
    FailingWebSocket.instances = [];

    const { unmount } = renderHook(() => useMcpStateSync({ maxReconnectAttempts: 0 }));

    // Should not throw on unmount
    expect(() => {
      unmount();
    }).not.toThrow();
  });

  it('should preserve existing state if connection drops after receiving data', () => {
    // Use a controllable mock
    class ControllableMockWS {
      static CONNECTING = 0;
      static OPEN = 1;
      static CLOSING = 2;
      static CLOSED = 3;
      static instances: ControllableMockWS[] = [];

      url: string;
      readyState: number = ControllableMockWS.CONNECTING;
      onopen: ((event: Event) => void) | null = null;
      onclose: ((event: CloseEvent) => void) | null = null;
      onerror: ((event: Event) => void) | null = null;
      onmessage: ((event: MessageEvent) => void) | null = null;

      constructor(url: string) {
        this.url = url;
        ControllableMockWS.instances.push(this);
      }

      send = vi.fn();
      close = vi.fn(() => {
        this.readyState = ControllableMockWS.CLOSED;
        this.onclose?.(new CloseEvent('close'));
      });

      simulateOpen() {
        this.readyState = ControllableMockWS.OPEN;
        this.onopen?.(new Event('open'));
      }

      simulateMessage(data: McpStateUpdate) {
        this.onmessage?.(new MessageEvent('message', { data: JSON.stringify(data) }));
      }

      simulateClose() {
        this.readyState = ControllableMockWS.CLOSED;
        this.onclose?.(new CloseEvent('close'));
      }
    }

    (global as any).WebSocket = ControllableMockWS;
    ControllableMockWS.instances = [];

    const { result } = renderHook(() => useMcpStateSync({ maxReconnectAttempts: 0 }));

    // Connect and receive data
    act(() => {
      ControllableMockWS.instances[0].simulateOpen();
    });
    act(() => {
      ControllableMockWS.instances[0].simulateMessage({ currentPage: '/dashboard' });
    });
    expect(result.current.state.currentPage).toBe('/dashboard');

    // Connection drops
    act(() => {
      ControllableMockWS.instances[0].simulateClose();
    });

    // State should be preserved even though connection is lost
    expect(result.current.state.currentPage).toBe('/dashboard');
    expect(result.current.isConnected).toBe(false);
  });
});
