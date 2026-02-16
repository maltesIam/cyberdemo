/**
 * CalendarHeatmap Component Unit Tests
 *
 * TDD tests for the GitHub-style calendar showing CVE discoveries per day
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { CalendarHeatmap } from "../../../src/components/vuln-views/CalendarHeatmap";
import type { CalendarHeatmapData } from "../../../src/types/vulnerabilityViews";

// Mock data for tests
const mockCalendarData: CalendarHeatmapData = {
  days: [
    {
      date: "2024-01-01",
      count: 5,
      critical_count: 2,
      high_count: 1,
      medium_count: 1,
      low_count: 1,
    },
    {
      date: "2024-01-02",
      count: 10,
      critical_count: 5,
      high_count: 3,
      medium_count: 2,
      low_count: 0,
    },
    {
      date: "2024-01-03",
      count: 0,
      critical_count: 0,
      high_count: 0,
      medium_count: 0,
      low_count: 0,
    },
    {
      date: "2024-01-04",
      count: 3,
      critical_count: 0,
      high_count: 1,
      medium_count: 2,
      low_count: 0,
    },
  ],
  start_date: "2024-01-01",
  end_date: "2024-01-04",
  max_count: 10,
  total_cves: 18,
};

describe("CalendarHeatmap Component", () => {
  // ============================================================================
  // Rendering Tests
  // ============================================================================
  describe("Rendering", () => {
    it("should render the calendar container", () => {
      render(<CalendarHeatmap data={mockCalendarData} />);

      const container = screen.getByTestId("calendar-heatmap");
      expect(container).toBeInTheDocument();
    });

    it("should render day cells for each day", () => {
      render(<CalendarHeatmap data={mockCalendarData} />);

      const dayCells = screen.getAllByTestId(/calendar-day-/);
      expect(dayCells).toHaveLength(4);
    });

    it("should render with custom className", () => {
      render(<CalendarHeatmap data={mockCalendarData} className="custom-class" />);

      const container = screen.getByTestId("calendar-heatmap");
      expect(container).toHaveClass("custom-class");
    });

    it("should show loading state when isLoading is true", () => {
      render(<CalendarHeatmap data={mockCalendarData} isLoading={true} />);

      expect(screen.getByTestId("calendar-loading")).toBeInTheDocument();
    });

    it("should show error message when error prop is provided", () => {
      render(<CalendarHeatmap data={mockCalendarData} error="Failed to load data" />);

      expect(screen.getByText(/failed to load data/i)).toBeInTheDocument();
    });

    it("should show empty state when no data", () => {
      const emptyData: CalendarHeatmapData = {
        days: [],
        start_date: "",
        end_date: "",
        max_count: 0,
        total_cves: 0,
      };

      render(<CalendarHeatmap data={emptyData} />);

      expect(screen.getByText(/no calendar data/i)).toBeInTheDocument();
    });

    it("should render month labels", () => {
      render(<CalendarHeatmap data={mockCalendarData} />);

      expect(screen.getByText(/jan/i)).toBeInTheDocument();
    });

    it("should render day-of-week labels", () => {
      render(<CalendarHeatmap data={mockCalendarData} />);

      // Should have Mon, Wed, Fri labels (typical GitHub calendar style)
      expect(screen.getByText(/mon/i)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Heat Intensity Tests
  // ============================================================================
  describe("Heat Intensity", () => {
    it("should apply highest intensity to days with most CVEs", () => {
      render(<CalendarHeatmap data={mockCalendarData} />);

      const highestDay = screen.getByTestId("calendar-day-2024-01-02");
      expect(highestDay).toHaveAttribute("data-intensity", "4"); // Highest intensity
    });

    it("should apply lowest intensity to days with zero CVEs", () => {
      render(<CalendarHeatmap data={mockCalendarData} />);

      const emptyDay = screen.getByTestId("calendar-day-2024-01-03");
      expect(emptyDay).toHaveAttribute("data-intensity", "0");
    });

    it("should apply medium intensity to days with moderate CVEs", () => {
      render(<CalendarHeatmap data={mockCalendarData} />);

      const mediumDay = screen.getByTestId("calendar-day-2024-01-01");
      // 5 out of max 10 = medium intensity
      const intensity = parseInt(mediumDay.getAttribute("data-intensity") ?? "0");
      expect(intensity).toBeGreaterThan(0);
      expect(intensity).toBeLessThan(4);
    });
  });

  // ============================================================================
  // Critical Day Pulse Animation Tests
  // ============================================================================
  describe("Critical Day Pulse Animation", () => {
    it("should show pulse animation on days with critical CVEs", () => {
      render(<CalendarHeatmap data={mockCalendarData} />);

      const criticalDay = screen.getByTestId("calendar-day-2024-01-01");
      expect(criticalDay).toHaveAttribute("data-has-critical", "true");
    });

    it("should not show pulse animation on days without critical CVEs", () => {
      render(<CalendarHeatmap data={mockCalendarData} />);

      const nonCriticalDay = screen.getByTestId("calendar-day-2024-01-04");
      expect(nonCriticalDay).toHaveAttribute("data-has-critical", "false");
    });
  });

  // ============================================================================
  // Interaction Tests
  // ============================================================================
  describe("Interactions", () => {
    it("should call onDayClick when a day is clicked", () => {
      const onDayClick = vi.fn();
      render(<CalendarHeatmap data={mockCalendarData} onDayClick={onDayClick} />);

      const day = screen.getByTestId("calendar-day-2024-01-01");
      fireEvent.click(day);

      expect(onDayClick).toHaveBeenCalledWith("2024-01-01");
    });

    it("should show tooltip on hover with CVE counts", () => {
      render(<CalendarHeatmap data={mockCalendarData} />);

      const day = screen.getByTestId("calendar-day-2024-01-01");
      fireEvent.mouseEnter(day);

      expect(screen.getByRole("tooltip")).toBeInTheDocument();
      expect(screen.getByText(/5 cves/i)).toBeInTheDocument();
      expect(screen.getByText(/2 critical/i)).toBeInTheDocument();
    });

    it("should hide tooltip on mouse leave", () => {
      render(<CalendarHeatmap data={mockCalendarData} />);

      const day = screen.getByTestId("calendar-day-2024-01-01");
      fireEvent.mouseEnter(day);
      fireEvent.mouseLeave(day);

      expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
    });
  });

  // ============================================================================
  // Legend Tests
  // ============================================================================
  describe("Legend", () => {
    it("should render the color legend", () => {
      render(<CalendarHeatmap data={mockCalendarData} />);

      expect(screen.getByTestId("calendar-legend")).toBeInTheDocument();
    });

    it("should show Less to More labels in legend", () => {
      render(<CalendarHeatmap data={mockCalendarData} />);

      expect(screen.getByText(/less/i)).toBeInTheDocument();
      expect(screen.getByText(/more/i)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Accessibility Tests
  // ============================================================================
  describe("Accessibility", () => {
    it("should have appropriate aria labels", () => {
      render(<CalendarHeatmap data={mockCalendarData} />);

      const container = screen.getByTestId("calendar-heatmap");
      expect(container).toHaveAttribute("aria-label", expect.stringContaining("calendar"));
    });

    it("should have focusable days", () => {
      render(<CalendarHeatmap data={mockCalendarData} />);

      const days = screen.getAllByTestId(/calendar-day-/);
      days.forEach((day) => {
        // HTML elements render tabIndex as lowercase 'tabindex' in the DOM
        expect(day).toHaveAttribute("tabindex", "0");
      });
    });
  });
});
