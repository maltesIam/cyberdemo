/**
 * Integration Tests for AnalyzeButton
 * IT-005: AnalyzeButton queues analysis, shows progress, persists result
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AnalyzeButton } from '../../src/components/demo/AnalyzeButton';

describe('IT-005: AnalyzeButton analysis flow', () => {
  it('should flow through idle → processing → completed', () => {
    const onAnalyze = vi.fn();
    const onExpandNarration = vi.fn();

    const { rerender } = render(
      <AnalyzeButton
        incidentId="inc-1"
        status="idle"
        onAnalyze={onAnalyze}
        onExpandNarration={onExpandNarration}
      />
    );

    // Click to analyze
    fireEvent.click(screen.getByTestId('analyze-button'));
    expect(onAnalyze).toHaveBeenCalledWith('inc-1');
    expect(onExpandNarration).toHaveBeenCalled();

    // Processing state
    rerender(
      <AnalyzeButton
        incidentId="inc-1"
        status="processing"
        onAnalyze={onAnalyze}
        onExpandNarration={onExpandNarration}
      />
    );
    expect(screen.getByText('Analyzing...')).toBeInTheDocument();

    // Completed state
    rerender(
      <AnalyzeButton
        incidentId="inc-1"
        status="completed"
        decision="contain"
        onAnalyze={onAnalyze}
        onExpandNarration={onExpandNarration}
      />
    );
    expect(screen.getByText('Contained')).toBeInTheDocument();
  });

  it('should support parallel analysis of multiple incidents', () => {
    render(
      <table>
        <tbody>
          <tr>
            <td><AnalyzeButton incidentId="inc-1" status="processing" onAnalyze={vi.fn()} /></td>
          </tr>
          <tr>
            <td><AnalyzeButton incidentId="inc-2" status="idle" onAnalyze={vi.fn()} /></td>
          </tr>
          <tr>
            <td><AnalyzeButton incidentId="inc-3" status="completed" decision="dismiss" onAnalyze={vi.fn()} /></td>
          </tr>
        </tbody>
      </table>
    );
    const buttons = screen.getAllByTestId('analyze-button');
    expect(buttons).toHaveLength(3);
    expect(screen.getByText('Analyzing...')).toBeInTheDocument();
    expect(screen.getByText('Analyze with AI')).toBeInTheDocument();
    expect(screen.getByText('Dismissed')).toBeInTheDocument();
  });
});
