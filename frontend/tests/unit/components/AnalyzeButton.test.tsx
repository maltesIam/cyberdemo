/**
 * Tests for AnalyzeButton Component
 * UT-025: Renders in table row
 * UT-026: 3 button states
 * UT-027: Click dispatches narration expand
 * UT-028: Async analysis call
 * UT-029: Result persists to incident
 * UT-030: Multiple parallel analyses
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AnalyzeButton } from '../../../src/components/demo/AnalyzeButton';

describe('UT-025: AnalyzeButton renders in table row', () => {
  it('should render the button', () => {
    render(
      <AnalyzeButton
        incidentId="inc-1"
        status="idle"
        onAnalyze={vi.fn()}
      />
    );
    expect(screen.getByTestId('analyze-button')).toBeInTheDocument();
  });

  it('should show "Analyze with AI" text in initial state', () => {
    render(
      <AnalyzeButton
        incidentId="inc-1"
        status="idle"
        onAnalyze={vi.fn()}
      />
    );
    expect(screen.getByText('Analyze with AI')).toBeInTheDocument();
  });
});

describe('UT-026: 3 button states', () => {
  it('should show initial state with robot icon', () => {
    render(
      <AnalyzeButton
        incidentId="inc-1"
        status="idle"
        onAnalyze={vi.fn()}
      />
    );
    expect(screen.getByLabelText('Analyze with AI')).toBeInTheDocument();
    expect(screen.getByLabelText('Analyze with AI')).not.toBeDisabled();
  });

  it('should show processing state with "Analyzing..."', () => {
    render(
      <AnalyzeButton
        incidentId="inc-1"
        status="processing"
        onAnalyze={vi.fn()}
      />
    );
    expect(screen.getByText('Analyzing...')).toBeInTheDocument();
    expect(screen.getByLabelText('Analysis in progress')).toBeDisabled();
  });

  it('should show completed state with contain decision icon', () => {
    render(
      <AnalyzeButton
        incidentId="inc-1"
        status="completed"
        decision="contain"
        onAnalyze={vi.fn()}
      />
    );
    expect(screen.getByText('Contained')).toBeInTheDocument();
  });

  it('should show completed state with escalate decision', () => {
    render(
      <AnalyzeButton
        incidentId="inc-1"
        status="completed"
        decision="escalate"
        onAnalyze={vi.fn()}
      />
    );
    expect(screen.getByText('Escalated')).toBeInTheDocument();
  });

  it('should show completed state with dismiss decision', () => {
    render(
      <AnalyzeButton
        incidentId="inc-1"
        status="completed"
        decision="dismiss"
        onAnalyze={vi.fn()}
      />
    );
    expect(screen.getByText('Dismissed')).toBeInTheDocument();
  });

  it('should show completed state with monitor decision', () => {
    render(
      <AnalyzeButton
        incidentId="inc-1"
        status="completed"
        decision="monitor"
        onAnalyze={vi.fn()}
      />
    );
    expect(screen.getByText('Monitoring')).toBeInTheDocument();
  });
});

describe('UT-027: Click dispatches narration expand', () => {
  it('should call onExpandNarration when clicked', () => {
    const onExpand = vi.fn();
    render(
      <AnalyzeButton
        incidentId="inc-1"
        status="idle"
        onAnalyze={vi.fn()}
        onExpandNarration={onExpand}
      />
    );
    fireEvent.click(screen.getByTestId('analyze-button'));
    expect(onExpand).toHaveBeenCalledTimes(1);
  });
});

describe('UT-028: Async analysis call', () => {
  it('should call onAnalyze with incidentId when clicked', () => {
    const onAnalyze = vi.fn();
    render(
      <AnalyzeButton
        incidentId="inc-42"
        status="idle"
        onAnalyze={onAnalyze}
      />
    );
    fireEvent.click(screen.getByTestId('analyze-button'));
    expect(onAnalyze).toHaveBeenCalledWith('inc-42');
  });

  it('should not call onAnalyze when already processing', () => {
    const onAnalyze = vi.fn();
    render(
      <AnalyzeButton
        incidentId="inc-1"
        status="processing"
        onAnalyze={onAnalyze}
      />
    );
    fireEvent.click(screen.getByTestId('analyze-button'));
    expect(onAnalyze).not.toHaveBeenCalled();
  });
});

describe('UT-029: Result persists to incident state', () => {
  it('should display decision after completion', () => {
    render(
      <AnalyzeButton
        incidentId="inc-1"
        status="completed"
        decision="contain"
        onAnalyze={vi.fn()}
      />
    );
    expect(screen.getByLabelText('Analysis complete: Contained')).toBeInTheDocument();
  });
});

describe('UT-030: Multiple parallel analyses', () => {
  it('should render multiple independent buttons', () => {
    const { container } = render(
      <div>
        <AnalyzeButton incidentId="inc-1" status="idle" onAnalyze={vi.fn()} />
        <AnalyzeButton incidentId="inc-2" status="processing" onAnalyze={vi.fn()} />
        <AnalyzeButton incidentId="inc-3" status="completed" decision="contain" onAnalyze={vi.fn()} />
      </div>
    );
    const buttons = container.querySelectorAll('[data-testid="analyze-button"]');
    expect(buttons).toHaveLength(3);
  });
});
