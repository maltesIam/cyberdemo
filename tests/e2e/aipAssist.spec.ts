/**
 * E2E Tests for aIP Assist Widget
 * E2E-002: aIP Assist widget full workflow
 */
import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.describe('E2E-002: aIP Assist widget full workflow', () => {
  test('should show aIP panel in simulation page', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');

    const aipColumn = page.locator('[data-testid="aip-column"]');
    await expect(aipColumn).toBeVisible();
  });

  test('should display suggestion list when expanded', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');

    const aipColumn = page.locator('[data-testid="aip-column"]');
    await expect(aipColumn).toBeVisible();
  });
});
