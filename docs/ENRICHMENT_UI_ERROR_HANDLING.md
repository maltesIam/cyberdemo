# Enrichment UI - Error Handling Implementation

## Overview

This document describes the error handling implementation for the enrichment buttons in the CyberDemo frontend. The implementation follows **defensive programming principles** to ensure the UI never crashes due to backend errors.

## Critical Requirements Met

### 1. UI Never Breaks on Backend Errors

**Implementation:**

- All API calls wrapped in try-catch blocks
- Defensive null/undefined checks using optional chaining (`?.`) and nullish coalescing (`??`)
- State cleanup in all error paths
- Buttons always re-enable after completion or error

**Code Examples:**

```typescript
// Defensive API response validation
if (!response.data || typeof response.data !== "object") {
  throw new Error("Invalid response from enrichment service");
}

// Safe progress access with fallback
const progress = typeof status.progress === "number" ? status.progress : 0;
setProgress(progress * 100);

// Safe source count access
const successfulSources = status.successful_sources ?? 0;
const failedSources = status.failed_sources ?? 0;
```

### 2. Partial Failures Show Warning, Not Error

**Implementation:**

- Three-tier notification system: success, warning, error
- Partial failures (some sources work) → warning
- Total failures (all sources fail) → error
- All sources succeed → success

**Code Example:**

```typescript
const evaluateResult = (status: EnrichmentStatusResponse) => {
  const successfulSources = status.successful_sources ?? 0;
  const failedSources = status.failed_sources ?? 0;
  const totalSources = successfulSources + failedSources;

  // All sources failed = error
  if (totalSources > 0 && successfulSources === 0) {
    showToast("error", "All enrichment sources failed...");
    return;
  }

  // Some sources failed = warning
  if (failedSources > 0) {
    showToast(
      "warning",
      `...${failedSources} source(s) unavailable. ${successfulSources} source(s) succeeded.`,
    );
  } else {
    // All sources succeeded = success
    showToast("success", `Successfully enriched from all ${successfulSources} sources!`);
  }
};
```

### 3. Network Error Handling

**Implementation:**

- Specific error messages for different failure modes
- Timeout detection and user-friendly messages
- Network error detection
- HTTP status code handling

**Code Example:**

```typescript
// Network error handling in enrichment.ts
if (error && typeof error === "object" && "code" in error) {
  const networkError = error as { code?: string };
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
  };
  const status = axiosError.response?.status ?? 500;
  const message = axiosError.response?.data?.message ?? "Unknown error";
  throw new Error(`Enrichment failed (${status}): ${message}`);
}
```

### 4. State Cleanup on All Error Paths

**Implementation:**

- Cleanup state in catch blocks
- Clear polling intervals on error
- Reset progress indicators
- Re-enable buttons

**Code Example:**

```typescript
const handleEnrichVulnerabilities = async () => {
  try {
    // ... enrichment logic
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
  }
};
```

### 5. Memory Leak Prevention

**Implementation:**

- Use refs to track polling intervals
- Cleanup intervals on component unmount
- Cleanup intervals on job completion/failure

**Code Example:**

```typescript
const vulnIntervalRef = useRef<number | null>(null);
const threatIntervalRef = useRef<number | null>(null);

// Cleanup on unmount
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
```

## Components Implemented

### 1. EnrichmentButtons.tsx

**Location:** `CyberDemo/frontend/src/components/EnrichmentButtons.tsx`

**Features:**

- Two enrichment buttons (vulnerabilities, threats)
- Progress indicators with spinner and percentage
- Toast notifications for all scenarios
- Automatic polling with status updates
- State management with cleanup
- Accessibility attributes (aria-label, aria-hidden)

**Props:**

```typescript
interface EnrichmentButtonsProps {
  onEnrichmentComplete?: () => void; // Callback to reload data
}
```

**State Management:**

- `vulnJobId`: Current vulnerability job ID (null when idle)
- `threatJobId`: Current threat job ID (null when idle)
- `vulnProgress`: Progress percentage (0-100)
- `threatProgress`: Progress percentage (0-100)

### 2. Toast Notification System

**Location:** `CyberDemo/frontend/src/utils/toast.tsx`

**Features:**

- Lightweight (no external dependencies)
- Four notification types: success, error, warning, info
- Auto-dismiss with configurable duration
- Manual dismiss button
- Slide-in animation
- Position: top-right corner
- Context-based (React Context API)

**API:**

```typescript
const { showToast } = useToast();

showToast("success", "Operation completed successfully", 4000);
showToast("warning", "Some sources unavailable", 6000);
showToast("error", "All sources failed", 7000);
showToast("info", "Enrichment started", 3000);
```

### 3. Enrichment API Client

**Location:** `CyberDemo/frontend/src/services/enrichment.ts`

**Features:**

- Type-safe API calls
- Defensive error handling
- Network error detection
- Timeout configuration
- User-friendly error messages

**API:**

```typescript
// Start vulnerability enrichment
const response = await enrichVulnerabilities({
  cve_ids: ["CVE-2024-0001"], // Optional
  sources: ["nvd", "epss", "github", "synthetic"], // Optional
  force_refresh: false, // Optional
});

// Start threat enrichment
const response = await enrichThreats({
  indicators: [{ type: "ip", value: "192.0.2.1" }], // Optional
  sources: ["otx", "abuseipdb", "greynoise", "virustotal", "synthetic"],
  force_refresh: false,
});

// Poll job status
const status = await getEnrichmentStatus(jobId);
```

### 4. Type Definitions

**Location:** `CyberDemo/frontend/src/types/enrichment.ts`

**Types:**

- `EnrichmentJobResponse`: Initial job creation response
- `EnrichmentStatusResponse`: Status polling response
- `SourceResult`: Per-source enrichment result
- `EnrichmentError`: Detailed error information
- `EnrichVulnerabilitiesOptions`: Vulnerability enrichment options
- `EnrichThreatsOptions`: Threat enrichment options

## Integration with Dashboard

**Location:** `CyberDemo/frontend/src/pages/DashboardPage.tsx`

**Changes:**

1. Import `EnrichmentButtons` component
2. Add buttons to header with flex layout
3. Pass `onEnrichmentComplete` callback to reload data

**Code:**

```tsx
<div className="flex items-center justify-between">
  <div>
    <h1 className="text-2xl font-bold text-white">Dashboard</h1>
    <p className="text-gray-400 mt-1">Real-time security operations overview</p>
  </div>
  <EnrichmentButtons onEnrichmentComplete={() => window.location.reload()} />
</div>
```

## Error Scenarios Handled

### 1. Network Timeout

- **Trigger:** API call exceeds timeout (10s for job start, 5s for status)
- **Behavior:** Show error toast, cleanup state, re-enable button
- **Message:** "Enrichment request timed out. Please try again."

### 2. Network Disconnection

- **Trigger:** No network connection
- **Behavior:** Show error toast, cleanup state, re-enable button
- **Message:** "Network error. Please check your connection."

### 3. Backend Error (4xx/5xx)

- **Trigger:** Backend returns error response
- **Behavior:** Show error toast with status code, cleanup state
- **Message:** "Enrichment failed (500): Internal server error"

### 4. Partial Source Failure

- **Trigger:** Some sources succeed, some fail
- **Behavior:** Show warning toast, continue with partial data, reload dashboard
- **Message:** "Enrichment completed with 2 source(s) unavailable. 2 source(s) succeeded."

### 5. Total Source Failure

- **Trigger:** All sources fail
- **Behavior:** Show error toast, cleanup state, do NOT reload
- **Message:** "All enrichment sources failed. Please try again later."

### 6. Invalid Response Data

- **Trigger:** Backend returns malformed JSON or missing fields
- **Behavior:** Show error toast, cleanup state, re-enable button
- **Message:** "Invalid response from enrichment service"

### 7. Status Polling Error

- **Trigger:** Error during status polling (transient)
- **Behavior:** Log error to console, continue polling (don't break UI)
- **Message:** (Console only, no user notification for transient errors)

## Testing Scenarios

### Manual Testing Checklist

- [ ] Click "Enriquecer Vulnerabilidades" button
  - [ ] Button shows spinner and progress
  - [ ] Progress updates every 2 seconds
  - [ ] Success toast on completion (all sources work)
  - [ ] Dashboard reloads with new data
  - [ ] Button re-enables

- [ ] Click "Enriquecer Amenazas" button
  - [ ] Same behavior as vulnerabilities

- [ ] Test with backend offline
  - [ ] Error toast: "Network error..."
  - [ ] Button re-enables immediately
  - [ ] No console errors

- [ ] Test with backend returning 500 error
  - [ ] Error toast with status code
  - [ ] Button re-enables
  - [ ] No console errors

- [ ] Test with partial source failures (mock)
  - [ ] Warning toast: "X sources unavailable, Y succeeded"
  - [ ] Dashboard reloads
  - [ ] Button re-enables

- [ ] Test with all sources failing (mock)
  - [ ] Error toast: "All sources failed"
  - [ ] Dashboard does NOT reload
  - [ ] Button re-enables

- [ ] Test rapid clicking
  - [ ] Button disabled during enrichment
  - [ ] No duplicate jobs started
  - [ ] State remains consistent

- [ ] Test component unmount during enrichment
  - [ ] No memory leaks (intervals cleared)
  - [ ] No "setState on unmounted component" warnings

### Browser Console Checks

During all test scenarios:

- [ ] No React errors
- [ ] No "Cannot read properties of undefined" errors
- [ ] No memory leak warnings
- [ ] Transient polling errors logged but not thrown

## Best Practices Applied

### 1. Optional Chaining (`?.`)

```typescript
const progress = status.progress ?? 0;
const sources = status.sources?.nvd?.enriched_count ?? 0;
```

### 2. Nullish Coalescing (`??`)

```typescript
const successfulSources = status.successful_sources ?? 0;
const message = error.message ?? "Unknown error";
```

### 3. Type Guards

```typescript
if (error instanceof Error) {
  throw error;
}

if (typeof response.data !== "object") {
  throw new Error("Invalid response");
}
```

### 4. Early Returns

```typescript
if (!response.data) {
  throw new Error("No data");
}
// Continue with safe access to response.data
```

### 5. Cleanup in Finally/Catch

```typescript
try {
  // ... operation
} catch (error) {
  // Cleanup state
  setJobId(null);
  setProgress(0);
  clearInterval(intervalRef.current);
  // Show error
  showToast("error", message);
}
```

## Future Enhancements

### 1. Error Details Modal (Optional)

- Show detailed error information for debugging
- List of failed sources with error messages
- Retry individual sources

### 2. Retry Logic

- Automatic retry on transient errors
- Exponential backoff for polling
- Max retry attempts configuration

### 3. Progress Details

- Show per-source progress
- Show items processed vs total
- ETA for completion

### 4. Cancel Job

- Add cancel button during enrichment
- Cancel endpoint in API
- Cleanup on cancel

## Conclusion

The enrichment UI implementation prioritizes **reliability and user experience**:

1. **UI never crashes** - All error paths are handled defensively
2. **Clear feedback** - Toast notifications for all scenarios
3. **Graceful degradation** - Partial failures show warnings, not errors
4. **State management** - Cleanup on all paths, no memory leaks
5. **Accessibility** - Proper ARIA attributes and semantic HTML

The implementation is ready for integration with the backend enrichment service described in section 7 of `ENRICHMENT_PLAN.md`.
