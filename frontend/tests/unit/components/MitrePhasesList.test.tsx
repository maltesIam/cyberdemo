/**
 * Tests for MitrePhasesList Component
 * UT-033: Renders vertical phases with status indicators
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MitrePhasesList } from '../../../src/components/demo/MitrePhasesList';
import type { MitreStage } from '../../../src/components/demo/types';

const mockStages: MitreStage[] = [
  { index: 0, tacticId: 'TA0001', tacticName: 'Initial Access', techniqueIds: ['T1566'], completed: true, active: false },
  { index: 1, tacticId: 'TA0002', tacticName: 'Execution', techniqueIds: ['T1059'], completed: false, active: true },
  { index: 2, tacticId: 'TA0003', tacticName: 'Persistence', techniqueIds: ['T1547'], completed: false, active: false },
];

describe('UT-033: MitrePhasesList vertical phases', () => {
  it('should render the phases list', () => {
    render(<MitrePhasesList stages={mockStages} currentStage={1} />);
    expect(screen.getByTestId('mitre-phases-list')).toBeInTheDocument();
  });

  it('should have MITRE ATT&CK Phases title', () => {
    render(<MitrePhasesList stages={mockStages} currentStage={1} />);
    expect(screen.getByText('MITRE ATT&CK Phases')).toBeInTheDocument();
  });

  it('should render all phase items', () => {
    render(<MitrePhasesList stages={mockStages} currentStage={1} />);
    expect(screen.getByTestId('phase-item-0')).toBeInTheDocument();
    expect(screen.getByTestId('phase-item-1')).toBeInTheDocument();
    expect(screen.getByTestId('phase-item-2')).toBeInTheDocument();
  });

  it('should display tactic names', () => {
    render(<MitrePhasesList stages={mockStages} currentStage={1} />);
    expect(screen.getByText('Initial Access')).toBeInTheDocument();
    expect(screen.getByText('Execution')).toBeInTheDocument();
    expect(screen.getByText('Persistence')).toBeInTheDocument();
  });

  it('should display tactic IDs', () => {
    render(<MitrePhasesList stages={mockStages} currentStage={1} />);
    expect(screen.getByText('TA0001')).toBeInTheDocument();
    expect(screen.getByText('TA0002')).toBeInTheDocument();
    expect(screen.getByText('TA0003')).toBeInTheDocument();
  });

  it('should show status indicators', () => {
    render(<MitrePhasesList stages={mockStages} currentStage={1} />);
    expect(screen.getByTestId('phase-status-completed')).toBeInTheDocument();
    expect(screen.getByTestId('phase-status-active')).toBeInTheDocument();
    expect(screen.getByTestId('phase-status-pending')).toBeInTheDocument();
  });

  it('should show message when no stages', () => {
    render(<MitrePhasesList stages={[]} currentStage={0} />);
    expect(screen.getByText('Select a scenario to view phases')).toBeInTheDocument();
  });

  it('should display technique count', () => {
    render(<MitrePhasesList stages={mockStages} currentStage={1} />);
    const techCounts = screen.getAllByText('1 tech');
    expect(techCounts.length).toBe(3);
  });
});
