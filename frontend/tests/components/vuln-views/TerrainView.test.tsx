/**
 * TerrainView Component Unit Tests
 *
 * TDD tests for the 3D terrain visualization where:
 * - Height = CVSS score
 * - Color = severity level
 * - Fire animation on KEV CVEs
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { TerrainView } from "../../../src/components/vuln-views/TerrainView";
import type { TerrainViewData } from "../../../src/types/vulnerabilityViews";

// Mock data for tests
const mockTerrainData: TerrainViewData = {
  points: [
    {
      cve_id: "CVE-2024-0001",
      cvss_score: 9.8,
      epss_score: 0.95,
      severity: "Critical",
      is_kev: true,
      exploit_count: 5,
      x: 0,
      y: 0,
    },
    {
      cve_id: "CVE-2024-0002",
      cvss_score: 7.5,
      epss_score: 0.6,
      severity: "High",
      is_kev: false,
      exploit_count: 2,
      x: 1,
      y: 0,
    },
    {
      cve_id: "CVE-2024-0003",
      cvss_score: 5.0,
      epss_score: 0.3,
      severity: "Medium",
      is_kev: false,
      exploit_count: 0,
      x: 2,
      y: 0,
    },
    {
      cve_id: "CVE-2024-0004",
      cvss_score: 3.0,
      epss_score: 0.1,
      severity: "Low",
      is_kev: false,
      exploit_count: 0,
      x: 3,
      y: 0,
    },
  ],
  grid_size: 4,
  max_cvss: 10,
  total_cves: 4,
};

describe("TerrainView Component", () => {
  // ============================================================================
  // Rendering Tests
  // ============================================================================
  describe("Rendering", () => {
    it("should render the terrain container", () => {
      render(<TerrainView data={mockTerrainData} />);

      const container = screen.getByTestId("terrain-view");
      expect(container).toBeInTheDocument();
    });

    it("should render terrain peaks for each CVE", () => {
      render(<TerrainView data={mockTerrainData} />);

      const peaks = screen.getAllByTestId(/terrain-peak-/);
      expect(peaks).toHaveLength(4);
    });

    it("should render with custom className", () => {
      render(<TerrainView data={mockTerrainData} className="custom-class" />);

      const container = screen.getByTestId("terrain-view");
      expect(container).toHaveClass("custom-class");
    });

    it("should show loading state when isLoading is true", () => {
      render(<TerrainView data={mockTerrainData} isLoading={true} />);

      expect(screen.getByTestId("terrain-loading")).toBeInTheDocument();
    });

    it("should show error message when error prop is provided", () => {
      render(<TerrainView data={mockTerrainData} error="Failed to load data" />);

      expect(screen.getByText(/failed to load data/i)).toBeInTheDocument();
    });

    it("should show empty state when no data points", () => {
      const emptyData: TerrainViewData = {
        points: [],
        grid_size: 0,
        max_cvss: 0,
        total_cves: 0,
      };

      render(<TerrainView data={emptyData} />);

      expect(screen.getByText(/no vulnerability data/i)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Visual Mapping Tests
  // ============================================================================
  describe("Visual Mapping", () => {
    it("should map CVSS score to peak height", () => {
      render(<TerrainView data={mockTerrainData} />);

      const criticalPeak = screen.getByTestId("terrain-peak-CVE-2024-0001");
      const lowPeak = screen.getByTestId("terrain-peak-CVE-2024-0004");

      // Critical (9.8) should have higher height than Low (3.0)
      const criticalHeight = criticalPeak.style.height || criticalPeak.getAttribute("data-height");
      const lowHeight = lowPeak.style.height || lowPeak.getAttribute("data-height");

      // Parse heights and compare
      expect(parseFloat(criticalHeight ?? "0")).toBeGreaterThan(parseFloat(lowHeight ?? "0"));
    });

    it("should apply correct color for Critical severity", () => {
      render(<TerrainView data={mockTerrainData} />);

      const criticalPeak = screen.getByTestId("terrain-peak-CVE-2024-0001");
      expect(criticalPeak).toHaveAttribute("data-severity", "Critical");
    });

    it("should apply correct color for High severity", () => {
      render(<TerrainView data={mockTerrainData} />);

      const highPeak = screen.getByTestId("terrain-peak-CVE-2024-0002");
      expect(highPeak).toHaveAttribute("data-severity", "High");
    });

    it("should apply correct color for Medium severity", () => {
      render(<TerrainView data={mockTerrainData} />);

      const mediumPeak = screen.getByTestId("terrain-peak-CVE-2024-0003");
      expect(mediumPeak).toHaveAttribute("data-severity", "Medium");
    });

    it("should apply correct color for Low severity", () => {
      render(<TerrainView data={mockTerrainData} />);

      const lowPeak = screen.getByTestId("terrain-peak-CVE-2024-0004");
      expect(lowPeak).toHaveAttribute("data-severity", "Low");
    });
  });

  // ============================================================================
  // KEV Fire Animation Tests
  // ============================================================================
  describe("KEV Fire Animation", () => {
    it("should show fire indicator on KEV CVEs", () => {
      render(<TerrainView data={mockTerrainData} />);

      const kevPeak = screen.getByTestId("terrain-peak-CVE-2024-0001");
      const fireIndicator = kevPeak.querySelector("[data-fire]");

      expect(fireIndicator).toBeInTheDocument();
    });

    it("should not show fire indicator on non-KEV CVEs", () => {
      render(<TerrainView data={mockTerrainData} />);

      const nonKevPeak = screen.getByTestId("terrain-peak-CVE-2024-0002");
      const fireIndicator = nonKevPeak.querySelector("[data-fire]");

      expect(fireIndicator).not.toBeInTheDocument();
    });
  });

  // ============================================================================
  // Interaction Tests
  // ============================================================================
  describe("Interactions", () => {
    it("should call onCVEClick when a peak is clicked", () => {
      const onCVEClick = vi.fn();
      render(<TerrainView data={mockTerrainData} onCVEClick={onCVEClick} />);

      const peak = screen.getByTestId("terrain-peak-CVE-2024-0001");
      fireEvent.click(peak);

      expect(onCVEClick).toHaveBeenCalledWith("CVE-2024-0001");
    });

    it("should show tooltip on hover", () => {
      render(<TerrainView data={mockTerrainData} />);

      const peak = screen.getByTestId("terrain-peak-CVE-2024-0001");
      fireEvent.mouseEnter(peak);

      expect(screen.getByRole("tooltip")).toBeInTheDocument();
      expect(screen.getByText("CVE-2024-0001")).toBeInTheDocument();
      expect(screen.getByText(/cvss: 9.8/i)).toBeInTheDocument();
    });

    it("should hide tooltip on mouse leave", () => {
      render(<TerrainView data={mockTerrainData} />);

      const peak = screen.getByTestId("terrain-peak-CVE-2024-0001");
      fireEvent.mouseEnter(peak);
      fireEvent.mouseLeave(peak);

      expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
    });
  });

  // ============================================================================
  // Accessibility Tests
  // ============================================================================
  describe("Accessibility", () => {
    it("should have appropriate aria labels", () => {
      render(<TerrainView data={mockTerrainData} />);

      const container = screen.getByTestId("terrain-view");
      expect(container).toHaveAttribute("aria-label", expect.stringContaining("vulnerability terrain"));
    });

    it("should have focusable peaks", () => {
      render(<TerrainView data={mockTerrainData} />);

      const peaks = screen.getAllByTestId(/terrain-peak-/);
      peaks.forEach((peak) => {
        // HTML elements render tabIndex as lowercase 'tabindex' in the DOM
        expect(peak).toHaveAttribute("tabindex", "0");
      });
    });

    it("should trigger click on Enter key", () => {
      const onCVEClick = vi.fn();
      render(<TerrainView data={mockTerrainData} onCVEClick={onCVEClick} />);

      const peak = screen.getByTestId("terrain-peak-CVE-2024-0001");
      fireEvent.keyDown(peak, { key: "Enter" });

      expect(onCVEClick).toHaveBeenCalledWith("CVE-2024-0001");
    });
  });
});
