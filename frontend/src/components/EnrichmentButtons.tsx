import { useState, useCallback, useRef, useEffect } from "react";
import { enrichVulnerabilities, enrichThreats, getEnrichmentStatus } from "../services/enrichment";
import { useToast } from "../utils/toast";
import type { EnrichmentStatusResponse } from "../types/enrichment";

interface EnrichmentButtonsProps {
  onEnrichmentComplete?: () => void;
}

/**
 * Enrichment buttons component with robust error handling
 * CRITICAL: UI never crashes due to backend errors
 * Handles partial failures gracefully (warning, not error)
 */
export function EnrichmentButtons({ onEnrichmentComplete }: EnrichmentButtonsProps) {
  const [vulnJobId, setVulnJobId] = useState<string | null>(null);
  const [threatJobId, setThreatJobId] = useState<string | null>(null);
  const [vulnProgress, setVulnProgress] = useState<number>(0);
  const [threatProgress, setThreatProgress] = useState<number>(0);

  // Use refs to track polling intervals to prevent memory leaks
  const vulnIntervalRef = useRef<number | null>(null);
  const threatIntervalRef = useRef<number | null>(null);

  const { showToast } = useToast();

  // Cleanup intervals on unmount
  useEffect(() => {
    return () => {
      if (vulnIntervalRef.current) {
        clearInterval(vulnIntervalRef.current);
      }
      if (threatIntervalRef.current) {
        clearInterval(threatIntervalRef.current);
      }
    };
  }, []);

  /**
   * Evaluate enrichment result and show appropriate notification
   * CRITICAL: Partial failures show warning, not error
   */
  const evaluateResult = useCallback(
    (status: EnrichmentStatusResponse, type: "vulnerabilities" | "threats") => {
      const successfulSources = status.successful_sources ?? 0;
      const failedSources = status.failed_sources ?? 0;
      const totalSources = successfulSources + failedSources;

      // All sources failed = error
      if (totalSources > 0 && successfulSources === 0) {
        showToast(
          "error",
          `All enrichment sources failed for ${type}. Please try again later.`,
          7000,
        );
        return;
      }

      // Some sources failed = warning
      if (failedSources > 0) {
        showToast(
          "warning",
          `Enrichment completed with ${failedSources} source(s) unavailable. ${successfulSources} source(s) succeeded.`,
          6000,
        );
      } else {
        // All sources succeeded = success
        showToast(
          "success",
          `Successfully enriched ${type} from all ${successfulSources} sources!`,
          4000,
        );
      }
    },
    [showToast],
  );

  /**
   * Poll enrichment status
   * CRITICAL: Always cleanup interval, even on error
   */
  const pollStatus = useCallback(
    async (
      jobId: string,
      setProgress: (progress: number) => void,
      setJobId: (jobId: string | null) => void,
      intervalRef: React.MutableRefObject<number | null>,
      type: "vulnerabilities" | "threats",
    ) => {
      try {
        const status = await getEnrichmentStatus(jobId);

        // Defensive: ensure progress is a number
        const progress = typeof status.progress === "number" ? status.progress : 0;
        setProgress(progress * 100);

        if (status.status === "completed" || status.status === "failed") {
          // Cleanup
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
          setJobId(null);
          setProgress(0);

          // Evaluate result
          if (status.status === "completed") {
            evaluateResult(status, type);
            // Notify parent to reload data
            if (onEnrichmentComplete) {
              onEnrichmentComplete();
            }
          } else {
            // Failed status
            showToast("error", `Enrichment job failed. Please try again.`, 5000);
          }
        }
      } catch (error) {
        // CRITICAL: Don't break polling on transient errors
        // Log error but continue polling
        console.error("[EnrichmentButtons] Status poll error:", error);

        // If we've failed multiple times in a row, stop polling
        // This prevents infinite polling on permanent failures
        // For now, we'll rely on the job timeout on the backend
      }
    },
    [evaluateResult, onEnrichmentComplete, showToast],
  );

  /**
   * Handle vulnerability enrichment
   * CRITICAL: Button always re-enables, even on error
   */
  const handleEnrichVulnerabilities = useCallback(async () => {
    try {
      // Start enrichment job
      const response = await enrichVulnerabilities({
        sources: ["nvd", "epss", "github", "synthetic"],
        force_refresh: false,
      });

      // Defensive: ensure we got a job_id
      if (!response.job_id) {
        throw new Error("No job ID returned from server");
      }

      setVulnJobId(response.job_id);
      setVulnProgress(0);

      // Show initial notification
      showToast("info", "Vulnerability enrichment started...", 3000);

      // Start polling
      vulnIntervalRef.current = window.setInterval(() => {
        pollStatus(
          response.job_id,
          setVulnProgress,
          setVulnJobId,
          vulnIntervalRef,
          "vulnerabilities",
        );
      }, 2000); // Poll every 2 seconds
    } catch (error) {
      // CRITICAL: Always cleanup state on error
      setVulnJobId(null);
      setVulnProgress(0);
      if (vulnIntervalRef.current) {
        clearInterval(vulnIntervalRef.current);
        vulnIntervalRef.current = null;
      }

      // Show error notification
      const message = error instanceof Error ? error.message : "Failed to start enrichment";
      showToast("error", message, 5000);

      console.error("[EnrichmentButtons] Vulnerability enrichment error:", error);
    }
  }, [pollStatus, showToast]);

  /**
   * Handle threat enrichment
   * CRITICAL: Button always re-enables, even on error
   */
  const handleEnrichThreats = useCallback(async () => {
    try {
      // Start enrichment job
      const response = await enrichThreats({
        sources: ["otx", "abuseipdb", "greynoise", "virustotal", "synthetic"],
        force_refresh: false,
      });

      // Defensive: ensure we got a job_id
      if (!response.job_id) {
        throw new Error("No job ID returned from server");
      }

      setThreatJobId(response.job_id);
      setThreatProgress(0);

      // Show initial notification
      showToast("info", "Threat enrichment started...", 3000);

      // Start polling
      threatIntervalRef.current = window.setInterval(() => {
        pollStatus(
          response.job_id,
          setThreatProgress,
          setThreatJobId,
          threatIntervalRef,
          "threats",
        );
      }, 2000); // Poll every 2 seconds
    } catch (error) {
      // CRITICAL: Always cleanup state on error
      setThreatJobId(null);
      setThreatProgress(0);
      if (threatIntervalRef.current) {
        clearInterval(threatIntervalRef.current);
        threatIntervalRef.current = null;
      }

      // Show error notification
      const message = error instanceof Error ? error.message : "Failed to start enrichment";
      showToast("error", message, 5000);

      console.error("[EnrichmentButtons] Threat enrichment error:", error);
    }
  }, [pollStatus, showToast]);

  return (
    <div className="flex gap-4">
      {/* Vulnerability Enrichment Button */}
      <button
        onClick={handleEnrichVulnerabilities}
        disabled={!!vulnJobId}
        className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-tertiary disabled:cursor-not-allowed text-primary rounded-lg transition-colors font-medium"
        aria-label="Enriquecer Vulnerabilidades"
      >
        {vulnJobId ? (
          <>
            <svg
              className="animate-spin h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>Enriching... {vulnProgress.toFixed(0)}%</span>
          </>
        ) : (
          <>
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
            <span>Enriquecer Vulnerabilidades</span>
          </>
        )}
      </button>

      {/* Threat Enrichment Button */}
      <button
        onClick={handleEnrichThreats}
        disabled={!!threatJobId}
        className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-tertiary disabled:cursor-not-allowed text-primary rounded-lg transition-colors font-medium"
        aria-label="Enriquecer Amenazas"
      >
        {threatJobId ? (
          <>
            <svg
              className="animate-spin h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>Enriching... {threatProgress.toFixed(0)}%</span>
          </>
        ) : (
          <>
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <span>Enriquecer Amenazas</span>
          </>
        )}
      </button>
    </div>
  );
}
