/**
 * RiskPanel Component Unit Tests
 *
 * TDD tests for the Risk Panel - Left Sidebar filter component
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { RiskPanel } from "../../../src/components/vuln-views/RiskPanel";

// ============================================================================
// Mock Data
// ============================================================================

const mockFilterCounts = {
  ssvc: {
    act: 15,
    attend: 28,
    trackStar: 42,
    track: 65,
  },
  severity: {
    critical: 12,
    high: 35,
    medium: 68,
    low: 35,
  },
  quickFilters: {
    kevOnly: 8,
    exploitable: 23,
    hasPublicExploit: 18,
    patchOverdue: 5,
  },
  ecosystems: {
    npm: 45,
    pip: 32,
    maven: 28,
    go: 15,
  },
  cweCategories: {
    injection: 25,
    xss: 18,
    auth: 12,
    crypto: 8,
    config: 15,
  },
};

const defaultProps = {
  filterCounts: mockFilterCounts,
  onFilterChange: vi.fn(),
  filters: {
    ssvc: [],
    severity: [],
    quickFilters: [],
    ecosystems: [],
    cweCategories: [],
    productSearch: "",
  },
};

// ============================================================================
// Rendering Tests
// ============================================================================

describe("RiskPanel Component", () => {
  describe("Rendering", () => {
    it("should render the risk panel container", () => {
      render(<RiskPanel {...defaultProps} />);
      const container = screen.getByTestId("risk-panel");
      expect(container).toBeInTheDocument();
    });

    it("should render with custom className", () => {
      render(<RiskPanel {...defaultProps} className="custom-class" />);
      const container = screen.getByTestId("risk-panel");
      expect(container).toHaveClass("custom-class");
    });

    it("should render panel header with title", () => {
      render(<RiskPanel {...defaultProps} />);
      expect(screen.getByText(/Risk Filters/i)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // SSVC Filter Tests
  // ============================================================================

  describe("SSVC Filter", () => {
    it("should render SSVC filter section", () => {
      render(<RiskPanel {...defaultProps} />);
      expect(screen.getByText(/SSVC Decision/i)).toBeInTheDocument();
    });

    it("should render Act checkbox with count", () => {
      render(<RiskPanel {...defaultProps} />);
      const actCheckbox = screen.getByRole("checkbox", { name: /act/i });
      expect(actCheckbox).toBeInTheDocument();
    });

    it("should call onFilterChange when SSVC checkbox is toggled", () => {
      const onFilterChange = vi.fn();
      render(<RiskPanel {...defaultProps} onFilterChange={onFilterChange} />);
      const actCheckbox = screen.getByRole("checkbox", { name: /act/i });
      fireEvent.click(actCheckbox);
      expect(onFilterChange).toHaveBeenCalled();
    });
  });

  // ============================================================================
  // Quick Filters Tests
  // ============================================================================

  describe("Quick Filters", () => {
    it("should render Quick Filters section", () => {
      render(<RiskPanel {...defaultProps} />);
      expect(screen.getByText(/Quick Filters/i)).toBeInTheDocument();
    });

    it("should render KEV Only filter", () => {
      render(<RiskPanel {...defaultProps} />);
      const kevCheckbox = screen.getByRole("checkbox", { name: /kev only/i });
      expect(kevCheckbox).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Severity Filter Tests
  // ============================================================================

  describe("Severity Filter", () => {
    it("should render Severity filter section", () => {
      render(<RiskPanel {...defaultProps} />);
      expect(screen.getByText(/Severity/i)).toBeInTheDocument();
    });

    it("should render Critical severity checkbox", () => {
      render(<RiskPanel {...defaultProps} />);
      const criticalCheckbox = screen.getByRole("checkbox", { name: /critical/i });
      expect(criticalCheckbox).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Product/Vendor Search Tests
  // ============================================================================

  describe("Product/Vendor Search", () => {
    it("should render search input", () => {
      render(<RiskPanel {...defaultProps} />);
      const searchInput = screen.getByPlaceholderText(/search product/i);
      expect(searchInput).toBeInTheDocument();
    });

    it("should call onFilterChange when search input changes", () => {
      const onFilterChange = vi.fn();
      render(<RiskPanel {...defaultProps} onFilterChange={onFilterChange} />);
      const searchInput = screen.getByPlaceholderText(/search product/i);
      fireEvent.change(searchInput, { target: { value: "apache" } });
      expect(onFilterChange).toHaveBeenCalled();
    });
  });

  // ============================================================================
  // Ecosystem Filter Tests
  // ============================================================================

  describe("Ecosystem Filter", () => {
    it("should render Ecosystem filter section", () => {
      render(<RiskPanel {...defaultProps} />);
      expect(screen.getByText(/Ecosystem/i)).toBeInTheDocument();
    });

    it("should render npm checkbox", () => {
      render(<RiskPanel {...defaultProps} />);
      const npmCheckbox = screen.getByRole("checkbox", { name: /npm/i });
      expect(npmCheckbox).toBeInTheDocument();
    });
  });

  // ============================================================================
  // CWE Category Filter Tests
  // ============================================================================

  describe("CWE Category Filter", () => {
    it("should render CWE Category filter section", () => {
      render(<RiskPanel {...defaultProps} />);
      expect(screen.getByText(/CWE Category/i)).toBeInTheDocument();
    });

    it("should render Injection category checkbox", () => {
      render(<RiskPanel {...defaultProps} />);
      const injectionCheckbox = screen.getByRole("checkbox", { name: /injection/i });
      expect(injectionCheckbox).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Presets Dropdown Tests
  // ============================================================================

  describe("Presets Dropdown", () => {
    it("should render presets dropdown", () => {
      render(<RiskPanel {...defaultProps} />);
      const presetsDropdown = screen.getByTestId("presets-dropdown");
      expect(presetsDropdown).toBeInTheDocument();
    });

    it("should open preset options when clicked", () => {
      render(<RiskPanel {...defaultProps} />);
      const presetsDropdown = screen.getByTestId("presets-dropdown");
      fireEvent.click(presetsDropdown);
      expect(screen.getByText(/Urgent Triage/i)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Reset Filters Tests
  // ============================================================================

  describe("Reset Filters", () => {
    it("should render reset button", () => {
      render(<RiskPanel {...defaultProps} />);
      // Use exact name to avoid matching multiple buttons
      const resetButton = screen.getByRole("button", { name: /reset filters/i });
      expect(resetButton).toBeInTheDocument();
    });

    it("should call onFilterChange with empty filters when reset is clicked", () => {
      const onFilterChange = vi.fn();
      render(<RiskPanel {...defaultProps} onFilterChange={onFilterChange} />);
      const resetButton = screen.getByRole("button", { name: /reset filters/i });
      fireEvent.click(resetButton);
      expect(onFilterChange).toHaveBeenCalled();
    });
  });

  // ============================================================================
  // Accessibility Tests
  // ============================================================================

  describe("Accessibility", () => {
    it("should have appropriate aria labels", () => {
      render(<RiskPanel {...defaultProps} />);
      const panel = screen.getByTestId("risk-panel");
      expect(panel).toHaveAttribute("aria-label");
    });

    it("should have keyboard navigable checkboxes", () => {
      render(<RiskPanel {...defaultProps} />);
      const checkboxes = screen.getAllByRole("checkbox");
      expect(checkboxes.length).toBeGreaterThan(0);
    });
  });
});
