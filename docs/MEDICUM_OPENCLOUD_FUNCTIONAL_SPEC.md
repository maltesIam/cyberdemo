# Medicum OpenCloud — Functional Specification

| Attribute | Value |
|-----------|-------|
| Version | 1.0.0 |
| Date | 2026-02-25 |
| Status | Draft |
| Project | Medicum OpenCloud — Replace Simulated Features with Real AI |
| Platform | OpenClaw Gateway + SoulBot (Claude) |
| SBX Version | 23.0.0 |

---

# PART 1: FUNCTIONAL DESCRIPTION

## 1.1 Executive Summary

Medicum is a medical consultation assistant frontend (React + Vite) that currently uses hardcoded demo data for core clinical features: SOAP note generation, ICD-10 coding, medical image analysis, and radiology reports. This project replaces ALL simulated functionality with real AI-powered processing using Claude (via an OpenClaw Gateway plugin called `medicum-ai`), following the exact same architectural pattern already proven in the CyberDemo plugin.

The system will create a single OpenClaw plugin (`medicum-ai`) with 5 deterministic actions that call Claude API, integrate it with the existing frontend stores via the MCP WebSocket client, and ensure all medical AI outputs include appropriate disclaimers and audit logging.

## 1.2 System Overview

### 1.2.1 Purpose

Replace every piece of simulated/hardcoded functionality in the Medicum frontend with real AI-powered processing through the OpenClaw Gateway, achieving the principle: "Nothing simulated, everything real."

### 1.2.2 Scope

- **In Scope**: OpenClaw plugin development (`medicum-ai`), frontend store integration, ICD-10 catalog data, medical AI prompts, disclaimer hooks, audit logging
- **Out of Scope**: Whisper transcription (already functional), patient data management (already functional), VAD (already functional), SNOMED CT integration (future), WhatsApp integration

### 1.2.3 Context

The system operates within this architecture:

```
Frontend (React/Vite, port 3000)
    → Vite proxy → WebSocket to OpenClaw Gateway (Docker, port 18789)
        → SoulBot Agent (Claude) → Plugin medicum-ai
            → Claude API (Anthropic) for AI processing
```

The CyberDemo plugin (`extensions/cyberdemo/`) is the reference implementation with 30+ actions and the exact pattern to follow.

## 1.3 User Roles and Personas

| ID | User Role | Description | Key Actions |
|----|-----------|-------------|-------------|
| P-001 | Medical Doctor | Primary user conducting patient consultations | Triggers SOAP generation, reviews AI suggestions, validates ICD-10 codes |
| P-002 | Radiologist | Specialist reviewing medical images | Uploads images for AI analysis, reviews and edits generated reports |
| P-003 | Medical Coder | Administrative staff assigning billing codes | Searches ICD-10 catalog, reviews AI code suggestions, assigns final codes |
| P-004 | System Administrator | Manages OpenClaw gateway and plugin configuration | Deploys plugin, configures API keys, monitors audit logs |

## 1.4 Functional Areas

### FA-001: SOAP Note Generation

**Description**: Replace the hardcoded `DEMO_SOAP` constant with real Claude-powered analysis of transcription segments to generate contextual SOAP notes.

| ID | Type | Description |
|----|------|-------------|
| US-001 | User Story | As a doctor, I want the system to automatically generate a SOAP note from my consultation transcription so that I don't have to write it manually |
| US-002 | User Story | As a doctor, I want the SOAP note to consider the patient's pre-existing conditions and medications so that the analysis is contextually accurate |
| BR-001 | Business Rule | SOAP notes must include all four sections: Subjective, Objective, Analysis, Plan |
| BR-002 | Business Rule | If transcription data is insufficient, the system must indicate "[Insufficient information]" rather than hallucinating content |
| BR-003 | Business Rule | SOAP generation must include a confidence score (0-1) for the overall note quality |

### FA-002: ICD-10 Code Suggestion

**Description**: Replace the hardcoded `DEMO_SUGGESTIONS` array (4 fixed codes) with Claude-powered ranking of relevant ICD-10 codes from a complete catalog of ~70,000 codes.

| ID | Type | Description |
|----|------|-------------|
| US-003 | User Story | As a medical coder, I want the system to suggest relevant ICD-10 codes based on the diagnosis text so that I can code consultations faster |
| US-004 | User Story | As a doctor, I want ICD-10 suggestions to consider the SOAP note and patient history so that codes are contextually relevant |
| BR-004 | Business Rule | The system must pre-filter the catalog to ~50 candidates before sending to Claude for ranking, to reduce cost and latency |
| BR-005 | Business Rule | Each suggestion must include: code, description, confidence (0-1), rationale, and is_primary flag |
| BR-006 | Business Rule | Maximum 10 suggestions returned by default (configurable) |

### FA-003: ICD-10 Catalog Search

**Description**: Replace the hardcoded `DEMO_ICD10_CATALOG` (10 codes) with a full catalog search of ~70,000 ICD-10 codes.

| ID | Type | Description |
|----|------|-------------|
| US-005 | User Story | As a medical coder, I want to search the complete ICD-10 catalog by code or description so that I can find the right code for any diagnosis |
| BR-007 | Business Rule | Search must be deterministic (no LLM) — pure text matching on code and description fields |
| BR-008 | Business Rule | Search returns maximum 20 results by default (configurable via limit parameter) |
| BR-009 | Business Rule | The ICD-10 catalog must contain ~70,000 codes with fields: codigo, descripcion_es, capitulo, subcapitulo |

### FA-004: Medical Image Analysis

**Description**: Replace the `setTimeout(2000)` + hardcoded `DEMO_KNEE_FINDINGS` with real Claude Vision analysis of medical images.

| ID | Type | Description |
|----|------|-------------|
| US-006 | User Story | As a radiologist, I want to upload a medical image and receive AI-powered analysis with findings classified by severity so that I have a starting point for my report |
| US-007 | User Story | As a doctor, I want image analysis to consider the clinical indication and patient context so that findings are clinically relevant |
| BR-010 | Business Rule | Image analysis must support X-ray, CT, MRI, and ultrasound modalities |
| BR-011 | Business Rule | Each finding must include severity classification and confidence score |
| BR-012 | Business Rule | Results must include an AI disclaimer stating that findings require professional medical validation |
| BR-013 | Business Rule | Image is sent as base64 to Claude Vision — the model actually examines the image |

### FA-005: Radiology Report Generation

**Description**: Replace the hardcoded `DEMO_KNEE_REPORT` template with Claude-generated professional radiology reports based on actual image analysis findings.

| ID | Type | Description |
|----|------|-------------|
| US-008 | User Story | As a radiologist, I want the system to generate a professional radiology report from the image analysis findings so that I can review and sign it |
| BR-014 | Business Rule | Reports must follow standard radiology format: header, technique, findings, conclusion, recommendations |
| BR-015 | Business Rule | Reports must be generated from actual analysis findings, not templates |

### FA-006: OpenClaw Plugin Architecture

**Description**: Create the `medicum-ai` plugin following the CyberDemo pattern: single tool with multiple actions, registered via `api.registerTool()`.

| ID | Type | Description |
|----|------|-------------|
| US-009 | User Story | As a system administrator, I want a single plugin that handles all medical AI actions so that deployment and configuration is simple |
| US-010 | User Story | As a system administrator, I want the plugin to be configurable (API key, model, language, max suggestions) so that I can tune it for different environments |
| BR-016 | Business Rule | Plugin must follow the exact CyberDemo pattern: one tool "medicum" with action parameter selecting the specific action |
| BR-017 | Business Rule | Plugin must use the Anthropic SDK to call Claude API directly for each action |
| BR-018 | Business Rule | Each action must have its own dedicated system prompt optimized for the specific medical task |

### FA-007: Frontend Store Integration

**Description**: Modify the existing Zustand stores to call the gateway via MCP WebSocket instead of using demo constants.

| ID | Type | Description |
|----|------|-------------|
| US-011 | User Story | As a doctor, I want the existing UI to work the same way but with real AI results instead of demo data so that the transition is seamless |
| BR-019 | Business Rule | Each store function must call `mcpClient.request('tools/call', ...)` with the appropriate medicum action |
| BR-020 | Business Rule | Each store function must include a fallback to demo data if the gateway is unavailable, with a console warning |
| BR-021 | Business Rule | Loading states must be properly managed (isGenerating, isAnalyzing flags) during async operations |

### FA-008: Medical AI Safety and Audit

**Description**: Implement hooks for AI disclaimer enforcement, medical audit logging, and ICD-10 validation.

| ID | Type | Description |
|----|------|-------------|
| US-012 | User Story | As a compliance officer, I want all medical AI operations to be audited so that we have a trail for regulatory review |
| US-013 | User Story | As a patient safety officer, I want all image analysis and report outputs to include an AI disclaimer so that users know results require professional validation |
| BR-022 | Business Rule | Post-tool hook must verify AI disclaimer presence in analyze_image and generate_report responses |
| BR-023 | Business Rule | Audit hook must log timestamp, action, input summary (without sensitive patient data), and output summary |
| BR-024 | Business Rule | Pre-tool hook must validate that all suggested ICD-10 codes exist in the official catalog |

## 1.5 Non-Functional Requirements Summary

| Category | Requirement |
|----------|-------------|
| Performance | SOAP generation must complete within 10 seconds |
| Performance | ICD-10 catalog search must complete within 500ms (deterministic, no LLM) |
| Performance | Image analysis must complete within 30 seconds |
| Security | Anthropic API key must be stored in plugin config, never exposed to frontend |
| Security | Audit logs must not contain sensitive patient data (PII) |
| Availability | Frontend must gracefully fall back to demo data if gateway is unavailable |
| Availability | Plugin must handle Claude API errors without crashing the gateway |
| Scalability | ICD-10 catalog (~70,000 entries, ~15-20MB JSON) must be loaded efficiently |
| Usability | Each action must be in a separate file following the CyberDemo pattern for maintainability |

## 1.6 Assumptions and Dependencies

| ID | Assumption/Dependency |
|----|----------------------|
| A-001 | OpenClaw Gateway is running in Docker container `soulinthebot-gateway` on port 18789 |
| A-002 | CyberDemo plugin is already functional and serves as the reference pattern |
| A-003 | Whisper transcription is already functional and provides real transcription segments |
| A-004 | MCP WebSocket client (`mcpClient.ts`) is already functional in the frontend |
| A-005 | Valid Anthropic API key is available for Claude API calls |
| D-001 | Anthropic SDK (`@anthropic-ai/sdk`) must be installed in the plugin |
| D-002 | ICD-10 catalog JSON file (~70,000 codes) must be sourced and included |
| D-003 | Claude model must support Vision (for image analysis action) |

## 1.7 Constraints

| ID | Constraint |
|----|-----------|
| C-001 | Must follow the exact CyberDemo plugin pattern (single tool, multiple actions) |
| C-002 | Plugin runs inside the Docker container, so all paths are container-relative |
| C-003 | Frontend communicates only via WebSocket through Vite proxy — no direct HTTP calls to gateway |
| C-004 | All medical AI responses are informational — system must NOT present itself as providing medical diagnoses |

## 1.8 Project Context

This is an **existing codebase** project. Key existing files:

| Component | File | Status |
|-----------|------|--------|
| Frontend Transcription Store | `src/stores/transcriptionStore.ts` | Has DEMO_SOAP, DEMO_TRANSCRIPTION — needs modification |
| Frontend Coding Store | `src/stores/codingStore.ts` | Has DEMO_SUGGESTIONS, DEMO_ICD10_CATALOG — needs modification |
| Frontend Image Store | `src/stores/imageStore.ts` | Has DEMO_KNEE_FINDINGS, DEMO_KNEE_REPORT — needs modification |
| MCP Client | `src/services/mcpClient.ts` | Functional — no changes needed |
| CyberDemo Plugin | `extensions/cyberdemo/` | Reference pattern — no changes needed |
| Gateway Config | `/root/.soulinthebot/moltbot.json` | Needs medicum-ai plugin registration |

---

# PART 2: TECHNICAL REQUIREMENTS

## 2.1 Requirements Traceability Matrix

All requirements trace back to user stories (US-xxx) and business rules (BR-xxx) from Part 1. Each functional area maps to an Epic containing Features and individual Requirements.

| Part 1 Source | Part 2 Coverage | Type |
|---------------|-----------------|------|
| US-001, US-002 | EPIC-001, FEAT-001-001, FEAT-001-002 | SOAP Generation |
| US-003, US-004 | EPIC-002, FEAT-002-001, FEAT-002-002 | ICD-10 Suggestion |
| US-005 | EPIC-003, FEAT-003-001, FEAT-003-002 | ICD-10 Search |
| US-006, US-007 | EPIC-004, FEAT-004-001, FEAT-004-002 | Image Analysis |
| US-008 | EPIC-005, FEAT-005-001, FEAT-005-002 | Report Generation |
| US-009, US-010 | EPIC-006, FEAT-006-001, FEAT-006-002, FEAT-006-003 | Plugin Structure |
| US-011 | EPIC-007, FEAT-007-001, FEAT-007-002, FEAT-007-003 | Frontend Integration |
| US-012, US-013 | EPIC-008, FEAT-008-001, FEAT-008-002, FEAT-008-003 | Safety and Audit |

## 2.2 Requirements Numbering Convention

```
EPIC-xxx           → Epic (one per functional area)
FEAT-xxx-yyy       → Feature within an Epic
REQ-xxx-yyy-zzz    → Requirement within a Feature
TECH-xxx           → Technical (cross-cutting) requirement
INT-xxx            → Integration requirement
DATA-xxx           → Data requirement
```

## 2.3 Priority Classification

| Priority | Code | Meaning |
|----------|------|---------|
| Must Have | MTH | Essential for MVP — system doesn't work without it |
| Nice to Have | NTH | Valuable but can be deferred — system works without it |

---

## 2.4 Epics, Features, and Requirements

### EPIC-001: SOAP Note Generation Plugin Action (MTH)

**Source**: FA-001 (US-001, US-002, BR-001, BR-002, BR-003)

#### FEAT-001-001: Generate SOAP Action Implementation (MTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-001-001-001 | Create `actions/generate-soap.ts` that accepts transcription_segments and patient_context parameters | MTH | US-001 |
| REQ-001-001-002 | Call Claude API with formatted dialogue from transcription segments and patient context | MTH | US-001, US-002 |
| REQ-001-001-003 | Parse Claude response as JSON returning { subjetivo, objetivo, analisis, plan, confidence } | MTH | BR-001, BR-003 |
| REQ-001-001-004 | Include "[Insufficient information]" markers when transcription data is insufficient | MTH | BR-002 |

#### FEAT-001-002: SOAP System Prompt (MTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-001-002-001 | Create `prompts/soap-prompt.ts` with medical documentation specialist system prompt | MTH | BR-001 |
| REQ-001-002-002 | Prompt must instruct Claude to output JSON-only with the 5 SOAP fields | MTH | BR-001, BR-003 |
| REQ-001-002-003 | Prompt must instruct Claude to use "[Insufficient information]" for missing data | MTH | BR-002 |

---

### EPIC-002: ICD-10 Code Suggestion Plugin Action (MTH)

**Source**: FA-002 (US-003, US-004, BR-004, BR-005, BR-006)

#### FEAT-002-001: Suggest ICD-10 Action Implementation (MTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-002-001-001 | Create `actions/suggest-icd10.ts` that accepts diagnosis_text, soap_note, and patient_conditions | MTH | US-003 |
| REQ-002-001-002 | Pre-filter ICD-10 catalog to ~50 candidates using text search before sending to Claude | MTH | BR-004 |
| REQ-002-001-003 | Call Claude API with candidates, diagnosis, SOAP note, and conditions for ranking | MTH | US-003, US-004 |
| REQ-002-001-004 | Return suggestions with fields: code, description, confidence, rationale, is_primary | MTH | BR-005 |
| REQ-002-001-005 | Limit returned suggestions to maxSuggestions config value (default 10) | MTH | BR-006 |

#### FEAT-002-002: ICD-10 Suggestion System Prompt (MTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-002-002-001 | Create `prompts/icd10-prompt.ts` with clinical coding specialist system prompt | MTH | US-003 |
| REQ-002-002-002 | Prompt must instruct Claude to rank candidates by clinical relevance | MTH | BR-005 |
| REQ-002-002-003 | Prompt must instruct Claude to provide rationale for each suggestion | MTH | BR-005 |

---

### EPIC-003: ICD-10 Catalog Search Plugin Action (MTH)

**Source**: FA-003 (US-005, BR-007, BR-008, BR-009)

#### FEAT-003-001: Search ICD-10 Action Implementation (MTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-003-001-001 | Create `actions/search-icd10.ts` that accepts query and limit parameters | MTH | US-005 |
| REQ-003-001-002 | Implement deterministic text search (no LLM) on codigo and descripcion fields | MTH | BR-007 |
| REQ-003-001-003 | Return results limited to the limit parameter (default 20) with total_matches count | MTH | BR-008 |

#### FEAT-003-002: ICD-10 Catalog Data (MTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-003-002-001 | Include ICD-10 catalog JSON with ~70,000 codes in `data/icd10-catalog.json` | MTH | BR-009 |
| REQ-003-002-002 | Each entry must have fields: codigo, descripcion_es, capitulo, subcapitulo | MTH | BR-009 |
| REQ-003-002-003 | Implement efficient catalog loading with caching to avoid repeated file reads | MTH | NFR-008 |

---

### EPIC-004: Medical Image Analysis Plugin Action (MTH)

**Source**: FA-004 (US-006, US-007, BR-010, BR-011, BR-012, BR-013)

#### FEAT-004-001: Analyze Image Action Implementation (MTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-004-001-001 | Create `actions/analyze-image.ts` that accepts image_base64, image_type, body_region, clinical_indication, patient_context | MTH | US-006 |
| REQ-004-001-002 | Call Claude Vision API with base64 image and text context for real image analysis | MTH | BR-013 |
| REQ-004-001-003 | Return findings with severity classification and confidence scores | MTH | BR-011 |
| REQ-004-001-004 | Include AI disclaimer in response (ai_disclaimer field) | MTH | BR-012 |

#### FEAT-004-002: Image Analysis System Prompt (MTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-004-002-001 | Create `prompts/image-prompt.ts` with diagnostic imaging specialist system prompt | MTH | US-006 |
| REQ-004-002-002 | Prompt must support X-ray, CT, MRI, and ultrasound modalities | MTH | BR-010 |
| REQ-004-002-003 | Prompt must instruct Claude to classify findings by severity and assign confidence | MTH | BR-011 |

---

### EPIC-005: Radiology Report Generation Plugin Action (MTH)

**Source**: FA-005 (US-008, BR-014, BR-015)

#### FEAT-005-001: Generate Report Action Implementation (MTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-005-001-001 | Create `actions/generate-report.ts` that accepts findings, study_info, patient_info | MTH | US-008 |
| REQ-005-001-002 | Call Claude API to generate structured radiology report from findings | MTH | BR-015 |
| REQ-005-001-003 | Return report with sections: header, technique, findings, conclusion, recommendations | MTH | BR-014 |

#### FEAT-005-002: Report Generation System Prompt (MTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-005-002-001 | Create `prompts/report-prompt.ts` with radiology report specialist system prompt | MTH | BR-014 |
| REQ-005-002-002 | Prompt must enforce standard radiology report format | MTH | BR-014 |

---

### EPIC-006: OpenClaw Plugin Structure (MTH)

**Source**: FA-006 (US-009, US-010, BR-016, BR-017, BR-018)

#### FEAT-006-001: Plugin Registration and Entry Point (MTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-006-001-001 | Create `extensions/medicum-ai/index.ts` with register(api) following CyberDemo pattern | MTH | BR-016 |
| REQ-006-001-002 | Create `extensions/medicum-ai/openclaw.plugin.json` manifest with configSchema | MTH | US-010 |
| REQ-006-001-003 | Create `extensions/medicum-ai/package.json` with anthropic SDK dependency | MTH | D-001 |

#### FEAT-006-002: Tool Handler and Action Router (MTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-006-002-001 | Create `src/medicum-tool.ts` with createMedicumTool(api) function | MTH | BR-016 |
| REQ-006-002-002 | Implement action router (switch statement) dispatching to generate_soap, suggest_icd10, search_icd10, analyze_image, generate_report | MTH | BR-016 |
| REQ-006-002-003 | Initialize Anthropic SDK with API key from config or environment variable | MTH | BR-017 |
| REQ-006-002-004 | Implement error handling returning { ok: false, error: message } on failure | MTH | NFR-007 |

#### FEAT-006-003: Plugin Configuration (MTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-006-003-001 | Support configurable fields: anthropicApiKey, model, icd10CatalogPath, maxSuggestions, language | MTH | US-010 |
| REQ-006-003-002 | Provide sensible defaults for all config fields | MTH | US-010 |

---

### EPIC-007: Frontend Store Integration (MTH)

**Source**: FA-007 (US-011, BR-019, BR-020, BR-021)

#### FEAT-007-001: Transcription Store Integration (MTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-007-001-001 | Modify `generateSOAPNote()` in `transcriptionStore.ts` to call gateway via mcpClient with action generate_soap | MTH | BR-019 |
| REQ-007-001-002 | Add isGeneratingSOAP loading state and manage it during async operation | MTH | BR-021 |
| REQ-007-001-003 | Implement fallback to DEMO_SOAP if gateway is unavailable with console.warn | MTH | BR-020 |

#### FEAT-007-002: Coding Store Integration (MTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-007-002-001 | Modify `loadSuggestions()` in `codingStore.ts` to call gateway via mcpClient with action suggest_icd10 | MTH | BR-019 |
| REQ-007-002-002 | Modify `searchCodes()` in `codingStore.ts` to call gateway via mcpClient with action search_icd10 | MTH | BR-019 |
| REQ-007-002-003 | Add loading states and manage them during async operations | MTH | BR-021 |
| REQ-007-002-004 | Implement fallback to demo data if gateway is unavailable | MTH | BR-020 |

#### FEAT-007-003: Image Store Integration (MTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-007-003-001 | Modify `analyzeImage()` in `imageStore.ts` to call gateway via mcpClient with actions analyze_image and generate_report | MTH | BR-019 |
| REQ-007-003-002 | Add isAnalyzing loading state and manage it during async operation | MTH | BR-021 |
| REQ-007-003-003 | Implement fallback to demo data if gateway is unavailable | MTH | BR-020 |

---

### EPIC-008: Medical AI Safety and Audit Hooks (MTH)

**Source**: FA-008 (US-012, US-013, BR-022, BR-023, BR-024)

#### FEAT-008-001: AI Disclaimer Hook (MTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-008-001-001 | Create post-tool hook that activates after analyze_image and generate_report actions | MTH | BR-022 |
| REQ-008-001-002 | Hook verifies that response includes ai_disclaimer field | MTH | BR-022 |

#### FEAT-008-002: Medical Audit Hook (NTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-008-002-001 | Create post-tool hook that activates after any medicum action | NTH | BR-023 |
| REQ-008-002-002 | Log timestamp, action name, input summary (without PII), and output summary | NTH | BR-023, NFR-005 |

#### FEAT-008-003: ICD-10 Validation Hook (NTH)

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| REQ-008-003-001 | Create pre-tool hook that activates before returning suggest_icd10 results | NTH | BR-024 |
| REQ-008-003-002 | Validate that all suggested codes exist in the official ICD-10 catalog | NTH | BR-024 |

---

## 2.5 Technical Requirements

| Req ID | Category | Description | MTH | Source |
|--------|----------|-------------|-----|--------|
| TECH-001 | Architecture | Plugin must be TypeScript compiled to JavaScript following CyberDemo conventions | MTH | C-001 |
| TECH-002 | Architecture | All Claude API calls must use the Anthropic SDK for direct API communication | MTH | D-001, BR-017 |
| TECH-003 | Resilience | Plugin must handle API errors gracefully without crashing the gateway process | MTH | NFR-007 |
| TECH-004 | Structure | Each action file must export a single async function with consistent signature | MTH | NFR-009 |
| TECH-005 | Structure | System prompts must be in separate files under prompts directory | MTH | BR-018 |
| TECH-006 | Performance | ICD-10 catalog must be loaded once and cached in memory for performance | MTH | NFR-008 |

## 2.6 Integration Requirements

| Req ID | Category | Description | MTH | Source |
|--------|----------|-------------|-----|--------|
| INT-001 | Plugin | Plugin must register with OpenClaw via api.registerTool in index.ts | MTH | BR-016 |
| INT-002 | Frontend | Frontend stores must communicate via mcpClient.request for tool calls | MTH | BR-019 |
| INT-003 | Deploy | Plugin must be deployed to Docker container extensions path | MTH | C-002 |
| INT-004 | Config | Plugin must be registered in moltbot.json under plugins.entries | MTH | A-001 |
| INT-005 | Config | Gateway must be restarted after plugin deployment for changes to take effect | MTH | A-001 |

## 2.7 Data Requirements

| Req ID | Category | Description | MTH | Source |
|--------|----------|-------------|-----|--------|
| DATA-001 | Catalog | ICD-10 catalog must contain ~70,000 codes from WHO/OMS official source | MTH | BR-009 |
| DATA-002 | Catalog | Catalog format JSON array with required fields per entry | MTH | BR-009 |
| DATA-003 | Catalog | Catalog file size approximately 15-20 MB | MTH | NFR-008 |
| DATA-004 | Fallback | Existing demo constants retained as fallback data | MTH | BR-020 |

---

## 2.8 Full Traceability Matrix

| Req ID | Source | Description | Code | Tests | Verified |
|--------|--------|-------------|------|-------|----------|
| REQ-001-001-001 | US-001 | Create generate-soap.ts action with transcription_segments and patient_context params | [ ] | [ ] | [ ] |
| REQ-001-001-002 | US-001, US-002 | Call Claude API with formatted dialogue and patient context | [ ] | [ ] | [ ] |
| REQ-001-001-003 | BR-001, BR-003 | Parse Claude response as JSON with subjetivo, objetivo, analisis, plan, confidence | [ ] | [ ] | [ ] |
| REQ-001-001-004 | BR-002 | Include insufficient information markers when data is missing | [ ] | [ ] | [ ] |
| REQ-001-002-001 | BR-001 | Create soap-prompt.ts with medical documentation system prompt | [ ] | [ ] | [ ] |
| REQ-001-002-002 | BR-001, BR-003 | Prompt instructs JSON-only output with 5 SOAP fields | [ ] | [ ] | [ ] |
| REQ-001-002-003 | BR-002 | Prompt instructs insufficient information handling | [ ] | [ ] | [ ] |
| REQ-002-001-001 | US-003 | Create suggest-icd10.ts with diagnosis_text, soap_note, patient_conditions params | [ ] | [ ] | [ ] |
| REQ-002-001-002 | BR-004 | Pre-filter catalog to ~50 candidates via text search | [ ] | [ ] | [ ] |
| REQ-002-001-003 | US-003, US-004 | Call Claude API with candidates and clinical context for ranking | [ ] | [ ] | [ ] |
| REQ-002-001-004 | BR-005 | Return suggestions with code, description, confidence, rationale, is_primary | [ ] | [ ] | [ ] |
| REQ-002-001-005 | BR-006 | Limit suggestions to maxSuggestions config value | [ ] | [ ] | [ ] |
| REQ-002-002-001 | US-003 | Create icd10-prompt.ts with clinical coding system prompt | [ ] | [ ] | [ ] |
| REQ-002-002-002 | BR-005 | Prompt instructs ranking by clinical relevance | [ ] | [ ] | [ ] |
| REQ-002-002-003 | BR-005 | Prompt instructs providing rationale for each suggestion | [ ] | [ ] | [ ] |
| REQ-003-001-001 | US-005 | Create search-icd10.ts with query and limit params | [ ] | [ ] | [ ] |
| REQ-003-001-002 | BR-007 | Implement deterministic text search on codigo and descripcion | [ ] | [ ] | [ ] |
| REQ-003-001-003 | BR-008 | Return results with limit and total_matches | [ ] | [ ] | [ ] |
| REQ-003-002-001 | BR-009 | Include ICD-10 catalog JSON with ~70,000 codes | [ ] | [ ] | [ ] |
| REQ-003-002-002 | BR-009 | Each entry has codigo, descripcion_es, capitulo, subcapitulo | [ ] | [ ] | [ ] |
| REQ-003-002-003 | NFR-008 | Implement catalog caching for efficient loading | [ ] | [ ] | [ ] |
| REQ-004-001-001 | US-006 | Create analyze-image.ts with image_base64, image_type, body_region, clinical_indication, patient_context | [ ] | [ ] | [ ] |
| REQ-004-001-002 | BR-013 | Call Claude Vision API with base64 image | [ ] | [ ] | [ ] |
| REQ-004-001-003 | BR-011 | Return findings with severity and confidence | [ ] | [ ] | [ ] |
| REQ-004-001-004 | BR-012 | Include AI disclaimer in response | [ ] | [ ] | [ ] |
| REQ-004-002-001 | US-006 | Create image-prompt.ts with diagnostic imaging system prompt | [ ] | [ ] | [ ] |
| REQ-004-002-002 | BR-010 | Prompt supports X-ray, CT, MRI, ultrasound modalities | [ ] | [ ] | [ ] |
| REQ-004-002-003 | BR-011 | Prompt instructs severity classification and confidence scoring | [ ] | [ ] | [ ] |
| REQ-005-001-001 | US-008 | Create generate-report.ts with findings, study_info, patient_info params | [ ] | [ ] | [ ] |
| REQ-005-001-002 | BR-015 | Call Claude API to generate report from findings | [ ] | [ ] | [ ] |
| REQ-005-001-003 | BR-014 | Return report with header, technique, findings, conclusion, recommendations | [ ] | [ ] | [ ] |
| REQ-005-002-001 | BR-014 | Create report-prompt.ts with radiology report system prompt | [ ] | [ ] | [ ] |
| REQ-005-002-002 | BR-014 | Prompt enforces standard radiology format | [ ] | [ ] | [ ] |
| REQ-006-001-001 | BR-016 | Create index.ts with register(api) following CyberDemo pattern | [ ] | [ ] | [ ] |
| REQ-006-001-002 | US-010 | Create openclaw.plugin.json manifest with configSchema | [ ] | [ ] | [ ] |
| REQ-006-001-003 | D-001 | Create package.json with anthropic SDK dependency | [ ] | [ ] | [ ] |
| REQ-006-002-001 | BR-016 | Create medicum-tool.ts with createMedicumTool(api) | [ ] | [ ] | [ ] |
| REQ-006-002-002 | BR-016 | Implement action router dispatching to all 5 actions | [ ] | [ ] | [ ] |
| REQ-006-002-003 | BR-017 | Initialize Anthropic SDK with config or env API key | [ ] | [ ] | [ ] |
| REQ-006-002-004 | NFR-007 | Implement error handling with ok/error response format | [ ] | [ ] | [ ] |
| REQ-006-003-001 | US-010 | Support configurable anthropicApiKey, model, icd10CatalogPath, maxSuggestions, language | [ ] | [ ] | [ ] |
| REQ-006-003-002 | US-010 | Provide sensible defaults for all config fields | [ ] | [ ] | [ ] |
| REQ-007-001-001 | BR-019 | Modify generateSOAPNote() to call gateway with action generate_soap | [ ] | [ ] | [ ] |
| REQ-007-001-002 | BR-021 | Add isGeneratingSOAP loading state | [ ] | [ ] | [ ] |
| REQ-007-001-003 | BR-020 | Implement fallback to DEMO_SOAP on gateway error | [ ] | [ ] | [ ] |
| REQ-007-002-001 | BR-019 | Modify loadSuggestions() to call gateway with action suggest_icd10 | [ ] | [ ] | [ ] |
| REQ-007-002-002 | BR-019 | Modify searchCodes() to call gateway with action search_icd10 | [ ] | [ ] | [ ] |
| REQ-007-002-003 | BR-021 | Add loading states for coding operations | [ ] | [ ] | [ ] |
| REQ-007-002-004 | BR-020 | Implement fallback to demo data on gateway error | [ ] | [ ] | [ ] |
| REQ-007-003-001 | BR-019 | Modify analyzeImage() to call gateway with actions analyze_image + generate_report | [ ] | [ ] | [ ] |
| REQ-007-003-002 | BR-021 | Add isAnalyzing loading state | [ ] | [ ] | [ ] |
| REQ-007-003-003 | BR-020 | Implement fallback to demo data on gateway error | [ ] | [ ] | [ ] |
| REQ-008-001-001 | BR-022 | Create post-tool hook for AI disclaimer on analyze_image and generate_report | [ ] | [ ] | [ ] |
| REQ-008-001-002 | BR-022 | Hook verifies ai_disclaimer field in response | [ ] | [ ] | [ ] |
| REQ-008-002-001 | BR-023 | Create post-tool audit hook for all medicum actions | [ ] | [ ] | [ ] |
| REQ-008-002-002 | BR-023, NFR-005 | Log timestamp, action, input summary (no PII), output summary | [ ] | [ ] | [ ] |
| REQ-008-003-001 | BR-024 | Create pre-tool hook for ICD-10 validation | [ ] | [ ] | [ ] |
| REQ-008-003-002 | BR-024 | Validate suggested codes exist in official catalog | [ ] | [ ] | [ ] |
| TECH-001 | C-001 | Plugin TypeScript following CyberDemo conventions | [ ] | [ ] | [ ] |
| TECH-002 | D-001, BR-017 | Use Anthropic SDK for Claude API calls | [ ] | [ ] | [ ] |
| TECH-003 | NFR-007 | Handle API errors without crashing gateway | [ ] | [ ] | [ ] |
| TECH-004 | NFR-009 | Each action as separate file with consistent signature | [ ] | [ ] | [ ] |
| TECH-005 | BR-018 | System prompts in separate files under prompts directory | [ ] | [ ] | [ ] |
| TECH-006 | NFR-008 | ICD-10 catalog loaded once and cached | [ ] | [ ] | [ ] |
| INT-001 | BR-016 | Register plugin via api.registerTool() | [ ] | [ ] | [ ] |
| INT-002 | BR-019 | Frontend uses mcpClient.request for tool calls | [ ] | [ ] | [ ] |
| INT-003 | C-002 | Deploy to Docker container extensions path | [ ] | [ ] | [ ] |
| INT-004 | A-001 | Register in moltbot.json plugins.entries | [ ] | [ ] | [ ] |
| INT-005 | A-001 | Gateway restart after deployment | [ ] | [ ] | [ ] |
| DATA-001 | BR-009 | ICD-10 catalog with ~70,000 codes from WHO/OMS | [ ] | [ ] | [ ] |
| DATA-002 | BR-009 | Catalog fields: codigo, descripcion_es, capitulo, subcapitulo | [ ] | [ ] | [ ] |
| DATA-003 | NFR-008 | Catalog file ~15-20 MB | [ ] | [ ] | [ ] |
| DATA-004 | BR-020 | Retain demo constants as fallback | [ ] | [ ] | [ ] |
| NFR-001 | FA-001 | SOAP generation must complete within 10 seconds | [ ] | [ ] | [ ] |
| NFR-002 | FA-003 | ICD-10 catalog search must complete within 500ms | [ ] | [ ] | [ ] |
| NFR-003 | FA-004 | Image analysis must complete within 30 seconds | [ ] | [ ] | [ ] |
| NFR-004 | FA-006 | Anthropic API key stored in plugin config, never exposed to frontend | [ ] | [ ] | [ ] |
| NFR-005 | FA-008 | Audit logs must not contain sensitive patient data | [ ] | [ ] | [ ] |
| NFR-006 | FA-007 | Frontend must gracefully fall back to demo data if gateway unavailable | [ ] | [ ] | [ ] |
| NFR-007 | FA-006 | Plugin must handle Claude API errors without crashing gateway | [ ] | [ ] | [ ] |
| NFR-008 | FA-003 | ICD-10 catalog loaded efficiently with caching | [ ] | [ ] | [ ] |
| NFR-009 | FA-006 | Each action in separate file following CyberDemo pattern for maintainability | [ ] | [ ] | [ ] |

---

## Verification: Part 1 to Part 2 Traceability

| Part 1 Item | Part 2 Coverage |
|-------------|-----------------|
| US-001 | REQ-001-001-001, REQ-001-001-002 |
| US-002 | REQ-001-001-002 |
| US-003 | REQ-002-001-001, REQ-002-001-003, REQ-002-002-001 |
| US-004 | REQ-002-001-003 |
| US-005 | REQ-003-001-001, REQ-003-001-002 |
| US-006 | REQ-004-001-001, REQ-004-002-001 |
| US-007 | REQ-004-001-001 |
| US-008 | REQ-005-001-001 |
| US-009 | REQ-006-001-001, REQ-006-002-001 |
| US-010 | REQ-006-001-002, REQ-006-003-001, REQ-006-003-002 |
| US-011 | REQ-007-001-001, REQ-007-002-001, REQ-007-003-001 |
| US-012 | REQ-008-002-001 |
| US-013 | REQ-008-001-001 |
| BR-001 | REQ-001-001-003, REQ-001-002-001, REQ-001-002-002 |
| BR-002 | REQ-001-001-004, REQ-001-002-003 |
| BR-003 | REQ-001-001-003, REQ-001-002-002 |
| BR-004 | REQ-002-001-002 |
| BR-005 | REQ-002-001-004, REQ-002-002-002, REQ-002-002-003 |
| BR-006 | REQ-002-001-005 |
| BR-007 | REQ-003-001-002 |
| BR-008 | REQ-003-001-003 |
| BR-009 | REQ-003-002-001, REQ-003-002-002, DATA-001, DATA-002 |
| BR-010 | REQ-004-002-002 |
| BR-011 | REQ-004-001-003, REQ-004-002-003 |
| BR-012 | REQ-004-001-004 |
| BR-013 | REQ-004-001-002 |
| BR-014 | REQ-005-001-003, REQ-005-002-001, REQ-005-002-002 |
| BR-015 | REQ-005-001-002 |
| BR-016 | REQ-006-001-001, REQ-006-002-001, REQ-006-002-002, INT-001 |
| BR-017 | REQ-006-002-003, TECH-002 |
| BR-018 | TECH-005 |
| BR-019 | REQ-007-001-001, REQ-007-002-001, REQ-007-002-002, REQ-007-003-001, INT-002 |
| BR-020 | REQ-007-001-003, REQ-007-002-004, REQ-007-003-003, DATA-004 |
| BR-021 | REQ-007-001-002, REQ-007-002-003, REQ-007-003-002 |
| BR-022 | REQ-008-001-001, REQ-008-001-002 |
| BR-023 | REQ-008-002-001, REQ-008-002-002 |
| BR-024 | REQ-008-003-001, REQ-008-003-002 |
| NFR-001 | TECH-003 |
| NFR-002 | REQ-003-001-002 |
| NFR-003 | REQ-004-001-001, REQ-004-001-002 |
| NFR-004 | REQ-006-002-003 |
| NFR-005 | REQ-008-002-002 |
| NFR-006 | REQ-007-001-003, REQ-007-002-004, REQ-007-003-003 |
| NFR-007 | REQ-006-002-004, TECH-003 |
| NFR-008 | REQ-003-002-003, TECH-006, DATA-003 |
| NFR-009 | TECH-004 |

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total Epics | 8 |
| Total Features | 19 |
| Total REQ Requirements | 58 |
| Total TECH Requirements | 6 |
| Total INT Requirements | 5 |
| Total DATA Requirements | 4 |
| Total NFR Requirements | 9 |
| **Total Requirements** | **82** |
| MTH Requirements | 78 |
| NTH Requirements | 4 |
| User Stories (Part 1) | 13 |
| Business Rules (Part 1) | 24 |

---

_Generated by SoftwareBuilderX v23.0.0 — Medicum OpenCloud Project_
