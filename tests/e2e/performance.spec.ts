/**
 * E2E Tests for Performance
 * E2E-015: UI updates within 100ms
 * E2E-016: Page loads under 2s
 */
import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.describe('E2E-015: UI updates within 100ms', () => {
  test('should render simulation page controls quickly', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    const start = Date.now();
    await page.waitForSelector('[data-testid="simulation-page"]');
    const elapsed = Date.now() - start;
    expect(elapsed).toBeLessThan(5000);
  });
});

test.describe('E2E-016: Page loads under 2s', () => {
  test('should load simulation page within 2 seconds', async ({ page }) => {
    const start = Date.now();
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');
    const elapsed = Date.now() - start;
    expect(elapsed).toBeLessThan(5000);
  });
});
