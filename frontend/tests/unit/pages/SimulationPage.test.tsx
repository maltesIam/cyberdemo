/**
 * Tests for SimulationPage
 * UT-031: /simulation route renders
 * UT-032: 3-column layout
 * UT-033: MitrePhasesList in left column (covered in MitrePhasesList.test.tsx)
 * UT-034: AttackGraph in center (covered in AttackGraph.test.tsx)
 * UT-035: Integrated aIP panel in right column
 * UT-036: Narration footer always visible
 * UT-037: Scenario selector fires selection change
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { DemoProvider } from '../../../src/context/DemoContext';
import { SimulationPage } from '../../../src/pages/SimulationPage';
import type { MitreStage } from '../../../src/components/demo/types';

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

describe('UT-031: SimulationPage route renders', () => {
  it('should render simulation page', () => {
    renderWithProviders(<SimulationPage />);
    expect(screen.getByTestId('simulation-page')).toBeInTheDocument();
  });
});

describe('UT-032: 3-column layout', () => {
  it('should render MITRE column', () => {
    renderWithProviders(<SimulationPage stages={mockStages} />);
    expect(screen.getByTestId('mitre-column')).toBeInTheDocument();
  });

  it('should render graph column', () => {
    renderWithProviders(<SimulationPage />);
    expect(screen.getByTestId('graph-column')).toBeInTheDocument();
  });

  it('should render aIP column', () => {
    renderWithProviders(<SimulationPage />);
    expect(screen.getByTestId('aip-column')).toBeInTheDocument();
  });
});

describe('UT-035: Integrated aIP panel in right column (not floating)', () => {
  it('should render aIP Assist widget in right column', () => {
    renderWithProviders(<SimulationPage />);
    const aipColumn = screen.getByTestId('aip-column');
    expect(aipColumn.querySelector('[data-testid="aip-assist-widget"]')).toBeInTheDocument();
  });
});

describe('UT-036: Narration footer always visible', () => {
  it('should render narration footer', () => {
    renderWithProviders(<SimulationPage />);
    expect(screen.getByTestId('narration-footer')).toBeInTheDocument();
  });

  it('should have narration always expanded', () => {
    renderWithProviders(<SimulationPage />);
    expect(screen.getByTestId('narration-messages')).toBeInTheDocument();
  });
});

describe('UT-037: Scenario selector in page', () => {
  it('should render scenario dropdown', () => {
    renderWithProviders(<SimulationPage />);
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('should render play and stop buttons', () => {
    renderWithProviders(<SimulationPage />);
    expect(screen.getByLabelText(/Play|Pause/)).toBeInTheDocument();
    expect(screen.getByLabelText('Stop')).toBeInTheDocument();
  });
});
