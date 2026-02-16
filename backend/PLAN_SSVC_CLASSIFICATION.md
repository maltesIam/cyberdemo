# Plan: SSVC and Classification API Endpoints

## Functional Specification

Build 5 API endpoints for vulnerability SSVC decisions and classification data:

### 5.4 Endpoints SSVC
1. **GET `/api/vulnerabilities/ssvc/summary`** - Distribution of SSVC decisions
2. **GET `/api/vulnerabilities/ssvc/tree`** - Decision tree with data for visualization

### 5.5 Endpoints Classification
3. **GET `/api/vulnerabilities/cwes`** - List CWEs with stats
4. **GET `/api/vulnerabilities/cwes/{cwe_id}`** - CWE detail with CVE list
5. **GET `/api/vulnerabilities/packages`** - Vulnerable packages with CVE count

---

## Requirements

### SSVC Summary Endpoint
- REQ-SSVC-001: Return count of each SSVC decision (Act, Attend, Track*, Track)
- REQ-SSVC-002: Calculate total count and act_percentage
- REQ-SSVC-003: Return critical_requires_action count (Critical severity + SSVC=Act)
- REQ-SSVC-004: Handle empty data gracefully

### SSVC Tree Endpoint
- REQ-TREE-001: Return hierarchical tree structure for visualization
- REQ-TREE-002: Group by exploitation status (active, poc, none)
- REQ-TREE-003: Sub-group by automatable/impact for decision mapping
- REQ-TREE-004: Include counts at each node

### CWEs List Endpoint
- REQ-CWE-001: Return list of unique CWEs with aggregated stats
- REQ-CWE-002: Include cve_count, critical_count, high_count per CWE
- REQ-CWE-003: Return total count of unique CWEs
- REQ-CWE-004: Support pagination (limit/offset)

### CWE Detail Endpoint
- REQ-CWED-001: Return CWE metadata (id, name, description)
- REQ-CWED-002: Return list of CVE IDs affected by this CWE
- REQ-CWED-003: Return severity breakdown for this CWE
- REQ-CWED-004: Return 404 if CWE not found

### Packages Endpoint
- REQ-PKG-001: Return list of vulnerable packages
- REQ-PKG-002: Include ecosystem, name, cve_count, critical_count
- REQ-PKG-003: Return total count of packages
- REQ-PKG-004: Support pagination

---

## Architecture

### File Structure
```
backend/
  src/
    api/
      vuln_ssvc.py           # New router with SSVC endpoints
      vulnerabilities.py     # Existing - no changes needed
    services/
      ssvc_calculator.py     # Existing - use for SSVC logic
  tests/
    unit/
      api/
        test_vuln_ssvc_classification_endpoints.py  # New tests
```

### Data Sources
- OpenSearch index: `ctem-findings-v1` (existing)
- PostgreSQL: `vulnerability_enrichment` table (for CWE data)

### Response Models
- SSVCSummaryResponse
- SSVCTreeResponse
- CWEListResponse
- CWEDetailResponse
- PackageListResponse

---

## EPICs and Features

### EPIC 1: SSVC Endpoints
- [ ] Feature 1.1: SSVC Summary endpoint
- [ ] Feature 1.2: SSVC Tree endpoint

### EPIC 2: Classification Endpoints
- [ ] Feature 2.1: CWEs list endpoint
- [ ] Feature 2.2: CWE detail endpoint
- [ ] Feature 2.3: Packages endpoint

---

## TDD Approach

1. **RED Phase**: Write ~18 failing tests
   - 4 tests for SSVC summary
   - 4 tests for SSVC tree
   - 4 tests for CWEs list
   - 3 tests for CWE detail
   - 3 tests for Packages

2. **GREEN Phase**: Implement router to pass tests

3. **REFACTOR Phase**: Clean up if needed

---

## Technical Notes

- Use existing `SSVCCalculator` service for SSVC logic
- Use OpenSearch aggregations for counting
- Use mock data approach similar to existing endpoints
- Follow existing patterns from `vulnerabilities.py`
