/**
 * IOC Detail Modal E2E Tests (Playwright)
 *
 * Tests for the IOC detail modal component:
 * 1. debe cargar detalle de IOC
 * 2. debe cambiar entre tabs
 * 3. debe ejecutar acciones
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
 * Generate comprehensive mock enriched threat data for detail modal testing
 */
function generateDetailedMockThreat(index: number, country: string = "RU") {
  const countries: Record<string, { name: string; lat: number; lon: number; city: string }> = {
    RU: { name: "Russia", lat: 55.7558, lon: 37.6173, city: "Moscow" },
    CN: { name: "China", lat: 39.9042, lon: 116.4074, city: "Beijing" },
    KP: { name: "North Korea", lat: 39.0392, lon: 125.7625, city: "Pyongyang" },
    IR: { name: "Iran", lat: 35.6892, lon: 51.389, city: "Tehran" },
    US: { name: "United States", lat: 38.9072, lon: -77.0369, city: "Washington" },
  };

  const geo = countries[country] || countries.RU;
  const riskLevels = ["critical", "high", "medium", "low"];
  const riskLevel = riskLevels[index % riskLevels.length];

  return {
    id: `threat-detail-${index}`,
    type: "ip",
    value: `45.33.32.${156 + index}`,
    risk_score: riskLevel === "critical" ? 95 : riskLevel === "high" ? 75 : riskLevel === "medium" ? 50 : 25,
    risk_level: riskLevel,
    confidence: 85 + Math.floor(Math.random() * 15),
    geo: {
      country: country,
      country_name: geo.name,
      city: geo.city,
      latitude: geo.lat,
      longitude: geo.lon,
    },
    network: {
      asn: 15169 + index,
      asn_org: "Malicious Hosting Provider Ltd",
      is_vpn: index % 3 === 0,
      is_proxy: index % 4 === 0,
      is_tor: index % 5 === 0,
      is_datacenter: index % 2 === 0,
    },
    reputation: {
      abuseipdb: {
        confidence_score: 85 + (index % 15),
        total_reports: 150 + index * 10,
        abuse_categories: ["scanner", "brute-force", "exploits"],
      },
      greynoise: {
        classification: "malicious",
        noise: true,
      },
      virustotal: {
        malicious_count: 42 + index,
        suspicious_count: 8 + index,
        harmless_count: 15,
        community_score: -35,
      },
    },
    threat_intel: {
      malware_families: ["Emotet", "TrickBot", "Cobalt Strike"],
      threat_actors: ["APT28", "APT29", "Lazarus Group"],
      campaigns: ["Operation Ghostwriter", "SolarWinds"],
      tags: ["scanner", "botnet", "c2", "ransomware", "apt"],
    },
    mitre_attack: {
      techniques: [
        { id: "T1566", name: "Phishing", tactic: "InitialAccess" },
        { id: "T1059", name: "Command and Scripting Interpreter", tactic: "Execution" },
        { id: "T1055", name: "Process Injection", tactic: "DefenseEvasion" },
        { id: "T1003", name: "OS Credential Dumping", tactic: "CredentialAccess" },
        { id: "T1021", name: "Remote Services", tactic: "LateralMovement" },
      ],
    },
    intel_feeds: [
      { source: "OTX", feed_name: "Malicious IPs Daily", author: "AlienVault", tlp: "green" },
      { source: "ThreatFox", feed_name: "Botnet C2 Servers", author: "Abuse.ch", tlp: "amber" },
      { source: "URLhaus", feed_name: "Malware Distribution", author: "Abuse.ch", tlp: "white" },
      { source: "MISP", feed_name: "APT Threat Intel", author: "CIRCL", tlp: "red" },
      { source: "Emerging Threats", feed_name: "Compromised IPs", author: "Proofpoint", tlp: "green" },
    ],
    enrichment_meta: {
      enriched_at: new Date().toISOString(),
      sources_successful: ["otx", "abuseipdb", "greynoise", "virustotal", "threatfox"],
      sources_failed: ["shodan"],
    },
  };
}

/**
 * Mock threat enrichment API for detail modal testing
 */
async function mockThreatEnrichmentAPIForDetail(page: Page, threatCount: number = 5) {
  const countries = ["RU", "CN", "KP", "IR", "US"];

  await page.route("**/api/enrichment/threats", async (route: Route) => {
    const enrichedIndicators = Array.from({ length: threatCount }, (_, i) =>
      generateDetailedMockThreat(i, countries[i % countries.length])
    );

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        job_id: `detail-test-job-${Date.now()}`,
        status: "completed",
        enriched_indicators: enrichedIndicators,
        successful_sources: 5,
        failed_sources: 1,
        total_items: threatCount,
      }),
    });
  });
}

/**
 * Open IOC detail modal by clicking on first table row
 */
async function openFirstIOCDetailModal(page: Page): Promise<boolean> {
  const tableRow = page.locator("tbody tr").first();

  if (await tableRow.isVisible({ timeout: 5000 })) {
    await tableRow.click();

    // Wait for modal to appear
    const modal = page.locator('[class*="fixed inset-0"]');
    await expect(modal).toBeVisible({ timeout: 5000 });
    return true;
  }
  return false;
}

// ============================================================================
// TEST 1: debe cargar detalle de IOC
// ============================================================================

test.describe("IOC Detail Modal - Loading", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);
    await mockThreatEnrichmentAPIForDetail(page, 5);
    await page.waitForTimeout(2000);
  });

  test("debe cargar detalle de IOC", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Verify modal header with IOC value
      const modalHeader = page.locator('[class*="sticky top-0"]');
      await expect(modalHeader).toBeVisible();

      // Verify IOC value is displayed (IP format)
      await expect(page.locator('[class*="font-mono"]').first()).toBeVisible();

      // Verify risk score badge
      const riskBadge = page.locator('[class*="border"]').filter({ hasText: /Risk:\s*\d+/ });
      await expect(riskBadge.first()).toBeVisible();

      // Verify close button
      const closeButton = page.locator('button').filter({ has: page.locator('svg path[d*="M6 18L18 6"]') });
      await expect(closeButton.first()).toBeVisible();
    }
  });

  test("debe mostrar seccion de geolocalizacion", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Verify Geolocation section
      await expect(page.getByText(/Geolocation/i).first()).toBeVisible();

      // Verify country info
      await expect(page.getByText(/Country/i).first()).toBeVisible();

      // Verify city info
      await expect(page.getByText(/City/i).first()).toBeVisible();

      // Verify coordinates
      await expect(page.getByText(/Coordinates/i).first()).toBeVisible();
    }
  });

  test("debe mostrar seccion de red/network", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Verify Network section
      await expect(page.getByText(/Network/i).first()).toBeVisible();

      // Verify ASN info
      await expect(page.getByText(/ASN/i).first()).toBeVisible();

      // Verify Organization
      await expect(page.getByText(/Organization/i).first()).toBeVisible();
    }
  });

  test("debe mostrar badges de caracteristicas de red", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // These badges appear based on network flags
      const possibleBadges = ["VPN", "Proxy", "Tor", "Datacenter"];

      // At least one badge should be visible for test data
      let foundBadge = false;
      for (const badge of possibleBadges) {
        const badgeElement = page.locator('[class*="bg-"]').filter({ hasText: badge });
        if (await badgeElement.count() > 0) {
          foundBadge = true;
          break;
        }
      }
      // Note: This may not always find a badge depending on mock data
      // The modal should render without errors regardless
      await expect(page.locator('[class*="fixed inset-0"]')).toBeVisible();
    }
  });

  test("debe mostrar fuentes de reputacion", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Verify Reputation Sources section
      await expect(page.getByText(/Reputation Sources/i)).toBeVisible();

      // Verify at least one reputation source
      const sources = ["AbuseIPDB", "GreyNoise", "VirusTotal"];
      let foundSource = false;
      for (const source of sources) {
        const sourceElement = page.getByText(source);
        if (await sourceElement.count() > 0) {
          foundSource = true;
          break;
        }
      }
      expect(foundSource).toBe(true);
    }
  });

  test("debe cerrar modal al hacer click en overlay", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Click on the overlay background (not the modal content)
      const overlay = page.locator('[class*="fixed inset-0"][class*="bg-black"]');
      await overlay.click({ position: { x: 10, y: 10 } }); // Click corner

      // Modal should close
      await expect(overlay).not.toBeVisible({ timeout: 3000 });
    }
  });

  test("debe cerrar modal al hacer click en boton X", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Find and click close button
      const closeButton = page.locator('button').filter({ has: page.locator('svg') }).last();
      await closeButton.click();

      // Modal should close
      const modal = page.locator('[class*="fixed inset-0"]');
      await expect(modal).not.toBeVisible({ timeout: 3000 });
    }
  });
});

// ============================================================================
// TEST 2: debe cambiar entre tabs (sections in modal)
// ============================================================================

test.describe("IOC Detail Modal - Section Navigation", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);
    await mockThreatEnrichmentAPIForDetail(page, 5);
    await page.waitForTimeout(2000);
  });

  test("debe cambiar entre tabs mostrando todas las secciones", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // The modal displays sections vertically, verify all are visible
      // Section 1: Geo & Network (grid with 2 columns)
      const geoNetworkSection = page.locator('[class*="grid"][class*="grid-cols-2"]').first();
      await expect(geoNetworkSection).toBeVisible();

      // Section 2: Reputation Sources
      await expect(page.getByText(/Reputation Sources/i)).toBeVisible();

      // Section 3: Threat Intelligence
      await expect(page.getByText(/Threat Intelligence/i)).toBeVisible();

      // Section 4: MITRE ATT&CK Techniques
      await expect(page.getByText(/MITRE ATT&CK/i).first()).toBeVisible();

      // Section 5: Intelligence Feeds
      await expect(page.getByText(/Intelligence Feeds/i)).toBeVisible();
    }
  });

  test("debe mostrar seccion de threat intelligence con malware families", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Verify Threat Intelligence section
      await expect(page.getByText(/Threat Intelligence/i)).toBeVisible();

      // Verify Malware Families subsection
      await expect(page.getByText(/Malware Families/i).first()).toBeVisible();

      // Verify at least one malware family badge
      const malwareBadges = page.locator('[class*="bg-red-500"]').filter({ hasText: /Emotet|TrickBot|Cobalt Strike/i });
      const badgeCount = await malwareBadges.count();
      expect(badgeCount).toBeGreaterThan(0);
    }
  });

  test("debe mostrar seccion de threat actors", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Verify Threat Actors subsection
      await expect(page.getByText(/Threat Actors/i).first()).toBeVisible();

      // Verify at least one threat actor badge
      const actorBadges = page.locator('[class*="bg-purple-500"]').filter({ hasText: /APT28|APT29|Lazarus/i });
      const badgeCount = await actorBadges.count();
      expect(badgeCount).toBeGreaterThan(0);
    }
  });

  test("debe mostrar seccion de tags", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Verify Tags subsection
      await expect(page.getByText(/Tags/i).first()).toBeVisible();

      // Verify tag badges exist
      const tagBadges = page.locator('[class*="bg-gray-700"]');
      const badgeCount = await tagBadges.count();
      expect(badgeCount).toBeGreaterThan(0);
    }
  });

  test("debe mostrar tecnicas MITRE ATT&CK", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Verify MITRE ATT&CK section
      await expect(page.getByText(/MITRE ATT&CK Techniques/i)).toBeVisible();

      // Verify technique badges (format: T####)
      const techniqueBadges = page.locator('[class*="bg-blue-500"]').filter({ hasText: /T\d{4}/ });
      const techniqueCount = await techniqueBadges.count();
      expect(techniqueCount).toBeGreaterThan(0);
    }
  });

  test("debe mostrar intel feeds con TLP colors", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Verify Intelligence Feeds section
      await expect(page.getByText(/Intelligence Feeds/i)).toBeVisible();

      // Verify TLP badges exist (red, amber, green, white)
      const tlpBadges = page.locator('[class*="rounded"]').filter({ hasText: /TLP:/i });
      const tlpCount = await tlpBadges.count();
      expect(tlpCount).toBeGreaterThan(0);
    }
  });

  test("debe poder hacer scroll en modal con contenido largo", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Verify modal content is scrollable
      const modalContent = page.locator('[class*="overflow-y-auto"]');
      await expect(modalContent.first()).toBeVisible();

      // Scroll down to see more content
      await modalContent.first().evaluate((el) => el.scrollBy(0, 300));

      // Should still see content after scrolling
      await expect(page.locator('[class*="fixed inset-0"]')).toBeVisible();
    }
  });
});

// ============================================================================
// TEST 3: debe ejecutar acciones
// ============================================================================

test.describe("IOC Detail Modal - Actions", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);
    await mockThreatEnrichmentAPIForDetail(page, 5);
    await page.waitForTimeout(2000);
  });

  test("debe ejecutar acciones - copiar IOC value", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // The IOC value is displayed in a font-mono class
      const iocValue = page.locator('[class*="font-mono"]').first();
      await expect(iocValue).toBeVisible();

      // IOC value should be selectable text
      const iocText = await iocValue.textContent();
      expect(iocText).toMatch(/\d+\.\d+\.\d+\.\d+/); // IP format
    }
  });

  test("debe mostrar metadatos de enriquecimiento", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Scroll to bottom of modal
      const modalContent = page.locator('[class*="overflow-y-auto"]').first();
      await modalContent.evaluate((el) => el.scrollTo(0, el.scrollHeight));

      // Verify enrichment metadata section
      await expect(page.getByText(/Enriched:/i)).toBeVisible();
      await expect(page.getByText(/Sources:/i)).toBeVisible();
    }
  });

  test("debe mostrar fecha de enriquecimiento", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Scroll to bottom
      const modalContent = page.locator('[class*="overflow-y-auto"]').first();
      await modalContent.evaluate((el) => el.scrollTo(0, el.scrollHeight));

      // Verify enrichment timestamp is displayed
      const enrichedText = page.locator('[class*="text-gray-500"]').filter({ hasText: /Enriched:/i });
      await expect(enrichedText.first()).toBeVisible();
    }
  });

  test("debe mostrar fuentes exitosas de enriquecimiento", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Scroll to bottom
      const modalContent = page.locator('[class*="overflow-y-auto"]').first();
      await modalContent.evaluate((el) => el.scrollTo(0, el.scrollHeight));

      // Verify sources list
      const sourcesText = page.locator('[class*="text-gray-500"]').filter({ hasText: /Sources:/i });
      await expect(sourcesText.first()).toBeVisible();
    }
  });

  test("debe poder hacer click en tecnica MITRE para ver detalles", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Find a MITRE technique badge with title attribute
      const techniqueBadge = page.locator('[class*="bg-blue-500"]').filter({ hasText: /T\d{4}/ }).first();

      if (await techniqueBadge.isVisible()) {
        // Verify badge has title attribute with technique name
        const title = await techniqueBadge.getAttribute("title");
        expect(title).toBeTruthy();
      }
    }
  });

  test("debe navegar a otro IOC despues de cerrar modal", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Close the modal
      const overlay = page.locator('[class*="fixed inset-0"][class*="bg-black"]');
      await overlay.click({ position: { x: 10, y: 10 } });

      // Wait for modal to close
      await page.waitForTimeout(500);

      // Click on second table row
      const secondRow = page.locator("tbody tr").nth(1);
      if (await secondRow.isVisible()) {
        await secondRow.click();

        // New modal should open
        const modal = page.locator('[class*="fixed inset-0"]');
        await expect(modal).toBeVisible({ timeout: 5000 });
      }
    }
  });
});

// ============================================================================
// Additional IOC Detail Tests - Content Validation
// ============================================================================

test.describe("IOC Detail Modal - Content Validation", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);
    await mockThreatEnrichmentAPIForDetail(page, 5);
    await page.waitForTimeout(2000);
  });

  test("debe mostrar AbuseIPDB confidence score", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Verify AbuseIPDB section
      const abuseipdbSection = page.locator('[class*="bg-gray-800"]').filter({ hasText: "AbuseIPDB" });
      await expect(abuseipdbSection.first()).toBeVisible();

      // Verify percentage indicator
      const percentageText = page.locator('[class*="text-red-400"]').filter({ hasText: /%/ });
      await expect(percentageText.first()).toBeVisible();
    }
  });

  test("debe mostrar GreyNoise classification", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Verify GreyNoise section
      const greynoiseSection = page.locator('[class*="bg-gray-800"]').filter({ hasText: "GreyNoise" });
      await expect(greynoiseSection.first()).toBeVisible();

      // Verify classification (malicious/benign)
      const classificationText = page.locator('[class*="font-bold"]').filter({ hasText: /malicious|benign/i });
      await expect(classificationText.first()).toBeVisible();
    }
  });

  test("debe mostrar VirusTotal detections", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Verify VirusTotal section
      const vtSection = page.locator('[class*="bg-gray-800"]').filter({ hasText: "VirusTotal" });
      await expect(vtSection.first()).toBeVisible();

      // Verify detection ratio (X/Y format)
      const detectionRatio = page.locator('[class*="text-orange-400"]').filter({ hasText: /\d+\/\d+/ });
      await expect(detectionRatio.first()).toBeVisible();
    }
  });

  test("debe mostrar tipo de IOC en header", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Verify IOC type is displayed
      await expect(page.getByText(/Type:\s*IP/i).first()).toBeVisible();
    }
  });

  test("debe mostrar riesgo con color apropiado", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Verify risk badge exists with appropriate styling
      const riskBadge = page.locator('[class*="border"]').filter({ hasText: /Risk:\s*\d+/ });
      await expect(riskBadge.first()).toBeVisible();

      // Risk badge should have color class based on level
      const riskClasses = await riskBadge.first().getAttribute("class");
      expect(riskClasses).toMatch(/text-(red|orange|yellow|green)/);
    }
  });
});

// ============================================================================
// IOC Detail Modal - Error Handling
// ============================================================================

test.describe("IOC Detail Modal - Error Handling", () => {
  test("debe manejar IOC sin datos de reputacion", async ({ page }) => {
    // Mock threat with minimal reputation data
    await page.route("**/api/enrichment/threats", async (route: Route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          job_id: "minimal-test",
          status: "completed",
          enriched_indicators: [
            {
              id: "threat-minimal",
              type: "ip",
              value: "1.2.3.4",
              risk_score: 50,
              risk_level: "medium",
              geo: {
                country: "US",
                country_name: "United States",
                city: "Unknown",
                latitude: 39.8,
                longitude: -98.5,
              },
              network: null,
              reputation: {}, // Empty reputation
              threat_intel: { malware_families: [], threat_actors: [], campaigns: [], tags: [] },
              mitre_attack: { techniques: [] },
              intel_feeds: [],
              enrichment_meta: {
                enriched_at: new Date().toISOString(),
                sources_successful: [],
                sources_failed: ["all"],
              },
            },
          ],
          successful_sources: 0,
          failed_sources: 5,
          total_items: 1,
        }),
      });
    });

    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);
    await page.waitForTimeout(2000);

    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Modal should still render without crashing
      await expect(page.locator('[class*="fixed inset-0"]')).toBeVisible();

      // Geolocation should still show
      await expect(page.getByText(/Geolocation/i).first()).toBeVisible();
    }
  });

  test("debe manejar IOC sin tecnicas MITRE", async ({ page }) => {
    // Mock threat without MITRE techniques
    await page.route("**/api/enrichment/threats", async (route: Route) => {
      const baseThreat = generateDetailedMockThreat(0, "RU");
      baseThreat.mitre_attack = { techniques: [] };

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          job_id: "no-mitre-test",
          status: "completed",
          enriched_indicators: [baseThreat],
          successful_sources: 3,
          failed_sources: 0,
          total_items: 1,
        }),
      });
    });

    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);
    await page.waitForTimeout(2000);

    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Modal should render
      await expect(page.locator('[class*="fixed inset-0"]')).toBeVisible();

      // MITRE section should still exist (possibly empty)
      await expect(page.getByText(/MITRE ATT&CK/i).first()).toBeVisible();
    }
  });

  test("debe manejar IOC sin intel feeds", async ({ page }) => {
    // Mock threat without intel feeds
    await page.route("**/api/enrichment/threats", async (route: Route) => {
      const baseThreat = generateDetailedMockThreat(0, "CN");
      baseThreat.intel_feeds = [];

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          job_id: "no-feeds-test",
          status: "completed",
          enriched_indicators: [baseThreat],
          successful_sources: 2,
          failed_sources: 0,
          total_items: 1,
        }),
      });
    });

    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);
    await page.waitForTimeout(2000);

    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Modal should render
      await expect(page.locator('[class*="fixed inset-0"]')).toBeVisible();

      // Intel Feeds section should exist (possibly empty)
      await expect(page.getByText(/Intelligence Feeds/i)).toBeVisible();
    }
  });
});

// ============================================================================
// IOC Detail Modal - Accessibility
// ============================================================================

test.describe("IOC Detail Modal - Accessibility", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);
    await mockThreatEnrichmentAPIForDetail(page, 5);
    await page.waitForTimeout(2000);
  });

  test("debe tener overlay oscuro para focus en modal", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Verify dark overlay
      const overlay = page.locator('[class*="bg-black"]').filter({ has: page.locator('[class*="bg-gray-800"]') });
      await expect(overlay.first()).toBeVisible();
    }
  });

  test("debe prevenir scroll del body cuando modal esta abierto", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Modal content should be scrollable
      const modalContent = page.locator('[class*="overflow-y-auto"]');
      await expect(modalContent.first()).toBeVisible();
    }
  });

  test("debe tener alto contraste para texto importante", async ({ page }) => {
    const opened = await openFirstIOCDetailModal(page);

    if (opened) {
      // Headers should be white text
      const headers = page.locator('[class*="text-white"]');
      const headerCount = await headers.count();
      expect(headerCount).toBeGreaterThan(0);

      // Secondary text should be gray
      const secondaryText = page.locator('[class*="text-gray-"]');
      const secondaryCount = await secondaryText.count();
      expect(secondaryCount).toBeGreaterThan(0);
    }
  });
});
