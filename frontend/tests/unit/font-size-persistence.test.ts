/**
 * Unit Tests: Font Size Persistence
 * Tasks: T-033 (REQ-003-003-001), T-034 (REQ-003-003-002), T-035 (REQ-003-003-003)
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { applyFontSizeFromStorage, getFontSizeStep, FONT_SIZES } from '../../src/utils/font-size';

beforeEach(() => {
  document.documentElement.style.fontSize = '';
  localStorage.clear();
});

// UT-033: REQ-003-003-001 - Font size step saved to localStorage
describe('T-033: Font size step saved to localStorage', () => {
  it('should use "font-size-step" as the localStorage key', () => {
    localStorage.setItem('font-size-step', '1');
    expect(localStorage.getItem('font-size-step')).toBe('1');
  });

  it('should accept "0" as a valid value (16px)', () => {
    localStorage.setItem('font-size-step', '0');
    const step = getFontSizeStep();
    expect(step).toBe(0);
  });

  it('should accept "1" as a valid value (18px)', () => {
    localStorage.setItem('font-size-step', '1');
    const step = getFontSizeStep();
    expect(step).toBe(1);
  });

  it('should accept "2" as a valid value (20px)', () => {
    localStorage.setItem('font-size-step', '2');
    const step = getFontSizeStep();
    expect(step).toBe(2);
  });
});

// UT-034: REQ-003-003-002 - Font size restored from localStorage before first paint
describe('T-034: Font size restored from localStorage', () => {
  it('should apply 18px when step 1 is stored', () => {
    localStorage.setItem('font-size-step', '1');
    applyFontSizeFromStorage();
    expect(document.documentElement.style.fontSize).toBe('18px');
  });

  it('should apply 20px when step 2 is stored', () => {
    localStorage.setItem('font-size-step', '2');
    applyFontSizeFromStorage();
    expect(document.documentElement.style.fontSize).toBe('20px');
  });

  it('should apply 16px when step 0 is stored', () => {
    localStorage.setItem('font-size-step', '0');
    applyFontSizeFromStorage();
    expect(document.documentElement.style.fontSize).toBe('16px');
  });
});

// UT-035: REQ-003-003-003 - Default to step 0 (16px) if localStorage unavailable
describe('T-035: Default to step 0 if localStorage unavailable', () => {
  it('should default to step 0 when localStorage is empty', () => {
    const step = getFontSizeStep();
    expect(step).toBe(0);
  });

  it('should default to step 0 with invalid localStorage value', () => {
    localStorage.setItem('font-size-step', 'invalid');
    const step = getFontSizeStep();
    expect(step).toBe(0);
  });

  it('should apply 16px when no stored value exists', () => {
    applyFontSizeFromStorage();
    expect(document.documentElement.style.fontSize).toBe('16px');
  });

  it('should export FONT_SIZES as [16, 18, 20]', () => {
    expect(FONT_SIZES).toEqual([16, 18, 20]);
  });
});
