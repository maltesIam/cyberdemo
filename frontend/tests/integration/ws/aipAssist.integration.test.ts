/**
 * Integration Tests for WebSocket aIP Assist Events
 * IT-INT-008: WebSocket /api/v1/aip-assist/ws/{session}
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useAipSuggestions } from '../../../src/hooks/useAipSuggestions';

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

describe('IT-INT-008: WebSocket aIP Assist Events', () => {
  it('should connect to aIP assist WebSocket', () => {
    renderHook(() => useAipSuggestions('sess-789'));

    expect(mockWsInstances.length).toBeGreaterThanOrEqual(1);
    expect(getLatestWs().url).toContain('/api/v1/aip-assist/ws/sess-789');
  });

  it('should not connect when sessionId is null', () => {
    renderHook(() => useAipSuggestions(null));

    expect(mockWsInstances).toHaveLength(0);
  });

  it('should receive suggestion messages and update state', () => {
    const { result } = renderHook(() => useAipSuggestions('sess-789'));

    const ws = getLatestWs();

    act(() => {
      ws.onopen?.(new Event('open'));
    });

    act(() => {
      ws.onmessage?.({
        data: JSON.stringify({
          type: 'suggestion',
          id: 'sug-1',
          suggestion_type: 'action',
          title: 'Isolate compromised host',
          description: 'Host 10.0.0.5 shows signs of compromise',
          confidence: 'high',
          timestamp: '2026-02-24T10:00:00Z',
        }),
      } as MessageEvent);
    });

    expect(result.current.suggestions).toHaveLength(1);
    expect(result.current.suggestions[0].title).toBe('Isolate compromised host');
    expect(result.current.suggestions[0].confidence).toBe('high');
    expect(result.current.suggestions[0].isRead).toBe(false);
    expect(result.current.unreadCount).toBe(1);
  });

  it('should handle thinking indicator messages', () => {
    const { result } = renderHook(() => useAipSuggestions('sess-789'));

    const ws = getLatestWs();

    act(() => {
      ws.onopen?.(new Event('open'));
    });

    act(() => {
      ws.onmessage?.({
        data: JSON.stringify({ type: 'thinking', active: true }),
      } as MessageEvent);
    });

    expect(result.current.isThinking).toBe(true);

    act(() => {
      ws.onmessage?.({
        data: JSON.stringify({
          type: 'suggestion',
          id: 'sug-1',
          title: 'Test',
          description: 'Test',
        }),
      } as MessageEvent);
    });

    expect(result.current.isThinking).toBe(false);
  });

  it('should accept suggestions with WebSocket notification', () => {
    const { result } = renderHook(() => useAipSuggestions('sess-789'));

    const ws = getLatestWs();

    act(() => {
      ws.onopen?.(new Event('open'));
      ws.readyState = 1;
    });

    act(() => {
      ws.onmessage?.({
        data: JSON.stringify({
          type: 'suggestion',
          id: 'sug-1',
          title: 'Test',
          description: 'Test',
        }),
      } as MessageEvent);
    });

    act(() => {
      result.current.acceptSuggestion('sug-1');
    });

    expect(result.current.suggestions[0].status).toBe('accepted');
    expect(ws.send).toHaveBeenCalledWith(
      JSON.stringify({ type: 'accept', suggestion_id: 'sug-1' })
    );
  });

  it('should track read state and compute stats', () => {
    const { result } = renderHook(() => useAipSuggestions('sess-789'));

    const ws = getLatestWs();

    act(() => {
      ws.onopen?.(new Event('open'));
    });

    act(() => {
      ws.onmessage?.({
        data: JSON.stringify({
          type: 'suggestion',
          id: 'sug-1',
          title: 'First',
          description: 'Test 1',
        }),
      } as MessageEvent);
    });

    act(() => {
      ws.onmessage?.({
        data: JSON.stringify({
          type: 'suggestion',
          id: 'sug-2',
          title: 'Second',
          description: 'Test 2',
        }),
      } as MessageEvent);
    });

    expect(result.current.unreadCount).toBe(2);
    expect(result.current.stats.totalSuggestions).toBe(2);

    act(() => {
      result.current.markAsRead('sug-1');
    });

    expect(result.current.unreadCount).toBe(1);
  });
});
