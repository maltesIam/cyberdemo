# Functional Specification: CyberDemo Interactive Frontend

| Attribute | Value |
|-----------|-------|
| Build ID | sbx-20260224-003500 |
| Created | 2026-02-24 |
| Source | docs/FRONTEND_DESCRIPTION.md |
| Template Version | SBX v21.0.0 |

---

# Part 1: Functional Description

## 1.1 Executive Summary

This specification defines the frontend components required to enable interactive demos for the CyberDemo SOC demonstration platform. The backend is fully built with REST APIs, WebSockets, and MCP Tools. The frontend needs 6 key components:

1. **Global Demo Control Bar** - Simulation controls in header across all pages
2. **aIP Assist Widget** - Floating AI assistant with proactive suggestions
3. **Narration Footer** - Real-time agent reasoning display
4. **Demo Cases Panel** - One-click SOC scenario execution (Cases 1/2/3)
5. **Analyze with AI Button** - Incident-specific AI analysis invocation
6. **Simulation Page** - Dedicated immersive demo experience at /simulation

**Scope**: Frontend components only (no new backend services).

## 1.2 System Overview

### 1.2.1 Purpose

Enable interactive demonstrations of CyberDemo's AI-driven SOC capabilities through frontend components that:
- Control attack simulations from any page
- Display agent reasoning in real-time
- Execute predefined demo scenarios with one click
- Invoke AI analysis on specific incidents
- Provide immersive experience for formal presentations

### 1.2.2 Scope

**In Scope:**
- F1: Global Demo Control Bar (header)
- F2: aIP Assist Floating Widget
- F3: Narration Footer Panel
- F4: Demo Cases 1/2/3 Panel (Dashboard)
- F5: "Analyze with AI" Button (Incidents)
- F6: Dedicated /simulation Page

**Out of Scope:**
- Backend APIs: POST /api/v1/simulation/start, /pause, /resume, /speed; POST /api/v1/analysis/queue (see INT-001 to INT-006)
- WebSocket endpoints: WS /api/v1/simulation/ws, /narration/ws, /aip-assist/ws (see INT-005 to INT-008)
- MCP Tools: agent_analyze_alert, simulation_start, aip_get_suggestion (see docs/FUNCTIONAL_SPEC.md)
- Attack scenarios: apt29, fin7, lazarus, revil, solarwinds, insider (backend demo/ folder)
- Existing 14 frontend views: Dashboard, Incidents, Detections, Assets, CTEM, Timeline, Alerts, Reports, Settings, Users, Integrations, Playbooks, Rules, Logs

### 1.2.3 Context

CyberDemo is a SOC demonstration platform with:
- 6 attack scenarios based on real APT groups (APT29, FIN7, Lazarus, REvil, SolarWinds, Insider)
- 3 demo SOC scenarios (auto-containment, VIP approval, false positive)
- AI agent for analysis and recommendations
- Real-time event streaming via WebSockets

## 1.3 User Roles and Personas

| User Role | Description | Primary Actions |
|-----------|-------------|-----------------|
| **SOC Analyst** | Security analyst using the platform | Investigate alerts, request AI analysis, approve/reject actions |
| **Demo Presenter** | Person demonstrating capabilities | Control speed, pause, select scenarios, execute cases 1/2/3 |
| **Security Manager** | Supervisor reviewing decisions | View agent narratives, approve VIP containments |

### Persona: Alex (SOC Analyst)
- 3 years SOC experience
- Wants quick triage with AI assistance
- Needs clear reasoning from AI decisions

### Persona: Maria (Demo Presenter)
- Sales engineer conducting demos
- Needs precise control over demo flow
- Wants impressive visuals for formal presentations

### Persona: Carlos (Security Manager)
- 10 years security leadership
- Reviews AI decisions for VIP assets
- Needs audit trail of AI reasoning

## 1.4 Functional Areas

### FA-001: Global Demo Controls

**US-001**: As a Demo Presenter, I want to control simulations from any page so that I can demonstrate without navigating away.

**Acceptance Criteria:**
- AC-001-01: Control bar visible in header on all pages
- AC-001-02: Can select from 6 attack scenarios via dropdown
- AC-001-03: Play/Pause/Stop buttons control simulation
- AC-001-04: Speed slider adjusts from 0.5x to 4x
- AC-001-05: MITRE progress shows colored circles per phase
- AC-001-06: Can collapse/expand the entire bar

**Business Rules:**
- BR-001-01: Only one scenario can run at a time
- BR-001-02: Pause stops event generation but maintains state
- BR-001-03: Stop resets all simulation state
- BR-001-04: MITRE progress reflects current attack phase

### FA-002: aIP Assist Widget

**US-002**: As a SOC Analyst, I want proactive AI suggestions so that I can respond faster to threats.

**Acceptance Criteria:**
- AC-002-01: Floating widget in bottom-right corner of all pages
- AC-002-02: Collapsed state shows circular button with notification badge
- AC-002-03: Expanded state shows panel with AI suggestions
- AC-002-04: Each suggestion has Analyze/Ignore/Details buttons
- AC-002-05: "Thinking" indicator when AI is processing
- AC-002-06: Badge shows count of unread suggestions

**Business Rules:**
- BR-002-01: Suggestions generate automatically based on activity
- BR-002-02: Badge shows unread suggestion count
- BR-002-03: Accepting suggestion may trigger automatic actions
- BR-002-04: Ignoring saves to history but dismisses from view

### FA-003: Narration Footer

**US-003**: As a Demo Presenter, I want to see AI reasoning in real-time so that I can explain decisions to the audience.

**Acceptance Criteria:**
- AC-003-01: Footer panel present on all pages
- AC-003-02: Shows streaming text with timestamps (terminal style)
- AC-003-03: Colors by type: info=white, warning=yellow, error=red, success=green
- AC-003-04: Expand/collapse button toggles visibility
- AC-003-05: Auto-scrolls to most recent message
- AC-003-06: Can filter messages by type

**Business Rules:**
- BR-003-01: Narration continues even when panel is collapsed
- BR-003-02: Messages accumulate throughout session
- BR-003-03: Filter options: All, Info, Warning, Error, Success

### FA-004: Demo Cases Panel

**US-004**: As a Demo Presenter, I want to execute predefined demo scenarios with one click so that I can demonstrate key capabilities quickly.

**Acceptance Criteria:**
- AC-004-01: Panel visible on Dashboard page
- AC-004-02: Three cards/buttons for Cases 1, 2, 3
- AC-004-03: Each card shows: name, host, type, expected result
- AC-004-04: Click invokes agent and shows process
- AC-004-05: Visual feedback during execution (loading state)
- AC-004-06: Final result matches expected outcome

**Demo Case Specifications:**

| Case ID | Target Host | Scenario | Expected Result |
|---------|-------------|----------|-----------------|
| CASE-001 | WS-FIN-042 | Malware on standard workstation | Auto-containment |
| CASE-002 | LAPTOP-CFO-01 | Malware on VIP laptop | Approval required |
| CASE-003 | SRV-DEV-03 | Suspicious activity on dev server | False positive |

**Business Rules:**
- BR-004-01: Only one case can execute at a time
- BR-004-02: Results must be deterministic (always match expected)
- BR-004-03: Narration must show full analysis process
- BR-004-04: Case 2 must display approval card for human decision

### FA-005: Analyze with AI Button

**US-005**: As a SOC Analyst, I want to request AI analysis on specific incidents so that I can get detailed recommendations.

**Acceptance Criteria:**
- AC-005-01: Button appears in each row of Incidents table
- AC-005-02: Initial state: "Analyze with AI" with robot icon
- AC-005-03: Processing state: "Analyzing..." (disabled)
- AC-005-04: Completed state: Shows decision icon (contained/pending/dismissed)
- AC-005-05: Click auto-expands narration panel
- AC-005-06: Analysis runs asynchronously

**Business Rules:**
- BR-005-01: Analysis queued and processed asynchronously
- BR-005-02: Progress visible via narration in real-time
- BR-005-03: Result persisted in incident record
- BR-005-04: Multiple incidents can analyze in parallel

### FA-006: Simulation Page

**US-006**: As a Demo Presenter, I want a dedicated simulation page so that I can give immersive presentations.

**Acceptance Criteria:**
- AC-006-01: Page accessible at /simulation route
- AC-006-02: Three-column layout: MITRE Phases | Visualization | aIP Panel
- AC-006-03: Left column: Vertical list of scenario phases with status indicators
- AC-006-04: Center column: Interactive attack graph (nodes=hosts/IOCs, edges=propagation)
- AC-006-05: Right column: aIP panel (integrated, not floating)
- AC-006-06: Footer: Narration always visible (not collapsible)
- AC-006-07: Scenario selector within the page
- AC-006-08: Real-time visualization updates from events

**Business Rules:**
- BR-006-01: Page is independent of global controls
- BR-006-02: Scenario selected within the page, not from global bar
- BR-006-03: Visualization updates in real-time from WebSocket events
- BR-006-04: Phase indicators: completed=green, active=yellow pulsing, pending=gray

## 1.5 Non-Functional Requirements Summary

| Category | Requirement |
|----------|-------------|
| Performance | UI updates within 100ms of WebSocket event, smooth 60fps animations, WebSocket reconnection within 3 seconds |
| Usability | Keyboard shortcuts Space=Play/Pause Esc=Stop, all controls accessible without mouse, ARIA labels on interactive elements |
| Availability | Graceful degradation when WebSocket disconnects, error messages for failed API calls, reconnection handling |
| Scalability | Support 1000+ narration messages without performance degradation, virtualized lists, lazy loading components |
| Security | No sensitive data in localStorage, XSS prevention in narration content display, input sanitization |

## 1.6 Assumptions and Dependencies

### Assumptions
- A1: Backend APIs are functional and stable
- A2: WebSocket connections are reliable
- A3: MCP Tools execute correctly
- A4: React 18+ is available in the project
- A5: Tailwind CSS is configured
- A6: Cytoscape.js is installed for graph visualization

### Dependencies
- D1: Backend REST APIs (listed in section 2.6)
- D2: WebSocket endpoints (listed in section 2.6)
- D3: React Context for state management
- D4: Existing component library

## 1.7 Constraints

- C1: Frontend only - no new backend services
- C2: Reuse existing base components (DemoControlPanel, AipAssistWidget, NarrationPanel)
- C3: Business logic remains in backend
- C4: Follow existing design system (colors, typography, spacing)

## 1.8 Project Context

### Existing Codebase
- **Framework**: React 18+ with TypeScript
- **State**: React Context + custom hooks
- **Styling**: Tailwind CSS
- **Routing**: React Router
- **Graphs**: Cytoscape.js

### Existing Components (to integrate)
- `DemoControlPanel` - Base control component
- `AipAssistWidget` - Base AI widget
- `NarrationPanel` - Base narration component

### Existing Views (14 total)
Dashboard, Incidents, Detections, Assets, CTEM, Timeline, Alerts, Reports, Settings, Users, Integrations, Playbooks, Rules, Logs

### Backend APIs Available
- POST /api/v1/analysis/queue - Queue AI analysis
- GET /api/v1/analysis/status/{id} - Analysis status
- WS /api/v1/analysis/ws - Analysis updates
- WS /api/v1/narration/ws/{session} - Narration stream
- WS /api/v1/aip-assist/ws/{session} - AI suggestions

---

# Part 2: Technical Requirements

## 2.1 Requirements Traceability Matrix (Brief)

| Source | Requirement Type | Count |
|--------|-----------------|-------|
| US-001 | REQ-001-xxx | 6 |
| US-002 | REQ-002-xxx | 6 |
| US-003 | REQ-003-xxx | 6 |
| US-004 | REQ-004-xxx | 6 |
| US-005 | REQ-005-xxx | 6 |
| US-006 | REQ-006-xxx | 8 |
| Technical | TECH-xxx | 6 |
| Integration | INT-xxx | 8 |
| Data | DATA-xxx | 4 |
| NFR | NFR-xxx | 5 |
| **Total** | All Types | **61** |

## 2.2 Requirements Numbering Convention

| Type | Format | Example |
|------|--------|---------|
| Epic | EPIC-XXX | EPIC-001 |
| Feature | FEAT-XXX-YYY | FEAT-001-001 |
| Requirement | REQ-XXX-YYY-ZZZ | REQ-001-001-001 |
| Technical | TECH-XXX | TECH-001 |
| Integration | INT-XXX | INT-001 |
| Data | DATA-XXX | DATA-001 |
| Non-Functional | NFR-XXX | NFR-001 |

## 2.3 Priority Classification

| Priority | Code | Description |
|----------|------|-------------|
| Must-To-Have | MTH | Required for demo functionality |
| Nice-To-Have | NTH | Enhances but not critical |

## 2.4 Epics and Features

### EPIC-001: Global Demo Infrastructure [MTH]

Components that appear on all pages to enable demo control.

#### FEAT-001-001: Demo Control Bar [MTH]

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-001-001 | Render control bar in header on all pages | MTH | AC-001-01 |
| REQ-001-001-002 | Implement scenario dropdown with 6 options | MTH | AC-001-02 |
| REQ-001-001-003 | Implement Play/Pause/Stop buttons | MTH | AC-001-03 |
| REQ-001-001-004 | Implement speed slider (0.5x-4x) | MTH | AC-001-04 |
| REQ-001-001-005 | Display MITRE phase progress circles | MTH | AC-001-05 |
| REQ-001-001-006 | Implement collapse/expand toggle | NTH | AC-001-06 |

#### FEAT-001-002: aIP Assist Widget [MTH]

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-002-001 | Position floating widget bottom-right all pages | MTH | AC-002-01 |
| REQ-001-002-002 | Implement collapsed state with badge | MTH | AC-002-02 |
| REQ-001-002-003 | Implement expanded panel with suggestions | MTH | AC-002-03 |
| REQ-001-002-004 | Add action buttons per suggestion | MTH | AC-002-04 |
| REQ-001-002-005 | Show thinking indicator during processing | MTH | AC-002-05 |
| REQ-001-002-006 | Update badge count for unread items | MTH | AC-002-06 |

#### FEAT-001-003: Narration Footer [MTH]

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-003-001 | Render footer panel on all pages | MTH | AC-003-01 |
| REQ-001-003-002 | Display streaming messages with timestamps | MTH | AC-003-02 |
| REQ-001-003-003 | Apply color coding by message type | MTH | AC-003-03 |
| REQ-001-003-004 | Implement expand/collapse toggle | MTH | AC-003-04 |
| REQ-001-003-005 | Auto-scroll to latest message | MTH | AC-003-05 |
| REQ-001-003-006 | Implement message type filter | NTH | AC-003-06 |

### EPIC-002: Demo Scenario Execution [MTH]

Components for executing and viewing demo scenarios.

#### FEAT-002-001: Demo Cases Panel [MTH]

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-002-001-001 | Render panel on Dashboard page | MTH | AC-004-01 |
| REQ-002-001-002 | Display 3 case cards with metadata | MTH | AC-004-02, AC-004-03 |
| REQ-002-001-003 | Invoke agent on card click | MTH | AC-004-04 |
| REQ-002-001-004 | Show loading state during execution | MTH | AC-004-05 |
| REQ-002-001-005 | Display deterministic result | MTH | AC-004-06 |
| REQ-002-001-006 | Render approval card for Case 2 | MTH | BR-004-04 |

#### FEAT-002-002: Incident AI Analysis [MTH]

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-002-002-001 | Add button to each Incidents table row | MTH | AC-005-01 |
| REQ-002-002-002 | Implement 3-state button (initial/processing/done) | MTH | AC-005-02, AC-005-03, AC-005-04 |
| REQ-002-002-003 | Auto-expand narration on click | MTH | AC-005-05 |
| REQ-002-002-004 | Queue analysis asynchronously | MTH | AC-005-06 |
| REQ-002-002-005 | Persist result to incident | MTH | BR-005-03 |
| REQ-002-002-006 | Support parallel analysis | NTH | BR-005-04 |

### EPIC-003: Immersive Simulation Experience [MTH]

Dedicated page for formal presentations.

#### FEAT-003-001: Simulation Page Layout [MTH]

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-003-001-001 | Create /simulation route | MTH | AC-006-01 |
| REQ-003-001-002 | Implement 3-column layout | MTH | AC-006-02 |
| REQ-003-001-003 | Render MITRE phases in left column | MTH | AC-006-03 |
| REQ-003-001-004 | Render attack graph in center column | MTH | AC-006-04 |
| REQ-003-001-005 | Render integrated aIP panel in right column | MTH | AC-006-05 |
| REQ-003-001-006 | Render fixed narration footer | MTH | AC-006-06 |
| REQ-003-001-007 | Add scenario selector to page | MTH | AC-006-07 |
| REQ-003-001-008 | Update visualization from WebSocket events | MTH | AC-006-08 |

## 2.5 Technical Requirements

| Req ID | Description | Priority | Rationale |
|--------|-------------|----------|-----------|
| TECH-001 | Create DemoContext provider for global state | MTH | Shared state across components |
| TECH-002 | Implement useSimulation hook for API calls | MTH | Encapsulate simulation logic |
| TECH-003 | Implement useNarration hook for WebSocket | MTH | Manage narration stream |
| TECH-004 | Implement useAipAssist hook for suggestions | MTH | Manage AI suggestions |
| TECH-005 | Create graph adapter for Cytoscape.js | MTH | Standard interface for visualization |
| TECH-006 | Implement keyboard shortcut handler | NTH | Space/Esc shortcuts |

## 2.6 Integration Requirements

| Req ID | Endpoint | Type | Description | Priority |
|--------|----------|------|-------------|----------|
| INT-001 | POST /api/v1/simulation/start | REST | Start simulation | MTH |
| INT-002 | POST /api/v1/simulation/pause | REST | Pause simulation | MTH |
| INT-003 | POST /api/v1/simulation/resume | REST | Resume simulation | MTH |
| INT-004 | POST /api/v1/simulation/speed | REST | Set speed | MTH |
| INT-005 | WS /api/v1/simulation/ws | WebSocket | Simulation events | MTH |
| INT-006 | POST /api/v1/analysis/queue | REST | Queue AI analysis | MTH |
| INT-007 | WS /api/v1/narration/ws/{session} | WebSocket | Narration stream | MTH |
| INT-008 | WS /api/v1/aip-assist/ws/{session} | WebSocket | AI suggestions | MTH |

## 2.7 Data Requirements

| Req ID | Source | Description | Priority |
|--------|--------|-------------|----------|
| DATA-001 | US-001 | Store simulation state (scenario, phase, speed, running) in React Context | MTH |
| DATA-002 | US-003 | Store narration messages (timestamp, type, content) with max 1000 entries | MTH |
| DATA-003 | US-002 | Store AI suggestions (id, content, status, actions) with read/unread tracking | MTH |
| DATA-004 | US-005 | Store incident analysis results (id, decision, timestamp) per incident | MTH |

## 2.8 Full Traceability Matrix

| Req ID | Source | Description | Priority | Code | Tests | Verified |
|--------|--------|-------------|----------|------|-------|----------|
| REQ-001-001-001 | US-001 | Render control bar in header | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-002 | US-001 | Scenario dropdown with 6 options | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-003 | US-001 | Play/Pause/Stop buttons | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-004 | US-001 | Speed slider 0.5x-4x | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-005 | US-001 | MITRE phase progress circles | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-006 | US-001 | Collapse/expand toggle | NTH | [ ] | [ ] | [ ] |
| REQ-001-002-001 | US-002 | Floating widget bottom-right | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-002 | US-002 | Collapsed state with badge | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-003 | US-002 | Expanded panel with suggestions | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-004 | US-002 | Action buttons per suggestion | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-005 | US-002 | Thinking indicator | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-006 | US-002 | Badge count for unread | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-001 | US-003 | Footer panel on all pages | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-002 | US-003 | Streaming messages with timestamps | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-003 | US-003 | Color coding by type | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-004 | US-003 | Expand/collapse toggle | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-005 | US-003 | Auto-scroll to latest | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-006 | US-003 | Message type filter | NTH | [ ] | [ ] | [ ] |
| REQ-002-001-001 | US-004 | Panel on Dashboard | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-002 | US-004 | 3 case cards with metadata | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-003 | US-004 | Invoke agent on click | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-004 | US-004 | Loading state during execution | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-005 | US-004 | Deterministic result display | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-006 | US-004 | Approval card for Case 2 | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-001 | US-005 | Button in Incidents table row | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-002 | US-005 | 3-state button | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-003 | US-005 | Auto-expand narration | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-004 | US-005 | Async analysis queue | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-005 | US-005 | Persist result to incident | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-006 | US-005 | Parallel analysis support | NTH | [ ] | [ ] | [ ] |
| REQ-003-001-001 | US-006 | /simulation route | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-002 | US-006 | 3-column layout | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-003 | US-006 | MITRE phases left column | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-004 | US-006 | Attack graph center column | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-005 | US-006 | aIP panel right column | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-006 | US-006 | Fixed narration footer | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-007 | US-006 | Scenario selector in page | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-008 | US-006 | Real-time visualization | MTH | [ ] | [ ] | [ ] |
| TECH-001 | Architecture | DemoContext provider for global state | MTH | [ ] | [ ] | [ ] |
| TECH-002 | Architecture | useSimulation hook for API calls | MTH | [ ] | [ ] | [ ] |
| TECH-003 | Architecture | useNarration hook for WebSocket | MTH | [ ] | [ ] | [ ] |
| TECH-004 | Architecture | useAipAssist hook for suggestions | MTH | [ ] | [ ] | [ ] |
| TECH-005 | Architecture | Cytoscape.js adapter for graphs | MTH | [ ] | [ ] | [ ] |
| TECH-006 | Architecture | Keyboard shortcut handler | NTH | [ ] | [ ] | [ ] |
| INT-001 | Backend API | POST /simulation/start | MTH | [ ] | [ ] | [ ] |
| INT-002 | Backend API | POST /simulation/pause | MTH | [ ] | [ ] | [ ] |
| INT-003 | Backend API | POST /simulation/resume | MTH | [ ] | [ ] | [ ] |
| INT-004 | Backend API | POST /simulation/speed | MTH | [ ] | [ ] | [ ] |
| INT-005 | Backend API | WS /simulation/ws | MTH | [ ] | [ ] | [ ] |
| INT-006 | Backend API | POST /analysis/queue | MTH | [ ] | [ ] | [ ] |
| INT-007 | Backend API | WS /narration/ws | MTH | [ ] | [ ] | [ ] |
| INT-008 | Backend API | WS /aip-assist/ws | MTH | [ ] | [ ] | [ ] |
| DATA-001 | US-001 | Simulation state storage | MTH | [ ] | [ ] | [ ] |
| DATA-002 | US-003 | Narration messages storage | MTH | [ ] | [ ] | [ ] |
| DATA-003 | US-002 | AI suggestions storage | MTH | [ ] | [ ] | [ ] |
| DATA-004 | US-005 | Analysis results storage | MTH | [ ] | [ ] | [ ] |
| NFR-001 | Performance | UI updates within 100ms | MTH | [ ] | [ ] | [ ] |
| NFR-002 | Usability | Keyboard shortcuts Space/Esc | NTH | [ ] | [ ] | [ ] |
| NFR-003 | Availability | WebSocket disconnect handling | MTH | [ ] | [ ] | [ ] |
| NFR-004 | Scalability | 1000+ messages support | MTH | [ ] | [ ] | [ ] |
| NFR-005 | Security | XSS prevention in narration | MTH | [ ] | [ ] | [ ] |

---

## Verification Section

### Part 1 to Part 2 Traceability

| Part 1 Element | Part 2 Coverage |
|----------------|-----------------|
| US-001 (Global Controls) | REQ-001-001-001 to REQ-001-001-006 |
| US-002 (aIP Assist) | REQ-001-002-001 to REQ-001-002-006 |
| US-003 (Narration) | REQ-001-003-001 to REQ-001-003-006 |
| US-004 (Demo Cases) | REQ-002-001-001 to REQ-002-001-006 |
| US-005 (AI Analysis) | REQ-002-002-001 to REQ-002-002-006 |
| US-006 (Simulation) | REQ-003-001-001 to REQ-003-001-008 |
| NFR-001 to NFR-005 | NFR-001 to NFR-005 |
| BR-xxx | Covered in respective REQ-xxx |
| AC-xxx | Mapped in REQ-xxx rows |

### Summary Statistics

| Category | Count |
|----------|-------|
| User Stories | 6 |
| Business Rules | 16 |
| Acceptance Criteria | 30 |
| Epics | 3 |
| Features | 6 |
| Functional Requirements (REQ) | 38 |
| Technical Requirements (TECH) | 6 |
| Integration Requirements (INT) | 8 |
| Data Requirements (DATA) | 4 |
| Non-Functional Requirements (NFR) | 5 |
| **Total Requirements** | **61** |
| MTH Requirements | 56 |
| NTH Requirements | 5 |

---

_Document generated by SoftwareBuilderX v21.0.0_
