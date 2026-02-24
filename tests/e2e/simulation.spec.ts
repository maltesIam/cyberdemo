/**
 * E2E Tests for Simulation Page
 * E2E-011: Simulation page layout
 * E2E-012: MITRE phases panel
 * E2E-013: Attack graph visualization
 * E2E-014: AI analysis panel
 */
import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.describe('E2E-011: Simulation page layout', () => {
  test('should show 3-column layout', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');

    await expect(page.locator('[data-testid="mitre-column"]')).toBeVisible();
    await expect(page.locator('[data-testid="graph-column"]')).toBeVisible();
    await expect(page.locator('[data-testid="aip-column"]')).toBeVisible();
  });
});

test.describe('E2E-012: MITRE phases panel', () => {
  test('should display MITRE phases in left column', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');

    const mitreColumn = page.locator('[data-testid="mitre-column"]');
    await expect(mitreColumn).toBeVisible();
  });
});

test.describe('E2E-013: Attack graph visualization', () => {
  test('should render attack graph in center column', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');

    const graphColumn = page.locator('[data-testid="graph-column"]');
    await expect(graphColumn).toBeVisible();
  });
});

test.describe('E2E-014: AI analysis panel', () => {
  test('should display AI analysis panel in right column', async ({ page }) => {
    await page.goto(`${BASE_URL}/simulation`);
    await page.waitForSelector('[data-testid="simulation-page"]');

    const aipColumn = page.locator('[data-testid="aip-column"]');
    await expect(aipColumn).toBeVisible();
  });
});
