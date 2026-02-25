# Medicum v2 — Functional Description

**AI-Powered Clinical Consultation Assistant**

**Version:** 2.0.0
**Date:** February 2026
**Status:** Design
**Location:** `SoulInTheBot/AIPerson/person.ai/medicum-demo/`
**Stack:** React 18 + Vite + TypeScript + Tailwind CSS + Zustand + AgentFlow Design System

---

## 1. Executive Summary

Medicum is an AI-powered clinical consultation assistant that transforms how physicians document and manage patient encounters. During a live consultation, the application listens to the doctor-patient conversation and autonomously:

- Transcribes speech in real time (Whisper GPU)
- Fills the SOAP clinical note automatically
- Converts medical terms to CIE-10 and SNOMED CT codes in real time
- Retrieves relevant patient history, images, and lab results
- Suggests possible diagnoses, recommended tests, and alternative treatments
- Looks up medications in pharmacological databases with posology
- Surfaces relevant international medical studies and clinical guidelines
- Highlights regions of interest on medical images using AI vision

The v2 redesign elevates the UI from a functional prototype to a **spectacular, enterprise-grade clinical workstation** while making every AI capability visible, transparent, and useful in real time.

---

## 2. Current State Analysis (v1)

### 2.1 Existing Architecture

| Component | Technology | Status |
|-----------|-----------|--------|
| Frontend | React 18 + Vite 4 + Tailwind 3.3 + Zustand 4.4 | Functional prototype |
| Transcription | Whisper GPU via proxy (`localhost:3050`) | Working with VAD |
| State Management | 6 Zustand stores (patient, transcription, coding, image, connection, tab) | Complete |
| MCP Integration | WebSocket client for agent control | Basic scaffolding |
| Design | Light-only, system fonts, `medical-primary` (#0066CC) palette | Basic |

### 2.2 Existing Tabs

| Tab | Features | Limitations |
|-----|----------|------------|
| **Consulta** | Whisper transcription with VAD, speaker toggle (doctor/patient), audio level visualization, SOAP note panel | SOAP generation is hardcoded demo data. No real AI generation. No real-time processing. |
| **Historia** | Accordion sections (personal, family, surgical backgrounds, lab results, clinical episodes) | Read-only static display. No AI-driven retrieval. No contextual surfacing. |
| **Codificación** | AI suggestion cards with confidence scores, CIE-10 search, primary/secondary code assignment, validation | Suggestions are pre-loaded, not real-time. No SNOMED. No conversion during conversation. |
| **Visor** | Image selector, zoom controls, AI analysis button, findings with confidence, radiological report | Analysis is simulated. No real AI vision. No region highlighting on images. |

### 2.3 Key v1 Gaps

1. **No real-time AI assistant** — The app transcribes but does not think
2. **No live SOAP generation** — Uses hardcoded demo data
3. **No contextual retrieval** — Does not access patient history during conversation
4. **No medication intelligence** — No drug lookup, interactions, or posology
5. **No diagnostic reasoning** — No differential diagnosis suggestions
6. **No clinical decision support** — No recommended tests or alternative treatments
7. **No medical literature** — No evidence-based references
8. **No AI vision** — Image analysis is simulated with no real model
9. **No visible reasoning** — The AI's thought process is invisible to the user
10. **Basic UI** — Functional but not visually impressive for a demo

---

## 3. Medicum v2 Vision

### 3.1 Core Concept

Medicum v2 transforms the application from a **transcription tool** into an **intelligent clinical copilot** that works alongside the physician in real time. Every AI action is visible, transparent, and contextually relevant.

The physician speaks naturally with the patient. The AI listens, understands, and autonomously performs multiple concurrent tasks — all visible on screen as they happen.

### 3.2 Design Philosophy

| Principle | Implementation |
|-----------|---------------|
| **Show the Work** | Every AI action appears in the reasoning stream — the doctor sees *why* the AI suggests something |
| **Ambient Intelligence** | The AI works silently in the background; the doctor never needs to click or ask |
| **Clinical Trust** | Confidence scores, source citations, and evidence links accompany every suggestion |
| **Zero Friction** | The primary workflow (talking to the patient) requires zero interaction with the UI |
| **Progressive Disclosure** | Summary first, detail on demand — nothing clutters the screen unless relevant |
| **Visual Spectacle** | Smooth animations, real-time streaming text, glowing highlights, and fluid transitions make the AI's work visually compelling |

---

## 4. Application Layout (v2)

### 4.1 Three-Column Layout

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Patient Header (sticky)                                          [🎤] [⚙] [◐] │
├────────────────────────┬──────────────────────────┬─────────────────────────────┤
│                        │                          │                             │
│   LEFT PANEL           │   CENTER PANEL           │   AI COPILOT PANEL          │
│   (Transcription +     │   (Context-dependent:    │   (Persistent right sidebar) │
│    SOAP Note)          │    SOAP / Historia /     │                             │
│                        │    Codificación / Visor) │   ┌─────────────────────┐   │
│   ┌──────────────┐     │                          │   │  🧠 AI Reasoning    │   │
│   │ 🎙 Live      │     │   Dynamic workspace      │   │  Stream             │   │
│   │ Transcript   │     │   that changes based on  │   │  (continuous scroll)│   │
│   │ (scrolling)  │     │   what the AI detects    │   │                     │   │
│   │              │     │   in the conversation    │   │  • Analyzing symptom│   │
│   │              │     │                          │   │  • Retrieving image │   │
│   │              │     │                          │   │  • Found CIE-10 code│   │
│   └──────────────┘     │                          │   │  • Checking drug... │   │
│   ┌──────────────┐     │                          │   └─────────────────────┘   │
│   │ 📋 SOAP Note │     │                          │   ┌─────────────────────┐   │
│   │ (live fill)  │     │                          │   │  💊 Suggestions     │   │
│   │ S: ...       │     │                          │   │  (collapsible cards)│   │
│   │ O: ...       │     │                          │   │                     │   │
│   │ A: ...       │     │                          │   │  Diagnosis: ...     │   │
│   │ P: ...       │     │                          │   │  Tests: ...         │   │
│   └──────────────┘     │                          │   │  Medications: ...   │   │
│                        │                          │   └─────────────────────┘   │
├────────────────────────┴──────────────────────────┴─────────────────────────────┤
│  Status Bar: [Whisper: Connected] [AI Model: Active] [Patient: María García]    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Panel Dimensions

| Panel | Width | Behavior |
|-------|-------|----------|
| Left (Transcription + SOAP) | 360px fixed | Always visible during consultation |
| Center (Workspace) | Flexible (remaining space) | Content changes based on AI context or manual tab selection |
| Right (AI Copilot) | 400px | Collapsible/expandable, floatable, resizable. Persistent across all views. |

### 4.3 Patient Header (v2)

The header is redesigned as a compact, information-dense clinical bar:

- **Left**: Patient avatar (initials or photo), full name, age, sex, NHC
- **Center**: Active allergies (severity-coded badges), active medications (pill icons), key vitals summary
- **Right**: Recording indicator (pulsing red dot when active), AI model status, theme/font controls
- **Background**: Subtle gradient with glassmorphism (`backdrop-blur`, translucent)

---

## 5. AI Copilot Panel — The Core Innovation

### 5.1 AI Reasoning Stream

The centerpiece of the right panel is a **continuous reasoning stream** that shows the AI's thought process in real time as the conversation unfolds. This is the "show the work" principle in action.

**Stream Entry Types:**

| Entry Type | Icon | Visual Style | Content |
|------------|------|-------------|---------|
| **Listening** | 🎧 | Subtle gray, pulsing | "Listening to conversation..." |
| **Understanding** | 🧠 | Blue, animated dots | "Detected symptom: knee pain on stairs" |
| **Retrieving** | 🔍 | Cyan, loading spinner | "Searching patient history for knee-related records..." |
| **Found** | ✅ | Green, slide-in | "Found: X-ray right knee (2025-08-15)" |
| **Coding** | 🏷️ | Purple, tag animation | "Mapped to CIE-10: M17.11 — Primary osteoarthritis, right knee" |
| **Drug Lookup** | 💊 | Amber, pill icon | "Checking Paracetamol interactions with current medications..." |
| **Diagnosis** | 🩺 | Blue gradient card | "Suggested: Gonartrosis grade II-III (confidence: 87%)" |
| **Alert** | ⚠️ | Red, attention pulse | "Interaction warning: Metformin + Ibuprofen renal risk" |
| **Literature** | 📚 | Teal, citation format | "Recent study: OARSI 2025 guidelines recommend..." |
| **Image Analysis** | 🖼️ | Indigo, thumbnail | "Highlighting medial joint space narrowing on X-ray" |

**Visual Characteristics:**
- Entries stream upward in a continuous scroll (newest at bottom)
- Each entry has a timestamp, icon, animated entrance (fade-in + slide-up)
- Entries can be collapsed/expanded for detail
- A "thinking" animation (three pulsing dots) appears between entries
- Color-coded left border for quick visual scanning

### 5.2 Suggestion Cards

Below the reasoning stream, collapsible suggestion cards appear as the AI accumulates findings:

#### 5.2.1 Diagnostic Suggestions Card

```
┌─────────────────────────────────────┐
│ 🩺 Possible Diagnoses              │
├─────────────────────────────────────┤
│ ● Gonartrosis primaria rodilla D.  │
│   M17.11 · Confidence: 87%         │
│   [View evidence] [Accept]         │
│                                     │
│ ○ Meniscopatía degenerativa        │
│   M23.30 · Confidence: 42%         │
│   [View evidence] [Accept]         │
│                                     │
│ ○ Bursitis rotuliana               │
│   M70.50 · Confidence: 18%         │
│   [View evidence] [Dismiss]        │
└─────────────────────────────────────┘
```

#### 5.2.2 Recommended Tests Card

```
┌─────────────────────────────────────┐
│ 🧪 Recommended Tests                │
├─────────────────────────────────────┤
│ ◻ Radiografía rodilla AP + Lateral │
│   Reason: Confirm joint space       │
│   narrowing and osteophyte grading  │
│   Priority: HIGH                    │
│                                     │
│ ◻ Analítica: VSG, PCR, Factor R.   │
│   Reason: Rule out inflammatory     │
│   arthritis given morning stiffness │
│   Priority: MEDIUM                  │
│                                     │
│ ◻ Resonancia magnética rodilla     │
│   Reason: Evaluate meniscus and     │
│   cartilage if conservative tx fails│
│   Priority: LOW (if X-ray normal)   │
└─────────────────────────────────────┘
```

#### 5.2.3 Medication Intelligence Card

```
┌─────────────────────────────────────┐
│ 💊 Medication Recommendation        │
├─────────────────────────────────────┤
│ Paracetamol 1g / 8h                │
│ Posología: 1 comprimido c/8h       │
│ Duración: 2-4 semanas              │
│ Source: Vademécum / AEMPS          │
│                                     │
│ ⚠ Alternatives considered:         │
│ · Ibuprofeno 600mg — Descartado    │
│   (Metformin interaction, renal)    │
│ · Metamizol 575mg — Viable         │
│   (Lower GI risk)                   │
│                                     │
│ 📚 OARSI 2025: First-line therapy  │
│    for knee OA is paracetamol +     │
│    topical NSAIDs                   │
│    [Open full study]                │
└─────────────────────────────────────┘
```

#### 5.2.4 Medical Literature Card

```
┌─────────────────────────────────────┐
│ 📚 Relevant Literature              │
├─────────────────────────────────────┤
│ 1. "2025 OARSI Guidelines for      │
│    Management of Osteoarthritis"    │
│    Arthritis & Rheumatology, 2025   │
│    Key finding: Graduated exercise  │
│    + weight management reduces      │
│    surgical intervention by 34%     │
│    [View abstract] [Full text]      │
│                                     │
│ 2. "Hyaluronic Acid vs PRP for     │
│    Knee Osteoarthritis: RCT 2025"  │
│    NEJM, 2025                       │
│    Key finding: PRP showed superior │
│    outcomes at 12 months            │
│    [View abstract] [Full text]      │
└─────────────────────────────────────┘
```

### 5.3 AI Copilot Behavior Modes

| Mode | Trigger | Behavior |
|------|---------|----------|
| **Floating Widget** | Default when panel is collapsed | Small floating bubble (bottom-right) showing entry count badge. Click to expand. |
| **Side Panel** | Click to expand or drag to dock | Full 400px right panel with reasoning stream + suggestion cards |
| **Fullscreen Focus** | Double-click on any suggestion card | Card expands to fill the center panel for detailed review |
| **Minimized** | User explicitly minimizes | Only a thin bar at the right edge with a pulsing indicator when new entries arrive |

---

## 6. Center Panel — Context-Adaptive Workspace

### 6.1 Automatic Context Switching

The center panel's content changes automatically based on what the AI detects in the conversation. The physician never needs to manually switch tabs during a consultation.

| Conversation Trigger | Center Panel Action |
|---------------------|---------------------|
| Doctor mentions "X-ray" or "image" | Visor appears with the relevant image pre-loaded. AI highlights regions of interest. |
| Doctor mentions a medication name | Medication detail card appears with posology, interactions, contraindications |
| Doctor mentions "history" or "previous visit" | Patient history panel opens, scrolled to the relevant episode |
| Doctor mentions "lab results" or a specific parameter | Lab results table appears with the relevant parameter highlighted |
| Doctor discusses a diagnosis | Codification panel appears with pre-selected CIE-10/SNOMED suggestions |
| No specific trigger detected | SOAP note occupies the center in an expanded, editable view |

### 6.2 Manual Override Tabs

A subtle tab bar (horizontally at the top of the center panel) allows the physician to manually override the auto-switching at any time:

| Tab | Content |
|-----|---------|
| **SOAP** | Expanded SOAP note editor (auto-populated from conversation) |
| **Historia** | Full patient history with accordion sections |
| **Codificación** | CIE-10/SNOMED coding workspace |
| **Visor** | Medical image viewer with AI analysis |
| **Farmacia** | Medication lookup, interactions checker, prescription pad |
| **Estudios** | Medical literature search and references |

---

## 7. Feature Specifications

### 7.1 Real-Time SOAP Note Generation

**How it works:**
1. Whisper transcribes each speech segment
2. Each segment is immediately sent to the LLM with the full conversation context
3. The LLM classifies the content into S/O/A/P categories
4. Each SOAP section updates incrementally with streaming text (typewriter effect)
5. The physician can edit any section manually at any time
6. Edits are preserved — AI appends, never overwrites manual changes

**Visual Treatment:**
- Each SOAP section has a colored left border: S (blue), O (green), A (amber), P (purple)
- New text appears with a subtle highlight animation that fades after 2 seconds
- A small AI badge indicates which content was AI-generated vs manually entered
- Confidence indicator per section

### 7.2 Real-Time Medical Coding

**How it works:**
1. As the SOAP note fills, the AI continuously identifies codifiable terms
2. CIE-10 and SNOMED CT mappings are computed in parallel
3. Suggestions appear in the AI reasoning stream with confidence scores
4. The physician can accept, reject, or modify any suggestion
5. Primary diagnosis is auto-detected; secondary diagnoses are ranked by relevance

**Visual Treatment:**
- Codifiable terms in the SOAP note are underlined with a dotted line
- Hovering a term shows the proposed code(s) in a tooltip
- Accepted codes appear as colored chips at the bottom of the SOAP section
- A running code summary panel shows all assigned codes with CIE-10 and SNOMED CT side by side

### 7.3 Contextual Patient History Retrieval

**How it works:**
1. The AI monitors the conversation for clinically relevant keywords
2. When a keyword maps to existing patient data, the AI proactively retrieves it
3. The retrieved data appears in the center panel and/or as a reasoning stream entry
4. Related historical episodes, images, and lab results are cross-referenced

**Examples:**
- Doctor says "knee": AI retrieves previous knee X-ray, related episodes, and relevant lab results
- Doctor says "last blood test": AI surfaces the most recent lab results with out-of-range values highlighted
- Doctor says "previous surgery": AI opens the surgical history with the matching procedure

### 7.4 Medical Image AI Analysis

**How it works:**
1. When an image is surfaced, the AI vision model analyzes it
2. Regions of interest are highlighted with bounding boxes or heatmaps overlaid on the image
3. Findings appear as annotated markers that can be clicked for detail
4. A structured radiological report is generated

**Visual Treatment:**
- Semi-transparent colored overlays on identified regions (red = pathological, green = normal, yellow = uncertain)
- Clickable numbered markers on the image linking to findings
- Findings panel with confidence bars and anatomical descriptions
- Side-by-side comparison mode for historical images

### 7.5 Medication Intelligence

**How it works:**
1. When a medication is mentioned, the AI queries pharmacological databases
2. The drug's ficha técnica (summary of product characteristics) is retrieved
3. Interactions with the patient's current medication list are checked automatically
4. Posology is calculated based on patient data (age, weight, renal function, etc.)
5. Alternative medications are suggested when interactions or contraindications are detected

**Data Sources (simulated for demo):**
- AEMPS (Agencia Española de Medicamentos)
- Vademécum
- BNF (British National Formulary)
- FDA Drug Interactions Database

**Visual Treatment:**
- Drug cards with key info: active ingredient, dosage forms, posology, contraindications
- Interaction matrix showing current medications vs proposed medication
- Color-coded risk levels: green (safe), yellow (monitor), red (contraindicated)
- Quick prescription builder: dosage, frequency, duration, route

### 7.6 Diagnostic Reasoning

**How it works:**
1. The AI maintains a running differential diagnosis based on conversation content
2. As new information is added (symptoms, history, exam findings), probabilities are recalculated
3. Diagnoses are ranked by probability and displayed with supporting evidence
4. The AI explains its reasoning for each diagnosis

**Visual Treatment:**
- Ranked list with probability bars (horizontal, gradient-filled)
- Each diagnosis expandable to show the evidence chain (which symptoms support it)
- "Red flags" highlighted with pulsing attention indicators
- Comparison view: what supports diagnosis A vs B

### 7.7 Clinical Decision Support

**How it works:**
1. Based on the working diagnosis and patient context, the AI recommends:
   - Diagnostic tests to confirm/rule out
   - Treatment protocols per clinical guidelines
   - Referral suggestions when appropriate
2. Recommendations are linked to clinical guidelines (NICE, OARSI, ESC, etc.)
3. Alternative treatment pathways are presented when the AI identifies potentially better options

**Visual Treatment:**
- Decision tree visualization for complex pathways
- Prioritized checklist with checkboxes for the physician to accept/decline
- Evidence tags linking each recommendation to its source guideline
- Cost/benefit indicators when relevant

### 7.8 Medical Literature Integration

**How it works:**
1. The AI identifies the clinical context and searches for relevant recent literature
2. Results are filtered by relevance, recency, and evidence quality (RCT > cohort > case report)
3. Key findings are extracted and summarized in plain language
4. Full abstracts and links to full text are available

**Visual Treatment:**
- Citation cards with: title, journal, year, key finding summary
- Evidence quality badge (A/B/C)
- "Why this paper?" explanation linking it to the current consultation
- Save/bookmark for later review

---

## 8. Visual Design Specification

### 8.1 Design System

Medicum v2 adopts the **AgentFlow Design System v2.0** with medical-specific extensions:

| Token | Dark Mode | Light Mode | Use |
|-------|-----------|------------|-----|
| `--medical-primary` | `#60a5fa` (primary-400) | `#2563eb` (primary-600) | Primary actions, doctor bubbles, CIE codes |
| `--medical-accent` | `#06b6d4` (secondary-500) | `#0891b2` (secondary-600) | AI reasoning, Copilot panel accents |
| `--soap-s` | `#60a5fa` | `#2563eb` | Subjective section |
| `--soap-o` | `#22c55e` | `#15803d` | Objective section |
| `--soap-a` | `#f59e0b` | `#d97706` | Analysis section |
| `--soap-p` | `#a855f7` | `#7c3aed` | Plan section |
| `--severity-critical` | `#ef4444` | `#dc2626` | Critical alerts, high-severity allergies |
| `--severity-high` | `#f97316` | `#ea580c` | High-severity items |
| `--severity-medium` | `#eab308` | `#ca8a04` | Medium-severity items |
| `--severity-low` | `#22c55e` | `#16a34a` | Low-severity, normal values |

### 8.2 Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Patient name | Inter | 20px | 600 semibold |
| Section headers | Inter | 14px | 600 semibold |
| Body text / SOAP content | Inter | 14px | 400 regular |
| CIE-10 / SNOMED codes | JetBrains Mono | 13px | 500 medium |
| AI reasoning entries | Inter | 13px | 400 regular |
| Timestamps | JetBrains Mono | 11px | 400 regular |
| Confidence scores | JetBrains Mono | 12px | 600 semibold |
| Labels / metadata | Inter | 12px | 500 medium |

### 8.3 Animations and Microinteractions

| Animation | Duration | Easing | Trigger |
|-----------|----------|--------|---------|
| AI entry slide-in | 300ms | ease-out | New reasoning entry |
| SOAP text streaming | 30ms per character | linear | AI fills SOAP section |
| Confidence bar fill | 500ms | ease-spring | Score calculation |
| Image region highlight | 400ms | ease-out | AI identifies finding |
| Tab auto-switch | 200ms | ease-default | Context change |
| Suggestion card expand | 250ms | ease-spring | Click on card |
| Pulsing recording dot | 1.5s infinite | ease-in-out | Active recording |
| Thinking dots (3) | 1s infinite stagger | ease-in-out | AI processing |
| Drug interaction alert | 300ms + pulse | ease-spring | Alert detected |
| New entry badge count | 200ms | ease-spring | Badge number update |

### 8.4 Glassmorphism Effects

The AI Copilot panel uses subtle glassmorphism for a premium feel:
- Panel background: `rgba(15, 23, 42, 0.85)` (dark) / `rgba(255, 255, 255, 0.9)` (light)
- `backdrop-filter: blur(12px)`
- Border: 1px `rgba(148, 163, 184, 0.15)`
- Floating widget: circular, 56px, with glow shadow matching panel accent

---

## 9. Data Models (v2 Additions)

### 9.1 AI Reasoning Entry

```typescript
interface AIReasoningEntry {
  id: string;
  timestamp: number;
  type: 'listening' | 'understanding' | 'retrieving' | 'found'
      | 'coding' | 'drug_lookup' | 'diagnosis' | 'alert'
      | 'literature' | 'image_analysis' | 'recommendation';
  title: string;
  detail?: string;
  confidence?: number;
  source?: string;
  relatedEntityId?: string;
  actions?: AIAction[];
}

interface AIAction {
  label: string;
  type: 'accept' | 'reject' | 'view_detail' | 'open_link';
  payload: Record<string, unknown>;
}
```

### 9.2 Diagnostic Suggestion

```typescript
interface DiagnosticSuggestion {
  id: string;
  code: string;
  codeSystem: 'CIE10' | 'SNOMED';
  description: string;
  probability: number;
  supportingEvidence: string[];
  differentialAgainst?: string[];
  suggestedTests?: string[];
  guidelines?: GuidelineReference[];
}
```

### 9.3 Medication Intelligence

```typescript
interface MedicationLookup {
  id: string;
  name: string;
  activeIngredient: string;
  dosageForms: string[];
  posology: PosologyRecommendation;
  interactions: DrugInteraction[];
  contraindications: string[];
  sideEffects: string[];
  source: string;
  alternatives: AlternativeMedication[];
}

interface PosologyRecommendation {
  dose: string;
  frequency: string;
  duration: string;
  route: string;
  adjustments?: string;
}

interface DrugInteraction {
  drug: string;
  severity: 'contraindicated' | 'serious' | 'moderate' | 'minor';
  description: string;
  recommendation: string;
}

interface AlternativeMedication {
  name: string;
  reason: string;
  advantages: string[];
  disadvantages: string[];
}
```

### 9.4 Literature Reference

```typescript
interface LiteratureReference {
  id: string;
  title: string;
  authors: string[];
  journal: string;
  year: number;
  doi?: string;
  abstractText: string;
  keyFinding: string;
  evidenceLevel: 'A' | 'B' | 'C';
  relevanceScore: number;
  contextExplanation: string;
}
```

### 9.5 Image Region Annotation

```typescript
interface ImageAnnotation {
  id: string;
  imageId: string;
  region: {
    type: 'bounding_box' | 'heatmap' | 'polygon';
    coordinates: number[];
    color: string;
  };
  finding: string;
  confidence: number;
  clinicalSignificance: 'normal' | 'uncertain' | 'pathological';
}
```

---

## 10. Backend Services Required

### 10.1 Service Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Medicum Backend                        │
├──────────────┬───────────────┬───────────────────────────┤
│ Transcription│  AI Reasoning │  Data Services            │
│ Service      │  Orchestrator │                           │
│              │  (LangGraph)  │  ├─ Patient History API   │
│ Whisper GPU  │               │  ├─ Medication DB API     │
│ + VAD        │  Coordinates  │  ├─ Literature Search API │
│              │  all AI tasks │  ├─ CIE-10/SNOMED API     │
│              │  in parallel  │  └─ Image Analysis API    │
└──────────────┴───────────────┴───────────────────────────┘
```

### 10.2 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `WS` | `/medicum/ws/{session_id}` | WebSocket for real-time AI reasoning stream |
| `POST` | `/medicum/transcribe` | Send audio segment for transcription |
| `POST` | `/medicum/soap/generate` | Generate/update SOAP note from conversation |
| `POST` | `/medicum/coding/suggest` | Get CIE-10/SNOMED suggestions from clinical text |
| `GET` | `/medicum/patient/{id}/history` | Retrieve patient history |
| `GET` | `/medicum/patient/{id}/images` | Retrieve patient diagnostic images |
| `POST` | `/medicum/drugs/lookup` | Look up medication details and interactions |
| `POST` | `/medicum/drugs/interactions` | Check interactions against current medications |
| `POST` | `/medicum/diagnosis/differential` | Get differential diagnosis suggestions |
| `POST` | `/medicum/tests/recommend` | Get recommended tests for a diagnosis |
| `POST` | `/medicum/literature/search` | Search medical literature by clinical context |
| `POST` | `/medicum/images/analyze` | Analyze medical image with AI vision |

### 10.3 AI Reasoning Orchestrator

The orchestrator is a **LangGraph StateGraph** that coordinates all AI tasks in parallel:

```
                    ┌─────────────────┐
                    │  Conversation   │
                    │  Input (text)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  NLU / Intent   │
                    │  Classification │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
   ┌────────▼──────┐ ┌──────▼───────┐ ┌──────▼──────┐
   │ SOAP Update   │ │ Code Mapping │ │ Context     │
   │ (parallel)    │ │ (parallel)   │ │ Detection   │
   └───────────────┘ └──────────────┘ └──────┬──────┘
                                              │
                              ┌────────────────┼─────────────┐
                              │                │             │
                     ┌────────▼──────┐ ┌───────▼─────┐ ┌────▼──────┐
                     │ History       │ │ Drug        │ │ Image     │
                     │ Retrieval     │ │ Lookup      │ │ Analysis  │
                     └───────────────┘ └─────────────┘ └───────────┘
                              │                │             │
                     ┌────────▼────────────────▼─────────────▼──────┐
                     │            Diagnosis Engine                  │
                     │  (differential diagnosis + recommendations) │
                     └────────────────────┬────────────────────────┘
                                          │
                     ┌────────────────────▼────────────────────────┐
                     │         Literature Search                   │
                     │  (evidence for diagnosis + treatment)       │
                     └────────────────────┬────────────────────────┘
                                          │
                     ┌────────────────────▼────────────────────────┐
                     │     WebSocket → AI Reasoning Stream         │
                     │     (all results streamed to frontend)      │
                     └─────────────────────────────────────────────┘
```

---

## 11. Demo Strategy

### 11.1 Simulation Mode

For demonstration purposes, all backend services can operate in **simulation mode** where:

- Transcription uses pre-recorded demo conversations (with realistic timing)
- SOAP generation streams pre-written clinical notes character by character
- CIE-10/SNOMED suggestions come from a local lookup table
- Drug lookups return pre-built medication profiles
- Diagnostic suggestions follow scripted clinical scenarios
- Literature references are pre-curated for the demo diagnosis
- Image analysis overlays are pre-computed bounding boxes

### 11.2 Demo Scenarios

#### Scenario 1: Knee Osteoarthritis Consultation

A 58-year-old female patient presents with knee pain. The demo shows:
1. Conversation transcript streaming in real time
2. SOAP note filling progressively
3. AI retrieving previous knee X-ray from patient history
4. Region highlighting on the X-ray (medial joint space narrowing)
5. CIE-10 code suggestion: M17.11
6. Medication recommendation: Paracetamol (with Metformin interaction check)
7. OARSI 2025 guidelines reference
8. Recommended tests: X-ray AP + Lateral, Blood panel

#### Scenario 2: Diabetic Patient Follow-up

A 65-year-old male with Type 2 Diabetes returns for follow-up. The demo shows:
1. AI proactively surfaces latest HbA1c and glucose results
2. Medication review: current Metformin dose adequacy assessment
3. Drug interaction check when doctor considers adding a statin
4. Retinopathy screening reminder based on clinical guidelines
5. Literature reference on SGLT2 inhibitors cardiovascular benefits

#### Scenario 3: Respiratory Infection — Urgent Consultation

A 42-year-old patient presents with fever and cough. The demo shows:
1. Real-time SOAP filling with symptoms (fever 38.5°C, productive cough, dyspnea)
2. Red flag detection: dyspnea triggers "Consider pneumonia" alert
3. AI recommends chest X-ray, PCR, blood gas
4. Chest X-ray analysis showing consolidation with AI overlay
5. Antibiotic suggestion with local resistance patterns
6. COVID/Flu differential based on current epidemiological data

### 11.3 Staged Implementation

Given the complexity, the demo can be implemented in stages:

| Stage | Features | Complexity | Impact |
|-------|----------|-----------|--------|
| **Stage 1** | New 3-column layout + AI reasoning stream (simulated) + improved SOAP display | Medium | High visual impact |
| **Stage 2** | Auto-context switching + medical image region highlighting + drug cards | Medium-High | Demonstrates core AI value |
| **Stage 3** | Live transcription + real SOAP generation + real CIE-10 mapping via LLM | High | Full AI pipeline |
| **Stage 4** | Literature integration + diagnostic reasoning + clinical decision support | High | Complete clinical copilot |

---

## 12. Component Inventory (v2)

### 12.1 New Components

| Component | Location | Description |
|-----------|----------|-------------|
| `AICopilotPanel` | `components/ai-copilot/AICopilotPanel.tsx` | Main right sidebar with reasoning stream and suggestion cards |
| `ReasoningStream` | `components/ai-copilot/ReasoningStream.tsx` | Scrolling list of AI reasoning entries with animations |
| `ReasoningEntry` | `components/ai-copilot/ReasoningEntry.tsx` | Individual entry with icon, animation, expand/collapse |
| `FloatingCopilotWidget` | `components/ai-copilot/FloatingCopilotWidget.tsx` | Minimized floating bubble with badge count |
| `DiagnosticCard` | `components/ai-copilot/cards/DiagnosticCard.tsx` | Ranked diagnosis suggestions with evidence |
| `MedicationCard` | `components/ai-copilot/cards/MedicationCard.tsx` | Drug info, posology, interactions, alternatives |
| `TestRecommendationCard` | `components/ai-copilot/cards/TestRecommendationCard.tsx` | Prioritized test recommendations |
| `LiteratureCard` | `components/ai-copilot/cards/LiteratureCard.tsx` | Medical literature citation with key findings |
| `ImageAnnotationOverlay` | `components/visor/ImageAnnotationOverlay.tsx` | SVG overlay for bounding boxes and heatmaps on images |
| `SOAPNoteEditor` | `components/soap/SOAPNoteEditor.tsx` | Enhanced SOAP editor with streaming text and code chips |
| `DrugInteractionMatrix` | `components/farmacia/DrugInteractionMatrix.tsx` | Visual matrix of drug interactions |
| `PrescriptionBuilder` | `components/farmacia/PrescriptionBuilder.tsx` | Quick prescription form |
| `ClinicalTimeline` | `components/historia/ClinicalTimeline.tsx` | Visual timeline of patient clinical history |
| `ContextualTabBar` | `components/layout/ContextualTabBar.tsx` | Auto-switching tab bar for center panel |
| `ThreeColumnLayout` | `components/layout/ThreeColumnLayout.tsx` | Main layout with resizable panels |
| `StatusBar` | `components/layout/StatusBar.tsx` | Bottom bar with connection status, AI model status |

### 12.2 New Zustand Stores

| Store | Purpose |
|-------|---------|
| `aiCopilotStore` | Manages reasoning entries, suggestion cards, panel state |
| `diagnosticStore` | Tracks differential diagnoses and their probabilities |
| `medicationStore` | Drug lookups, interactions, prescription state |
| `literatureStore` | Search results, saved references |
| `layoutStore` | Panel sizes, active center tab, auto-switch preferences |

---

## 13. Non-Functional Requirements

| Category | Requirement | Target |
|----------|-------------|--------|
| Performance | AI reasoning entries appear within 200ms of generation | < 200ms |
| Performance | SOAP streaming text at readable speed | 30ms per character |
| Performance | Image annotation overlays render within 500ms | < 500ms |
| Responsiveness | Application functions on 1280px+ screens | Desktop-first |
| Accessibility | WCAG 2.2 AA compliance in both themes | All contrast ratios met |
| Accessibility | Keyboard navigation for all interactive elements | Tab/Enter/Esc |
| Theme | Dark + Light + System auto-detect | AgentFlow Design System |
| Data Privacy | No real patient data in demo mode | All data is synthetic |
| Extensibility | Plugin architecture for additional AI capabilities | Modular service design |

---

## 14. Success Metrics

The demo is considered successful when a viewer:

1. **Immediately understands** what the AI is doing (reasoning stream)
2. **Sees the AI work in real time** across multiple parallel tasks
3. **Trusts the AI's output** (confidence scores, evidence, sources)
4. **Is impressed by the visual quality** (animations, glassmorphism, fluid transitions)
5. **Recognizes the clinical value** (saves time, catches interactions, surfaces evidence)
6. **Wants to use it** — the demo creates desire, not just understanding

---

## 15. Glossary

| Term | Definition |
|------|-----------|
| **SOAP** | Subjective, Objective, Analysis, Plan — standard clinical note format |
| **CIE-10** | International Classification of Diseases, 10th Revision (Spanish: CIE-10) |
| **SNOMED CT** | Systematized Nomenclature of Medicine — Clinical Terms |
| **VAD** | Voice Activity Detection — detects when someone is speaking |
| **NHC** | Número de Historia Clínica — Patient Medical Record Number |
| **AEMPS** | Agencia Española de Medicamentos y Productos Sanitarios |
| **Posología** | Dosage regimen: dose, frequency, route, duration |
| **Gonartrosis** | Osteoarthritis of the knee (Spanish medical term) |
| **Ficha Técnica** | Summary of Product Characteristics (drug documentation) |
| **LangGraph** | Framework for orchestrating multi-step AI agent workflows |

---

*Document generated: February 2026*
*Project: SoulInTheBot / Medicum v2*
