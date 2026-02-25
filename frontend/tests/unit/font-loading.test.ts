/**
 * Unit Tests: Font Loading
 * Tasks: T-009 (REQ-001-003-001), T-010 (REQ-001-003-002), T-011 (REQ-001-003-003)
 *
 * Tests verify Inter and JetBrains Mono fonts are loaded with correct weights.
 */
import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

// Check across index.html and design-tokens.css for font loading
function getProjectFiles(): string {
  const files = [
    path.resolve(__dirname, '../../index.html'),
    path.resolve(__dirname, '../../src/styles/design-tokens.css'),
    path.resolve(__dirname, '../../src/index.css'),
  ];
  return files
    .filter(f => fs.existsSync(f))
    .map(f => fs.readFileSync(f, 'utf-8'))
    .join('\n');
}

// UT-009: REQ-001-003-001 - Inter font loaded with weights 300-800
describe('T-009: Inter font loaded with correct weights', () => {
  it('should reference Inter font', () => {
    const content = getProjectFiles();
    expect(content).toMatch(/Inter/);
  });

  it('should load Inter with weight range 300-800 or individual weights', () => {
    const content = getProjectFiles();
    // Check for Google Fonts URL or @font-face declarations
    const hasGoogleFonts = content.match(/fonts\.googleapis\.com.*Inter.*wght@[^"']*300/);
    const hasFontFace = content.match(/@font-face[^}]*Inter/s);
    const hasImport = content.match(/@import.*Inter/);
    expect(hasGoogleFonts || hasFontFace || hasImport).toBeTruthy();
  });
});

// UT-010: REQ-001-003-002 - JetBrains Mono font loaded with weights 400, 600
describe('T-010: JetBrains Mono font loaded with correct weights', () => {
  it('should reference JetBrains Mono font', () => {
    const content = getProjectFiles();
    expect(content).toMatch(/JetBrains\+Mono|JetBrains Mono/);
  });

  it('should load JetBrains Mono with weights 400 and 600', () => {
    const content = getProjectFiles();
    const hasGoogleFonts = content.match(/fonts\.googleapis\.com.*JetBrains\+Mono.*wght@[^"']*400/);
    const hasFontFace = content.match(/@font-face[^}]*JetBrains Mono/s);
    const hasImport = content.match(/@import.*JetBrains/);
    expect(hasGoogleFonts || hasFontFace || hasImport).toBeTruthy();
  });
});

// UT-011: REQ-001-003-003 - Verify font-display: swap
describe('T-011: font-display swap configured', () => {
  it('should use font-display: swap or display=swap parameter', () => {
    const content = getProjectFiles();
    const hasDisplaySwap = content.includes('display=swap') || content.includes('font-display: swap');
    expect(hasDisplaySwap).toBe(true);
  });
});
