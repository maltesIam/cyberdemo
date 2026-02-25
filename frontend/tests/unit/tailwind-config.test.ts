/**
 * Unit Tests: Tailwind Config Extension
 * Tasks: T-006 (REQ-001-002-001), T-007 (REQ-001-002-002), T-008 (REQ-001-002-003)
 *
 * Tests verify Tailwind config references CSS custom properties via var() syntax.
 */
import { describe, it, expect, beforeAll } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

let tailwindConfigContent: string;

beforeAll(() => {
  const configPath = path.resolve(__dirname, '../../tailwind.config.js');
  tailwindConfigContent = fs.readFileSync(configPath, 'utf-8');
});

// UT-006: REQ-001-002-001 - CyberDemo tailwind.config.js references CSS custom properties
describe('T-006: Tailwind config references CSS custom properties', () => {
  it('should use var(--token) syntax for colors', () => {
    expect(tailwindConfigContent).toMatch(/var\(--/);
  });

  it('should define primary color using CSS custom property', () => {
    expect(tailwindConfigContent).toContain('var(--primary)');
  });

  it('should define background colors using CSS custom properties', () => {
    expect(tailwindConfigContent).toContain('var(--bg-primary)');
  });

  it('should define text colors using CSS custom properties', () => {
    expect(tailwindConfigContent).toContain('var(--text-primary)');
  });

  it('should define border colors using CSS custom properties', () => {
    expect(tailwindConfigContent).toContain('var(--border-primary)');
  });

  it('should keep existing soc-* colors', () => {
    expect(tailwindConfigContent).toContain('soc-red');
    expect(tailwindConfigContent).toContain('soc-orange');
    expect(tailwindConfigContent).toContain('soc-yellow');
    expect(tailwindConfigContent).toContain('soc-green');
  });
});

// UT-008: REQ-001-002-003 - Tailwind font families configured for Inter + JetBrains Mono
describe('T-008: Tailwind font families configured', () => {
  it('should configure sans font family with Inter', () => {
    expect(tailwindConfigContent).toMatch(/sans.*Inter/s);
  });

  it('should configure mono font family with JetBrains Mono', () => {
    expect(tailwindConfigContent).toMatch(/mono.*JetBrains Mono/s);
  });
});
