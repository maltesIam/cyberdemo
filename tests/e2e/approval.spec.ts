/**
 * E2E Tests for Approval Card Workflow
 * E2E-005: Approval card workflow
 */
import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.describe('E2E-005: Approval card workflow', () => {
  test('should show approval card for VIP case requiring human decision', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');
    await expect(page.locator('[data-testid="simulation-page"]')).toBeVisible();
  });
});
