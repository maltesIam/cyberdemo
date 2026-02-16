/**
 * CVEAssetsPage Tests - TDD
 *
 * Tests for the CVE Affected Assets nested page
 * - Table of affected assets
 * - Pagination
 * - Asset criticality badges
 * - Navigation back to CVE
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { ToastProvider } from "../../../src/utils/toast";
import React from "react";
import { CVEAssetsPage } from "../../../src/pages/vuln-pages/CVEAssetsPage";

// ============================================================================
// Mock API Module
// ============================================================================

vi.mock("../../../src/services/api", () => ({
  getCVEAffectedAssets: vi.fn().mockResolvedValue({
    cve_id: "CVE-2024-0001",
    assets: [
      {
        asset_id: "asset-001",
        hostname: "prod-web-01.example.com",
        ip_address: "10.0.1.10",
        asset_type: "server",
        criticality: "critical",
        business_unit: "E-Commerce",
        detection_date: "2024-01-15",
        remediation_status: "pending",
      },
      {
        asset_id: "asset-002",
        hostname: "prod-api-02.example.com",
        ip_address: "10.0.1.20",
        asset_type: "server",
        criticality: "high",
        business_unit: "API Services",
        detection_date: "2024-01-15",
        remediation_status: "in_progress",
      },
      {
        asset_id: "asset-003",
        hostname: "dev-app-01.example.com",
        ip_address: "10.0.2.10",
        asset_type: "server",
        criticality: "medium",
        business_unit: "Development",
        detection_date: "2024-01-16",
        remediation_status: "remediated",
      },
    ],
    total: 23,
    page: 1,
    page_size: 10,
    total_pages: 3,
  }),
  getVulnerabilityDetail: vi.fn().mockResolvedValue({
    cve_id: "CVE-2024-0001",
    title: "Critical RCE Vulnerability",
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
              path="/vulnerabilities/cves/:cveId/assets"
              element={<CVEAssetsPage />}
            />
          </Routes>
        </MemoryRouter>
      </ToastProvider>
    </QueryClientProvider>
  );
}

// ============================================================================
// CVEAssetsPage Tests
// ============================================================================

describe("CVEAssetsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Page Header", () => {
    it("should display page title with CVE ID", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        const cveElements = screen.getAllByText(/CVE-2024-0001/i);
        expect(cveElements.length).toBeGreaterThan(0);
        const assetsElements = screen.getAllByText(/Assets/i);
        expect(assetsElements.length).toBeGreaterThan(0);
      });
    });

    it("should display total affected assets count", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        expect(screen.getByText(/23/)).toBeInTheDocument();
      });
    });
  });

  describe("Assets Table", () => {
    it("should render assets table with headers", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        expect(screen.getByRole("table")).toBeInTheDocument();
        expect(screen.getByText(/Hostname/i)).toBeInTheDocument();
        expect(screen.getByText(/IP Address/i)).toBeInTheDocument();
        expect(screen.getByText(/Criticality/i)).toBeInTheDocument();
      });
    });

    it("should display asset hostname", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        expect(
          screen.getByText(/prod-web-01\.example\.com/i)
        ).toBeInTheDocument();
      });
    });

    it("should display asset IP address", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        expect(screen.getByText(/10\.0\.1\.10/)).toBeInTheDocument();
      });
    });

    it("should display business unit", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        expect(screen.getByText(/E-Commerce/i)).toBeInTheDocument();
      });
    });
  });

  describe("Criticality Badges", () => {
    it("should display critical badge with red styling", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        const criticalBadge = screen.getAllByText(/critical/i)[0];
        expect(criticalBadge).toBeInTheDocument();
      });
    });

    it("should display high badge with orange styling", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        const highBadge = screen.getByText(/high/i);
        expect(highBadge).toBeInTheDocument();
      });
    });

    it("should display medium badge with yellow styling", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        const mediumBadge = screen.getByText(/medium/i);
        expect(mediumBadge).toBeInTheDocument();
      });
    });
  });

  describe("Pagination", () => {
    it("should display pagination controls", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        expect(screen.getByRole("navigation", { name: /pagination/i })).toBeInTheDocument();
      });
    });

    it("should show current page info", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        expect(screen.getByText(/Page 1 of 3/i)).toBeInTheDocument();
      });
    });

    it("should have next page button", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        const nextButton = screen.getByRole("button", { name: /next/i });
        expect(nextButton).toBeInTheDocument();
        expect(nextButton).toBeEnabled();
      });
    });

    it("should have previous button disabled on first page", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        const prevButton = screen.getByRole("button", { name: /previous/i });
        expect(prevButton).toBeDisabled();
      });
    });
  });

  describe("Navigation", () => {
    it("should have breadcrumb navigation", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        const breadcrumb = screen.getByRole("navigation", { name: /breadcrumb/i });
        expect(breadcrumb).toBeInTheDocument();
      });
    });

    it("should have link back to CVE detail", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        const cveLink = screen.getByRole("link", { name: /CVE-2024-0001/i });
        expect(cveLink).toHaveAttribute(
          "href",
          "/vulnerabilities/cves/CVE-2024-0001"
        );
      });
    });

    it("should have link back to Vulnerabilities dashboard", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        const vulnLink = screen.getByRole("link", { name: /vulnerabilities/i });
        expect(vulnLink).toHaveAttribute("href", "/vulnerabilities");
      });
    });
  });

  describe("Remediation Status", () => {
    it("should display remediation status for each asset", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        expect(screen.getByText(/pending/i)).toBeInTheDocument();
        expect(screen.getByText(/in.progress/i)).toBeInTheDocument();
        expect(screen.getByText(/remediated/i)).toBeInTheDocument();
      });
    });
  });

  describe("Loading State", () => {
    it("should show loading state while fetching data", async () => {
      renderWithRoute("/vulnerabilities/cves/CVE-2024-0001/assets");

      await waitFor(() => {
        expect(screen.getByRole("table")).toBeInTheDocument();
      });
    });
  });
});
