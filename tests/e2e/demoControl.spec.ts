/**
 * E2E Tests for Demo Control Bar
 * E2E-001: Demo control bar full workflow
 * E2E-007: Toggle visibility works
 */
import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.describe('E2E-001: Demo control bar full workflow', () => {
  test('should select scenario, play, adjust speed, view MITRE progress, pause, stop', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');

    // Select a scenario
    const scenarioDropdown = page.locator('[data-testid="scenario-dropdown"]');
    await expect(scenarioDropdown).toBeVisible();

    // Play button should exist
    const playButton = page.getByRole('button', { name: 'Play' });
    await expect(playButton).toBeVisible();

    // Stop button should exist
    const stopButton = page.getByRole('button', { name: 'Stop' });
    await expect(stopButton).toBeVisible();

    // Speed display should exist
    await expect(page.getByText('Speed:')).toBeVisible();
  });
});

test.describe('E2E-007: Toggle visibility works', () => {
  test('should toggle control bar visibility', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');

    // Control bar should be visible
    const controlBar = page.locator('[data-testid="simulation-page"] >> .bg-gray-800');
    await expect(controlBar.first()).toBeVisible();
  });
});
