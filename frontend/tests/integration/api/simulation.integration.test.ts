/**
 * Integration Tests for Simulation REST APIs
 * IT-INT-001: POST /api/v1/simulation/start
 * IT-INT-002: POST /api/v1/simulation/pause
 * IT-INT-003: POST /api/v1/simulation/resume
 * IT-INT-004: POST /api/v1/simulation/speed
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useSimulation } from '../../../src/hooks/useSimulation';
import { apiClient } from '../../../src/services/api';
import { ATTACK_SCENARIOS } from '../../../src/components/demo/types';

vi.mock('../../../src/services/api', () => ({
  apiClient: {
    post: vi.fn(),
  },
}));

const mockedApiClient = vi.mocked(apiClient);

beforeEach(() => {
  vi.clearAllMocks();
});

const apt29Scenario = ATTACK_SCENARIOS[0]; // APT29

describe('IT-INT-001: POST /api/v1/simulation/start', () => {
  it('should start simulation with scenario', async () => {
    mockedApiClient.post.mockResolvedValueOnce({ data: { session_id: 'sess-123' } });

    const { result } = renderHook(() => useSimulation());
    await act(async () => {
      await result.current.start(apt29Scenario);
    });

    expect(mockedApiClient.post).toHaveBeenCalledWith('/api/v1/simulation/start', {
      scenario_id: apt29Scenario.id,
    });
    expect(result.current.state.sessionId).toBe('sess-123');
  });

  it('should handle start failure', async () => {
    mockedApiClient.post.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useSimulation());
    const sessionId = await act(async () => {
      return await result.current.start(apt29Scenario);
    });

    expect(sessionId).toBeNull();
    expect(result.current.state.error).toBe('Network error');
  });
});

describe('IT-INT-002: POST /api/v1/simulation/pause', () => {
  it('should pause simulation', async () => {
    mockedApiClient.post.mockResolvedValueOnce({ data: {} });

    const { result } = renderHook(() => useSimulation());
    await act(async () => {
      await result.current.pause('sess-123');
    });

    expect(mockedApiClient.post).toHaveBeenCalledWith('/api/v1/simulation/pause', {
      session_id: 'sess-123',
    });
  });
});

describe('IT-INT-003: POST /api/v1/simulation/resume', () => {
  it('should resume simulation', async () => {
    mockedApiClient.post.mockResolvedValueOnce({ data: {} });

    const { result } = renderHook(() => useSimulation());
    await act(async () => {
      await result.current.resume('sess-123');
    });

    expect(mockedApiClient.post).toHaveBeenCalledWith('/api/v1/simulation/resume', {
      session_id: 'sess-123',
    });
  });
});

describe('IT-INT-004: POST /api/v1/simulation/speed', () => {
  it('should change simulation speed', async () => {
    mockedApiClient.post.mockResolvedValueOnce({ data: {} });

    const { result } = renderHook(() => useSimulation());
    await act(async () => {
      await result.current.setSpeed('sess-123', 2);
    });

    expect(mockedApiClient.post).toHaveBeenCalledWith('/api/v1/simulation/speed', {
      session_id: 'sess-123',
      speed: 2,
    });
  });
});
