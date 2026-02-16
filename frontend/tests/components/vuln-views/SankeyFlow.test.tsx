/**
 * SankeyFlow Component Unit Tests
 *
 * TDD tests for the remediation workflow visualization using Sankey diagram
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { SankeyFlow } from "../../../src/components/vuln-views/SankeyFlow";
import type { SankeyFlowData } from "../../../src/types/vulnerabilityViews";

// Mock data for tests
const mockSankeyData: SankeyFlowData = {
  nodes: [
    { id: "discovered", name: "Discovered", count: 100, color: "#6b7280" },
    { id: "triaged", name: "Triaged", count: 90, color: "#3b82f6" },
    { id: "assigned", name: "Assigned", count: 80, color: "#8b5cf6" },
    { id: "in_progress", name: "In Progress", count: 60, color: "#f59e0b" },
    { id: "remediated", name: "Remediated", count: 40, color: "#22c55e" },
    { id: "accepted_risk", name: "Accepted Risk", count: 15, color: "#ef4444" },
    { id: "false_positive", name: "False Positive", count: 5, color: "#9ca3af" },
  ],
  links: [
    { source: "discovered", target: "triaged", value: 90 },
    { source: "discovered", target: "false_positive", value: 5 },
    { source: "discovered", target: "accepted_risk", value: 5 },
    { source: "triaged", target: "assigned", value: 80 },
    { source: "triaged", target: "accepted_risk", value: 10 },
    { source: "assigned", target: "in_progress", value: 60 },
    { source: "assigned", target: "remediated", value: 20 },
    { source: "in_progress", target: "remediated", value: 40 },
    { source: "in_progress", target: "in_progress", value: 20 }, // Still in progress
  ],
  total_cves: 100,
  remediated_count: 40,
  in_progress_count: 60,
  open_count: 100,
};

describe("SankeyFlow Component", () => {
  // ============================================================================
  // Rendering Tests
  // ============================================================================
  describe("Rendering", () => {
    it("should render the sankey container", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      const container = screen.getByTestId("sankey-flow");
      expect(container).toBeInTheDocument();
    });

    it("should render SVG element for the diagram", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      const svg = screen.getByTestId("sankey-svg");
      expect(svg).toBeInTheDocument();
      expect(svg.tagName.toLowerCase()).toBe("svg");
    });

    it("should render nodes for each workflow stage", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      const nodes = screen.getAllByTestId(/sankey-node-/);
      expect(nodes).toHaveLength(7);
    });

    it("should render links between nodes", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      const links = screen.getAllByTestId(/sankey-link-/);
      expect(links.length).toBeGreaterThanOrEqual(1);
    });

    it("should render with custom className", () => {
      render(<SankeyFlow data={mockSankeyData} className="custom-class" />);

      const container = screen.getByTestId("sankey-flow");
      expect(container).toHaveClass("custom-class");
    });

    it("should show loading state when isLoading is true", () => {
      render(<SankeyFlow data={mockSankeyData} isLoading={true} />);

      expect(screen.getByTestId("sankey-loading")).toBeInTheDocument();
    });

    it("should show error message when error prop is provided", () => {
      render(<SankeyFlow data={mockSankeyData} error="Failed to load data" />);

      expect(screen.getByText(/failed to load data/i)).toBeInTheDocument();
    });

    it("should show empty state when no data", () => {
      const emptyData: SankeyFlowData = {
        nodes: [],
        links: [],
        total_cves: 0,
        remediated_count: 0,
        in_progress_count: 0,
        open_count: 0,
      };

      render(<SankeyFlow data={emptyData} />);

      expect(screen.getByText(/no remediation data/i)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Node Rendering Tests
  // ============================================================================
  describe("Node Rendering", () => {
    it("should render node rectangles with correct heights", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      const discoveredNode = screen.getByTestId("sankey-node-discovered");
      const remediatedNode = screen.getByTestId("sankey-node-remediated");

      // Discovered (100) should be taller than Remediated (40)
      const discoveredHeight = parseFloat(discoveredNode.getAttribute("height") ?? "0");
      const remediatedHeight = parseFloat(remediatedNode.getAttribute("height") ?? "0");

      expect(discoveredHeight).toBeGreaterThan(remediatedHeight);
    });

    it("should display node labels", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      // Labels appear in both SVG and stats sections
      expect(screen.getAllByText("Discovered").length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText("Triaged").length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText("Remediated").length).toBeGreaterThanOrEqual(1);
    });

    it("should display node counts", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      // Counts appear in both SVG nodes and stats sections
      expect(screen.getAllByText("100").length).toBeGreaterThanOrEqual(1); // Discovered/Total
      expect(screen.getAllByText("40").length).toBeGreaterThanOrEqual(1); // Remediated
    });

    it("should apply correct colors to nodes", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      const remediatedNode = screen.getByTestId("sankey-node-remediated");
      expect(remediatedNode).toHaveAttribute("fill", "#22c55e");
    });
  });

  // ============================================================================
  // Link Rendering Tests
  // ============================================================================
  describe("Link Rendering", () => {
    it("should render links with gradient from source to target", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      const link = screen.getByTestId("sankey-link-discovered-triaged");
      expect(link).toHaveAttribute("data-source", "discovered");
      expect(link).toHaveAttribute("data-target", "triaged");
    });

    it("should size links proportionally to flow value", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      const largeLink = screen.getByTestId("sankey-link-discovered-triaged"); // 90
      const smallLink = screen.getByTestId("sankey-link-discovered-false_positive"); // 5

      const largeWidth = parseFloat(largeLink.getAttribute("stroke-width") ?? "0");
      const smallWidth = parseFloat(smallLink.getAttribute("stroke-width") ?? "0");

      expect(largeWidth).toBeGreaterThan(smallWidth);
    });
  });

  // ============================================================================
  // Flow Animation Tests
  // ============================================================================
  describe("Flow Animation", () => {
    it("should have flow animation on links", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      const link = screen.getByTestId("sankey-link-discovered-triaged");
      expect(link).toHaveClass("animate-sankey-flow");
    });

    it("should show particle animation when enabled", () => {
      render(<SankeyFlow data={mockSankeyData} showParticles={true} />);

      const particles = screen.getAllByTestId(/sankey-particle-/);
      expect(particles.length).toBeGreaterThanOrEqual(1);
    });

    it("should not show particles when disabled", () => {
      render(<SankeyFlow data={mockSankeyData} showParticles={false} />);

      const particles = screen.queryAllByTestId(/sankey-particle-/);
      expect(particles.length).toBe(0);
    });
  });

  // ============================================================================
  // Interaction Tests
  // ============================================================================
  describe("Interactions", () => {
    it("should call onNodeClick when a node is clicked", () => {
      const onNodeClick = vi.fn();
      render(<SankeyFlow data={mockSankeyData} onNodeClick={onNodeClick} />);

      const node = screen.getByTestId("sankey-node-remediated");
      fireEvent.click(node);

      expect(onNodeClick).toHaveBeenCalledWith("remediated");
    });

    it("should show tooltip on node hover", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      const node = screen.getByTestId("sankey-node-discovered");
      fireEvent.mouseEnter(node);

      expect(screen.getByRole("tooltip")).toBeInTheDocument();
      // "Discovered" appears in both tooltip and SVG label
      expect(screen.getAllByText(/discovered/i).length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText(/100 cves/i)).toBeInTheDocument();
    });

    it("should show tooltip on link hover with flow details", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      const link = screen.getByTestId("sankey-link-discovered-triaged");
      fireEvent.mouseEnter(link);

      expect(screen.getByRole("tooltip")).toBeInTheDocument();
      expect(screen.getByText(/90 cves/i)).toBeInTheDocument();
    });

    it("should hide tooltip on mouse leave", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      const node = screen.getByTestId("sankey-node-discovered");
      fireEvent.mouseEnter(node);
      fireEvent.mouseLeave(node);

      expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
    });

    it("should highlight connected links when hovering on node", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      const node = screen.getByTestId("sankey-node-triaged");
      fireEvent.mouseEnter(node);

      // Links connected to triaged should be highlighted
      const inLink = screen.getByTestId("sankey-link-discovered-triaged");
      const outLink = screen.getByTestId("sankey-link-triaged-assigned");

      expect(inLink).toHaveAttribute("data-highlighted", "true");
      expect(outLink).toHaveAttribute("data-highlighted", "true");
    });
  });

  // ============================================================================
  // Stats Summary Tests
  // ============================================================================
  describe("Stats Summary", () => {
    it("should display total CVEs count", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      expect(screen.getByTestId("sankey-stat-total")).toHaveTextContent("100");
    });

    it("should display remediated count", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      expect(screen.getByTestId("sankey-stat-remediated")).toHaveTextContent("40");
    });

    it("should display in-progress count", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      expect(screen.getByTestId("sankey-stat-progress")).toHaveTextContent("60");
    });

    it("should display remediation percentage", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      // 40/100 = 40%
      expect(screen.getByText(/40%/)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Time Period Filter Tests
  // ============================================================================
  describe("Time Period Filter", () => {
    it("should render time period selector", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      expect(screen.getByTestId("sankey-time-selector")).toBeInTheDocument();
    });

    it("should have 7d, 30d, 90d, All options", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      expect(screen.getByText("7d")).toBeInTheDocument();
      expect(screen.getByText("30d")).toBeInTheDocument();
      expect(screen.getByText("90d")).toBeInTheDocument();
      expect(screen.getByText("All")).toBeInTheDocument();
    });

    it("should call onTimePeriodChange when period is selected", () => {
      const onTimePeriodChange = vi.fn();
      render(<SankeyFlow data={mockSankeyData} onTimePeriodChange={onTimePeriodChange} />);

      const button30d = screen.getByText("30d");
      fireEvent.click(button30d);

      expect(onTimePeriodChange).toHaveBeenCalledWith("30d");
    });
  });

  // ============================================================================
  // Accessibility Tests
  // ============================================================================
  describe("Accessibility", () => {
    it("should have appropriate aria labels", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      const container = screen.getByTestId("sankey-flow");
      expect(container).toHaveAttribute("aria-label", expect.stringContaining("remediation"));
    });

    it("should have focusable nodes", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      const nodes = screen.getAllByTestId(/sankey-node-/);
      nodes.forEach((node) => {
        // SVG elements render tabIndex as lowercase 'tabindex' in the DOM
        expect(node).toHaveAttribute("tabindex", "0");
      });
    });

    it("should trigger click on Enter key", () => {
      const onNodeClick = vi.fn();
      render(<SankeyFlow data={mockSankeyData} onNodeClick={onNodeClick} />);

      const node = screen.getByTestId("sankey-node-remediated");
      fireEvent.keyDown(node, { key: "Enter" });

      expect(onNodeClick).toHaveBeenCalledWith("remediated");
    });

    it("should support keyboard navigation between nodes", () => {
      render(<SankeyFlow data={mockSankeyData} />);

      const firstNode = screen.getByTestId("sankey-node-discovered");
      firstNode.focus();

      fireEvent.keyDown(firstNode, { key: "ArrowRight" });

      // Focus should move to next node
      const secondNode = screen.getByTestId("sankey-node-triaged");
      expect(document.activeElement).toBe(secondNode);
    });
  });
});
