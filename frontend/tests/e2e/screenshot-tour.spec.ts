/**
 * Screenshot Tour - Captures screenshots of all main pages and Medicum tabs
 * for visual review of the application.
 */
import { test, expect } from "@playwright/test";
import * as path from "path";
import * as fs from "fs";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const BASE_URL = "http://localhost:5173";
const SCREENSHOT_DIR = path.join(
  __dirname,
  "../../test-results/screenshots-tour"
);

test.beforeAll(() => {
  if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  }
});

test.use({
  baseURL: BASE_URL,
  viewport: { width: 1440, height: 900 },
});

test("01 - Main page (Generation - default redirect)", async ({ page }) => {
  await page.goto(BASE_URL);
  await page.waitForLoadState("networkidle");
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "01-main-generation.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 01-main-generation.png");
});

test("02 - Command Center (Surface)", async ({ page }) => {
  await page.goto(`${BASE_URL}/surface`);
  await page.waitForLoadState("networkidle");
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "02-command-center.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 02-command-center.png");
});

test("03 - Dashboard", async ({ page }) => {
  await page.goto(`${BASE_URL}/dashboard`);
  await page.waitForLoadState("networkidle");
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "03-dashboard.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 03-dashboard.png");
});

test("04 - Assets", async ({ page }) => {
  await page.goto(`${BASE_URL}/assets`);
  await page.waitForLoadState("networkidle");
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "04-assets.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 04-assets.png");
});

test("05 - Incidents", async ({ page }) => {
  await page.goto(`${BASE_URL}/incidents`);
  await page.waitForLoadState("networkidle");
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "05-incidents.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 05-incidents.png");
});

test("06 - Detections", async ({ page }) => {
  await page.goto(`${BASE_URL}/detections`);
  await page.waitForLoadState("networkidle");
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "06-detections.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 06-detections.png");
});

test("07 - CTEM", async ({ page }) => {
  await page.goto(`${BASE_URL}/ctem`);
  await page.waitForLoadState("networkidle");
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "07-ctem.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 07-ctem.png");
});

test("08 - Threats Enrichment", async ({ page }) => {
  await page.goto(`${BASE_URL}/threats`);
  await page.waitForLoadState("networkidle");
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "08-threats.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 08-threats.png");
});

test("09 - Vulnerabilities", async ({ page }) => {
  await page.goto(`${BASE_URL}/vulnerabilities`);
  await page.waitForLoadState("networkidle");
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "09-vulnerabilities.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 09-vulnerabilities.png");
});

test("10 - Simulation", async ({ page }) => {
  await page.goto(`${BASE_URL}/simulation`);
  await page.waitForLoadState("networkidle");
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "10-simulation.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 10-simulation.png");
});

test("11 - Graph", async ({ page }) => {
  await page.goto(`${BASE_URL}/graph`);
  await page.waitForLoadState("networkidle");
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "11-graph.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 11-graph.png");
});

test("12 - Postmortems", async ({ page }) => {
  await page.goto(`${BASE_URL}/postmortems`);
  await page.waitForLoadState("networkidle");
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "12-postmortems.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 12-postmortems.png");
});

test("13 - Timeline", async ({ page }) => {
  await page.goto(`${BASE_URL}/timeline`);
  await page.waitForLoadState("networkidle");
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "13-timeline.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 13-timeline.png");
});

test("14 - Tickets", async ({ page }) => {
  await page.goto(`${BASE_URL}/tickets`);
  await page.waitForLoadState("networkidle");
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "14-tickets.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 14-tickets.png");
});

test("15 - Config", async ({ page }) => {
  await page.goto(`${BASE_URL}/config`);
  await page.waitForLoadState("networkidle");
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "15-config.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 15-config.png");
});

// ---- MEDICUM PAGE AND ALL TABS ----

test("16 - Medicum main page (Consulta tab)", async ({ page }) => {
  await page.goto(`${BASE_URL}/medicum`);
  await page.waitForLoadState("networkidle");
  // Wait for the page to fully render
  await page.waitForTimeout(1000);
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "16-medicum-consulta.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 16-medicum-consulta.png");
});

test("17 - Medicum Historia tab", async ({ page }) => {
  await page.goto(`${BASE_URL}/medicum`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(800);

  // Click Historia tab
  const historiaTab = page.locator("button, [role='tab']").filter({ hasText: /Historia/i }).first();
  if (await historiaTab.isVisible()) {
    await historiaTab.click();
    await page.waitForTimeout(800);
  } else {
    // Try text selector
    await page.getByText("Historia").first().click();
    await page.waitForTimeout(800);
  }

  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "17-medicum-historia.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 17-medicum-historia.png");
});

test("18 - Medicum Codificacion tab", async ({ page }) => {
  await page.goto(`${BASE_URL}/medicum`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(800);

  // Click Codificacion tab
  const codTab = page.locator("button, [role='tab']").filter({ hasText: /Codif/i }).first();
  if (await codTab.isVisible()) {
    await codTab.click();
    await page.waitForTimeout(800);
  } else {
    await page.getByText(/Codif/i).first().click();
    await page.waitForTimeout(800);
  }

  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "18-medicum-codificacion.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 18-medicum-codificacion.png");
});

test("19 - Medicum Visor tab", async ({ page }) => {
  await page.goto(`${BASE_URL}/medicum`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(800);

  // Click Visor tab
  const visorTab = page.locator("button, [role='tab']").filter({ hasText: /Visor/i }).first();
  if (await visorTab.isVisible()) {
    await visorTab.click();
    await page.waitForTimeout(800);
  } else {
    await page.getByText("Visor").first().click();
    await page.waitForTimeout(800);
  }

  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "19-medicum-visor.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 19-medicum-visor.png");
});

// ---- Files Manager ----

test("20 - Files Manager", async ({ page }) => {
  await page.goto(`${BASE_URL}/files`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(800);
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, "20-files-manager.png"),
    fullPage: true,
  });
  console.log("Screenshot saved: 20-files-manager.png");
});

// ---- Sidebar visible on main layout ----

test("21 - Sidebar navigation visible", async ({ page }) => {
  await page.goto(`${BASE_URL}/generation`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(800);
  // Screenshot of the left sidebar area
  const sidebar = page.locator("nav, aside, [class*='sidebar'], [class*='Sidebar']").first();
  if (await sidebar.isVisible()) {
    await sidebar.screenshot({
      path: path.join(SCREENSHOT_DIR, "21-sidebar.png"),
    });
    console.log("Screenshot saved: 21-sidebar.png (sidebar element)");
  } else {
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "21-sidebar-full.png"),
      fullPage: false,
    });
    console.log("Screenshot saved: 21-sidebar-full.png (full viewport)");
  }
});
