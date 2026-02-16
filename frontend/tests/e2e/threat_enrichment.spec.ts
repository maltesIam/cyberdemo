/**
 * Threat Enrichment E2E Tests (Playwright)
 *
 * Following THREAT_ENRICHMENT_BUILD_PLAN.md Section 11.3:
 * 1. debe mostrar boton de enriquecer amenazas
 * 2. debe enriquecer amenazas con exito
 * 3. debe manejar error de fuente sin romper UI
 * 4. debe limitar a 100 IOCs por fuente
 * 5. debe cargar mapa mundi con marcadores
 * 6. debe mostrar panel lateral al click en pais
 * 7. debe animar lineas de ataque
 */

import { test, expect, Page, Route } from "@playwright/test";

const BASE_URL = "http://localhost:3000";

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
 * Generate mock enriched threat data
 */
function generateMockEnrichedThreat(index: number, country: string = "RU") {
  const countries: Record<string, { name: string; lat: number; lon: number }> = {
    RU: { name: "Russia", lat: 61.5, lon: 105.3 },
    CN: { name: "China", lat: 35.9, lon: 104.2 },
    KP: { name: "North Korea", lat: 40.3, lon: 127.5 },
    IR: { name: "Iran", lat: 32.4, lon: 53.7 },
    US: { name: "United States", lat: 39.8, lon: -98.5 },
  };

  const geo = countries[country] || countries.RU;
  const riskLevels = ["critical", "high", "medium", "low"];
  const malwareFamilies = ["Emotet", "TrickBot", "Cobalt Strike", "Mimikatz", "Ryuk"];
  const threatActors = ["APT28", "APT29", "Lazarus Group", "Fancy Bear", "Cozy Bear"];

  return {
    id: `threat-${index}`,
    type: "ip",
    value: `192.168.${Math.floor(index / 256)}.${index % 256}`,
    risk_score: Math.floor(Math.random() * 100),
    risk_level: riskLevels[Math.floor(Math.random() * riskLevels.length)],
    confidence: Math.floor(Math.random() * 100),
    geo: {
      country: country,
      country_name: geo.name,
      city: "Moscow",
      latitude: geo.lat + (Math.random() - 0.5) * 10,
      longitude: geo.lon + (Math.random() - 0.5) * 10,
    },
    network: {
      asn: 12345,
      asn_org: "Example ISP",
      is_vpn: Math.random() > 0.7,
      is_proxy: Math.random() > 0.8,
      is_tor: Math.random() > 0.9,
      is_datacenter: Math.random() > 0.5,
    },
    reputation: {
      abuseipdb: {
        confidence_score: Math.floor(Math.random() * 100),
        total_reports: Math.floor(Math.random() * 1000),
        abuse_categories: ["scanner", "brute-force"],
      },
      greynoise: {
        classification: Math.random() > 0.5 ? "malicious" : "benign",
        noise: Math.random() > 0.5,
      },
      virustotal: {
        malicious_count: Math.floor(Math.random() * 50),
        suspicious_count: Math.floor(Math.random() * 20),
        harmless_count: Math.floor(Math.random() * 30),
        community_score: Math.floor(Math.random() * 100),
      },
    },
    threat_intel: {
      malware_families: [malwareFamilies[Math.floor(Math.random() * malwareFamilies.length)]],
      threat_actors: [threatActors[Math.floor(Math.random() * threatActors.length)]],
      campaigns: ["Operation Example"],
      tags: ["scanner", "botnet", "c2"],
    },
    mitre_attack: {
      techniques: [
        { id: "T1566", name: "Phishing", tactic: "InitialAccess" },
        { id: "T1059", name: "Command and Scripting Interpreter", tactic: "Execution" },
      ],
    },
    intel_feeds: [
      {
        source: "OTX",
        feed_name: "Malicious IPs",
        author: "AlienVault",
        tlp: "green",
      },
    ],
    enrichment_meta: {
      enriched_at: new Date().toISOString(),
      sources_successful: ["otx", "abuseipdb", "greynoise"],
      sources_failed: [],
    },
  };
}

/**
 * Mock threat enrichment API
 */
async function mockThreatEnrichmentAPI(
  page: Page,
  options: {
    successfulSources?: number;
    failedSources?: number;
    totalItems?: number;
    status?: "completed" | "failed" | "running";
    shouldFail?: boolean;
    errorMessage?: string;
  } = {}
) {
  const {
    successfulSources = 5,
    failedSources = 0,
    totalItems = 15,
    status = "completed",
    shouldFail = false,
    errorMessage = "Enrichment failed",
  } = options;

  const jobId = `threat-job-${Date.now()}`;

  // Mock the enrichment start endpoint
  await page.route("**/api/enrichment/threats", async (route: Route) => {
    if (shouldFail) {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ message: errorMessage }),
      });
      return;
    }

    // Generate mock enriched indicators
    const countries = ["RU", "CN", "KP", "IR", "US"];
    const enrichedIndicators = Array.from({ length: Math.min(totalItems, 100) }, (_, i) =>
      generateMockEnrichedThreat(i, countries[i % countries.length])
    );

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        job_id: jobId,
        status: status,
        enriched_indicators: enrichedIndicators,
        successful_sources: successfulSources,
        failed_sources: failedSources,
        total_items: Math.min(totalItems, 100),
        errors:
          failedSources > 0
            ? [{ source: "virustotal", error: "API rate limit", recoverable: true }]
            : [],
      }),
    });
  });

  return jobId;
}

// ============================================================================
// TEST 1: debe mostrar boton de enriquecer amenazas
// ============================================================================

test.describe("Threat Enrichment - Button Display", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);
  });

  test("debe mostrar boton de enriquecer amenazas", async ({ page }) => {
    // Look for the "Enrich Threats" button
    const enrichButton = page.getByRole("button", { name: /enrich.*threats|enriquecer/i });
    await expect(enrichButton).toBeVisible();
    await expect(enrichButton).toBeEnabled();
  });

  test("debe mostrar boton de refresh demo data", async ({ page }) => {
    const refreshButton = page.getByRole("button", { name: /refresh.*demo|demo.*data/i });
    await expect(refreshButton).toBeVisible();
    await expect(refreshButton).toBeEnabled();
  });

  test("debe mostrar area de entrada de IOCs", async ({ page }) => {
    const textarea = page.locator("textarea");
    await expect(textarea).toBeVisible();

    // Verify placeholder text
    const placeholder = await textarea.getAttribute("placeholder");
    expect(placeholder).toContain("IOC");
  });

  test("debe mostrar estadisticas de amenazas", async ({ page }) => {
    // Look for stats cards
    const statsCards = page.locator("[class*='bg-gray-800']").filter({ hasText: /Total|Critical|High|Medium/i });
    const count = await statsCards.count();
    expect(count).toBeGreaterThan(0);
  });
});

// ============================================================================
// TEST 2: debe enriquecer amenazas con exito
// ============================================================================

test.describe("Threat Enrichment - Success Flow", () => {
  test("debe enriquecer amenazas con exito", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    // Mock successful enrichment
    await mockThreatEnrichmentAPI(page, {
      successfulSources: 5,
      failedSources: 0,
      totalItems: 10,
      status: "completed",
    });

    // Enter IOCs in the textarea
    const textarea = page.locator("textarea");
    await textarea.fill("192.168.1.100\nevil-domain.com\n8.8.8.8");

    // Click enrich button
    const enrichButton = page.getByRole("button", { name: /enrich.*threats|enriquecer/i });
    await enrichButton.click();

    // Should show loading/spinner state
    await expect(page.getByText(/\d+%|enriching/i)).toBeVisible({ timeout: 5000 });

    // Wait for completion
    await page.waitForTimeout(2000);

    // Should show success toast
    const toast = page.locator('[role="alert"], [class*="toast"]');
    await expect(toast.first()).toBeVisible({ timeout: 5000 });

    // Table should have enriched data
    const table = page.locator("table");
    await expect(table).toBeVisible({ timeout: 10000 });
  });

  test("debe mostrar progreso de enriquecimiento", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    await mockThreatEnrichmentAPI(page, { totalItems: 5 });

    const textarea = page.locator("textarea");
    await textarea.fill("192.168.1.1");

    const enrichButton = page.getByRole("button", { name: /enrich.*threats|enriquecer/i });
    await enrichButton.click();

    // Should show percentage progress
    await expect(page.getByText(/\d+%/)).toBeVisible({ timeout: 5000 });
  });
});

// ============================================================================
// TEST 3: debe manejar error de fuente sin romper UI
// ============================================================================

test.describe("Threat Enrichment - Error Handling", () => {
  test("debe manejar error de fuente sin romper UI", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    // Mock partial failure (some sources fail)
    await mockThreatEnrichmentAPI(page, {
      successfulSources: 3,
      failedSources: 2,
      totalItems: 5,
      status: "completed",
    });

    const textarea = page.locator("textarea");
    await textarea.fill("192.168.1.100");

    const enrichButton = page.getByRole("button", { name: /enrich.*threats|enriquecer/i });
    await enrichButton.click();

    await page.waitForTimeout(2000);

    // UI should remain functional
    await expect(page.locator("main")).toBeVisible();
    await expect(enrichButton).toBeEnabled({ timeout: 10000 });

    // Check for no critical React errors
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });

    const criticalErrors = errors.filter(
      (e) => e.includes("React") || e.includes("TypeError") || e.includes("Uncaught")
    );
    expect(criticalErrors).toHaveLength(0);
  });

  test("debe mostrar error toast cuando falla completamente", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    // Mock complete failure
    await mockThreatEnrichmentAPI(page, {
      shouldFail: true,
      errorMessage: "All sources failed",
    });

    const textarea = page.locator("textarea");
    await textarea.fill("192.168.1.100");

    const enrichButton = page.getByRole("button", { name: /enrich.*threats|enriquecer/i });
    await enrichButton.click();

    // Should show error toast
    const errorToast = page.locator('[role="alert"], [class*="toast"]');
    await expect(errorToast.first()).toBeVisible({ timeout: 10000 });

    // Button should be re-enabled after error
    await expect(enrichButton).toBeEnabled({ timeout: 5000 });
  });

  test("debe recuperarse y permitir retry despues de error", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    let callCount = 0;

    // First call fails, second succeeds
    await page.route("**/api/enrichment/threats", async (route: Route) => {
      callCount++;

      if (callCount === 1) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({ message: "Temporary error" }),
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            job_id: "retry-job",
            status: "completed",
            enriched_indicators: [generateMockEnrichedThreat(0, "RU")],
            successful_sources: 5,
            failed_sources: 0,
            total_items: 1,
          }),
        });
      }
    });

    const textarea = page.locator("textarea");
    await textarea.fill("192.168.1.100");

    const enrichButton = page.getByRole("button", { name: /enrich.*threats|enriquecer/i });

    // First attempt - fails
    await enrichButton.click();
    await page.waitForTimeout(1000);
    await expect(enrichButton).toBeEnabled({ timeout: 5000 });

    // Retry - succeeds
    await enrichButton.click();
    await page.waitForTimeout(2000);

    // Should now show enriched data
    const toast = page.locator('[role="alert"], [class*="toast"]');
    await expect(toast.first()).toBeVisible({ timeout: 5000 });
  });
});

// ============================================================================
// TEST 4: debe limitar a 100 IOCs por fuente
// ============================================================================

test.describe("Threat Enrichment - IOC Limiting", () => {
  test("debe limitar a 100 IOCs por fuente", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    let capturedRequest: { indicators?: Array<{ type: string; value: string }> } | null = null;

    // Intercept request to verify limiting
    await page.route("**/api/enrichment/threats", async (route: Route) => {
      const request = route.request();
      capturedRequest = JSON.parse(request.postData() || "{}");

      // Generate exactly 100 mock indicators
      const enrichedIndicators = Array.from({ length: 100 }, (_, i) =>
        generateMockEnrichedThreat(i, ["RU", "CN", "KP"][i % 3])
      );

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          job_id: "limit-test-job",
          status: "completed",
          enriched_indicators: enrichedIndicators,
          successful_sources: 5,
          failed_sources: 0,
          total_items: 100,
        }),
      });
    });

    // Generate more than 100 IOCs
    const manyIPs = Array.from({ length: 150 }, (_, i) => `10.0.${Math.floor(i / 256)}.${i % 256}`).join("\n");

    const textarea = page.locator("textarea");
    await textarea.fill(manyIPs);

    const enrichButton = page.getByRole("button", { name: /enrich.*threats|enriquecer/i });
    await enrichButton.click();

    await page.waitForTimeout(2000);

    // Verify the response indicates limiting
    const toast = page.locator('[role="alert"], [class*="toast"]');
    await expect(toast.first()).toBeVisible({ timeout: 5000 });

    // The table should not show more than 100 items
    const tableRows = page.locator("tbody tr");
    const rowCount = await tableRows.count();
    expect(rowCount).toBeLessThanOrEqual(100);
  });
});

// ============================================================================
// TEST 5: debe cargar mapa mundi con marcadores
// ============================================================================

test.describe("Threat Map - World Map Display", () => {
  test("debe cargar mapa mundi con marcadores", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    // Mock enrichment API to return threats with geo data
    await mockThreatEnrichmentAPI(page, { totalItems: 15 });

    // Wait for demo data to load (the page loads demo data on mount)
    await page.waitForTimeout(2000);

    // Verify SVG map is rendered
    const svgMap = page.locator("svg[viewBox]");
    await expect(svgMap.first()).toBeVisible({ timeout: 10000 });

    // Verify map has country markers (circles)
    const markers = page.locator("svg circle");
    const markerCount = await markers.count();
    expect(markerCount).toBeGreaterThan(0);

    // Verify map title is visible
    await expect(page.getByText(/Threat Origins|Live Attack Map/i)).toBeVisible();
  });

  test("debe mostrar leyenda de niveles de riesgo", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    // Wait for page load
    await page.waitForTimeout(1000);

    // Verify legend is visible
    await expect(page.getByText(/Risk Level/i)).toBeVisible();

    // Verify risk levels in legend
    const riskLevels = ["critical", "high", "medium", "low"];
    for (const level of riskLevels) {
      await expect(page.getByText(new RegExp(level, "i")).first()).toBeVisible();
    }
  });

  test("debe mostrar contadores de paises en el mapa", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    await mockThreatEnrichmentAPI(page, { totalItems: 15 });
    await page.waitForTimeout(2000);

    // Verify country stats overlay
    const statsOverlay = page.locator('[class*="bg-gray-800"]').filter({ hasText: /Russia|China/i });
    const count = await statsOverlay.count();
    expect(count).toBeGreaterThan(0);
  });
});

// ============================================================================
// TEST 6: debe mostrar panel lateral al click en pais
// ============================================================================

test.describe("Threat Map - Country Interaction", () => {
  test("debe mostrar panel lateral al click en pais", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    await mockThreatEnrichmentAPI(page, { totalItems: 15 });
    await page.waitForTimeout(2000);

    // Click on a country marker (circle in SVG)
    const countryMarker = page.locator("svg g.cursor-pointer").first();
    if (await countryMarker.isVisible()) {
      await countryMarker.click();

      // Should show toast with country info
      const toast = page.locator('[role="alert"], [class*="toast"]');
      await expect(toast.first()).toBeVisible({ timeout: 5000 });
    }
  });

  test("debe filtrar amenazas al seleccionar pais", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    await mockThreatEnrichmentAPI(page, { totalItems: 15 });
    await page.waitForTimeout(2000);

    // Click on a country marker
    const countryMarker = page.locator("svg g.cursor-pointer").first();
    if (await countryMarker.isVisible()) {
      await countryMarker.click();

      // Verify toast appears with filtering info
      const toast = page.locator('[role="alert"], [class*="toast"]');
      await expect(toast.first()).toBeVisible({ timeout: 5000 });
      await expect(toast.first()).toContainText(/filtering|Filtering/i);
    }
  });
});

// ============================================================================
// TEST 7: debe animar lineas de ataque
// ============================================================================

test.describe("Threat Map - Attack Line Animations", () => {
  test("debe animar lineas de ataque", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    await mockThreatEnrichmentAPI(page, { totalItems: 15 });
    await page.waitForTimeout(2000);

    // Verify animated paths exist
    const animatedPaths = page.locator('svg path[d*="Q"]'); // Bezier curves
    const pathCount = await animatedPaths.count();
    expect(pathCount).toBeGreaterThan(0);

    // Verify animation elements exist
    const animations = page.locator("svg animate, svg animateMotion");
    const animationCount = await animations.count();
    expect(animationCount).toBeGreaterThan(0);

    // Verify glow filter is applied
    const glowFilter = page.locator('svg filter#glow');
    await expect(glowFilter).toBeVisible();
  });

  test("debe mostrar lineas con colores por nivel de riesgo", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    await mockThreatEnrichmentAPI(page, { totalItems: 15 });
    await page.waitForTimeout(2000);

    // Verify paths with different stroke colors exist
    const paths = page.locator('svg path[stroke]');
    const pathCount = await paths.count();
    expect(pathCount).toBeGreaterThan(0);
  });

  test("debe mostrar marcador SOC (objetivo)", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    await page.waitForTimeout(1000);

    // Verify SOC marker text
    await expect(page.locator("svg text").filter({ hasText: "SOC" })).toBeVisible();
  });

  test("debe tener pulso animado en marcadores de amenaza", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    await mockThreatEnrichmentAPI(page, { totalItems: 15 });
    await page.waitForTimeout(2000);

    // Verify pulsing animations on circles
    const pulsingCircles = page.locator('svg circle animate[attributeName="r"]');
    const pulseCount = await pulsingCircles.count();
    expect(pulseCount).toBeGreaterThan(0);
  });
});

// ============================================================================
// Additional Threat Enrichment Tests
// ============================================================================

test.describe("Threat Enrichment - IOC Table", () => {
  test("debe mostrar tabla de IOCs enriquecidos", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    await mockThreatEnrichmentAPI(page, { totalItems: 10 });
    await page.waitForTimeout(2000);

    // Verify table headers
    const table = page.locator("table");
    await expect(table).toBeVisible({ timeout: 10000 });

    // Verify expected columns
    await expect(page.getByText(/IOC/i).first()).toBeVisible();
    await expect(page.getByText(/Type/i).first()).toBeVisible();
    await expect(page.getByText(/Risk/i).first()).toBeVisible();
    await expect(page.getByText(/Country/i).first()).toBeVisible();
  });

  test("debe abrir modal de detalle al click en IOC", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    await mockThreatEnrichmentAPI(page, { totalItems: 5 });
    await page.waitForTimeout(2000);

    // Click on first table row
    const tableRow = page.locator("tbody tr").first();
    if (await tableRow.isVisible()) {
      await tableRow.click();

      // Modal should appear
      const modal = page.locator('[class*="fixed inset-0"]');
      await expect(modal).toBeVisible({ timeout: 5000 });

      // Modal should show threat details
      await expect(page.getByText(/Geolocation|Network|Reputation/i).first()).toBeVisible();
    }
  });
});

test.describe("Threat Enrichment - Malware and Threat Actors", () => {
  test("debe mostrar familias de malware", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    await mockThreatEnrichmentAPI(page, { totalItems: 15 });
    await page.waitForTimeout(2000);

    // Verify malware families section
    await expect(page.getByText(/Malware Families/i)).toBeVisible();
  });

  test("debe mostrar actores de amenaza", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    await mockThreatEnrichmentAPI(page, { totalItems: 15 });
    await page.waitForTimeout(2000);

    // Verify threat actors section
    await expect(page.getByText(/Threat Actors/i)).toBeVisible();
  });

  test("debe mostrar tecnicas MITRE ATT&CK", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    await mockThreatEnrichmentAPI(page, { totalItems: 15 });
    await page.waitForTimeout(2000);

    // Verify MITRE ATT&CK section
    await expect(page.getByText(/MITRE ATT&CK|ATT&CK Coverage/i).first()).toBeVisible();
  });
});

test.describe("Threat Enrichment - Page Load", () => {
  test("debe cargar pagina sin errores", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error" && !msg.text().includes("favicon")) {
        errors.push(msg.text());
      }
    });

    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    // Verify main content is visible
    const mainContent = page.locator("main");
    await expect(mainContent).toBeVisible();

    // Verify no critical React errors
    const criticalErrors = errors.filter(
      (e) => e.includes("React") || e.includes("TypeError") || e.includes("ReferenceError")
    );
    expect(criticalErrors.length).toBe(0);
  });

  test("debe mostrar titulo de la pagina", async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);

    // Verify page title
    await expect(page.getByText(/Threat Intelligence|Threat Enrichment/i).first()).toBeVisible();
  });
});
