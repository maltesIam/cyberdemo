/**
 * E2E Tests for Cross-Browser Compatibility
 * E2E-019: Works on Chrome/Firefox/Edge
 */
import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.describe('E2E-019: Works on Chrome/Firefox/Edge', () => {
  test('should render simulation page correctly', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');
    await expect(page.locator('[data-testid="simulation-page"]')).toBeVisible();
    await expect(page.locator('[data-testid="mitre-column"]')).toBeVisible();
    await expect(page.locator('[data-testid="graph-column"]')).toBeVisible();
    await expect(page.locator('[data-testid="aip-column"]')).toBeVisible();
  });
});
