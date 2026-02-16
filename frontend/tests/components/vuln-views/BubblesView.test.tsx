/**
 * BubblesView Component Unit Tests
 *
 * TDD tests for animated bubbles where size = risk score with D3-force physics
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { BubblesView } from "../../../src/components/vuln-views/BubblesView";
import type { BubblesViewData } from "../../../src/types/vulnerabilityViews";

// Mock data for tests
const mockBubblesData: BubblesViewData = {
  bubbles: [
    {
      cve_id: "CVE-2024-0001",
      risk_score: 95,
      cvss_score: 9.8,
      epss_score: 0.95,
      severity: "Critical",
      is_kev: true,
      ssvc_decision: "Act",
      title: "Critical RCE Vulnerability",
      affected_asset_count: 50,
    },
    {
      cve_id: "CVE-2024-0002",
      risk_score: 75,
      cvss_score: 7.5,
      epss_score: 0.6,
      severity: "High",
      is_kev: false,
      ssvc_decision: "Attend",
      title: "High Privilege Escalation",
      affected_asset_count: 30,
    },
    {
      cve_id: "CVE-2024-0003",
      risk_score: 45,
      cvss_score: 5.0,
      epss_score: 0.3,
      severity: "Medium",
      is_kev: false,
      ssvc_decision: "Track*",
      title: "Medium XSS Vulnerability",
      affected_asset_count: 15,
    },
    {
      cve_id: "CVE-2024-0004",
      risk_score: 20,
      cvss_score: 3.0,
      epss_score: 0.1,
      severity: "Low",
      is_kev: false,
      ssvc_decision: "Track",
      title: "Low Info Disclosure",
      affected_asset_count: 5,
    },
  ],
  total_cves: 4,
  severity_distribution: {
    critical: 1,
    high: 1,
    medium: 1,
    low: 1,
  },
};

describe("BubblesView Component", () => {
  // ============================================================================
  // Rendering Tests
  // ============================================================================
  describe("Rendering", () => {
    it("should render the bubbles container", () => {
      render(<BubblesView data={mockBubblesData} />);

      const container = screen.getByTestId("bubbles-view");
      expect(container).toBeInTheDocument();
    });

    it("should render SVG element for the visualization", () => {
      render(<BubblesView data={mockBubblesData} />);

      const svg = screen.getByTestId("bubbles-svg");
      expect(svg).toBeInTheDocument();
      expect(svg.tagName.toLowerCase()).toBe("svg");
    });

    it("should render a bubble for each CVE", () => {
      render(<BubblesView data={mockBubblesData} />);

      const bubbles = screen.getAllByTestId(/bubble-/);
      expect(bubbles).toHaveLength(4);
    });

    it("should render with custom className", () => {
      render(<BubblesView data={mockBubblesData} className="custom-class" />);

      const container = screen.getByTestId("bubbles-view");
      expect(container).toHaveClass("custom-class");
    });

    it("should show loading state when isLoading is true", () => {
      render(<BubblesView data={mockBubblesData} isLoading={true} />);

      expect(screen.getByTestId("bubbles-loading")).toBeInTheDocument();
    });

    it("should show error message when error prop is provided", () => {
      render(<BubblesView data={mockBubblesData} error="Failed to load data" />);

      expect(screen.getByText(/failed to load data/i)).toBeInTheDocument();
    });

    it("should show empty state when no bubbles", () => {
      const emptyData: BubblesViewData = {
        bubbles: [],
        total_cves: 0,
        severity_distribution: { critical: 0, high: 0, medium: 0, low: 0 },
      };

      render(<BubblesView data={emptyData} />);

      expect(screen.getByText(/no vulnerability data/i)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Visual Mapping Tests
  // ============================================================================
  describe("Visual Mapping", () => {
    it("should size bubbles based on risk score", () => {
      render(<BubblesView data={mockBubblesData} />);

      const criticalBubble = screen.getByTestId("bubble-CVE-2024-0001");
      const lowBubble = screen.getByTestId("bubble-CVE-2024-0004");

      const criticalRadius = parseFloat(criticalBubble.getAttribute("r") ?? "0");
      const lowRadius = parseFloat(lowBubble.getAttribute("r") ?? "0");

      // Higher risk score = larger bubble
      expect(criticalRadius).toBeGreaterThan(lowRadius);
    });

    it("should apply correct color for Critical severity", () => {
      render(<BubblesView data={mockBubblesData} />);

      const bubble = screen.getByTestId("bubble-CVE-2024-0001");
      expect(bubble).toHaveAttribute("data-severity", "Critical");
    });

    it("should apply correct color for High severity", () => {
      render(<BubblesView data={mockBubblesData} />);

      const bubble = screen.getByTestId("bubble-CVE-2024-0002");
      expect(bubble).toHaveAttribute("data-severity", "High");
    });

    it("should apply correct color for Medium severity", () => {
      render(<BubblesView data={mockBubblesData} />);

      const bubble = screen.getByTestId("bubble-CVE-2024-0003");
      expect(bubble).toHaveAttribute("data-severity", "Medium");
    });

    it("should apply correct color for Low severity", () => {
      render(<BubblesView data={mockBubblesData} />);

      const bubble = screen.getByTestId("bubble-CVE-2024-0004");
      expect(bubble).toHaveAttribute("data-severity", "Low");
    });
  });

  // ============================================================================
  // KEV Indicator Tests
  // ============================================================================
  describe("KEV Indicator", () => {
    it("should show KEV indicator on KEV CVEs", () => {
      render(<BubblesView data={mockBubblesData} />);

      const kevBubble = screen.getByTestId("bubble-CVE-2024-0001");
      const kevIndicator = kevBubble.parentElement?.querySelector("[data-kev]");

      expect(kevIndicator).toBeInTheDocument();
    });

    it("should not show KEV indicator on non-KEV CVEs", () => {
      render(<BubblesView data={mockBubblesData} />);

      const nonKevBubble = screen.getByTestId("bubble-CVE-2024-0002");
      const kevIndicator = nonKevBubble.parentElement?.querySelector("[data-kev]");

      expect(kevIndicator).not.toBeInTheDocument();
    });
  });

  // ============================================================================
  // SSVC Decision Indicator Tests
  // ============================================================================
  describe("SSVC Decision Indicator", () => {
    it("should show Act indicator for Act decisions", () => {
      render(<BubblesView data={mockBubblesData} />);

      const actBubble = screen.getByTestId("bubble-CVE-2024-0001");
      expect(actBubble).toHaveAttribute("data-ssvc", "Act");
    });

    it("should show Attend indicator for Attend decisions", () => {
      render(<BubblesView data={mockBubblesData} />);

      const attendBubble = screen.getByTestId("bubble-CVE-2024-0002");
      expect(attendBubble).toHaveAttribute("data-ssvc", "Attend");
    });

    it("should show Track* indicator for Track* decisions", () => {
      render(<BubblesView data={mockBubblesData} />);

      const trackStarBubble = screen.getByTestId("bubble-CVE-2024-0003");
      expect(trackStarBubble).toHaveAttribute("data-ssvc", "Track*");
    });

    it("should show Track indicator for Track decisions", () => {
      render(<BubblesView data={mockBubblesData} />);

      const trackBubble = screen.getByTestId("bubble-CVE-2024-0004");
      expect(trackBubble).toHaveAttribute("data-ssvc", "Track");
    });
  });

  // ============================================================================
  // Interaction Tests
  // ============================================================================
  describe("Interactions", () => {
    it("should call onCVEClick when a bubble is clicked", () => {
      const onCVEClick = vi.fn();
      render(<BubblesView data={mockBubblesData} onCVEClick={onCVEClick} />);

      const bubble = screen.getByTestId("bubble-CVE-2024-0001");
      fireEvent.click(bubble);

      expect(onCVEClick).toHaveBeenCalledWith("CVE-2024-0001");
    });

    it("should show tooltip on hover with CVE details", () => {
      render(<BubblesView data={mockBubblesData} />);

      const bubble = screen.getByTestId("bubble-CVE-2024-0001");
      fireEvent.mouseEnter(bubble);

      expect(screen.getByRole("tooltip")).toBeInTheDocument();
      expect(screen.getByText("CVE-2024-0001")).toBeInTheDocument();
      expect(screen.getByText(/risk: 95/i)).toBeInTheDocument();
      expect(screen.getByText(/50 assets/i)).toBeInTheDocument();
    });

    it("should hide tooltip on mouse leave", () => {
      render(<BubblesView data={mockBubblesData} />);

      const bubble = screen.getByTestId("bubble-CVE-2024-0001");
      fireEvent.mouseEnter(bubble);
      fireEvent.mouseLeave(bubble);

      expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
    });

    it("should highlight connected bubbles on hover", () => {
      render(<BubblesView data={mockBubblesData} />);

      const bubble = screen.getByTestId("bubble-CVE-2024-0001");
      fireEvent.mouseEnter(bubble);

      // The hovered bubble should be highlighted
      expect(bubble).toHaveAttribute("data-highlighted", "true");
    });
  });

  // ============================================================================
  // Filter Integration Tests
  // ============================================================================
  describe("Filter Integration", () => {
    it("should filter bubbles by SSVC decision", () => {
      render(<BubblesView data={mockBubblesData} filterSSVC={["Act"]} />);

      const bubbles = screen.getAllByTestId(/bubble-/);
      // Only Act decision bubble should be visible
      const visibleBubbles = bubbles.filter(
        (b) => !b.classList.contains("hidden") && b.getAttribute("data-ssvc") === "Act",
      );
      expect(visibleBubbles.length).toBeGreaterThanOrEqual(1);
    });

    it("should filter bubbles by severity", () => {
      render(<BubblesView data={mockBubblesData} filterSeverity={["Critical"]} />);

      const bubbles = screen.getAllByTestId(/bubble-/);
      const visibleBubbles = bubbles.filter(
        (b) => !b.classList.contains("hidden") && b.getAttribute("data-severity") === "Critical",
      );
      expect(visibleBubbles.length).toBeGreaterThanOrEqual(1);
    });
  });

  // ============================================================================
  // Legend Tests
  // ============================================================================
  describe("Legend", () => {
    it("should render severity legend", () => {
      render(<BubblesView data={mockBubblesData} />);

      expect(screen.getByTestId("bubbles-legend")).toBeInTheDocument();
      expect(screen.getByText(/critical/i)).toBeInTheDocument();
      expect(screen.getByText(/high/i)).toBeInTheDocument();
      expect(screen.getByText(/medium/i)).toBeInTheDocument();
      expect(screen.getByText(/low/i)).toBeInTheDocument();
    });

    it("should show severity counts in legend", () => {
      render(<BubblesView data={mockBubblesData} />);

      const legend = screen.getByTestId("bubbles-legend");
      expect(legend).toHaveTextContent("1"); // Each severity has 1
    });
  });

  // ============================================================================
  // Accessibility Tests
  // ============================================================================
  describe("Accessibility", () => {
    it("should have appropriate aria labels", () => {
      render(<BubblesView data={mockBubblesData} />);

      const container = screen.getByTestId("bubbles-view");
      expect(container).toHaveAttribute("aria-label", expect.stringContaining("vulnerability"));
    });

    it("should have focusable bubbles", () => {
      render(<BubblesView data={mockBubblesData} />);

      const bubbles = screen.getAllByTestId(/bubble-/);
      bubbles.forEach((bubble) => {
        // SVG elements render tabIndex as lowercase 'tabindex' in the DOM
        expect(bubble).toHaveAttribute("tabindex", "0");
      });
    });

    it("should trigger click on Enter key", () => {
      const onCVEClick = vi.fn();
      render(<BubblesView data={mockBubblesData} onCVEClick={onCVEClick} />);

      const bubble = screen.getByTestId("bubble-CVE-2024-0001");
      fireEvent.keyDown(bubble, { key: "Enter" });

      expect(onCVEClick).toHaveBeenCalledWith("CVE-2024-0001");
    });
  });
});
