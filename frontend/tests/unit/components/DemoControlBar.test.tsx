/**
 * Tests for DemoControlBar Component
 * UT-001: Renders in header with all controls
 * UT-002: Scenario dropdown with 6 options
 * UT-003: Play/Pause/Stop buttons
 * UT-004: Speed slider 0.5x-4x
 * UT-005: MITRE progress circles (covered here + MitreProgress.test.tsx)
 * UT-006: Collapse/expand toggle
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { DemoControlBar } from '../../../src/components/demo/DemoControlBar';
import type { DemoState, MitreStage } from '../../../src/components/demo/types';

const createDefaultState = (overrides?: Partial<DemoState>): DemoState => ({
  playState: 'stopped',
  speed: 1,
  selectedScenario: null,
  currentStage: 0,
  stages: [],
  sessionId: null,
  startedAt: null,
  ...overrides,
});

const mockStages: MitreStage[] = [
  { index: 0, tacticId: 'TA0001', tacticName: 'Initial Access', techniqueIds: ['T1566'], completed: true, active: false },
  { index: 1, tacticId: 'TA0002', tacticName: 'Execution', techniqueIds: ['T1059'], completed: false, active: true },
  { index: 2, tacticId: 'TA0003', tacticName: 'Persistence', techniqueIds: ['T1547'], completed: false, active: false },
];

const mockScenario = {
  id: 'apt29',
  name: 'APT29 - Cozy Bear',
  description: 'Russian state-sponsored',
  category: 'Nation State',
  stages: 8,
};

describe('UT-001: DemoControlBar renders in header with all controls', () => {
  it('should render the control bar', () => {
    render(
      <DemoControlBar
        state={createDefaultState()}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
      />
    );
    expect(screen.getByTestId('demo-control-bar')).toBeInTheDocument();
  });

  it('should have accessible aria-label', () => {
    render(
      <DemoControlBar
        state={createDefaultState()}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
      />
    );
    expect(screen.getByLabelText('Demo simulation controls')).toBeInTheDocument();
  });
});

describe('UT-002: ScenarioDropdown with 6 options', () => {
  it('should render scenario dropdown', () => {
    render(
      <DemoControlBar
        state={createDefaultState()}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
      />
    );
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('should show "Select Scenario" when no scenario selected', () => {
    render(
      <DemoControlBar
        state={createDefaultState()}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
      />
    );
    expect(screen.getByText('Select Scenario')).toBeInTheDocument();
  });

  it('should show selected scenario name', () => {
    render(
      <DemoControlBar
        state={createDefaultState({ selectedScenario: mockScenario })}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
      />
    );
    expect(screen.getByText('APT29 - Cozy Bear')).toBeInTheDocument();
  });
});

describe('UT-003: Play/Pause/Stop buttons', () => {
  it('should render play button when stopped', () => {
    render(
      <DemoControlBar
        state={createDefaultState()}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
      />
    );
    expect(screen.getByLabelText('Play')).toBeInTheDocument();
    expect(screen.getByLabelText('Stop')).toBeInTheDocument();
  });

  it('should render pause button when playing', () => {
    render(
      <DemoControlBar
        state={createDefaultState({ playState: 'playing', selectedScenario: mockScenario })}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
      />
    );
    expect(screen.getByLabelText('Pause')).toBeInTheDocument();
  });

  it('should disable play when no scenario selected', () => {
    render(
      <DemoControlBar
        state={createDefaultState()}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
      />
    );
    expect(screen.getByLabelText('Play')).toBeDisabled();
  });

  it('should call onPlay when play clicked', () => {
    const onPlay = vi.fn();
    render(
      <DemoControlBar
        state={createDefaultState({ selectedScenario: mockScenario })}
        onPlay={onPlay}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
      />
    );
    fireEvent.click(screen.getByLabelText('Play'));
    expect(onPlay).toHaveBeenCalledTimes(1);
  });

  it('should call onPause when pause clicked', () => {
    const onPause = vi.fn();
    render(
      <DemoControlBar
        state={createDefaultState({ playState: 'playing', selectedScenario: mockScenario })}
        onPlay={vi.fn()}
        onPause={onPause}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
      />
    );
    fireEvent.click(screen.getByLabelText('Pause'));
    expect(onPause).toHaveBeenCalledTimes(1);
  });

  it('should call onStop when stop clicked', () => {
    const onStop = vi.fn();
    render(
      <DemoControlBar
        state={createDefaultState({ playState: 'playing', selectedScenario: mockScenario })}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={onStop}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
      />
    );
    fireEvent.click(screen.getByLabelText('Stop'));
    expect(onStop).toHaveBeenCalledTimes(1);
  });
});

describe('UT-004: Speed slider 0.5x-4x', () => {
  it('should render speed slider', () => {
    render(
      <DemoControlBar
        state={createDefaultState()}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
      />
    );
    expect(screen.getByRole('slider')).toBeInTheDocument();
  });

  it('should display current speed', () => {
    render(
      <DemoControlBar
        state={createDefaultState({ speed: 2 })}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
      />
    );
    expect(screen.getByText('2x')).toBeInTheDocument();
  });

  it('should call onSpeedChange when slider changes', () => {
    const onSpeedChange = vi.fn();
    render(
      <DemoControlBar
        state={createDefaultState()}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={onSpeedChange}
        onScenarioSelect={vi.fn()}
      />
    );
    fireEvent.change(screen.getByRole('slider'), { target: { value: '2' } });
    expect(onSpeedChange).toHaveBeenCalledWith(2);
  });
});

describe('UT-005: MITRE phase progress circles', () => {
  it('should render phase circles for each stage', () => {
    render(
      <DemoControlBar
        state={createDefaultState({ stages: mockStages })}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
      />
    );
    expect(screen.getByTestId('phase-circle-TA0001')).toBeInTheDocument();
    expect(screen.getByTestId('phase-circle-TA0002')).toBeInTheDocument();
    expect(screen.getByTestId('phase-circle-TA0003')).toBeInTheDocument();
  });

  it('should show "No scenario selected" when no stages', () => {
    render(
      <DemoControlBar
        state={createDefaultState()}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
      />
    );
    expect(screen.getByText('No scenario selected')).toBeInTheDocument();
  });
});

describe('UT-006: Collapse/expand toggle', () => {
  it('should render collapse button when onToggleCollapse provided', () => {
    render(
      <DemoControlBar
        state={createDefaultState()}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
        onToggleCollapse={vi.fn()}
      />
    );
    expect(screen.getByLabelText('Collapse control bar')).toBeInTheDocument();
  });

  it('should render collapsed state with expand button', () => {
    render(
      <DemoControlBar
        state={createDefaultState()}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
        isCollapsed={true}
        onToggleCollapse={vi.fn()}
      />
    );
    expect(screen.getByText('Demo Controls')).toBeInTheDocument();
    expect(screen.getByLabelText('Expand control bar')).toBeInTheDocument();
  });

  it('should call onToggleCollapse when clicked', () => {
    const onToggle = vi.fn();
    render(
      <DemoControlBar
        state={createDefaultState()}
        onPlay={vi.fn()}
        onPause={vi.fn()}
        onStop={vi.fn()}
        onSpeedChange={vi.fn()}
        onScenarioSelect={vi.fn()}
        onToggleCollapse={onToggle}
      />
    );
    fireEvent.click(screen.getByLabelText('Collapse control bar'));
    expect(onToggle).toHaveBeenCalledTimes(1);
  });
});
