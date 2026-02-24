/**
 * Tests for useSimulation hook
 * UT-TECH-002: Wraps REST API calls for start, pause, resume, speed
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useSimulation } from '../../../src/hooks/useSimulation';

// Mock axios
vi.mock('../../../src/services/api', () => ({
  apiClient: {
    post: vi.fn(),
  },
}));

import { apiClient } from '../../../src/services/api';

const mockPost = vi.mocked(apiClient.post);

describe('useSimulation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should have correct initial state', () => {
    const { result } = renderHook(() => useSimulation());
    expect(result.current.state.isLoading).toBe(false);
    expect(result.current.state.error).toBeNull();
    expect(result.current.state.sessionId).toBeNull();
  });

  it('should start simulation and return session ID', async () => {
    mockPost.mockResolvedValueOnce({ data: { session_id: 'session-123' } });

    const { result } = renderHook(() => useSimulation());
    let sessionId: string | null = null;

    await act(async () => {
      sessionId = await result.current.start({
        id: 'apt29',
        name: 'APT29',
        description: 'test',
        category: 'APT',
        stages: 8,
      });
    });

    expect(sessionId).toBe('session-123');
    expect(result.current.state.sessionId).toBe('session-123');
    expect(result.current.state.isLoading).toBe(false);
    expect(mockPost).toHaveBeenCalledWith('/api/v1/simulation/start', {
      scenario_id: 'apt29',
    });
  });

  it('should handle start error', async () => {
    mockPost.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useSimulation());
    let sessionId: string | null = null;

    await act(async () => {
      sessionId = await result.current.start({
        id: 'apt29',
        name: 'APT29',
        description: 'test',
        category: 'APT',
        stages: 8,
      });
    });

    expect(sessionId).toBeNull();
    expect(result.current.state.error).toBe('Network error');
  });

  it('should pause simulation', async () => {
    mockPost.mockResolvedValueOnce({ data: { success: true } });

    const { result } = renderHook(() => useSimulation());
    let success = false;

    await act(async () => {
      success = await result.current.pause('session-123');
    });

    expect(success).toBe(true);
    expect(mockPost).toHaveBeenCalledWith('/api/v1/simulation/pause', {
      session_id: 'session-123',
    });
  });

  it('should resume simulation', async () => {
    mockPost.mockResolvedValueOnce({ data: { success: true } });

    const { result } = renderHook(() => useSimulation());
    let success = false;

    await act(async () => {
      success = await result.current.resume('session-123');
    });

    expect(success).toBe(true);
    expect(mockPost).toHaveBeenCalledWith('/api/v1/simulation/resume', {
      session_id: 'session-123',
    });
  });

  it('should set speed', async () => {
    mockPost.mockResolvedValueOnce({ data: { success: true } });

    const { result } = renderHook(() => useSimulation());
    let success = false;

    await act(async () => {
      success = await result.current.setSpeed('session-123', 2);
    });

    expect(success).toBe(true);
    expect(mockPost).toHaveBeenCalledWith('/api/v1/simulation/speed', {
      session_id: 'session-123',
      speed: 2,
    });
  });

  it('should handle pause error', async () => {
    mockPost.mockRejectedValueOnce(new Error('Pause failed'));

    const { result } = renderHook(() => useSimulation());

    await act(async () => {
      await result.current.pause('session-123');
    });

    expect(result.current.state.error).toBe('Pause failed');
  });

  it('should clear error', async () => {
    mockPost.mockRejectedValueOnce(new Error('Some error'));

    const { result } = renderHook(() => useSimulation());

    await act(async () => {
      await result.current.start({
        id: 'apt29',
        name: 'APT29',
        description: 'test',
        category: 'APT',
        stages: 8,
      });
    });

    expect(result.current.state.error).toBe('Some error');

    act(() => {
      result.current.clearError();
    });

    expect(result.current.state.error).toBeNull();
  });
});
