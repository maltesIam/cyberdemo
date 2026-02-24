/**
 * UT-002: WS state triggers UI navigation tests
 * REQ-001-001-002: When state update includes `currentPage`, navigate to that page
 * with a toast notification "Vega navigated to [page]"
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useWsNavigation } from '../../../src/hooks/useWsNavigation';
import { renderHook } from '@testing-library/react';

// Mock react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
}));

// Mock toast
const mockShowToast = vi.fn();
vi.mock('../../../src/utils/toast', () => ({
  useToast: () => ({
    showToast: mockShowToast,
    toasts: [],
    removeToast: vi.fn(),
  }),
}));

describe('useWsNavigation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should navigate when currentPage changes', () => {
    const { rerender } = renderHook(
      ({ currentPage }) => useWsNavigation(currentPage),
      { initialProps: { currentPage: undefined as string | undefined } }
    );

    rerender({ currentPage: '/dashboard' });

    expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
  });

  it('should show toast notification with page name', () => {
    const { rerender } = renderHook(
      ({ currentPage }) => useWsNavigation(currentPage),
      { initialProps: { currentPage: undefined as string | undefined } }
    );

    rerender({ currentPage: '/incidents' });

    expect(mockShowToast).toHaveBeenCalledWith(
      'info',
      expect.stringContaining('Vega navigated to'),
      expect.any(Number)
    );
    expect(mockShowToast).toHaveBeenCalledWith(
      'info',
      expect.stringContaining('incidents'),
      expect.any(Number)
    );
  });

  it('should not navigate when currentPage is undefined', () => {
    renderHook(() => useWsNavigation(undefined));
    expect(mockNavigate).not.toHaveBeenCalled();
    expect(mockShowToast).not.toHaveBeenCalled();
  });

  it('should not navigate when currentPage does not change', () => {
    const { rerender } = renderHook(
      ({ currentPage }) => useWsNavigation(currentPage),
      { initialProps: { currentPage: '/dashboard' as string | undefined } }
    );

    // Navigate should fire on first defined value
    expect(mockNavigate).toHaveBeenCalledTimes(1);
    mockNavigate.mockClear();
    mockShowToast.mockClear();

    // Same page re-rendered - should NOT navigate again
    rerender({ currentPage: '/dashboard' });
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('should navigate when page changes from one to another', () => {
    const { rerender } = renderHook(
      ({ currentPage }) => useWsNavigation(currentPage),
      { initialProps: { currentPage: '/dashboard' as string | undefined } }
    );

    mockNavigate.mockClear();
    mockShowToast.mockClear();

    rerender({ currentPage: '/graph' });

    expect(mockNavigate).toHaveBeenCalledWith('/graph');
    expect(mockShowToast).toHaveBeenCalledWith(
      'info',
      expect.stringContaining('graph'),
      expect.any(Number)
    );
  });

  it('should format page name nicely in toast (strip leading slash)', () => {
    const { rerender } = renderHook(
      ({ currentPage }) => useWsNavigation(currentPage),
      { initialProps: { currentPage: undefined as string | undefined } }
    );

    rerender({ currentPage: '/dashboard' });

    const toastMessage = mockShowToast.mock.calls[0][1];
    expect(toastMessage).toBe('Vega navigated to dashboard');
  });
});
