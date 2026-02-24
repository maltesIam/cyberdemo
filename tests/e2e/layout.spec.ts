/**
 * E2E Tests for Layout
 * E2E-018: Min width 1280px enforced
 */
import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.describe('E2E-018: Min width 1280px enforced', () => {
  test('should display properly at 1280px width', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');
    await expect(page.locator('[data-testid="simulation-page"]')).toBeVisible();
  });
});
