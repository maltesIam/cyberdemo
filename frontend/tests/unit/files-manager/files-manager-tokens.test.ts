/**
 * Unit Tests for Files Manager Token Migration (T-088 to T-094)
 * Tests that FM CSS tokens map correctly to AgentFlow design tokens.
 */
import { describe, it, expect, beforeEach, afterEach } from 'vitest';

// We test the CSS token file content directly by reading the stylesheet
// and verifying it contains the correct AgentFlow tokens

describe('Files Manager Token Migration', () => {
  let styleElement: HTMLStyleElement;

  beforeEach(() => {
    // Clean up any existing data-theme
    document.documentElement.removeAttribute('data-theme');
  });

  afterEach(() => {
    if (styleElement && styleElement.parentNode) {
      styleElement.parentNode.removeChild(styleElement);
    }
    document.documentElement.removeAttribute('data-theme');
  });

  /**
   * Helper: injects a stylesheet and returns computed style on a test element
   */
  function injectStylesAndGetComputed(css: string, selector: string = '.fm-test'): CSSStyleDeclaration {
    styleElement = document.createElement('style');
    styleElement.textContent = css;
    document.head.appendChild(styleElement);

    const el = document.createElement('div');
    el.className = 'fm-test';
    if (selector !== '.fm-test') {
      el.setAttribute('data-testid', 'fm-element');
    }
    document.body.appendChild(el);
    const computed = window.getComputedStyle(el);
    return computed;
  }

  // T-088: REQ-006-001-001 - Replace --files-bg-primary with --bg-primary (dark)
  describe('T-088: --bg-primary token (dark)', () => {
    it('should define --bg-primary as #020617 in dark theme', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();

      // Dark theme should have --bg-primary: #020617
      expect(css).toContain('--bg-primary');
      expect(css).toMatch(/\[data-theme="dark"\][\s\S]*--bg-primary:\s*#020617/);
    });

    it('should NOT contain legacy --files-bg-primary token', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).not.toContain('--files-bg-primary');
    });
  });

  // T-089: REQ-006-001-002 - Replace --files-bg-secondary with --bg-secondary (dark)
  describe('T-089: --bg-secondary token (dark)', () => {
    it('should define --bg-secondary as #0f172a in dark theme', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).toMatch(/\[data-theme="dark"\][\s\S]*--bg-secondary:\s*#0f172a/);
    });

    it('should NOT contain legacy --files-bg-secondary token', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).not.toContain('--files-bg-secondary');
    });
  });

  // T-090: REQ-006-001-003 - Replace --files-bg-tertiary with --bg-tertiary (dark)
  describe('T-090: --bg-tertiary token (dark)', () => {
    it('should define --bg-tertiary as #1e293b in dark theme', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).toMatch(/\[data-theme="dark"\][\s\S]*--bg-tertiary:\s*#1e293b/);
    });

    it('should NOT contain legacy --files-bg-tertiary token', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).not.toContain('--files-bg-tertiary');
    });
  });

  // T-091: REQ-006-001-004 - Replace --files-text-* with --text-* tokens
  describe('T-091: --text-* tokens', () => {
    it('should define --text-primary in dark theme as #f8fafc', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).toMatch(/\[data-theme="dark"\][\s\S]*--text-primary:\s*#f8fafc/);
    });

    it('should define --text-secondary in dark theme as #94a3b8', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).toMatch(/\[data-theme="dark"\][\s\S]*--text-secondary:\s*#94a3b8/);
    });

    it('should define --text-tertiary in dark theme as #64748b', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).toMatch(/\[data-theme="dark"\][\s\S]*--text-tertiary:\s*#64748b/);
    });

    it('should NOT contain legacy --files-text-* tokens', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).not.toContain('--files-text-primary');
      expect(css).not.toContain('--files-text-secondary');
      expect(css).not.toContain('--files-text-tertiary');
    });
  });

  // T-092: REQ-006-001-005 - Replace --files-border with --border-* tokens
  describe('T-092: --border-* tokens', () => {
    it('should define --border-primary in dark theme as #334155', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).toMatch(/\[data-theme="dark"\][\s\S]*--border-primary:\s*#334155/);
    });

    it('should define --border-secondary in dark theme as #1e293b', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).toMatch(/\[data-theme="dark"\][\s\S]*--border-secondary:\s*#1e293b/);
    });

    it('should NOT contain legacy --files-border token', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).not.toContain('--files-border');
    });
  });

  // T-093: REQ-006-001-006 - Update light theme values to AgentFlow spec
  describe('T-093: Light theme tokens', () => {
    it('should define light theme --bg-primary as #ffffff', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).toMatch(/\[data-theme="light"\][\s\S]*--bg-primary:\s*#ffffff/);
    });

    it('should define light theme --bg-secondary as #f8fafc', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).toMatch(/\[data-theme="light"\][\s\S]*--bg-secondary:\s*#f8fafc/);
    });

    it('should define light theme --bg-tertiary as #f1f5f9', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).toMatch(/\[data-theme="light"\][\s\S]*--bg-tertiary:\s*#f1f5f9/);
    });

    it('should define light theme --text-primary as #0f172a', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).toMatch(/\[data-theme="light"\][\s\S]*--text-primary:\s*#0f172a/);
    });

    it('should define light theme --text-secondary as #475569', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).toMatch(/\[data-theme="light"\][\s\S]*--text-secondary:\s*#475569/);
    });

    it('should define light theme --border-primary as #e2e8f0', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).toMatch(/\[data-theme="light"\][\s\S]*--border-primary:\s*#e2e8f0/);
    });
  });

  // T-094: REQ-006-001-007 - Add missing shadow, radius, spacing tokens
  describe('T-094: Shadow, radius, spacing tokens', () => {
    it('should define shadow tokens', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).toContain('--shadow-sm');
      expect(css).toContain('--shadow-md');
      expect(css).toContain('--shadow-lg');
    });

    it('should define radius tokens', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).toContain('--radius-sm');
      expect(css).toContain('--radius-md');
      expect(css).toContain('--radius-lg');
      expect(css).toContain('--radius-xl');
      expect(css).toContain('--radius-full');
    });

    it('should define spacing tokens', async () => {
      const { getFilesManagerTokensCSS } = await import('../../../src/components/files-manager/fm-design-tokens');
      const css = getFilesManagerTokensCSS();
      expect(css).toContain('--space-1');
      expect(css).toContain('--space-2');
      expect(css).toContain('--space-3');
      expect(css).toContain('--space-4');
      expect(css).toContain('--space-6');
      expect(css).toContain('--space-8');
    });
  });
});
