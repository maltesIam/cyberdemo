/**
 * useSimulation - Hook wrapping REST API calls for simulation control
 *
 * TECH-002: Implements start, pause, resume, speed REST API calls
 */

import { useState, useCallback } from 'react';
import { apiClient } from '../services/api';
import type { SpeedMultiplier, AttackScenario } from '../components/demo/types';

export interface SimulationApiState {
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
}

export interface UseSimulationReturn {
  state: SimulationApiState;
  start: (scenario: AttackScenario) => Promise<string | null>;
  pause: (sessionId: string) => Promise<boolean>;
  resume: (sessionId: string) => Promise<boolean>;
  setSpeed: (sessionId: string, speed: SpeedMultiplier) => Promise<boolean>;
  clearError: () => void;
}

export function useSimulation(): UseSimulationReturn {
  const [state, setState] = useState<SimulationApiState>({
    isLoading: false,
    error: null,
    sessionId: null,
  });

  const start = useCallback(async (scenario: AttackScenario): Promise<string | null> => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const response = await apiClient.post('/api/v1/simulation/start', {
        scenario_id: scenario.id,
      });
      const sessionId = response.data?.session_id ?? null;
      setState({ isLoading: false, error: null, sessionId });
      return sessionId;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to start simulation';
      setState((prev) => ({ ...prev, isLoading: false, error: message }));
      return null;
    }
  }, []);

  const pause = useCallback(async (sessionId: string): Promise<boolean> => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      await apiClient.post('/api/v1/simulation/pause', { session_id: sessionId });
      setState((prev) => ({ ...prev, isLoading: false }));
      return true;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to pause simulation';
      setState((prev) => ({ ...prev, isLoading: false, error: message }));
      return false;
    }
  }, []);

  const resume = useCallback(async (sessionId: string): Promise<boolean> => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      await apiClient.post('/api/v1/simulation/resume', { session_id: sessionId });
      setState((prev) => ({ ...prev, isLoading: false }));
      return true;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to resume simulation';
      setState((prev) => ({ ...prev, isLoading: false, error: message }));
      return false;
    }
  }, []);

  const setSpeed = useCallback(async (sessionId: string, speed: SpeedMultiplier): Promise<boolean> => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      await apiClient.post('/api/v1/simulation/speed', {
        session_id: sessionId,
        speed,
      });
      setState((prev) => ({ ...prev, isLoading: false }));
      return true;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to set speed';
      setState((prev) => ({ ...prev, isLoading: false, error: message }));
      return false;
    }
  }, []);

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  return { state, start, pause, resume, setSpeed, clearError };
}
