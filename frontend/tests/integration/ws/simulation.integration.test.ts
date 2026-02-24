/**
 * Integration Tests for WebSocket Simulation Events
 * IT-INT-005: WebSocket /api/v1/simulation/ws/{session}
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useWebSocket } from '../../../src/hooks/useWebSocket';

let mockWsInstances: MockWS[];

class MockWS {
  static OPEN = 1;
  static CONNECTING = 0;
  static CLOSING = 2;
  static CLOSED = 3;

  url: string;
  onopen: ((e: Event) => void) | null = null;
  onclose: ((e: CloseEvent) => void) | null = null;
  onerror: ((e: Event) => void) | null = null;
  onmessage: ((e: MessageEvent) => void) | null = null;
  readyState = 0;
  close = vi.fn();
  send = vi.fn();

  constructor(url: string) {
    this.url = url;
    mockWsInstances.push(this);
  }
}

beforeEach(() => {
  mockWsInstances = [];
  vi.stubGlobal('WebSocket', MockWS);
});

afterEach(() => {
  vi.restoreAllMocks();
});

function getLatestWs(): MockWS {
  return mockWsInstances[mockWsInstances.length - 1];
}

describe('IT-INT-005: WebSocket Simulation Events', () => {
  it('should connect to simulation WebSocket URL', () => {
    renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/api/v1/simulation/ws/sess-123',
        autoConnect: true,
        reconnect: false,
      })
    );

    expect(mockWsInstances.length).toBeGreaterThanOrEqual(1);
    expect(getLatestWs().url).toBe('ws://localhost:8000/api/v1/simulation/ws/sess-123');
  });

  it('should report connected status when WebSocket opens', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/api/v1/simulation/ws/sess-123',
        autoConnect: true,
        reconnect: false,
      })
    );

    expect(result.current.status).toBe('connecting');

    act(() => {
      getLatestWs().onopen?.(new Event('open'));
    });

    expect(result.current.status).toBe('connected');
  });

  it('should receive and parse simulation event messages', () => {
    const onMessage = vi.fn();
    renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/api/v1/simulation/ws/sess-123',
        onMessage,
        autoConnect: true,
        reconnect: false,
      })
    );

    const ws = getLatestWs();

    act(() => {
      ws.onopen?.(new Event('open'));
    });

    const event = {
      type: 'phase_change',
      phase: 2,
      tactic: 'Execution',
      timestamp: '2026-02-24T10:00:00Z',
    };

    act(() => {
      ws.onmessage?.({ data: JSON.stringify(event) } as MessageEvent);
    });

    expect(onMessage).toHaveBeenCalledWith(event);
  });

  it('should send messages through WebSocket', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/api/v1/simulation/ws/sess-123',
        autoConnect: true,
        reconnect: false,
      })
    );

    const ws = getLatestWs();

    act(() => {
      ws.onopen?.(new Event('open'));
      ws.readyState = 1; // OPEN
    });

    act(() => {
      result.current.send({ type: 'control', action: 'pause' });
    });

    expect(ws.send).toHaveBeenCalledWith(
      JSON.stringify({ type: 'control', action: 'pause' })
    );
  });

  it('should handle disconnection', () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/api/v1/simulation/ws/sess-123',
        autoConnect: true,
        reconnect: false,
      })
    );

    const ws = getLatestWs();

    act(() => {
      ws.onopen?.(new Event('open'));
    });

    expect(result.current.status).toBe('connected');

    act(() => {
      ws.onclose?.({} as CloseEvent);
    });

    expect(result.current.status).toBe('disconnected');
  });
});
