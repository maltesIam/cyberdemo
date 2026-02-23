/**
 * useKeyboardShortcuts Hook Tests
 *
 * Tests for keyboard shortcuts hook including:
 * - Space for play/pause toggle
 * - Escape for stop
 * - +/- for speed control
 *
 * Requirements: REQ-006-001-005
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useKeyboardShortcuts } from "../../../src/components/demo/useKeyboardShortcuts";
import type { SpeedMultiplier, PlayState } from "../../../src/components/demo/types";

// Mock keyboard event helper
const createKeyboardEvent = (key: string, options: Partial<KeyboardEvent> = {}) => {
  return new KeyboardEvent("keydown", {
    key,
    bubbles: true,
    ...options,
  });
};

describe("useKeyboardShortcuts", () => {
  let mockCallbacks: {
    onTogglePlayPause: ReturnType<typeof vi.fn>;
    onStop: ReturnType<typeof vi.fn>;
    onSpeedUp: ReturnType<typeof vi.fn>;
    onSpeedDown: ReturnType<typeof vi.fn>;
  };

  beforeEach(() => {
    mockCallbacks = {
      onTogglePlayPause: vi.fn(),
      onStop: vi.fn(),
      onSpeedUp: vi.fn(),
      onSpeedDown: vi.fn(),
    };
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("Space Key - Play/Pause Toggle (REQ-006-001-005)", () => {
    it("should call onTogglePlayPause when Space is pressed", () => {
      renderHook(() =>
        useKeyboardShortcuts({
          ...mockCallbacks,
          isEnabled: true,
        })
      );

      act(() => {
        document.dispatchEvent(createKeyboardEvent(" "));
      });

      expect(mockCallbacks.onTogglePlayPause).toHaveBeenCalledTimes(1);
    });

    it("should not trigger when typing in an input", () => {
      renderHook(() =>
        useKeyboardShortcuts({
          ...mockCallbacks,
          isEnabled: true,
        })
      );

      // Create a mock input element
      const input = document.createElement("input");
      document.body.appendChild(input);
      input.focus();

      act(() => {
        const event = createKeyboardEvent(" ");
        Object.defineProperty(event, "target", { value: input });
        document.dispatchEvent(event);
      });

      expect(mockCallbacks.onTogglePlayPause).not.toHaveBeenCalled();

      document.body.removeChild(input);
    });

    it("should not trigger when disabled", () => {
      renderHook(() =>
        useKeyboardShortcuts({
          ...mockCallbacks,
          isEnabled: false,
        })
      );

      act(() => {
        document.dispatchEvent(createKeyboardEvent(" "));
      });

      expect(mockCallbacks.onTogglePlayPause).not.toHaveBeenCalled();
    });
  });

  describe("Escape Key - Stop (REQ-006-001-005)", () => {
    it("should call onStop when Escape is pressed", () => {
      renderHook(() =>
        useKeyboardShortcuts({
          ...mockCallbacks,
          isEnabled: true,
        })
      );

      act(() => {
        document.dispatchEvent(createKeyboardEvent("Escape"));
      });

      expect(mockCallbacks.onStop).toHaveBeenCalledTimes(1);
    });

    it("should not call onStop when disabled", () => {
      renderHook(() =>
        useKeyboardShortcuts({
          ...mockCallbacks,
          isEnabled: false,
        })
      );

      act(() => {
        document.dispatchEvent(createKeyboardEvent("Escape"));
      });

      expect(mockCallbacks.onStop).not.toHaveBeenCalled();
    });
  });

  describe("Speed Control Keys (REQ-006-001-005)", () => {
    it("should call onSpeedUp when + is pressed", () => {
      renderHook(() =>
        useKeyboardShortcuts({
          ...mockCallbacks,
          isEnabled: true,
        })
      );

      act(() => {
        document.dispatchEvent(createKeyboardEvent("+"));
      });

      expect(mockCallbacks.onSpeedUp).toHaveBeenCalledTimes(1);
    });

    it("should call onSpeedUp when = is pressed (unshifted +)", () => {
      renderHook(() =>
        useKeyboardShortcuts({
          ...mockCallbacks,
          isEnabled: true,
        })
      );

      act(() => {
        document.dispatchEvent(createKeyboardEvent("="));
      });

      expect(mockCallbacks.onSpeedUp).toHaveBeenCalledTimes(1);
    });

    it("should call onSpeedDown when - is pressed", () => {
      renderHook(() =>
        useKeyboardShortcuts({
          ...mockCallbacks,
          isEnabled: true,
        })
      );

      act(() => {
        document.dispatchEvent(createKeyboardEvent("-"));
      });

      expect(mockCallbacks.onSpeedDown).toHaveBeenCalledTimes(1);
    });

    it("should not trigger speed change when disabled", () => {
      renderHook(() =>
        useKeyboardShortcuts({
          ...mockCallbacks,
          isEnabled: false,
        })
      );

      act(() => {
        document.dispatchEvent(createKeyboardEvent("+"));
        document.dispatchEvent(createKeyboardEvent("-"));
      });

      expect(mockCallbacks.onSpeedUp).not.toHaveBeenCalled();
      expect(mockCallbacks.onSpeedDown).not.toHaveBeenCalled();
    });
  });

  describe("Cleanup", () => {
    it("should remove event listener on unmount", () => {
      const removeEventListenerSpy = vi.spyOn(document, "removeEventListener");

      const { unmount } = renderHook(() =>
        useKeyboardShortcuts({
          ...mockCallbacks,
          isEnabled: true,
        })
      );

      unmount();

      expect(removeEventListenerSpy).toHaveBeenCalledWith("keydown", expect.any(Function));
    });
  });

  describe("Event Prevention", () => {
    it("should prevent default for Space key", () => {
      renderHook(() =>
        useKeyboardShortcuts({
          ...mockCallbacks,
          isEnabled: true,
        })
      );

      const event = createKeyboardEvent(" ");
      const preventDefaultSpy = vi.spyOn(event, "preventDefault");

      act(() => {
        document.dispatchEvent(event);
      });

      expect(preventDefaultSpy).toHaveBeenCalled();
    });
  });

  describe("Callback Independence", () => {
    it("should work with only some callbacks provided", () => {
      renderHook(() =>
        useKeyboardShortcuts({
          onTogglePlayPause: mockCallbacks.onTogglePlayPause,
          isEnabled: true,
        })
      );

      act(() => {
        document.dispatchEvent(createKeyboardEvent(" "));
        document.dispatchEvent(createKeyboardEvent("Escape")); // No callback for this
      });

      expect(mockCallbacks.onTogglePlayPause).toHaveBeenCalledTimes(1);
      // Should not throw even without onStop callback
    });
  });

  describe("Dynamic Enable/Disable", () => {
    it("should respond to isEnabled changes", () => {
      const { rerender } = renderHook(
        ({ isEnabled }) =>
          useKeyboardShortcuts({
            ...mockCallbacks,
            isEnabled,
          }),
        { initialProps: { isEnabled: true } }
      );

      act(() => {
        document.dispatchEvent(createKeyboardEvent(" "));
      });
      expect(mockCallbacks.onTogglePlayPause).toHaveBeenCalledTimes(1);

      // Disable
      rerender({ isEnabled: false });

      act(() => {
        document.dispatchEvent(createKeyboardEvent(" "));
      });
      expect(mockCallbacks.onTogglePlayPause).toHaveBeenCalledTimes(1); // Still 1

      // Re-enable
      rerender({ isEnabled: true });

      act(() => {
        document.dispatchEvent(createKeyboardEvent(" "));
      });
      expect(mockCallbacks.onTogglePlayPause).toHaveBeenCalledTimes(2);
    });
  });
});
