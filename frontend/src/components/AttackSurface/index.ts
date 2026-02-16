/**
 * AttackSurface Components
 *
 * Interactive attack surface visualization with multiple layers:
 * - Base: All assets (gray)
 * - EDR: Assets with detections (red)
 * - SIEM: Assets in incidents (orange)
 * - CTEM: Vulnerability risk (yellow/green gradient)
 * - Threats: Related IOCs (purple)
 * - Containment: Contained hosts (blue)
 */

// Main visualization component
export { AttackSurfaceLayers } from "./AttackSurfaceLayers";

// Individual controls
export { LayerToggle, LayerToggleInline } from "./LayerToggle";
export { TimeSlider, TimeSliderCompact } from "./TimeSlider";

// Types
export type {
  LayerType,
  LayerConfig,
  LayerState,
  VisualAsset,
  AssetCluster,
  TimeRange,
  ZoomLevel,
  VisualizationState,
  AssetConnection,
  ExportData,
  VisualMode,
} from "./types";

// Constants
export { LAYER_COLORS, LAYER_RENDER_ORDER } from "./types";
