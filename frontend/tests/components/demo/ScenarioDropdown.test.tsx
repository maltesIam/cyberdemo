/**
 * ScenarioDropdown Component Tests
 *
 * Tests for the scenario selection dropdown including:
 * - Rendering all 6 attack scenarios
 * - Selection behavior
 * - Displaying current scenario
 * - Disabled state during simulation
 *
 * Requirements: REQ-006-001-003
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, within } from "@testing-library/react";
import { ScenarioDropdown } from "../../../src/components/demo/ScenarioDropdown";
import type { AttackScenario } from "../../../src/components/demo/types";

// All 6 attack scenarios
const ALL_SCENARIOS: AttackScenario[] = [
  {
    id: "apt29",
    name: "APT29 (Cozy Bear)",
    description: "Government espionage campaign",
    category: "APT",
    stages: 8,
  },
  {
    id: "fin7",
    name: "FIN7",
    description: "Financial attack campaign",
    category: "Financial",
    stages: 7,
  },
  {
    id: "lazarus",
    name: "Lazarus Group",
    description: "Destructive attack campaign",
    category: "APT",
    stages: 9,
  },
  {
    id: "revil",
    name: "REvil Ransomware",
    description: "Ransomware attack",
    category: "Ransomware",
    stages: 6,
  },
  {
    id: "solarwinds",
    name: "SolarWinds-style",
    description: "Supply chain attack",
    category: "Supply Chain",
    stages: 10,
  },
  {
    id: "insider",
    name: "Insider Threat",
    description: "Internal threat actor",
    category: "Insider",
    stages: 5,
  },
];

describe("ScenarioDropdown", () => {
  describe("Rendering (REQ-006-001-003)", () => {
    it("should render the dropdown with label", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={null}
          onSelect={vi.fn()}
        />
      );

      expect(screen.getByRole("combobox")).toBeInTheDocument();
      // Check for the label element specifically
      expect(screen.getByLabelText(/scenario/i)).toBeInTheDocument();
    });

    it("should display 'Select Scenario' when no scenario is selected", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={null}
          onSelect={vi.fn()}
        />
      );

      expect(screen.getByRole("combobox")).toHaveTextContent(/select scenario/i);
    });

    it("should display selected scenario name", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={ALL_SCENARIOS[0]}
          onSelect={vi.fn()}
        />
      );

      expect(screen.getByRole("combobox")).toHaveTextContent("APT29 (Cozy Bear)");
    });

    it("should render all 6 scenarios in dropdown", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={null}
          onSelect={vi.fn()}
        />
      );

      // Open the dropdown
      fireEvent.click(screen.getByRole("combobox"));

      // Check all scenarios are present
      expect(screen.getByText("APT29 (Cozy Bear)")).toBeInTheDocument();
      expect(screen.getByText("FIN7")).toBeInTheDocument();
      expect(screen.getByText("Lazarus Group")).toBeInTheDocument();
      expect(screen.getByText("REvil Ransomware")).toBeInTheDocument();
      expect(screen.getByText("SolarWinds-style")).toBeInTheDocument();
      expect(screen.getByText("Insider Threat")).toBeInTheDocument();
    });

    it("should show scenario description in dropdown options", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={null}
          onSelect={vi.fn()}
        />
      );

      fireEvent.click(screen.getByRole("combobox"));

      expect(screen.getByText("Government espionage campaign")).toBeInTheDocument();
      expect(screen.getByText("Financial attack campaign")).toBeInTheDocument();
    });

    it("should show stage count for each scenario", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={null}
          onSelect={vi.fn()}
        />
      );

      fireEvent.click(screen.getByRole("combobox"));

      // APT29 has 8 stages
      expect(screen.getByText(/8 stages/i)).toBeInTheDocument();
      // FIN7 has 7 stages
      expect(screen.getByText(/7 stages/i)).toBeInTheDocument();
    });
  });

  describe("Selection Behavior", () => {
    it("should call onSelect when a scenario is clicked", () => {
      const onSelect = vi.fn();
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={null}
          onSelect={onSelect}
        />
      );

      fireEvent.click(screen.getByRole("combobox"));
      fireEvent.click(screen.getByText("FIN7"));

      expect(onSelect).toHaveBeenCalledWith(ALL_SCENARIOS[1]);
    });

    it("should close dropdown after selection", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={null}
          onSelect={vi.fn()}
        />
      );

      fireEvent.click(screen.getByRole("combobox"));
      expect(screen.getByRole("listbox")).toBeInTheDocument();

      fireEvent.click(screen.getByText("FIN7"));

      // Dropdown should close
      expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
    });

    it("should toggle dropdown when clicking the button", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={null}
          onSelect={vi.fn()}
        />
      );

      const button = screen.getByRole("combobox");

      // Initially closed
      expect(screen.queryByRole("listbox")).not.toBeInTheDocument();

      // Open
      fireEvent.click(button);
      expect(screen.getByRole("listbox")).toBeInTheDocument();

      // Close
      fireEvent.click(button);
      expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
    });

    it("should highlight currently selected scenario", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={ALL_SCENARIOS[2]}
          onSelect={vi.fn()}
        />
      );

      fireEvent.click(screen.getByRole("combobox"));

      // Use getAllByRole to find all options, then find the one with Lazarus
      const options = screen.getAllByRole("option");
      const lazarusOption = options.find(opt => opt.textContent?.includes("Lazarus Group"));
      expect(lazarusOption).toHaveAttribute("aria-selected", "true");
    });
  });

  describe("Disabled State", () => {
    it("should be disabled when isDisabled prop is true", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={null}
          onSelect={vi.fn()}
          isDisabled={true}
        />
      );

      const button = screen.getByRole("combobox");
      expect(button).toBeDisabled();
    });

    it("should not open dropdown when disabled", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={null}
          onSelect={vi.fn()}
          isDisabled={true}
        />
      );

      fireEvent.click(screen.getByRole("combobox"));

      expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
    });

    it("should show visual disabled state", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={null}
          onSelect={vi.fn()}
          isDisabled={true}
        />
      );

      const button = screen.getByRole("combobox");
      expect(button).toHaveClass("opacity-50");
    });
  });

  describe("Category Grouping", () => {
    it("should group scenarios by category", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={null}
          onSelect={vi.fn()}
        />
      );

      fireEvent.click(screen.getByRole("combobox"));

      // Check for category headers
      expect(screen.getByText("APT")).toBeInTheDocument();
      expect(screen.getByText("Financial")).toBeInTheDocument();
      expect(screen.getByText("Ransomware")).toBeInTheDocument();
    });
  });

  describe("Keyboard Navigation", () => {
    it("should open dropdown with Enter key", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={null}
          onSelect={vi.fn()}
        />
      );

      const button = screen.getByRole("combobox");
      button.focus();
      fireEvent.keyDown(button, { key: "Enter" });

      expect(screen.getByRole("listbox")).toBeInTheDocument();
    });

    it("should close dropdown with Escape key", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={null}
          onSelect={vi.fn()}
        />
      );

      fireEvent.click(screen.getByRole("combobox"));
      expect(screen.getByRole("listbox")).toBeInTheDocument();

      fireEvent.keyDown(screen.getByRole("listbox"), { key: "Escape" });

      expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
    });

    it("should navigate options with arrow keys", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={null}
          onSelect={vi.fn()}
        />
      );

      fireEvent.click(screen.getByRole("combobox"));
      const listbox = screen.getByRole("listbox");

      fireEvent.keyDown(listbox, { key: "ArrowDown" });

      // First option should be focused
      const options = screen.getAllByRole("option");
      expect(options[0]).toHaveAttribute("data-focused", "true");
    });
  });

  describe("Accessibility", () => {
    it("should have proper ARIA attributes", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={ALL_SCENARIOS[0]}
          onSelect={vi.fn()}
        />
      );

      const combobox = screen.getByRole("combobox");
      expect(combobox).toHaveAttribute("aria-haspopup", "listbox");
      expect(combobox).toHaveAttribute("aria-expanded", "false");

      fireEvent.click(combobox);
      expect(combobox).toHaveAttribute("aria-expanded", "true");
    });

    it("should have accessible label", () => {
      render(
        <ScenarioDropdown
          scenarios={ALL_SCENARIOS}
          selectedScenario={null}
          onSelect={vi.fn()}
        />
      );

      expect(screen.getByRole("combobox")).toHaveAccessibleName(/scenario/i);
    });
  });
});
