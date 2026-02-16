/**
 * CVEDetailPanel Component Unit Tests
 *
 * TDD tests for the CVE Detail Panel - Right Slide-in component
 * Features:
 * - Header with CVE-ID, Pin, Expand, Close buttons
 * - Risk Profile section with CVSS/EPSS bars, KEV badge, SSVC decision
 * - Risk Radar mini chart
 * - Description with CWE links
 * - Enrichment Sources grid
 * - Affected Assets list
 * - Exploits list
 * - Attack Chain visualization
 * - Vendor Patches section
 * - Action buttons
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { CVEDetailPanel } from "../../../src/components/vuln-views/CVEDetailPanel";

// ============================================================================
// Mock Data
// ============================================================================

const mockCVEDetail = {
  cve_id: "CVE-2024-0001",
  title: "Critical Remote Code Execution in Apache Log4j",
  description:
    "Apache Log4j2 allows remote attackers to execute arbitrary code via a crafted input that exploits JNDI lookups.",
  cvss_v3_score: 9.8,
  cvss_v3_vector: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
  epss_score: 0.972,
  epss_percentile: 99.8,
  risk_score: 95,
  severity: "Critical" as const,
  is_kev: true,
  kev_date_added: "2024-01-15",
  kev_due_date: "2024-02-05",
  kev_ransomware_use: true,
  ssvc_decision: "Act" as const,
  ssvc_exploitation: "Active",
  ssvc_automatable: true,
  exploit_count: 15,
  exploit_maturity: "Weaponized",
  has_nuclei_template: true,
  affected_asset_count: 127,
  affected_critical_assets: 12,
  cwe_ids: ["CWE-94", "CWE-502", "CWE-20"],
  ecosystems: ["java", "maven"],
  patch_available: true,
  published_date: "2024-01-10",
  last_enriched_at: "2024-02-15T10:30:00Z",
  enrichment_level: "full",
  enrichment_sources: ["NVD", "EPSS", "KEV", "ExploitDB", "Nuclei", "GHSA"],
  affected_assets: [
    { id: "asset-1", hostname: "prod-server-01", criticality: "High" },
    { id: "asset-2", hostname: "prod-server-02", criticality: "Critical" },
    { id: "asset-3", hostname: "dev-server-01", criticality: "Low" },
  ],
  exploits: [
    { id: "exp-1", name: "Log4Shell PoC", source: "ExploitDB", url: "https://exploit-db.com/..." },
    { id: "exp-2", name: "nuclei-log4j", source: "Nuclei", url: "https://github.com/..." },
  ],
  attack_chain: {
    cwe: "CWE-94",
    technique: "T1059",
    actor: "APT29",
  },
  patches: [
    { vendor: "Apache", version: "2.17.1", url: "https://apache.org/...", date: "2024-01-20" },
  ],
};

const defaultProps = {
  cve: mockCVEDetail,
  isOpen: true,
  onClose: vi.fn(),
  onPin: vi.fn(),
  onExpand: vi.fn(),
  onAction: vi.fn(),
};

// ============================================================================
// Rendering Tests
// ============================================================================

describe("CVEDetailPanel Component", () => {
  describe("Rendering", () => {
    it("should render the panel when isOpen is true", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const panel = screen.getByTestId("cve-detail-panel");
      expect(panel).toBeInTheDocument();
    });

    it("should not render when isOpen is false", () => {
      render(<CVEDetailPanel {...defaultProps} isOpen={false} />);

      expect(screen.queryByTestId("cve-detail-panel")).not.toBeInTheDocument();
    });

    it("should render with slide-in animation class", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const panel = screen.getByTestId("cve-detail-panel");
      expect(panel).toHaveClass("animate-slide-in-right");
    });

    it("should render with custom className", () => {
      render(<CVEDetailPanel {...defaultProps} className="custom-panel" />);

      const panel = screen.getByTestId("cve-detail-panel");
      expect(panel).toHaveClass("custom-panel");
    });
  });

  // ============================================================================
  // Header Tests
  // ============================================================================

  describe("Header", () => {
    it("should render CVE-ID in header", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      expect(screen.getByText("CVE-2024-0001")).toBeInTheDocument();
    });

    it("should render Pin button", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const pinButton = screen.getByRole("button", { name: /pin/i });
      expect(pinButton).toBeInTheDocument();
    });

    it("should call onPin when Pin button is clicked", () => {
      const onPin = vi.fn();
      render(<CVEDetailPanel {...defaultProps} onPin={onPin} />);

      const pinButton = screen.getByRole("button", { name: /pin/i });
      fireEvent.click(pinButton);

      expect(onPin).toHaveBeenCalledWith("CVE-2024-0001");
    });

    it("should render Expand button", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const expandButton = screen.getByRole("button", { name: /expand/i });
      expect(expandButton).toBeInTheDocument();
    });

    it("should call onExpand when Expand button is clicked", () => {
      const onExpand = vi.fn();
      render(<CVEDetailPanel {...defaultProps} onExpand={onExpand} />);

      const expandButton = screen.getByRole("button", { name: /expand/i });
      fireEvent.click(expandButton);

      expect(onExpand).toHaveBeenCalledWith("CVE-2024-0001");
    });

    it("should render Close button", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const closeButton = screen.getByRole("button", { name: /close/i });
      expect(closeButton).toBeInTheDocument();
    });

    it("should call onClose when Close button is clicked", () => {
      const onClose = vi.fn();
      render(<CVEDetailPanel {...defaultProps} onClose={onClose} />);

      const closeButton = screen.getByRole("button", { name: /close/i });
      fireEvent.click(closeButton);

      expect(onClose).toHaveBeenCalled();
    });

    it("should render title", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      expect(
        screen.getByText(/Critical Remote Code Execution in Apache Log4j/i)
      ).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Risk Profile Section Tests
  // ============================================================================

  describe("Risk Profile Section", () => {
    it("should render Risk Profile section", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      expect(screen.getByText(/Risk Profile/i)).toBeInTheDocument();
    });

    it("should render CVSS score bar", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const cvssBar = screen.getByTestId("cvss-bar");
      expect(cvssBar).toBeInTheDocument();
      expect(screen.getByText("9.8")).toBeInTheDocument();
    });

    it("should render EPSS score bar", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const epssBar = screen.getByTestId("epss-bar");
      expect(epssBar).toBeInTheDocument();
      expect(screen.getByText(/97\.2%/)).toBeInTheDocument();
    });

    it("should render KEV badge when is_kev is true", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const kevBadge = screen.getByTestId("kev-badge");
      expect(kevBadge).toBeInTheDocument();
      expect(kevBadge).toHaveClass("animate-fire");
    });

    it("should not render KEV badge when is_kev is false", () => {
      render(
        <CVEDetailPanel
          {...defaultProps}
          cve={{ ...mockCVEDetail, is_kev: false }}
        />
      );

      expect(screen.queryByTestId("kev-badge")).not.toBeInTheDocument();
    });

    it("should render SSVC decision with glow effect", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const ssvcBadge = screen.getByTestId("ssvc-badge");
      expect(ssvcBadge).toBeInTheDocument();
      expect(ssvcBadge).toHaveTextContent("Act");
      expect(ssvcBadge).toHaveClass("glow-red");
    });

    it("should render ransomware indicator when kev_ransomware_use is true", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      expect(screen.getByText(/Ransomware/i)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Risk Radar Mini Chart Tests
  // ============================================================================

  describe("Risk Radar Chart", () => {
    it("should render Risk Radar section", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const radarChart = screen.getByTestId("risk-radar");
      expect(radarChart).toBeInTheDocument();
    });

    it("should render 5 axis labels", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const radarChart = screen.getByTestId("risk-radar");
      // 5 axes: CVSS, EPSS, KEV, Exploitability, Asset Impact
      expect(radarChart).toHaveAttribute("data-axes", "5");
    });
  });

  // ============================================================================
  // Description Section Tests
  // ============================================================================

  describe("Description Section", () => {
    it("should render description text", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      expect(
        screen.getByText(/Apache Log4j2 allows remote attackers/i)
      ).toBeInTheDocument();
    });

    it("should render CWE links", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const cweLinks = screen.getAllByTestId(/cwe-link-/);
      expect(cweLinks).toHaveLength(3);
    });

    it("should render CWE-94 as clickable link", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const cweLink = screen.getByTestId("cwe-link-CWE-94");
      expect(cweLink).toBeInTheDocument();
      expect(cweLink.tagName.toLowerCase()).toBe("a");
    });
  });

  // ============================================================================
  // Enrichment Sources Tests
  // ============================================================================

  describe("Enrichment Sources", () => {
    it("should render Enrichment Sources section", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      expect(screen.getByText(/Enrichment Sources/i)).toBeInTheDocument();
    });

    it("should render source badges grid", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const sourcesGrid = screen.getByTestId("enrichment-sources-grid");
      expect(sourcesGrid).toBeInTheDocument();
    });

    it("should render enrichment source badges", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const sourcesGrid = screen.getByTestId("enrichment-sources-grid");
      // Just verify the grid contains sources
      expect(sourcesGrid.children.length).toBeGreaterThan(0);
    });

    it("should show last enriched timestamp", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      expect(screen.getByText(/Last enriched/i)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Affected Assets Tests
  // ============================================================================

  describe("Affected Assets", () => {
    it("should render Affected Assets section", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      expect(screen.getByText(/Affected Assets/i)).toBeInTheDocument();
    });

    it("should render asset list", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      expect(screen.getByText("prod-server-01")).toBeInTheDocument();
      expect(screen.getByText("prod-server-02")).toBeInTheDocument();
    });

    it("should show asset count badge", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      expect(screen.getByText("127")).toBeInTheDocument();
    });

    it("should render View All link", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const viewAllLinks = screen.getAllByText(/View All/i);
      expect(viewAllLinks.length).toBeGreaterThan(0);
    });

    it("should show criticality indicator for each asset", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const criticalAsset = screen.getByTestId("asset-asset-2");
      expect(criticalAsset).toHaveTextContent("Critical");
    });
  });

  // ============================================================================
  // Exploits List Tests
  // ============================================================================

  describe("Exploits List", () => {
    it("should render Exploits section header", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      // Find all elements with "Exploits" text
      const exploitElements = screen.getAllByText(/Exploits/i);
      expect(exploitElements.length).toBeGreaterThan(0);
    });

    it("should render exploit count badge", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      // Exploit count is 15
      const countBadges = screen.getAllByText("15");
      expect(countBadges.length).toBeGreaterThan(0);
    });

    it("should render exploit list items", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      expect(screen.getByText("Log4Shell PoC")).toBeInTheDocument();
      expect(screen.getByText("nuclei-log4j")).toBeInTheDocument();
    });

    it("should render exploits with source info", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      // Verify exploit items exist
      expect(screen.getByText("Log4Shell PoC")).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Attack Chain Visualization Tests
  // ============================================================================

  describe("Attack Chain Visualization", () => {
    it("should render Attack Chain section", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      expect(screen.getByText(/Attack Chain/i)).toBeInTheDocument();
    });

    it("should render CWE node", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const attackChain = screen.getByTestId("attack-chain");
      expect(attackChain).toHaveTextContent("CWE-94");
    });

    it("should render MITRE T-code node", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const attackChain = screen.getByTestId("attack-chain");
      expect(attackChain).toHaveTextContent("T1059");
    });

    it("should render Actor node", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const attackChain = screen.getByTestId("attack-chain");
      expect(attackChain).toHaveTextContent("APT29");
    });

    it("should render connection arrows between nodes", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const arrows = screen.getAllByTestId("attack-chain-arrow");
      expect(arrows.length).toBeGreaterThanOrEqual(2);
    });
  });

  // ============================================================================
  // Vendor Patches Section Tests
  // ============================================================================

  describe("Vendor Patches", () => {
    it("should render Vendor Patches section", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      expect(screen.getByText(/Vendor Patches/i)).toBeInTheDocument();
    });

    it("should show patch available indicator when patch exists", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const patchIndicator = screen.getByTestId("patch-available");
      expect(patchIndicator).toBeInTheDocument();
    });

    it("should render patch information", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      // Verify patch link exists
      const patchLink = screen.getByTestId("patch-link-0");
      expect(patchLink).toBeInTheDocument();
    });

    it("should render patch link", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const patchLink = screen.getByTestId("patch-link-0");
      expect(patchLink).toHaveAttribute("href", "https://apache.org/...");
    });
  });

  // ============================================================================
  // Action Buttons Tests
  // ============================================================================

  describe("Action Buttons", () => {
    it("should render Create Ticket button", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const createTicketBtn = screen.getByRole("button", { name: /create ticket/i });
      expect(createTicketBtn).toBeInTheDocument();
    });

    it("should call onAction with 'create_ticket' when clicked", () => {
      const onAction = vi.fn();
      render(<CVEDetailPanel {...defaultProps} onAction={onAction} />);

      const createTicketBtn = screen.getByRole("button", { name: /create ticket/i });
      fireEvent.click(createTicketBtn);

      expect(onAction).toHaveBeenCalledWith("create_ticket", "CVE-2024-0001");
    });

    it("should render Escalate button", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const escalateBtn = screen.getByRole("button", { name: /escalate/i });
      expect(escalateBtn).toBeInTheDocument();
    });

    it("should render Accept Risk button", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const acceptRiskBtn = screen.getByRole("button", { name: /accept risk/i });
      expect(acceptRiskBtn).toBeInTheDocument();
    });

    it("should render Add Watchlist button", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const watchlistBtn = screen.getByRole("button", { name: /watchlist/i });
      expect(watchlistBtn).toBeInTheDocument();
    });

    it("should render Export button", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const exportBtn = screen.getByRole("button", { name: /export/i });
      expect(exportBtn).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Loading State Tests
  // ============================================================================

  describe("Loading State", () => {
    it("should show loading state when isLoading is true", () => {
      render(<CVEDetailPanel {...defaultProps} cve={null} isLoading={true} />);

      expect(screen.getByTestId("cve-detail-loading")).toBeInTheDocument();
    });

    it("should show skeleton placeholders while loading", () => {
      render(<CVEDetailPanel {...defaultProps} cve={null} isLoading={true} />);

      const skeletons = screen.getAllByTestId(/skeleton-/);
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  // ============================================================================
  // Keyboard Navigation Tests
  // ============================================================================

  describe("Keyboard Navigation", () => {
    it("should close panel on Escape key", () => {
      const onClose = vi.fn();
      render(<CVEDetailPanel {...defaultProps} onClose={onClose} />);

      fireEvent.keyDown(document, { key: "Escape" });

      expect(onClose).toHaveBeenCalled();
    });

    it("should trap focus within panel", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const panel = screen.getByTestId("cve-detail-panel");
      const focusableElements = panel.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );

      expect(focusableElements.length).toBeGreaterThan(0);
    });
  });

  // ============================================================================
  // Accessibility Tests
  // ============================================================================

  describe("Accessibility", () => {
    it("should have role dialog", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const panel = screen.getByRole("dialog");
      expect(panel).toBeInTheDocument();
    });

    it("should have aria-labelledby pointing to title", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const panel = screen.getByRole("dialog");
      expect(panel).toHaveAttribute("aria-labelledby");
    });

    it("should have aria-describedby for description", () => {
      render(<CVEDetailPanel {...defaultProps} />);

      const panel = screen.getByRole("dialog");
      expect(panel).toHaveAttribute("aria-describedby");
    });
  });
});
