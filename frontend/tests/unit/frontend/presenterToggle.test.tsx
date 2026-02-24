/**
 * Unit Tests for Presenter Toggle (UT-012)
 *
 * Requirement: REQ-001-003-003
 * Task: T-030
 *
 * Add a toggle control in the demo control panel that enables/disables
 * auto-UI-actions from the agent.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { PresenterToggle } from "../../../src/components/demo/PresenterToggle";

describe("PresenterToggle", () => {
  it("should render a toggle switch", () => {
    render(<PresenterToggle enabled={true} onToggle={vi.fn()} />);

    const toggle = screen.getByRole("switch");
    expect(toggle).toBeDefined();
  });

  it("should display label text", () => {
    render(<PresenterToggle enabled={true} onToggle={vi.fn()} />);

    expect(screen.getByText("Auto UI Actions")).toBeDefined();
  });

  it("should reflect enabled state as checked", () => {
    render(<PresenterToggle enabled={true} onToggle={vi.fn()} />);

    const toggle = screen.getByRole("switch");
    expect(toggle.getAttribute("aria-checked")).toBe("true");
  });

  it("should reflect disabled state as unchecked", () => {
    render(<PresenterToggle enabled={false} onToggle={vi.fn()} />);

    const toggle = screen.getByRole("switch");
    expect(toggle.getAttribute("aria-checked")).toBe("false");
  });

  it("should call onToggle when clicked", () => {
    const onToggle = vi.fn();
    render(<PresenterToggle enabled={true} onToggle={onToggle} />);

    const toggle = screen.getByRole("switch");
    fireEvent.click(toggle);

    expect(onToggle).toHaveBeenCalledTimes(1);
  });

  it("should pass the new state to onToggle callback", () => {
    const onToggle = vi.fn();
    render(<PresenterToggle enabled={true} onToggle={onToggle} />);

    const toggle = screen.getByRole("switch");
    fireEvent.click(toggle);

    // When enabled=true and clicked, should toggle to false
    expect(onToggle).toHaveBeenCalledWith(false);
  });

  it("should toggle from disabled to enabled", () => {
    const onToggle = vi.fn();
    render(<PresenterToggle enabled={false} onToggle={onToggle} />);

    const toggle = screen.getByRole("switch");
    fireEvent.click(toggle);

    expect(onToggle).toHaveBeenCalledWith(true);
  });

  it("should have proper accessible name", () => {
    render(<PresenterToggle enabled={true} onToggle={vi.fn()} />);

    const toggle = screen.getByRole("switch");
    expect(toggle.getAttribute("aria-label")).toBe("Toggle auto UI actions");
  });

  it("should have data-testid for E2E testing", () => {
    render(<PresenterToggle enabled={true} onToggle={vi.fn()} />);

    expect(screen.getByTestId("presenter-toggle")).toBeDefined();
  });
});
