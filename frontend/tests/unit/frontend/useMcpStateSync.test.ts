/**
 * UT-001: useMcpStateSync hook tests
 * REQ-001-001-001: WebSocket state sync between React and MCP WS Server
 * TECH-001: useMcpStateSync hook interface
 * NFR-002: WS auto-reconnect with exponential backoff
 * NFR-004: No memory leaks from WS connections
 * INT-001: WebSocket protocol for React to MCP WS Server
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useMcpStateSync } from '../../../src/hooks/useMcpStateSync';
import type { McpStateUpdate } from '../../../src/types/mcpState';

// Mock WebSocket with controllable behavior
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;
  static instances: MockWebSocket[] = [];

  url: string;
  readyState: number = MockWebSocket.CONNECTING;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    MockWebSocket.instances.push(this);
  }

  send = vi.fn();
  close = vi.fn(() => {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.(new CloseEvent('close'));
  });

  // Test helpers
  simulateOpen() {
    this.readyState = MockWebSocket.OPEN;
    this.onopen?.(new Event('open'));
  }

  simulateMessage(data: McpStateUpdate) {
    this.onmessage?.(new MessageEvent('message', { data: JSON.stringify(data) }));
  }

  simulateClose() {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.(new CloseEvent('close'));
  }

  simulateError() {
    this.readyState = MockWebSocket.CLOSED;
    this.onerror?.(new Event('error'));
  }
}

describe('useMcpStateSync', () => {
  let originalWebSocket: typeof WebSocket;

  beforeEach(() => {
    originalWebSocket = global.WebSocket;
    (global as any).WebSocket = MockWebSocket;
    MockWebSocket.instances = [];
    vi.useFakeTimers();
  });

  afterEach(() => {
    global.WebSocket = originalWebSocket;
    vi.useRealTimers();
  });

  it('should connect to the MCP WS Server on port 3001 by default', () => {
    renderHook(() => useMcpStateSync());
    expect(MockWebSocket.instances.length).toBe(1);
    expect(MockWebSocket.instances[0].url).toContain('3001');
  });

  it('should accept a custom URL', () => {
    renderHook(() => useMcpStateSync({ url: 'ws://custom:9999/ws' }));
    expect(MockWebSocket.instances[0].url).toBe('ws://custom:9999/ws');
  });

  it('should start with connecting status', () => {
    const { result } = renderHook(() => useMcpStateSync());
    expect(result.current.connectionStatus).toBe('connecting');
    expect(result.current.isConnected).toBe(false);
  });

  it('should transition to connected when WS opens', () => {
    const { result } = renderHook(() => useMcpStateSync());
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });
    expect(result.current.connectionStatus).toBe('connected');
    expect(result.current.isConnected).toBe(true);
  });

  it('should have empty initial state', () => {
    const { result } = renderHook(() => useMcpStateSync());
    expect(result.current.state).toEqual({});
  });

  it('should update state when receiving a valid JSON message', () => {
    const { result } = renderHook(() => useMcpStateSync());
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    const stateUpdate: McpStateUpdate = {
      currentPage: '/dashboard',
      highlightedAssets: [{ assetId: 'asset-1', mode: 'pulse' }],
    };

    act(() => {
      MockWebSocket.instances[0].simulateMessage(stateUpdate);
    });

    expect(result.current.state.currentPage).toBe('/dashboard');
    expect(result.current.state.highlightedAssets).toHaveLength(1);
    expect(result.current.state.highlightedAssets![0].assetId).toBe('asset-1');
  });

  it('should merge successive state updates', () => {
    const { result } = renderHook(() => useMcpStateSync());
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    act(() => {
      MockWebSocket.instances[0].simulateMessage({ currentPage: '/dashboard' });
    });
    act(() => {
      MockWebSocket.instances[0].simulateMessage({
        charts: [{ id: 'c1', title: 'Test', type: 'bar', data: [] }],
      });
    });

    expect(result.current.state.currentPage).toBe('/dashboard');
    expect(result.current.state.charts).toHaveLength(1);
  });

  it('should overwrite fields when a new update replaces them', () => {
    const { result } = renderHook(() => useMcpStateSync());
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    act(() => {
      MockWebSocket.instances[0].simulateMessage({ currentPage: '/dashboard' });
    });
    act(() => {
      MockWebSocket.instances[0].simulateMessage({ currentPage: '/incidents' });
    });

    expect(result.current.state.currentPage).toBe('/incidents');
  });

  it('should transition to disconnected when WS closes', () => {
    const { result } = renderHook(() => useMcpStateSync());
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });
    expect(result.current.connectionStatus).toBe('connected');

    act(() => {
      MockWebSocket.instances[0].simulateClose();
    });
    expect(result.current.connectionStatus).toBe('disconnected');
    expect(result.current.isConnected).toBe(false);
  });

  it('should auto-reconnect with exponential backoff after disconnect', () => {
    renderHook(() => useMcpStateSync());
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });
    act(() => {
      MockWebSocket.instances[0].simulateClose();
    });

    // First reconnect after 1000ms base delay
    expect(MockWebSocket.instances.length).toBe(1);
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(MockWebSocket.instances.length).toBe(2);

    // Second disconnect + reconnect after 2000ms
    act(() => {
      MockWebSocket.instances[1].simulateClose();
    });
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(MockWebSocket.instances.length).toBe(2); // not yet
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(MockWebSocket.instances.length).toBe(3);
  });

  it('should reset reconnect attempts after successful connection', () => {
    renderHook(() => useMcpStateSync());

    // First connection and disconnect
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });
    act(() => {
      MockWebSocket.instances[0].simulateClose();
    });
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(MockWebSocket.instances.length).toBe(2);

    // Reconnect successfully
    act(() => {
      MockWebSocket.instances[1].simulateOpen();
    });
    // Disconnect again
    act(() => {
      MockWebSocket.instances[1].simulateClose();
    });

    // Should reconnect after 1000ms (reset backoff), not 2000ms
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(MockWebSocket.instances.length).toBe(3);
  });

  it('should stop reconnecting after max attempts', () => {
    renderHook(() => useMcpStateSync({ maxReconnectAttempts: 2 }));

    // Attempt 1
    act(() => {
      MockWebSocket.instances[0].simulateClose();
    });
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(MockWebSocket.instances.length).toBe(2);

    // Attempt 2
    act(() => {
      MockWebSocket.instances[1].simulateClose();
    });
    act(() => {
      vi.advanceTimersByTime(2000);
    });
    expect(MockWebSocket.instances.length).toBe(3);

    // Attempt 3 - should NOT reconnect (max was 2)
    act(() => {
      MockWebSocket.instances[2].simulateClose();
    });
    act(() => {
      vi.advanceTimersByTime(10000);
    });
    expect(MockWebSocket.instances.length).toBe(3);
  });

  it('should cleanup WS connection on unmount (no memory leaks)', () => {
    const { unmount } = renderHook(() => useMcpStateSync());
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });
    expect(MockWebSocket.instances[0].close).not.toHaveBeenCalled();

    unmount();
    expect(MockWebSocket.instances[0].close).toHaveBeenCalled();
  });

  it('should expose reconnect function', () => {
    const { result } = renderHook(() => useMcpStateSync());
    expect(typeof result.current.reconnect).toBe('function');
  });

  it('should expose disconnect function', () => {
    const { result } = renderHook(() => useMcpStateSync());
    expect(typeof result.current.disconnect).toBe('function');
  });

  it('should manually reconnect when reconnect is called', () => {
    const { result } = renderHook(() => useMcpStateSync());
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    act(() => {
      result.current.disconnect();
    });

    const countBefore = MockWebSocket.instances.length;
    act(() => {
      result.current.reconnect();
    });
    expect(MockWebSocket.instances.length).toBe(countBefore + 1);
  });

  it('should call onStateUpdate callback when state changes', () => {
    const onStateUpdate = vi.fn();
    renderHook(() => useMcpStateSync({ onStateUpdate }));
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    const update: McpStateUpdate = { currentPage: '/dashboard' };
    act(() => {
      MockWebSocket.instances[0].simulateMessage(update);
    });

    expect(onStateUpdate).toHaveBeenCalledWith(expect.objectContaining({ currentPage: '/dashboard' }));
  });

  it('should ignore invalid JSON messages', () => {
    const { result } = renderHook(() => useMcpStateSync());
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    // Send invalid JSON directly
    act(() => {
      MockWebSocket.instances[0].onmessage?.(
        new MessageEvent('message', { data: 'not-json{' })
      );
    });

    // State should remain empty
    expect(result.current.state).toEqual({});
  });
});
