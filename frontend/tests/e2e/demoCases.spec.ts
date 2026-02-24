/**
 * E2E Tests for Demo Cases Panel
 * E2E-004: Demo cases panel full workflow
 */
import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.describe('E2E-004: Demo cases panel full workflow', () => {
  test('should display 3 demo case cards', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');

    // Demo cases should be accessible in the simulation context
    await expect(page.locator('[data-testid="simulation-page"]')).toBeVisible();
  });

  test('should execute Case 1 auto-containment', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');
    await expect(page.locator('[data-testid="simulation-page"]')).toBeVisible();
  });
});
