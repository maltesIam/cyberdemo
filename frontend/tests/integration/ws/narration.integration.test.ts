/**
 * Integration Tests for WebSocket Narration Events
 * IT-INT-007: WebSocket /api/v1/narration/ws/{session}
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useNarration } from '../../../src/hooks/useNarration';

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

describe('IT-INT-007: WebSocket Narration Events', () => {
  it('should connect when sessionId is provided', () => {
    renderHook(() => useNarration('sess-456'));

    expect(mockWsInstances.length).toBeGreaterThanOrEqual(1);
    expect(getLatestWs().url).toContain('/narration/ws/sess-456');
  });

  it('should not connect when sessionId is null', () => {
    renderHook(() => useNarration(null));

    expect(mockWsInstances).toHaveLength(0);
  });

  it('should receive and buffer narration messages', () => {
    const { result } = renderHook(() => useNarration('sess-456'));

    const ws = getLatestWs();

    act(() => {
      ws.onopen?.(new Event('open'));
    });

    act(() => {
      ws.onmessage?.({
        data: JSON.stringify({
          id: 'msg-1',
          timestamp: '2026-02-24T10:00:00Z',
          type: 'info',
          content: 'Simulation started - APT29 scenario',
        }),
      } as MessageEvent);
    });

    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0].content).toBe('Simulation started - APT29 scenario');
    expect(result.current.messages[0].type).toBe('info');
  });

  it('should handle warning and error message types', () => {
    const { result } = renderHook(() => useNarration('sess-456'));

    const ws = getLatestWs();

    act(() => {
      ws.onopen?.(new Event('open'));
    });

    act(() => {
      ws.onmessage?.({
        data: JSON.stringify({
          id: 'msg-warn',
          type: 'warning',
          content: 'Lateral movement detected',
        }),
      } as MessageEvent);
    });

    act(() => {
      ws.onmessage?.({
        data: JSON.stringify({
          id: 'msg-err',
          type: 'error',
          content: 'Critical: Data exfiltration in progress',
        }),
      } as MessageEvent);
    });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[0].type).toBe('warning');
    expect(result.current.messages[1].type).toBe('error');
  });

  it('should toggle expanded state', () => {
    const { result } = renderHook(() => useNarration('sess-456'));

    expect(result.current.isExpanded).toBe(false);

    act(() => {
      result.current.toggleExpanded();
    });

    expect(result.current.isExpanded).toBe(true);
  });

  it('should clear all messages', () => {
    const { result } = renderHook(() => useNarration('sess-456'));

    const ws = getLatestWs();

    act(() => {
      ws.onopen?.(new Event('open'));
    });

    act(() => {
      ws.onmessage?.({
        data: JSON.stringify({ id: 'msg-1', type: 'info', content: 'test' }),
      } as MessageEvent);
    });

    expect(result.current.messages).toHaveLength(1);

    act(() => {
      result.current.clearMessages();
    });

    expect(result.current.messages).toHaveLength(0);
  });
});
