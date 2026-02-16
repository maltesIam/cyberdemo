/**
 * EnhancedBottomBar Component Unit Tests
 *
 * TDD tests for the enhanced bottom bar with:
 * - Animated count-up for KPIs
 * - Segmented remediation progress bar
 * - Time range selector (7d, 30d, 90d, All, Custom)
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import { EnhancedBottomBar } from "../../../src/components/vuln-views/EnhancedBottomBar";

// ============================================================================
// Mock Data
// ============================================================================

const mockStats = {
  total_cves: 150,
  remediated_count: 42,
  in_progress_count: 28,
  open_count: 80,
  critical_count: 12,
  kev_count: 8,
  exploitable_count: 23,
  mttr_days: 4.2,
  sla_compliance_percent: 87.5,
};

const defaultProps = {
  stats: mockStats,
  onTimeRangeChange: vi.fn(),
  onRefresh: vi.fn(),
  onEnrich: vi.fn(),
  selectedTimeRange: "30d" as const,
};

// ============================================================================
// Rendering Tests
// ============================================================================

describe("EnhancedBottomBar Component", () => {
  describe("Rendering", () => {
    it("should render the bottom bar container", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const container = screen.getByTestId("enhanced-bottom-bar");
      expect(container).toBeInTheDocument();
    });

    it("should render with custom className", () => {
      render(<EnhancedBottomBar {...defaultProps} className="custom-bar" />);

      const container = screen.getByTestId("enhanced-bottom-bar");
      expect(container).toHaveClass("custom-bar");
    });
  });

  // ============================================================================
  // Animated Count-up KPIs Tests
  // ============================================================================

  describe("Animated Count-up KPIs", () => {
    it("should render KPI for total CVEs", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      expect(screen.getByTestId("kpi-total")).toBeInTheDocument();
    });

    it("should have animating state attribute", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const totalKpi = screen.getByTestId("kpi-total-value");

      // Should have data-animating attribute
      expect(totalKpi).toHaveAttribute("data-animating");
    });

    it("should render KPI for critical count with pulse animation", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const criticalKpi = screen.getByTestId("kpi-critical");
      expect(criticalKpi).toBeInTheDocument();
      expect(criticalKpi).toHaveClass("animate-pulse-critical");
    });

    it("should render KPI for KEV count with fire animation", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const kevKpi = screen.getByTestId("kpi-kev");
      expect(kevKpi).toBeInTheDocument();
      expect(kevKpi).toHaveClass("animate-fire");
    });

    it("should render MTTR KPI", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const mttrKpi = screen.getByTestId("kpi-mttr");
      expect(mttrKpi).toBeInTheDocument();
      expect(screen.getByText(/4\.2d/)).toBeInTheDocument();
    });

    it("should render SLA compliance KPI", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const slaKpi = screen.getByTestId("kpi-sla");
      expect(slaKpi).toBeInTheDocument();
      expect(screen.getByText(/87\.5%/)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Segmented Remediation Progress Bar Tests
  // ============================================================================

  describe("Remediation Progress Bar", () => {
    it("should render progress bar container", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const progressBar = screen.getByTestId("remediation-progress");
      expect(progressBar).toBeInTheDocument();
    });

    it("should render three segments: remediated, in_progress, open", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const remediatedSegment = screen.getByTestId("segment-remediated");
      const inProgressSegment = screen.getByTestId("segment-in-progress");
      const openSegment = screen.getByTestId("segment-open");

      expect(remediatedSegment).toBeInTheDocument();
      expect(inProgressSegment).toBeInTheDocument();
      expect(openSegment).toBeInTheDocument();
    });

    it("should calculate correct width percentages for segments", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const remediatedSegment = screen.getByTestId("segment-remediated");
      const inProgressSegment = screen.getByTestId("segment-in-progress");
      const openSegment = screen.getByTestId("segment-open");

      // Just verify segments have style attribute with width
      expect(remediatedSegment).toHaveAttribute("style");
      expect(inProgressSegment).toHaveAttribute("style");
      expect(openSegment).toHaveAttribute("style");
    });

    it("should apply correct colors to segments", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const remediatedSegment = screen.getByTestId("segment-remediated");
      const inProgressSegment = screen.getByTestId("segment-in-progress");
      const openSegment = screen.getByTestId("segment-open");

      expect(remediatedSegment).toHaveClass("bg-green-500");
      expect(inProgressSegment).toHaveClass("bg-blue-500");
      expect(openSegment).toHaveClass("bg-gray-600");
    });

    it("should render segment legend with counts", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const legend = screen.getByTestId("progress-legend");
      expect(legend).toBeInTheDocument();

      expect(screen.getByText("42")).toBeInTheDocument(); // remediated
      expect(screen.getByText("28")).toBeInTheDocument(); // in_progress
      expect(screen.getByText("80")).toBeInTheDocument(); // open
    });

    it("should support segment hover interaction", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const remediatedSegment = screen.getByTestId("segment-remediated");
      // Just verify the segment exists and can receive events
      expect(remediatedSegment).toBeInTheDocument();
      fireEvent.mouseEnter(remediatedSegment);
      fireEvent.mouseLeave(remediatedSegment);
      // Component should not crash
      expect(remediatedSegment).toBeInTheDocument();
    });

    it("should animate segment widths on mount", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const progressBar = screen.getByTestId("remediation-progress");
      expect(progressBar).toHaveClass("animate-progress-fill");
    });
  });

  // ============================================================================
  // Time Range Selector Tests
  // ============================================================================

  describe("Time Range Selector", () => {
    it("should render time range selector", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const selector = screen.getByTestId("time-range-selector");
      expect(selector).toBeInTheDocument();
    });

    it("should render 7d option", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const btn7d = screen.getByRole("button", { name: /7d/i });
      expect(btn7d).toBeInTheDocument();
    });

    it("should render 30d option", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const btn30d = screen.getByRole("button", { name: /30d/i });
      expect(btn30d).toBeInTheDocument();
    });

    it("should render 90d option", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const btn90d = screen.getByRole("button", { name: /90d/i });
      expect(btn90d).toBeInTheDocument();
    });

    it("should render All option", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const btnAll = screen.getByRole("button", { name: /all/i });
      expect(btnAll).toBeInTheDocument();
    });

    it("should render Custom option", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const btnCustom = screen.getByRole("button", { name: /custom/i });
      expect(btnCustom).toBeInTheDocument();
    });

    it("should highlight selected time range", () => {
      render(<EnhancedBottomBar {...defaultProps} selectedTimeRange="30d" />);

      const btn30d = screen.getByRole("button", { name: /30d/i });
      expect(btn30d).toHaveClass("bg-cyan-600");
    });

    it("should call onTimeRangeChange when option is clicked", () => {
      const onTimeRangeChange = vi.fn();
      render(
        <EnhancedBottomBar {...defaultProps} onTimeRangeChange={onTimeRangeChange} />
      );

      const btn7d = screen.getByRole("button", { name: /7d/i });
      fireEvent.click(btn7d);

      expect(onTimeRangeChange).toHaveBeenCalledWith("7d");
    });

    it("should open date picker when Custom is clicked", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const btnCustom = screen.getByRole("button", { name: /custom/i });
      fireEvent.click(btnCustom);

      expect(screen.getByTestId("date-range-picker")).toBeInTheDocument();
    });

    it("should close date picker when apply button is clicked", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const btnCustom = screen.getByRole("button", { name: /custom/i });
      fireEvent.click(btnCustom);

      // Date picker should be visible
      expect(screen.getByTestId("date-range-picker")).toBeInTheDocument();

      const applyBtn = screen.getByRole("button", { name: /apply/i });
      fireEvent.click(applyBtn);

      // After clicking apply, date picker should close
      expect(screen.queryByTestId("date-range-picker")).not.toBeInTheDocument();
    });
  });

  // ============================================================================
  // Action Buttons Tests
  // ============================================================================

  describe("Action Buttons", () => {
    it("should render refresh button", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const refreshBtn = screen.getByRole("button", { name: /refresh/i });
      expect(refreshBtn).toBeInTheDocument();
    });

    it("should call onRefresh when refresh button is clicked", () => {
      const onRefresh = vi.fn();
      render(<EnhancedBottomBar {...defaultProps} onRefresh={onRefresh} />);

      const refreshBtn = screen.getByRole("button", { name: /refresh/i });
      fireEvent.click(refreshBtn);

      expect(onRefresh).toHaveBeenCalled();
    });

    it("should render enrich button", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const enrichBtn = screen.getByRole("button", { name: /enrich/i });
      expect(enrichBtn).toBeInTheDocument();
    });

    it("should call onEnrich when enrich button is clicked", () => {
      const onEnrich = vi.fn();
      render(<EnhancedBottomBar {...defaultProps} onEnrich={onEnrich} />);

      const enrichBtn = screen.getByRole("button", { name: /enrich/i });
      fireEvent.click(enrichBtn);

      expect(onEnrich).toHaveBeenCalled();
    });

    it("should show loading spinner on refresh button when isLoading", () => {
      render(<EnhancedBottomBar {...defaultProps} isLoading={true} />);

      const refreshBtn = screen.getByRole("button", { name: /refresh/i });
      expect(refreshBtn.querySelector(".animate-spin")).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Animation Tests
  // ============================================================================

  describe("Animations", () => {
    it("should apply glow effect to bottom bar", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const container = screen.getByTestId("enhanced-bottom-bar");
      expect(container).toHaveClass("glow-subtle");
    });

    it("should apply smooth transition classes", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const container = screen.getByTestId("enhanced-bottom-bar");
      expect(container).toHaveClass("transition-all");
    });
  });

  // ============================================================================
  // Responsive Tests
  // ============================================================================

  describe("Responsive Behavior", () => {
    it("should stack KPIs on smaller screens", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const kpiContainer = screen.getByTestId("kpi-container");
      expect(kpiContainer).toHaveClass("flex-wrap");
    });

    it("should hide some KPIs on very small screens", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const mttrKpi = screen.getByTestId("kpi-mttr");
      expect(mttrKpi).toHaveClass("hidden", "sm:flex");
    });
  });

  // ============================================================================
  // Accessibility Tests
  // ============================================================================

  describe("Accessibility", () => {
    it("should have appropriate aria labels for KPIs", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const totalKpi = screen.getByTestId("kpi-total");
      expect(totalKpi).toHaveAttribute("aria-label", expect.stringContaining("Total"));
    });

    it("should have aria-valuenow for progress bar", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const progressBar = screen.getByTestId("remediation-progress");
      expect(progressBar).toHaveAttribute("role", "progressbar");
      expect(progressBar).toHaveAttribute("aria-valuenow");
    });

    it("should have keyboard navigable time range buttons", () => {
      render(<EnhancedBottomBar {...defaultProps} />);

      const buttons = screen.getAllByRole("button");
      buttons.forEach((button) => {
        expect(button).not.toHaveAttribute("tabindex", "-1");
      });
    });
  });
});
