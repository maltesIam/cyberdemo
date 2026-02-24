/**
 * Unit Tests for Keyboard Shortcuts Hook
 * UT-TECH-006: Keyboard shortcut handler for Space=Play/Pause, Esc=Stop
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useKeyboardShortcuts } from '../../../src/hooks/useKeyboardShortcuts';

describe('UT-TECH-006: Keyboard shortcut handler', () => {
  const handlers = {
    onPlayPause: vi.fn(),
    onStop: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should register keyboard event listener on mount', () => {
    const addSpy = vi.spyOn(document, 'addEventListener');
    renderHook(() => useKeyboardShortcuts(handlers));

    expect(addSpy).toHaveBeenCalledWith('keydown', expect.any(Function));
  });

  it('should remove keyboard event listener on unmount', () => {
    const removeSpy = vi.spyOn(document, 'removeEventListener');
    const { unmount } = renderHook(() => useKeyboardShortcuts(handlers));

    unmount();
    expect(removeSpy).toHaveBeenCalledWith('keydown', expect.any(Function));
  });

  it('should call onPlayPause when Space is pressed', () => {
    renderHook(() => useKeyboardShortcuts(handlers));

    document.dispatchEvent(new KeyboardEvent('keydown', { code: 'Space' }));

    expect(handlers.onPlayPause).toHaveBeenCalledTimes(1);
  });

  it('should call onStop when Escape is pressed', () => {
    renderHook(() => useKeyboardShortcuts(handlers));

    document.dispatchEvent(new KeyboardEvent('keydown', { code: 'Escape' }));

    expect(handlers.onStop).toHaveBeenCalledTimes(1);
  });

  it('should not trigger when typing in input fields', () => {
    renderHook(() => useKeyboardShortcuts(handlers));

    const event = new KeyboardEvent('keydown', { code: 'Space' });
    Object.defineProperty(event, 'target', {
      value: document.createElement('input'),
    });
    document.dispatchEvent(event);

    expect(handlers.onPlayPause).not.toHaveBeenCalled();
  });

  it('should not trigger when typing in textarea', () => {
    renderHook(() => useKeyboardShortcuts(handlers));

    const event = new KeyboardEvent('keydown', { code: 'Space' });
    Object.defineProperty(event, 'target', {
      value: document.createElement('textarea'),
    });
    document.dispatchEvent(event);

    expect(handlers.onPlayPause).not.toHaveBeenCalled();
  });

  it('should not trigger when disabled', () => {
    renderHook(() => useKeyboardShortcuts({ ...handlers, enabled: false }));

    document.dispatchEvent(new KeyboardEvent('keydown', { code: 'Space' }));
    document.dispatchEvent(new KeyboardEvent('keydown', { code: 'Escape' }));

    expect(handlers.onPlayPause).not.toHaveBeenCalled();
    expect(handlers.onStop).not.toHaveBeenCalled();
  });

  it('should ignore unregistered keys', () => {
    renderHook(() => useKeyboardShortcuts(handlers));

    document.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyA' }));
    document.dispatchEvent(new KeyboardEvent('keydown', { code: 'Enter' }));

    expect(handlers.onPlayPause).not.toHaveBeenCalled();
    expect(handlers.onStop).not.toHaveBeenCalled();
  });
});
