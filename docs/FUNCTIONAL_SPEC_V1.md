# Functional Specification: CyberDemo Interactive Frontend

| Attribute | Value |
|-----------|-------|
| Version | 1.0.0 |
| Date | 2026-02-23 |
| Build ID | sbx-20260223-203537 |
| Status | Draft |

---

# PART 1: FUNCTIONAL DESCRIPTION
*For business stakeholders and non-technical readers*

## 1.1 Executive Summary

CyberDemo Interactive Frontend is a set of React components that enhance the existing CyberDemo SOC platform with interactive demo capabilities. The system enables presenters to showcase AI-powered security operations through attack simulations, real-time agent reasoning visualization, and predefined demo scenarios.

The frontend integrates with an already-complete backend that provides REST APIs, WebSockets, and MCP Tools for agent orchestration. This project focuses exclusively on building the missing UI components to create an immersive demo experience.

Key deliverables include: global demo controls visible on all pages, a floating AI assistant widget, a narration panel showing agent reasoning in real-time, demo scenario buttons, an "Analyze with AI" feature for incidents, and a dedicated simulation page for formal presentations.

## 1.2 System Overview

### 1.2.1 Purpose

Enable CyberDemo platform users to:
1. Control attack simulations from any page in the application
2. Observe AI agent reasoning in real-time through streaming narration
3. Execute predefined SOC demo scenarios with deterministic outcomes
4. Request AI analysis on specific security incidents
5. Deliver immersive security demos during formal presentations

### 1.2.2 Scope

**In Scope:**
- Global demo control bar integrated in all pages header
- Floating aIP Assist widget with proactive suggestions
- Collapsible narration footer with agent reasoning stream
- Demo Cases 1/2/3 panel on Dashboard page
- "Analyze with AI" button on Incidents table
- Dedicated /simulation page with 3-column layout
- React Context for global state management
- WebSocket integration for real-time updates
- Keyboard shortcuts for demo control

**Out of Scope:**
- Backend API development (already built)
- WebSocket server implementation (already built)
- MCP Tools development (already built)
- Attack scenario definitions (already built)
- Existing frontend views modification (Dashboard, Incidents, etc.)
- Authentication and authorization systems
- Mobile responsive design (desktop only, 1280px+)

### 1.2.3 Context Diagram

```
                    ┌─────────────────────────┐
                    │     Demo Presenter      │
                    │     SOC Analyst         │
                    │     Security Manager    │
                    └───────────┬─────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                  CyberDemo Interactive Frontend               │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────────────┐│
│  │ Demo Control│ │ aIP Assist  │ │    Narration Panel       ││
│  │    Bar      │ │   Widget    │ │                          ││
│  └─────────────┘ └─────────────┘ └──────────────────────────┘│
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────────────┐│
│  │Demo Cases   │ │ AI Analyze  │ │   Simulation Page        ││
│  │   Panel     │ │   Button    │ │                          ││
│  └─────────────┘ └─────────────┘ └──────────────────────────┘│
└───────────────────────────────────────────────────────────────┘
                                │
                    REST APIs   │   WebSockets
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                    CyberDemo Backend                          │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────────────┐│
│  │ Analysis    │ │ Simulation  │ │    Narration             ││
│  │    API      │ │    API      │ │    WebSocket             ││
│  └─────────────┘ └─────────────┘ └──────────────────────────┘│
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────────────┐│
│  │ Demo        │ │ aIP Assist  │ │    MCP Tools             ││
│  │ Scenarios   │ │    API      │ │    (Agent)               ││
│  └─────────────┘ └─────────────┘ └──────────────────────────┘│
└───────────────────────────────────────────────────────────────┘
```

## 1.3 User Roles and Personas

| Role ID | Role Name | Description | Primary Goals |
|---------|-----------|-------------|---------------|
| USR-001 | SOC Analyst | Security operations analyst using the platform daily | Investigate alerts, request AI analysis on incidents, approve/reject containment actions |
| USR-002 | Demo Presenter | Person showcasing CyberDemo capabilities to prospects | Control simulation speed, pause at key moments, execute demo cases, deliver compelling presentations |
| USR-003 | Security Manager | Supervisor reviewing agent decisions | View agent reasoning narratives, approve VIP asset containment, audit AI decisions |

## 1.4 Functional Areas

### 1.4.1 Demo Control System

**Description**: A global control system that allows users to manage attack simulations from any page in the application. The control bar appears in the header and provides playback controls, scenario selection, and MITRE phase progress visualization.

**User Stories**:
- US-001: As a Demo Presenter, I want to select an attack scenario from a dropdown so that I can demonstrate different APT group behaviors
- US-002: As a Demo Presenter, I want to play/pause/stop the simulation so that I can control the demo flow
- US-003: As a Demo Presenter, I want to adjust simulation speed (0.5x-4x) so that I can speed through or slow down key moments
- US-004: As a SOC Analyst, I want to see MITRE phase progress visually so that I can understand where the attack is in its lifecycle
- US-005: As a Demo Presenter, I want to hide/show the control bar so that I can focus on specific content when needed

**Business Rules**:
- BR-001: Only one scenario can execute at a time
- BR-002: Pause stops event generation but maintains current state
- BR-003: Stop resets all simulation state to initial
- BR-004: MITRE progress must reflect current attack phase accurately
- BR-005: Control bar must be visible on all pages except /simulation

**Workflows**:
1. User opens any page in the application
2. Demo control bar is visible in header
3. User selects scenario from dropdown (6 options)
4. User clicks Play to start simulation
5. Events stream via WebSocket
6. MITRE progress updates in real-time
7. User can Pause/Resume at any time
8. User clicks Stop to reset

### 1.4.2 AI Assistant Widget (aIP Assist)

**Description**: A floating widget in the bottom-right corner of all pages that displays proactive suggestions from the AI agent. The widget can be expanded or collapsed and shows a notification badge for unread suggestions.

**User Stories**:
- US-006: As a SOC Analyst, I want to see AI suggestions without requesting them so that I can be proactively informed
- US-007: As a SOC Analyst, I want to expand/collapse the assistant panel so that I can focus on my work
- US-008: As a SOC Analyst, I want to see how many unread suggestions exist so that I can prioritize reviewing them
- US-009: As a SOC Analyst, I want to accept or ignore suggestions so that I can act on relevant insights
- US-010: As a Security Manager, I want to see a "thinking" indicator so that I know when the agent is processing

**Business Rules**:
- BR-006: Suggestions generate automatically based on platform activity
- BR-007: Badge shows count of unread suggestions
- BR-008: Accepting a suggestion may trigger automatic actions
- BR-009: Ignoring a suggestion saves it to history for audit
- BR-010: Widget must be visible on all pages

**Workflows**:
1. Agent detects relevant activity via WebSocket
2. Suggestion appears in widget
3. Badge count increments
4. User clicks to expand widget
5. User reviews suggestion content
6. User clicks Accept (triggers action) or Ignore (archives)
7. Badge count decrements

### 1.4.3 Narration System

**Description**: A footer panel that displays the AI agent's reasoning in real-time as streaming text. The panel shows timestamped messages with color coding and can be expanded or collapsed while continuing to receive messages.

**User Stories**:
- US-011: As a Demo Presenter, I want to see agent reasoning in real-time so that I can explain AI decisions to the audience
- US-012: As a SOC Analyst, I want messages color-coded by type so that I can quickly identify warnings and errors
- US-013: As a Demo Presenter, I want the panel to auto-scroll so that I always see the latest message
- US-014: As a SOC Analyst, I want to expand/collapse the panel so that I can manage screen real estate
- US-015: As a Security Manager, I want to filter messages by type so that I can focus on specific categories

**Business Rules**:
- BR-011: Narration continues streaming even when panel is collapsed
- BR-012: Messages accumulate during entire session
- BR-013: Color coding: info=white, warning=yellow, error=red, success=green
- BR-014: Timestamps shown for each message
- BR-015: Panel collapsible on all pages except /simulation

**Workflows**:
1. User performs action that triggers agent analysis
2. Agent reasoning streams via WebSocket
3. Messages appear in footer panel with timestamps
4. Panel auto-scrolls to latest message
5. User can collapse panel (streaming continues)
6. User can expand to view accumulated messages
7. User can filter by message type

### 1.4.4 Demo Scenarios Panel

**Description**: A panel on the Dashboard page displaying three predefined SOC demo scenarios. Each scenario is a card that, when clicked, executes a deterministic demo showing the AI agent's decision-making process.

**User Stories**:
- US-016: As a Demo Presenter, I want to execute Demo Case 1 (Auto-Containment) so that I can show autonomous response
- US-017: As a Demo Presenter, I want to execute Demo Case 2 (VIP Approval) so that I can show human-in-the-loop workflow
- US-018: As a Demo Presenter, I want to execute Demo Case 3 (False Positive) so that I can show intelligent triage
- US-019: As a Demo Presenter, I want to see expected outcome on each card so that I know what to expect
- US-020: As a Demo Presenter, I want to see execution status so that I know when the demo is complete

**Business Rules**:
- BR-016: Only one demo case can execute at a time
- BR-017: Demo outcomes are deterministic (same input = same result)
- BR-018: Narration panel shows complete analysis process
- BR-019: Case 1 (WS-FIN-042): Auto-containment, no human intervention
- BR-020: Case 2 (LAPTOP-CFO-01): VIP detected, requires approval
- BR-021: Case 3 (SRV-DEV-03): False positive, alert dismissed

**Workflows**:
1. User navigates to Dashboard
2. Demo Cases panel shows 3 cards
3. User clicks a case card
4. API triggers demo scenario
5. Agent processes and narrates reasoning
6. For Case 2: Approval card appears, user must approve/reject
7. Demo completes with deterministic outcome
8. Status shows "Complete" on card

### 1.4.5 AI Analysis Feature

**Description**: A button on each row of the Incidents table that allows users to request AI analysis for specific incidents. The analysis runs asynchronously and results are streamed through the narration panel.

**User Stories**:
- US-021: As a SOC Analyst, I want to analyze a specific incident with AI so that I get expert recommendations
- US-022: As a SOC Analyst, I want to see analysis progress so that I know it's working
- US-023: As a SOC Analyst, I want the narration panel to open automatically so that I can follow the reasoning
- US-024: As a SOC Analyst, I want to see the final decision on the button so that I know the outcome
- US-025: As a SOC Analyst, I want to analyze multiple incidents in parallel so that I can work efficiently

**Business Rules**:
- BR-022: Analysis queues asynchronously via API
- BR-023: Progress visible in real-time via narration
- BR-024: Result persisted on incident record
- BR-025: Multiple parallel analyses supported
- BR-026: Button states: Initial -> Processing -> Complete (with decision)

**Workflows**:
1. User views Incidents table
2. User clicks "Analyze with AI" on a row
3. Button changes to "Analyzing..."
4. Narration panel expands automatically
5. Agent reasoning streams in real-time
6. Analysis completes
7. Button shows decision icon (contained/pending/dismissed)
8. Result saved to incident

### 1.4.6 Simulation Page

**Description**: A dedicated full-page experience for formal demos with a 3-column layout showing MITRE phases, attack graph visualization, and AI analysis panel. The narration footer is always visible.

**User Stories**:
- US-026: As a Demo Presenter, I want a full-page simulation view so that I can deliver immersive presentations
- US-027: As a Demo Presenter, I want to see MITRE phases with status indicators so that I can track attack progression
- US-028: As a Demo Presenter, I want to see an interactive attack graph so that I can visualize the attack in real-time
- US-029: As a Demo Presenter, I want to click on a phase to see technique details so that I can explain specific attack methods
- US-030: As a Demo Presenter, I want the narration always visible so that I can narrate along with the agent

**Business Rules**:
- BR-027: Page is independent of global controls (has its own)
- BR-028: Scenario selected within the page
- BR-029: Visualization updates in real-time based on simulation events
- BR-030: MITRE indicators: completed=green, active=yellow pulsing, pending=gray
- BR-031: Narration footer is not collapsible on this page

**Workflows**:
1. User navigates to /simulation
2. 3-column layout displays
3. User selects scenario from page selector
4. User starts simulation
5. Left column: MITRE phases update status
6. Center column: Attack graph animates
7. Right column: AI analysis appears
8. Bottom: Narration streams continuously
9. User can click phases for details
10. Simulation completes

## 1.5 Non-Functional Requirements Summary

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | UI updates < 100ms from WebSocket event receipt |
| NFR-002 | Performance | Page load time < 2 seconds on standard connection |
| NFR-003 | Availability | Components must gracefully handle WebSocket disconnection and auto-reconnect |
| NFR-004 | Security | No sensitive data stored in frontend state |
| NFR-005 | Scalability | Support concurrent users viewing same simulation |
| NFR-006 | Usability | Keyboard shortcuts: Space=Play/Pause, Esc=Stop, Arrow keys for speed |
| NFR-007 | Usability | Minimum supported width 1280px desktop only |
| NFR-008 | Security | Support Chrome, Firefox, Edge (last 2 versions) |
| NFR-009 | Usability | ARIA labels on all interactive elements |
| NFR-010 | Usability | Full keyboard navigation for all controls |

## 1.6 Assumptions and Dependencies

### Assumptions
- Backend APIs are fully operational and documented
- WebSocket connections are stable and low-latency
- Existing React component library follows consistent patterns
- Users have modern browsers (Chrome, Firefox, Edge - last 2 versions)
- Screen resolution minimum 1280px width

### Dependencies
- React 18+ (already in use)
- React Context API for global state
- Tailwind CSS for styling
- Cytoscape.js for graph visualization
- Native WebSocket API
- Existing component library (DemoControlPanel, AipAssistWidget, NarrationPanel)

## 1.7 Constraints

- **Frontend Only**: No new backend services except REST wrappers over existing MCP Tools
- **Reuse Components**: Must use existing base components where available
- **No Logic Duplication**: Business logic stays in backend, frontend only presents
- **Style Consistency**: Must follow existing design system (colors, typography, spacing)
- **Desktop Only**: No mobile responsive requirements

## 1.8 Project Context

This project extends an existing CyberDemo platform. The backend is complete with:
- 40+ REST API endpoints
- 4 WebSocket endpoints for real-time updates
- 15+ MCP Tools for agent orchestration
- 6 APT attack scenarios
- 3 SOC demo scenarios

The current frontend has 14 operational views but lacks the interactive demo components that this specification addresses.

---

# PART 2: TECHNICAL REQUIREMENTS
*Traceable requirements for development*

## 2.1 Requirements Traceability Matrix

This document traces all requirements from user stories and business rules in Part 1 to technical specifications in Part 2. Full traceability matrix provided in Section 2.8.

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
| Must-To-Have | MTH | Critical for MVP, cannot launch without |
| Nice-To-Have | NTH | Desired but not blocking launch |

## 2.4 Epics

### EPIC-001: Global Demo Controls `MTH`

**ID**: EPIC-001
**Priority**: MTH
**Description**: Implement global demo control components that appear on all pages, enabling simulation control, AI assistant access, and narration viewing from anywhere in the application.
**Business Value**: Enables seamless demo experience without page navigation
**Traces To**: Section 1.4.1, 1.4.2, 1.4.3

**Acceptance Criteria**:
- [ ] AC-001: Demo control bar visible in header on all pages
- [ ] AC-002: aIP Assist widget visible on all pages
- [ ] AC-003: Narration footer visible on all pages
- [ ] AC-004: Global state shared via React Context

#### Features

##### FEAT-001-001: Demo Control Bar `MTH`

**ID**: FEAT-001-001
**Priority**: MTH
**Description**: Header component with simulation playback controls, scenario selector, speed control, and MITRE progress display.
**Traces To**: US-001, US-002, US-003, US-004, US-005, BR-001, BR-002, BR-003, BR-004, BR-005

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-001-001 | Scenario dropdown with 6 attack options | MTH | Dropdown shows APT29, FIN7, Lazarus, REvil, SolarWinds, Insider |
| REQ-001-001-002 | Play button starts simulation | MTH | Clicking Play calls POST /api/v1/simulation/start |
| REQ-001-001-003 | Pause button pauses simulation | MTH | Clicking Pause calls POST /api/v1/simulation/pause |
| REQ-001-001-004 | Stop button resets simulation | MTH | Clicking Stop resets state and UI to initial |
| REQ-001-001-005 | Speed control slider (0.5x-4x) | MTH | Slider calls POST /api/v1/simulation/speed |
| REQ-001-001-006 | MITRE progress indicator (colored circles) | MTH | Circles update color based on WebSocket events |
| REQ-001-001-007 | Toggle visibility button | NTH | Button collapses/expands control bar |
| REQ-001-001-008 | Keyboard shortcut Space for Play/Pause | NTH | Space key toggles play/pause state |
| REQ-001-001-009 | Keyboard shortcut Esc for Stop | NTH | Escape key stops simulation |

##### FEAT-001-002: aIP Assist Widget `MTH`

**ID**: FEAT-001-002
**Priority**: MTH
**Description**: Floating widget in bottom-right corner showing proactive AI suggestions with expand/collapse functionality.
**Traces To**: US-006, US-007, US-008, US-009, US-010, BR-006, BR-007, BR-008, BR-009, BR-010

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-002-001 | Collapsed state shows circular button with icon | MTH | Button visible in bottom-right corner |
| REQ-001-002-002 | Badge shows unread suggestion count | MTH | Badge updates when new suggestions arrive |
| REQ-001-002-003 | Click expands to suggestion panel | MTH | Panel shows list of suggestions |
| REQ-001-002-004 | Suggestion shows title, description, actions | MTH | Each suggestion has Accept/Ignore buttons |
| REQ-001-002-005 | Accept button triggers associated action | MTH | Calls appropriate API endpoint |
| REQ-001-002-006 | Ignore button archives suggestion | MTH | Removes from panel, saves to history |
| REQ-001-002-007 | "Thinking" indicator during agent processing | MTH | Animated indicator shown when agent is working |
| REQ-001-002-008 | WebSocket subscription to aIP Assist events | MTH | Connects to WS /api/v1/aip-assist/ws/{session} |

##### FEAT-001-003: Narration Footer `MTH`

**ID**: FEAT-001-003
**Priority**: MTH
**Description**: Footer panel displaying streaming agent reasoning with timestamps, color coding, and collapse functionality.
**Traces To**: US-011, US-012, US-013, US-014, US-015, BR-011, BR-012, BR-013, BR-014, BR-015

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-003-001 | WebSocket connection to narration stream | MTH | Connects to WS /api/v1/narration/ws/{session} |
| REQ-001-003-002 | Messages display with timestamps | MTH | Format: [HH:MM:SS] message |
| REQ-001-003-003 | Color coding by message type | MTH | info=white, warning=yellow, error=red, success=green |
| REQ-001-003-004 | Auto-scroll to latest message | MTH | Panel scrolls automatically as messages arrive |
| REQ-001-003-005 | Expand/collapse toggle button | MTH | Button toggles panel visibility |
| REQ-001-003-006 | Continue receiving messages when collapsed | MTH | WebSocket stays connected, messages buffered |
| REQ-001-003-007 | Filter dropdown by message type | NTH | Dropdown to show only selected types |

##### FEAT-001-004: Global State Context `MTH`

**ID**: FEAT-001-004
**Priority**: MTH
**Description**: React Context provider managing shared state for simulation, narration, and AI assistant across all components.
**Traces To**: Section 1.2.2, AC-004

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-004-001 | SimulationContext with state and actions | MTH | Provides: scenario, status, speed, phase |
| REQ-001-004-002 | NarrationContext with messages and visibility | MTH | Provides: messages[], isExpanded, addMessage() |
| REQ-001-004-003 | AipAssistContext with suggestions and state | MTH | Provides: suggestions[], unreadCount, expanded |
| REQ-001-004-004 | Provider wraps entire application | MTH | App.tsx wrapped with all context providers |

---

### EPIC-002: Demo Scenarios `MTH`

**ID**: EPIC-002
**Priority**: MTH
**Description**: Implement the Demo Cases panel and Analyze with AI functionality for demonstrating agent capabilities on specific incidents.
**Business Value**: Provides one-click demos and ad-hoc AI analysis
**Traces To**: Section 1.4.4, 1.4.5

**Acceptance Criteria**:
- [ ] AC-005: Demo Cases panel visible on Dashboard
- [ ] AC-006: All 3 cases executable with deterministic outcomes
- [ ] AC-007: Analyze button visible on every incident row
- [ ] AC-008: Analysis results shown in narration and on button

#### Features

##### FEAT-002-001: Demo Cases Panel `MTH`

**ID**: FEAT-002-001
**Priority**: MTH
**Description**: Dashboard panel with 3 cards for predefined SOC demo scenarios.
**Traces To**: US-016, US-017, US-018, US-019, US-020, BR-016, BR-017, BR-018, BR-019, BR-020, BR-021

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-002-001-001 | Panel displays 3 scenario cards | MTH | Cards for Case 1, 2, 3 visible |
| REQ-002-001-002 | Card shows: name, host, type, expected outcome | MTH | All info visible on each card |
| REQ-002-001-003 | Click card executes demo scenario | MTH | Calls POST /api/v1/demo-scenarios/run/{n} |
| REQ-002-001-004 | Case 1 auto-contains WS-FIN-042 | MTH | Outcome: contained automatically |
| REQ-002-001-005 | Case 2 requests approval for LAPTOP-CFO-01 | MTH | Outcome: approval card appears |
| REQ-002-001-006 | Case 3 dismisses SRV-DEV-03 as false positive | MTH | Outcome: alert marked benign |
| REQ-002-001-007 | Status indicator during execution | MTH | Shows "Running..." then "Complete" |
| REQ-002-001-008 | Only one case can run at a time | MTH | Other cards disabled during execution |

##### FEAT-002-002: Approval Card `MTH`

**ID**: FEAT-002-002
**Priority**: MTH
**Description**: Modal or inline card for VIP asset containment approval (Case 2).
**Traces To**: US-017, BR-020

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-002-002-001 | Approval card appears when VIP detected | MTH | Card shows after Case 2 triggers |
| REQ-002-002-002 | Card shows asset info and agent reasoning | MTH | Displays host, risk level, recommendation |
| REQ-002-002-003 | Approve button confirms containment | MTH | Calls approval API, contains asset |
| REQ-002-002-004 | Reject button denies containment | MTH | Calls rejection API, logs decision |

##### FEAT-002-003: Analyze with AI Button `MTH`

**ID**: FEAT-002-003
**Priority**: MTH
**Description**: Button on each Incidents table row to trigger AI analysis.
**Traces To**: US-021, US-022, US-023, US-024, US-025, BR-022, BR-023, BR-024, BR-025, BR-026

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-002-003-001 | Button shows "Analyze with AI" initially | MTH | Default state on each row |
| REQ-002-003-002 | Click enqueues analysis via API | MTH | Calls POST /api/v1/analysis/queue |
| REQ-002-003-003 | Button changes to "Analyzing..." during processing | MTH | Disabled state with spinner |
| REQ-002-003-004 | Narration panel expands automatically | MTH | Panel opens when analysis starts |
| REQ-002-003-005 | Button shows decision icon when complete | MTH | Icons: contained, pending, dismissed |
| REQ-002-003-006 | Support multiple parallel analyses | MTH | Different rows can analyze simultaneously |

---

### EPIC-003: Simulation Page `MTH`

**ID**: EPIC-003
**Priority**: MTH
**Description**: Implement the dedicated /simulation page with 3-column layout for immersive formal presentations.
**Business Value**: Professional demo experience for sales and training
**Traces To**: Section 1.4.6

**Acceptance Criteria**:
- [ ] AC-009: Page accessible at /simulation route
- [ ] AC-010: 3-column layout displays correctly
- [ ] AC-011: MITRE phases show with status indicators
- [ ] AC-012: Attack graph visualizes in real-time
- [ ] AC-013: Narration always visible (not collapsible)

#### Features

##### FEAT-003-001: Simulation Page Layout `MTH`

**ID**: FEAT-003-001
**Priority**: MTH
**Description**: Full-page 3-column layout with independent controls.
**Traces To**: US-026, US-030, BR-027, BR-028, BR-031

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-003-001-001 | Route /simulation accessible | MTH | Navigation to /simulation works |
| REQ-003-001-002 | 3-column layout: phases, graph, AI panel | MTH | Columns sized appropriately |
| REQ-003-001-003 | Page has own scenario selector | MTH | Dropdown in page header |
| REQ-003-001-004 | Page has own playback controls | MTH | Play/Pause/Stop buttons |
| REQ-003-001-005 | Narration footer always visible | MTH | No collapse button on this page |
| REQ-003-001-006 | Hide global controls on this page | MTH | Global bar not shown |

##### FEAT-003-002: MITRE Phases Panel `MTH`

**ID**: FEAT-003-002
**Priority**: MTH
**Description**: Left column showing attack phases with status indicators.
**Traces To**: US-027, US-029, BR-030

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-003-002-001 | Vertical list of MITRE phases | MTH | All phases for selected scenario |
| REQ-003-002-002 | Status indicators: green/yellow/gray | MTH | Colors match phase status |
| REQ-003-002-003 | Yellow indicator pulses for active phase | MTH | CSS animation for active |
| REQ-003-002-004 | Click phase shows technique details | MTH | Expandable details panel |

##### FEAT-003-003: Attack Graph Visualization `MTH`

**ID**: FEAT-003-003
**Priority**: MTH
**Description**: Center column with interactive Cytoscape.js graph showing attack in real-time.
**Traces To**: US-028, BR-029

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-003-003-001 | Cytoscape.js graph container | MTH | Graph renders in center column |
| REQ-003-003-002 | Nodes for hosts, IOCs, C2 connections | MTH | Different node types distinguishable |
| REQ-003-003-003 | Edges for propagation and communication | MTH | Lines connect related nodes |
| REQ-003-003-004 | Real-time updates from WebSocket | MTH | Graph updates as events arrive |
| REQ-003-003-005 | Animation for new events | MTH | Visual feedback on changes |

##### FEAT-003-004: AI Analysis Panel `MTH`

**ID**: FEAT-003-004
**Priority**: MTH
**Description**: Right column with integrated AI assistant panel (non-floating).
**Traces To**: Section 1.4.6

**Requirements**:

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-003-004-001 | Panel shows AI suggestions inline | MTH | Not floating, integrated in layout |
| REQ-003-004-002 | Always visible, not collapsible | MTH | No toggle button |
| REQ-003-004-003 | Shows analysis, recommendations, correlations | MTH | Content from aIP Assist API |

---

## 2.5 Technical Requirements

| ID | Category | Requirement | Priority | Rationale |
|----|----------|-------------|----------|-----------|
| TECH-001 | Architecture | Use React Context for global state management | MTH | Enables state sharing across all components |
| TECH-002 | Architecture | Create custom hooks for WebSocket connections | MTH | Reusable connection logic |
| TECH-003 | Architecture | Implement lazy loading for Simulation page | NTH | Reduces initial bundle size |
| TECH-004 | Styling | Use Tailwind CSS classes matching existing design | MTH | Visual consistency |
| TECH-005 | Visualization | Use Cytoscape.js for attack graph | MTH | Already installed, powerful graph library |
| TECH-006 | State | Implement optimistic UI updates | NTH | Better user experience |
| TECH-007 | Error Handling | Display user-friendly error messages | MTH | Graceful degradation |
| TECH-008 | Error Handling | Auto-reconnect WebSockets on disconnect | MTH | Resilient connections |

## 2.6 Integration Requirements

| ID | External System | Requirement | Priority | Interface Type |
|----|-----------------|-------------|----------|----------------|
| INT-001 | Analysis API | Queue analysis via POST /api/v1/analysis/queue | MTH | REST API |
| INT-002 | Analysis API | Get status via GET /api/v1/analysis/status/{id} | MTH | REST API |
| INT-003 | Simulation API | Start via POST /api/v1/simulation/start | MTH | REST API |
| INT-004 | Simulation API | Pause via POST /api/v1/simulation/pause | MTH | REST API |
| INT-005 | Simulation API | Resume via POST /api/v1/simulation/resume | MTH | REST API |
| INT-006 | Simulation API | Speed via POST /api/v1/simulation/speed | MTH | REST API |
| INT-007 | Simulation API | State via GET /api/v1/simulation/state | MTH | REST API |
| INT-008 | Demo Scenarios | List via GET /api/v1/demo-scenarios/scenarios | MTH | REST API |
| INT-009 | Demo Scenarios | Run via POST /api/v1/demo-scenarios/run/{n} | MTH | REST API |
| INT-010 | aIP Assist | State via GET /api/v1/aip-assist/session/{id}/state | MTH | REST API |
| INT-011 | aIP Assist | Feedback via POST /api/v1/aip-assist/session/{id}/feedback | MTH | REST API |
| INT-012 | Analysis WS | Real-time updates via WS /api/v1/analysis/ws | MTH | WebSocket |
| INT-013 | Narration WS | Streaming via WS /api/v1/narration/ws/{session} | MTH | WebSocket |
| INT-014 | aIP Assist WS | Suggestions via WS /api/v1/aip-assist/ws/{session} | MTH | WebSocket |
| INT-015 | Simulation WS | State updates via WS /api/v1/simulation/ws | MTH | WebSocket |

## 2.7 Data Requirements

| ID | Entity | Description | Priority |
|----|--------|-------------|----------|
| DATA-001 | SimulationState | Current scenario, status, speed, phase | MTH |
| DATA-002 | NarrationMessage | timestamp, type, content | MTH |
| DATA-003 | AipSuggestion | id, title, description, actions, read status | MTH |
| DATA-004 | DemoCase | id, name, host, type, expectedOutcome, status | MTH |
| DATA-005 | MitrePhase | id, name, status (pending/active/complete), techniques[] | MTH |
| DATA-006 | AttackGraphNode | id, type, label, position | MTH |
| DATA-007 | AttackGraphEdge | id, source, target, type | MTH |

## 2.8 Full Traceability Matrix

| Req ID | Source | Description | Priority | Code File | Tests | Verified |
|--------|--------|-------------|----------|-----------|-------|----------|
| REQ-001-001-001 | US-001 | Scenario dropdown with 6 options | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-002 | US-002 | Play button starts simulation | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-003 | US-002 | Pause button pauses simulation | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-004 | US-002 | Stop button resets simulation | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-005 | US-003 | Speed control slider (0.5x-4x) | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-006 | US-004 | MITRE progress indicator | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-007 | US-005 | Toggle visibility button | NTH | [ ] | [ ] | [ ] |
| REQ-001-001-008 | US-005 | Keyboard shortcut Space | NTH | [ ] | [ ] | [ ] |
| REQ-001-001-009 | US-005 | Keyboard shortcut Esc | NTH | [ ] | [ ] | [ ] |
| REQ-001-002-001 | US-006 | Collapsed circular button | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-002 | US-008 | Unread suggestion badge | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-003 | US-007 | Expand to suggestion panel | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-004 | US-006 | Suggestion content display | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-005 | US-009 | Accept button triggers action | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-006 | US-009 | Ignore button archives | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-007 | US-010 | Thinking indicator | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-008 | US-006 | WebSocket subscription | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-001 | US-011 | WebSocket connection to narration | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-002 | US-011 | Messages with timestamps | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-003 | US-012 | Color coding by type | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-004 | US-013 | Auto-scroll to latest | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-005 | US-014 | Expand/collapse toggle | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-006 | US-014 | Continue receiving when collapsed | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-007 | US-015 | Filter by message type | NTH | [ ] | [ ] | [ ] |
| REQ-001-004-001 | AC-004 | SimulationContext | MTH | [ ] | [ ] | [ ] |
| REQ-001-004-002 | AC-004 | NarrationContext | MTH | [ ] | [ ] | [ ] |
| REQ-001-004-003 | AC-004 | AipAssistContext | MTH | [ ] | [ ] | [ ] |
| REQ-001-004-004 | AC-004 | Provider wraps app | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-001 | US-016 | Panel displays 3 cards | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-002 | US-019 | Card shows info | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-003 | US-016 | Click executes scenario | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-004 | US-016 | Case 1 auto-contains | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-005 | US-017 | Case 2 requests approval | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-006 | US-018 | Case 3 false positive | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-007 | US-020 | Status indicator | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-008 | BR-016 | One case at a time | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-001 | US-017 | Approval card appears | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-002 | US-017 | Card shows asset info | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-003 | US-017 | Approve button | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-004 | US-017 | Reject button | MTH | [ ] | [ ] | [ ] |
| REQ-002-003-001 | US-021 | Button shows initial state | MTH | [ ] | [ ] | [ ] |
| REQ-002-003-002 | US-021 | Click enqueues analysis | MTH | [ ] | [ ] | [ ] |
| REQ-002-003-003 | US-022 | Processing state | MTH | [ ] | [ ] | [ ] |
| REQ-002-003-004 | US-023 | Narration expands auto | MTH | [ ] | [ ] | [ ] |
| REQ-002-003-005 | US-024 | Decision icon on complete | MTH | [ ] | [ ] | [ ] |
| REQ-002-003-006 | US-025 | Parallel analyses | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-001 | US-026 | Route accessible | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-002 | US-026 | 3-column layout | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-003 | BR-028 | Page scenario selector | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-004 | BR-027 | Page playback controls | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-005 | BR-031 | Narration always visible | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-006 | BR-027 | Hide global controls | MTH | [ ] | [ ] | [ ] |
| REQ-003-002-001 | US-027 | Vertical MITRE list | MTH | [ ] | [ ] | [ ] |
| REQ-003-002-002 | US-027 | Status indicators | MTH | [ ] | [ ] | [ ] |
| REQ-003-002-003 | BR-030 | Pulsing active indicator | MTH | [ ] | [ ] | [ ] |
| REQ-003-002-004 | US-029 | Click shows techniques | MTH | [ ] | [ ] | [ ] |
| REQ-003-003-001 | US-028 | Cytoscape container | MTH | [ ] | [ ] | [ ] |
| REQ-003-003-002 | US-028 | Node types | MTH | [ ] | [ ] | [ ] |
| REQ-003-003-003 | US-028 | Edge types | MTH | [ ] | [ ] | [ ] |
| REQ-003-003-004 | BR-029 | Real-time WebSocket updates | MTH | [ ] | [ ] | [ ] |
| REQ-003-003-005 | BR-029 | Animation for events | MTH | [ ] | [ ] | [ ] |
| REQ-003-004-001 | Section 1.4.6 | AI panel inline | MTH | [ ] | [ ] | [ ] |
| REQ-003-004-002 | Section 1.4.6 | Always visible | MTH | [ ] | [ ] | [ ] |
| REQ-003-004-003 | Section 1.4.6 | Shows analysis content | MTH | [ ] | [ ] | [ ] |
| TECH-001 | Section 1.6 | React Context for state | MTH | [ ] | [ ] | [ ] |
| TECH-002 | Section 1.6 | Custom WebSocket hooks | MTH | [ ] | [ ] | [ ] |
| TECH-003 | Section 1.6 | Lazy loading simulation | NTH | [ ] | [ ] | [ ] |
| TECH-004 | Section 1.6 | Tailwind CSS consistency | MTH | [ ] | [ ] | [ ] |
| TECH-005 | Section 1.6 | Cytoscape.js for graph | MTH | [ ] | [ ] | [ ] |
| TECH-006 | Section 1.5 | Optimistic UI updates | NTH | [ ] | [ ] | [ ] |
| TECH-007 | Section 1.5 | User-friendly errors | MTH | [ ] | [ ] | [ ] |
| TECH-008 | Section 1.5 | WebSocket auto-reconnect | MTH | [ ] | [ ] | [ ] |
| INT-001 | Section 1.4.5 | Analysis queue API | MTH | [ ] | [ ] | [ ] |
| INT-002 | Section 1.4.5 | Analysis status API | MTH | [ ] | [ ] | [ ] |
| INT-003 | Section 1.4.1 | Simulation start API | MTH | [ ] | [ ] | [ ] |
| INT-004 | Section 1.4.1 | Simulation pause API | MTH | [ ] | [ ] | [ ] |
| INT-005 | Section 1.4.1 | Simulation resume API | MTH | [ ] | [ ] | [ ] |
| INT-006 | Section 1.4.1 | Simulation speed API | MTH | [ ] | [ ] | [ ] |
| INT-007 | Section 1.4.1 | Simulation state API | MTH | [ ] | [ ] | [ ] |
| INT-008 | Section 1.4.4 | Demo scenarios list API | MTH | [ ] | [ ] | [ ] |
| INT-009 | Section 1.4.4 | Demo scenarios run API | MTH | [ ] | [ ] | [ ] |
| INT-010 | Section 1.4.2 | aIP Assist state API | MTH | [ ] | [ ] | [ ] |
| INT-011 | Section 1.4.2 | aIP Assist feedback API | MTH | [ ] | [ ] | [ ] |
| INT-012 | Section 1.4.5 | Analysis WebSocket | MTH | [ ] | [ ] | [ ] |
| INT-013 | Section 1.4.3 | Narration WebSocket | MTH | [ ] | [ ] | [ ] |
| INT-014 | Section 1.4.2 | aIP Assist WebSocket | MTH | [ ] | [ ] | [ ] |
| INT-015 | Section 1.4.1 | Simulation WebSocket | MTH | [ ] | [ ] | [ ] |
| DATA-001 | Section 1.4.1 | SimulationState entity | MTH | [ ] | [ ] | [ ] |
| DATA-002 | Section 1.4.3 | NarrationMessage entity | MTH | [ ] | [ ] | [ ] |
| DATA-003 | Section 1.4.2 | AipSuggestion entity | MTH | [ ] | [ ] | [ ] |
| DATA-004 | Section 1.4.4 | DemoCase entity | MTH | [ ] | [ ] | [ ] |
| DATA-005 | Section 1.4.6 | MitrePhase entity | MTH | [ ] | [ ] | [ ] |
| DATA-006 | Section 1.4.6 | AttackGraphNode entity | MTH | [ ] | [ ] | [ ] |
| DATA-007 | Section 1.4.6 | AttackGraphEdge entity | MTH | [ ] | [ ] | [ ] |
| NFR-001 | Section 1.5 | UI update < 100ms | MTH | [ ] | [ ] | [ ] |
| NFR-002 | Section 1.5 | Page load < 2s | MTH | [ ] | [ ] | [ ] |
| NFR-003 | Section 1.5 | Availability - WebSocket handling | MTH | [ ] | [ ] | [ ] |
| NFR-004 | Section 1.5 | Security - No sensitive data | MTH | [ ] | [ ] | [ ] |
| NFR-005 | Section 1.5 | Scalability - Concurrent users | MTH | [ ] | [ ] | [ ] |
| NFR-006 | Section 1.5 | Usability - Keyboard shortcuts | NTH | [ ] | [ ] | [ ] |
| NFR-007 | Section 1.5 | Usability - Min 1280px width | MTH | [ ] | [ ] | [ ] |
| NFR-008 | Section 1.5 | Compatibility - Browsers | MTH | [ ] | [ ] | [ ] |
| NFR-009 | Section 1.5 | Accessibility - ARIA labels | NTH | [ ] | [ ] | [ ] |
| NFR-010 | Section 1.5 | Accessibility - Keyboard nav | NTH | [ ] | [ ] | [ ] |

## 2.9 Non-Functional Requirements (Detailed)

| ID | Category | Requirement | Priority |
|----|----------|-------------|----------|
| NFR-001 | Performance | UI updates must complete within 100ms of WebSocket event | MTH |
| NFR-002 | Performance | Page load time < 2 seconds on standard connection | MTH |
| NFR-003 | Availability | Components must gracefully handle WebSocket disconnection and auto-reconnect | MTH |
| NFR-004 | Security | No sensitive data stored in frontend state | MTH |
| NFR-005 | Scalability | Support concurrent users viewing same simulation | MTH |
| NFR-006 | Usability | Keyboard shortcuts: Space=Play/Pause, Esc=Stop, Arrow keys for speed | NTH |
| NFR-007 | Usability | Minimum supported width 1280px desktop only | MTH |
| NFR-008 | Security | Support Chrome, Firefox, Edge (last 2 versions) | MTH |
| NFR-009 | Usability | ARIA labels on all interactive elements | NTH |
| NFR-010 | Usability | Full keyboard navigation for all controls | NTH |

---

# VERIFICATION SECTION

## Part 1 to Part 2 Traceability

| Part 1 Section | Description | Covered in Part 2 | Requirement IDs |
|----------------|-------------|-------------------|-----------------|
| 1.4.1 | Demo Control System | [x] | REQ-001-001-001 to REQ-001-001-009 |
| 1.4.2 | AI Assistant Widget | [x] | REQ-001-002-001 to REQ-001-002-008 |
| 1.4.3 | Narration System | [x] | REQ-001-003-001 to REQ-001-003-007 |
| 1.4.4 | Demo Scenarios Panel | [x] | REQ-002-001-001 to REQ-002-001-008, REQ-002-002-001 to REQ-002-002-004 |
| 1.4.5 | AI Analysis Feature | [x] | REQ-002-003-001 to REQ-002-003-006 |
| 1.4.6 | Simulation Page | [x] | REQ-003-001-001 to REQ-003-004-003 |
| US-001 | Scenario dropdown | [x] | REQ-001-001-001 |
| US-002 | Playback controls | [x] | REQ-001-001-002, REQ-001-001-003, REQ-001-001-004 |
| US-003 | Speed control | [x] | REQ-001-001-005 |
| US-004 | MITRE progress | [x] | REQ-001-001-006 |
| US-005 | Toggle visibility | [x] | REQ-001-001-007 |
| US-006 | AI suggestions | [x] | REQ-001-002-001, REQ-001-002-004, REQ-001-002-008 |
| US-007 | Expand/collapse widget | [x] | REQ-001-002-003 |
| US-008 | Unread badge | [x] | REQ-001-002-002 |
| US-009 | Accept/ignore | [x] | REQ-001-002-005, REQ-001-002-006 |
| US-010 | Thinking indicator | [x] | REQ-001-002-007 |
| US-011 | Real-time narration | [x] | REQ-001-003-001, REQ-001-003-002 |
| US-012 | Color coding | [x] | REQ-001-003-003 |
| US-013 | Auto-scroll | [x] | REQ-001-003-004 |
| US-014 | Collapse narration | [x] | REQ-001-003-005, REQ-001-003-006 |
| US-015 | Filter messages | [x] | REQ-001-003-007 |
| US-016 | Demo Case 1 | [x] | REQ-002-001-001, REQ-002-001-003, REQ-002-001-004 |
| US-017 | Demo Case 2 | [x] | REQ-002-001-005, REQ-002-002-001 to REQ-002-002-004 |
| US-018 | Demo Case 3 | [x] | REQ-002-001-006 |
| US-019 | Card info | [x] | REQ-002-001-002 |
| US-020 | Execution status | [x] | REQ-002-001-007 |
| US-021 | AI analysis button | [x] | REQ-002-003-001, REQ-002-003-002 |
| US-022 | Analysis progress | [x] | REQ-002-003-003 |
| US-023 | Auto-open narration | [x] | REQ-002-003-004 |
| US-024 | Decision icon | [x] | REQ-002-003-005 |
| US-025 | Parallel analyses | [x] | REQ-002-003-006 |
| US-026 | Full-page simulation | [x] | REQ-003-001-001, REQ-003-001-002 |
| US-027 | MITRE phases | [x] | REQ-003-002-001, REQ-003-002-002 |
| US-028 | Attack graph | [x] | REQ-003-003-001 to REQ-003-003-005 |
| US-029 | Phase techniques | [x] | REQ-003-002-004 |
| US-030 | Narration always visible | [x] | REQ-003-001-005 |
| BR-001 | One scenario at a time | [x] | REQ-002-001-008 |
| BR-002 | Pause maintains state | [x] | REQ-001-001-003 |
| BR-003 | Stop resets state | [x] | REQ-001-001-004 |
| BR-004 | MITRE accuracy | [x] | REQ-001-001-006 |
| BR-005 | Control bar visibility | [x] | REQ-001-001-007, REQ-003-001-006 |
| BR-006 | Auto suggestions | [x] | REQ-001-002-008 |
| BR-007 | Unread badge count | [x] | REQ-001-002-002 |
| BR-008 | Accept triggers action | [x] | REQ-001-002-005 |
| BR-009 | Ignore archives | [x] | REQ-001-002-006 |
| BR-010 | Widget all pages | [x] | REQ-001-002-001 |
| BR-011 | Narration continues | [x] | REQ-001-003-006 |
| BR-012 | Messages accumulate | [x] | REQ-001-003-001 |
| BR-013 | Color coding | [x] | REQ-001-003-003 |
| BR-014 | Timestamps | [x] | REQ-001-003-002 |
| BR-015 | Collapsible footer | [x] | REQ-001-003-005 |
| BR-016 | One demo at a time | [x] | REQ-002-001-008 |
| BR-017 | Deterministic outcomes | [x] | REQ-002-001-004, REQ-002-001-005, REQ-002-001-006 |
| BR-018 | Narration shows process | [x] | REQ-001-003-001 |
| BR-019 | Case 1 auto-contain | [x] | REQ-002-001-004 |
| BR-020 | Case 2 VIP approval | [x] | REQ-002-001-005, REQ-002-002-001 |
| BR-021 | Case 3 false positive | [x] | REQ-002-001-006 |
| BR-022 | Async analysis | [x] | REQ-002-003-002 |
| BR-023 | Progress via narration | [x] | REQ-002-003-003 |
| BR-024 | Result persisted | [x] | REQ-002-003-005 |
| BR-025 | Parallel support | [x] | REQ-002-003-006 |
| BR-026 | Button states | [x] | REQ-002-003-001, REQ-002-003-003, REQ-002-003-005 |
| BR-027 | Page independent | [x] | REQ-003-001-003, REQ-003-001-004, REQ-003-001-006 |
| BR-028 | Page scenario selector | [x] | REQ-003-001-003 |
| BR-029 | Real-time visualization | [x] | REQ-003-003-004, REQ-003-003-005 |
| BR-030 | MITRE indicators | [x] | REQ-003-002-002, REQ-003-002-003 |
| BR-031 | Narration not collapsible | [x] | REQ-003-001-005 |

## Summary Statistics

| Category | MTH Count | NTH Count | Total |
|----------|-----------|-----------|-------|
| Epics | 3 | 0 | 3 |
| Features | 11 | 0 | 11 |
| Requirements (REQ) | 58 | 6 | 64 |
| Technical (TECH) | 6 | 2 | 8 |
| Integration (INT) | 15 | 0 | 15 |
| Data (DATA) | 7 | 0 | 7 |
| Non-Functional (NFR) | 6 | 4 | 10 |
| **Total** | **106** | **12** | **118** |

---

*Document generated by SoftwareBuilderX v21.0.0*
