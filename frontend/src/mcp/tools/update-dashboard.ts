/**
 * Tool: update_dashboard
 *
 * Updates dashboard KPIs and/or charts in real-time.
 */

import type { UpdateDashboardInput, UpdateDashboardOutput, MCPContext } from "../types";

export async function updateDashboard(
  input: UpdateDashboardInput,
  context: { setState: MCPContext["setState"] },
): Promise<UpdateDashboardOutput> {
  // At least one of kpis or charts should be provided
  if (!input.kpis && !input.charts) {
    return {
      success: false,
      error: "At least one of kpis or charts must be provided",
    };
  }

  // Update state
  context.setState((prev) => {
    let updatedCharts = prev.charts;

    // Update existing charts if provided
    if (input.charts) {
      updatedCharts = prev.charts.map((chart) => {
        const update = input.charts?.find((u) => u.chart_id === chart.chart_id);
        if (update) {
          return {
            ...chart,
            data: update.data,
          };
        }
        return chart;
      });
    }

    return {
      ...prev,
      charts: updatedCharts,
      currentView: "dashboard",
    };
  });

  return {
    success: true,
  };
}
