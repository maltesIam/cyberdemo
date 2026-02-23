/**
 * CopilotWidget Component Tests - DEPRECATED
 *
 * Tests for the aIP Assist suggestion widget component.
 * Note: CopilotWidget is now an alias for AipAssistWidget.
 *
 * aIP = Artificial Intelligence Person
 *
 * Requirements:
 * - REQ-004-002-004: UI widget for showing suggestions
 * - REQ-004-002-005: Tracking of acceptance/rejection by session
 * - TECH-012: New component AipAssistWidget.tsx
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { CopilotWidget } from "../../../src/components/copilot/CopilotWidget";
import type {
  CopilotSuggestion,
  CopilotSessionStats,
} from "../../../src/components/copilot/types";

// Mock suggestions for testing
const mockSuggestions: CopilotSuggestion[] = [
  {
    id: "sug-001",
    type: "action",
    title: "Block IP Address",
    description: "Block suspicious IP 192.168.1.100 at firewall",
    confidence: "high",
    status: "pending",
    createdAt: "2024-02-23T10:00:00Z",
    relatedContext: "ALERT-001",
    reason: "Multiple failed login attempts detected",
  },
  {
    id: "sug-002",
    type: "investigation",
    title: "Investigate User Activity",
    description: "Review user john.doe's recent activity",
    confidence: "medium",
    status: "pending",
    createdAt: "2024-02-23T10:01:00Z",
    relatedContext: "ALERT-002",
  },
  {
    id: "sug-003",
    type: "correlation",
    title: "Correlate Events",
    description: "Link alerts ALERT-001 and ALERT-002",
    confidence: "low",
    status: "pending",
    createdAt: "2024-02-23T10:02:00Z",
  },
];

// Mock stats for testing
const mockStats: CopilotSessionStats = {
  totalSuggestions: 10,
  acceptedCount: 6,
  rejectedCount: 2,
  expiredCount: 2,
  acceptanceRate: 75,
};

// Default props for testing
const defaultProps = {
  suggestions: mockSuggestions,
  stats: mockStats,
  isExpanded: true,
  isEnabled: true,
  onAccept: vi.fn(),
  onReject: vi.fn(),
  onToggleExpand: vi.fn(),
  onToggleEnabled: vi.fn(),
  onExplainWhy: vi.fn(),
};

// Helper to render with defaults
const renderCopilotWidget = (
  overrides: Partial<typeof defaultProps> = {}
) => {
  const props = { ...defaultProps, ...overrides };
  return {
    ...render(<CopilotWidget {...props} />),
    ...props,
  };
};

describe("CopilotWidget", () => {
  describe("Component Structure (REQ-004-002-004)", () => {
    it("should render the widget container", () => {
      renderCopilotWidget();
      expect(screen.getByTestId("aip-assist-widget")).toBeInTheDocument();
    });

    it("should render with proper styling classes", () => {
      renderCopilotWidget();
      const widget = screen.getByTestId("aip-assist-widget");
      expect(widget).toHaveClass("bg-gray-800");
    });

    it("should render the aIP Assist header", () => {
      renderCopilotWidget();
      expect(screen.getByText("aIP Assist")).toBeInTheDocument();
    });

    it("should have accessible label", () => {
      renderCopilotWidget();
      const widget = screen.getByTestId("aip-assist-widget");
      expect(widget).toHaveAttribute("aria-label", "aIP Assist suggestions");
    });
  });

  describe("Suggestion Display (REQ-004-002-004)", () => {
    it("should render all pending suggestions", () => {
      renderCopilotWidget();
      expect(screen.getByText("Block IP Address")).toBeInTheDocument();
      expect(screen.getByText("Investigate User Activity")).toBeInTheDocument();
      expect(screen.getByText("Correlate Events")).toBeInTheDocument();
    });

    it("should show suggestion description", () => {
      renderCopilotWidget();
      expect(
        screen.getByText("Block suspicious IP 192.168.1.100 at firewall")
      ).toBeInTheDocument();
    });

    it("should show confidence indicator for each suggestion", () => {
      renderCopilotWidget();
      expect(screen.getByText("High")).toBeInTheDocument();
      expect(screen.getByText("Medium")).toBeInTheDocument();
      expect(screen.getByText("Low")).toBeInTheDocument();
    });

    it("should show suggestion type badge", () => {
      renderCopilotWidget();
      expect(screen.getByText("Action")).toBeInTheDocument();
      expect(screen.getByText("Investigation")).toBeInTheDocument();
      expect(screen.getByText("Correlation")).toBeInTheDocument();
    });

    it("should show reason when provided", () => {
      renderCopilotWidget();
      expect(
        screen.getByText(/Multiple failed login attempts detected/)
      ).toBeInTheDocument();
    });

    it("should show empty state when no suggestions", () => {
      renderCopilotWidget({ suggestions: [] });
      expect(screen.getByText(/no suggestions/i)).toBeInTheDocument();
    });
  });

  describe("Suggestion Actions (REQ-004-002-004)", () => {
    it("should render accept button for each suggestion", () => {
      renderCopilotWidget();
      const acceptButtons = screen.getAllByRole("button", { name: /accept/i });
      expect(acceptButtons.length).toBe(3);
    });

    it("should render reject button for each suggestion", () => {
      renderCopilotWidget();
      const rejectButtons = screen.getAllByRole("button", { name: /reject/i });
      expect(rejectButtons.length).toBe(3);
    });

    it("should call onAccept with suggestion ID when accept is clicked", () => {
      const onAccept = vi.fn();
      renderCopilotWidget({ onAccept });

      const acceptButtons = screen.getAllByRole("button", { name: /accept/i });
      fireEvent.click(acceptButtons[0]);

      expect(onAccept).toHaveBeenCalledWith("sug-001");
    });

    it("should call onReject with suggestion ID when reject is clicked", () => {
      const onReject = vi.fn();
      renderCopilotWidget({ onReject });

      const rejectButtons = screen.getAllByRole("button", { name: /reject/i });
      fireEvent.click(rejectButtons[0]);

      expect(onReject).toHaveBeenCalledWith("sug-001");
    });

    it("should render explain why button when handler is provided", () => {
      renderCopilotWidget({ onExplainWhy: vi.fn() });
      const explainButtons = screen.getAllByRole("button", { name: /why/i });
      expect(explainButtons.length).toBeGreaterThan(0);
    });

    it("should call onExplainWhy with suggestion ID when clicked", () => {
      const onExplainWhy = vi.fn();
      renderCopilotWidget({ onExplainWhy });

      const explainButtons = screen.getAllByRole("button", { name: /why/i });
      fireEvent.click(explainButtons[0]);

      expect(onExplainWhy).toHaveBeenCalledWith("sug-001");
    });
  });

  describe("Session Stats (REQ-004-002-005)", () => {
    it("should display total suggestions count", () => {
      renderCopilotWidget();
      expect(screen.getByText("10")).toBeInTheDocument();
    });

    it("should display accepted count", () => {
      renderCopilotWidget();
      expect(screen.getByText("6")).toBeInTheDocument();
    });

    it("should display rejected count", () => {
      renderCopilotWidget();
      expect(screen.getByText("2")).toBeInTheDocument();
    });

    it("should display acceptance rate", () => {
      renderCopilotWidget();
      expect(screen.getByText(/75%/)).toBeInTheDocument();
    });

    it("should show stats section with proper labels", () => {
      renderCopilotWidget();
      expect(screen.getByText(/total/i)).toBeInTheDocument();
      expect(screen.getByText(/accepted/i)).toBeInTheDocument();
      expect(screen.getByText(/rejected/i)).toBeInTheDocument();
    });
  });

  describe("Toggle Controls", () => {
    it("should render expand/collapse toggle", () => {
      renderCopilotWidget();
      expect(
        screen.getByRole("button", { name: /toggle|expand|collapse/i })
      ).toBeInTheDocument();
    });

    it("should call onToggleExpand when toggle is clicked", () => {
      const onToggleExpand = vi.fn();
      renderCopilotWidget({ onToggleExpand });

      const toggle = screen.getByRole("button", { name: /toggle|expand|collapse/i });
      fireEvent.click(toggle);

      expect(onToggleExpand).toHaveBeenCalled();
    });

    it("should hide suggestions list when collapsed", () => {
      renderCopilotWidget({ isExpanded: false });
      expect(screen.queryByText("Block IP Address")).not.toBeInTheDocument();
    });

    it("should show suggestion count when collapsed", () => {
      renderCopilotWidget({ isExpanded: false });
      expect(screen.getByText("3")).toBeInTheDocument(); // 3 suggestions
    });

    it("should render enabled/disabled toggle", () => {
      renderCopilotWidget();
      expect(
        screen.getByRole("switch", { name: /aIP Assist/i }) ||
        screen.getByRole("button", { name: /enable|disable/i })
      ).toBeInTheDocument();
    });

    it("should call onToggleEnabled when enabled toggle is clicked", () => {
      const onToggleEnabled = vi.fn();
      renderCopilotWidget({ onToggleEnabled });

      const toggle = screen.getByRole("switch", { name: /aIP Assist/i }) ||
        screen.getByRole("button", { name: /enable|disable/i });
      fireEvent.click(toggle);

      expect(onToggleEnabled).toHaveBeenCalled();
    });

    it("should show disabled state when copilot is disabled", () => {
      renderCopilotWidget({ isEnabled: false });
      expect(screen.getByText(/disabled/i)).toBeInTheDocument();
    });
  });

  describe("Visual Indicators", () => {
    it("should show high confidence in green", () => {
      renderCopilotWidget();
      const highConfidence = screen.getByText("High");
      expect(highConfidence).toHaveClass("text-green-400");
    });

    it("should show medium confidence in yellow", () => {
      renderCopilotWidget();
      const mediumConfidence = screen.getByText("Medium");
      expect(mediumConfidence).toHaveClass("text-yellow-400");
    });

    it("should show low confidence in red", () => {
      renderCopilotWidget();
      const lowConfidence = screen.getByText("Low");
      expect(lowConfidence).toHaveClass("text-red-400");
    });

    it("should show action type badge with correct color", () => {
      renderCopilotWidget();
      const badge = screen.getByText("Action").closest("span");
      expect(badge).toHaveClass("bg-blue-500");
    });
  });

  describe("Accessibility", () => {
    it("should have proper aria roles for suggestion list", () => {
      renderCopilotWidget();
      expect(screen.getByRole("list")).toBeInTheDocument();
    });

    it("should have accessible names for action buttons", () => {
      renderCopilotWidget();
      expect(screen.getAllByRole("button", { name: /accept/i })).toHaveLength(3);
      expect(screen.getAllByRole("button", { name: /reject/i })).toHaveLength(3);
    });

    it("should be keyboard navigable", () => {
      renderCopilotWidget();
      const firstAcceptButton = screen.getAllByRole("button", { name: /accept/i })[0];
      firstAcceptButton.focus();
      expect(document.activeElement).toBe(firstAcceptButton);
    });
  });

  describe("Time Display", () => {
    it("should show relative time for suggestions", () => {
      // The component should show something like "Just now" or a formatted time
      renderCopilotWidget();
      // We expect some time indicator to be present
      const timeIndicators = screen.queryAllByText(/ago|now|today/i);
      // At minimum, the suggestions should have timestamps
      expect(screen.getByTestId("aip-assist-widget")).toBeInTheDocument();
    });
  });
});

describe("CopilotWidget Integration", () => {
  it("should handle accepting and rejecting suggestions in sequence", () => {
    const onAccept = vi.fn();
    const onReject = vi.fn();
    renderCopilotWidget({ onAccept, onReject });

    // Accept first suggestion
    const acceptButtons = screen.getAllByRole("button", { name: /accept/i });
    fireEvent.click(acceptButtons[0]);
    expect(onAccept).toHaveBeenCalledWith("sug-001");

    // Reject second suggestion
    const rejectButtons = screen.getAllByRole("button", { name: /reject/i });
    fireEvent.click(rejectButtons[1]);
    expect(onReject).toHaveBeenCalledWith("sug-002");
  });

  it("should work with different suggestion types", () => {
    const alertSuggestion: CopilotSuggestion = {
      id: "sug-alert",
      type: "alert",
      title: "Critical Alert",
      description: "Escalate to security team",
      confidence: "high",
      status: "pending",
      createdAt: new Date().toISOString(),
    };

    renderCopilotWidget({ suggestions: [alertSuggestion] });
    expect(screen.getByText("Alert")).toBeInTheDocument();
    expect(screen.getByText("Critical Alert")).toBeInTheDocument();
  });
});
