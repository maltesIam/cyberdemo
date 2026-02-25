/**
 * ScenarioDropdown Component
 *
 * A dropdown for selecting attack scenarios with category grouping,
 * descriptions, and stage counts.
 *
 * Requirements:
 * - REQ-006-001-003: Scenario selection dropdown with all 6 attack scenarios
 */

import { useState, useRef, useEffect, useCallback, useMemo } from "react";
import type { ScenarioDropdownProps, AttackScenario } from "./types";

/** Group scenarios by category */
const groupByCategory = (scenarios: AttackScenario[]): Map<string, AttackScenario[]> => {
  const groups = new Map<string, AttackScenario[]>();

  scenarios.forEach(scenario => {
    const existing = groups.get(scenario.category) || [];
    groups.set(scenario.category, [...existing, scenario]);
  });

  return groups;
};

/** Chevron icon for dropdown */
const ChevronIcon = ({ isOpen }: { isOpen: boolean }) => (
  <svg
    className={`w-4 h-4 transition-transform ${isOpen ? "rotate-180" : ""}`}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M19 9l-7 7-7-7"
    />
  </svg>
);

export function ScenarioDropdown({
  scenarios,
  selectedScenario,
  onSelect,
  isDisabled = false,
}: ScenarioDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Group scenarios by category
  const groupedScenarios = useMemo(() => groupByCategory(scenarios), [scenarios]);

  // Flatten scenarios for keyboard navigation
  const flatScenarios = useMemo(() => scenarios, [scenarios]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  // Toggle dropdown
  const toggleDropdown = useCallback(() => {
    if (!isDisabled) {
      setIsOpen((prev) => !prev);
      setFocusedIndex(-1);
    }
  }, [isDisabled]);

  // Handle selection
  const handleSelect = useCallback(
    (scenario: AttackScenario) => {
      onSelect(scenario);
      setIsOpen(false);
      buttonRef.current?.focus();
    },
    [onSelect]
  );

  // Handle keyboard navigation
  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      if (isDisabled) return;

      switch (event.key) {
        case "Enter":
        case " ":
          event.preventDefault();
          if (!isOpen) {
            setIsOpen(true);
          } else if (focusedIndex >= 0 && focusedIndex < flatScenarios.length) {
            handleSelect(flatScenarios[focusedIndex]);
          }
          break;
        case "Escape":
          event.preventDefault();
          setIsOpen(false);
          buttonRef.current?.focus();
          break;
        case "ArrowDown":
          event.preventDefault();
          if (!isOpen) {
            setIsOpen(true);
          } else {
            setFocusedIndex((prev) =>
              prev < flatScenarios.length - 1 ? prev + 1 : prev
            );
          }
          break;
        case "ArrowUp":
          event.preventDefault();
          if (isOpen) {
            setFocusedIndex((prev) => (prev > 0 ? prev - 1 : prev));
          }
          break;
        case "Home":
          event.preventDefault();
          if (isOpen) {
            setFocusedIndex(0);
          }
          break;
        case "End":
          event.preventDefault();
          if (isOpen) {
            setFocusedIndex(flatScenarios.length - 1);
          }
          break;
      }
    },
    [isDisabled, isOpen, focusedIndex, flatScenarios, handleSelect]
  );

  // Render scenario option
  const renderOption = (scenario: AttackScenario, index: number) => {
    const isSelected = selectedScenario?.id === scenario.id;
    const isFocused = focusedIndex === index;
    const globalIndex = flatScenarios.findIndex((s) => s.id === scenario.id);

    return (
      <div
        key={scenario.id}
        role="option"
        aria-selected={isSelected}
        data-focused={globalIndex === focusedIndex ? "true" : "false"}
        className={`px-3 py-2 cursor-pointer transition-colors ${
          isSelected
            ? "bg-cyan-600/30 text-cyan-300"
            : isFocused
            ? "bg-tertiary"
            : "hover:bg-tertiary"
        }`}
        onClick={() => handleSelect(scenario)}
        onMouseEnter={() => setFocusedIndex(globalIndex)}
      >
        <div className="flex items-center justify-between">
          <div className="flex-1 min-w-0">
            <div className="font-medium text-sm text-primary truncate">
              {scenario.name}
            </div>
            <div className="text-xs text-secondary truncate">
              {scenario.description}
            </div>
          </div>
          <div className="ml-2 flex-shrink-0 text-xs text-tertiary">
            {scenario.stages} stages
          </div>
        </div>
        {isSelected && (
          <svg
            className="absolute right-3 w-4 h-4 text-cyan-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        )}
      </div>
    );
  };

  return (
    <div ref={dropdownRef} className="relative" data-testid="scenario-dropdown">
      {/* Label */}
      <label
        id="scenario-label"
        className="block text-xs text-secondary mb-1"
      >
        Scenario
      </label>

      {/* Dropdown Button */}
      <button
        ref={buttonRef}
        type="button"
        role="combobox"
        aria-labelledby="scenario-label"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-controls="scenario-listbox"
        disabled={isDisabled}
        className={`w-full flex items-center justify-between px-3 py-2 bg-tertiary border border-primary rounded-lg text-sm transition-colors ${
          isDisabled
            ? "opacity-50 cursor-not-allowed"
            : "hover:border-gray-500 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
        }`}
        onClick={toggleDropdown}
        onKeyDown={handleKeyDown}
      >
        <span className={selectedScenario ? "text-primary" : "text-secondary"}>
          {selectedScenario?.name || "Select Scenario"}
        </span>
        <ChevronIcon isOpen={isOpen} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          id="scenario-listbox"
          role="listbox"
          aria-labelledby="scenario-label"
          className="absolute z-50 w-full mt-1 bg-secondary border border-primary rounded-lg shadow-lg max-h-80 overflow-y-auto"
          onKeyDown={handleKeyDown}
        >
          {Array.from(groupedScenarios.entries()).map(([category, categoryScenarios]) => (
            <div key={category}>
              {/* Category Header */}
              <div className="px-3 py-1.5 text-xs font-semibold text-tertiary bg-primary/50 sticky top-0">
                {category}
              </div>
              {/* Category Options */}
              {categoryScenarios.map((scenario) =>
                renderOption(scenario, flatScenarios.findIndex(s => s.id === scenario.id))
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
