/**
 * LayerToggle Component
 *
 * Toggle controls for enabling/disabling attack surface visualization layers.
 * Each layer has a distinct color and can be toggled independently.
 */

import { useMemo } from "react";
import clsx from "clsx";
import type { LayerType, LayerState, LayerConfig } from "./types";
import { LAYER_COLORS, LAYER_RENDER_ORDER } from "./types";

interface LayerToggleProps {
  layers: LayerState[];
  onToggle: (layerId: LayerType) => void;
  onOpacityChange?: (layerId: LayerType, opacity: number) => void;
  compact?: boolean;
  className?: string;
}

// SVG Icons for each layer type
function LayerIcon({ type, className }: { type: LayerConfig["icon"]; className?: string }) {
  const baseClass = clsx("w-4 h-4", className);

  switch (type) {
    case "shield":
      return (
        <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
          />
        </svg>
      );
    case "alert":
      return (
        <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      );
    case "incident":
      return (
        <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z"
          />
        </svg>
      );
    case "vulnerability":
      return (
        <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      );
    case "threat":
      return (
        <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
          />
        </svg>
      );
    case "lock":
      return (
        <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
          />
        </svg>
      );
    case "network":
      return (
        <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
          />
        </svg>
      );
    default:
      return null;
  }
}

// Single layer toggle button
function LayerButton({
  config,
  state,
  onToggle,
  compact,
}: {
  config: LayerConfig;
  state: LayerState;
  onToggle: () => void;
  compact?: boolean;
}) {
  const isEnabled = state.enabled;

  return (
    <button
      onClick={onToggle}
      className={clsx(
        "flex items-center gap-2 rounded-lg border transition-all duration-200",
        compact ? "px-2 py-1.5" : "px-3 py-2",
        isEnabled
          ? "border-transparent shadow-md"
          : "border-primary bg-secondary text-secondary hover:bg-tertiary hover:border-gray-500",
      )}
      style={
        isEnabled
          ? {
              backgroundColor: `${config.colorBase}20`,
              borderColor: config.colorBase,
              color: config.colorLight,
            }
          : undefined
      }
      title={config.description}
    >
      <span
        className={clsx(
          "flex items-center justify-center rounded",
          compact ? "w-5 h-5" : "w-6 h-6",
        )}
        style={
          isEnabled
            ? { backgroundColor: `${config.colorBase}40` }
            : { backgroundColor: "rgb(55 65 81)" }
        }
      >
        <LayerIcon type={config.icon} />
      </span>
      <span className={clsx("font-medium", compact ? "text-xs" : "text-sm")}>{config.label}</span>
      {isEnabled && (
        <span
          className={clsx(
            "flex items-center justify-center rounded-full",
            compact ? "w-4 h-4" : "w-5 h-5",
          )}
          style={{ backgroundColor: config.colorBase }}
        >
          <svg
            className={clsx(compact ? "w-2.5 h-2.5" : "w-3 h-3")}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clipRule="evenodd"
            />
          </svg>
        </span>
      )}
    </button>
  );
}

// Layer legend indicator (small colored dot)
function LayerLegend({ layers }: { layers: LayerState[] }) {
  const enabledLayers = useMemo(() => layers.filter((l) => l.enabled), [layers]);

  if (enabledLayers.length === 0) return null;

  return (
    <div className="flex items-center gap-1.5 ml-3 pl-3 border-l border-primary">
      <span className="text-xs text-tertiary">Active:</span>
      <div className="flex items-center gap-1">
        {enabledLayers.map((layer) => (
          <span
            key={layer.id}
            className="w-2.5 h-2.5 rounded-full"
            style={{ backgroundColor: LAYER_COLORS[layer.id].colorBase }}
            title={LAYER_COLORS[layer.id].label}
          />
        ))}
      </div>
    </div>
  );
}

export function LayerToggle({
  layers,
  onToggle,
  onOpacityChange: _onOpacityChange,
  compact = false,
  className,
}: LayerToggleProps) {
  // Note: onOpacityChange reserved for future opacity slider feature
  void _onOpacityChange;
  // Sort layers by render order
  const sortedLayers = useMemo(() => {
    return [...layers].sort(
      (a, b) => LAYER_RENDER_ORDER.indexOf(a.id) - LAYER_RENDER_ORDER.indexOf(b.id),
    );
  }, [layers]);

  return (
    <div className={clsx("flex flex-col gap-3", className)}>
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-secondary">Visualization Layers</h3>
        <LayerLegend layers={layers} />
      </div>

      <div className={clsx("flex flex-wrap gap-2", compact && "gap-1.5")}>
        {sortedLayers.map((layer) => (
          <LayerButton
            key={layer.id}
            config={LAYER_COLORS[layer.id]}
            state={layer}
            onToggle={() => onToggle(layer.id)}
            compact={compact}
          />
        ))}
      </div>

      {/* Quick actions */}
      <div className="flex items-center gap-2 mt-1">
        <button
          onClick={() => {
            // Enable all layers
            layers.forEach((l) => {
              if (!l.enabled) onToggle(l.id);
            });
          }}
          className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
        >
          Enable All
        </button>
        <span className="text-tertiary">|</span>
        <button
          onClick={() => {
            // Disable all except base
            layers.forEach((l) => {
              if (l.enabled && l.id !== "base") onToggle(l.id);
            });
          }}
          className="text-xs text-secondary hover:text-secondary transition-colors"
        >
          Reset
        </button>
      </div>
    </div>
  );
}

// Export a minimal version for inline use
export function LayerToggleInline({
  layers,
  onToggle,
  className,
}: Omit<LayerToggleProps, "compact" | "onOpacityChange">) {
  return (
    <div className={clsx("flex items-center gap-1.5", className)}>
      {LAYER_RENDER_ORDER.map((layerId) => {
        const layer = layers.find((l) => l.id === layerId);
        if (!layer) return null;

        const config = LAYER_COLORS[layerId];

        return (
          <button
            key={layerId}
            onClick={() => onToggle(layerId)}
            className={clsx(
              "w-7 h-7 rounded flex items-center justify-center transition-all",
              layer.enabled ? "shadow-sm" : "bg-secondary text-tertiary hover:bg-tertiary",
            )}
            style={
              layer.enabled
                ? {
                    backgroundColor: `${config.colorBase}30`,
                    color: config.colorLight,
                  }
                : undefined
            }
            title={`${config.label}: ${config.description}`}
          >
            <LayerIcon type={config.icon} className="w-3.5 h-3.5" />
          </button>
        );
      })}
    </div>
  );
}
