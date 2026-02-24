# Build Plan: CyberDemo Interactive Frontend

| Attribute | Value |
|-----------|-------|
| Build ID | sbx-20260224-021825 |
| Created | 2026-02-24 |
| Functional Spec | docs/FRONTEND_FUNCTIONAL_SPEC.md |
| Template Version | SBX v21.0.0 |

---

## Build Phases

### Cycle 1: MTH (Must-To-Have)

| Phase | Description | Tasks | Status |
|-------|-------------|-------|--------|
| P1 | Core Infrastructure (Context, Hooks, Data) | 10 tasks | Pending |
| P2 | Global Components (Control Bar, aIP Widget, Narration) | 18 tasks | Pending |
| P3 | Demo Execution (Demo Cases, AI Analysis) | 12 tasks | Pending |
| P4 | Simulation Page and Integration | 16 tasks | Pending |

### Cycle 2: NTH (Nice-To-Have)

| Phase | Description | Tasks | Status |
|-------|-------------|-------|--------|
| P5 | Enhanced Features | 5 tasks | Pending |

### NFR Status

| NFR ID | Category | Status |
|--------|----------|--------|
| NFR-001 | Performance | Not implementable this phase |
| NFR-002 | Usability | Not implementable this phase |
| NFR-003 | Availability | Not implementable this phase |
| NFR-004 | Scalability | Not implementable this phase |
| NFR-005 | Security | Not implementable this phase |

---

## Task Assignments

### Build Agent Distribution

| Agent | Focus Area | Task Count |
|-------|------------|------------|
| Agent 1 | State Management and Hooks | 10 tasks |
| Agent 2 | Global UI Components | 18 tasks |
| Agent 3 | Demo Execution Features | 12 tasks |
| Agent 4 | Simulation Page and Integration | 16 tasks |

---

### Detailed Task List

#### Phase P1: Core Infrastructure

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-001 | TECH-001 | Create DemoContext provider with simulation state, narration, aIP assist, and analysis results | 1 | Pending |
| T-002 | TECH-002 | Implement useSimulation hook wrapping REST API calls (start, pause, resume, speed) | 1 | Pending |
| T-003 | TECH-003 | Implement useNarration hook managing WebSocket connection and message buffer | 1 | Pending |
| T-004 | TECH-004 | Implement useAipAssist hook managing WebSocket connection and suggestion state | 1 | Pending |
| T-005 | TECH-005 | Create Cytoscape.js graph adapter with standard interface for attack visualization | 1 | Pending |
| T-006 | DATA-001 | Define simulation state schema (scenario, phase, speed, running) in DemoContext | 1 | Pending |
| T-007 | DATA-002 | Define narration message schema (timestamp, type, content) with max 1000 entries | 1 | Pending |
| T-008 | DATA-003 | Define AI suggestions schema (id, content, status, actions) with read tracking | 1 | Pending |
| T-009 | DATA-004 | Define analysis results schema (id, decision, timestamp) per incident | 1 | Pending |
| T-010 | INT-005 | Implement WebSocket connection to /api/v1/simulation/ws for simulation events | 1 | Pending |

#### Phase P2: Global Components

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-011 | REQ-001-001-001 | Render DemoControlBar component in header layout on all pages | 2 | Pending |
| T-012 | REQ-001-001-002 | Implement scenario dropdown with 6 attack options (APT29, FIN7, Lazarus, REvil, SolarWinds, Insider) | 2 | Pending |
| T-013 | REQ-001-001-003 | Implement Play/Pause/Stop buttons with correct state transitions | 2 | Pending |
| T-014 | REQ-001-001-004 | Implement speed slider control from 0.5x to 4x | 2 | Pending |
| T-015 | REQ-001-001-005 | Display MITRE ATT&CK phase progress with colored circles | 2 | Pending |
| T-016 | REQ-001-002-001 | Position AipAssistWidget as floating component in bottom-right corner on all pages | 2 | Pending |
| T-017 | REQ-001-002-002 | Implement collapsed state with circular button and notification badge | 2 | Pending |
| T-018 | REQ-001-002-003 | Implement expanded panel displaying AI suggestions list | 2 | Pending |
| T-019 | REQ-001-002-004 | Add Analyze/Ignore/Details action buttons per suggestion item | 2 | Pending |
| T-020 | REQ-001-002-005 | Show animated thinking indicator when AI is processing | 2 | Pending |
| T-021 | REQ-001-002-006 | Update badge count reflecting unread suggestion items | 2 | Pending |
| T-022 | REQ-001-003-001 | Render NarrationFooter panel in layout footer on all pages | 2 | Pending |
| T-023 | REQ-001-003-002 | Display streaming narration messages with timestamps in terminal style | 2 | Pending |
| T-024 | REQ-001-003-003 | Apply color coding by message type (info=white, warning=yellow, error=red, success=green) | 2 | Pending |
| T-025 | REQ-001-003-004 | Implement expand/collapse toggle button for narration panel | 2 | Pending |
| T-026 | REQ-001-003-005 | Auto-scroll to most recent message on new narration entry | 2 | Pending |
| T-027 | INT-007 | Implement WebSocket connection to /api/v1/narration/ws/{session} for narration stream | 2 | Pending |
| T-028 | INT-008 | Implement WebSocket connection to /api/v1/aip-assist/ws/{session} for AI suggestions | 2 | Pending |

#### Phase P3: Demo Execution

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-029 | REQ-002-001-001 | Render DemoCasesPanel component on Dashboard page | 3 | Pending |
| T-030 | REQ-002-001-002 | Display 3 case cards showing name, host, type, and expected result | 3 | Pending |
| T-031 | REQ-002-001-003 | Invoke backend agent on card click and show analysis process | 3 | Pending |
| T-032 | REQ-002-001-004 | Show loading state with visual feedback during case execution | 3 | Pending |
| T-033 | REQ-002-001-005 | Display deterministic result matching expected outcome | 3 | Pending |
| T-034 | REQ-002-001-006 | Render approval card for Case 2 requiring human decision | 3 | Pending |
| T-035 | REQ-002-002-001 | Add Analyze with AI button to each row in Incidents table | 3 | Pending |
| T-036 | REQ-002-002-002 | Implement 3-state button (initial, processing, completed with decision icon) | 3 | Pending |
| T-037 | REQ-002-002-003 | Auto-expand narration panel when Analyze button is clicked | 3 | Pending |
| T-038 | REQ-002-002-004 | Queue analysis request asynchronously via POST /analysis/queue | 3 | Pending |
| T-039 | REQ-002-002-005 | Persist analysis result to incident record in state | 3 | Pending |
| T-040 | INT-006 | Implement REST call to POST /api/v1/analysis/queue for AI analysis | 3 | Pending |

#### Phase P4: Simulation Page and Integration

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-041 | REQ-003-001-001 | Create /simulation route in React Router configuration | 4 | Pending |
| T-042 | REQ-003-001-002 | Implement 3-column responsive layout (MITRE Phases, Visualization, aIP Panel) | 4 | Pending |
| T-043 | REQ-003-001-003 | Render vertical MITRE phase list with status indicators in left column | 4 | Pending |
| T-044 | REQ-003-001-004 | Render interactive attack graph using Cytoscape.js in center column | 4 | Pending |
| T-045 | REQ-003-001-005 | Render integrated aIP panel (not floating) in right column | 4 | Pending |
| T-046 | REQ-003-001-006 | Render fixed narration footer (always visible, not collapsible) | 4 | Pending |
| T-047 | REQ-003-001-007 | Add scenario selector dropdown within the simulation page | 4 | Pending |
| T-048 | REQ-003-001-008 | Update graph visualization in real-time from WebSocket events | 4 | Pending |
| T-049 | INT-001 | Implement REST call to POST /api/v1/simulation/start | 4 | Pending |
| T-050 | INT-002 | Implement REST call to POST /api/v1/simulation/pause | 4 | Pending |
| T-051 | INT-003 | Implement REST call to POST /api/v1/simulation/resume | 4 | Pending |
| T-052 | INT-004 | Implement REST call to POST /api/v1/simulation/speed | 4 | Pending |

#### Phase P5: Enhanced Features (NTH)

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-053 | REQ-001-001-006 | Implement collapse/expand toggle for entire control bar | 2 | Pending |
| T-054 | REQ-001-003-006 | Implement message type filter for narration panel | 2 | Pending |
| T-055 | REQ-002-002-006 | Support parallel analysis of multiple incidents | 3 | Pending |
| T-056 | TECH-006 | Implement keyboard shortcut handler (Space=Play/Pause, Esc=Stop) | 1 | Pending |

---

## Requirements Coverage Matrix

| Requirement ID | Task ID | Test IDs | Status |
|----------------|---------|----------|--------|
| REQ-001-001-001 | T-011 | UT-001, IT-001, E2E-001 | [ ] |
| REQ-001-001-002 | T-012 | UT-002, IT-001, E2E-001 | [ ] |
| REQ-001-001-003 | T-013 | UT-003, IT-001, E2E-001 | [ ] |
| REQ-001-001-004 | T-014 | UT-004, IT-001, E2E-001 | [ ] |
| REQ-001-001-005 | T-015 | UT-005, IT-001, E2E-001 | [ ] |
| REQ-001-001-006 | T-053 | UT-006, E2E-001 | [ ] |
| REQ-001-002-001 | T-016 | UT-007, IT-002, E2E-002 | [ ] |
| REQ-001-002-002 | T-017 | UT-008, IT-002, E2E-002 | [ ] |
| REQ-001-002-003 | T-018 | UT-009, IT-002, E2E-002 | [ ] |
| REQ-001-002-004 | T-019 | UT-010, IT-002, E2E-002 | [ ] |
| REQ-001-002-005 | T-020 | UT-011, IT-002, E2E-002 | [ ] |
| REQ-001-002-006 | T-021 | UT-012, IT-002, E2E-002 | [ ] |
| REQ-001-003-001 | T-022 | UT-013, IT-003, E2E-003 | [ ] |
| REQ-001-003-002 | T-023 | UT-014, IT-003, E2E-003 | [ ] |
| REQ-001-003-003 | T-024 | UT-015, IT-003, E2E-003 | [ ] |
| REQ-001-003-004 | T-025 | UT-016, IT-003, E2E-003 | [ ] |
| REQ-001-003-005 | T-026 | UT-017, IT-003, E2E-003 | [ ] |
| REQ-001-003-006 | T-054 | UT-018, E2E-003 | [ ] |
| REQ-002-001-001 | T-029 | UT-019, IT-004, E2E-004 | [ ] |
| REQ-002-001-002 | T-030 | UT-020, IT-004, E2E-004 | [ ] |
| REQ-002-001-003 | T-031 | UT-021, IT-004, E2E-004 | [ ] |
| REQ-002-001-004 | T-032 | UT-022, IT-004, E2E-004 | [ ] |
| REQ-002-001-005 | T-033 | UT-023, IT-004, E2E-004 | [ ] |
| REQ-002-001-006 | T-034 | UT-024, IT-004, E2E-004 | [ ] |
| REQ-002-002-001 | T-035 | UT-025, IT-005, E2E-005 | [ ] |
| REQ-002-002-002 | T-036 | UT-026, IT-005, E2E-005 | [ ] |
| REQ-002-002-003 | T-037 | UT-027, IT-005, E2E-005 | [ ] |
| REQ-002-002-004 | T-038 | UT-028, IT-005, E2E-005 | [ ] |
| REQ-002-002-005 | T-039 | UT-029, IT-005, E2E-005 | [ ] |
| REQ-002-002-006 | T-055 | UT-030, E2E-005 | [ ] |
| REQ-003-001-001 | T-041 | UT-031, IT-006, E2E-006 | [ ] |
| REQ-003-001-002 | T-042 | UT-032, IT-006, E2E-006 | [ ] |
| REQ-003-001-003 | T-043 | UT-033, IT-006, E2E-006 | [ ] |
| REQ-003-001-004 | T-044 | UT-034, IT-006, E2E-006 | [ ] |
| REQ-003-001-005 | T-045 | UT-035, IT-006, E2E-006 | [ ] |
| REQ-003-001-006 | T-046 | UT-036, IT-006, E2E-006 | [ ] |
| REQ-003-001-007 | T-047 | UT-037, IT-006, E2E-006 | [ ] |
| REQ-003-001-008 | T-048 | UT-038, IT-006, E2E-006 | [ ] |
| TECH-001 | T-001 | UT-TECH-001 | [ ] |
| TECH-002 | T-002 | UT-TECH-002 | [ ] |
| TECH-003 | T-003 | UT-TECH-003 | [ ] |
| TECH-004 | T-004 | UT-TECH-004 | [ ] |
| TECH-005 | T-005 | UT-TECH-005 | [ ] |
| TECH-006 | T-056 | UT-TECH-006 | [ ] |
| INT-001 | T-049 | IT-INT-001 | [ ] |
| INT-002 | T-050 | IT-INT-002 | [ ] |
| INT-003 | T-051 | IT-INT-003 | [ ] |
| INT-004 | T-052 | IT-INT-004 | [ ] |
| INT-005 | T-010 | IT-INT-005 | [ ] |
| INT-006 | T-040 | IT-INT-006 | [ ] |
| INT-007 | T-027 | IT-INT-007 | [ ] |
| INT-008 | T-028 | IT-INT-008 | [ ] |
| DATA-001 | T-006 | UT-DATA-001 | [ ] |
| DATA-002 | T-007 | UT-DATA-002 | [ ] |
| DATA-003 | T-008 | UT-DATA-003 | [ ] |
| DATA-004 | T-009 | UT-DATA-004 | [ ] |
| NFR-001 | N/A | N/A | Not implementable this phase |
| NFR-002 | N/A | N/A | Not implementable this phase |
| NFR-003 | N/A | N/A | Not implementable this phase |
| NFR-004 | N/A | N/A | Not implementable this phase |
| NFR-005 | N/A | N/A | Not implementable this phase |

---
_Document generated by SoftwareBuilderX v21.0.0_
