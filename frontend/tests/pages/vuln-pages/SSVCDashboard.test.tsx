/**
 * SSVCDashboard Tests - TDD
 *
 * Tests for the SSVC Decision Dashboard
 * - Interactive SSVC decision tree
 * - Glow effects on hover
 * - Click to filter CVEs by decision path
 * - Decision statistics
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { ToastProvider } from "../../../src/utils/toast";
import React from "react";
import { SSVCDashboard } from "../../../src/pages/vuln-pages/SSVCDashboard";

// ============================================================================
// Mock API Module
// ============================================================================

vi.mock("../../../src/services/api", () => ({
  getSSVCDashboard: vi.fn().mockResolvedValue({
    decision_tree: {
      exploitation: {
        active: {
          automatable: { yes: { decision: "Act", count: 5 }, no: { decision: "Act", count: 3 } },
        },
      },
    },
    summary: {
      total_cves: 150,
      act: 8,
      attend: 18,
      track_star: 39,
      track: 85,
    },
    decision_distribution: [
      { decision: "Act", count: 8, percentage: 5.3 },
      { decision: "Attend", count: 18, percentage: 12.0 },
      { decision: "Track*", count: 39, percentage: 26.0 },
      { decision: "Track", count: 85, percentage: 56.7 },
    ],
  }),
  getVulnerabilitySummary: vi.fn().mockResolvedValue({
    total_cves: 150,
    ssvc_act: 8,
    ssvc_attend: 18,
    ssvc_track_star: 39,
    ssvc_track: 85,
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

function renderWithRoute(initialRoute: string = "/vulnerabilities/ssvc") {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <MemoryRouter initialEntries={[initialRoute]}>
          <Routes>
            <Route
              path="/vulnerabilities/ssvc"
              element={<SSVCDashboard />}
            />
          </Routes>
        </MemoryRouter>
      </ToastProvider>
    </QueryClientProvider>
  );
}

// ============================================================================
// SSVCDashboard Tests
// ============================================================================

describe("SSVCDashboard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Page Header", () => {
    it("should display SSVC Dashboard title", async () => {
      renderWithRoute();

      await waitFor(() => {
        const ssvcElements = screen.getAllByText(/SSVC/i);
        expect(ssvcElements.length).toBeGreaterThan(0);
        const decisionElements = screen.getAllByText(/Decision/i);
        expect(decisionElements.length).toBeGreaterThan(0);
      });
    });

    it("should display total CVEs count", async () => {
      renderWithRoute();

      await waitFor(() => {
        const countElements = screen.getAllByText(/150/);
        expect(countElements.length).toBeGreaterThan(0);
      });
    });
  });

  describe("Decision Tree Visualization", () => {
    it("should render decision tree container", async () => {
      renderWithRoute();

      await waitFor(() => {
        expect(screen.getByTestId("ssvc-decision-tree")).toBeInTheDocument();
      });
    });

    it("should display exploitation status nodes", async () => {
      renderWithRoute();

      await waitFor(() => {
        const activeElements = screen.getAllByText(/Active/i);
        expect(activeElements.length).toBeGreaterThan(0);
        expect(screen.getByText(/PoC/i)).toBeInTheDocument();
        expect(screen.getByText(/None/i)).toBeInTheDocument();
      });
    });

    it("should display automatable nodes", async () => {
      renderWithRoute();

      await waitFor(() => {
        const automatableElements = screen.getAllByText(/Automatable/i);
        expect(automatableElements.length).toBeGreaterThan(0);
      });
    });

    it("should display decision outcome nodes", async () => {
      renderWithRoute();

      await waitFor(() => {
        // Decision outcomes are displayed in cards and tree
        const actElements = screen.getAllByText(/Act/i);
        expect(actElements.length).toBeGreaterThan(0);
        const attendElements = screen.getAllByText(/Attend/i);
        expect(attendElements.length).toBeGreaterThan(0);
      });
    });
  });

  describe("Decision Statistics", () => {
    it("should display Act count", async () => {
      renderWithRoute();

      await waitFor(() => {
        // The "8" for Act count should appear - may appear multiple times
        const countElements = screen.getAllByText(/^8$/);
        expect(countElements.length).toBeGreaterThan(0);
      });
    });

    it("should display Attend count", async () => {
      renderWithRoute();

      await waitFor(() => {
        // The "18" for Attend count should appear - may appear multiple times
        const countElements = screen.getAllByText(/^18$/);
        expect(countElements.length).toBeGreaterThan(0);
      });
    });

    it("should display decision percentages", async () => {
      renderWithRoute();

      await waitFor(() => {
        // Should show percentage distribution - use getAllByText since it may appear multiple times
        const percentElements = screen.getAllByText(/5\.3%/i);
        expect(percentElements.length).toBeGreaterThan(0);
      });
    });
  });

  describe("Decision Cards", () => {
    it("should render Act decision card", async () => {
      renderWithRoute();

      await waitFor(() => {
        const actCard = screen.getByTestId("ssvc-card-act");
        expect(actCard).toBeInTheDocument();
      });
    });

    it("should render Attend decision card", async () => {
      renderWithRoute();

      await waitFor(() => {
        const attendCard = screen.getByTestId("ssvc-card-attend");
        expect(attendCard).toBeInTheDocument();
      });
    });

    it("should render Track* decision card", async () => {
      renderWithRoute();

      await waitFor(() => {
        const trackStarCard = screen.getByTestId("ssvc-card-track-star");
        expect(trackStarCard).toBeInTheDocument();
      });
    });

    it("should render Track decision card", async () => {
      renderWithRoute();

      await waitFor(() => {
        const trackCard = screen.getByTestId("ssvc-card-track");
        expect(trackCard).toBeInTheDocument();
      });
    });
  });

  describe("Navigation", () => {
    it("should have breadcrumb navigation", async () => {
      renderWithRoute();

      await waitFor(() => {
        const breadcrumb = screen.getByRole("navigation", { name: /breadcrumb/i });
        expect(breadcrumb).toBeInTheDocument();
      });
    });

    it("should have link back to Vulnerabilities dashboard", async () => {
      renderWithRoute();

      await waitFor(() => {
        const vulnLink = screen.getByRole("link", { name: /vulnerabilities/i });
        expect(vulnLink).toHaveAttribute("href", "/vulnerabilities");
      });
    });
  });

  describe("Decision Description", () => {
    it("should display SSVC framework explanation", async () => {
      renderWithRoute();

      await waitFor(() => {
        // The text includes "prioritization" in the about section
        const ssvcText = screen.getAllByText(/prioritization/i);
        expect(ssvcText.length).toBeGreaterThan(0);
      });
    });
  });
});
