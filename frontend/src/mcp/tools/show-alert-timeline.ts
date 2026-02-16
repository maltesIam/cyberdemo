/**
 * Tool: show_alert_timeline
 *
 * Displays an alert timeline for a specific incident.
 */

import type { ShowAlertTimelineInput, ShowAlertTimelineOutput, MCPContext } from "../types";

export async function showAlertTimeline(
  input: ShowAlertTimelineInput,
  context: { setState: MCPContext["setState"] },
): Promise<ShowAlertTimelineOutput> {
  // Validate input
  if (!input.incident_id) {
    return {
      success: false,
      error: "incident_id is required",
    };
  }

  if (!input.alerts || input.alerts.length === 0) {
    return {
      success: false,
      error: "alerts array cannot be empty",
    };
  }

  // Update state to show timeline
  context.setState((prev) => ({
    ...prev,
    timeline: {
      incident_id: input.incident_id,
      alerts: input.alerts,
    },
    currentView: "timeline",
  }));

  return {
    success: true,
  };
}
