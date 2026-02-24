/**
 * UT-018: Dashboard KPI animation tests
 * REQ-001-004-004: KPI numbers on dashboard animate from 0 to their
 * target value with a counting effect.
 * TECH-007: KPI animation component
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { AnimatedKpiValue } from '../../../src/components/mcp/AnimatedKpiValue';

describe('AnimatedKpiValue', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should render the component with a data-testid', () => {
    render(<AnimatedKpiValue value={42} />);
    expect(screen.getByTestId('animated-kpi')).toBeDefined();
  });

  it('should start at 0 when animate is true', () => {
    render(<AnimatedKpiValue value={100} animate={true} />);
    const el = screen.getByTestId('animated-kpi');
    // Initially should show 0 (before animation starts)
    expect(el.textContent).toBe('0');
  });

  it('should reach the target value after animation completes', () => {
    render(<AnimatedKpiValue value={42} animate={true} durationMs={500} />);

    // Advance timers past the animation duration
    act(() => {
      vi.advanceTimersByTime(600);
    });

    const el = screen.getByTestId('animated-kpi');
    expect(el.textContent).toBe('42');
  });

  it('should show intermediate values during animation', () => {
    render(<AnimatedKpiValue value={100} animate={true} durationMs={1000} />);

    // Advance to roughly halfway
    act(() => {
      vi.advanceTimersByTime(500);
    });

    const el = screen.getByTestId('animated-kpi');
    const currentValue = parseInt(el.textContent ?? '0', 10);

    // Should be somewhere between 0 and 100
    expect(currentValue).toBeGreaterThan(0);
    expect(currentValue).toBeLessThanOrEqual(100);
  });

  it('should show value immediately when animate is false', () => {
    render(<AnimatedKpiValue value={42} animate={false} />);
    const el = screen.getByTestId('animated-kpi');
    expect(el.textContent).toBe('42');
  });

  it('should show value immediately when animate is not provided', () => {
    render(<AnimatedKpiValue value={77} />);
    // By default, if not animating, should show the final value
    // Wait for any potential initial render
    act(() => {
      vi.advanceTimersByTime(0);
    });
    const el = screen.getByTestId('animated-kpi');
    expect(el.textContent).toBe('77');
  });

  it('should handle decimal values by rounding during animation', () => {
    render(<AnimatedKpiValue value={3.5} animate={true} durationMs={500} decimals={1} />);

    act(() => {
      vi.advanceTimersByTime(600);
    });

    const el = screen.getByTestId('animated-kpi');
    expect(el.textContent).toBe('3.5');
  });

  it('should accept a prefix (e.g. currency symbol)', () => {
    render(<AnimatedKpiValue value={42} prefix="$" animate={false} />);
    const el = screen.getByTestId('animated-kpi');
    expect(el.textContent).toContain('$');
    expect(el.textContent).toContain('42');
  });

  it('should accept a suffix (e.g. unit)', () => {
    render(<AnimatedKpiValue value={42} suffix="h" animate={false} />);
    const el = screen.getByTestId('animated-kpi');
    expect(el.textContent).toContain('42');
    expect(el.textContent).toContain('h');
  });

  it('should update when target value changes', () => {
    const { rerender } = render(
      <AnimatedKpiValue value={42} animate={true} durationMs={500} />
    );

    act(() => {
      vi.advanceTimersByTime(600);
    });

    expect(screen.getByTestId('animated-kpi').textContent).toBe('42');

    // Change target value
    rerender(<AnimatedKpiValue value={100} animate={true} durationMs={500} />);

    act(() => {
      vi.advanceTimersByTime(600);
    });

    expect(screen.getByTestId('animated-kpi').textContent).toBe('100');
  });

  it('should handle zero as target value', () => {
    render(<AnimatedKpiValue value={0} animate={false} />);
    const el = screen.getByTestId('animated-kpi');
    expect(el.textContent).toBe('0');
  });

  it('should cleanup animation on unmount', () => {
    const { unmount } = render(
      <AnimatedKpiValue value={100} animate={true} durationMs={5000} />
    );

    // Unmount before animation completes
    unmount();

    // Should not throw or cause errors
    act(() => {
      vi.advanceTimersByTime(6000);
    });
  });
});
