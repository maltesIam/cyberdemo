# Medicum OpenCloud — Progress

| Attribute | Value |
|-----------|-------|
| Version | 1.0.0 |
| Date | 2026-02-25 |
| Build ID | sbx-20260225-222317 |
| Functional Spec | docs/MEDICUM_OPENCLOUD_FUNCTIONAL_SPEC.md |
| Build Plan | docs/MEDICUM_OPENCLOUD_BUILD_PLAN.md |

---

## Overall Progress

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 1: Data + Plugin Skeleton | Pending | 0% |
| Phase 2: Actions (SOAP, Search, Image, Report) | Pending | 0% |
| Phase 3: ICD-10 Suggestion | Pending | 0% |
| Phase 4: Frontend Integration | Pending | 0% |
| Phase 5: Safety Hooks | Pending | 0% |
| **Total** | **Pending** | **0%** |

---

## Phase 1: Data Layer + Plugin Skeleton

### WS-1: Data Layer and Catalog (8 tasks)

- [ ] T-DATA-001 — ICD-10 catalog with ~70,000 codes
- [ ] T-DATA-002 — Catalog JSON array with required fields
- [ ] T-DATA-003 — Catalog file ~15-20 MB
- [ ] T-DATA-004 — Retain demo constants as fallback
- [ ] T-003-002 — ICD-10 catalog JSON in data directory
- [ ] T-003-003 — Entry fields: codigo, descripcion_es, capitulo, subcapitulo
- [ ] T-003-004 — Efficient catalog loading with caching
- [ ] T-TECH-006 — Catalog loaded once and cached in memory

### WS-2: Plugin Skeleton and Structure (18 tasks)

- [ ] T-006-001 — Create index.ts with register(api)
- [ ] T-006-002 — Create openclaw.plugin.json manifest
- [ ] T-006-003 — Create package.json with anthropic SDK
- [ ] T-006-004 — Create medicum-tool.ts with createMedicumTool(api)
- [ ] T-006-005 — Action router dispatching to 5 actions
- [ ] T-006-006 — Initialize Anthropic SDK with API key
- [ ] T-006-007 — Error handling with { ok: false, error: message }
- [ ] T-006-008 — Configurable fields in plugin config
- [ ] T-006-009 — Sensible defaults for all config fields
- [ ] T-TECH-001 — TypeScript compiled to JS
- [ ] T-TECH-002 — All Claude API calls use Anthropic SDK
- [ ] T-TECH-003 — Handle API errors without crashing gateway
- [ ] T-TECH-004 — Each action in separate file
- [ ] T-TECH-005 — System prompts in separate files
- [ ] T-INT-001 — Register with OpenClaw via api.registerTool
- [ ] T-INT-003 — Deploy to Docker container
- [ ] T-INT-004 — Register in moltbot.json
- [ ] T-INT-005 — Gateway restart after deployment

---

## Phase 2: Actions (SOAP, Search, Image, Report)

### WS-3: SOAP Note Generation (7 tasks)

- [ ] T-001-001 — Create generate-soap.ts
- [ ] T-001-002 — Call Claude API with formatted dialogue
- [ ] T-001-003 — Parse response as JSON with 5 SOAP fields
- [ ] T-001-004 — Include "[Insufficient information]" markers
- [ ] T-001-005 — Create soap-prompt.ts
- [ ] T-001-006 — Prompt instructs JSON-only output
- [ ] T-001-007 — Prompt instructs "[Insufficient information]"

### WS-4: ICD-10 Search (3 tasks)

- [ ] T-003-001 — Create search-icd10.ts
- [ ] T-003-005 — Deterministic text search on codigo and descripcion
- [ ] T-003-006 — Return limited results with total_matches

### WS-6: Image Analysis (7 tasks)

- [ ] T-004-001 — Create analyze-image.ts
- [ ] T-004-002 — Call Claude Vision API with base64 image
- [ ] T-004-003 — Return findings with severity and confidence
- [ ] T-004-004 — Include ai_disclaimer in response
- [ ] T-004-005 — Create image-prompt.ts
- [ ] T-004-006 — Support X-ray, CT, MRI, ultrasound
- [ ] T-004-007 — Classify findings by severity

### WS-7: Report Generation (5 tasks)

- [ ] T-005-001 — Create generate-report.ts
- [ ] T-005-002 — Call Claude API for structured report
- [ ] T-005-003 — Return: header, technique, findings, conclusion, recommendations
- [ ] T-005-004 — Create report-prompt.ts
- [ ] T-005-005 — Enforce standard radiology format

---

## Phase 3: ICD-10 Suggestion

### WS-5: ICD-10 Suggestion (8 tasks)

- [ ] T-002-001 — Create suggest-icd10.ts
- [ ] T-002-002 — Pre-filter catalog to ~50 candidates
- [ ] T-002-003 — Call Claude API with candidates for ranking
- [ ] T-002-004 — Return: code, description, confidence, rationale, is_primary
- [ ] T-002-005 — Limit suggestions to maxSuggestions
- [ ] T-002-006 — Create icd10-prompt.ts
- [ ] T-002-007 — Prompt instructs ranking by clinical relevance
- [ ] T-002-008 — Prompt instructs rationale per suggestion

---

## Phase 4: Frontend Store Integration

### WS-8: Frontend Integration (11 tasks)

- [ ] T-007-001 — Modify generateSOAPNote() for mcpClient
- [ ] T-007-002 — Add isGeneratingSOAP loading state
- [ ] T-007-003 — Fallback to DEMO_SOAP
- [ ] T-007-004 — Modify loadSuggestions() for gateway
- [ ] T-007-005 — Modify searchCodes() for gateway
- [ ] T-007-006 — Add loading states for coding store
- [ ] T-007-007 — Fallback to demo data (coding)
- [ ] T-007-008 — Modify analyzeImage() for gateway
- [ ] T-007-009 — Add isAnalyzing loading state
- [ ] T-007-010 — Fallback to demo data (image)
- [ ] T-INT-002 — Frontend stores via mcpClient.request

---

## Phase 5: Safety Hooks

### WS-9: Safety Hooks (6 tasks)

- [ ] T-008-001 — Post-tool hook for analyze_image/generate_report (MTH)
- [ ] T-008-002 — Verify ai_disclaimer field (MTH)
- [ ] T-NTH-001 — Post-tool hook for audit logging (NTH)
- [ ] T-NTH-002 — Log timestamp, action, input, output (NTH)
- [ ] T-NTH-003 — Pre-tool hook for suggest_icd10 validation (NTH)
- [ ] T-NTH-004 — Validate codes exist in ICD-10 catalog (NTH)

---

## Excluded (NFR — No Build/Test)

NFR-001 through NFR-009 excluded per stakeholder decision.

---

## Change Log

| Date | Change |
|------|--------|
| 2026-02-25 | Initial progress document created |
