/**
 * Integration Tests for DemoControlBar
 * IT-001: DemoControlBar interacts with DemoContext for simulation control
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { DemoControlBar } from '../../src/components/demo/DemoControlBar';
import type { DemoState, AttackScenario, SpeedMultiplier } from '../../src/components/demo/types';
import { ATTACK_SCENARIOS } from '../../src/components/demo/types';

const mockScenario = ATTACK_SCENARIOS[0];

const createState = (overrides?: Partial<DemoState>): DemoState => ({
  playState: 'stopped',
  speed: 1,
  selectedScenario: null,
  currentStage: 0,
  stages: [],
  sessionId: null,
  startedAt: null,
  ...overrides,
});

describe('IT-001: DemoControlBar integration with simulation state', () => {
  it('should flow through select → play → pause → stop lifecycle', () => {
    const onPlay = vi.fn();
    const onPause = vi.fn();
    const onStop = vi.fn();
    const onScenarioSelect = vi.fn();
    const onSpeedChange = vi.fn();

    // Initial render: stopped state
    const { rerender } = render(
      <DemoControlBar
        state={createState()}
        onPlay={onPlay}
        onPause={onPause}
        onStop={onStop}
        onSpeedChange={onSpeedChange}
        onScenarioSelect={onScenarioSelect}
      />
    );
    expect(screen.getByLabelText('Play')).toBeDisabled();

    // After scenario selected: play enabled
    rerender(
      <DemoControlBar
        state={createState({ selectedScenario: mockScenario })}
        onPlay={onPlay}
        onPause={onPause}
        onStop={onStop}
        onSpeedChange={onSpeedChange}
        onScenarioSelect={onScenarioSelect}
      />
    );
    expect(screen.getByLabelText('Play')).not.toBeDisabled();
    fireEvent.click(screen.getByLabelText('Play'));
    expect(onPlay).toHaveBeenCalled();

    // After playing: pause button visible
    rerender(
      <DemoControlBar
        state={createState({ playState: 'playing', selectedScenario: mockScenario })}
        onPlay={onPlay}
        onPause={onPause}
        onStop={onStop}
        onSpeedChange={onSpeedChange}
        onScenarioSelect={onScenarioSelect}
      />
    );
    expect(screen.getByLabelText('Pause')).toBeInTheDocument();
    fireEvent.click(screen.getByLabelText('Stop'));
    expect(onStop).toHaveBeenCalled();
  });

  it('should update speed through slider', () => {
    const onSpeedChange = vi.fn();
    render(
      <DemoControlBar
        state={createState({ selectedScenario: mockScenario })}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={onSpeedChange}
        onScenarioSelect={vi.fn()}
      />
    );
    fireEvent.change(screen.getByRole('slider'), { target: { value: '4' } });
    expect(onSpeedChange).toHaveBeenCalledWith(4);
  });

  it('should render MITRE progress when stages exist', () => {
    render(
      <DemoControlBar
        state={createState({
          selectedScenario: mockScenario,
          stages: [
            { index: 0, tacticId: 'TA0001', tacticName: 'Recon', techniqueIds: [], completed: true, active: false },
            { index: 1, tacticId: 'TA0002', tacticName: 'Exec', techniqueIds: [], completed: false, active: true },
          ],
        })}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
      />
    );
    expect(screen.getByTestId('phase-circle-TA0001')).toBeInTheDocument();
    expect(screen.getByTestId('phase-circle-TA0002')).toBeInTheDocument();
  });
});
