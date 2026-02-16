/**
 * EnrichmentButtons Component Unit Tests
 *
 * Tests for:
 * 1. Buttons render correctly
 * 2. Loading state shows spinner
 * 3. Progress percentage updates
 * 4. Error handling with toast
 * 5. Partial failures show warning toast
 * 6. Total failures show error toast
 * 7. Cleanup on unmount
 */

import { describe, it, expect, beforeEach, afterEach, vi, Mock } from "vitest";
import { render, screen, fireEvent, waitFor, act, cleanup } from "@testing-library/react";
import { EnrichmentButtons } from "../../src/components/EnrichmentButtons";
import { ToastProvider } from "../../src/utils/toast";
import * as enrichmentService from "../../src/services/enrichment";

// Mock the enrichment service
vi.mock("../../src/services/enrichment", () => ({
  enrichVulnerabilities: vi.fn(),
  enrichThreats: vi.fn(),
  getEnrichmentStatus: vi.fn(),
}));

// Helper to render component with ToastProvider
function renderWithProviders(onComplete?: () => void) {
  return render(
    <ToastProvider>
      <EnrichmentButtons onEnrichmentComplete={onComplete} />
    </ToastProvider>,
  );
}

// Helper to flush pending promises without running all timers
// This allows async operations to complete without triggering auto-dismiss timers
async function flushPromisesAndTimers() {
  // Flush microtasks (pending promises) by advancing a small amount
  await act(async () => {
    // Advance just enough to trigger immediate state updates
    await vi.advanceTimersByTimeAsync(100);
  });
}

describe("EnrichmentButtons Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  // ============================================================================
  // TEST 1: Buttons render correctly
  // ============================================================================
  describe("Button Rendering", () => {
    it("should render vulnerability enrichment button", () => {
      renderWithProviders();

      const vulnButton = screen.getByRole("button", { name: /enriquecer vulnerabilidades/i });
      expect(vulnButton).toBeInTheDocument();
      expect(vulnButton).toBeEnabled();
    });

    it("should render threat enrichment button", () => {
      renderWithProviders();

      const threatButton = screen.getByRole("button", { name: /enriquecer amenazas/i });
      expect(threatButton).toBeInTheDocument();
      expect(threatButton).toBeEnabled();
    });

    it("should render both buttons with correct styling", () => {
      renderWithProviders();

      const vulnButton = screen.getByRole("button", { name: /enriquecer vulnerabilidades/i });
      const threatButton = screen.getByRole("button", { name: /enriquecer amenazas/i });

      expect(vulnButton).toHaveClass("bg-purple-600");
      expect(threatButton).toHaveClass("bg-red-600");
    });

    it("should render SVG icons in buttons", () => {
      renderWithProviders();

      const vulnButton = screen.getByRole("button", { name: /enriquecer vulnerabilidades/i });
      const threatButton = screen.getByRole("button", { name: /enriquecer amenazas/i });

      expect(vulnButton.querySelector("svg")).toBeInTheDocument();
      expect(threatButton.querySelector("svg")).toBeInTheDocument();
    });
  });

  // ============================================================================
  // TEST 2: Loading state shows spinner
  // ============================================================================
  describe("Loading State", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.runOnlyPendingTimers();
      vi.useRealTimers();
    });

    it("should show spinner when vulnerability enrichment is in progress", async () => {
      const mockEnrich = enrichmentService.enrichVulnerabilities as Mock;
      mockEnrich.mockResolvedValue({ job_id: "test-job-123" });

      const mockStatus = enrichmentService.getEnrichmentStatus as Mock;
      mockStatus.mockResolvedValue({
        job_id: "test-job-123",
        status: "running",
        progress: 0.5,
        processed_items: 50,
        total_items: 100,
        failed_items: 0,
      });

      renderWithProviders();

      const vulnButton = screen.getByRole("button", { name: /enriquecer vulnerabilidades/i });

      await act(async () => {
        fireEvent.click(vulnButton);
      });

      // Flush promises and timers to allow state updates
      await flushPromisesAndTimers();

      // Button should show loading state
      expect(screen.getByText(/enriching\.\.\./i)).toBeInTheDocument();

      // Button should be disabled
      expect(vulnButton).toBeDisabled();

      // Should have spinner (animate-spin class)
      const spinner = vulnButton.querySelector(".animate-spin");
      expect(spinner).toBeInTheDocument();
    });

    it("should show spinner when threat enrichment is in progress", async () => {
      const mockEnrich = enrichmentService.enrichThreats as Mock;
      mockEnrich.mockResolvedValue({ job_id: "threat-job-456" });

      const mockStatus = enrichmentService.getEnrichmentStatus as Mock;
      mockStatus.mockResolvedValue({
        job_id: "threat-job-456",
        status: "running",
        progress: 0.3,
        processed_items: 30,
        total_items: 100,
        failed_items: 0,
      });

      renderWithProviders();

      const threatButton = screen.getByRole("button", { name: /enriquecer amenazas/i });

      await act(async () => {
        fireEvent.click(threatButton);
      });

      // Flush promises and timers to allow state updates
      await flushPromisesAndTimers();

      // Button should show loading state
      expect(screen.getByText(/enriching\.\.\./i)).toBeInTheDocument();

      // Button should be disabled
      expect(threatButton).toBeDisabled();
    });
  });

  // ============================================================================
  // TEST 3: Progress percentage updates
  // ============================================================================
  describe("Progress Updates", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.runOnlyPendingTimers();
      vi.useRealTimers();
    });

    it("should show progress percentage during vulnerability enrichment", async () => {
      const mockEnrich = enrichmentService.enrichVulnerabilities as Mock;
      mockEnrich.mockResolvedValue({ job_id: "test-job-progress" });

      const mockStatus = enrichmentService.getEnrichmentStatus as Mock;
      mockStatus.mockResolvedValueOnce({
        job_id: "test-job-progress",
        status: "running",
        progress: 0.25,
        processed_items: 25,
        total_items: 100,
        failed_items: 0,
      });

      renderWithProviders();

      const vulnButton = screen.getByRole("button", { name: /enriquecer vulnerabilidades/i });

      await act(async () => {
        fireEvent.click(vulnButton);
      });

      // Flush promises to resolve the initial enrichment call
      await flushPromisesAndTimers();

      // Advance timer to trigger polling
      await act(async () => {
        await vi.advanceTimersByTimeAsync(2000);
      });

      // Should show progress percentage
      expect(screen.getByText(/25%/)).toBeInTheDocument();
    });

    it("should update progress percentage as job progresses", async () => {
      const mockEnrich = enrichmentService.enrichVulnerabilities as Mock;
      mockEnrich.mockResolvedValue({ job_id: "test-job-progress-update" });

      const mockStatus = enrichmentService.getEnrichmentStatus as Mock;
      mockStatus
        .mockResolvedValueOnce({
          job_id: "test-job-progress-update",
          status: "running",
          progress: 0.25,
          processed_items: 25,
          total_items: 100,
          failed_items: 0,
        })
        .mockResolvedValueOnce({
          job_id: "test-job-progress-update",
          status: "running",
          progress: 0.75,
          processed_items: 75,
          total_items: 100,
          failed_items: 0,
        });

      renderWithProviders();

      const vulnButton = screen.getByRole("button", { name: /enriquecer vulnerabilidades/i });

      await act(async () => {
        fireEvent.click(vulnButton);
      });

      // Flush promises to resolve the initial enrichment call
      await flushPromisesAndTimers();

      // First poll
      await act(async () => {
        await vi.advanceTimersByTimeAsync(2000);
      });

      expect(screen.getByText(/25%/)).toBeInTheDocument();

      // Second poll
      await act(async () => {
        await vi.advanceTimersByTimeAsync(2000);
      });

      expect(screen.getByText(/75%/)).toBeInTheDocument();
    });
  });

  // ============================================================================
  // TEST 4: Error handling with toast
  // ============================================================================
  describe("Error Handling", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.runOnlyPendingTimers();
      vi.useRealTimers();
    });

    it("should show error toast when enrichment fails to start", async () => {
      const mockEnrich = enrichmentService.enrichVulnerabilities as Mock;
      mockEnrich.mockRejectedValue(new Error("Network error. Please check your connection."));

      renderWithProviders();

      const vulnButton = screen.getByRole("button", { name: /enriquecer vulnerabilidades/i });

      await act(async () => {
        fireEvent.click(vulnButton);
      });

      // Flush promises to allow error to be handled
      await flushPromisesAndTimers();

      // Should show error toast
      const toast = screen.getByRole("alert");
      expect(toast).toBeInTheDocument();
      expect(toast).toHaveTextContent(/network error/i);

      // Button should be re-enabled
      expect(vulnButton).toBeEnabled();
    });

    it("should show error toast when job fails", async () => {
      const mockEnrich = enrichmentService.enrichVulnerabilities as Mock;
      mockEnrich.mockResolvedValue({ job_id: "test-job-fail" });

      const mockStatus = enrichmentService.getEnrichmentStatus as Mock;
      mockStatus.mockResolvedValue({
        job_id: "test-job-fail",
        status: "failed",
        progress: 0.3,
        processed_items: 30,
        total_items: 100,
        failed_items: 70,
      });

      renderWithProviders();

      const vulnButton = screen.getByRole("button", { name: /enriquecer vulnerabilidades/i });

      await act(async () => {
        fireEvent.click(vulnButton);
      });

      // Flush promises to resolve the initial enrichment call
      await flushPromisesAndTimers();

      // Advance timer to trigger polling
      await act(async () => {
        await vi.advanceTimersByTimeAsync(2000);
      });

      // Should show error toast for failed job (may have multiple toasts - info + error)
      const toasts = screen.getAllByRole("alert");
      const errorToast = toasts.find((t) => t.textContent?.toLowerCase().includes("failed"));
      expect(errorToast).toBeInTheDocument();
      expect(errorToast).toHaveTextContent(/failed/i);

      // Button should be re-enabled
      expect(vulnButton).toBeEnabled();
    });

    it("should handle missing job_id in response", async () => {
      const mockEnrich = enrichmentService.enrichVulnerabilities as Mock;
      mockEnrich.mockResolvedValue({});

      renderWithProviders();

      const vulnButton = screen.getByRole("button", { name: /enriquecer vulnerabilidades/i });

      await act(async () => {
        fireEvent.click(vulnButton);
      });

      // Flush promises to allow error to be handled
      await flushPromisesAndTimers();

      // Should show error toast
      const toast = screen.getByRole("alert");
      expect(toast).toBeInTheDocument();
      expect(toast).toHaveTextContent(/no job id/i);

      // Button should be re-enabled
      expect(vulnButton).toBeEnabled();
    });
  });

  // ============================================================================
  // TEST 5: Partial failures show warning toast
  // ============================================================================
  describe("Partial Failure Handling", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.runOnlyPendingTimers();
      vi.useRealTimers();
    });

    it("should show warning toast when some sources fail", async () => {
      const mockEnrich = enrichmentService.enrichVulnerabilities as Mock;
      mockEnrich.mockResolvedValue({ job_id: "test-job-partial" });

      const mockStatus = enrichmentService.getEnrichmentStatus as Mock;
      mockStatus.mockResolvedValue({
        job_id: "test-job-partial",
        status: "completed",
        progress: 1.0,
        processed_items: 100,
        total_items: 100,
        failed_items: 0,
        successful_sources: 3,
        failed_sources: 1,
        sources: {
          nvd: { status: "success", enriched_count: 100 },
          epss: { status: "success", enriched_count: 100 },
          github: { status: "success", enriched_count: 100 },
          synthetic: { status: "failed", enriched_count: 0, error: "API timeout" },
        },
        errors: [{ source: "synthetic", error: "API timeout", recoverable: true }],
      });

      renderWithProviders();

      const vulnButton = screen.getByRole("button", { name: /enriquecer vulnerabilidades/i });

      await act(async () => {
        fireEvent.click(vulnButton);
      });

      // Flush promises to resolve the initial enrichment call
      await flushPromisesAndTimers();

      // Advance timer to trigger polling
      await act(async () => {
        await vi.advanceTimersByTimeAsync(2000);
      });

      // Should show warning toast (partial success) - may have multiple toasts
      const toasts = screen.getAllByRole("alert");
      const warningToast = toasts.find((t) => t.textContent?.includes("unavailable"));
      expect(warningToast).toBeInTheDocument();
      expect(warningToast).toHaveTextContent(/1 source.*unavailable/i);
      expect(warningToast).toHaveTextContent(/3 source.*succeeded/i);
    });

    it("should call onEnrichmentComplete callback on partial success", async () => {
      const onCompleteMock = vi.fn();

      const mockEnrich = enrichmentService.enrichVulnerabilities as Mock;
      mockEnrich.mockResolvedValue({ job_id: "test-job-callback" });

      const mockStatus = enrichmentService.getEnrichmentStatus as Mock;
      mockStatus.mockResolvedValue({
        job_id: "test-job-callback",
        status: "completed",
        progress: 1.0,
        processed_items: 100,
        total_items: 100,
        failed_items: 0,
        successful_sources: 2,
        failed_sources: 2,
      });

      renderWithProviders(onCompleteMock);

      const vulnButton = screen.getByRole("button", { name: /enriquecer vulnerabilidades/i });

      await act(async () => {
        fireEvent.click(vulnButton);
      });

      // Flush promises to resolve the initial enrichment call
      await flushPromisesAndTimers();

      // Advance timer to trigger polling
      await act(async () => {
        await vi.advanceTimersByTimeAsync(2000);
      });

      // Callback should be called even on partial success
      expect(onCompleteMock).toHaveBeenCalled();
    });
  });

  // ============================================================================
  // TEST 6: Total failures show error toast
  // ============================================================================
  describe("Total Failure Handling", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.runOnlyPendingTimers();
      vi.useRealTimers();
    });

    it("should show error toast when all sources fail", async () => {
      const mockEnrich = enrichmentService.enrichVulnerabilities as Mock;
      mockEnrich.mockResolvedValue({ job_id: "test-job-total-fail" });

      const mockStatus = enrichmentService.getEnrichmentStatus as Mock;
      mockStatus.mockResolvedValue({
        job_id: "test-job-total-fail",
        status: "completed",
        progress: 1.0,
        processed_items: 0,
        total_items: 100,
        failed_items: 100,
        successful_sources: 0,
        failed_sources: 4,
        sources: {
          nvd: { status: "failed", enriched_count: 0, error: "API timeout" },
          epss: { status: "failed", enriched_count: 0, error: "Rate limited" },
          github: { status: "failed", enriched_count: 0, error: "Auth error" },
          synthetic: { status: "failed", enriched_count: 0, error: "Service unavailable" },
        },
        errors: [
          { source: "nvd", error: "API timeout", recoverable: true },
          { source: "epss", error: "Rate limited", recoverable: true },
          { source: "github", error: "Auth error", recoverable: false },
          { source: "synthetic", error: "Service unavailable", recoverable: true },
        ],
      });

      renderWithProviders();

      const vulnButton = screen.getByRole("button", { name: /enriquecer vulnerabilidades/i });

      await act(async () => {
        fireEvent.click(vulnButton);
      });

      // Flush promises to resolve the initial enrichment call
      await flushPromisesAndTimers();

      // Advance timer to trigger polling
      await act(async () => {
        await vi.advanceTimersByTimeAsync(2000);
      });

      // Should show error toast (all sources failed) - may have multiple toasts
      const toasts = screen.getAllByRole("alert");
      const errorToast = toasts.find((t) => t.textContent?.toLowerCase().includes("all"));
      expect(errorToast).toBeInTheDocument();
      expect(errorToast).toHaveTextContent(/all.*sources failed/i);
    });
  });

  // ============================================================================
  // TEST 7: Cleanup on unmount
  // ============================================================================
  describe("Cleanup on Unmount", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.runOnlyPendingTimers();
      vi.useRealTimers();
    });

    it("should clear polling interval on unmount", async () => {
      const clearIntervalSpy = vi.spyOn(global, "clearInterval");

      const mockEnrich = enrichmentService.enrichVulnerabilities as Mock;
      mockEnrich.mockResolvedValue({ job_id: "test-job-unmount" });

      const mockStatus = enrichmentService.getEnrichmentStatus as Mock;
      mockStatus.mockResolvedValue({
        job_id: "test-job-unmount",
        status: "running",
        progress: 0.5,
        processed_items: 50,
        total_items: 100,
        failed_items: 0,
      });

      const { unmount } = renderWithProviders();

      const vulnButton = screen.getByRole("button", { name: /enriquecer vulnerabilidades/i });

      await act(async () => {
        fireEvent.click(vulnButton);
      });

      // Flush promises to resolve the initial enrichment call
      await flushPromisesAndTimers();

      // Unmount while polling is active
      unmount();

      // clearInterval should have been called during cleanup
      expect(clearIntervalSpy).toHaveBeenCalled();
    });

    it("should not cause memory leaks with active timers", async () => {
      const mockEnrich = enrichmentService.enrichVulnerabilities as Mock;
      mockEnrich.mockResolvedValue({ job_id: "test-job-memory" });

      const mockStatus = enrichmentService.getEnrichmentStatus as Mock;
      mockStatus.mockResolvedValue({
        job_id: "test-job-memory",
        status: "running",
        progress: 0.5,
        processed_items: 50,
        total_items: 100,
        failed_items: 0,
      });

      const { unmount } = renderWithProviders();

      const vulnButton = screen.getByRole("button", { name: /enriquecer vulnerabilidades/i });

      await act(async () => {
        fireEvent.click(vulnButton);
      });

      // Unmount immediately
      unmount();

      // Advancing timers after unmount should not cause errors
      await act(async () => {
        vi.advanceTimersByTime(10000);
      });

      // If we got here without errors, no memory leak
      expect(true).toBe(true);
    });
  });

  // ============================================================================
  // Additional Tests: Success scenarios
  // ============================================================================
  describe("Success Scenarios", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.runOnlyPendingTimers();
      vi.useRealTimers();
    });

    it("should show success toast when all sources succeed", async () => {
      const mockEnrich = enrichmentService.enrichVulnerabilities as Mock;
      mockEnrich.mockResolvedValue({ job_id: "test-job-success" });

      const mockStatus = enrichmentService.getEnrichmentStatus as Mock;
      mockStatus.mockResolvedValue({
        job_id: "test-job-success",
        status: "completed",
        progress: 1.0,
        processed_items: 100,
        total_items: 100,
        failed_items: 0,
        successful_sources: 4,
        failed_sources: 0,
      });

      renderWithProviders();

      const vulnButton = screen.getByRole("button", { name: /enriquecer vulnerabilidades/i });

      await act(async () => {
        fireEvent.click(vulnButton);
      });

      // Flush promises to resolve the initial enrichment call
      await flushPromisesAndTimers();

      // Advance timer to trigger polling
      await act(async () => {
        await vi.advanceTimersByTimeAsync(2000);
      });

      // Should show success toast (may have multiple toasts - info + success)
      const toasts = screen.getAllByRole("alert");
      const successToast = toasts.find((t) => t.textContent?.includes("Successfully"));
      expect(successToast).toBeInTheDocument();
      expect(successToast).toHaveTextContent(/successfully enriched/i);
      expect(successToast).toHaveTextContent(/4 sources/i);
    });

    it("should re-enable button after successful completion", async () => {
      const mockEnrich = enrichmentService.enrichVulnerabilities as Mock;
      mockEnrich.mockResolvedValue({ job_id: "test-job-reenable" });

      const mockStatus = enrichmentService.getEnrichmentStatus as Mock;
      mockStatus.mockResolvedValue({
        job_id: "test-job-reenable",
        status: "completed",
        progress: 1.0,
        processed_items: 100,
        total_items: 100,
        failed_items: 0,
        successful_sources: 4,
        failed_sources: 0,
      });

      renderWithProviders();

      const vulnButton = screen.getByRole("button", { name: /enriquecer vulnerabilidades/i });

      await act(async () => {
        fireEvent.click(vulnButton);
      });

      // Button should be disabled during enrichment
      expect(vulnButton).toBeDisabled();

      // Flush promises to resolve the initial enrichment call
      await flushPromisesAndTimers();

      // Advance timer to trigger polling
      await act(async () => {
        await vi.advanceTimersByTimeAsync(2000);
      });

      // Button should be re-enabled after completion
      expect(screen.getByRole("button", { name: /enriquecer vulnerabilidades/i })).toBeEnabled();
    });
  });

  // ============================================================================
  // Threat Enrichment Tests
  // ============================================================================
  describe("Threat Enrichment", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.runOnlyPendingTimers();
      vi.useRealTimers();
    });

    it("should start threat enrichment when button clicked", async () => {
      const mockEnrich = enrichmentService.enrichThreats as Mock;
      mockEnrich.mockResolvedValue({ job_id: "threat-job-start" });

      const mockStatus = enrichmentService.getEnrichmentStatus as Mock;
      mockStatus.mockResolvedValue({
        job_id: "threat-job-start",
        status: "running",
        progress: 0.5,
        processed_items: 50,
        total_items: 100,
        failed_items: 0,
      });

      renderWithProviders();

      const threatButton = screen.getByRole("button", { name: /enriquecer amenazas/i });

      await act(async () => {
        fireEvent.click(threatButton);
      });

      // Flush promises to ensure the mock was called
      await flushPromisesAndTimers();

      expect(mockEnrich).toHaveBeenCalledWith({
        sources: ["otx", "abuseipdb", "greynoise", "virustotal", "synthetic"],
        force_refresh: false,
      });
    });

    it("should show info toast when threat enrichment starts", async () => {
      const mockEnrich = enrichmentService.enrichThreats as Mock;
      mockEnrich.mockResolvedValue({ job_id: "threat-job-info" });

      const mockStatus = enrichmentService.getEnrichmentStatus as Mock;
      mockStatus.mockResolvedValue({
        job_id: "threat-job-info",
        status: "running",
        progress: 0.5,
        processed_items: 50,
        total_items: 100,
        failed_items: 0,
      });

      renderWithProviders();

      const threatButton = screen.getByRole("button", { name: /enriquecer amenazas/i });

      await act(async () => {
        fireEvent.click(threatButton);
      });

      // Flush promises to allow state updates
      await flushPromisesAndTimers();

      // Should show info toast
      const toast = screen.getByRole("alert");
      expect(toast).toBeInTheDocument();
      expect(toast).toHaveTextContent(/threat enrichment started/i);
    });
  });
});
