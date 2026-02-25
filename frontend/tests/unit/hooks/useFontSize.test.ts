/**
 * UT-013: useFontSize Hook
 * Requirement: REQ-003-001-001
 * Task: T-003-001
 *
 * AC-001: Hook provides `fontSizeStep` state (0, 1, 2)
 * AC-002: Hook provides `cycleFontSize()` function
 * AC-003: Step 0 = 16px, Step 1 = 18px, Step 2 = 20px
 * AC-004: On mount, reads from localStorage key `font-size-step`
 * AC-005: On change, writes to localStorage and updates `html { font-size }`
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useFontSize } from '../../../src/hooks/useFontSize';

beforeEach(() => {
  document.documentElement.style.fontSize = '';
  localStorage.clear();
});

describe('UT-013: useFontSize Hook (REQ-003-001-001)', () => {
  // AC-001: Hook provides fontSizeStep state (0, 1, 2)
  describe('AC-001: fontSizeStep state', () => {
    it('should return fontSizeStep as 0 by default', () => {
      const { result } = renderHook(() => useFontSize());
      expect(result.current.fontSizeStep).toBe(0);
    });

    it('should return fontSizeStep as 1 when stored', () => {
      localStorage.setItem('font-size-step', '1');
      const { result } = renderHook(() => useFontSize());
      expect(result.current.fontSizeStep).toBe(1);
    });

    it('should return fontSizeStep as 2 when stored', () => {
      localStorage.setItem('font-size-step', '2');
      const { result } = renderHook(() => useFontSize());
      expect(result.current.fontSizeStep).toBe(2);
    });
  });

  // AC-002: Hook provides cycleFontSize() function
  describe('AC-002: cycleFontSize function', () => {
    it('should expose a cycleFontSize function', () => {
      const { result } = renderHook(() => useFontSize());
      expect(typeof result.current.cycleFontSize).toBe('function');
    });

    it('should cycle from step 0 to step 1', () => {
      const { result } = renderHook(() => useFontSize());
      act(() => {
        result.current.cycleFontSize();
      });
      expect(result.current.fontSizeStep).toBe(1);
    });

    it('should cycle from step 1 to step 2', () => {
      localStorage.setItem('font-size-step', '1');
      const { result } = renderHook(() => useFontSize());
      act(() => {
        result.current.cycleFontSize();
      });
      expect(result.current.fontSizeStep).toBe(2);
    });

    it('should cycle from step 2 back to step 0', () => {
      localStorage.setItem('font-size-step', '2');
      const { result } = renderHook(() => useFontSize());
      act(() => {
        result.current.cycleFontSize();
      });
      expect(result.current.fontSizeStep).toBe(0);
    });
  });

  // AC-003: Step 0 = 16px, Step 1 = 18px, Step 2 = 20px
  describe('AC-003: Font size pixel values', () => {
    it('should expose fontSizePx as 16 at step 0', () => {
      const { result } = renderHook(() => useFontSize());
      expect(result.current.fontSizePx).toBe(16);
    });

    it('should expose fontSizePx as 18 at step 1', () => {
      localStorage.setItem('font-size-step', '1');
      const { result } = renderHook(() => useFontSize());
      expect(result.current.fontSizePx).toBe(18);
    });

    it('should expose fontSizePx as 20 at step 2', () => {
      localStorage.setItem('font-size-step', '2');
      const { result } = renderHook(() => useFontSize());
      expect(result.current.fontSizePx).toBe(20);
    });
  });

  // AC-004: On mount, reads from localStorage key `font-size-step`
  describe('AC-004: Reads from localStorage on mount', () => {
    it('should read existing step from localStorage', () => {
      localStorage.setItem('font-size-step', '2');
      const { result } = renderHook(() => useFontSize());
      expect(result.current.fontSizeStep).toBe(2);
    });

    it('should default to 0 when localStorage is empty', () => {
      const { result } = renderHook(() => useFontSize());
      expect(result.current.fontSizeStep).toBe(0);
    });

    it('should default to 0 when localStorage has invalid value', () => {
      localStorage.setItem('font-size-step', 'invalid');
      const { result } = renderHook(() => useFontSize());
      expect(result.current.fontSizeStep).toBe(0);
    });
  });

  // AC-005: On change, writes to localStorage and updates html { font-size }
  describe('AC-005: Writes to localStorage and updates html font-size', () => {
    it('should write new step to localStorage after cycling', () => {
      const { result } = renderHook(() => useFontSize());
      act(() => {
        result.current.cycleFontSize();
      });
      expect(localStorage.getItem('font-size-step')).toBe('1');
    });

    it('should update document.documentElement.style.fontSize after cycling', () => {
      const { result } = renderHook(() => useFontSize());
      act(() => {
        result.current.cycleFontSize();
      });
      expect(document.documentElement.style.fontSize).toBe('18px');
    });

    it('should update both localStorage and fontSize on full cycle', () => {
      const { result } = renderHook(() => useFontSize());
      // step 0 -> 1 (18px)
      act(() => { result.current.cycleFontSize(); });
      expect(localStorage.getItem('font-size-step')).toBe('1');
      expect(document.documentElement.style.fontSize).toBe('18px');

      // step 1 -> 2 (20px)
      act(() => { result.current.cycleFontSize(); });
      expect(localStorage.getItem('font-size-step')).toBe('2');
      expect(document.documentElement.style.fontSize).toBe('20px');

      // step 2 -> 0 (16px)
      act(() => { result.current.cycleFontSize(); });
      expect(localStorage.getItem('font-size-step')).toBe('0');
      expect(document.documentElement.style.fontSize).toBe('16px');
    });
  });

  // Additional: sizeLabel property
  describe('Additional: sizeLabel property', () => {
    it('should expose sizeLabel as "Normal" at step 0', () => {
      const { result } = renderHook(() => useFontSize());
      expect(result.current.sizeLabel).toBe('Normal');
    });

    it('should expose sizeLabel as "Medium" at step 1', () => {
      localStorage.setItem('font-size-step', '1');
      const { result } = renderHook(() => useFontSize());
      expect(result.current.sizeLabel).toBe('Medium');
    });

    it('should expose sizeLabel as "Large" at step 2', () => {
      localStorage.setItem('font-size-step', '2');
      const { result } = renderHook(() => useFontSize());
      expect(result.current.sizeLabel).toBe('Large');
    });
  });
});
