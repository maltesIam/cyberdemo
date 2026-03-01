# Test Plan

| Attribute | Value |
|-----------|-------|
| Version | 1.0.0 |
| Date | 2026-02-25 |
| Build ID | sbx-20260225-222317 |
| Functional Spec | docs/MEDICUM_OPENCLOUD_FUNCTIONAL_SPEC.md |
| Build Plan | docs/MEDICUM_OPENCLOUD_BUILD_PLAN.md |

---

## 1. Test Strategy

### 1.1 Overview

Tests are organized by workstream and follow TDD: write tests first, then implement. NFR requirements are excluded from test scope per stakeholder decision.

### 1.2 Test Types

- **Unit Tests (UT-xxx)**: Test individual functions/modules in isolation with mocked dependencies
- **Integration Tests (IT-xxx)**: Test interactions between components (plugin actions + Anthropic SDK, frontend stores + mcpClient)
- **E2E Tests (E2E-xxx)**: Test complete user flows through the frontend UI

### 1.3 Test Infrastructure

- **Unit Tests**: Vitest (TypeScript) for plugin code
- **Integration Tests**: Vitest with mocked Anthropic API responses
- **E2E Tests**: Playwright for frontend flows

---

## 2. Unit Tests

### WS-1: Data Layer

| Test ID | Requirement | Description | File |
|---------|-------------|-------------|------|
| UT-001 | REQ-003-002-001 | Catalog loads from JSON file successfully | `tests/unit/catalog-loader.test.ts` |
| UT-002 | REQ-003-002-002 | Catalog entries have required fields | `tests/unit/catalog-loader.test.ts` |
| UT-003 | REQ-003-002-003 | Catalog caching returns same instance | `tests/unit/catalog-loader.test.ts` |
| UT-004 | DATA-001 | Catalog contains ~70,000 entries | `tests/unit/catalog-data.test.ts` |
| UT-005 | DATA-002 | Each entry has codigo, descripcion_es, capitulo, subcapitulo | `tests/unit/catalog-data.test.ts` |

### WS-2: Plugin Skeleton

| Test ID | Requirement | Description | File |
|---------|-------------|-------------|------|
| UT-006 | REQ-006-001-001 | Plugin register() exports correctly | `tests/unit/plugin-register.test.ts` |
| UT-007 | REQ-006-002-001 | createMedicumTool returns tool object | `tests/unit/medicum-tool.test.ts` |
| UT-008 | REQ-006-002-002 | Action router dispatches to correct action | `tests/unit/medicum-tool.test.ts` |
| UT-009 | REQ-006-002-003 | Anthropic SDK initialized with config key | `tests/unit/medicum-tool.test.ts` |
| UT-010 | REQ-006-002-004 | Error handling returns { ok: false, error } | `tests/unit/medicum-tool.test.ts` |
| UT-011 | REQ-006-003-001 | Plugin config has all configurable fields | `tests/unit/plugin-config.test.ts` |
| UT-012 | REQ-006-003-002 | Plugin config has sensible defaults | `tests/unit/plugin-config.test.ts` |

### WS-3: SOAP Generation

| Test ID | Requirement | Description | File |
|---------|-------------|-------------|------|
| UT-013 | REQ-001-001-001 | generate-soap accepts required params | `tests/unit/actions/generate-soap.test.ts` |
| UT-014 | REQ-001-001-002 | Formats dialogue from transcription segments | `tests/unit/actions/generate-soap.test.ts` |
| UT-015 | REQ-001-001-003 | Parses JSON response with 5 SOAP fields | `tests/unit/actions/generate-soap.test.ts` |
| UT-016 | REQ-001-001-004 | Includes "[Insufficient information]" markers | `tests/unit/actions/generate-soap.test.ts` |
| UT-017 | REQ-001-002-001 | SOAP prompt has medical specialist context | `tests/unit/prompts/soap-prompt.test.ts` |
| UT-018 | REQ-001-002-002 | Prompt instructs JSON-only output | `tests/unit/prompts/soap-prompt.test.ts` |
| UT-019 | REQ-001-002-003 | Prompt mentions "[Insufficient information]" | `tests/unit/prompts/soap-prompt.test.ts` |

### WS-4: ICD-10 Search

| Test ID | Requirement | Description | File |
|---------|-------------|-------------|------|
| UT-020 | REQ-003-001-001 | search-icd10 accepts query and limit | `tests/unit/actions/search-icd10.test.ts` |
| UT-021 | REQ-003-001-002 | Searches codigo and descripcion fields | `tests/unit/actions/search-icd10.test.ts` |
| UT-022 | REQ-003-001-003 | Returns limited results with total_matches | `tests/unit/actions/search-icd10.test.ts` |

### WS-5: ICD-10 Suggestion

| Test ID | Requirement | Description | File |
|---------|-------------|-------------|------|
| UT-023 | REQ-002-001-001 | suggest-icd10 accepts required params | `tests/unit/actions/suggest-icd10.test.ts` |
| UT-024 | REQ-002-001-002 | Pre-filters catalog to ~50 candidates | `tests/unit/actions/suggest-icd10.test.ts` |
| UT-025 | REQ-002-001-003 | Calls Claude API with candidates | `tests/unit/actions/suggest-icd10.test.ts` |
| UT-026 | REQ-002-001-004 | Returns suggestions with all required fields | `tests/unit/actions/suggest-icd10.test.ts` |
| UT-027 | REQ-002-001-005 | Limits to maxSuggestions count | `tests/unit/actions/suggest-icd10.test.ts` |
| UT-028 | REQ-002-002-001 | ICD-10 prompt has coding specialist context | `tests/unit/prompts/icd10-prompt.test.ts` |
| UT-029 | REQ-002-002-002 | Prompt instructs clinical relevance ranking | `tests/unit/prompts/icd10-prompt.test.ts` |
| UT-030 | REQ-002-002-003 | Prompt instructs rationale per suggestion | `tests/unit/prompts/icd10-prompt.test.ts` |

### WS-6: Image Analysis

| Test ID | Requirement | Description | File |
|---------|-------------|-------------|------|
| UT-031 | REQ-004-001-001 | analyze-image accepts full parameter set | `tests/unit/actions/analyze-image.test.ts` |
| UT-032 | REQ-004-001-002 | Calls Claude Vision API with base64 image | `tests/unit/actions/analyze-image.test.ts` |
| UT-033 | REQ-004-001-003 | Returns findings with severity and confidence | `tests/unit/actions/analyze-image.test.ts` |
| UT-034 | REQ-004-001-004 | Includes ai_disclaimer in response | `tests/unit/actions/analyze-image.test.ts` |
| UT-035 | REQ-004-002-001 | Image prompt has imaging specialist context | `tests/unit/prompts/image-prompt.test.ts` |
| UT-036 | REQ-004-002-002 | Prompt supports X-ray, CT, MRI, ultrasound | `tests/unit/prompts/image-prompt.test.ts` |
| UT-037 | REQ-004-002-003 | Prompt instructs severity classification | `tests/unit/prompts/image-prompt.test.ts` |

### WS-7: Report Generation

| Test ID | Requirement | Description | File |
|---------|-------------|-------------|------|
| UT-038 | REQ-005-001-001 | generate-report accepts required params | `tests/unit/actions/generate-report.test.ts` |
| UT-039 | REQ-005-001-002 | Calls Claude API for structured report | `tests/unit/actions/generate-report.test.ts` |
| UT-040 | REQ-005-001-003 | Returns all report sections | `tests/unit/actions/generate-report.test.ts` |
| UT-041 | REQ-005-002-001 | Report prompt has specialist context | `tests/unit/prompts/report-prompt.test.ts` |
| UT-042 | REQ-005-002-002 | Prompt enforces standard format | `tests/unit/prompts/report-prompt.test.ts` |

### WS-8: Frontend Integration

| Test ID | Requirement | Description | File |
|---------|-------------|-------------|------|
| UT-043 | REQ-007-001-001 | generateSOAPNote calls mcpClient | `tests/unit/stores/transcriptionStore.test.ts` |
| UT-044 | REQ-007-001-002 | isGeneratingSOAP state managed correctly | `tests/unit/stores/transcriptionStore.test.ts` |
| UT-045 | REQ-007-001-003 | Falls back to DEMO_SOAP on error | `tests/unit/stores/transcriptionStore.test.ts` |
| UT-046 | REQ-007-002-001 | loadSuggestions calls mcpClient suggest_icd10 | `tests/unit/stores/codingStore.test.ts` |
| UT-047 | REQ-007-002-002 | searchCodes calls mcpClient search_icd10 | `tests/unit/stores/codingStore.test.ts` |
| UT-048 | REQ-007-002-003 | Loading states managed in coding store | `tests/unit/stores/codingStore.test.ts` |
| UT-049 | REQ-007-002-004 | Coding store falls back to demo data | `tests/unit/stores/codingStore.test.ts` |
| UT-050 | REQ-007-003-001 | analyzeImage calls mcpClient analyze_image | `tests/unit/stores/imageStore.test.ts` |
| UT-051 | REQ-007-003-002 | isAnalyzing state managed correctly | `tests/unit/stores/imageStore.test.ts` |
| UT-052 | REQ-007-003-003 | Image store falls back to demo data | `tests/unit/stores/imageStore.test.ts` |

### WS-9: Safety Hooks

| Test ID | Requirement | Description | File |
|---------|-------------|-------------|------|
| UT-053 | REQ-008-001-001 | Disclaimer hook activates for image/report actions | `tests/unit/hooks/disclaimer-hook.test.ts` |
| UT-054 | REQ-008-001-002 | Disclaimer hook verifies ai_disclaimer field | `tests/unit/hooks/disclaimer-hook.test.ts` |
| UT-055 | REQ-008-002-001 | Audit hook activates for any medicum action | `tests/unit/hooks/audit-hook.test.ts` |
| UT-056 | REQ-008-002-002 | Audit hook logs without PII | `tests/unit/hooks/audit-hook.test.ts` |
| UT-057 | REQ-008-003-001 | Validation hook activates before suggest_icd10 | `tests/unit/hooks/validation-hook.test.ts` |
| UT-058 | REQ-008-003-002 | Validation hook verifies codes in catalog | `tests/unit/hooks/validation-hook.test.ts` |

### TECH/INT/DATA Cross-cutting

| Test ID | Requirement | Description | File |
|---------|-------------|-------------|------|
| UT-059 | TECH-001 | Plugin compiles TypeScript to JS | `tests/unit/plugin-build.test.ts` |
| UT-060 | TECH-002 | Anthropic SDK used for API calls | `tests/unit/medicum-tool.test.ts` |
| UT-061 | TECH-003 | API error handling doesn't crash | `tests/unit/medicum-tool.test.ts` |
| UT-062 | TECH-004 | Actions are in separate files | `tests/unit/plugin-structure.test.ts` |
| UT-063 | TECH-005 | Prompts are in prompts directory | `tests/unit/plugin-structure.test.ts` |
| UT-064 | TECH-006 | Catalog caching works | `tests/unit/catalog-loader.test.ts` |
| UT-065 | INT-001 | Plugin registers via api.registerTool | `tests/unit/plugin-register.test.ts` |
| UT-066 | INT-002 | Frontend uses mcpClient.request | `tests/unit/stores/mcpClient.test.ts` |
| UT-067 | DATA-003 | Catalog file within size limits | `tests/unit/catalog-data.test.ts` |
| UT-068 | DATA-004 | Demo constants retained as fallback | `tests/unit/stores/fallback.test.ts` |
| UT-069 | REQ-006-001-002 | Plugin manifest has valid JSON schema | `tests/unit/plugin-config.test.ts` |
| UT-070 | REQ-006-001-003 | Package.json has anthropic dependency | `tests/unit/plugin-config.test.ts` |
| UT-071 | INT-005 | Gateway restart script exists and is executable | `tests/unit/deployment.test.ts` |

### NFR — EXCLUDED (no verification needed)

| Test ID | Requirement | Description | File |
|---------|-------------|-------------|------|
| UT-072 | NFR-001 | EXCLUDED — SOAP generation performance | — |
| UT-073 | NFR-002 | EXCLUDED — ICD-10 search performance | — |
| UT-074 | NFR-003 | EXCLUDED — Image analysis performance | — |
| UT-075 | NFR-004 | EXCLUDED — API key security | — |
| UT-076 | NFR-005 | EXCLUDED — Audit log PII | — |
| UT-077 | NFR-006 | EXCLUDED — Availability fallback | — |
| UT-078 | NFR-007 | EXCLUDED — Error handling resilience | — |
| UT-079 | NFR-008 | EXCLUDED — Catalog loading scalability | — |
| UT-080 | NFR-009 | EXCLUDED — File structure usability | — |

---

## 3. Integration Tests

| Test ID | Requirement | Description | File |
|---------|-------------|-------------|------|
| IT-001 | REQ-001-001-002 | SOAP action → Anthropic API mock → JSON response | `tests/integration/soap-flow.test.ts` |
| IT-002 | REQ-002-001-003 | Suggest action → pre-filter → Anthropic API mock → ranked results | `tests/integration/suggest-flow.test.ts` |
| IT-003 | REQ-003-001-002 | Search action → catalog → filtered results | `tests/integration/search-flow.test.ts` |
| IT-004 | REQ-004-001-002 | Image action → Anthropic Vision API mock → findings | `tests/integration/image-flow.test.ts` |
| IT-005 | REQ-005-001-002 | Report action → Anthropic API mock → structured report | `tests/integration/report-flow.test.ts` |
| IT-006 | REQ-006-002-002 | Action router → correct action → response | `tests/integration/action-router.test.ts` |
| IT-007 | INT-001 | Plugin registers and responds to tool calls | `tests/integration/plugin-register.test.ts` |
| IT-008 | INT-002 | Frontend store → mcpClient → gateway mock → response | `tests/integration/frontend-gateway.test.ts` |
| IT-009 | INT-003 | Plugin deploys to container extensions path | `tests/integration/deployment.test.ts` |
| IT-010 | INT-004 | Plugin registered in moltbot.json | `tests/integration/deployment.test.ts` |

---

## 4. E2E Tests (Playwright)

| Test ID | Requirement | Description | File |
|---------|-------------|-------------|------|
| E2E-001 | REQ-007-001-001 | User triggers SOAP generation from transcription UI | `tests/e2e/soap-generation.spec.ts` |
| E2E-002 | REQ-007-002-001 | User sees ICD-10 suggestions in coding panel | `tests/e2e/icd10-suggestion.spec.ts` |
| E2E-003 | REQ-007-002-002 | User searches ICD-10 codes and sees results | `tests/e2e/icd10-search.spec.ts` |
| E2E-004 | REQ-007-003-001 | User uploads image and sees analysis results | `tests/e2e/image-analysis.spec.ts` |
| E2E-005 | REQ-007-001-003 | UI falls back to demo data when gateway unavailable | `tests/e2e/fallback-behavior.spec.ts` |

---

## 5. Test Summary

| Category | Count |
|----------|-------|
| Unit Tests (UT-xxx) | 71 |
| Integration Tests (IT-xxx) | 10 |
| E2E Tests (E2E-xxx) | 5 |
| **Total Tests** | **86** |
| Requirements Covered | 73 (NFR excluded) |

---

## 6. Excluded from Testing

NFR-001 through NFR-009 are excluded from test scope per stakeholder decision.
