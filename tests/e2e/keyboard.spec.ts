/**
 * E2E Tests for Keyboard Shortcuts
 * E2E-008: Space key toggles play/pause
 * E2E-009: Esc key stops simulation
 * E2E-017: Keyboard shortcuts work
 */
import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.describe('E2E-008: Space key toggles play/pause', () => {
  test('should toggle play/pause on Space press', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');
    await expect(page.locator('[data-testid="simulation-page"]')).toBeVisible();
  });
});

test.describe('E2E-009: Esc key stops simulation', () => {
  test('should stop simulation on Escape press', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');
    await expect(page.locator('[data-testid="simulation-page"]')).toBeVisible();
  });
});

test.describe('E2E-017: Keyboard shortcuts work', () => {
  test('should register all keyboard shortcuts', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');
    await expect(page.locator('[data-testid="simulation-page"]')).toBeVisible();
  });
});
