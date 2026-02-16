// Enrichment API types

export interface EnrichmentJobResponse {
  job_id: string;
  status: "pending" | "running" | "completed" | "failed";
  total_items: number;
  estimated_duration_seconds?: number;
  successful_sources?: number;
  failed_sources?: number;
  sources?: Record<string, SourceResult>;
  errors?: EnrichmentError[];
}

export interface SourceResult {
  status: "success" | "failed";
  enriched_count: number;
  failed_count?: number;
  error?: string;
}

export interface EnrichmentError {
  source: string;
  error: string;
  recoverable: boolean;
}

export interface EnrichmentStatusResponse {
  job_id: string;
  status: "pending" | "running" | "completed" | "failed";
  progress: number; // 0.0 - 1.0
  processed_items: number;
  total_items: number;
  failed_items: number;
  started_at: string;
  completed_at?: string | null;
  estimated_completion?: string;
  successful_sources?: number;
  failed_sources?: number;
  sources?: Record<string, SourceResult>;
  errors?: EnrichmentError[];
}

export interface EnrichVulnerabilitiesOptions {
  cve_ids?: string[];
  sources?: string[];
  force_refresh?: boolean;
}

export interface EnrichThreatsOptions {
  indicators?: Array<{
    type: "ip" | "domain" | "url" | "hash";
    value: string;
  }>;
  sources?: string[];
  force_refresh?: boolean;
}
