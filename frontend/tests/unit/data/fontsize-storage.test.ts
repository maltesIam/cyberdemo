/**
 * UT-060: LocalStorage Font Size Persistence
 * Requirement: DATA-002
 * Task: T-DATA-002
 *
 * AC-001: Key `font-size-step` stores current step
 * AC-002: Valid values: 0, 1, 2
 * AC-003: Default if no stored value: 0
 */
import { describe, it, expect, beforeEach } from 'vitest';
import {
  getFontSizeStep,
  saveFontSizeStep,
  applyFontSizeFromStorage,
  cycleFontSize,
  FONT_SIZES,
} from '../../../src/utils/font-size';

beforeEach(() => {
  document.documentElement.style.fontSize = '';
  localStorage.clear();
});

describe('UT-060: LocalStorage Font Size Persistence (DATA-002)', () => {
  // AC-001: Key `font-size-step` stores current step
  describe('AC-001: Uses font-size-step localStorage key', () => {
    it('should use "font-size-step" as the localStorage key', () => {
      saveFontSizeStep(1);
      expect(localStorage.getItem('font-size-step')).toBe('1');
    });

    it('should read from "font-size-step" key', () => {
      localStorage.setItem('font-size-step', '2');
      expect(getFontSizeStep()).toBe(2);
    });

    it('should save step via cycleFontSize', () => {
      cycleFontSize(0); // cycles to 1
      expect(localStorage.getItem('font-size-step')).toBe('1');
    });
  });

  // AC-002: Valid values: 0, 1, 2
  describe('AC-002: Valid values are 0, 1, 2', () => {
    it('should accept step 0 (16px)', () => {
      saveFontSizeStep(0);
      expect(getFontSizeStep()).toBe(0);
    });

    it('should accept step 1 (18px)', () => {
      saveFontSizeStep(1);
      expect(getFontSizeStep()).toBe(1);
    });

    it('should accept step 2 (20px)', () => {
      saveFontSizeStep(2);
      expect(getFontSizeStep()).toBe(2);
    });

    it('should not save invalid step values (negative)', () => {
      saveFontSizeStep(-1);
      expect(localStorage.getItem('font-size-step')).toBeNull();
    });

    it('should not save invalid step values (> 2)', () => {
      saveFontSizeStep(3);
      expect(localStorage.getItem('font-size-step')).toBeNull();
    });

    it('FONT_SIZES should map to [16, 18, 20]', () => {
      expect(FONT_SIZES[0]).toBe(16);
      expect(FONT_SIZES[1]).toBe(18);
      expect(FONT_SIZES[2]).toBe(20);
    });
  });

  // AC-003: Default if no stored value: 0
  describe('AC-003: Default to step 0', () => {
    it('should default to step 0 when localStorage is empty', () => {
      expect(getFontSizeStep()).toBe(0);
    });

    it('should default to step 0 when localStorage has invalid string', () => {
      localStorage.setItem('font-size-step', 'abc');
      expect(getFontSizeStep()).toBe(0);
    });

    it('should default to step 0 when localStorage has out-of-range number', () => {
      localStorage.setItem('font-size-step', '5');
      expect(getFontSizeStep()).toBe(0);
    });

    it('should apply 16px (default) when no stored value', () => {
      applyFontSizeFromStorage();
      expect(document.documentElement.style.fontSize).toBe('16px');
    });
  });

  // Functional: Full cycle persistence
  describe('Functional: Persistence across cycles', () => {
    it('should persist each step correctly through full cycle', () => {
      // Step 0 -> 1
      let nextStep = cycleFontSize(0);
      expect(nextStep).toBe(1);
      expect(localStorage.getItem('font-size-step')).toBe('1');
      expect(document.documentElement.style.fontSize).toBe('18px');

      // Step 1 -> 2
      nextStep = cycleFontSize(1);
      expect(nextStep).toBe(2);
      expect(localStorage.getItem('font-size-step')).toBe('2');
      expect(document.documentElement.style.fontSize).toBe('20px');

      // Step 2 -> 0
      nextStep = cycleFontSize(2);
      expect(nextStep).toBe(0);
      expect(localStorage.getItem('font-size-step')).toBe('0');
      expect(document.documentElement.style.fontSize).toBe('16px');
    });

    it('should restore saved value after applyFontSizeFromStorage', () => {
      localStorage.setItem('font-size-step', '2');
      applyFontSizeFromStorage();
      expect(document.documentElement.style.fontSize).toBe('20px');
    });
  });
});
