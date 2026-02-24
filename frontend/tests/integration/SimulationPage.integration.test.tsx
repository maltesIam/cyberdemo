/**
 * Integration Tests for SimulationPage
 * IT-006: SimulationPage loads, displays 3-column layout
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { DemoProvider } from '../../src/context/DemoContext';
import { SimulationPage } from '../../src/pages/SimulationPage';
import type { MitreStage } from '../../src/components/demo/types';

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <MemoryRouter>
      <DemoProvider>{ui}</DemoProvider>
    </MemoryRouter>
  );
}

// Mock cytoscape
vi.mock('cytoscape', () => ({
  default: vi.fn(() => ({
    on: vi.fn(),
    destroy: vi.fn(),
    getElementById: vi.fn(() => ({ length: 0 })),
    add: vi.fn(),
    layout: vi.fn(() => ({ run: vi.fn() })),
  })),
}));

const mockStages: MitreStage[] = [
  { index: 0, tacticId: 'TA0001', tacticName: 'Initial Access', techniqueIds: ['T1566'], completed: true, active: false },
  { index: 1, tacticId: 'TA0002', tacticName: 'Execution', techniqueIds: ['T1059'], completed: false, active: true },
];

describe('IT-006: SimulationPage integration', () => {
  it('should render full simulation page with all columns', () => {
    renderWithProviders(
      <SimulationPage />
    );

    // All 3 columns present
    expect(screen.getByTestId('mitre-column')).toBeInTheDocument();
    expect(screen.getByTestId('graph-column')).toBeInTheDocument();
    expect(screen.getByTestId('aip-column')).toBeInTheDocument();

    // Narration footer always visible (no outlet context = empty messages = waiting state)
    expect(screen.getByTestId('narration-footer')).toBeInTheDocument();
    expect(screen.getByText('Waiting for narration events...')).toBeInTheDocument();

    // MITRE phases from DemoContext (default state)
    expect(screen.getByTestId('mitre-column')).toBeInTheDocument();
  });

  it('should render scenario selector and controls', () => {
    renderWithProviders(<SimulationPage />);
    expect(screen.getByRole('combobox')).toBeInTheDocument();
    expect(screen.getByLabelText(/Play|Pause/)).toBeInTheDocument();
    expect(screen.getByLabelText('Stop')).toBeInTheDocument();
  });
});
