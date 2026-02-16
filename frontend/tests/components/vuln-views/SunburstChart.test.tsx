/**
 * SunburstChart Component Unit Tests
 *
 * TDD tests for the hierarchical CWE visualization in a sunburst/radial format
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { SunburstChart } from "../../../src/components/vuln-views/SunburstChart";
import type { SunburstChartData } from "../../../src/types/vulnerabilityViews";

// Mock data for tests
const mockSunburstData: SunburstChartData = {
  root: {
    name: "All CWEs",
    value: 100,
    children: [
      {
        name: "Injection",
        value: 40,
        cwe_id: "CWE-74",
        severity_counts: { critical: 15, high: 15, medium: 8, low: 2 },
        children: [
          {
            name: "SQL Injection",
            value: 25,
            cwe_id: "CWE-89",
            severity_counts: { critical: 10, high: 10, medium: 5, low: 0 },
          },
          {
            name: "Command Injection",
            value: 15,
            cwe_id: "CWE-78",
            severity_counts: { critical: 5, high: 5, medium: 3, low: 2 },
          },
        ],
      },
      {
        name: "Authentication",
        value: 30,
        cwe_id: "CWE-287",
        severity_counts: { critical: 8, high: 12, medium: 7, low: 3 },
      },
      {
        name: "Memory",
        value: 30,
        cwe_id: "CWE-119",
        severity_counts: { critical: 10, high: 8, medium: 7, low: 5 },
      },
    ],
  },
  total_cves: 100,
  total_cwes: 5,
};

describe("SunburstChart Component", () => {
  // ============================================================================
  // Rendering Tests
  // ============================================================================
  describe("Rendering", () => {
    it("should render the sunburst container", () => {
      render(<SunburstChart data={mockSunburstData} />);

      const container = screen.getByTestId("sunburst-chart");
      expect(container).toBeInTheDocument();
    });

    it("should render SVG element for the chart", () => {
      render(<SunburstChart data={mockSunburstData} />);

      const svg = screen.getByTestId("sunburst-svg");
      expect(svg).toBeInTheDocument();
      expect(svg.tagName.toLowerCase()).toBe("svg");
    });

    it("should render arc segments for each CWE category", () => {
      render(<SunburstChart data={mockSunburstData} />);

      // Should have arcs for root's children and their children
      const arcs = screen.getAllByTestId(/sunburst-arc-/);
      expect(arcs.length).toBeGreaterThanOrEqual(3); // At least 3 top-level categories
    });

    it("should render with custom className", () => {
      render(<SunburstChart data={mockSunburstData} className="custom-class" />);

      const container = screen.getByTestId("sunburst-chart");
      expect(container).toHaveClass("custom-class");
    });

    it("should show loading state when isLoading is true", () => {
      render(<SunburstChart data={mockSunburstData} isLoading={true} />);

      expect(screen.getByTestId("sunburst-loading")).toBeInTheDocument();
    });

    it("should show error message when error prop is provided", () => {
      render(<SunburstChart data={mockSunburstData} error="Failed to load data" />);

      expect(screen.getByText(/failed to load data/i)).toBeInTheDocument();
    });

    it("should show empty state when no CWE data", () => {
      const emptyData: SunburstChartData = {
        root: { name: "Empty", value: 0 },
        total_cves: 0,
        total_cwes: 0,
      };

      render(<SunburstChart data={emptyData} />);

      expect(screen.getByText(/no cwe data/i)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Visual Mapping Tests
  // ============================================================================
  describe("Visual Mapping", () => {
    it("should size arcs proportionally to value", () => {
      render(<SunburstChart data={mockSunburstData} />);

      // Injection (40%) should be larger than Authentication (30%)
      const injectionArc = screen.getByTestId("sunburst-arc-CWE-74");
      const authArc = screen.getByTestId("sunburst-arc-CWE-287");

      // Check that arc data reflects proportion
      expect(injectionArc).toHaveAttribute("data-value", "40");
      expect(authArc).toHaveAttribute("data-value", "30");
    });

    it("should render nested children in inner rings", () => {
      render(<SunburstChart data={mockSunburstData} />);

      // SQL Injection should be in a nested ring
      const sqlArc = screen.getByTestId("sunburst-arc-CWE-89");
      expect(sqlArc).toHaveAttribute("data-depth", "2");
    });

    it("should apply severity-based coloring", () => {
      render(<SunburstChart data={mockSunburstData} />);

      const injectionArc = screen.getByTestId("sunburst-arc-CWE-74");
      // Should have color based on dominant severity (critical/high)
      expect(injectionArc).toHaveAttribute("data-dominant-severity");
    });
  });

  // ============================================================================
  // Center Display Tests
  // ============================================================================
  describe("Center Display", () => {
    it("should show total CVE count in center", () => {
      render(<SunburstChart data={mockSunburstData} />);

      expect(screen.getByTestId("sunburst-center")).toBeInTheDocument();
      // Use getAllByText since count appears in both center and stats
      expect(screen.getAllByText("100").length).toBeGreaterThanOrEqual(1);
    });

    it("should update center display when hovering on arc", () => {
      render(<SunburstChart data={mockSunburstData} />);

      const injectionArc = screen.getByTestId("sunburst-arc-CWE-74");
      fireEvent.mouseEnter(injectionArc);

      // 40 appears in center display when hovering
      expect(screen.getAllByText("40").length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/injection/i).length).toBeGreaterThanOrEqual(1);
    });
  });

  // ============================================================================
  // Interaction Tests
  // ============================================================================
  describe("Interactions", () => {
    it("should call onCWEClick when an arc is clicked", () => {
      const onCWEClick = vi.fn();
      render(<SunburstChart data={mockSunburstData} onCWEClick={onCWEClick} />);

      const arc = screen.getByTestId("sunburst-arc-CWE-89");
      fireEvent.click(arc);

      expect(onCWEClick).toHaveBeenCalledWith("CWE-89");
    });

    it("should zoom into category on double click", () => {
      render(<SunburstChart data={mockSunburstData} />);

      const injectionArc = screen.getByTestId("sunburst-arc-CWE-74");
      fireEvent.doubleClick(injectionArc);

      // After zoom, children should be more prominent
      const sqlArc = screen.getByTestId("sunburst-arc-CWE-89");
      expect(sqlArc).toHaveAttribute("data-zoomed", "true");
    });

    it("should reset zoom when clicking center", () => {
      render(<SunburstChart data={mockSunburstData} />);

      // First zoom in
      const injectionArc = screen.getByTestId("sunburst-arc-CWE-74");
      fireEvent.doubleClick(injectionArc);

      // Then click center to reset
      const center = screen.getByTestId("sunburst-center");
      fireEvent.click(center);

      // All arcs should be visible again
      const arcs = screen.getAllByTestId(/sunburst-arc-/);
      expect(arcs.length).toBeGreaterThanOrEqual(3);
    });

    it("should show tooltip on arc hover", () => {
      render(<SunburstChart data={mockSunburstData} />);

      const arc = screen.getByTestId("sunburst-arc-CWE-89");
      fireEvent.mouseEnter(arc);

      expect(screen.getByRole("tooltip")).toBeInTheDocument();
      expect(screen.getByText(/sql injection/i)).toBeInTheDocument();
      expect(screen.getByText(/25 cves/i)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Breadcrumb Tests
  // ============================================================================
  describe("Breadcrumb", () => {
    it("should show breadcrumb trail when zoomed", () => {
      render(<SunburstChart data={mockSunburstData} />);

      const injectionArc = screen.getByTestId("sunburst-arc-CWE-74");
      fireEvent.doubleClick(injectionArc);

      expect(screen.getByTestId("sunburst-breadcrumb")).toBeInTheDocument();
      expect(screen.getAllByText(/all cwes/i).length).toBeGreaterThanOrEqual(1);
      // "Injection" appears in both breadcrumb and center display
      expect(screen.getAllByText(/injection/i).length).toBeGreaterThanOrEqual(1);
    });
  });

  // ============================================================================
  // Accessibility Tests
  // ============================================================================
  describe("Accessibility", () => {
    it("should have appropriate aria labels", () => {
      render(<SunburstChart data={mockSunburstData} />);

      const container = screen.getByTestId("sunburst-chart");
      expect(container).toHaveAttribute("aria-label", expect.stringContaining("CWE"));
    });

    it("should have focusable arcs", () => {
      render(<SunburstChart data={mockSunburstData} />);

      const arcs = screen.getAllByTestId(/sunburst-arc-/);
      arcs.forEach((arc) => {
        // SVG elements render tabIndex as lowercase 'tabindex' in the DOM
        expect(arc).toHaveAttribute("tabindex", "0");
      });
    });

    it("should support keyboard navigation", () => {
      const onCWEClick = vi.fn();
      render(<SunburstChart data={mockSunburstData} onCWEClick={onCWEClick} />);

      const arc = screen.getByTestId("sunburst-arc-CWE-89");
      fireEvent.keyDown(arc, { key: "Enter" });

      expect(onCWEClick).toHaveBeenCalledWith("CWE-89");
    });
  });
});
