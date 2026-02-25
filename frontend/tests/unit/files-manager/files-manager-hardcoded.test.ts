/**
 * Unit Tests for Files Manager Hardcoded Color Removal (T-097, T-098)
 * Tests that no hardcoded hex colors remain in FM files.
 */
import { describe, it, expect } from 'vitest';

describe('Files Manager Hardcoded Color Removal', () => {
  // T-097: REQ-006-003-001 - Fix hardcoded colors in index.html
  describe('T-097: No hardcoded colors in FM index.html', () => {
    it('should not contain hardcoded hex color #4a9eff', async () => {
      const { getFilesManagerIndexHTML } = await import('../../../src/components/files-manager/fm-index-html');
      const html = getFilesManagerIndexHTML();
      expect(html).not.toContain('#4a9eff');
    });

    it('should not contain hardcoded hex color #ff4444', async () => {
      const { getFilesManagerIndexHTML } = await import('../../../src/components/files-manager/fm-index-html');
      const html = getFilesManagerIndexHTML();
      expect(html).not.toContain('#ff4444');
    });

    it('should use CSS custom properties for loading spinner', async () => {
      const { getFilesManagerIndexHTML } = await import('../../../src/components/files-manager/fm-index-html');
      const html = getFilesManagerIndexHTML();
      expect(html).toMatch(/var\(--color-primary-500/);
    });

    it('should use CSS custom properties for error colors', async () => {
      const { getFilesManagerIndexHTML } = await import('../../../src/components/files-manager/fm-index-html');
      const html = getFilesManagerIndexHTML();
      expect(html).toMatch(/var\(--color-error/);
    });
  });

  // T-098: REQ-006-003-002 - Fix hardcoded colors in files-epic002.ts
  describe('T-098: No hardcoded colors in files-epic002.ts', () => {
    it('should not contain inline hardcoded rgba backdrop color', async () => {
      const { getFilesEpic002Styles } = await import('../../../src/components/files-manager/fm-epic002-styles');
      const styles = getFilesEpic002Styles();
      // Should not have hardcoded rgba values for modal backdrops
      expect(styles).not.toMatch(/rgba\(0,\s*0,\s*0,\s*0\.5\)/);
    });

    it('should use CSS custom properties for modal backdrop', async () => {
      const { getFilesEpic002Styles } = await import('../../../src/components/files-manager/fm-epic002-styles');
      const styles = getFilesEpic002Styles();
      expect(styles).toContain('var(--');
    });

    it('should use CSS custom properties for shadows', async () => {
      const { getFilesEpic002Styles } = await import('../../../src/components/files-manager/fm-epic002-styles');
      const styles = getFilesEpic002Styles();
      expect(styles).toContain('var(--shadow-');
    });
  });
});
