/**
 * UT-062: WCAG 2.2 AA Color Contrast Compliance
 * Requirement: NFR-002
 * Task: T-NFR-002
 *
 * AC-001: Normal text: 4.5:1 minimum contrast ratio
 * AC-002: Large text: 3:1 minimum
 * AC-003: UI components: 3:1 minimum
 *
 * Tests verify contrast ratios for all text/background combinations
 * in both Dark and Light themes using the actual design token hex values.
 */
import { describe, it, expect } from 'vitest';

// Helper: Calculate relative luminance per WCAG 2.0
function hexToLuminance(hex: string): number {
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;

  const sRGB = [r, g, b].map(c =>
    c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
  );

  return 0.2126 * sRGB[0] + 0.7152 * sRGB[1] + 0.0722 * sRGB[2];
}

function contrastRatio(hex1: string, hex2: string): number {
  const l1 = hexToLuminance(hex1);
  const l2 = hexToLuminance(hex2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

// Design token color values from design-tokens.css
const DARK_THEME = {
  bgPrimary: '#0a0a0f',
  bgSecondary: '#12121a',
  bgTertiary: '#1a1a2e',
  bgCard: '#1a1a2e',
  bgElevated: '#1e1e32',
  textPrimary: '#f1f5f9',
  textSecondary: '#94a3b8',
  textTertiary: '#64748b',
  primary: '#6366f1',
  primary600: '#4f46e5',
  borderFocus: '#6366f1',
};

const LIGHT_THEME = {
  bgPrimary: '#ffffff',
  bgSecondary: '#f8fafc',
  bgTertiary: '#f1f5f9',
  bgCard: '#ffffff',
  bgElevated: '#ffffff',
  textPrimary: '#0f172a',
  textSecondary: '#475569',
  textTertiary: '#64748b',
  primary: '#4f46e5',
  primary600: '#4f46e5',
  borderFocus: '#4f46e5',
};

describe('UT-062: WCAG 2.2 AA Color Contrast (NFR-002)', () => {
  // AC-001: Normal text >= 4.5:1
  describe('AC-001: Normal text contrast ratios (>= 4.5:1)', () => {
    describe('Dark theme', () => {
      it('text-primary (#f1f5f9) on bg-primary (#0a0a0f) >= 4.5:1', () => {
        const ratio = contrastRatio(DARK_THEME.textPrimary, DARK_THEME.bgPrimary);
        expect(ratio).toBeGreaterThanOrEqual(4.5);
      });

      it('text-secondary (#94a3b8) on bg-primary (#0a0a0f) >= 4.5:1', () => {
        const ratio = contrastRatio(DARK_THEME.textSecondary, DARK_THEME.bgPrimary);
        expect(ratio).toBeGreaterThanOrEqual(4.5);
      });

      it('text-primary (#f1f5f9) on bg-secondary (#12121a) >= 4.5:1', () => {
        const ratio = contrastRatio(DARK_THEME.textPrimary, DARK_THEME.bgSecondary);
        expect(ratio).toBeGreaterThanOrEqual(4.5);
      });

      it('text-secondary (#94a3b8) on bg-secondary (#12121a) >= 4.5:1', () => {
        const ratio = contrastRatio(DARK_THEME.textSecondary, DARK_THEME.bgSecondary);
        expect(ratio).toBeGreaterThanOrEqual(4.5);
      });

      it('text-primary (#f1f5f9) on bg-tertiary (#1a1a2e) >= 4.5:1', () => {
        const ratio = contrastRatio(DARK_THEME.textPrimary, DARK_THEME.bgTertiary);
        expect(ratio).toBeGreaterThanOrEqual(4.5);
      });

      it('text-primary (#f1f5f9) on bg-card (#1a1a2e) >= 4.5:1', () => {
        const ratio = contrastRatio(DARK_THEME.textPrimary, DARK_THEME.bgCard);
        expect(ratio).toBeGreaterThanOrEqual(4.5);
      });

      it('text-primary (#f1f5f9) on bg-elevated (#1e1e32) >= 4.5:1', () => {
        const ratio = contrastRatio(DARK_THEME.textPrimary, DARK_THEME.bgElevated);
        expect(ratio).toBeGreaterThanOrEqual(4.5);
      });
    });

    describe('Light theme', () => {
      it('text-primary (#0f172a) on bg-primary (#ffffff) >= 4.5:1', () => {
        const ratio = contrastRatio(LIGHT_THEME.textPrimary, LIGHT_THEME.bgPrimary);
        expect(ratio).toBeGreaterThanOrEqual(4.5);
      });

      it('text-secondary (#475569) on bg-primary (#ffffff) >= 4.5:1', () => {
        const ratio = contrastRatio(LIGHT_THEME.textSecondary, LIGHT_THEME.bgPrimary);
        expect(ratio).toBeGreaterThanOrEqual(4.5);
      });

      it('text-primary (#0f172a) on bg-secondary (#f8fafc) >= 4.5:1', () => {
        const ratio = contrastRatio(LIGHT_THEME.textPrimary, LIGHT_THEME.bgSecondary);
        expect(ratio).toBeGreaterThanOrEqual(4.5);
      });

      it('text-secondary (#475569) on bg-secondary (#f8fafc) >= 4.5:1', () => {
        const ratio = contrastRatio(LIGHT_THEME.textSecondary, LIGHT_THEME.bgSecondary);
        expect(ratio).toBeGreaterThanOrEqual(4.5);
      });

      it('text-primary (#0f172a) on bg-tertiary (#f1f5f9) >= 4.5:1', () => {
        const ratio = contrastRatio(LIGHT_THEME.textPrimary, LIGHT_THEME.bgTertiary);
        expect(ratio).toBeGreaterThanOrEqual(4.5);
      });

      it('text-primary (#0f172a) on bg-card (#ffffff) >= 4.5:1', () => {
        const ratio = contrastRatio(LIGHT_THEME.textPrimary, LIGHT_THEME.bgCard);
        expect(ratio).toBeGreaterThanOrEqual(4.5);
      });
    });
  });

  // AC-002: Large text >= 3:1
  describe('AC-002: Large text contrast ratios (>= 3:1)', () => {
    describe('Dark theme', () => {
      it('text-tertiary (#64748b) on bg-primary (#0a0a0f) >= 3:1 (large text)', () => {
        const ratio = contrastRatio(DARK_THEME.textTertiary, DARK_THEME.bgPrimary);
        expect(ratio).toBeGreaterThanOrEqual(3);
      });

      it('text-tertiary (#64748b) on bg-secondary (#12121a) >= 3:1 (large text)', () => {
        const ratio = contrastRatio(DARK_THEME.textTertiary, DARK_THEME.bgSecondary);
        expect(ratio).toBeGreaterThanOrEqual(3);
      });
    });

    describe('Light theme', () => {
      it('text-tertiary (#64748b) on bg-primary (#ffffff) >= 3:1 (large text)', () => {
        const ratio = contrastRatio(LIGHT_THEME.textTertiary, LIGHT_THEME.bgPrimary);
        expect(ratio).toBeGreaterThanOrEqual(3);
      });

      it('text-tertiary (#64748b) on bg-secondary (#f8fafc) >= 3:1 (large text)', () => {
        const ratio = contrastRatio(LIGHT_THEME.textTertiary, LIGHT_THEME.bgSecondary);
        expect(ratio).toBeGreaterThanOrEqual(3);
      });
    });
  });

  // AC-003: UI components >= 3:1
  describe('AC-003: UI component contrast ratios (>= 3:1)', () => {
    describe('Dark theme', () => {
      it('primary (#6366f1) on bg-primary (#0a0a0f) >= 3:1', () => {
        const ratio = contrastRatio(DARK_THEME.primary, DARK_THEME.bgPrimary);
        expect(ratio).toBeGreaterThanOrEqual(3);
      });

      it('primary-600 (#4f46e5) on bg-primary (#0a0a0f) >= 3:1', () => {
        const ratio = contrastRatio(DARK_THEME.primary600, DARK_THEME.bgPrimary);
        expect(ratio).toBeGreaterThanOrEqual(3);
      });

      it('border-focus (#6366f1) on bg-primary (#0a0a0f) >= 3:1', () => {
        const ratio = contrastRatio(DARK_THEME.borderFocus, DARK_THEME.bgPrimary);
        expect(ratio).toBeGreaterThanOrEqual(3);
      });
    });

    describe('Light theme', () => {
      it('primary (#4f46e5) on bg-primary (#ffffff) >= 3:1', () => {
        const ratio = contrastRatio(LIGHT_THEME.primary, LIGHT_THEME.bgPrimary);
        expect(ratio).toBeGreaterThanOrEqual(3);
      });

      it('primary-600 (#4f46e5) on bg-primary (#ffffff) >= 3:1', () => {
        const ratio = contrastRatio(LIGHT_THEME.primary600, LIGHT_THEME.bgPrimary);
        expect(ratio).toBeGreaterThanOrEqual(3);
      });

      it('border-focus (#4f46e5) on bg-primary (#ffffff) >= 3:1', () => {
        const ratio = contrastRatio(LIGHT_THEME.borderFocus, LIGHT_THEME.bgPrimary);
        expect(ratio).toBeGreaterThanOrEqual(3);
      });
    });

    describe('Semantic colors on backgrounds', () => {
      it('success (#22c55e) on dark bg (#0a0a0f) >= 3:1', () => {
        const ratio = contrastRatio('#22c55e', DARK_THEME.bgPrimary);
        expect(ratio).toBeGreaterThanOrEqual(3);
      });

      it('error (#ef4444) on dark bg (#0a0a0f) >= 3:1', () => {
        const ratio = contrastRatio('#ef4444', DARK_THEME.bgPrimary);
        expect(ratio).toBeGreaterThanOrEqual(3);
      });

      it('warning (#f59e0b) on dark bg (#0a0a0f) >= 3:1', () => {
        const ratio = contrastRatio('#f59e0b', DARK_THEME.bgPrimary);
        expect(ratio).toBeGreaterThanOrEqual(3);
      });

      it('info (#3b82f6) on dark bg (#0a0a0f) >= 3:1', () => {
        const ratio = contrastRatio('#3b82f6', DARK_THEME.bgPrimary);
        expect(ratio).toBeGreaterThanOrEqual(3);
      });
    });
  });

  // Button text contrast
  describe('Button text contrast', () => {
    it('white text on primary-600 dark (#4f46e5) >= 4.5:1', () => {
      const ratio = contrastRatio('#ffffff', '#4f46e5');
      expect(ratio).toBeGreaterThanOrEqual(4.5);
    });

    it('white text on error (#ef4444) >= 3:1', () => {
      const ratio = contrastRatio('#ffffff', '#ef4444');
      expect(ratio).toBeGreaterThanOrEqual(3);
    });

    it('white text on secondary-600 (#0891b2) >= 3:1', () => {
      const ratio = contrastRatio('#ffffff', '#0891b2');
      expect(ratio).toBeGreaterThanOrEqual(3);
    });
  });
});
