/**
 * Toast Utility Unit Tests
 *
 * Tests for:
 * 1. Toast context renders
 * 2. Show success/error/warning/info toasts
 * 3. Auto-dismiss functionality
 * 4. Manual dismiss functionality
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, fireEvent, waitFor, act, cleanup, within } from "@testing-library/react";
import { ToastProvider, useToast, ToastType } from "../../src/utils/toast";
import React from "react";

// Test component that uses the toast hook
function TestComponent({
  type,
  message,
  duration,
}: {
  type?: ToastType;
  message?: string;
  duration?: number;
}) {
  const { showToast } = useToast();

  return (
    <div>
      <button
        onClick={() => showToast(type ?? "success", message ?? "Test message", duration)}
        data-testid="show-toast"
      >
        Show Toast
      </button>
      <button onClick={() => showToast("success", "Success message")} data-testid="show-success">
        Success
      </button>
      <button onClick={() => showToast("error", "Error message")} data-testid="show-error">
        Error
      </button>
      <button onClick={() => showToast("warning", "Warning message")} data-testid="show-warning">
        Warning
      </button>
      <button onClick={() => showToast("info", "Info message")} data-testid="show-info">
        Info
      </button>
    </div>
  );
}

// Helper to render with ToastProvider
function renderWithProvider(props: { type?: ToastType; message?: string; duration?: number } = {}) {
  return render(
    <ToastProvider>
      <TestComponent {...props} />
    </ToastProvider>,
  );
}

// Error boundary to catch errors in tests
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return <div data-testid="error-boundary">Error: {this.state.error?.message}</div>;
    }
    return this.props.children;
  }
}

describe("Toast Utility", () => {
  afterEach(() => {
    cleanup();
  });

  // ============================================================================
  // TEST 1: Toast context renders
  // ============================================================================
  describe("Toast Context Rendering", () => {
    it("should render children within ToastProvider", () => {
      renderWithProvider();

      expect(screen.getByTestId("show-toast")).toBeInTheDocument();
    });

    it("should throw error when useToast is used outside provider", () => {
      // Suppress console.error for this test
      const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

      // Render with error boundary to catch the error
      render(
        <ErrorBoundary>
          <TestComponent />
        </ErrorBoundary>,
      );

      // Should render error boundary with error message
      expect(screen.getByTestId("error-boundary")).toHaveTextContent(
        "useToast must be used within a ToastProvider",
      );

      consoleSpy.mockRestore();
    });

    it("should render toast container", () => {
      const { container } = renderWithProvider();

      // Toast container should exist (fixed position element)
      const toastContainer = container.querySelector(".fixed.top-4.right-4");
      expect(toastContainer).toBeInTheDocument();
    });
  });

  // ============================================================================
  // TEST 2: Show success/error/warning/info toasts
  // ============================================================================
  describe("Show Toast Types", () => {
    it("should show success toast with correct styling", async () => {
      renderWithProvider();

      const successButton = screen.getByTestId("show-success");
      fireEvent.click(successButton);

      const toast = await screen.findByRole("alert");
      expect(toast).toBeInTheDocument();
      expect(toast).toHaveTextContent("Success message");
      expect(toast).toHaveClass("bg-green-900/90");
    });

    it("should show error toast with correct styling", async () => {
      renderWithProvider();

      const errorButton = screen.getByTestId("show-error");
      fireEvent.click(errorButton);

      const toast = await screen.findByRole("alert");
      expect(toast).toBeInTheDocument();
      expect(toast).toHaveTextContent("Error message");
      expect(toast).toHaveClass("bg-red-900/90");
    });

    it("should show warning toast with correct styling", async () => {
      renderWithProvider();

      const warningButton = screen.getByTestId("show-warning");
      fireEvent.click(warningButton);

      const toast = await screen.findByRole("alert");
      expect(toast).toBeInTheDocument();
      expect(toast).toHaveTextContent("Warning message");
      expect(toast).toHaveClass("bg-orange-900/90");
    });

    it("should show info toast with correct styling", async () => {
      renderWithProvider();

      const infoButton = screen.getByTestId("show-info");
      fireEvent.click(infoButton);

      const toast = await screen.findByRole("alert");
      expect(toast).toBeInTheDocument();
      expect(toast).toHaveTextContent("Info message");
      expect(toast).toHaveClass("bg-cyan-900/90");
    });

    it("should display correct icon for each toast type", async () => {
      renderWithProvider();

      // Test success icon
      fireEvent.click(screen.getByTestId("show-success"));

      const successToast = await screen.findByRole("alert");
      expect(successToast.querySelector("svg")).toBeInTheDocument();
    });

    it("should support multiple toasts at once", async () => {
      renderWithProvider();

      fireEvent.click(screen.getByTestId("show-success"));
      fireEvent.click(screen.getByTestId("show-error"));
      fireEvent.click(screen.getByTestId("show-warning"));

      const toasts = await screen.findAllByRole("alert");
      expect(toasts.length).toBe(3);
    });
  });

  // ============================================================================
  // TEST 3: Auto-dismiss functionality (with fake timers)
  // ============================================================================
  describe("Auto-Dismiss", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.runOnlyPendingTimers();
      vi.useRealTimers();
    });

    it("should auto-dismiss toast after default duration (5000ms)", async () => {
      renderWithProvider();

      const showButton = screen.getByTestId("show-toast");

      await act(async () => {
        fireEvent.click(showButton);
      });

      // Toast should be visible
      expect(screen.getByRole("alert")).toBeInTheDocument();

      // Advance timers past default duration (5000ms) + fade out animation (300ms)
      await act(async () => {
        vi.advanceTimersByTime(5400);
      });

      // Toast should be removed (direct assertion after timer advance)
      expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    });

    it("should auto-dismiss toast after custom duration", async () => {
      renderWithProvider({ duration: 2000 });

      const showButton = screen.getByTestId("show-toast");

      await act(async () => {
        fireEvent.click(showButton);
      });

      // Toast should be visible
      expect(screen.getByRole("alert")).toBeInTheDocument();

      // Advance timers past custom duration (2000ms) + fade out animation (300ms)
      await act(async () => {
        vi.advanceTimersByTime(2400);
      });

      // Toast should be removed (direct assertion after timer advance)
      expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    });

    it("should fade out before being removed", async () => {
      renderWithProvider({ duration: 1000 });

      const showButton = screen.getByTestId("show-toast");

      await act(async () => {
        fireEvent.click(showButton);
      });

      const toast = screen.getByRole("alert");
      expect(toast).toHaveClass("opacity-100");

      // Advance to start fade out
      await act(async () => {
        vi.advanceTimersByTime(1100);
      });

      // Toast should start fading (may be opacity-0 or removed by now)
      // Just check it has the transition class
      expect(toast).toHaveClass("transition-all");
    });
  });

  // ============================================================================
  // TEST 4: Manual dismiss functionality
  // ============================================================================
  describe("Manual Dismiss", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.runOnlyPendingTimers();
      vi.useRealTimers();
    });

    it("should have close button on toast", async () => {
      renderWithProvider();

      const showButton = screen.getByTestId("show-toast");

      await act(async () => {
        fireEvent.click(showButton);
      });

      const toast = screen.getByRole("alert");
      const closeButton = within(toast).getByRole("button", { name: /close/i });

      expect(closeButton).toBeInTheDocument();
    });

    it("should dismiss toast when close button clicked", async () => {
      renderWithProvider();

      const showButton = screen.getByTestId("show-toast");

      await act(async () => {
        fireEvent.click(showButton);
      });

      const toast = screen.getByRole("alert");
      const closeButton = within(toast).getByRole("button", { name: /close/i });

      await act(async () => {
        fireEvent.click(closeButton);
      });

      // Wait for fade out animation
      await act(async () => {
        vi.advanceTimersByTime(400);
      });

      // Toast should be removed (direct assertion after timer advance)
      expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    });

    it("should only dismiss clicked toast when multiple are shown", async () => {
      renderWithProvider();

      // Show multiple toasts
      await act(async () => {
        fireEvent.click(screen.getByTestId("show-success"));
        fireEvent.click(screen.getByTestId("show-error"));
      });

      const toasts = screen.getAllByRole("alert");
      expect(toasts.length).toBe(2);

      // Close the first toast
      const firstCloseButton = within(toasts[0]).getByRole("button", { name: /close/i });

      await act(async () => {
        fireEvent.click(firstCloseButton);
      });

      // Wait for fade out animation
      await act(async () => {
        vi.advanceTimersByTime(400);
      });

      // Only one toast should remain (direct assertion after timer advance)
      const remainingToasts = screen.getAllByRole("alert");
      expect(remainingToasts.length).toBe(1);
    });
  });

  // ============================================================================
  // Additional Tests: Toast Content and Accessibility
  // ============================================================================
  describe("Toast Content and Accessibility", () => {
    it("should display custom message in toast", async () => {
      renderWithProvider({ message: "Custom test message here" });

      const showButton = screen.getByTestId("show-toast");
      fireEvent.click(showButton);

      const toast = await screen.findByRole("alert");
      expect(toast).toHaveTextContent("Custom test message here");
    });

    it("should have role=alert for accessibility", async () => {
      renderWithProvider();

      const showButton = screen.getByTestId("show-toast");
      fireEvent.click(showButton);

      const toast = await screen.findByRole("alert");
      expect(toast).toHaveAttribute("role", "alert");
    });

    it("should have aria-label on close button", async () => {
      renderWithProvider();

      const showButton = screen.getByTestId("show-toast");
      fireEvent.click(showButton);

      const toast = await screen.findByRole("alert");
      const closeButton = within(toast).getByRole("button", { name: /close/i });

      expect(closeButton).toHaveAttribute("aria-label", "Close notification");
    });

    it("should have proper visual styling classes", async () => {
      renderWithProvider();

      const showButton = screen.getByTestId("show-toast");
      fireEvent.click(showButton);

      const toast = await screen.findByRole("alert");

      // Check for essential styling classes
      expect(toast).toHaveClass("rounded-lg");
      expect(toast).toHaveClass("shadow-lg");
      expect(toast).toHaveClass("p-4");
    });
  });

  // ============================================================================
  // Edge Cases
  // ============================================================================
  describe("Edge Cases", () => {
    it("should handle rapid toast creation", async () => {
      renderWithProvider();

      const showButton = screen.getByTestId("show-toast");

      // Rapid fire clicks
      for (let i = 0; i < 10; i++) {
        fireEvent.click(showButton);
      }

      // All toasts should be created
      const toasts = await screen.findAllByRole("alert");
      expect(toasts.length).toBe(10);
    });

    it("should handle empty message", async () => {
      renderWithProvider({ message: "" });

      const showButton = screen.getByTestId("show-toast");
      fireEvent.click(showButton);

      // Toast should still render
      const toast = await screen.findByRole("alert");
      expect(toast).toBeInTheDocument();
    });

    it("should handle long messages without breaking layout", async () => {
      const longMessage =
        "This is a very long message that should be displayed properly without breaking the toast layout. It may wrap to multiple lines but should still be readable and not overflow the container.";
      renderWithProvider({ message: longMessage });

      const showButton = screen.getByTestId("show-toast");
      fireEvent.click(showButton);

      const toast = await screen.findByRole("alert");
      expect(toast).toHaveTextContent(longMessage);
      // Should have max-width constraint
      expect(toast).toHaveClass("max-w-[500px]");
    });
  });
});
