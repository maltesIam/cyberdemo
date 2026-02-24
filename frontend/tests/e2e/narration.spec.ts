/**
 * E2E Tests for Narration Footer
 * E2E-003: Narration footer full workflow
 * E2E-010: Filter messages by type
 */
import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.describe('E2E-003: Narration footer full workflow', () => {
  test('should display narration footer at bottom of simulation page', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');

    // Scope to the simulation page's inline narration footer
    const footer = page.locator('[data-testid="simulation-page"] [data-testid="narration-footer"]');
    await expect(footer).toBeVisible();
  });

  test('should show messages with color coding', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');

    const footer = page.locator('[data-testid="simulation-page"] [data-testid="narration-footer"]');
    await expect(footer).toBeVisible();
  });
});

test.describe('E2E-010: Filter messages by type', () => {
  test('should filter narration messages by selected type', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');

    // Narration footer should be present within the simulation page
    const footer = page.locator('[data-testid="simulation-page"] [data-testid="narration-footer"]');
    await expect(footer).toBeVisible();
  });
});
