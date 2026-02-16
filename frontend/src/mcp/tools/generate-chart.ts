/**
 * Tool: generate_chart
 *
 * Generates and displays a chart on the UI.
 */

import type { GenerateChartInput, GenerateChartOutput, MCPContext } from "../types";

let chartCounter = 0;

function generateChartId(): string {
  chartCounter += 1;
  return `chart-${Date.now()}-${chartCounter}`;
}

export async function generateChart(
  input: GenerateChartInput,
  context: { setState: MCPContext["setState"] },
): Promise<GenerateChartOutput> {
  // Validate input
  if (!input.data || !input.data.labels || !input.data.values) {
    return {
      success: false,
      error: "Invalid chart data: labels and values are required",
    };
  }

  if (input.data.labels.length === 0 || input.data.values.length === 0) {
    return {
      success: false,
      error: "Invalid chart data: labels and values cannot be empty",
    };
  }

  if (input.data.labels.length !== input.data.values.length) {
    return {
      success: false,
      error: "Invalid chart data: labels and values must have the same length",
    };
  }

  const chart_id = generateChartId();

  // Update state to add the chart
  context.setState((prev) => ({
    ...prev,
    charts: [
      ...prev.charts,
      {
        chart_id,
        chart_type: input.chart_type,
        title: input.title,
        data: input.data,
      },
    ],
  }));

  return {
    success: true,
    chart_id,
  };
}
