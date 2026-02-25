# Functional Specification: Medicum SoulBot — De Simulado a Real con OpenClaw

| Attribute | Value |
|-----------|-------|
| Version | 1.0.0 |
| Date | 2026-02-25 |
| Build ID | sbx-20260225-150400 |
| Status | Draft |
| Input Document | MEDICUM_OPENCLOUD_FUNCTIONAL_DESCRIPTION.md v2.0.0 |

---

# PART 1: FUNCTIONAL DESCRIPTION
*For business stakeholders and non-technical readers*

## 1.1 Executive Summary

Medicum is a medical consultation assistant integrated into the CyberDemo platform. Currently, 6 of its core features are **simulated** with hardcoded constants and fake delays (`setTimeout`). This project replaces ALL simulated functionality with real AI-powered processing using Claude (via the OpenClaw gateway), following the exact pattern already proven in CyberDemo's security orchestration.

The result: a fully functional medical assistant where SOAP notes are generated from real transcriptions, ICD-10 codes are suggested by AI from a 70,000-code catalog, and medical images are analyzed by Claude Vision — all through the existing WebSocket connection to the OpenClaw gateway.

## 1.2 System Overview

### 1.2.1 Purpose

Replace all hardcoded demo data and simulated behavior in the Medicum frontend with real AI-powered functionality, delivered through an OpenClaw plugin (`medicum-ai`) that uses Claude as its reasoning engine.

### 1.2.2 Scope

**In Scope:**
- OpenClaw plugin `medicum-ai` with 5 medical actions (generate_soap, suggest_icd10, search_icd10, analyze_image, generate_report)
- Frontend store modifications to call gateway instead of using demo constants
- ICD-10 catalog integration (70,000 codes)
- Medical AI disclaimer enforcement
- Container deployment of plugin and skill
- Graceful fallback to demo data when gateway is unavailable

**Out of Scope:**
- SNOMED CT catalog integration (future NTH)
- Real-time Whisper transcription (already functional, no changes needed)
- Patient data persistence (uses existing paciente_demo.json)
- Multi-language support beyond Spanish
- HIPAA/GDPR compliance infrastructure (research phase only)

### 1.2.3 Context Diagram

```
[Whisper GPU] --transcription--> [Medicum Frontend (React)]
                                        |
                                  WebSocket :18789
                                        |
                                        v
                               [OpenClaw Gateway (Docker)]
                                        |
                                        v
                               [SoulBot (Claude Agent)]
                                        |
                                   tool "medicum"
                                        |
                                        v
                               [Plugin: medicum-ai]
                                   |           |
                            Claude API    ICD-10 Catalog
                          (text+vision)   (70K codes JSON)
```

## 1.3 User Roles and Personas

| Role ID | Role Name | Description | Primary Goals |
|---------|-----------|-------------|---------------|
| USR-001 | Physician | Medical doctor conducting consultations | Document consultations via SOAP, get ICD-10 suggestions, analyze images |
| USR-002 | Radiologist | Specialist reviewing diagnostic images | Analyze medical images, generate structured radiology reports |
| USR-003 | Medical Coder | Administrative staff for clinical coding | Search and validate ICD-10 codes from consultation data |

## 1.4 Functional Areas

### 1.4.1 Consultation Documentation (SOAP Generation)

**Description**: Convert real-time doctor-patient transcription into structured SOAP notes using Claude.

**User Stories**:
- US-001: As a Physician, I want my consultation transcription converted to a SOAP note automatically so that I can focus on the patient instead of documentation
- US-002: As a Physician, I want the SOAP note to consider patient context (age, conditions, medications) so that the analysis is clinically relevant

**Business Rules**:
- BR-001: SOAP generation must use actual transcription segments, not hardcoded text
- BR-002: If transcription is insufficient, SOAP must indicate "[Informacion insuficiente]" in affected sections
- BR-003: SOAP output must be structured JSON with fields: subjetivo, objetivo, analisis, plan, confidence
- BR-004: When gateway is unavailable, system falls back to demo SOAP with a visible warning

**Workflows**:
1. Physician conducts consultation (Whisper transcribes in real-time)
2. Physician clicks "Generate SOAP"
3. Frontend sends transcription segments + patient context to gateway
4. Plugin calls Claude with medical system prompt
5. Claude analyzes dialogue and generates structured SOAP
6. SOAP appears in ConsultaTab with confidence score

### 1.4.2 Clinical Coding (ICD-10 Suggestions)

**Description**: AI-powered ICD-10 code suggestions based on diagnosis text, SOAP notes, and patient conditions.

**User Stories**:
- US-003: As a Physician, I want ICD-10 codes suggested automatically from my diagnosis so that coding is faster and more accurate
- US-004: As a Medical Coder, I want to search the full ICD-10 catalog (70K codes) so that I can find any code I need

**Business Rules**:
- BR-005: Suggestions must come from the real ICD-10 catalog (70,000 codes), not from 10 hardcoded codes
- BR-006: Claude must rank suggestions with confidence scores and rationale
- BR-007: Each suggestion must indicate if it is primary or secondary diagnosis
- BR-008: Text search must work without LLM (deterministic, fast)
- BR-009: All suggested codes must be validated against the official catalog before returning

**Workflows**:
1. SOAP note is generated (or diagnosis text is entered manually)
2. System pre-filters ICD-10 catalog locally (text match, ~50 candidates)
3. Claude ranks candidates by clinical relevance
4. Top suggestions appear in CodificacionTab with code, description, confidence, rationale

### 1.4.3 Medical Image Analysis

**Description**: AI analysis of medical images (X-ray, CT, MRI, ultrasound) using Claude Vision.

**User Stories**:
- US-005: As a Radiologist, I want diagnostic images analyzed by AI so that I get a structured list of findings with severity and confidence
- US-006: As a Radiologist, I want a professional radiology report generated from findings so that I have a complete document ready for review

**Business Rules**:
- BR-010: Image analysis must use Claude Vision (real image inspection), not setTimeout with fake findings
- BR-011: Findings must include: description, location, severity (normal/mild/moderate/severe), confidence (0-1)
- BR-012: Every image analysis response must include an AI disclaimer
- BR-013: Report must follow standard radiology format: header, technique, findings, conclusion, recommendations
- BR-014: Report must include patient identification and study metadata

**Workflows**:
1. Physician/Radiologist uploads medical image in VisorTab
2. Selects image type (xray/ct/mri/ultrasound), body region, clinical indication
3. Plugin sends image as base64 to Claude Vision
4. Claude Vision analyzes the actual image and returns structured findings
5. Physician reviews findings and requests full radiology report
6. Claude generates professional report from findings + study info + patient data

### 1.4.4 Gateway Plugin & Deployment

**Description**: OpenClaw plugin following the CyberDemo pattern, with container deployment.

**User Stories**:
- US-007: As a Developer, I want a single plugin with multiple actions so that the gateway integration is clean and follows existing patterns
- US-008: As a DevOps, I want the plugin deployable via docker cp + restart so that deployment is simple and reproducible

**Business Rules**:
- BR-015: Plugin must follow exactly the CyberDemo pattern (register → registerTool → actions switch)
- BR-016: Plugin must work with the existing WebSocket MCP protocol
- BR-017: All actions must return standardized response format: { protocolVersion, ok, status, output/error }
- BR-018: Plugin must be configurable via moltbot.json (API key, model, language, maxSuggestions)

## 1.5 Non-Functional Requirements (Summary)

| Category | Requirement |
|----------|-------------|
| Performance | SOAP generation < 10s, ICD-10 search < 500ms, Image analysis < 30s |
| Availability | Graceful fallback to demo data when gateway/Claude unavailable |
| Security | API keys stored in config only, no patient data in logs, AI disclaimer on medical outputs |
| Scalability | Single-user (consultation context), catalog loaded once in memory |
| Usability | Loading indicators during AI processing, error messages in Spanish |

## 1.6 Assumptions and Dependencies

### Assumptions
- OpenClaw gateway is running in Docker container on port 18789
- Anthropic API key is available and configured
- Claude claude-sonnet-4 model supports both text and vision
- Existing WebSocket MCP protocol works for tool calls
- ICD-10 catalog JSON file is available (downloadable from OMS/MSSSI)

### Dependencies
- OpenClaw Gateway (running, accessible)
- Anthropic Claude API (claude-sonnet-4-20250514)
- Existing medicum frontend components (React + Zustand)
- Existing mcpClient.ts WebSocket connection
- Whisper transcription system (already functional)
- CyberDemo plugin as reference pattern

## 1.7 Constraints

- Must follow CyberDemo plugin pattern exactly (no architectural experimentation)
- ICD-10 catalog size ~15-20MB JSON (must fit in memory)
- Claude API calls add latency (no sub-second medical analysis)
- Spanish language only for v1.0
- Single-tenant: one physician, one patient at a time

## 1.8 Project Context

This project extends an **existing codebase**: the Medicum frontend is already integrated into CyberDemo as a React component with Zustand stores, and connects to the OpenClaw gateway via WebSocket. The CyberDemo platform already has a working plugin (`cyberdemo`) that follows the exact pattern we will replicate.

**Existing Codebase:**
- Frontend: `frontend/src/components/medicum/` — 6 tab components, 6 stores, 1 MCP client, 1 types file
- Gateway: OpenClaw running in Docker on `:18789` with CyberDemo plugin as reference
- Connection: `mcpClient.ts` already establishes WebSocket to gateway and handles req/res/event protocol
- Data: `paciente_demo.json` with patient context (no changes needed)
- Transcription: Whisper GPU proxy already functional (no changes needed)

**What Changes:**
- NEW: Plugin `medicum-ai` in `extensions/medicum-ai/` (gateway side)
- MODIFY: 3 Zustand stores (`transcriptionStore.ts`, `codingStore.ts`, `imageStore.ts`) to call gateway instead of using hardcoded constants
- NEW: ICD-10 catalog JSON file (~70K codes)
- NEW: 4 medical system prompts for Claude
- NEW: Deployment script for Docker container

---

# PART 2: TECHNICAL REQUIREMENTS
*Traceable requirements for development*

## 2.1 Requirements Traceability Matrix (Brief)

| Category | Count | Coverage |
|----------|-------|----------|
| Functional Requirements (REQ) | 60 | All traced to US/BR |
| Technical Requirements (TECH) | 8 | All traced to NFR/architecture |
| Integration Requirements (INT) | 4 | All traced to system interfaces |
| Data Requirements (DATA) | 4 | All traced to data needs |
| Non-Functional Requirements (NFR) | 8 | All traced to Section 1.5 |
| **Total** | **84** | Full traceability in Section 2.8 |

## 2.2 Requirements Numbering Convention

```
EPIC-XXX           : Epic level
FEAT-XXX-YYY       : Feature under Epic XXX
REQ-XXX-YYY-ZZZ    : Requirement under Feature YYY
TECH-XXX           : Technical requirement
INT-XXX            : Integration requirement
DATA-XXX           : Data requirement
NFR-XXX            : Non-functional requirement
```

## 2.3 Priority Classification

| Priority | Code | Description |
|----------|------|-------------|
| Must-To-Have | MTH | Critical for replacing simulated functionality |
| Nice-To-Have | NTH | Enhancements beyond base replacement |

## 2.4 Epics

### EPIC-001: OpenClaw Plugin (medicum-ai) `MTH`

**ID**: EPIC-001
**Priority**: MTH
**Description**: Create the medicum-ai OpenClaw plugin with 5 medical actions that call Claude API, following the CyberDemo pattern exactly.
**Business Value**: Core engine that replaces all simulated functionality with real AI processing.
**Traces To**: Section 1.4.1, 1.4.2, 1.4.3, 1.4.4

**Acceptance Criteria**:
- [ ] AC-001: Plugin registers successfully in OpenClaw gateway
- [ ] AC-002: All 5 actions callable via WebSocket MCP protocol
- [ ] AC-003: Actions return real Claude-generated results, not hardcoded data

#### Features

##### FEAT-001-001: Plugin Registration & Entry Point `MTH`

**ID**: FEAT-001-001
**Priority**: MTH
**Description**: Plugin manifest, entry point, and tool registration following CyberDemo pattern.
**Traces To**: US-007, BR-015, BR-016, BR-017, BR-018

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-001-001 | Create openclaw.plugin.json manifest with configSchema (anthropicApiKey, model, icd10CatalogPath, maxSuggestions, language) | MTH | Manifest validates and plugin loads in gateway |
| REQ-001-001-002 | Create index.ts entry point that calls register(api) and registerTool with sandboxed check | MTH | Plugin registers tool "medicum" on gateway startup |
| REQ-001-001-003 | Create medicum-tool.ts with action switch dispatching to 5 action handlers | MTH | Tool routes actions correctly, unknown actions return error |
| REQ-001-001-004 | All actions return standardized response format { protocolVersion: 1, ok, status, output/error } | MTH | Response format matches CyberDemo pattern |

##### FEAT-001-002: Generate SOAP Action `MTH`

**ID**: FEAT-001-002
**Priority**: MTH
**Description**: Action that generates structured SOAP notes from transcription using Claude.
**Traces To**: US-001, US-002, BR-001, BR-002, BR-003

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-002-001 | Accept transcription_segments array [{speaker, text, timestamp}] and patient_context object | MTH | Validates input structure before calling Claude |
| REQ-001-002-002 | Format transcription as dialogue "[MEDICO]: text / [PACIENTE]: text" for Claude prompt | MTH | Claude receives properly formatted consultation dialogue |
| REQ-001-002-003 | Use medical system prompt that instructs structured SOAP output with confidence | MTH | System prompt produces consistent JSON output |
| REQ-001-002-004 | Return parsed JSON { subjetivo, objetivo, analisis, plan, confidence } | MTH | Output is valid JSON with all 5 fields |
| REQ-001-002-005 | Handle insufficient transcription with "[Informacion insuficiente]" markers | MTH | Short/empty transcription returns markers, not errors |

##### FEAT-001-003: Suggest ICD-10 Action `MTH`

**ID**: FEAT-001-003
**Priority**: MTH
**Description**: AI-ranked ICD-10 suggestions from diagnosis text using pre-filtering + Claude ranking.
**Traces To**: US-003, BR-005, BR-006, BR-007

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-003-001 | Accept diagnosis_text, optional soap_note, optional patient_conditions | MTH | Action handles all input combinations |
| REQ-001-003-002 | Pre-filter ICD-10 catalog locally by text match to ~50 candidates | MTH | Text search completes in <200ms |
| REQ-001-003-003 | Send candidates to Claude for clinical ranking with context | MTH | Claude returns ranked list, not just text match |
| REQ-001-003-004 | Return suggestions array [{code, description, confidence, rationale, is_primary}] | MTH | Each suggestion has all 5 fields |
| REQ-001-003-005 | Limit results to configurable maxSuggestions (default 10) | MTH | Never returns more than configured limit |

##### FEAT-001-004: Search ICD-10 Action `MTH`

**ID**: FEAT-001-004
**Priority**: MTH
**Description**: Deterministic text search across full 70,000-code ICD-10 catalog.
**Traces To**: US-004, BR-005, BR-008

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-004-001 | Accept query string and optional limit (default 20) | MTH | Query parameter is required, limit optional |
| REQ-001-004-002 | Search by code and description (case-insensitive) across full catalog | MTH | Finds codes by partial code or description text |
| REQ-001-004-003 | Return { results: [{codigo, descripcion}], total_matches } | MTH | Results structure is consistent |
| REQ-001-004-004 | Complete search in <500ms even for broad queries | MTH | No LLM call, pure text filtering |

##### FEAT-001-005: Analyze Image Action `MTH`

**ID**: FEAT-001-005
**Priority**: MTH
**Description**: Medical image analysis using Claude Vision for X-ray, CT, MRI, ultrasound.
**Traces To**: US-005, BR-010, BR-011, BR-012

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-005-001 | Accept image_base64, image_type (xray/ct/mri/ultrasound), body_region, clinical_indication | MTH | All parameters validated before Claude call |
| REQ-001-005-002 | Send image to Claude Vision with medical analysis system prompt | MTH | Claude receives image as base64 media content |
| REQ-001-005-003 | Return structured findings [{description, location, severity, confidence}] | MTH | Each finding has all 4 fields with severity enum |
| REQ-001-005-004 | Include overall_impression and ai_disclaimer in response | MTH | AI disclaimer always present in response |
| REQ-001-005-005 | Include limitations field acknowledging AI analysis constraints | MTH | Response honestly states limitations |

##### FEAT-001-006: Generate Report Action `MTH`

**ID**: FEAT-001-006
**Priority**: MTH
**Description**: Professional radiology report generation from image analysis findings.
**Traces To**: US-006, BR-013, BR-014

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-006-001 | Accept findings array, study_info object, patient_info object | MTH | All three inputs required for complete report |
| REQ-001-006-002 | Generate report with standard sections: header, technique, findings, conclusion, recommendations | MTH | Report has all 5 sections |
| REQ-001-006-003 | Include patient identification and study metadata in report header | MTH | Report header has patient name, ID, study date, modality |
| REQ-001-006-004 | Return structured report as JSON (not free-form text) | MTH | Report is parseable JSON with section fields |

---

### EPIC-002: Frontend Store Integration `MTH`

**ID**: EPIC-002
**Priority**: MTH
**Description**: Modify Medicum Zustand stores to call OpenClaw gateway instead of using hardcoded demo data.
**Business Value**: Connects the UI to the real AI backend, completing the simulation-to-real migration.
**Traces To**: Section 1.4.1, 1.4.2, 1.4.3

**Acceptance Criteria**:
- [ ] AC-004: All 3 stores call gateway via mcpClient.request()
- [ ] AC-005: Demo constants are replaced by real AI calls
- [ ] AC-006: Graceful fallback to demo data when gateway unavailable

#### Features

##### FEAT-002-001: TranscriptionStore Integration `MTH`

**ID**: FEAT-002-001
**Priority**: MTH
**Description**: Replace hardcoded DEMO_SOAP in transcriptionStore.ts with gateway call.
**Traces To**: US-001, BR-001, BR-004

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-002-001-001 | Replace `generateSOAPNote: () => set({ soapNote: DEMO_SOAP })` with async gateway call | MTH | Function calls mcpClient.request with action generate_soap |
| REQ-002-001-002 | Pass current transcription segments and patient context as parameters | MTH | Real transcription data sent, not hardcoded |
| REQ-002-001-003 | Add loading state isGeneratingSOAP while waiting for response | MTH | UI shows loading indicator during generation |
| REQ-002-001-004 | Fallback to DEMO_SOAP with console.warn when gateway unavailable | MTH | App doesn't crash when gateway is down |

##### FEAT-002-002: CodingStore Integration `MTH`

**ID**: FEAT-002-002
**Priority**: MTH
**Description**: Replace DEMO_SUGGESTIONS and DEMO_ICD10_CATALOG with gateway calls.
**Traces To**: US-003, US-004, BR-005, BR-009

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-002-002-001 | Replace `loadSuggestions()` to call gateway with action suggest_icd10 | MTH | Function calls mcpClient.request with diagnosis from SOAP |
| REQ-002-002-002 | Replace `searchCodes()` to call gateway with action search_icd10 | MTH | Function calls mcpClient.request with search query |
| REQ-002-002-003 | Remove DEMO_SUGGESTIONS constant (4 hardcoded codes) | MTH | No hardcoded suggestion data in store |
| REQ-002-002-004 | Remove DEMO_ICD10_CATALOG constant (10 hardcoded codes) | MTH | No hardcoded catalog data in store |
| REQ-002-002-005 | Add loading states isLoadingSuggestions and isSearching | MTH | UI shows loading during AI processing |

##### FEAT-002-003: ImageStore Integration `MTH`

**ID**: FEAT-002-003
**Priority**: MTH
**Description**: Replace setTimeout + DEMO_KNEE_FINDINGS/REPORT with gateway calls to Claude Vision.
**Traces To**: US-005, US-006, BR-010, BR-013

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-002-003-001 | Replace `analyzeImage()` setTimeout with gateway call to action analyze_image | MTH | Function sends real image data to Claude Vision via gateway |
| REQ-002-003-002 | Convert uploaded image to base64 before sending | MTH | Image properly encoded as base64 string |
| REQ-002-003-003 | Replace DEMO_KNEE_FINDINGS constant with real Claude Vision findings | MTH | No hardcoded findings data |
| REQ-002-003-004 | Replace DEMO_KNEE_REPORT with gateway call to action generate_report | MTH | No hardcoded report template |
| REQ-002-003-005 | Add loading states isAnalyzing and isGeneratingReport | MTH | UI shows loading during image analysis |

---

### EPIC-003: Data & Catalogs `MTH`

**ID**: EPIC-003
**Priority**: MTH
**Description**: Provide the ICD-10 catalog data and medical system prompts.
**Business Value**: Foundation data that enables accurate medical AI processing.
**Traces To**: Section 1.4.2

**Acceptance Criteria**:
- [ ] AC-007: ICD-10 catalog with ~70,000 codes loaded and searchable
- [ ] AC-008: Medical system prompts produce consistent, structured output

#### Features

##### FEAT-003-001: ICD-10 Catalog `MTH`

**ID**: FEAT-003-001
**Priority**: MTH
**Description**: Complete ICD-10 catalog as JSON for local text search and Claude ranking.
**Traces To**: BR-005, BR-009

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-003-001-001 | ICD-10 catalog JSON with ~70,000 codes (codigo, descripcion_es, capitulo, subcapitulo) | MTH | File contains >50,000 valid ICD-10 entries |
| REQ-003-001-002 | Catalog loaded into memory once at plugin initialization | MTH | No repeated file reads per request |
| REQ-003-001-003 | Catalog sourced from official OMS/MSSSI eCIE10 | MTH | Codes match official CIE-10 2026 edition |

##### FEAT-003-002: Medical System Prompts `MTH`

**ID**: FEAT-003-002
**Priority**: MTH
**Description**: Specialized system prompts for each medical action.
**Traces To**: BR-003, BR-006, BR-011, BR-013

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-003-002-001 | SOAP system prompt: instructs structured output with subjetivo/objetivo/analisis/plan/confidence | MTH | Claude consistently returns valid JSON SOAP |
| REQ-003-002-002 | ICD-10 system prompt: instructs ranking with confidence, rationale, is_primary | MTH | Claude consistently returns ranked suggestions |
| REQ-003-002-003 | Image analysis prompt: instructs structured findings with severity and confidence | MTH | Claude Vision returns consistent findings format |
| REQ-003-002-004 | Report generation prompt: instructs standard radiology format | MTH | Claude returns report with all required sections |

---

### EPIC-004: Gateway Skills & Hooks `NTH`

**ID**: EPIC-004
**Priority**: NTH (except ai-disclaimer hook which is MTH)
**Description**: SoulBot skill instructions and validation/audit hooks.
**Business Value**: Enables conversational medical assistant and ensures safety/audit.
**Traces To**: Section 1.4.4

**Acceptance Criteria**:
- [ ] AC-009: AI disclaimer hook validates all medical responses
- [ ] AC-010: Skill enables conversational medical workflow

#### Features

##### FEAT-004-001: AI Disclaimer Hook `MTH`

**ID**: FEAT-004-001
**Priority**: MTH
**Description**: Post-tool hook that verifies AI medical responses include disclaimer.
**Traces To**: BR-012

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-004-001-001 | Post-tool hook triggers after analyze_image and generate_report actions | MTH | Hook fires on every image/report response |
| REQ-004-001-002 | Verifies response includes ai_disclaimer field | MTH | Missing disclaimer triggers warning |

##### FEAT-004-002: Medicum Consult Skill `NTH`

**ID**: FEAT-004-002
**Priority**: NTH
**Description**: SKILL.md file that instructs SoulBot on medical consultation workflow.
**Traces To**: US-001, US-003, US-005

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-004-002-001 | Create SKILL.md with step-by-step consultation workflow (SOAP → ICD-10 → Image) | NTH | Skill file follows OpenClaw SKILL.md format |
| REQ-004-002-002 | Skill includes disclaimer reminder for all AI-generated medical content | NTH | Disclaimer mentioned in skill instructions |

##### FEAT-004-003: Audit & Validation Hooks `NTH`

**ID**: FEAT-004-003
**Priority**: NTH
**Description**: Medical audit logging and ICD-10 validation hooks.
**Traces To**: BR-009

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-004-003-001 | audit-medical hook logs timestamp, action, summary (no patient data) after every medicum action | NTH | Audit trail exists for all medical AI calls |
| REQ-004-003-002 | validate-icd10 hook verifies all suggested codes exist in catalog before returning | NTH | No non-existent ICD-10 codes returned to user |

---

### EPIC-005: Deployment & Configuration `MTH`

**ID**: EPIC-005
**Priority**: MTH
**Description**: Container deployment, configuration management, and operational readiness.
**Business Value**: Makes the system deployable and configurable without code changes.
**Traces To**: Section 1.4.4

**Acceptance Criteria**:
- [ ] AC-011: Plugin deployable via docker cp + restart
- [ ] AC-012: Configuration via moltbot.json with no hardcoded secrets

#### Features

##### FEAT-005-001: Container Deployment `MTH`

**ID**: FEAT-005-001
**Priority**: MTH
**Description**: Deployment scripts and documentation for Docker container.
**Traces To**: US-008

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-005-001-001 | Deployment script that copies plugin, catalog, skill to container | MTH | Single script deploys all components |
| REQ-005-001-002 | Script installs npm dependencies inside container | MTH | Plugin dependencies available after deploy |
| REQ-005-001-003 | Script registers plugin in moltbot.json | MTH | Plugin enabled and configured in gateway config |

##### FEAT-005-002: Configuration Management `MTH`

**ID**: FEAT-005-002
**Priority**: MTH
**Description**: Plugin configuration via moltbot.json.
**Traces To**: BR-018

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-005-002-001 | anthropicApiKey configurable via moltbot.json or env var fallback | MTH | API key never hardcoded in source |
| REQ-005-002-002 | model configurable with default claude-sonnet-4-20250514 | MTH | Model can be changed without code changes |
| REQ-005-002-003 | maxSuggestions and language configurable | MTH | Defaults work, overrides respected |

## 2.5 Technical Requirements

| ID | Category | Requirement | Priority | Rationale |
|----|----------|-------------|----------|-----------|
| TECH-001 | Architecture | Plugin follows CyberDemo pattern: register → registerTool → action switch | MTH | Proven pattern, team familiarity |
| TECH-002 | Architecture | TypeScript source compiled for OpenClaw runtime | MTH | Gateway expects compiled JS |
| TECH-003 | Security | Anthropic API key from config/env, never in source code | MTH | Credential protection |
| TECH-004 | Error Handling | All Claude API calls wrapped in try/catch with meaningful error messages | MTH | Graceful degradation |
| TECH-005 | Performance | ICD-10 catalog loaded once at plugin init, cached in memory | MTH | Avoid 15MB file read per request |
| TECH-006 | Compatibility | Use @anthropic-ai/sdk for Claude API calls | MTH | Official SDK, maintained |
| TECH-007 | Testing | Unit tests for each action with mocked Claude responses | MTH | Verify logic without API calls |
| TECH-008 | Testing | Integration test with real gateway (when available) | NTH | End-to-end verification |

## 2.6 Integration Requirements

| ID | External System | Requirement | Priority | Interface Type |
|----|-----------------|-------------|----------|----------------|
| INT-001 | OpenClaw Gateway | Plugin registers via api.registerTool() and responds to tool calls over WebSocket | MTH | WebSocket MCP |
| INT-002 | Anthropic Claude API | Plugin calls claude-sonnet-4 for text and vision analysis | MTH | REST API (SDK) |
| INT-003 | Medicum Frontend | Frontend stores call gateway via mcpClient.request('tools/call', ...) | MTH | WebSocket |
| INT-004 | ICD-10 Catalog File | Plugin reads JSON catalog from local filesystem at init | MTH | File I/O |

## 2.7 Data Requirements

| ID | Entity | Description | Priority |
|----|--------|-------------|----------|
| DATA-001 | ICD-10 Catalog | JSON file with ~70,000 ICD-10 codes (codigo, descripcion_es, capitulo, subcapitulo) | MTH |
| DATA-002 | System Prompts | 4 medical system prompts (SOAP, ICD-10, Image, Report) as TypeScript constants | MTH |
| DATA-003 | Plugin Manifest | openclaw.plugin.json with configSchema | MTH |
| DATA-004 | Patient Demo Data | Existing paciente_demo.json (no changes) | MTH |

## 2.8 Non-Functional Requirements (Detailed)

| ID | Category | Requirement | Priority |
|----|----------|-------------|----------|
| NFR-001 | Performance | SOAP generation responds within 10 seconds | MTH |
| NFR-002 | Performance | ICD-10 text search responds within 500ms | MTH |
| NFR-003 | Performance | Image analysis responds within 30 seconds | MTH |
| NFR-004 | Availability | Frontend gracefully falls back to demo data when gateway unavailable | MTH |
| NFR-005 | Security | No patient data logged in audit hooks (only action summaries) | MTH |
| NFR-006 | Usability | Loading indicators shown during all AI processing | MTH |
| NFR-007 | Usability | Error messages displayed in Spanish | MTH |
| NFR-008 | Maintainability | System prompts in separate files, easily modifiable | MTH |

---

# VERIFICATION SECTION

## 2.9 Full Traceability Matrix

| Req ID | Source | Description | Priority | Code File | Tests | Verified |
|--------|--------|-------------|----------|-----------|-------|----------|
| REQ-001-001-001 | US-007, BR-018 | Plugin manifest with configSchema | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-002 | US-007, BR-015 | Entry point index.ts with register/registerTool | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-003 | US-007, BR-015 | medicum-tool.ts action switch dispatcher | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-004 | BR-017 | Standardized response format | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-001 | US-001, BR-001 | generate_soap accepts transcription + context | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-002 | US-001, BR-001 | Format transcription as dialogue | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-003 | BR-003 | Medical SOAP system prompt | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-004 | BR-003 | Return structured SOAP JSON | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-005 | BR-002 | Handle insufficient transcription | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-001 | US-003, BR-006 | suggest_icd10 accepts diagnosis + context | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-002 | BR-005, BR-008 | Pre-filter catalog locally (~50 candidates) | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-003 | BR-006 | Claude ranks candidates with context | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-004 | BR-006, BR-007 | Return ranked suggestions with confidence | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-005 | BR-005 | Configurable maxSuggestions limit | MTH | [ ] | [ ] | [ ] |
| REQ-001-004-001 | US-004, BR-008 | search_icd10 accepts query + limit | MTH | [ ] | [ ] | [ ] |
| REQ-001-004-002 | BR-005, BR-008 | Search full catalog by code/description | MTH | [ ] | [ ] | [ ] |
| REQ-001-004-003 | BR-008 | Return results with total_matches | MTH | [ ] | [ ] | [ ] |
| REQ-001-004-004 | BR-008 | Search completes in <500ms | MTH | [ ] | [ ] | [ ] |
| REQ-001-005-001 | US-005, BR-010 | analyze_image accepts image + metadata | MTH | [ ] | [ ] | [ ] |
| REQ-001-005-002 | BR-010 | Send image to Claude Vision | MTH | [ ] | [ ] | [ ] |
| REQ-001-005-003 | BR-011 | Return structured findings | MTH | [ ] | [ ] | [ ] |
| REQ-001-005-004 | BR-012 | Include AI disclaimer in response | MTH | [ ] | [ ] | [ ] |
| REQ-001-005-005 | BR-012 | Include limitations field | MTH | [ ] | [ ] | [ ] |
| REQ-001-006-001 | US-006, BR-013 | generate_report accepts findings + study + patient | MTH | [ ] | [ ] | [ ] |
| REQ-001-006-002 | BR-013 | Report with 5 standard sections | MTH | [ ] | [ ] | [ ] |
| REQ-001-006-003 | BR-014 | Report includes patient/study metadata | MTH | [ ] | [ ] | [ ] |
| REQ-001-006-004 | BR-013 | Return structured JSON report | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-001 | US-001, BR-001 | Replace DEMO_SOAP with gateway call | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-002 | BR-001 | Pass real transcription + patient context | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-003 | US-001 | Add isGeneratingSOAP loading state | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-004 | BR-004 | Fallback to DEMO_SOAP when gateway down | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-001 | US-003, BR-005 | Replace loadSuggestions with gateway call | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-002 | US-004, BR-005 | Replace searchCodes with gateway call | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-003 | BR-005 | Remove DEMO_SUGGESTIONS constant | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-004 | BR-005 | Remove DEMO_ICD10_CATALOG constant | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-005 | US-003 | Add loading states for coding operations | MTH | [ ] | [ ] | [ ] |
| REQ-002-003-001 | US-005, BR-010 | Replace analyzeImage setTimeout with gateway call | MTH | [ ] | [ ] | [ ] |
| REQ-002-003-002 | BR-010 | Convert image to base64 before sending | MTH | [ ] | [ ] | [ ] |
| REQ-002-003-003 | BR-010 | Remove DEMO_KNEE_FINDINGS constant | MTH | [ ] | [ ] | [ ] |
| REQ-002-003-004 | BR-013 | Replace DEMO_KNEE_REPORT with gateway call | MTH | [ ] | [ ] | [ ] |
| REQ-002-003-005 | US-005 | Add loading states for image operations | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-001 | BR-005 | ICD-10 catalog JSON ~70,000 codes | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-002 | TECH-005 | Catalog loaded once, cached in memory | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-003 | BR-005, BR-009 | Catalog from official OMS/MSSSI source | MTH | [ ] | [ ] | [ ] |
| REQ-003-002-001 | BR-003 | SOAP system prompt | MTH | [ ] | [ ] | [ ] |
| REQ-003-002-002 | BR-006 | ICD-10 ranking system prompt | MTH | [ ] | [ ] | [ ] |
| REQ-003-002-003 | BR-011 | Image analysis system prompt | MTH | [ ] | [ ] | [ ] |
| REQ-003-002-004 | BR-013 | Report generation system prompt | MTH | [ ] | [ ] | [ ] |
| REQ-004-001-001 | BR-012 | AI disclaimer hook on image/report actions | MTH | [ ] | [ ] | [ ] |
| REQ-004-001-002 | BR-012 | Verify ai_disclaimer field present | MTH | [ ] | [ ] | [ ] |
| REQ-004-002-001 | US-001 | Consultation workflow SKILL.md | NTH | [ ] | [ ] | [ ] |
| REQ-004-002-002 | BR-012 | Disclaimer in skill instructions | NTH | [ ] | [ ] | [ ] |
| REQ-004-003-001 | BR-009 | Audit-medical hook for logging | NTH | [ ] | [ ] | [ ] |
| REQ-004-003-002 | BR-009 | Validate-icd10 hook for code verification | NTH | [ ] | [ ] | [ ] |
| REQ-005-001-001 | US-008 | Deployment script for container | MTH | [ ] | [ ] | [ ] |
| REQ-005-001-002 | US-008 | Install npm dependencies in container | MTH | [ ] | [ ] | [ ] |
| REQ-005-001-003 | BR-018 | Register plugin in moltbot.json | MTH | [ ] | [ ] | [ ] |
| REQ-005-002-001 | BR-018, TECH-003 | API key from config/env | MTH | [ ] | [ ] | [ ] |
| REQ-005-002-002 | BR-018 | Configurable model | MTH | [ ] | [ ] | [ ] |
| REQ-005-002-003 | BR-018 | Configurable maxSuggestions and language | MTH | [ ] | [ ] | [ ] |
| TECH-001 | 1.4.4 | CyberDemo plugin pattern | MTH | [ ] | [ ] | [ ] |
| TECH-002 | 1.4.4 | TypeScript compiled for runtime | MTH | [ ] | [ ] | [ ] |
| TECH-003 | 1.5 | API key from config/env only | MTH | [ ] | [ ] | [ ] |
| TECH-004 | 1.5 | Try/catch on all Claude calls | MTH | [ ] | [ ] | [ ] |
| TECH-005 | 1.5 | Catalog cached in memory | MTH | [ ] | [ ] | [ ] |
| TECH-006 | BR-015 | Use @anthropic-ai/sdk | MTH | [ ] | [ ] | [ ] |
| TECH-007 | BR-001 | Unit tests with mocked Claude | MTH | [ ] | [ ] | [ ] |
| TECH-008 | BR-016 | Integration test with real gateway | NTH | [ ] | [ ] | [ ] |
| INT-001 | 1.4.4 | Plugin registers in OpenClaw via registerTool | MTH | [ ] | [ ] | [ ] |
| INT-002 | 1.4.4 | Claude API calls via SDK | MTH | [ ] | [ ] | [ ] |
| INT-003 | 1.4.1 | Frontend calls gateway via mcpClient | MTH | [ ] | [ ] | [ ] |
| INT-004 | 1.4.2 | ICD-10 catalog file read at init | MTH | [ ] | [ ] | [ ] |
| DATA-001 | 1.4.2 | ICD-10 catalog JSON 70K codes | MTH | [ ] | [ ] | [ ] |
| DATA-002 | BR-003, BR-011 | 4 medical system prompts | MTH | [ ] | [ ] | [ ] |
| DATA-003 | 1.4.4 | Plugin manifest | MTH | [ ] | [ ] | [ ] |
| DATA-004 | US-001 | Patient demo data (existing) | MTH | [ ] | [ ] | [ ] |
| NFR-001 | 1.5 | SOAP < 10s | MTH | [ ] | [ ] | [ ] |
| NFR-002 | 1.5 | ICD-10 search < 500ms | MTH | [ ] | [ ] | [ ] |
| NFR-003 | 1.5 | Image analysis < 30s | MTH | [ ] | [ ] | [ ] |
| NFR-004 | 1.5 | Graceful fallback to demo | MTH | [ ] | [ ] | [ ] |
| NFR-005 | 1.5 | No patient data in logs | MTH | [ ] | [ ] | [ ] |
| NFR-006 | 1.5 | Loading indicators | MTH | [ ] | [ ] | [ ] |
| NFR-007 | 1.5 | Error messages in Spanish | MTH | [ ] | [ ] | [ ] |
| NFR-008 | 1.5 | Prompts in separate files | MTH | [ ] | [ ] | [ ] |

## Part 1 to Part 2 Traceability

| Part 1 Section | Description | Covered in Part 2 | Requirement IDs |
|----------------|-------------|-------------------|-----------------|
| 1.4.1 | Consultation Documentation (SOAP) | [x] | REQ-001-002-001 to REQ-001-002-005, REQ-002-001-001 to REQ-002-001-004 |
| 1.4.2 | Clinical Coding (ICD-10) | [x] | REQ-001-003-001 to REQ-001-003-005, REQ-001-004-001 to REQ-001-004-004, REQ-002-002-001 to REQ-002-002-005 |
| 1.4.3 | Medical Image Analysis | [x] | REQ-001-005-001 to REQ-001-005-005, REQ-001-006-001 to REQ-001-006-004, REQ-002-003-001 to REQ-002-003-005 |
| 1.4.4 | Gateway Plugin & Deployment | [x] | REQ-001-001-001 to REQ-001-001-004, REQ-005-001-001 to REQ-005-002-003 |
| US-001 | SOAP from transcription | [x] | REQ-001-002-001, REQ-002-001-001 |
| US-002 | SOAP with patient context | [x] | REQ-001-002-001, REQ-002-001-002 |
| US-003 | ICD-10 suggestions | [x] | REQ-001-003-001, REQ-002-002-001 |
| US-004 | ICD-10 catalog search | [x] | REQ-001-004-001, REQ-002-002-002 |
| US-005 | Image analysis | [x] | REQ-001-005-001, REQ-002-003-001 |
| US-006 | Radiology report | [x] | REQ-001-006-001, REQ-002-003-004 |
| US-007 | Single plugin with actions | [x] | REQ-001-001-001 to REQ-001-001-004 |
| US-008 | Docker deployment | [x] | REQ-005-001-001 to REQ-005-001-003 |
| BR-001 | Real transcription, not hardcoded | [x] | REQ-001-002-001, REQ-002-001-001, REQ-002-001-002 |
| BR-002 | Insufficient data handling | [x] | REQ-001-002-005 |
| BR-003 | Structured SOAP JSON | [x] | REQ-001-002-003, REQ-001-002-004, REQ-003-002-001 |
| BR-004 | Demo fallback when unavailable | [x] | REQ-002-001-004 |
| BR-005 | 70K ICD-10 catalog | [x] | REQ-001-003-002, REQ-003-001-001 |
| BR-006 | AI-ranked suggestions | [x] | REQ-001-003-003, REQ-001-003-004, REQ-003-002-002 |
| BR-007 | Primary/secondary diagnosis | [x] | REQ-001-003-004 |
| BR-008 | Deterministic text search | [x] | REQ-001-004-002, REQ-001-004-004 |
| BR-009 | Validate codes against catalog | [x] | REQ-004-003-002 |
| BR-010 | Claude Vision real analysis | [x] | REQ-001-005-002, REQ-002-003-001 |
| BR-011 | Structured findings format | [x] | REQ-001-005-003, REQ-003-002-003 |
| BR-012 | AI disclaimer | [x] | REQ-001-005-004, REQ-004-001-001, REQ-004-001-002 |
| BR-013 | Standard radiology format | [x] | REQ-001-006-002, REQ-003-002-004 |
| BR-014 | Patient/study metadata in report | [x] | REQ-001-006-003 |
| BR-015 | CyberDemo plugin pattern | [x] | TECH-001, REQ-001-001-002 |
| BR-016 | WebSocket MCP protocol | [x] | INT-001, INT-003 |
| BR-017 | Standardized response format | [x] | REQ-001-001-004 |
| BR-018 | Configurable via moltbot.json | [x] | REQ-005-002-001 to REQ-005-002-003 |

## Summary Statistics

| Category | MTH Count | NTH Count | Total |
|----------|-----------|-----------|-------|
| Epics | 4 | 1 | 5 |
| Features | 14 | 2 | 16 |
| Requirements (REQ) | 53 | 4 | 57 |
| Technical (TECH) | 7 | 1 | 8 |
| Integration (INT) | 4 | 0 | 4 |
| Data (DATA) | 4 | 0 | 4 |
| Non-Functional (NFR) | 8 | 0 | 8 |
| **Total** | **76** | **5** | **81** |

---

*Document generated by SoftwareBuilderX v23.0.0*
*Input: MEDICUM_OPENCLOUD_FUNCTIONAL_DESCRIPTION.md v2.0.0*
