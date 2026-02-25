/**
 * UT-001: REQ-001-001-001 - Color Scale Tokens
 * Task: T-001-001
 *
 * Verifies all color scale tokens (Primary blue, Secondary cyan, Accent amber,
 * Neutral slate, Semantic colors, Agent status colors) are defined as CSS
 * custom properties in :root.
 */
import { describe, it, expect, beforeAll } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

let cssContent: string;

beforeAll(() => {
  const cssPath = path.resolve(__dirname, '../../../src/styles/design-tokens.css');
  cssContent = fs.readFileSync(cssPath, 'utf-8');
});

describe('UT-001: Color Scale Tokens (REQ-001-001-001)', () => {
  // AC-001: All Primary color tokens (50-950) defined
  describe('AC-001: Primary color palette (Blue) tokens 50-950', () => {
    const primaryShades = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950];
    primaryShades.forEach((shade) => {
      it(`should define --color-primary-${shade}`, () => {
        expect(cssContent).toContain(`--color-primary-${shade}`);
      });
    });
  });

  // AC-002: All Secondary color tokens (50-950) defined
  describe('AC-002: Secondary color palette (Cyan) tokens', () => {
    const secondaryShades = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950];
    secondaryShades.forEach((shade) => {
      it(`should define --color-secondary-${shade}`, () => {
        expect(cssContent).toContain(`--color-secondary-${shade}`);
      });
    });
  });

  // AC-003: All Accent color tokens (50-900) defined
  describe('AC-003: Accent color palette (Amber) tokens', () => {
    const accentShades = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900];
    accentShades.forEach((shade) => {
      it(`should define --color-accent-${shade}`, () => {
        expect(cssContent).toContain(`--color-accent-${shade}`);
      });
    });
  });

  // AC-004: All Neutral color tokens (0-950) defined
  describe('AC-004: Neutral color palette (Slate) tokens', () => {
    const neutralShades = [0, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950];
    neutralShades.forEach((shade) => {
      it(`should define --color-neutral-${shade}`, () => {
        expect(cssContent).toContain(`--color-neutral-${shade}`);
      });
    });
  });

  // AC-005: All Semantic color tokens defined
  describe('AC-005: Semantic color tokens', () => {
    const semanticTokens = [
      '--color-success',
      '--color-success-light',
      '--color-success-dark',
      '--color-warning',
      '--color-warning-light',
      '--color-warning-dark',
      '--color-error',
      '--color-error-light',
      '--color-error-dark',
      '--color-info',
      '--color-info-light',
      '--color-info-dark',
    ];
    semanticTokens.forEach((token) => {
      it(`should define ${token}`, () => {
        expect(cssContent).toContain(`${token}:`);
      });
    });
  });

  // AC-006: All Agent status color tokens defined
  describe('AC-006: Agent status color tokens', () => {
    const agentStatuses = ['idle', 'running', 'success', 'error', 'waiting', 'queued'];
    agentStatuses.forEach((status) => {
      it(`should define --color-agent-${status}`, () => {
        expect(cssContent).toContain(`--color-agent-${status}`);
      });
    });
  });

  // Verify color values match spec
  describe('Color values match AgentFlow spec', () => {
    it('should set --color-agent-idle to slate (#94a3b8)', () => {
      expect(cssContent).toMatch(/--color-agent-idle:\s*#94a3b8/);
    });

    it('should set --color-agent-running to blue (#3b82f6)', () => {
      expect(cssContent).toMatch(/--color-agent-running:\s*#3b82f6/);
    });

    it('should set --color-agent-success to green (#22c55e)', () => {
      expect(cssContent).toMatch(/--color-agent-success:\s*#22c55e/);
    });

    it('should set --color-agent-error to red (#ef4444)', () => {
      expect(cssContent).toMatch(/--color-agent-error:\s*#ef4444/);
    });

    it('should set --color-agent-waiting to amber (#f59e0b)', () => {
      expect(cssContent).toMatch(/--color-agent-waiting:\s*#f59e0b/);
    });

    it('should set --color-agent-queued to cyan (#06b6d4)', () => {
      expect(cssContent).toMatch(/--color-agent-queued:\s*#06b6d4/);
    });
  });
});
