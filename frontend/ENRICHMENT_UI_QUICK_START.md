# Enrichment UI - Quick Start Guide

## For Developers

### Using the Enrichment Buttons

The enrichment buttons are already integrated into the Dashboard page. No additional setup required.

### Customizing Behavior

#### Change Reload Behavior

By default, the dashboard reloads on enrichment completion. To customize:

```tsx
// In DashboardPage.tsx
<EnrichmentButtons
  onEnrichmentComplete={() => {
    // Custom behavior here instead of reload
    // Example: refetch specific data
    queryClient.invalidateQueries(["dashboard-kpis"]);
  }}
/>
```

#### Change Default Sources

Modify default sources in `EnrichmentButtons.tsx`:

```typescript
// Line ~113
const response = await enrichVulnerabilities({
  sources: ["nvd", "epss", "github", "synthetic"], // Change here
  force_refresh: false,
});
```

#### Change Polling Interval

Modify polling interval (default: 2 seconds):

```typescript
// Line ~126
vulnIntervalRef.current = window.setInterval(() => {
  pollStatus(...);
}, 2000); // Change to 5000 for 5 seconds
```

### Adding Toast Notifications Elsewhere

The toast system is available app-wide via context:

```tsx
import { useToast } from "../utils/toast";

function MyComponent() {
  const { showToast } = useToast();

  const handleAction = () => {
    showToast("success", "Action completed!", 4000);
    showToast("warning", "Something needs attention", 6000);
    showToast("error", "Action failed", 7000);
    showToast("info", "FYI: Something happened", 3000);
  };

  return <button onClick={handleAction}>Do Something</button>;
}
```

### Error Handling Pattern

When creating new API calls, follow this defensive pattern:

```typescript
export async function myApiCall(): Promise<MyResponse> {
  try {
    const response = await apiClient.get<MyResponse>("/my/endpoint", {
      timeout: 5000,
    });

    // Defensive validation
    if (!response.data || typeof response.data !== "object") {
      throw new Error("Invalid response");
    }

    // Safe access with fallbacks
    const value = response.data.someField ?? "default";

    return response.data;
  } catch (error: unknown) {
    // Network error handling
    if (error && typeof error === "object" && "code" in error) {
      const networkError = error as { code?: string };
      if (networkError.code === "ECONNABORTED") {
        throw new Error("Request timed out");
      }
      if (networkError.code === "ERR_NETWORK") {
        throw new Error("Network error");
      }
    }

    // Axios error handling
    if (error && typeof error === "object" && "response" in error) {
      const axiosError = error as {
        response?: { data?: { message?: string }; status?: number };
      };
      const status = axiosError.response?.status ?? 500;
      const message = axiosError.response?.data?.message ?? "Unknown error";
      throw new Error(`API Error (${status}): ${message}`);
    }

    // Generic fallback
    if (error instanceof Error) {
      throw error;
    }

    throw new Error("API call failed");
  }
}
```

## For Backend Developers

### Expected API Endpoints

#### 1. Start Vulnerability Enrichment

```http
POST /api/enrichment/vulnerabilities
Content-Type: application/json

{
  "cve_ids": ["CVE-2024-0001"], // Optional, if empty enriches all
  "sources": ["nvd", "epss", "github", "synthetic"], // Optional
  "force_refresh": false // Optional
}

Response 200:
{
  "job_id": "uuid-here",
  "status": "pending",
  "total_items": 150,
  "estimated_duration_seconds": 45
}
```

#### 2. Start Threat Enrichment

```http
POST /api/enrichment/threats
Content-Type: application/json

{
  "indicators": [
    { "type": "ip", "value": "192.0.2.1" },
    { "type": "domain", "value": "evil.com" }
  ], // Optional
  "sources": ["otx", "abuseipdb", "greynoise", "virustotal", "synthetic"],
  "force_refresh": false
}

Response 200:
{
  "job_id": "uuid-here",
  "status": "pending",
  "total_items": 200
}
```

#### 3. Get Enrichment Status

```http
GET /api/enrichment/status/{job_id}

Response 200:
{
  "job_id": "uuid-here",
  "status": "running", // pending | running | completed | failed
  "progress": 0.67, // 0.0 to 1.0
  "processed_items": 100,
  "total_items": 150,
  "failed_items": 2,
  "started_at": "2026-02-13T10:00:00Z",
  "completed_at": null,
  "estimated_completion": "2026-02-13T10:00:45Z",

  // IMPORTANT: Include these for partial failure handling
  "successful_sources": 2,
  "failed_sources": 2,
  "sources": {
    "nvd": {
      "status": "success",
      "enriched_count": 50,
      "failed_count": 0
    },
    "epss": {
      "status": "success",
      "enriched_count": 50
    },
    "github": {
      "status": "failed",
      "enriched_count": 0,
      "error": "API rate limit exceeded"
    },
    "synthetic": {
      "status": "failed",
      "error": "Service unavailable"
    }
  },
  "errors": [
    {
      "source": "github",
      "error": "API rate limit exceeded",
      "recoverable": true
    },
    {
      "source": "synthetic",
      "error": "Service unavailable",
      "recoverable": true
    }
  ]
}
```

### Critical Backend Requirements

#### 1. Status Field Must Be Accurate

```python
# Backend must return these statuses correctly
status = "pending"   # Job created, not started yet
status = "running"   # Job is actively processing
status = "completed" # Job finished (with or without partial failures)
status = "failed"    # Job failed completely (all sources failed)
```

#### 2. Progress Must Be 0.0 to 1.0

```python
# Frontend expects progress as float between 0.0 and 1.0
progress = processed_items / total_items  # 0.0 to 1.0
# Frontend will multiply by 100 for percentage display
```

#### 3. Partial Failures = completed, Not failed

```python
# Even if some sources fail, if ANY source succeeds:
if successful_sources > 0:
    status = "completed"  # NOT "failed"
    successful_sources = 2
    failed_sources = 2
else:
    status = "failed"  # Only if ALL sources fail
```

#### 4. Timeout Handling

```python
# Frontend has these timeouts:
# - Job start: 10 seconds
# - Status polling: 5 seconds (every 2 seconds)

# Backend should:
# - Return job_id quickly (<5s)
# - Keep job alive for polling
# - Don't block on slow sources
```

## Testing

### Manual Testing

1. **Start Development Server:**

```bash
cd CyberDemo/frontend
npm run dev
```

2. **Navigate to Dashboard:**

```
http://localhost:5173/dashboard
```

3. **Test Vulnerability Enrichment:**
   - Click "Enriquecer Vulnerabilidades"
   - Should show spinner and progress
   - Should show toast notification on completion
   - Dashboard should reload

4. **Test Threat Enrichment:**
   - Click "Enriquecer Amenazas"
   - Same behavior as vulnerabilities

### Testing with Mock Backend

Create a mock server for testing:

```typescript
// In test-server.ts
import express from "express";

const app = express();
app.use(express.json());

let jobs = new Map();

app.post("/api/enrichment/vulnerabilities", (req, res) => {
  const job_id = "test-job-" + Date.now();
  jobs.set(job_id, { progress: 0, status: "running" });

  res.json({
    job_id,
    status: "pending",
    total_items: 100,
  });
});

app.get("/api/enrichment/status/:job_id", (req, res) => {
  const job = jobs.get(req.params.job_id);

  if (!job) {
    return res.status(404).json({ error: "Job not found" });
  }

  // Simulate progress
  job.progress = Math.min(1.0, job.progress + 0.1);

  if (job.progress >= 1.0) {
    job.status = "completed";
  }

  res.json({
    job_id: req.params.job_id,
    status: job.status,
    progress: job.progress,
    processed_items: Math.floor(job.progress * 100),
    total_items: 100,
    failed_items: 0,
    successful_sources: 4,
    failed_sources: 0,
  });
});

app.listen(8000, () => console.log("Mock server on :8000"));
```

### Browser Console Tests

Open browser console and verify:

1. **No React errors:**

```
// Should NOT see:
// "Cannot read properties of undefined"
// "setState on unmounted component"
```

2. **Expected logs:**

```
// Should see status polling logs:
[EnrichmentButtons] Status poll: 25%
[EnrichmentButtons] Status poll: 50%
[EnrichmentButtons] Status poll: 75%
[EnrichmentButtons] Status poll: completed
```

## Troubleshooting

### Button Not Showing

**Check:** Is ToastProvider wrapping the App?

```tsx
// In App.tsx
<ToastProvider>
  <BrowserRouter>{/* ... */}</BrowserRouter>
</ToastProvider>
```

### Toast Not Showing

**Check:** Is component using useToast hook?

```tsx
import { useToast } from "../utils/toast";
const { showToast } = useToast();
```

### Button Not Re-enabling After Error

**Check:** Is state cleanup in catch block?

```typescript
catch (error) {
  setJobId(null);        // ✅ Reset job ID
  setProgress(0);        // ✅ Reset progress
  clearInterval(ref);    // ✅ Clear interval
  showToast('error', message); // ✅ Show error
}
```

### Memory Leak Warning

**Check:** Is cleanup effect present?

```typescript
useEffect(() => {
  return () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
  };
}, []);
```

### Progress Not Updating

**Check:** Is backend returning progress as 0.0-1.0?

```python
# Backend should return:
progress = 0.5  # NOT 50
```

## Support

For issues or questions:

1. Check `ENRICHMENT_UI_ERROR_HANDLING.md` for detailed documentation
2. Check `ENRICHMENT_PLAN.md` section 6-7 for design decisions
3. Check browser console for error messages
4. Check network tab for API responses

## Next Steps

1. **Backend Integration:** Implement enrichment endpoints
2. **E2E Testing:** Run Playwright tests (see `ENRICHMENT_PLAN.md` section 8.4)
3. **Performance Testing:** Test with 100+ items
4. **User Acceptance Testing:** Test with real users
