/**
 * DNAView Component Unit Tests
 *
 * TDD tests for the double helix visualization showing CVE-Asset pairs
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DNAView } from "../../../src/components/vuln-views/DNAView";
import type { DNAViewData } from "../../../src/types/vulnerabilityViews";

// Mock data for tests
const mockDNAData: DNAViewData = {
  strands: [
    {
      cve_id: "CVE-2024-0001",
      asset_id: "asset-001",
      asset_hostname: "server-prod-01",
      cvss_score: 9.8,
      severity: "Critical",
      is_kev: true,
      exploit_available: true,
      position: 0,
    },
    {
      cve_id: "CVE-2024-0001",
      asset_id: "asset-002",
      asset_hostname: "server-prod-02",
      cvss_score: 9.8,
      severity: "Critical",
      is_kev: true,
      exploit_available: true,
      position: 1,
    },
    {
      cve_id: "CVE-2024-0002",
      asset_id: "asset-003",
      asset_hostname: "workstation-01",
      cvss_score: 7.5,
      severity: "High",
      is_kev: false,
      exploit_available: true,
      position: 2,
    },
    {
      cve_id: "CVE-2024-0003",
      asset_id: "asset-004",
      asset_hostname: "laptop-dev-01",
      cvss_score: 5.0,
      severity: "Medium",
      is_kev: false,
      exploit_available: false,
      position: 3,
    },
  ],
  total_pairs: 4,
  kev_pairs: 2,
  exploitable_pairs: 3,
};

describe("DNAView Component", () => {
  // ============================================================================
  // Rendering Tests
  // ============================================================================
  describe("Rendering", () => {
    it("should render the DNA view container", () => {
      render(<DNAView data={mockDNAData} />);

      const container = screen.getByTestId("dna-view");
      expect(container).toBeInTheDocument();
    });

    it("should render SVG element for the helix", () => {
      render(<DNAView data={mockDNAData} />);

      const svg = screen.getByTestId("dna-svg");
      expect(svg).toBeInTheDocument();
      expect(svg.tagName.toLowerCase()).toBe("svg");
    });

    it("should render nodes for each CVE-Asset pair", () => {
      render(<DNAView data={mockDNAData} />);

      const nodes = screen.getAllByTestId(/dna-node-/);
      expect(nodes).toHaveLength(4);
    });

    it("should render helix backbone strands", () => {
      render(<DNAView data={mockDNAData} />);

      const strands = screen.getAllByTestId(/dna-strand-/);
      expect(strands.length).toBeGreaterThanOrEqual(2); // At least 2 backbone strands
    });

    it("should render connecting rungs between strands", () => {
      render(<DNAView data={mockDNAData} />);

      const rungs = screen.getAllByTestId(/dna-rung-/);
      expect(rungs.length).toBeGreaterThanOrEqual(1);
    });

    it("should render with custom className", () => {
      render(<DNAView data={mockDNAData} className="custom-class" />);

      const container = screen.getByTestId("dna-view");
      expect(container).toHaveClass("custom-class");
    });

    it("should show loading state when isLoading is true", () => {
      render(<DNAView data={mockDNAData} isLoading={true} />);

      expect(screen.getByTestId("dna-loading")).toBeInTheDocument();
    });

    it("should show error message when error prop is provided", () => {
      render(<DNAView data={mockDNAData} error="Failed to load data" />);

      expect(screen.getByText(/failed to load data/i)).toBeInTheDocument();
    });

    it("should show empty state when no strands", () => {
      const emptyData: DNAViewData = {
        strands: [],
        total_pairs: 0,
        kev_pairs: 0,
        exploitable_pairs: 0,
      };

      render(<DNAView data={emptyData} />);

      expect(screen.getByText(/no cve-asset pairs/i)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Visual Mapping Tests
  // ============================================================================
  describe("Visual Mapping", () => {
    it("should position nodes along helix based on position", () => {
      render(<DNAView data={mockDNAData} />);

      const node0 = screen.getByTestId("dna-node-0");
      const node3 = screen.getByTestId("dna-node-3");

      // Nodes should have different y positions
      const y0 = parseFloat(node0.getAttribute("cy") ?? "0");
      const y3 = parseFloat(node3.getAttribute("cy") ?? "0");

      expect(y0).not.toBe(y3);
    });

    it("should apply correct color for Critical severity", () => {
      render(<DNAView data={mockDNAData} />);

      const node = screen.getByTestId("dna-node-0");
      expect(node).toHaveAttribute("data-severity", "Critical");
    });

    it("should apply correct color for High severity", () => {
      render(<DNAView data={mockDNAData} />);

      const node = screen.getByTestId("dna-node-2");
      expect(node).toHaveAttribute("data-severity", "High");
    });

    it("should apply correct color for Medium severity", () => {
      render(<DNAView data={mockDNAData} />);

      const node = screen.getByTestId("dna-node-3");
      expect(node).toHaveAttribute("data-severity", "Medium");
    });

    it("should size nodes based on CVSS score", () => {
      render(<DNAView data={mockDNAData} />);

      const criticalNode = screen.getByTestId("dna-node-0");
      const mediumNode = screen.getByTestId("dna-node-3");

      const criticalRadius = parseFloat(criticalNode.getAttribute("r") ?? "0");
      const mediumRadius = parseFloat(mediumNode.getAttribute("r") ?? "0");

      expect(criticalRadius).toBeGreaterThan(mediumRadius);
    });
  });

  // ============================================================================
  // KEV Indicator Tests
  // ============================================================================
  describe("KEV Indicator", () => {
    it("should show KEV glow on KEV pairs", () => {
      render(<DNAView data={mockDNAData} />);

      const kevNode = screen.getByTestId("dna-node-0");
      expect(kevNode).toHaveAttribute("data-kev", "true");
    });

    it("should not show KEV glow on non-KEV pairs", () => {
      render(<DNAView data={mockDNAData} />);

      const nonKevNode = screen.getByTestId("dna-node-2");
      expect(nonKevNode).toHaveAttribute("data-kev", "false");
    });
  });

  // ============================================================================
  // Exploit Indicator Tests
  // ============================================================================
  describe("Exploit Indicator", () => {
    it("should show exploit indicator on exploitable pairs", () => {
      render(<DNAView data={mockDNAData} />);

      const exploitNode = screen.getByTestId("dna-node-0");
      expect(exploitNode).toHaveAttribute("data-exploit", "true");
    });

    it("should not show exploit indicator on non-exploitable pairs", () => {
      render(<DNAView data={mockDNAData} />);

      const nonExploitNode = screen.getByTestId("dna-node-3");
      expect(nonExploitNode).toHaveAttribute("data-exploit", "false");
    });
  });

  // ============================================================================
  // Rotation Animation Tests
  // ============================================================================
  describe("Rotation Animation", () => {
    it("should have rotation animation class", () => {
      render(<DNAView data={mockDNAData} />);

      const helix = screen.getByTestId("dna-helix-group");
      expect(helix).toHaveClass("animate-dna-rotate");
    });

    it("should pause rotation on hover", () => {
      render(<DNAView data={mockDNAData} />);

      const container = screen.getByTestId("dna-view");
      fireEvent.mouseEnter(container);

      const helix = screen.getByTestId("dna-helix-group");
      expect(helix).toHaveAttribute("data-paused", "true");
    });

    it("should resume rotation on mouse leave", () => {
      render(<DNAView data={mockDNAData} />);

      const container = screen.getByTestId("dna-view");
      fireEvent.mouseEnter(container);
      fireEvent.mouseLeave(container);

      const helix = screen.getByTestId("dna-helix-group");
      expect(helix).toHaveAttribute("data-paused", "false");
    });
  });

  // ============================================================================
  // Interaction Tests
  // ============================================================================
  describe("Interactions", () => {
    it("should call onCVEClick when a CVE node is clicked", () => {
      const onCVEClick = vi.fn();
      render(<DNAView data={mockDNAData} onCVEClick={onCVEClick} />);

      const node = screen.getByTestId("dna-node-0");
      fireEvent.click(node);

      expect(onCVEClick).toHaveBeenCalledWith("CVE-2024-0001");
    });

    it("should call onAssetClick when an asset label is clicked", () => {
      const onAssetClick = vi.fn();
      render(<DNAView data={mockDNAData} onAssetClick={onAssetClick} />);

      const assetLabel = screen.getByText("server-prod-01");
      fireEvent.click(assetLabel);

      expect(onAssetClick).toHaveBeenCalledWith("asset-001");
    });

    it("should show tooltip on node hover", () => {
      render(<DNAView data={mockDNAData} />);

      const node = screen.getByTestId("dna-node-0");
      fireEvent.mouseEnter(node);

      expect(screen.getByRole("tooltip")).toBeInTheDocument();
      // Use getAllByText since hostname appears in both tooltip and label
      expect(screen.getAllByText("CVE-2024-0001").length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText("server-prod-01").length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText(/cvss: 9.8/i)).toBeInTheDocument();
    });

    it("should hide tooltip on mouse leave", () => {
      render(<DNAView data={mockDNAData} />);

      const node = screen.getByTestId("dna-node-0");
      fireEvent.mouseEnter(node);
      fireEvent.mouseLeave(node);

      expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
    });

    it("should highlight related pairs when hovering on CVE", () => {
      render(<DNAView data={mockDNAData} />);

      // CVE-2024-0001 appears in 2 pairs
      const node = screen.getByTestId("dna-node-0");
      fireEvent.mouseEnter(node);

      // Both nodes with CVE-2024-0001 should be highlighted
      const node0 = screen.getByTestId("dna-node-0");
      const node1 = screen.getByTestId("dna-node-1");

      expect(node0).toHaveAttribute("data-highlighted", "true");
      expect(node1).toHaveAttribute("data-highlighted", "true");
    });
  });

  // ============================================================================
  // Stats Display Tests
  // ============================================================================
  describe("Stats Display", () => {
    it("should show total pairs count", () => {
      render(<DNAView data={mockDNAData} />);

      expect(screen.getByText(/4 pairs/i)).toBeInTheDocument();
    });

    it("should show KEV pairs count", () => {
      render(<DNAView data={mockDNAData} />);

      expect(screen.getByText(/2 kev/i)).toBeInTheDocument();
    });

    it("should show exploitable pairs count", () => {
      render(<DNAView data={mockDNAData} />);

      expect(screen.getByText(/3 exploitable/i)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Accessibility Tests
  // ============================================================================
  describe("Accessibility", () => {
    it("should have appropriate aria labels", () => {
      render(<DNAView data={mockDNAData} />);

      const container = screen.getByTestId("dna-view");
      expect(container).toHaveAttribute("aria-label", expect.stringContaining("CVE"));
    });

    it("should have focusable nodes", () => {
      render(<DNAView data={mockDNAData} />);

      const nodes = screen.getAllByTestId(/dna-node-/);
      nodes.forEach((node) => {
        // SVG elements render tabIndex as lowercase 'tabindex' in the DOM
        expect(node).toHaveAttribute("tabindex", "0");
      });
    });

    it("should trigger click on Enter key", () => {
      const onCVEClick = vi.fn();
      render(<DNAView data={mockDNAData} onCVEClick={onCVEClick} />);

      const node = screen.getByTestId("dna-node-0");
      fireEvent.keyDown(node, { key: "Enter" });

      expect(onCVEClick).toHaveBeenCalledWith("CVE-2024-0001");
    });
  });
});
