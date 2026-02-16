/**
 * AssetsPage Layer Switch Tests - TDD
 *
 * Tests for the layer toggle feature that shows/hides different data columns
 * based on selected layer: Base, EDR, SIEM, CTEM
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";

// Import the component and layer utilities
import { AssetsPage } from "../src/pages/AssetsPage";
import { LAYER_COLUMNS, type AssetLayer } from "../src/pages/AssetsPage";

// ============================================================================
// Layer Configuration Tests
// ============================================================================

describe("Asset Layer Configuration", () => {
  it("should define Base layer columns", () => {
    expect(LAYER_COLUMNS.base).toBeDefined();
    expect(LAYER_COLUMNS.base).toContain("hostname");
    expect(LAYER_COLUMNS.base).toContain("os");
    expect(LAYER_COLUMNS.base).toContain("owner");
    expect(LAYER_COLUMNS.base).toContain("network");
  });

  it("should define EDR layer columns", () => {
    expect(LAYER_COLUMNS.edr).toBeDefined();
    expect(LAYER_COLUMNS.edr).toContain("detectionCount");
    expect(LAYER_COLUMNS.edr).toContain("lastAlert");
  });

  it("should define SIEM layer columns", () => {
    expect(LAYER_COLUMNS.siem).toBeDefined();
    expect(LAYER_COLUMNS.siem).toContain("incidentCount");
    expect(LAYER_COLUMNS.siem).toContain("severity");
  });

  it("should define CTEM layer columns", () => {
    expect(LAYER_COLUMNS.ctem).toBeDefined();
    expect(LAYER_COLUMNS.ctem).toContain("riskColor");
    expect(LAYER_COLUMNS.ctem).toContain("cveCount");
  });

  it("should have all valid layer types", () => {
    const validLayers: AssetLayer[] = ["base", "edr", "siem", "ctem"];
    validLayers.forEach((layer) => {
      expect(LAYER_COLUMNS[layer]).toBeDefined();
      expect(Array.isArray(LAYER_COLUMNS[layer])).toBe(true);
    });
  });
});

// ============================================================================
// Layer Toggle UI Tests
// ============================================================================

describe("Asset Layer Toggle UI", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    // Mock the API hook responses
    vi.mock("../src/hooks/useApi", () => ({
      useAssets: vi.fn().mockReturnValue({
        data: {
          data: [
            {
              id: "asset-001",
              hostname: "web-server-01",
              ip: "10.0.0.1",
              mac: "00:11:22:33:44:55",
              os: "Linux",
              os_version: "22.04",
              type: "server",
              owner: "John Doe",
              department: "IT",
              site: "NYC",
              risk_score: 75,
              tags: ["production"],
              last_seen: "2024-01-15T10:00:00Z",
              installed_software: [],
              open_ports: [80, 443],
              vulnerabilities: [
                { cve_id: "CVE-2024-001", severity: "high", cvss_score: 7.5, description: "Test" },
              ],
            },
          ],
          total: 1,
          page: 1,
          page_size: 20,
          total_pages: 1,
        },
        isLoading: false,
        error: null,
      }),
      useAsset: vi.fn().mockReturnValue({
        data: null,
        isLoading: false,
        error: null,
      }),
    }));
  });

  const renderAssetsPage = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AssetsPage />
        </BrowserRouter>
      </QueryClientProvider>,
    );
  };

  it("should render layer toggle buttons", () => {
    renderAssetsPage();

    expect(screen.getByRole("button", { name: /base/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /edr/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /siem/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /ctem/i })).toBeInTheDocument();
  });

  it("should have Base layer active by default", () => {
    renderAssetsPage();

    const baseButton = screen.getByRole("button", { name: /base/i });
    expect(baseButton).toHaveClass("bg-cyan-600"); // Active state class
  });

  it("should switch to EDR layer when clicked", () => {
    renderAssetsPage();

    const edrButton = screen.getByRole("button", { name: /edr/i });
    fireEvent.click(edrButton);

    expect(edrButton).toHaveClass("bg-cyan-600");
  });

  it("should switch to SIEM layer when clicked", () => {
    renderAssetsPage();

    const siemButton = screen.getByRole("button", { name: /siem/i });
    fireEvent.click(siemButton);

    expect(siemButton).toHaveClass("bg-cyan-600");
  });

  it("should switch to CTEM layer when clicked", () => {
    renderAssetsPage();

    const ctemButton = screen.getByRole("button", { name: /ctem/i });
    fireEvent.click(ctemButton);

    expect(ctemButton).toHaveClass("bg-cyan-600");
  });

  it("should allow multiple layers to be active simultaneously", () => {
    renderAssetsPage();

    const baseButton = screen.getByRole("button", { name: /base/i });
    const edrButton = screen.getByRole("button", { name: /edr/i });

    // Base is active by default
    expect(baseButton).toHaveClass("bg-cyan-600");

    // Click EDR while holding Ctrl (or just clicking to toggle)
    fireEvent.click(edrButton);

    // Now EDR should also be active
    expect(edrButton).toHaveClass("bg-cyan-600");
  });
});

// ============================================================================
// Column Visibility Tests
// ============================================================================

describe("Asset Column Visibility", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
  });

  const renderAssetsPage = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AssetsPage />
        </BrowserRouter>
      </QueryClientProvider>,
    );
  };

  it("should show Base columns when Base layer is active", () => {
    renderAssetsPage();

    // Base columns should be visible - check table headers specifically
    const headers = screen.getAllByRole("columnheader");
    const headerTexts = headers.map((h) => h.textContent?.toLowerCase() ?? "");

    expect(headerTexts.some((t) => t.includes("hostname"))).toBe(true);
    expect(headerTexts.some((t) => t.includes("owner"))).toBe(true);
  });

  it("should show EDR columns when EDR layer is activated", () => {
    renderAssetsPage();

    const edrButton = screen.getByRole("button", { name: /edr/i });
    fireEvent.click(edrButton);

    // EDR columns should be visible
    const headers = screen.getAllByRole("columnheader");
    const headerTexts = headers.map((h) => h.textContent?.toLowerCase() ?? "");

    expect(headerTexts.some((t) => t.includes("detection count"))).toBe(true);
    expect(headerTexts.some((t) => t.includes("last alert"))).toBe(true);
  });

  it("should show SIEM columns when SIEM layer is activated", () => {
    renderAssetsPage();

    const siemButton = screen.getByRole("button", { name: /siem/i });
    fireEvent.click(siemButton);

    // SIEM columns should be visible
    const headers = screen.getAllByRole("columnheader");
    const headerTexts = headers.map((h) => h.textContent?.toLowerCase() ?? "");

    expect(headerTexts.some((t) => t.includes("incident count"))).toBe(true);
    expect(headerTexts.some((t) => t.includes("severity"))).toBe(true);
  });

  it("should show CTEM columns when CTEM layer is activated", () => {
    renderAssetsPage();

    const ctemButton = screen.getByRole("button", { name: /ctem/i });
    fireEvent.click(ctemButton);

    // CTEM columns should be visible
    const headers = screen.getAllByRole("columnheader");
    const headerTexts = headers.map((h) => h.textContent?.toLowerCase() ?? "");

    expect(headerTexts.some((t) => t.includes("risk"))).toBe(true);
    expect(headerTexts.some((t) => t.includes("cve"))).toBe(true);
  });
});
