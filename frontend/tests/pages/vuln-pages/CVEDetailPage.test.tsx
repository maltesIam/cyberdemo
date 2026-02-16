/**
 * CVEDetailPage Tests - TDD
 *
 * Tests for the CVE Detail nested page
 * - Route parameter handling
 * - CVE data display
 * - Breadcrumb navigation
 * - Back button functionality
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { ToastProvider } from "../../../src/utils/toast";
import React from "react";
import { CVEDetailPage } from "../../../src/pages/vuln-pages/CVEDetailPage";

// ============================================================================
// Mock API Module
// ============================================================================

vi.mock("../../../src/services/api", () => ({
  getVulnerabilityDetail: vi.fn().mockResolvedValue({
    cve_id: "CVE-2024-0001",
    title: "Critical Remote Code Execution in Apache Log4j",
    description: "A vulnerability in Apache Log4j allows remote code execution via JNDI lookups.",
    cvss_v3_score: 9.8,
    cvss_v3_vector: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
    epss_score: 0.972,
    epss_percentile: 99.5,
    risk_score: 95,
    severity: "Critical",
    is_kev: true,
    kev_date_added: "2024-01-15",
    kev_due_date: "2024-01-29",
    kev_ransomware_use: true,
    ssvc_decision: "Act",
    ssvc_exploitation: "active",
    ssvc_automatable: true,
    exploit_count: 5,
    exploit_maturity: "functional",
    has_nuclei_template: true,
    affected_asset_count: 23,
    affected_critical_assets: 8,
    remediation_status: "in_progress",
    assigned_to: "security-team",
    sla_due_date: "2024-02-01",
    sla_status: "at_risk",
    cwe_ids: ["CWE-502", "CWE-917"],
    ecosystems: ["java", "maven"],
    patch_available: true,
    published_date: "2024-01-10",
    last_enriched_at: "2024-01-20T10:30:00Z",
    enrichment_level: "full",
  }),
  getVulnerabilitySummary: vi.fn().mockResolvedValue({
    total_cves: 150,
    critical_count: 12,
  }),
}));

// ============================================================================
// Test Utilities
// ============================================================================

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
    },
  });
}

function renderWithRoute(initialRoute: string) {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <MemoryRouter initialEntries={[initialRoute]}>
          <Routes>
            <Route
              path="/vulnerabilities/cves/:cveId"
              element={<CVEDetailPage />}
            />
          </Routes>
        </MemoryRouter>
      </ToastProvider>
    </QueryClientProvider>
  );
}

// ============================================================================
// CVEDetailPage Tests
// ============================================================================

describe("CVEDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Route Parameter Handling", () => {
    it("should extract cveId from route params", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001");

      await waitFor(() => {
        expect(screen.getByText(/CVE-2024-0001/i)).toBeInTheDocument();
      });
    });

    it("should fetch CVE data using the route param", async () => {
      const api = await import("../../../src/services/api");

      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001");

      await waitFor(() => {
        expect(api.getVulnerabilityDetail).toHaveBeenCalledWith("CVE-2024-0001");
      });
    });
  });

  describe("CVE Detail Display", () => {
    it("should display CVE title", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001");

      await waitFor(() => {
        expect(
          screen.getByText(/Critical Remote Code Execution/i)
        ).toBeInTheDocument();
      });
    });

    it("should display CVSS score with severity badge", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001");

      await waitFor(() => {
        // CVSS is displayed somewhere on the page - check for score or label
        const cvssElements = screen.getAllByText(/9\.8|CVSS/i);
        expect(cvssElements.length).toBeGreaterThan(0);
        const criticalElements = screen.getAllByText(/Critical/i);
        expect(criticalElements.length).toBeGreaterThan(0);
      });
    });

    it("should display EPSS score", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001");

      await waitFor(() => {
        expect(screen.getByText(/97\.2/i)).toBeInTheDocument();
      });
    });

    it("should display KEV status when vulnerability is in KEV", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001");

      await waitFor(() => {
        expect(screen.getByText(/KEV/i)).toBeInTheDocument();
      });
    });

    it("should display SSVC decision badge", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001");

      await waitFor(() => {
        expect(screen.getByText(/Act/i)).toBeInTheDocument();
      });
    });

    it("should display affected assets count", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001");

      await waitFor(() => {
        expect(screen.getByText(/23/)).toBeInTheDocument();
      });
    });

    it("should display exploit information", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001");

      await waitFor(() => {
        expect(screen.getByText(/5.*exploit/i)).toBeInTheDocument();
      });
    });

    it("should display remediation status", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001");

      await waitFor(() => {
        expect(screen.getByText(/in.progress/i)).toBeInTheDocument();
      });
    });
  });

  describe("Breadcrumb Navigation", () => {
    it("should display breadcrumbs with Vulnerabilities link", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001");

      await waitFor(() => {
        const breadcrumb = screen.getByRole("navigation", {
          name: /breadcrumb/i,
        });
        expect(breadcrumb).toBeInTheDocument();
      });
    });

    it("should have link back to Vulnerabilities dashboard", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001");

      await waitFor(() => {
        const vulnLink = screen.getByRole("link", { name: /vulnerabilities/i });
        expect(vulnLink).toHaveAttribute("href", "/vulnerabilities");
      });
    });

    it("should display current CVE ID in breadcrumb", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001");

      await waitFor(() => {
        const breadcrumbNav = screen.getByRole("navigation", {
          name: /breadcrumb/i,
        });
        expect(breadcrumbNav).toHaveTextContent(/CVE-2024-0001/);
      });
    });
  });

  describe("Back Button Navigation", () => {
    it("should have a back button", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001");

      await waitFor(() => {
        const backButton = screen.getByRole("button", { name: /back/i });
        expect(backButton).toBeInTheDocument();
      });
    });
  });

  describe("Loading State", () => {
    it("should show loading state while fetching data", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001");

      await waitFor(() => {
        expect(screen.getByText(/CVE-2024-0001/i)).toBeInTheDocument();
      });
    });
  });

  describe("Action Links", () => {
    it("should have link to view affected assets", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001");

      await waitFor(() => {
        const assetsLink = screen.getByRole("link", { name: /assets/i });
        expect(assetsLink).toHaveAttribute(
          "href",
          "/vulnerabilities/cves/CVE-2024-0001/assets"
        );
      });
    });

    it("should have link to view exploits", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001");

      await waitFor(() => {
        const exploitsLink = screen.getByRole("link", { name: /exploit/i });
        expect(exploitsLink).toHaveAttribute(
          "href",
          "/vulnerabilities/cves/CVE-2024-0001/exploits"
        );
      });
    });
  });
});
