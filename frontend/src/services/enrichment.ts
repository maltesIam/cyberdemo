import { apiClient } from "./api";
import type {
  EnrichmentJobResponse,
  EnrichmentStatusResponse,
  EnrichVulnerabilitiesOptions,
  EnrichThreatsOptions,
} from "../types/enrichment";

/**
 * Enrichment API client with defensive error handling
 * CRITICAL: All methods use optional chaining and null checks
 */

/**
 * Start vulnerability enrichment job
 * @param options - Enrichment configuration options
 * @returns Promise<EnrichmentJobResponse>
 * @throws Error with user-friendly message on failure
 */
export async function enrichVulnerabilities(
  options: EnrichVulnerabilitiesOptions = {},
): Promise<EnrichmentJobResponse> {
  try {
    const response = await apiClient.post<EnrichmentJobResponse>(
      "/api/enrichment/vulnerabilities",
      {
        cve_ids: options.cve_ids,
        sources: options.sources ?? ["nvd", "epss", "github", "synthetic"],
        force_refresh: options.force_refresh ?? false,
      },
      {
        timeout: 10000, // 10 second timeout for job initiation
      },
    );

    // Defensive checks on response data
    if (!response.data || typeof response.data !== "object") {
      throw new Error("Invalid response from enrichment service");
    }

    if (!response.data.job_id) {
      throw new Error("No job ID returned from enrichment service");
    }

    return response.data;
  } catch (error: unknown) {
    // Network error handling
    if (error && typeof error === "object" && "code" in error) {
      const networkError = error as { code?: string; message?: string };
      if (networkError.code === "ECONNABORTED") {
        throw new Error("Enrichment request timed out. Please try again.");
      }
      if (networkError.code === "ERR_NETWORK") {
        throw new Error("Network error. Please check your connection.");
      }
    }

    // Axios error handling
    if (error && typeof error === "object" && "response" in error) {
      const axiosError = error as {
        response?: { data?: { message?: string }; status?: number };
        message?: string;
      };
      const status = axiosError.response?.status ?? 500;
      const message = axiosError.response?.data?.message ?? axiosError.message ?? "Unknown error";
      throw new Error(`Enrichment failed (${status}): ${message}`);
    }

    // Generic error fallback
    if (error instanceof Error) {
      throw error;
    }

    throw new Error("Failed to start vulnerability enrichment");
  }
}

/**
 * Start threat enrichment job
 * @param options - Enrichment configuration options
 * @returns Promise<EnrichmentJobResponse>
 * @throws Error with user-friendly message on failure
 */
export async function enrichThreats(
  options: EnrichThreatsOptions = {},
): Promise<EnrichmentJobResponse> {
  try {
    const response = await apiClient.post<EnrichmentJobResponse>(
      "/api/enrichment/threats",
      {
        indicators: options.indicators,
        sources: options.sources ?? ["otx", "abuseipdb", "greynoise", "virustotal", "synthetic"],
        force_refresh: options.force_refresh ?? false,
      },
      {
        timeout: 10000, // 10 second timeout for job initiation
      },
    );

    // Defensive checks on response data
    if (!response.data || typeof response.data !== "object") {
      throw new Error("Invalid response from enrichment service");
    }

    if (!response.data.job_id) {
      throw new Error("No job ID returned from enrichment service");
    }

    return response.data;
  } catch (error: unknown) {
    // Network error handling
    if (error && typeof error === "object" && "code" in error) {
      const networkError = error as { code?: string; message?: string };
      if (networkError.code === "ECONNABORTED") {
        throw new Error("Enrichment request timed out. Please try again.");
      }
      if (networkError.code === "ERR_NETWORK") {
        throw new Error("Network error. Please check your connection.");
      }
    }

    // Axios error handling
    if (error && typeof error === "object" && "response" in error) {
      const axiosError = error as {
        response?: { data?: { message?: string }; status?: number };
        message?: string;
      };
      const status = axiosError.response?.status ?? 500;
      const message = axiosError.response?.data?.message ?? axiosError.message ?? "Unknown error";
      throw new Error(`Enrichment failed (${status}): ${message}`);
    }

    // Generic error fallback
    if (error instanceof Error) {
      throw error;
    }

    throw new Error("Failed to start threat enrichment");
  }
}

/**
 * Get enrichment job status
 * @param jobId - Job identifier
 * @returns Promise<EnrichmentStatusResponse>
 * @throws Error with user-friendly message on failure
 */
export async function getEnrichmentStatus(jobId: string): Promise<EnrichmentStatusResponse> {
  try {
    if (!jobId || typeof jobId !== "string") {
      throw new Error("Invalid job ID");
    }

    const response = await apiClient.get<EnrichmentStatusResponse>(
      `/api/enrichment/status/${jobId}`,
      {
        timeout: 5000, // 5 second timeout for status check
      },
    );

    // Defensive checks on response data
    if (!response.data || typeof response.data !== "object") {
      throw new Error("Invalid response from enrichment service");
    }

    // Ensure progress is a valid number between 0 and 1
    const progress = response.data.progress ?? 0;
    response.data.progress = Math.max(0, Math.min(1, progress));

    return response.data;
  } catch (error: unknown) {
    // Network error handling
    if (error && typeof error === "object" && "code" in error) {
      const networkError = error as { code?: string };
      if (networkError.code === "ECONNABORTED") {
        throw new Error("Status check timed out");
      }
      if (networkError.code === "ERR_NETWORK") {
        throw new Error("Network error during status check");
      }
    }

    // Axios error handling
    if (error && typeof error === "object" && "response" in error) {
      const axiosError = error as {
        response?: { data?: { message?: string }; status?: number };
        message?: string;
      };
      const status = axiosError.response?.status ?? 500;
      const message = axiosError.response?.data?.message ?? axiosError.message ?? "Unknown error";
      throw new Error(`Status check failed (${status}): ${message}`);
    }

    // Generic error fallback
    if (error instanceof Error) {
      throw error;
    }

    throw new Error("Failed to check enrichment status");
  }
}
