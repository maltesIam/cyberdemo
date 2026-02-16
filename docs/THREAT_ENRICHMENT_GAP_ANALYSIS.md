# Gap Analysis - Threat Enrichment System

**Version:** 1.0
**Date:** 2026-02-16
**Purpose:** Identify gaps between build plan, functional document, and current implementation

---

## 1. Executive Summary

This document analyzes the current state of the Threat Enrichment System implementation versus the build plan (THREAT_ENRICHMENT_BUILD_PLAN.md) and functional design (THREAT_ENRICHMENT_DESIGN.md).

### Overall Progress Summary

| Category | Items in Plan | Already Done | Pending | % Complete |
|----------|---------------|--------------|---------|------------|
| Backend Core | 6 | 5 | 1 | 83% |
| API Clients (Tier 1-2) | 11 | 3 (existing) | 8 | 27% |
| API Clients (Tier 3-4) | 6 | 0 | 6 | 0% |
| Synthetic Generators | 6 | 3 | 3 | 50% |
| API Endpoints | 15 | 2 (partial) | 13 | 13% |
| Frontend - Pages Base | 6 | 3 | 3 | 50% |
| Frontend - Map Mundi | 6 | 5 | 1 | 83% |
| Frontend - Additional Views | 7 | 0 | 7 | 0% |
| Tests | 5+ | 4 | 1 | 80% |
| MCP Integration | 4 | 0 | 4 | 0% |

**Estimated Overall Completion: ~35%**

---

## 2. Items ALREADY DONE

### 2.1 Backend Core (Phase 1)

| Item | Status | Location | Notes |
|------|--------|----------|-------|
| EnrichmentService class | DONE | `backend/src/services/enrichment_service.py` | Full implementation with enrich_vulnerabilities() and enrich_threats() |
| enrich_threats() method | DONE | `enrichment_service.py:345-485` | Complete with indicator parsing, source iteration, and error handling |
| enrich_single_indicator() logic | DONE | `enrichment_service.py:487-517` | Implemented as _enrich_threat_from_source() |
| MAX_ITEMS_PER_SOURCE (100) limit | DONE | `enrichment_service.py:24` | Correctly limits to 100 items |
| Graceful degradation (source failure) | DONE | `enrichment_service.py:450-460` | CircuitBreakerOpenError and Exception handling |
| Risk score calculation | DONE | `enrichment_service.py:700-757` | Weighted algorithm with AbuseIPDB, VT, GreyNoise, etc. |
| Risk level conversion | DONE | `enrichment_service.py:759-768` | critical/high/medium/low/unknown |
| Confidence calculation | DONE | `enrichment_service.py:771-778` | Based on successful sources |
| Circuit Breaker | DONE | `backend/src/services/circuit_breaker.py` | Full CLOSED/OPEN/HALF_OPEN state machine |
| CircuitBreaker states | DONE | `circuit_breaker.py:20-25` | Enum with all 3 states |
| CircuitBreaker threshold (5 failures) | DONE | `circuit_breaker.py:46` | Configurable, defaults to 5 |
| CircuitBreaker timeout (60s) | DONE | `circuit_breaker.py:46` | Configurable, defaults to 60s |
| Job tracking (in-memory) | DONE | `enrichment_service.py:215-255` | _create_job() with UUID and status |
| Job status retrieval | DONE | `enrichment_service.py:185-213` | get_enrichment_status() method |
| In-memory cache | DONE | `backend/src/services/enrichment_cache.py` | Thread-safe with TTL |

### 2.2 Database Models (Phase 1)

| Item | Status | Location | Notes |
|------|--------|----------|-------|
| EnrichmentJob model | DONE | `backend/src/models/enrichment.py:16-39` | With status, progress tracking |
| VulnerabilityEnrichment model | DONE | `enrichment.py:42-100` | CVSS, EPSS, threat actors, etc. |
| ThreatEnrichment model | DONE | `enrichment.py:103-174` | IOC fields, reputation, malware families |
| EnrichmentCache model | DONE | `enrichment.py:177-198` | Cache key, expiration, hit count |
| Database indexes | DONE | `enrichment.py` | Multiple indexes defined |

### 2.3 Synthetic Generators (Phase 2.7)

| Item | Status | Location | Notes |
|------|--------|----------|-------|
| CrowdStrikeSandboxMock | DONE | `generators/enrichment/crowdstrike_mock.py` | Full sandbox report generation |
| - generate_sandbox_report() | DONE | Lines 28-106 | Malicious/clean verdicts |
| - Behaviors generation | DONE | Lines 108-162 | Persistence, network, file, process, evasion |
| - MITRE techniques extraction | DONE | Lines 164-190 | Maps behaviors to T-codes |
| - IOCs extraction | DONE | Lines 192-224 | IPs, domains, file paths |
| TenableVPRMock | DONE | `generators/enrichment/tenable_mock.py` | VPR score calculation |
| RecordedFutureMock | DONE | `generators/enrichment/recorded_future_mock.py` | Risk score, threat actors, campaigns |
| Synthetic data in EnrichmentService | DONE | `enrichment_service.py:519-632` | _generate_synthetic_threat_data() |

### 2.4 Frontend - Pages Base (Phase 4)

| Item | Status | Location | Notes |
|------|--------|----------|-------|
| ThreatEnrichmentPage | DONE | `frontend/src/pages/ThreatEnrichmentPage.tsx` | Full page with stats, IOC list, modal |
| Stats cards | DONE | Lines 304-329 | Total, critical, high, medium, countries, TTPs |
| IOC input form | DONE | Lines 332-390 | Textarea with auto-detect |
| Enrich button with progress | DONE | Lines 357-388 | Spinner, progress %, disabled states |
| IOC list table | DONE | Lines 407-505 | With pagination scroll, risk badges |
| IOC detail modal | DONE | Lines 626-893 | Geo, network, reputation, threat intel tabs |
| Malware families sidebar | DONE | Lines 509-550 | Bar chart visualization |
| Threat actors sidebar | DONE | Lines 553-583 | Tag cloud |
| MITRE ATT&CK sidebar | DONE | Lines 586-621 | Tactics list |

### 2.5 Frontend - Map Mundi (Phase 5)

| Item | Status | Location | Notes |
|------|--------|----------|-------|
| ThreatMap component | DONE | `frontend/src/components/ThreatMap.tsx` | SVG-based world map |
| Country markers | DONE | Lines 304-356 | Pulsing circles with size/color |
| Attack lines | DONE | Lines 359-395 | Bezier curves with animation |
| SOC target marker | DONE | Lines 398-426 | Green pulsing circle |
| Legend | DONE | Lines 202-212 | Risk level colors |
| Country stats overlay | DONE | Lines 430-467 | RU, CN, KP, IR counts |
| geoToSvg projection | DONE | Lines 94-98 | Equirectangular projection |
| generateCurvedPath | DONE | Lines 101-117 | Bezier curve generation |

### 2.6 Unit Tests

| Item | Status | Location | Notes |
|------|--------|----------|-------|
| test_enrichment_limits_to_100_items | DONE | `tests/unit/services/test_enrichment_service.py` | MAX_ITEMS_PER_SOURCE test |
| test_handles_source_failure_gracefully | DONE | Same file | Graceful degradation test |
| test_circuit_breaker_opens_after_5_failures | DONE | `tests/unit/services/test_circuit_breaker.py` | State transition tests |
| test_circuit_breaker_half_open | DONE | Same file | Timeout and recovery tests |
| test_circuit_breaker_resets | DONE | Same file | Success resets failures |
| Integration test | DONE | `tests/integration/test_enrichment_api.py` | API endpoint tests |
| Performance test | DONE | `tests/performance/test_enrichment_performance.py` | 100 IOCs < 1 min test |

---

## 3. Items PENDING (Not Yet Implemented)

### 3.1 Backend Core - Remaining

| Item | Priority | Notes |
|------|----------|-------|
| PostgreSQL tables creation (migrations) | Medium | Models exist but need Alembic migration |
| Database persistence (optional) | Low | In-memory works, DB is optional fallback |

### 3.2 API Clients - Tier 1 (NEW)

| Item | Priority | API Docs |
|------|----------|----------|
| ThreatFox client | HIGH | https://threatfox.abuse.ch/api/ |
| URLhaus client | HIGH | https://urlhaus.abuse.ch/api/ |
| MalwareBazaar client | HIGH | https://bazaar.abuse.ch/api/ |
| IPinfo client | HIGH | https://ipinfo.io/developers |
| Pulsedive client | MEDIUM | https://pulsedive.com/api/ |

### 3.3 API Clients - Tier 2 (NEW)

| Item | Priority | API Docs |
|------|----------|----------|
| VirusTotal client | HIGH | https://developers.virustotal.com/ |
| Shodan client | HIGH | https://developer.shodan.io/ |
| Censys client | MEDIUM | https://search.censys.io/api |
| HaveIBeenPwned client | MEDIUM | https://haveibeenpwned.com/API |

### 3.4 API Clients - Tier 3-4 (NEW)

| Item | Priority | Notes |
|------|----------|-------|
| MITRE ATT&CK client (STIX/TAXII) | HIGH | For proper TTP mapping |
| Feodo Tracker client | HIGH | abuse.ch C2 tracker |
| Cloudflare Radar client | MEDIUM | Traffic insights |
| MISP client | MEDIUM | Self-hosted integration |
| OpenCTI client | MEDIUM | Self-hosted integration |
| Maltiverse client | LOW | Aggregated IOCs |

### 3.5 Synthetic Generators - Remaining

| Item | Priority | Notes |
|------|----------|-------|
| ThreatQuotientMock | HIGH | Context generation, campaigns |
| MandiantMock | HIGH | APT mapping by country/malware |
| MISPMock | LOW | Event/attribute generation |

### 3.6 API Endpoints - NEW

| Endpoint | Priority | Notes |
|----------|----------|-------|
| POST /api/enrichment/threats | PARTIAL | Exists in service, needs router |
| GET /api/enrichment/threats/status/{job_id} | PARTIAL | Exists in service, needs router |
| GET /api/intel/indicators | HIGH | List with pagination |
| GET /api/intel/indicators/{type}/{value} | HIGH | IOC detail |
| GET /api/threats/map | MEDIUM | Map data aggregation |
| GET /api/threats/stats | MEDIUM | KPIs |
| GET /api/threats/countries | MEDIUM | IOCs by country |
| GET /api/threats/actors | MEDIUM | Threat actors list |
| GET /api/threats/malware | MEDIUM | Malware families |
| GET /api/threats/mitre | MEDIUM | MITRE matrix data |
| POST /api/intel/indicators/{}/block | LOW | Action endpoint |
| POST /api/intel/indicators/export | LOW | CSV/STIX export |

### 3.7 Frontend - Additional Views

| Item | Priority | Notes |
|------|----------|-------|
| IOCDetail page with tabs (standalone route) | HIGH | Currently only modal exists |
| ThreatActorList page | MEDIUM | /threats/actors |
| ThreatActorDetail page | MEDIUM | /threats/actors/:name |
| MalwareList page | MEDIUM | /threats/malware |
| MalwareDetail page | MEDIUM | /threats/malware/:family |
| MITREMatrix full page | MEDIUM | Interactive matrix |
| RelationshipGraph component | LOW | Force-directed graph |
| Timeline component | LOW | Risk score evolution |

### 3.8 Frontend - Map Enhancements

| Item | Priority | Notes |
|------|----------|-------|
| Country click panel (detailed) | MEDIUM | Currently only toast |
| Heatmap overlay toggle | LOW | Density visualization |
| 3D globe view (optional) | LOW | globe.gl integration |

### 3.9 MCP Integration

| Item | Priority | Notes |
|------|----------|-------|
| Configure mcp-threatintel server | MEDIUM | External server setup |
| Tool enrichment.threats | MEDIUM | MCP tool registration |
| Tool threats.query | LOW | Query via MCP |
| MCP documentation | LOW | Usage guide |

### 3.10 E2E Tests

| Item | Priority | Notes |
|------|----------|-------|
| threat_enrichment.spec.ts | HIGH | Button, progress, errors |
| threat_map.spec.ts | HIGH | Map loading, interactions |
| ioc_detail.spec.ts | MEDIUM | Modal/page navigation |

---

## 4. Items in Functional Doc Missing from Build Plan

### 4.1 Keyboard Shortcuts

The functional doc (THREAT_ENRICHMENT_DESIGN.md) describes keyboard shortcuts (Ctrl+K command palette, G then M for map, etc.) but these are not in the build plan.

**Recommendation:** Add as Phase 6 polish item.

### 4.2 Command Palette

The design includes a Slack/VSCode-style command palette for quick actions. Not in build plan.

**Recommendation:** Add as optional Phase 6 item.

### 4.3 Export Formats

Design mentions STIX 2.1 and MISP export formats. Build plan has endpoint but no format details.

**Recommendation:** Add format specifications to Phase 3 endpoints.

### 4.4 Real-time Updates

Design mentions "real-time pulse effect" for new threats. Not detailed in build plan.

**Recommendation:** Add WebSocket/SSE consideration for live updates.

---

## 5. Priority Matrix - What to Build Next

### Tier 1: Critical Path (Must Have for Demo)

1. **API Router for /api/enrichment/threats** - Service exists, just needs FastAPI router
2. **ThreatFox client** - High-value free API
3. **URLhaus client** - High-value free API
4. **E2E tests for enrichment flow** - Verify everything works
5. **ThreatQuotientMock** - Better threat context generation
6. **MandiantMock** - APT attribution

### Tier 2: High Value (Should Have)

1. VirusTotal client (if API key available)
2. MITRE ATT&CK client for proper TTP data
3. IOCDetail standalone page
4. /api/threats/stats endpoint
5. /api/threats/map endpoint

### Tier 3: Nice to Have

1. MalwareList/MalwareDetail pages
2. ThreatActorList/ThreatActorDetail pages
3. MITREMatrix full page
4. RelationshipGraph
5. Shodan/Censys clients
6. MCP integration

---

## 6. Technical Debt & Risks

### 6.1 Identified Issues

| Issue | Severity | Mitigation |
|-------|----------|------------|
| No FastAPI router for enrichment endpoints | HIGH | Create router file |
| Synthetic data only (no real APIs connected) | MEDIUM | Add API keys, implement clients |
| Frontend calls API that doesn't exist as route | HIGH | Wire up router |
| No database migrations | LOW | Works in-memory, DB optional |

### 6.2 Performance Concerns

| Concern | Status | Notes |
|---------|--------|-------|
| 100 IOCs < 1 min | ADDRESSED | Limit enforced, test exists |
| Map 60fps with 500+ IOCs | UNKNOWN | Needs E2E performance test |
| Cache hit rate >= 70% | PARTIAL | In-memory cache exists |

---

## 7. Conclusion

The Threat Enrichment System has a solid foundation with:
- Core enrichment service with graceful degradation
- Circuit breaker protection
- Synthetic data generation for demos
- Frontend page with map visualization
- Unit and integration tests

**Immediate priorities:**
1. Create FastAPI router to expose enrichment endpoints
2. Add ThreatFox and URLhaus clients for real threat data
3. Implement ThreatQuotient and Mandiant mocks for richer synthetic data
4. Add E2E tests to validate full flow

**Estimated effort to reach 80% completion:** 8-10 days

---

**Document Author:** Supervision Agent
**Last Updated:** 2026-02-16
