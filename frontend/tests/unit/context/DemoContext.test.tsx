/**
 * Tests for DemoContext provider
 * UT-TECH-001: DemoContext with simulation, narration, aIP, analysis state
 */
import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import React from 'react';
import { DemoProvider, useDemoContext, useDemoState, useDemoActions } from '../../../src/context/DemoContext';
import { ATTACK_SCENARIOS } from '../../../src/components/demo/types';

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <DemoProvider>{children}</DemoProvider>
);

describe('DemoContext', () => {
  it('should provide initial state', () => {
    const { result } = renderHook(() => useDemoState(), { wrapper });
    expect(result.current.playState).toBe('stopped');
    expect(result.current.speed).toBe(1);
    expect(result.current.selectedScenario).toBeNull();
    expect(result.current.currentStage).toBe(0);
    expect(result.current.stages).toEqual([]);
  });

  it('should throw when used outside provider', () => {
    expect(() => {
      renderHook(() => useDemoContext());
    }).toThrow('useDemoContext must be used within a DemoProvider');
  });

  it('should select scenario', () => {
    const { result } = renderHook(() => useDemoContext(), { wrapper });

    act(() => {
      result.current.actions.selectScenario(ATTACK_SCENARIOS[0]);
    });

    expect(result.current.state.selectedScenario?.id).toBe('apt29');
    expect(result.current.state.stages.length).toBeGreaterThan(0);
  });

  it('should play/pause/stop', () => {
    const { result } = renderHook(() => useDemoContext(), { wrapper });

    // Select scenario first
    act(() => {
      result.current.actions.selectScenario(ATTACK_SCENARIOS[0]);
    });

    // Play
    act(() => {
      result.current.actions.play();
    });
    expect(result.current.state.playState).toBe('playing');
    expect(result.current.state.sessionId).toBeTruthy();

    // Pause
    act(() => {
      result.current.actions.pause();
    });
    expect(result.current.state.playState).toBe('paused');

    // Stop
    act(() => {
      result.current.actions.stop();
    });
    expect(result.current.state.playState).toBe('stopped');
    expect(result.current.state.sessionId).toBeNull();
  });

  it('should set speed', () => {
    const { result } = renderHook(() => useDemoContext(), { wrapper });

    act(() => {
      result.current.actions.setSpeed(2);
    });

    expect(result.current.state.speed).toBe(2);
  });

  it('should advance stage', () => {
    const { result } = renderHook(() => useDemoContext(), { wrapper });

    act(() => {
      result.current.actions.selectScenario(ATTACK_SCENARIOS[0]);
    });

    act(() => {
      result.current.actions.advanceStage();
    });

    expect(result.current.state.currentStage).toBe(1);
    expect(result.current.state.stages[0].completed).toBe(true);
    expect(result.current.state.stages[1].active).toBe(true);
  });

  it('should toggle play/pause', () => {
    const { result } = renderHook(() => useDemoContext(), { wrapper });

    act(() => {
      result.current.actions.selectScenario(ATTACK_SCENARIOS[0]);
    });

    act(() => {
      result.current.actions.togglePlayPause();
    });
    expect(result.current.state.playState).toBe('playing');

    act(() => {
      result.current.actions.togglePlayPause();
    });
    expect(result.current.state.playState).toBe('paused');
  });

  it('should reset demo', () => {
    const { result } = renderHook(() => useDemoContext(), { wrapper });

    act(() => {
      result.current.actions.selectScenario(ATTACK_SCENARIOS[0]);
      result.current.actions.play();
    });

    act(() => {
      result.current.actions.resetDemo();
    });

    expect(result.current.state.playState).toBe('stopped');
    expect(result.current.state.selectedScenario).toBeNull();
  });

  it('should provide separate state and actions hooks', () => {
    const { result: stateResult } = renderHook(() => useDemoState(), { wrapper });
    const { result: actionsResult } = renderHook(() => useDemoActions(), { wrapper });

    expect(stateResult.current.playState).toBe('stopped');
    expect(typeof actionsResult.current.play).toBe('function');
    expect(typeof actionsResult.current.pause).toBe('function');
    expect(typeof actionsResult.current.stop).toBe('function');
  });
});
