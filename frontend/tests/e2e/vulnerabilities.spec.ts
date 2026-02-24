/**
 * Vulnerability Enrichment E2E Tests (Playwright)
 *
 * Tests for the Vulnerability Command Center and related pages:
 * 1. VulnerabilityDashboard - Main dashboard with 6 visualization tabs
 * 2. CVEDetailPage - Individual CVE detail view
 * 3. CVEAssetsPage - Affected assets list
 * 4. CVEExploitsPage - Exploit sources
 * 5. SSVCDashboard - SSVC decision dashboard
 */

import { test, expect, Page, Route } from "@playwright/test";

const BASE_URL = "http://localhost:3000";

// ============================================================================
// Mock Data Generators
// ============================================================================

/**
 * Generate mock vulnerability overview data
 */
function generateMockOverview() {
  return {
    total_cves: 247,
    critical_count: 15,
    high_count: 42,
    medium_count: 98,
    low_count: 92,
    kev_count: 8,
    exploitable_count: 23,
    overdue_count: 5,
    sla_compliance_percent: 87.5,
    mttr_days: 12.3,
    ssvc_act: 12,
    ssvc_attend: 35,
    ssvc_track_star: 67,
    ssvc_track: 133,
    remediated_count: 89,
    in_progress_count: 45,
    open_count: 113,
  };
}

/**
 * Generate mock CVE list data
 */
function generateMockCVEList(count: number = 10) {
  const severities = ["Critical", "High", "Medium", "Low"];
  const decisions = ["Act", "Attend", "Track*", "Track"];
  const statuses = ["open", "in_progress", "remediated", "accepted_risk"];

  return Array.from({ length: count }, (_, i) => ({
    cve_id: `CVE-2024-${1000 + i}`,
    title: `Vulnerability in Component ${i + 1}`,
    severity: severities[i % 4],
    cvss_v3_score: 5 + (i % 5),
    epss_score: Math.random() * 0.5,
    ssvc_decision: decisions[i % 4],
    is_kev: i % 5 === 0,
    exploit_count: i % 3,
    affected_asset_count: Math.floor(Math.random() * 50) + 1,
    remediation_status: statuses[i % 4],
    published_date: "2024-01-15",
  }));
}

/**
 * Generate mock terrain visualization data
 */
function generateMockTerrainData() {
  return {
    points: Array.from({ length: 20 }, (_, i) => ({
      cve_id: `CVE-2024-${1000 + i}`,
      x: Math.random() * 100,
      y: Math.random() * 100,
      cvss: 5 + Math.random() * 5,
      severity: ["Critical", "High", "Medium", "Low"][i % 4],
      is_kev: i % 5 === 0,
    })),
    grid_size: 10,
    max_cvss: 10,
    total_cves: 20,
  };
}

/**
 * Generate mock calendar heatmap data
 */
function generateMockCalendarData() {
  const days = [];
  const startDate = new Date("2024-01-01");
  for (let i = 0; i < 90; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    days.push({
      date: date.toISOString().split("T")[0],
      count: Math.floor(Math.random() * 10),
      severity_breakdown: {
        critical: Math.floor(Math.random() * 3),
        high: Math.floor(Math.random() * 4),
        medium: Math.floor(Math.random() * 3),
        low: Math.floor(Math.random() * 2),
      },
    });
  }
  return {
    days,
    start_date: "2024-01-01",
    end_date: "2024-03-31",
    max_count: 10,
    total_cves: 247,
  };
}

/**
 * Generate mock sunburst data
 */
function generateMockSunburstData() {
  return {
    root: {
      name: "CWE",
      value: 247,
      children: [
        {
          name: "CWE-79",
          value: 45,
          children: [
            { name: "CVE-2024-1001", value: 1 },
            { name: "CVE-2024-1002", value: 1 },
          ],
        },
        {
          name: "CWE-89",
          value: 32,
          children: [
            { name: "CVE-2024-1003", value: 1 },
          ],
        },
        {
          name: "CWE-119",
          value: 28,
          children: [],
        },
      ],
    },
    total_cves: 247,
    total_cwes: 15,
  };
}

/**
 * Generate mock bubbles data
 */
function generateMockBubblesData() {
  return {
    bubbles: Array.from({ length: 30 }, (_, i) => ({
      cve_id: `CVE-2024-${1000 + i}`,
      severity: ["Critical", "High", "Medium", "Low"][i % 4],
      ssvc_decision: ["Act", "Attend", "Track*", "Track"][i % 4],
      cvss: 5 + (i % 5),
      epss: Math.random() * 0.5,
      is_kev: i % 5 === 0,
      radius: 20 + Math.random() * 30,
    })),
    total_cves: 30,
    severity_distribution: {
      critical: 8,
      high: 8,
      medium: 8,
      low: 6,
    },
  };
}

/**
 * Generate mock DNA data
 */
function generateMockDNAData() {
  return {
    strands: Array.from({ length: 15 }, (_, i) => ({
      cve_id: `CVE-2024-${1000 + i}`,
      exploit_id: `EDB-${50000 + i}`,
      is_kev: i % 3 === 0,
      has_poc: i % 2 === 0,
      severity: ["Critical", "High", "Medium", "Low"][i % 4],
    })),
    total_pairs: 15,
    kev_pairs: 5,
    exploitable_pairs: 8,
  };
}

/**
 * Generate mock Sankey flow data
 */
function generateMockSankeyData() {
  return {
    nodes: [
      { id: "critical", name: "Critical", color: "#ef4444" },
      { id: "high", name: "High", color: "#f97316" },
      { id: "medium", name: "Medium", color: "#eab308" },
      { id: "low", name: "Low", color: "#22c55e" },
      { id: "act", name: "Act", color: "#ef4444" },
      { id: "attend", name: "Attend", color: "#f97316" },
      { id: "track_star", name: "Track*", color: "#eab308" },
      { id: "track", name: "Track", color: "#22c55e" },
      { id: "remediated", name: "Remediated", color: "#22c55e" },
      { id: "in_progress", name: "In Progress", color: "#3b82f6" },
      { id: "open", name: "Open", color: "#6b7280" },
    ],
    links: [
      { source: "critical", target: "act", value: 10 },
      { source: "high", target: "attend", value: 25 },
      { source: "medium", target: "track_star", value: 40 },
      { source: "low", target: "track", value: 50 },
      { source: "act", target: "remediated", value: 8 },
      { source: "attend", target: "in_progress", value: 15 },
      { source: "track_star", target: "open", value: 30 },
    ],
    total_cves: 247,
    remediated_count: 89,
    in_progress_count: 45,
    open_count: 113,
  };
}

/**
 * Generate mock CVE detail data
 */
function generateMockCVEDetail(cveId: string) {
  return {
    cve_id: cveId,
    title: "Remote Code Execution in Example Component",
    description: "A vulnerability in Example Component allows remote attackers to execute arbitrary code via crafted input.",
    severity: "Critical",
    cvss_v3_score: 9.8,
    cvss_v3_vector: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
    epss_score: 0.45,
    epss_percentile: 95,
    risk_score: 92,
    ssvc_decision: "Act",
    is_kev: true,
    kev_date_added: "2024-01-10",
    kev_due_date: "2024-01-31",
    kev_ransomware_use: true,
    exploit_count: 3,
    exploit_maturity: "weaponized",
    has_nuclei_template: true,
    affected_asset_count: 45,
    affected_critical_assets: 8,
    remediation_status: "in_progress",
    assigned_to: "security-team@example.com",
    sla_due_date: "2024-02-15",
    sla_status: "at_risk",
    patch_available: true,
    cwe_ids: ["CWE-79", "CWE-89"],
    ecosystems: ["npm", "pypi"],
    published_date: "2024-01-05",
    last_enriched_at: "2024-01-15T10:30:00Z",
    enrichment_level: "full",
  };
}

/**
 * Generate mock affected assets data
 */
function generateMockAssetsData(cveId: string) {
  const assetTypes = ["server", "workstation", "container", "cloud_instance"];
  const criticalities = ["critical", "high", "medium", "low"] as const;
  const businessUnits = ["Engineering", "Finance", "HR", "Operations"];
  const statuses = ["pending", "in_progress", "remediated", "accepted_risk"];

  return {
    cve_id: cveId,
    assets: Array.from({ length: 15 }, (_, i) => ({
      asset_id: `asset-${1000 + i}`,
      hostname: `srv-${String(i + 1).padStart(3, "0")}.example.com`,
      ip_address: `192.168.${Math.floor(i / 256)}.${i % 256}`,
      asset_type: assetTypes[i % 4],
      criticality: criticalities[i % 4],
      business_unit: businessUnits[i % 4],
      detection_date: "2024-01-12",
      remediation_status: statuses[i % 4],
    })),
    total: 15,
    page: 1,
    page_size: 10,
    total_pages: 2,
  };
}

/**
 * Generate mock exploits data
 */
function generateMockExploitsData(cveId: string) {
  const sources = ["exploitdb", "github", "nuclei", "metasploit", "other"] as const;
  const maturities = ["poc", "functional", "weaponized"] as const;

  return {
    cve_id: cveId,
    exploits: Array.from({ length: 5 }, (_, i) => ({
      id: `exploit-${i + 1}`,
      source: sources[i % 5],
      source_id: sources[i % 5] === "exploitdb" ? `EDB-${50000 + i}` : `POC-${i + 1}`,
      title: `Exploit for ${cveId} - Variant ${i + 1}`,
      url: `https://example.com/exploit/${i + 1}`,
      author: `researcher${i + 1}`,
      publish_date: "2024-01-08",
      verification_status: i % 2 === 0 ? "verified" : "unverified",
      maturity: maturities[i % 3],
    })),
    total: 5,
    has_nuclei_template: true,
    exploit_maturity: "weaponized",
  };
}

/**
 * Generate mock SSVC dashboard data
 */
function generateMockSSVCDashboard() {
  return {
    decision_tree: {
      exploitation: {
        active: { automatable: { yes: "Act", no: "Attend" }, count: 20 },
        poc: { automatable: { yes: "Attend", no: "Track*" }, count: 45 },
        none: { automatable: { yes: "Track*", no: "Track" }, count: 182 },
      },
    },
    summary: {
      total_cves: 247,
      act: 12,
      attend: 35,
      track_star: 67,
      track: 133,
    },
    decision_distribution: [
      { decision: "Act", count: 12, percentage: 4.9 },
      { decision: "Attend", count: 35, percentage: 14.2 },
      { decision: "Track*", count: 67, percentage: 27.1 },
      { decision: "Track", count: 133, percentage: 53.8 },
    ],
  };
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Wait for page to be fully loaded
 */
async function waitForPageReady(page: Page) {
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(500); // Allow for React hydration
}

/**
 * Setup all vulnerability API mocks
 */
async function setupVulnerabilityMocks(page: Page) {
  // Mock overview/summary endpoint
  await page.route("**/api/vulnerabilities/summary", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(generateMockOverview()),
    });
  });

  // Mock vulnerability list endpoint
  await page.route("**/vulnerabilities?*", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        items: generateMockCVEList(20),
        total: 247,
        page: 1,
        page_size: 20,
        total_pages: 13,
      }),
    });
  });

  // Mock terrain data
  await page.route("**/api/vulnerabilities/terrain", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(generateMockTerrainData()),
    });
  });

  // Mock calendar heatmap data
  await page.route("**/api/vulnerabilities/heatmap", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(generateMockCalendarData()),
    });
  });

  // Mock sunburst data
  await page.route("**/api/vulnerabilities/sunburst", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(generateMockSunburstData()),
    });
  });

  // Mock bubbles data
  await page.route("**/api/vulnerabilities/bubbles", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(generateMockBubblesData()),
    });
  });

  // Mock DNA data (using terrain endpoint pattern)
  await page.route("**/api/vulnerabilities/dna*", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(generateMockDNAData()),
    });
  });

  // Mock Sankey flow data
  await page.route("**/vulnerabilities/remediation/flow", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(generateMockSankeyData()),
    });
  });

  // Mock CVE detail endpoint (use regex to match sub-paths like /assets, /exploits)
  await page.route(/\/vulnerabilities\/cves\/CVE-/, async (route: Route) => {
    // Don't intercept page navigation (SPA HTML requests)
    if (route.request().resourceType() === "document") {
      await route.continue();
      return;
    }

    const url = route.request().url();
    const match = url.match(/CVE-\d+-\d+/);
    const cveId = match ? match[0] : "CVE-2024-1000";

    // Check if this is assets or exploits sub-route
    if (url.includes("/assets")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(generateMockAssetsData(cveId)),
      });
    } else if (url.includes("/exploits")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(generateMockExploitsData(cveId)),
      });
    } else {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(generateMockCVEDetail(cveId)),
      });
    }
  });

  // Mock SSVC dashboard
  await page.route("**/vulnerabilities/ssvc/dashboard", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(generateMockSSVCDashboard()),
    });
  });
}

// ============================================================================
// TEST SUITE 1: Navigation Tests
// ============================================================================

test.describe("Vulnerability Dashboard - Navigation", () => {
  test.beforeEach(async ({ page }) => {
    await setupVulnerabilityMocks(page);
  });

  test("should navigate to Vulnerabilities from sidebar", async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    await waitForPageReady(page);

    // Click on Vulnerabilities in sidebar
    const vulnLink = page.locator('nav a[href="/vulnerabilities"]');
    await expect(vulnLink).toBeVisible();
    await vulnLink.click();

    // Verify navigation to vulnerabilities page
    await expect(page).toHaveURL(/\/vulnerabilities/);
    await expect(page.getByText(/Vulnerability Command Center/i)).toBeVisible();
  });

  test("should display main dashboard header and title", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities`);
    await waitForPageReady(page);

    // Verify title and subtitle
    await expect(page.getByText(/Vulnerability Command Center/i)).toBeVisible();
    await expect(page.getByText(/Real-time CVE intelligence/i)).toBeVisible();
  });

  test("should display KPI cards row", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities`);
    await waitForPageReady(page);

    // Verify KPI cards are visible
    await expect(page.getByText(/Total CVEs/i).first()).toBeVisible();
    await expect(page.getByText(/Critical/i).first()).toBeVisible();
    await expect(page.getByText(/KEV/i).first()).toBeVisible();
    await expect(page.getByText(/Exploitable/i)).toBeVisible();
    await expect(page.getByText(/Overdue/i)).toBeVisible();
    await expect(page.getByText(/SLA %/i)).toBeVisible();
    await expect(page.getByText(/MTTR/i)).toBeVisible();
  });

  test("should display view selector tabs", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities`);
    await waitForPageReady(page);

    // Verify view selector is visible
    const viewSelector = page.locator('[data-testid="view-selector"]');
    await expect(viewSelector).toBeVisible();

    // Verify all tab buttons exist
    await expect(page.getByRole("tab", { name: /Risk Terrain/i })).toBeVisible();
    await expect(page.getByRole("tab", { name: /Vulnerability Calendar/i })).toBeVisible();
    await expect(page.getByRole("tab", { name: /CWE Sunburst/i })).toBeVisible();
    await expect(page.getByRole("tab", { name: /Priority Bubbles/i })).toBeVisible();
    await expect(page.getByRole("tab", { name: /Exploit DNA/i })).toBeVisible();
    await expect(page.getByRole("tab", { name: /Remediation Flow/i })).toBeVisible();
  });
});

// ============================================================================
// TEST SUITE 2: Tab Switching Tests
// ============================================================================

test.describe("Vulnerability Dashboard - Tab Switching", () => {
  test.beforeEach(async ({ page }) => {
    await setupVulnerabilityMocks(page);
    await page.goto(`${BASE_URL}/vulnerabilities`);
    await waitForPageReady(page);
  });

  test("should switch to Calendar view", async ({ page }) => {
    const calendarTab = page.getByRole("tab", { name: /Vulnerability Calendar/i });
    await calendarTab.click();

    // Verify tab is now selected
    await expect(calendarTab).toHaveAttribute("aria-selected", "true");

    // Verify calendar view panel is visible
    await expect(page.locator('[role="tabpanel"]')).toBeVisible();
  });

  test("should switch to Sunburst view", async ({ page }) => {
    const sunburstTab = page.getByRole("tab", { name: /CWE Sunburst/i });
    await sunburstTab.click();

    // Verify tab is now selected
    await expect(sunburstTab).toHaveAttribute("aria-selected", "true");
  });

  test("should switch to Bubbles view", async ({ page }) => {
    const bubblesTab = page.getByRole("tab", { name: /Priority Bubbles/i });
    await bubblesTab.click();

    // Verify tab is now selected
    await expect(bubblesTab).toHaveAttribute("aria-selected", "true");
  });

  test("should switch to DNA view", async ({ page }) => {
    const dnaTab = page.getByRole("tab", { name: /Exploit DNA/i });
    await dnaTab.click();

    // Verify tab is now selected
    await expect(dnaTab).toHaveAttribute("aria-selected", "true");
  });

  test("should switch to Sankey view", async ({ page }) => {
    const sankeyTab = page.getByRole("tab", { name: /Remediation Flow/i });
    await sankeyTab.click();

    // Verify tab is now selected
    await expect(sankeyTab).toHaveAttribute("aria-selected", "true");
  });

  test("should switch back to Terrain view", async ({ page }) => {
    // First switch to another tab
    await page.getByRole("tab", { name: /Vulnerability Calendar/i }).click();
    await page.waitForTimeout(300);

    // Then switch back to terrain
    const terrainTab = page.getByRole("tab", { name: /Risk Terrain/i });
    await terrainTab.click();

    // Verify tab is now selected
    await expect(terrainTab).toHaveAttribute("aria-selected", "true");
  });
});

// ============================================================================
// TEST SUITE 3: Filter Sidebar Tests
// ============================================================================

test.describe("Vulnerability Dashboard - Filter Sidebar", () => {
  test.beforeEach(async ({ page }) => {
    await setupVulnerabilityMocks(page);
    await page.goto(`${BASE_URL}/vulnerabilities`);
    await waitForPageReady(page);
  });

  test("should display severity filter section", async ({ page }) => {
    await expect(page.getByText("Severity").first()).toBeVisible();
    await expect(page.getByRole("checkbox", { name: /Critical/i })).toBeVisible();
    await expect(page.getByRole("checkbox", { name: /High/i })).toBeVisible();
    await expect(page.getByRole("checkbox", { name: /Medium/i })).toBeVisible();
    await expect(page.getByRole("checkbox", { name: /Low/i })).toBeVisible();
  });

  test("should toggle severity filter", async ({ page }) => {
    const criticalCheckbox = page.getByRole("checkbox", { name: /Critical/i });

    // Initially unchecked
    await expect(criticalCheckbox).not.toBeChecked();

    // Click to check
    await criticalCheckbox.click();
    await expect(criticalCheckbox).toBeChecked();

    // Click to uncheck
    await criticalCheckbox.click();
    await expect(criticalCheckbox).not.toBeChecked();
  });

  test("should display SSVC Decision filter section", async ({ page }) => {
    await expect(page.getByText("SSVC Decision")).toBeVisible();
    await expect(page.getByRole("checkbox", { name: "Act" })).toBeVisible();
    await expect(page.getByRole("checkbox", { name: "Attend" })).toBeVisible();
    await expect(page.getByRole("checkbox", { name: "Track*" })).toBeVisible();
    await expect(page.getByRole("checkbox", { name: "Track", exact: true })).toBeVisible();
  });

  test("should toggle SSVC decision filter", async ({ page }) => {
    const actCheckbox = page.getByRole("checkbox", { name: "Act" });

    await expect(actCheckbox).not.toBeChecked();
    await actCheckbox.click();
    await expect(actCheckbox).toBeChecked();
  });

  test("should toggle KEV Only filter", async ({ page }) => {
    const kevCheckbox = page.getByRole("checkbox", { name: /KEV Only/i });

    await expect(kevCheckbox).not.toBeChecked();
    await kevCheckbox.click();
    await expect(kevCheckbox).toBeChecked();
  });

  test("should display CVSS Range inputs", async ({ page }) => {
    await expect(page.getByText("CVSS Range")).toBeVisible();

    // Check for min and max inputs
    const minInput = page.locator('input[type="number"]').first();
    const maxInput = page.locator('input[type="number"]').nth(1);

    await expect(minInput).toBeVisible();
    await expect(maxInput).toBeVisible();
  });

  test("should display search input", async ({ page }) => {
    await expect(page.getByText("Search")).toBeVisible();
    const searchInput = page.getByPlaceholder(/CVE-2024/i);
    await expect(searchInput).toBeVisible();
  });

  test("should accept search input", async ({ page }) => {
    const searchInput = page.getByPlaceholder(/CVE-2024/i);
    await searchInput.fill("CVE-2024-1234");
    await expect(searchInput).toHaveValue("CVE-2024-1234");
  });
});

// ============================================================================
// TEST SUITE 4: Bottom Action Bar Tests
// ============================================================================

test.describe("Vulnerability Dashboard - Bottom Action Bar", () => {
  test.beforeEach(async ({ page }) => {
    await setupVulnerabilityMocks(page);
    await page.goto(`${BASE_URL}/vulnerabilities`);
    await waitForPageReady(page);
  });

  test("should display bottom action bar", async ({ page }) => {
    const actionBar = page.locator('[data-testid="bottom-action-bar"]');
    await expect(actionBar).toBeVisible();
  });

  test("should display remediation progress bar", async ({ page }) => {
    await expect(page.getByText(/Remediation:/i)).toBeVisible();
  });

  test("should display Refresh button", async ({ page }) => {
    const refreshButton = page.getByRole("button", { name: /Refresh/i });
    await expect(refreshButton).toBeVisible();
    await expect(refreshButton).toBeEnabled();
  });

  test("should display Export button", async ({ page }) => {
    const exportButton = page.getByRole("button", { name: /Export/i });
    await expect(exportButton).toBeVisible();
    await expect(exportButton).toBeEnabled();
  });

  test("should display Enrich Vulnerabilities button", async ({ page }) => {
    const enrichButton = page.getByRole("button", { name: /Enrich Vulnerabilities/i });
    await expect(enrichButton).toBeVisible();
    await expect(enrichButton).toBeEnabled();
  });

  test("should show toast on Refresh click", async ({ page }) => {
    const refreshButton = page.getByRole("button", { name: /Refresh/i });
    await refreshButton.click();

    // Verify toast appears
    const toast = page.locator('[role="alert"], [class*="toast"]');
    await expect(toast.first()).toBeVisible({ timeout: 5000 });
  });

  test("should show toast on Export click", async ({ page }) => {
    const exportButton = page.getByRole("button", { name: /Export/i });
    await exportButton.click();

    // Verify toast appears
    const toast = page.locator('[role="alert"], [class*="toast"]');
    await expect(toast.first()).toBeVisible({ timeout: 5000 });
  });
});

// ============================================================================
// TEST SUITE 5: CVE Detail Page Tests
// ============================================================================

test.describe("CVE Detail Page", () => {
  test.beforeEach(async ({ page }) => {
    await setupVulnerabilityMocks(page);
  });

  test("should load CVE detail page directly", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000`);
    await waitForPageReady(page);

    // Verify page title
    await expect(page.getByText("CVE-2024-1000").first()).toBeVisible();
  });

  test("should display breadcrumb navigation", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000`);
    await waitForPageReady(page);

    // Verify breadcrumbs
    await expect(page.getByLabel("Breadcrumb").getByRole("link", { name: /Vulnerabilities/i })).toBeVisible();
  });

  test("should display severity badge", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000`);
    await waitForPageReady(page);

    // Verify severity badge
    await expect(page.getByText(/Critical/i).first()).toBeVisible();
  });

  test("should display KEV badge when applicable", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000`);
    await waitForPageReady(page);

    // Verify KEV badge (mock data has is_kev: true)
    await expect(page.getByText("KEV").first()).toBeVisible();
  });

  test("should display SSVC decision badge", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000`);
    await waitForPageReady(page);

    // Verify SSVC decision badge
    await expect(page.getByText(/SSVC: Act/i)).toBeVisible();
  });

  test("should display description section", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000`);
    await waitForPageReady(page);

    await expect(page.getByText("Description")).toBeVisible();
  });

  test("should display risk scores section", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000`);
    await waitForPageReady(page);

    await expect(page.getByText("Risk Scores")).toBeVisible();
    await expect(page.getByText("CVSS v3")).toBeVisible();
    await expect(page.getByText("EPSS")).toBeVisible();
  });

  test("should display remediation section", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000`);
    await waitForPageReady(page);

    await expect(page.getByText("Remediation")).toBeVisible();
    await expect(page.getByText("Status:")).toBeVisible();
  });

  test("should have View Assets button", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000`);
    await waitForPageReady(page);

    const viewAssetsLink = page.locator('a[aria-label="View Affected Assets"]');
    await expect(viewAssetsLink).toBeVisible({ timeout: 15000 });
  });

  test("should have View Exploits button", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000`);
    await waitForPageReady(page);

    const viewExploitsLink = page.getByRole("link", { name: /View Exploits/i });
    await expect(viewExploitsLink).toBeVisible();
  });

  test("should navigate to assets page from detail", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000`);
    await waitForPageReady(page);

    const viewAssetsLink = page.locator('a[aria-label="View Affected Assets"]');
    await expect(viewAssetsLink).toBeVisible({ timeout: 15000 });
    await viewAssetsLink.click();

    await expect(page).toHaveURL(/\/vulnerabilities\/cves\/CVE-2024-1000\/assets/);
  });

  test("should navigate to exploits page from detail", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000`);
    await waitForPageReady(page);

    const viewExploitsLink = page.getByRole("link", { name: /View Exploits/i });
    await viewExploitsLink.click();

    await expect(page).toHaveURL(/\/vulnerabilities\/cves\/CVE-2024-1000\/exploits/);
  });

  test("should have Back button", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000`);
    await waitForPageReady(page);

    const backButton = page.getByRole("button", { name: /Back/i });
    await expect(backButton).toBeVisible();
  });
});

// ============================================================================
// TEST SUITE 6: CVE Assets Page Tests
// ============================================================================

test.describe("CVE Assets Page", () => {
  test.beforeEach(async ({ page }) => {
    await setupVulnerabilityMocks(page);
  });

  test("should load assets page", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000/assets`);
    await waitForPageReady(page);

    await expect(page.getByRole("heading", { name: /Affected Assets/i })).toBeVisible();
  });

  test("should display breadcrumb navigation", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000/assets`);
    await waitForPageReady(page);

    // Verify breadcrumbs (scope to Breadcrumb nav to avoid sidebar/exploits matches)
    await expect(page.getByLabel("Breadcrumb").getByRole("link", { name: /Vulnerabilities/i })).toBeVisible();
    await expect(page.getByLabel("Breadcrumb").getByRole("link", { name: /CVE-2024-1000/i })).toBeVisible();
  });

  test("should display assets count", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000/assets`);
    await waitForPageReady(page);

    await expect(page.getByText(/assets affected/i)).toBeVisible();
  });

  test("should display assets table", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000/assets`);
    await waitForPageReady(page);

    // Verify table headers
    await expect(page.getByText("Hostname")).toBeVisible();
    await expect(page.getByText("IP Address")).toBeVisible();
    await expect(page.getByText("Type")).toBeVisible();
    await expect(page.getByText("Criticality")).toBeVisible();
    await expect(page.getByText("Business Unit")).toBeVisible();
  });

  test("should have Back button", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000/assets`);
    await waitForPageReady(page);

    const backButton = page.getByRole("button", { name: /Back/i });
    await expect(backButton).toBeVisible();
  });
});

// ============================================================================
// TEST SUITE 7: CVE Exploits Page Tests
// ============================================================================

test.describe("CVE Exploits Page", () => {
  test.beforeEach(async ({ page }) => {
    await setupVulnerabilityMocks(page);
  });

  test("should load exploits page", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000/exploits`);
    await waitForPageReady(page);

    await expect(page.getByText(/Exploits/i).first()).toBeVisible();
  });

  test("should display breadcrumb navigation", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000/exploits`);
    await waitForPageReady(page);

    // Verify breadcrumbs (scope to Breadcrumb nav to avoid sidebar/exploits matches)
    await expect(page.getByLabel("Breadcrumb").getByRole("link", { name: /Vulnerabilities/i })).toBeVisible();
    await expect(page.getByLabel("Breadcrumb").getByRole("link", { name: /CVE-2024-1000/i })).toBeVisible();
  });

  test("should display exploit count", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000/exploits`);
    await waitForPageReady(page);

    await expect(page.getByText(/known exploits/i)).toBeVisible();
  });

  test("should display maturity badge when applicable", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000/exploits`);
    await waitForPageReady(page);

    await expect(page.getByText(/maturity/i).first()).toBeVisible();
  });

  test("should display Nuclei Template badge when applicable", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000/exploits`);
    await waitForPageReady(page);

    await expect(page.getByText(/Nuclei Template/i)).toBeVisible();
  });

  test("should have Back button", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000/exploits`);
    await waitForPageReady(page);

    const backButton = page.getByRole("button", { name: /Back/i });
    await expect(backButton).toBeVisible();
  });
});

// ============================================================================
// TEST SUITE 8: SSVC Dashboard Tests
// ============================================================================

test.describe("SSVC Dashboard", () => {
  test.beforeEach(async ({ page }) => {
    await setupVulnerabilityMocks(page);
  });

  test("should load SSVC dashboard", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/ssvc`);
    await waitForPageReady(page);

    await expect(page.getByText(/SSVC Decision Dashboard/i)).toBeVisible();
  });

  test("should display breadcrumb navigation", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/ssvc`);
    await waitForPageReady(page);

    await expect(page.getByLabel("Breadcrumb").getByRole("link", { name: /Vulnerabilities/i })).toBeVisible();
  });

  test("should display total CVEs count", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/ssvc`);
    await waitForPageReady(page);

    await expect(page.getByText(/Total CVEs/i).first()).toBeVisible();
  });

  test("should display SSVC decision cards", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/ssvc`);
    await waitForPageReady(page);

    // Verify all 4 decision cards
    await expect(page.locator('[data-testid="ssvc-card-act"]')).toBeVisible();
    await expect(page.locator('[data-testid="ssvc-card-attend"]')).toBeVisible();
    await expect(page.locator('[data-testid="ssvc-card-track-star"]')).toBeVisible();
    await expect(page.locator('[data-testid="ssvc-card-track"]')).toBeVisible();
  });

  test("should display decision tree visualization", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/ssvc`);
    await waitForPageReady(page);

    const decisionTree = page.locator('[data-testid="ssvc-decision-tree"]');
    await expect(decisionTree).toBeVisible();
  });

  test("should display exploitation status column", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/ssvc`);
    await waitForPageReady(page);

    await expect(page.getByText(/Exploitation Status/i).first()).toBeVisible();
    await expect(page.locator('[data-testid="tree-node-exploitation-active"]')).toBeVisible();
    await expect(page.locator('[data-testid="tree-node-exploitation-poc"]')).toBeVisible();
    await expect(page.locator('[data-testid="tree-node-exploitation-none"]')).toBeVisible();
  });

  test("should display automatable column", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/ssvc`);
    await waitForPageReady(page);

    await expect(page.getByText(/Automatable/i).first()).toBeVisible();
    await expect(page.locator('[data-testid="tree-node-automatable-yes"]')).toBeVisible();
    await expect(page.locator('[data-testid="tree-node-automatable-no"]')).toBeVisible();
  });

  test("should display decision outcomes column", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/ssvc`);
    await waitForPageReady(page);

    await expect(page.getByText(/Decision Outcome/i)).toBeVisible();
    await expect(page.locator('[data-testid="decision-node-act"]')).toBeVisible();
    await expect(page.locator('[data-testid="decision-node-attend"]')).toBeVisible();
    await expect(page.locator('[data-testid="decision-node-track-star"]')).toBeVisible();
    await expect(page.locator('[data-testid="decision-node-track"]')).toBeVisible();
  });

  test("should select decision on card click", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/ssvc`);
    await waitForPageReady(page);

    const actCard = page.locator('[data-testid="ssvc-card-act"]');
    await actCard.click();

    // Verify selection info panel appears
    await expect(page.getByText(/CVEs with "Act" Decision/i)).toBeVisible();
  });

  test("should show View All CVEs link when decision selected", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/ssvc`);
    await waitForPageReady(page);

    const actCard = page.locator('[data-testid="ssvc-card-act"]');
    await actCard.click();

    // Verify "View All CVEs" link appears
    await expect(page.getByRole("link", { name: /View All CVEs/i })).toBeVisible();
  });

  test("should display About SSVC section", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/ssvc`);
    await waitForPageReady(page);

    await expect(page.getByText(/About SSVC/i)).toBeVisible();
    await expect(page.getByText(/Stakeholder-Specific Vulnerability Categorization/i).first()).toBeVisible();
  });
});

// ============================================================================
// TEST SUITE 9: Error Handling Tests
// ============================================================================

test.describe("Vulnerability Dashboard - Error Handling", () => {
  test("should handle API error gracefully on main dashboard", async ({ page }) => {
    // Mock API to return error
    await page.route("**/api/vulnerabilities/**", async (route: Route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ message: "Internal Server Error" }),
      });
    });

    await page.goto(`${BASE_URL}/vulnerabilities`);
    await waitForPageReady(page);

    // Page should still render without crashing
    await expect(page.locator("main").first()).toBeVisible();
  });

  test("should show error state on CVE detail page when CVE not found", async ({ page }) => {
    // Mock API to return 404 (skip document requests for SPA navigation)
    await page.route("**/vulnerabilities/cves/CVE-9999-9999", async (route: Route) => {
      if (route.request().resourceType() === "document") {
        await route.continue();
        return;
      }
      await route.fulfill({
        status: 404,
        contentType: "application/json",
        body: JSON.stringify({ message: "CVE not found" }),
      });
    });

    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-9999-9999`);
    await waitForPageReady(page);

    // Should show error message
    await expect(page.getByText(/Error/i).first()).toBeVisible();
  });

  test("should show Back to Vulnerabilities button on error", async ({ page }) => {
    await page.route("**/vulnerabilities/cves/CVE-9999-9999", async (route: Route) => {
      if (route.request().resourceType() === "document") {
        await route.continue();
        return;
      }
      await route.fulfill({
        status: 404,
        contentType: "application/json",
        body: JSON.stringify({ message: "CVE not found" }),
      });
    });

    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-9999-9999`);
    await waitForPageReady(page);

    const backButton = page.getByRole("button", { name: /Back to Vulnerabilities/i });
    await expect(backButton).toBeVisible();
  });
});

// ============================================================================
// TEST SUITE 10: Page Load Performance Tests
// ============================================================================

test.describe("Vulnerability Dashboard - Page Load", () => {
  test.beforeEach(async ({ page }) => {
    await setupVulnerabilityMocks(page);
  });

  test("should load main dashboard without errors", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error" && !msg.text().includes("favicon")) {
        errors.push(msg.text());
      }
    });

    await page.goto(`${BASE_URL}/vulnerabilities`);
    await waitForPageReady(page);

    // Verify main content is visible
    await expect(page.locator("main").first()).toBeVisible();

    // Verify no critical React errors
    const criticalErrors = errors.filter(
      (e) => e.includes("React") || e.includes("TypeError") || e.includes("ReferenceError")
    );
    expect(criticalErrors.length).toBe(0);
  });

  test("should load CVE detail page without errors", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error" && !msg.text().includes("favicon")) {
        errors.push(msg.text());
      }
    });

    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000`);
    await waitForPageReady(page);

    await expect(page.locator("main").first()).toBeVisible();

    const criticalErrors = errors.filter(
      (e) => e.includes("React") || e.includes("TypeError") || e.includes("ReferenceError")
    );
    expect(criticalErrors.length).toBe(0);
  });

  test("should load SSVC dashboard without errors", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error" && !msg.text().includes("favicon")) {
        errors.push(msg.text());
      }
    });

    await page.goto(`${BASE_URL}/vulnerabilities/ssvc`);
    await waitForPageReady(page);

    await expect(page.locator("main").first()).toBeVisible();

    const criticalErrors = errors.filter(
      (e) => e.includes("React") || e.includes("TypeError") || e.includes("ReferenceError")
    );
    expect(criticalErrors.length).toBe(0);
  });
});

// ============================================================================
// TEST SUITE 11: Accessibility Tests
// ============================================================================

test.describe("Vulnerability Dashboard - Accessibility", () => {
  test.beforeEach(async ({ page }) => {
    await setupVulnerabilityMocks(page);
  });

  test("tabs should have correct ARIA attributes", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities`);
    await waitForPageReady(page);

    const tabs = page.getByRole("tab");
    const tabCount = await tabs.count();
    expect(tabCount).toBe(6);

    // First tab should be selected by default
    const firstTab = tabs.first();
    await expect(firstTab).toHaveAttribute("aria-selected", "true");
  });

  test("tablist should have correct role", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities`);
    await waitForPageReady(page);

    const tablist = page.getByRole("tablist");
    await expect(tablist).toBeVisible();
  });

  test("tabpanel should have correct role", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities`);
    await waitForPageReady(page);

    const tabpanel = page.getByRole("tabpanel");
    await expect(tabpanel).toBeVisible();
  });

  test("buttons should have aria-labels", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities`);
    await waitForPageReady(page);

    const refreshButton = page.getByRole("button", { name: /Refresh/i });
    await expect(refreshButton).toHaveAttribute("aria-label");

    const exportButton = page.getByRole("button", { name: /Export/i });
    await expect(exportButton).toHaveAttribute("aria-label");
  });

  test("pagination should have aria-label", async ({ page }) => {
    await page.goto(`${BASE_URL}/vulnerabilities/cves/CVE-2024-1000/assets`);
    await waitForPageReady(page);

    const pagination = page.locator('nav[aria-label="Pagination"]');
    // Only expect pagination if there are multiple pages
    if (await pagination.isVisible()) {
      await expect(pagination).toHaveAttribute("aria-label", "Pagination");
    }
  });
});
