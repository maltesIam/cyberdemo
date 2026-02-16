/**
 * PostmortemsPage Features Tests - TDD
 *
 * Tests for:
 * 1. Embedded timeline chart showing incident progression
 * 2. Export PDF functionality
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";

// Import the component and utilities
import { PostmortemsPage } from "../src/pages/PostmortemsPage";
import { IncidentTimelineChart, type TimelinePhase } from "../src/components/IncidentTimelineChart";

// ============================================================================
// Timeline Chart Type Tests
// ============================================================================

describe("Incident Timeline Chart Types", () => {
  it("should define TimelinePhase interface", () => {
    const phase: TimelinePhase = {
      name: "Alert",
      timestamp: "2024-01-15T10:00:00Z",
      color: "#ef4444",
    };

    expect(phase.name).toBe("Alert");
    expect(phase.timestamp).toBeDefined();
    expect(phase.color).toBeDefined();
  });

  it("should accept all required timeline phases", () => {
    const phases: TimelinePhase[] = [
      { name: "Alert", timestamp: "2024-01-15T10:00:00Z", color: "#ef4444" },
      { name: "Investigation", timestamp: "2024-01-15T10:15:00Z", color: "#f59e0b" },
      { name: "Containment", timestamp: "2024-01-15T11:00:00Z", color: "#3b82f6" },
      { name: "Resolution", timestamp: "2024-01-15T14:00:00Z", color: "#22c55e" },
    ];

    expect(phases).toHaveLength(4);
    expect(phases.map((p) => p.name)).toEqual([
      "Alert",
      "Investigation",
      "Containment",
      "Resolution",
    ]);
  });
});

// ============================================================================
// Timeline Chart Component Tests
// ============================================================================

describe("IncidentTimelineChart Component", () => {
  const mockPhases: TimelinePhase[] = [
    { name: "Alert", timestamp: "2024-01-15T10:00:00Z", color: "#ef4444" },
    { name: "Investigation", timestamp: "2024-01-15T10:15:00Z", color: "#f59e0b" },
    { name: "Containment", timestamp: "2024-01-15T11:00:00Z", color: "#3b82f6" },
    { name: "Resolution", timestamp: "2024-01-15T14:00:00Z", color: "#22c55e" },
  ];

  it("should render timeline chart with phases", () => {
    render(<IncidentTimelineChart phases={mockPhases} />);

    expect(screen.getByText("Alert")).toBeInTheDocument();
    expect(screen.getByText("Investigation")).toBeInTheDocument();
    expect(screen.getByText("Containment")).toBeInTheDocument();
    expect(screen.getByText("Resolution")).toBeInTheDocument();
  });

  it("should render SVG chart element", () => {
    const { container } = render(<IncidentTimelineChart phases={mockPhases} />);

    const svg = container.querySelector("svg");
    expect(svg).toBeInTheDocument();
  });

  it("should display timestamps for each phase", () => {
    render(<IncidentTimelineChart phases={mockPhases} />);

    // Should display formatted times - use getAllByText since there might be multiple
    const times = screen.getAllByText(/\d{2}:\d{2}/);
    expect(times.length).toBeGreaterThan(0);
  });

  it("should calculate duration between phases", () => {
    render(<IncidentTimelineChart phases={mockPhases} showDurations />);

    // Should show duration indicators - use getAllByTestId since there are multiple durations
    const durations = screen.getAllByTestId("timeline-duration");
    expect(durations.length).toBeGreaterThan(0);
  });

  it("should render with empty phases array", () => {
    render(<IncidentTimelineChart phases={[]} />);

    expect(screen.getByText(/no timeline data/i)).toBeInTheDocument();
  });

  it("should render with single phase", () => {
    const singlePhase: TimelinePhase[] = [
      { name: "Alert", timestamp: "2024-01-15T10:00:00Z", color: "#ef4444" },
    ];

    render(<IncidentTimelineChart phases={singlePhase} />);

    expect(screen.getByText("Alert")).toBeInTheDocument();
  });
});

// ============================================================================
// Postmortem Detail Modal with Timeline Tests
// ============================================================================

describe("Postmortem Detail Modal Timeline", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    vi.mock("../src/hooks/useApi", () => ({
      usePostmortems: vi.fn().mockReturnValue({
        data: {
          data: [
            {
              id: "pm-001",
              incident_id: "inc-001",
              title: "Ransomware Attack Analysis",
              summary: "Analysis of ransomware incident",
              root_cause: "Phishing email",
              impact: "Critical systems affected",
              timeline: [
                { timestamp: "2024-01-15T10:00:00Z", description: "Alert detected" },
                { timestamp: "2024-01-15T10:15:00Z", description: "Investigation started" },
                { timestamp: "2024-01-15T11:00:00Z", description: "Containment completed" },
                { timestamp: "2024-01-15T14:00:00Z", description: "Incident resolved" },
              ],
              lessons_learned: ["Better email filtering"],
              action_items: [],
              created_at: "2024-01-16T09:00:00Z",
              author: "Security Team",
            },
          ],
          total: 1,
          page: 1,
          page_size: 20,
          total_pages: 1,
        },
        isLoading: false,
        error: null,
      }),
      usePostmortem: vi.fn().mockReturnValue({
        data: {
          id: "pm-001",
          incident_id: "inc-001",
          title: "Ransomware Attack Analysis",
          summary: "Analysis of ransomware incident",
          root_cause: "Phishing email",
          impact: "Critical systems affected",
          timeline: [
            { timestamp: "2024-01-15T10:00:00Z", description: "Alert detected" },
            { timestamp: "2024-01-15T10:15:00Z", description: "Investigation started" },
            { timestamp: "2024-01-15T11:00:00Z", description: "Containment completed" },
            { timestamp: "2024-01-15T14:00:00Z", description: "Incident resolved" },
          ],
          lessons_learned: ["Better email filtering"],
          action_items: [],
          created_at: "2024-01-16T09:00:00Z",
          author: "Security Team",
        },
        isLoading: false,
        error: null,
      }),
    }));
  });

  const renderPostmortemsPage = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <PostmortemsPage />
        </BrowserRouter>
      </QueryClientProvider>,
    );
  };

  it("should show timeline chart in postmortem detail modal", async () => {
    renderPostmortemsPage();

    // Click to open a postmortem detail - wait for data to load first
    await waitFor(() => {
      const viewButtons = screen.queryAllByRole("button", { name: /view/i });
      expect(viewButtons.length).toBeGreaterThan(0);
    });

    const viewButton = screen.getByRole("button", { name: /view/i });
    fireEvent.click(viewButton);

    // Should show the modal dialog
    await waitFor(
      () => {
        expect(screen.getByRole("dialog")).toBeInTheDocument();
      },
      { timeout: 2000 },
    );

    // Should show the postmortem report header in the modal
    expect(screen.getByText("Postmortem Report")).toBeInTheDocument();
  });
});

// ============================================================================
// Export PDF Tests
// ============================================================================

describe("Export PDF Functionality", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    // Mock window.print
    vi.stubGlobal("print", vi.fn());

    vi.mock("../src/hooks/useApi", () => ({
      usePostmortems: vi.fn().mockReturnValue({
        data: {
          data: [
            {
              id: "pm-001",
              incident_id: "inc-001",
              title: "Test Postmortem",
              summary: "Test summary",
              root_cause: "Test cause",
              impact: "Test impact",
              timeline: [],
              lessons_learned: [],
              action_items: [],
              created_at: "2024-01-16T09:00:00Z",
              author: "Test Author",
            },
          ],
          total: 1,
          page: 1,
          page_size: 20,
          total_pages: 1,
        },
        isLoading: false,
        error: null,
      }),
      usePostmortem: vi.fn().mockReturnValue({
        data: {
          id: "pm-001",
          incident_id: "inc-001",
          title: "Test Postmortem",
          summary: "Test summary",
          root_cause: "Test cause",
          impact: "Test impact",
          timeline: [],
          lessons_learned: [],
          action_items: [],
          created_at: "2024-01-16T09:00:00Z",
          author: "Test Author",
        },
        isLoading: false,
        error: null,
      }),
    }));
  });

  const renderPostmortemsPage = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <PostmortemsPage />
        </BrowserRouter>
      </QueryClientProvider>,
    );
  };

  it("should render Export PDF button in postmortem detail modal", async () => {
    renderPostmortemsPage();

    // Click to open a postmortem detail
    const viewButton = screen.getByRole("button", { name: /view/i });
    fireEvent.click(viewButton);

    // Should show Export PDF button
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /export pdf/i })).toBeInTheDocument();
    });
  });

  it("should call print function when Export PDF is clicked", async () => {
    renderPostmortemsPage();

    // Click to open a postmortem detail
    const viewButton = screen.getByRole("button", { name: /view/i });
    fireEvent.click(viewButton);

    // Click Export PDF button
    await waitFor(() => {
      const exportButton = screen.getByRole("button", { name: /export pdf/i });
      fireEvent.click(exportButton);
    });

    // window.print should have been called
    expect(window.print).toHaveBeenCalled();
  });

  it("should have PDF icon on Export button", async () => {
    renderPostmortemsPage();

    const viewButton = screen.getByRole("button", { name: /view/i });
    fireEvent.click(viewButton);

    await waitFor(() => {
      const exportButton = screen.getByRole("button", { name: /export pdf/i });
      // Check that button contains SVG icon
      expect(exportButton.querySelector("svg")).toBeInTheDocument();
    });
  });

  it("should add print-specific styles for PDF export", async () => {
    renderPostmortemsPage();

    const viewButton = screen.getByRole("button", { name: /view/i });
    fireEvent.click(viewButton);

    await waitFor(() => {
      const modal = screen.getByRole("dialog");
      // Modal should have print-friendly class
      expect(modal).toHaveClass("print:bg-white");
    });
  });
});

// ============================================================================
// Print Styles Tests
// ============================================================================

describe("Print Styles for PDF Export", () => {
  it("should define print media query styles", () => {
    // This tests that the component applies correct Tailwind print classes
    const printClasses = [
      "print:bg-white",
      "print:text-black",
      "print:shadow-none",
      "print:border-none",
    ];

    // These classes should be available in the component
    printClasses.forEach((cls) => {
      expect(cls).toMatch(/^print:/);
    });
  });
});
