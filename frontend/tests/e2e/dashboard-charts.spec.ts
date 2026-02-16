/**
 * E2E Tests for Dashboard Charts and Widgets
 *
 * Tests verify that all dashboard charts/widgets:
 * 1. Display actual data (not placeholders)
 * 2. Show proper visualizations
 * 3. Are responsive and functional
 */

import { test, expect } from "@playwright/test";

const BASE_URL = "http://localhost:3000";
const API_URL = "http://localhost:8000";

test.describe("Dashboard Charts - Pre-condition: Generate Data", () => {
  test.beforeAll(async ({ request }) => {
    // Ensure data exists before running chart tests
    const statusResponse = await request.get(`${API_URL}/gen/status`);
    const status = await statusResponse.json();

    // Generate data if not present
    if (status.incidents < 10) {
      await request.post(`${API_URL}/gen/incidents`);
    }
    if (status.detections < 10) {
      await request.post(`${API_URL}/gen/edr`);
    }
    if (status.assets < 5) {
      await request.post(`${API_URL}/gen/assets`);
    }
  });
});

test.describe("Dashboard Charts - Incidents by Hour Widget", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    await page.waitForTimeout(2000); // Wait for data to load
  });

  test("DASH-CHART-001: Incidents by Hour chart container exists", async ({ page }) => {
    // Should have a section titled "Incidents by Hour"
    const chartSection = page.locator(
      "h3:has-text('Incidents by Hour'), h2:has-text('Incidents by Hour')",
    );
    await expect(chartSection).toBeVisible();
  });

  test("DASH-CHART-002: Incidents by Hour shows actual chart (not placeholder)", async ({
    page,
  }) => {
    // The chart section should NOT contain placeholder text
    const placeholderText = page.locator("text='Connect to backend for live data'");
    const placeholderCount = await placeholderText.count();

    // After fix, there should be no placeholders OR at most one (for detection trend if not yet fixed)
    // For this specific chart, check its container doesn't have the placeholder
    const incidentsSection = page.locator("h3:has-text('Incidents by Hour')").locator("..");
    const hasPlaceholder = await incidentsSection
      .locator("text='Connect to backend for live data'")
      .isVisible()
      .catch(() => false);

    expect(hasPlaceholder).toBeFalsy();
  });

  test("DASH-CHART-003: Incidents by Hour displays bars or chart elements", async ({ page }) => {
    // Should have SVG chart elements or visual bars
    const incidentsSection = page.locator("h3:has-text('Incidents by Hour')").locator("..");

    // Check for SVG (chart) or bar elements
    const hasSvg = await incidentsSection.locator("svg").count();
    const hasBars = await incidentsSection.locator("[class*='bar'], [class*='bg-']").count();
    const hasDataElements = await incidentsSection.locator("rect, line, path").count();

    expect(hasSvg > 0 || hasBars > 0 || hasDataElements > 0).toBeTruthy();
  });

  test("DASH-CHART-004: Incidents by Hour shows hour labels", async ({ page }) => {
    const incidentsSection = page.locator("h3:has-text('Incidents by Hour')").locator("..");

    // Should have hour labels like "00:00", "06:00", etc.
    const hasHourLabels = await incidentsSection.locator("text=/\\d{1,2}:\\d{2}/").count();
    expect(hasHourLabels).toBeGreaterThan(0);
  });
});

test.describe("Dashboard Charts - Severity Distribution Widget", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    await page.waitForTimeout(2000);
  });

  test("DASH-CHART-005: Severity Distribution section exists", async ({ page }) => {
    const severitySection = page.locator("h3:has-text('Severity'), h2:has-text('Severity')");
    await expect(severitySection).toBeVisible();
  });

  test("DASH-CHART-006: Severity Distribution shows severity levels", async ({ page }) => {
    // Should show severity levels: critical, high, medium, low
    const severityLabels = ["High", "Critical", "Medium", "Low"];
    let foundCount = 0;

    for (const label of severityLabels) {
      const labelVisible = await page
        .locator(`text=${label}`)
        .first()
        .isVisible()
        .catch(() => false);
      if (labelVisible) foundCount++;
    }

    expect(foundCount).toBeGreaterThan(0);
  });

  test("DASH-CHART-007: Severity Distribution shows progress bars", async ({ page }) => {
    const severitySection = page.locator("h3:has-text('Severity')").locator("..");

    // Should have progress bar elements
    const progressBars = await severitySection
      .locator("[class*='rounded-full'], [class*='h-2'], [role='progressbar']")
      .count();
    expect(progressBars).toBeGreaterThan(0);
  });

  test("DASH-CHART-008: Severity Distribution shows percentages", async ({ page }) => {
    const severitySection = page.locator("h3:has-text('Severity')").locator("..");

    // Should show percentage values
    const hasPercentages = await severitySection.locator("text=/\\d+(\\.\\d+)?%/").count();
    expect(hasPercentages).toBeGreaterThan(0);
  });
});

test.describe("Dashboard Charts - Top Affected Hosts Widget", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    await page.waitForTimeout(2000);
  });

  test("DASH-CHART-009: Top Affected Hosts section exists", async ({ page }) => {
    const hostsSection = page.locator(
      "h3:has-text('Top Affected Hosts'), h2:has-text('Top Affected Hosts')",
    );
    await expect(hostsSection).toBeVisible();
  });

  test("DASH-CHART-010: Top Affected Hosts shows host data (not 'No host data')", async ({
    page,
  }) => {
    const hostsSection = page.locator("h3:has-text('Top Affected Hosts')").locator("..");

    // Should NOT show "No host data available" message when data exists
    const noDataMessage = await hostsSection
      .locator("text='No host data available'")
      .isVisible()
      .catch(() => false);

    // When data exists, should show actual hosts
    const hasHostNames = await hostsSection
      .locator("text=/[a-zA-Z0-9-]+\\.(local|corp|internal|com)/")
      .count();

    // Either should have host names OR (if no incidents) can show no data message
    // After fix, with generated data, should show host names
    expect(hasHostNames > 0 || !noDataMessage).toBeTruthy();
  });

  test("DASH-CHART-011: Top Affected Hosts shows numbered list", async ({ page }) => {
    const hostsSection = page.locator("h3:has-text('Top Affected Hosts')").locator("..");

    // Should have numbered items (1. 2. 3. etc.) or ranking
    const hasNumbers = await hostsSection.locator("text=/^[1-5]\\.$/").count();
    const hasProgressBars = await hostsSection.locator("[class*='rounded-full']").count();

    expect(hasNumbers > 0 || hasProgressBars > 0).toBeTruthy();
  });
});

test.describe("Dashboard Charts - Detection Trend Widget", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    await page.waitForTimeout(2000);
  });

  test("DASH-CHART-012: Detection Trend section exists", async ({ page }) => {
    const trendSection = page.locator(
      "h3:has-text('Detection Trend'), h2:has-text('Detection Trend')",
    );
    await expect(trendSection).toBeVisible();
  });

  test("DASH-CHART-013: Detection Trend shows actual chart (not placeholder)", async ({ page }) => {
    const trendSection = page.locator("h3:has-text('Detection Trend')").locator("..");

    // Should NOT contain placeholder text
    const hasPlaceholder = await trendSection
      .locator("text='Connect to backend for live data'")
      .isVisible()
      .catch(() => false);

    expect(hasPlaceholder).toBeFalsy();
  });

  test("DASH-CHART-014: Detection Trend displays chart elements", async ({ page }) => {
    const trendSection = page.locator("h3:has-text('Detection Trend')").locator("..");

    // Should have line chart SVG elements
    const hasSvg = await trendSection.locator("svg").count();
    const hasLines = await trendSection.locator("path, line, polyline").count();
    const hasDataBars = await trendSection.locator("[class*='bg-']").count();

    expect(hasSvg > 0 || hasLines > 0 || hasDataBars > 0).toBeTruthy();
  });

  test("DASH-CHART-015: Detection Trend shows day labels", async ({ page }) => {
    const trendSection = page.locator("h3:has-text('Detection Trend')").locator("..");

    // Should have day labels like Mon, Tue, etc. or dates
    const dayLabels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    let foundDays = 0;
    for (const day of dayLabels) {
      const found = await trendSection.locator(`text=${day}`).count();
      if (found > 0) foundDays++;
    }

    // Or date format like "02/14", "Feb 14"
    const hasDateLabels = await trendSection
      .locator("text=/\\d{1,2}\\/\\d{1,2}|[A-Z][a-z]{2} \\d{1,2}/")
      .count();

    expect(foundDays > 0 || hasDateLabels > 0).toBeTruthy();
  });
});

test.describe("Dashboard Charts - KPI Cards Widget", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    await page.waitForTimeout(2000);
  });

  test("DASH-CHART-016: Total Incidents KPI card shows number", async ({ page }) => {
    const totalIncidents = page.locator("text='Total Incidents'").locator("..");
    await expect(totalIncidents).toBeVisible();

    // Should show a number value
    const hasNumber = await totalIncidents.locator("text=/^\\d+$|^\\d{1,3}(,\\d{3})*$/").count();
    expect(hasNumber).toBeGreaterThan(0);
  });

  test("DASH-CHART-017: Critical Open KPI card shows number", async ({ page }) => {
    const criticalOpen = page.locator("text='Critical Open'").locator("..");
    await expect(criticalOpen).toBeVisible();

    const hasNumber = await criticalOpen.locator("text=/^\\d+$|^\\d{1,3}(,\\d{3})*$/").count();
    expect(hasNumber).toBeGreaterThan(0);
  });

  test("DASH-CHART-018: Hosts Contained KPI card exists", async ({ page }) => {
    const hostsContained = page.locator("text='Hosts Contained'").locator("..");
    await expect(hostsContained).toBeVisible();
  });

  test("DASH-CHART-019: MTTR KPI card shows time value", async ({ page }) => {
    const mttr = page.locator("text='MTTR'").locator("..");
    await expect(mttr).toBeVisible();

    // Should show time value like "4.5h" or similar
    const hasTimeValue = await mttr.locator("text=/\\d+\\.?\\d*h/").count();
    expect(hasTimeValue).toBeGreaterThan(0);
  });
});

test.describe("Dashboard Charts - API Integration", () => {
  test("DASH-API-001: Dashboard KPIs endpoint returns data", async ({ request }) => {
    const response = await request.get(`${API_URL}/dashboard/kpis`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data).toHaveProperty("total_incidents");
    expect(data).toHaveProperty("incidents_by_severity");
    expect(data).toHaveProperty("incidents_by_hour");
    expect(data).toHaveProperty("top_affected_hosts");
  });

  test("DASH-API-002: Dashboard KPIs has incidents_by_hour data", async ({ request }) => {
    const response = await request.get(`${API_URL}/dashboard/kpis`);
    const data = await response.json();

    expect(Array.isArray(data.incidents_by_hour)).toBeTruthy();
    // Should have 24 hours of data
    expect(data.incidents_by_hour.length).toBe(24);
  });

  test("DASH-API-003: Dashboard KPIs has detection_trend data", async ({ request }) => {
    const response = await request.get(`${API_URL}/dashboard/kpis`);
    const data = await response.json();

    // After fix, should have detection_trend array
    expect(data).toHaveProperty("detection_trend");
    expect(Array.isArray(data.detection_trend)).toBeTruthy();
    // Should have 7 days of data
    expect(data.detection_trend.length).toBe(7);
  });
});
