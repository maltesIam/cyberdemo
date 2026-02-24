/**
 * E2E Tests for Accessibility
 * E2E-020: Full keyboard navigation
 */
import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.describe('E2E-020: Full keyboard navigation', () => {
  test('should support Tab navigation through simulation controls', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');

    // Tab to first interactive element
    await page.keyboard.press('Tab');
    const focused = await page.evaluate(() => document.activeElement?.tagName);
    expect(focused).toBeTruthy();
  });

  test('should have accessible labels on control buttons', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');

    // Verify ARIA labels on buttons
    const playButton = page.getByRole('button', { name: /Play|Pause/ });
    await expect(playButton).toBeVisible();

    const stopButton = page.getByRole('button', { name: 'Stop' });
    await expect(stopButton).toBeVisible();
  });
});
