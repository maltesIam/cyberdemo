/**
 * Unit Tests for Files Manager Component Integration (T-095, T-096)
 * Tests that theme-toggle and font-size-button Lit components are integrated in FM toolbar.
 */
import { describe, it, expect } from 'vitest';

describe('Files Manager Component Integration', () => {
  // T-095: REQ-006-002-001 - Integrate theme-toggle in FM toolbar
  describe('T-095: Theme toggle in FM toolbar', () => {
    it('should export FM toolbar HTML that includes theme-toggle component', async () => {
      const { getFilesManagerToolbarHTML } = await import('../../../src/components/files-manager/fm-toolbar');
      const html = getFilesManagerToolbarHTML();
      expect(html).toContain('theme-toggle');
    });

    it('should place theme-toggle in the toolbar actions area', async () => {
      const { getFilesManagerToolbarHTML } = await import('../../../src/components/files-manager/fm-toolbar');
      const html = getFilesManagerToolbarHTML();
      expect(html).toContain('toolbar-actions');
      expect(html).toContain('theme-toggle');
    });
  });

  // T-096: REQ-006-002-002 - Integrate font-size-button in FM toolbar
  describe('T-096: Font size button in FM toolbar', () => {
    it('should export FM toolbar HTML that includes font-size-button component', async () => {
      const { getFilesManagerToolbarHTML } = await import('../../../src/components/files-manager/fm-toolbar');
      const html = getFilesManagerToolbarHTML();
      expect(html).toContain('font-size-button');
    });

    it('should place font-size-button before (left of) theme-toggle', async () => {
      const { getFilesManagerToolbarHTML } = await import('../../../src/components/files-manager/fm-toolbar');
      const html = getFilesManagerToolbarHTML();
      const fontSizeIdx = html.indexOf('font-size-button');
      const themeToggleIdx = html.indexOf('theme-toggle');
      expect(fontSizeIdx).toBeLessThan(themeToggleIdx);
    });
  });
});
