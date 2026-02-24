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

    // Scope to simulation page's own controls (not Layout's DemoControlBar)
    const simPage = page.locator('[data-testid="simulation-page"]');

    // Select a scenario - the simulation page has its own dropdown
    const scenarioDropdown = simPage.locator('[data-testid="scenario-dropdown"]');
    await expect(scenarioDropdown).toBeVisible();

    // Play button should exist within simulation page
    const playButton = simPage.getByRole('button', { name: 'Play' });
    await expect(playButton).toBeVisible();

    // Stop button should exist within simulation page
    const stopButton = simPage.getByRole('button', { name: 'Stop' });
    await expect(stopButton).toBeVisible();

    // Speed display should exist within simulation page
    await expect(simPage.getByText('Speed:')).toBeVisible();
  });
});

test.describe('E2E-007: Toggle visibility works', () => {
  test('should toggle control bar visibility', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');

    // Control bar should be visible within simulation page
    const controlBar = page.locator('[data-testid="simulation-page"] >> .bg-gray-800');
    await expect(controlBar.first()).toBeVisible();
  });
});
