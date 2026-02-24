# Functional Specification: CyberDemo Agent-to-UI Enhancement

| Attribute | Value |
|-----------|-------|
| Version | 2.0.0 |
| Date | 2026-02-24 |
| Build ID | sbx-20260224-152226 |
| Template Version | SBX v20.0.0 |
| Status | Final |
| Input Document | docs/FRONTEND_ADVANCED_DESCRIPTION.md |

---

# PART 1: FUNCTIONAL DESCRIPTION

## 1.1 Executive Summary

CyberDemo is a Security Operations Center (SOC) simulation platform that demonstrates AI agent capabilities in security incident investigation and response. The platform currently supports 40 backend MCP tools and a frontend with 8 MCP tools, enabling the AI agent Vega to analyze alerts and provide text-based narration.

This enhancement transforms CyberDemo from a passive demo into an interactive experience through two major additions:

1. **Agent-to-UI Bidirectional Control**: Vega gains the ability to control the UI directly, navigating pages, highlighting assets, generating charts, and showing timelines in real-time as it investigates.
2. **Dynamic Scenario Data Engine**: Static mock data is replaced with phase-aware scenario data that evolves as each attack simulation progresses, making every SOC tool return contextually relevant information.

**In Scope:**
- WebSocket integration between React app and Frontend MCP WS Server
- Backend UIBridge for forwarding agent UI commands
- Phase-aware UI actions triggered after agent analysis
- Enhanced visual effects for 8 frontend MCP tools
- ScenarioStateManager singleton for cumulative phase data
- Complete APT29 scenario script with 8 phases
- 5 additional scenario scripts (FIN7, Lazarus, REvil, SolarWinds, Insider)
- Integration of all 25 SOC tool handlers with the ScenarioStateManager
- 6 agent orchestration tool enhancements for scenario awareness
- Phase synchronization between simulation state and data engine

**Out of Scope:**
- Changes to the OpenClaw/Vega agent itself (only integration layer changes)
- New backend MCP tools beyond the existing 40
- Production deployment infrastructure
- Multi-tenant or multi-user session management
- Real external API integrations (all data remains mock/simulated)
- Mobile or responsive design changes

## 1.2 System Overview

### 1.2.1 Purpose

Enable the AI agent Vega to visually demonstrate its investigation findings by controlling the UI in real-time, while providing rich phase-aware data from attack simulation scenarios that makes every SOC tool contextually relevant.

### 1.2.2 Scope

The system extends the existing CyberDemo platform architecture with:
1. A React hook for WebSocket state synchronization with the Frontend MCP WS Server
2. A Python UIBridge module for backend-to-WS-Server communication
3. A ScenarioStateManager for cumulative phase-aware mock data
4. 6 scenario scripts based on real APT groups (MITRE ATT&CK mapped)
5. Integration of 31 tool handlers (25 SOC + 6 agent orchestration) with the data engine

### 1.2.3 Context Diagram

The system operates within the existing CyberDemo architecture. The React frontend communicates with the Backend MCP Server (40 tools). The new UIBridge in the backend forwards UI control commands to the Frontend MCP WS Server (port 3001), which broadcasts state updates to connected React clients via WebSocket. The ScenarioStateManager sits in the backend, providing phase-aware data to all tool handlers.

## 1.3 User Roles and Personas

| User Role | Description | Key Actions |
|-----------|-------------|-------------|
| Demo Audience | Watches the UI change in real-time as Vega investigates | Observes navigation, highlights, charts, and timelines |
| Demo Presenter | Starts simulation, controls pace, can intervene | Select scenario, pause/resume, toggle auto-UI-actions |
| Vega (AI Agent) | Analyzes phases and controls the UI to show findings | Analyze alerts, navigate pages, highlight assets, generate charts |

## 1.4 Functional Areas

### 1.4.1 Agent-to-UI Bidirectional Control (EPIC-001)

Enables the AI agent Vega to control the React UI in real-time by connecting the backend to the Frontend MCP WS Server and having the React app respond to state updates.

**User Stories:**
- US-001: As the React app, I need to connect to the MCP WS Server so I can receive UI commands from the agent
- US-002: As the backend, I need to forward UI control commands to the MCP WS Server so the UI responds to agent actions
- US-003: As Vega, when I analyze a phase of the attack, I should not only explain but also SHOW it on screen
- US-004: As a Demo Presenter, I want the 8 frontend MCP tools to produce richer, more visible effects
- US-005: As a developer, I want the MCP WS Server to start automatically with the dev environment

**Business Rules:**
- BR-001: The WS connection must not block the main thread
- BR-002: State updates must be applied within 100ms of receipt
- BR-003: If the WS Server is unavailable, the app must work normally (graceful degradation)
- BR-004: Navigation triggered by agent must be visually distinct (brief toast notification)
- BR-005: UI actions from the agent must be rate-limited (max 2 per second)
- BR-006: Failed UI actions must not affect backend operation
- BR-007: UI actions must not fire if the WS Server is disconnected
- BR-008: UI actions must not interrupt user interaction (queue if user is clicking)

### 1.4.2 Dynamic Scenario Data Engine (EPIC-002)

Replaces static mock data in the 25 SOC tools with a ScenarioStateManager that produces contextually appropriate data based on which scenario is running, which phase the simulation is in, and what actions the agent has taken.

**User Stories:**
- US-006: As the backend, I need a central state manager for cumulative simulation state
- US-007: As a Demo Presenter, I need the APT29 scenario with complete event scripts for all 8 phases
- US-008: As a Demo Presenter, I need 5 additional attack scenarios with domain-appropriate events
- US-009: As a tool handler, I need to query the ScenarioStateManager instead of returning static data
- US-010: As an agent orchestration tool, I need to use scenario data for contextual analysis
- US-011: As the simulation controller, I need phase advances to sync with the data engine

**Business Rules:**
- BR-009: Data is always cumulative (earlier phase events never disappear)
- BR-010: Agent mutations are immediate and visible to subsequent tool calls
- BR-011: Only one scenario can be active at a time
- BR-012: If no scenario is running, tools return current static mock data (backward compatibility)
- BR-013: Tools must not reveal future-phase data
- BR-014: Contained hosts show status "contained" in all relevant tool responses
- BR-015: Closed incidents show status "closed" in all tool responses
- BR-016: The ScenarioStateManager must be thread-safe (asyncio Lock)
- BR-017: Each scenario follows MITRE ATT&CK tactics in order

## 1.5 Non-Functional Requirements Summary

| Category | Requirement |
|----------|-------------|
| Performance | UI state updates must render within 100ms of WebSocket receipt |
| Availability | WS connection must auto-reconnect with exponential backoff |
| Availability | All UI actions must degrade gracefully if WS Server is down |
| Security | No memory leaks from WS connections (proper cleanup on unmount) |
| Scalability | Maximum 50 concurrent React clients supported |
| Performance | ScenarioStateManager must respond in less than 10ms for any query |
| Scalability | Memory usage for all scenario data must be less than 50MB |
| Usability | Adding a new scenario requires only creating a new script file |
| Availability | All existing E2E and unit tests must continue passing (backward compatible) |

## 1.6 Assumptions and Dependencies

**Assumptions:**
- The existing Frontend MCP WS Server (port 3001) is operational and supports the 8 tools
- The backend MCP Server has all 40 tools functional
- The Vega/OpenClaw agent gateway is optionally available for enrichment
- All 168 existing E2E tests pass as baseline

**Dependencies:**
- React 18+ with hooks support
- Python 3.11+ with asyncio and websockets library
- Existing MCP tool infrastructure
- Frontend MCP WS Server running on port 3001

## 1.7 Constraints

- No new external service dependencies (all data remains mock/simulated)
- WebSocket connection limited to localhost (development environment)
- Maximum 8 phases per scenario (MITRE ATT&CK kill chain)
- No changes to the Vega agent internals (only integration layer)

## 1.8 Project Context

CyberDemo is an existing platform with:
- React frontend with 168 passing E2E tests
- Backend MCP Server with 40 tools (Python/FastAPI)
- Frontend MCP WS Server with 8 tools (TypeScript/Node.js)
- Vega AI agent integration via GatewayClient
- Simulation control (start, pause, speed, jump-to-stage)

This enhancement builds on the existing architecture without breaking current functionality.

---

# PART 2: TECHNICAL REQUIREMENTS

## 2.1 Requirements Traceability Matrix

| Source Section | Requirement Types | Count |
|----------------|-------------------|-------|
| Section 1.4.1 (EPIC-001) | Functional (REQ-001-*) | 19 requirements |
| Section 1.4.2 (EPIC-002) | Functional (REQ-002-*) | 23 requirements |
| Section 1.5 | Non-Functional (NFR-*) | 9 requirements |
| System Design | Technical (TECH-*) | 13 requirements |
| System Integration | Integration (INT-*) | 5 requirements |
| Data Architecture | Data (DATA-*) | 7 requirements |

## 2.2 Requirements Numbering Convention

- **REQ-{epic}-{feature}-{seq}**: Functional requirements (e.g., REQ-001-001-001)
- **TECH-{seq}**: Technical requirements (e.g., TECH-001)
- **INT-{seq}**: Integration requirements (e.g., INT-001)
- **DATA-{seq}**: Data requirements (e.g., DATA-001)
- **NFR-{seq}**: Non-functional requirements (e.g., NFR-001)

## 2.3 Priority Classification

| Priority | Label | Description |
|----------|-------|-------------|
| MTH | Must-To-Have | Core functionality required for the enhancement to work |
| NTH | Nice-To-Have | Additional features that improve the experience but are not blocking |

## 2.4 Epics

### EPIC-001: Agent-to-UI Bidirectional Control `MTH`

**Description:** Enable Vega to control the React UI in real-time through WebSocket integration with the Frontend MCP WS Server.

**Business Value:** Transforms the demo from a passive text narration into an interactive visual experience where the audience sees the AI agent actively investigating and presenting findings.

**Acceptance Criteria:**
- The React app receives and applies state updates from the WS Server
- The backend can forward UI commands to the WS Server
- Each simulation phase triggers appropriate UI actions
- The 8 frontend MCP tools produce enhanced visual effects

##### FEAT-001-001: React to MCP WS Server Connection `MTH`

**Description:** React hook useMcpStateSync that connects to ws://localhost:3001 and applies state updates.

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-001-001 | React hook connects to WS Server on mount with auto-reconnect | MTH | Hook establishes WebSocket connection on component mount and reconnects automatically on disconnect |
| REQ-001-001-002 | State updates from WS Server trigger UI navigation with toast notification | MTH | When WS Server sends currentView update, React router navigates and shows brief toast indicating agent-triggered navigation (BR-004) |
| REQ-001-001-003 | highlightedAssets state changes trigger node highlighting on graph page | MTH | When highlightedAssets array is updated via WS, corresponding nodes pulse or glow on the network graph |
| REQ-001-001-004 | Charts array entries render as floating overlay components | MTH | When charts array receives new entry via WS, a chart overlay appears with specified type and data |
| REQ-001-001-005 | Timeline state renders as sliding panel from right | MTH | When timeline state is updated via WS, a panel slides in from right displaying timeline entries |
| REQ-001-001-006 | App works normally if WS Server is unavailable (graceful degradation) | MTH | If WS Server is down, all existing functionality works without errors or visual glitches |

##### FEAT-001-002: Backend to WS Server Bridge `MTH`

**Description:** Python UIBridge class that forwards UI control commands to the MCP WS Server.

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-002-001 | UIBridge WebSocket client connects to WS Server (lazy, first use) | MTH | UIBridge opens WS connection on first send_action call and reuses for subsequent calls |
| REQ-001-002-002 | REST endpoint POST /api/v1/ui/action for programmatic UI commands | MTH | POST request with action payload returns 200 and forwards command to WS Server |
| REQ-001-002-003 | Silent failure when WS Server is unavailable (no crash) | MTH | If WS Server is down, UIBridge logs warning and returns without raising exception |

##### FEAT-001-003: Agent Analysis with UI Actions `MTH`

**Description:** After Vega analyzes a simulation phase, appropriate UI actions are triggered automatically.

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-003-001 | Phase-to-UI-Action mapping defined for APT29 scenario (8 phases) | MTH | Configuration maps each APT29 phase to specific UI actions (navigate, highlight, chart) |
| REQ-001-003-002 | UI actions trigger 1-2 seconds after agent text analysis appears | MTH | After agent text renders, UI actions fire with configurable delay (default 1.5s) |
| REQ-001-003-003 | Presenter can disable auto-UI-actions via a toggle | MTH | Toggle in presenter controls enables or disables automatic UI actions globally |
| REQ-001-003-004 | UI actions from agent are rate-limited to max 2 per second | MTH | Rate limiter queues or drops UI actions exceeding 2 per second threshold (BR-005) |
| REQ-001-003-005 | UI actions queue when user is interacting (no interruption) | MTH | If user is actively clicking or typing, agent UI actions are queued until idle (BR-008) |

##### FEAT-001-004: Enhanced Frontend MCP Tools `MTH`

**Description:** Enhance the 8 existing frontend MCP tools for richer visual effects.

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-004-001 | Charts render as floating overlays with smooth animation and auto-dismiss | MTH | Chart appears with fade-in animation and auto-dismisses after configurable timeout |
| REQ-001-004-002 | Asset highlights support three modes: pulse, glow, and zoom | MTH | Each highlight mode produces visually distinct CSS animation on the target node |
| REQ-001-004-003 | Timeline panel slides in from right with animated entries | MTH | Panel slides smoothly from right edge and entries appear with staggered animation |
| REQ-001-004-004 | Dashboard KPI updates animate with counting number effect | MTH | KPI values animate from old to new value using counting number transition |

##### FEAT-001-005: WS Server Startup Integration `NTH`

**Description:** MCP WS Server starts automatically with npm run dev.

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-005-001 | npm run dev starts both React dev server and MCP WS Server | NTH | Single npm run dev command launches both processes using concurrently or similar |

### EPIC-002: Dynamic Scenario Data Engine `MTH`

**Description:** Replace static mock data with phase-aware scenario data that evolves as attack simulations progress.

**Business Value:** Makes the demo realistic by providing contextually appropriate data for every SOC tool based on the current attack phase, creating a coherent narrative across all investigation tools.

**Acceptance Criteria:**
- ScenarioStateManager provides cumulative phase data
- APT29 scenario has complete event scripts for all 8 phases
- All 25 SOC tool handlers query the manager for phase-appropriate data
- Phase advances sync between simulation and data engine

##### FEAT-002-001: ScenarioStateManager `MTH`

**Description:** Singleton Python class managing cumulative simulation state with query and mutation methods.

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-002-001-001 | Singleton class with start_scenario, advance_to_phase, reset methods | MTH | Only one instance exists; start loads scenario, advance accumulates phase data, reset clears state |
| REQ-002-001-002 | Cumulative phase data (phase N includes all data from phases 1 through N) | MTH | Advancing to phase 3 includes all events from phases 1, 2, and 3 |
| REQ-002-001-003 | Agent mutations (contain host, close incident, add comment) persist in state | MTH | After agent calls contain_host, all subsequent queries show host as contained |
| REQ-002-001-004 | Thread-safe state with asyncio Lock | MTH | Concurrent access to state manager does not cause data corruption |
| REQ-002-001-005 | Only one scenario active at a time (exclusive lock) | MTH | Starting a new scenario resets previous one; concurrent start attempts are rejected (BR-011) |

##### FEAT-002-002: APT29 Scenario Script `MTH`

**Description:** Complete event script for APT29 (Cozy Bear) with 8 phases, 14 SIEM incidents, 15 EDR detections, 7 IOCs.

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-002-002-001 | Phase 1-8 event definitions with SIEM incidents | MTH | Each of 8 phases has associated SIEM incident events with MITRE ATT&CK mapping |
| REQ-002-002-002 | 14 cumulative SIEM incidents across 8 phases | MTH | Total of 14 unique SIEM incidents distributed across phases with proper severity |
| REQ-002-002-003 | 15 cumulative EDR detections across 8 phases | MTH | Total of 15 unique EDR detections with process, path, and action details |
| REQ-002-002-004 | 7 cumulative Intel IOCs across 8 phases | MTH | Total of 7 IOCs (IPs, domains, hashes) with threat intel source attribution |
| REQ-002-002-005 | Cross-reference consistency between incidents, detections, and IOCs | MTH | IOC IPs referenced in incidents match IOC definitions and EDR network connections |

##### FEAT-002-003: Additional Scenario Scripts `NTH`

**Description:** 5 additional scenario scripts (FIN7, Lazarus, REvil, SolarWinds, Insider Threat).

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-002-003-001 | FIN7 scenario script (6 phases, financial targeting) | NTH | FIN7 script with 6 phases covering point-of-sale targeting with MITRE mapping |
| REQ-002-003-002 | Lazarus scenario script (5 phases, destructive wiper) | NTH | Lazarus script with 5 phases covering destructive wiper attack with MITRE mapping |
| REQ-002-003-003 | REvil scenario script (5 phases, ransomware) | NTH | REvil script with 5 phases covering ransomware deployment with MITRE mapping |
| REQ-002-003-004 | SolarWinds scenario script (6 phases, supply chain) | NTH | SolarWinds script with 6 phases covering supply chain compromise with MITRE mapping |
| REQ-002-003-005 | Insider Threat scenario script (3 phases, credential abuse) | NTH | Insider script with 3 phases covering credential abuse and data exfiltration |

##### FEAT-002-004: Tool Handler Integration `MTH`

**Description:** All 25 SOC domain tool handlers query ScenarioStateManager for phase-appropriate data.

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-002-004-001 | 25 tool handlers integrated with ScenarioStateManager query methods | MTH | Each of the 25 SOC tool handlers calls ScenarioStateManager before returning data |
| REQ-002-004-002 | Backward compatibility when no scenario is active (return static data) | MTH | When no scenario is active, tools return existing static mock data unchanged |
| REQ-002-004-003 | Agent mutations (contain, close, comment) reflected immediately in queries | MTH | After mutation call, next query to any tool reflects the mutation |
| REQ-002-004-004 | Tools must not reveal future-phase data (data isolation) | MTH | Query for current phase data never includes events from phases not yet reached (BR-013) |

##### FEAT-002-005: Agent Orchestration Enhancement `NTH`

**Description:** 6 agent orchestration tools use scenario data instead of separate mock stores.

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-002-005-001 | Agent orchestration tools query ScenarioStateManager for analysis context | NTH | 6 orchestration tools use ScenarioStateManager data for contextual responses |
| REQ-002-005-002 | Optional Vega gateway enrichment for text analysis portion | NTH | If Vega gateway is available, agent analysis text is enriched with LLM output |

##### FEAT-002-006: Simulation Phase Synchronization `MTH`

**Description:** Phase advances in the simulation sync with ScenarioStateManager.

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-002-006-001 | attack_start_scenario initializes both SimulationStateManager and ScenarioStateManager | MTH | Starting scenario loads data into both managers atomically |
| REQ-002-006-002 | Phase advance and jump-to-stage apply cumulative events to ScenarioStateManager | MTH | Advancing or jumping to phase N accumulates all events from phase 1 through N |

## 2.5 Technical Requirements

| ID | Category | Requirement | Priority | Verification |
|----|----------|-------------|----------|--------------|
| TECH-001 | Frontend | useMcpStateSync React hook with WebSocket connection to port 3001 | MTH | Hook connects and syncs state on mount |
| TECH-002 | Backend | UIBridge Python class with async WebSocket client | MTH | Class sends commands to WS Server |
| TECH-003 | API | REST endpoint POST /api/v1/ui/action for programmatic UI control | MTH | Endpoint accepts and forwards UI commands |
| TECH-004 | Frontend | Chart overlay React component with auto-dismiss timer | MTH | Component renders chart and auto-dismisses |
| TECH-005 | Frontend | Asset highlight effects via CSS animations (pulse, glow, zoom) | MTH | Three animation modes apply to nodes |
| TECH-006 | Frontend | Timeline sliding panel React component | MTH | Panel slides from right on state update |
| TECH-007 | Frontend | KPI animation component (counting number effect) | MTH | Numbers animate from old to new value |
| TECH-008 | Backend | ScenarioStateManager singleton class with async-safe state | MTH | Singleton with asyncio Lock protection |
| TECH-009 | Backend | Scenario script files in backend/src/mcp/scenarios/ directory | MTH | Scripts load via standard file pattern |
| TECH-010 | Backend | PhaseEvents data structure with SIEM, EDR, Intel event lists | MTH | Data structure holds typed event lists |
| TECH-011 | Backend | 25 tool handler modifications to query ScenarioStateManager | MTH | Each handler queries manager for data |
| TECH-012 | Backend | Backward compatibility: if no scenario active, return static data | MTH | Tools return static data when no scenario |
| TECH-013 | Testing | E2E tests with Playwright for UI control flows | MTH | Playwright tests verify UI actions work |

## 2.6 Integration Requirements

| ID | Systems | Description | Priority | Verification |
|----|---------|-------------|----------|--------------|
| INT-001 | React, MCP WS Server | WebSocket protocol for state synchronization (port 3001) | MTH | WS messages parsed and state applied |
| INT-002 | Backend, MCP WS Server | UIBridge WebSocket client for forwarding UI commands | MTH | Commands reach WS Server from backend |
| INT-003 | Tool Handlers, ScenarioStateManager | Query interface for phase-aware data retrieval | MTH | Tools receive phase-appropriate data |
| INT-004 | Simulation, Data Engine | Phase advance synchronization between SimulationStateManager and ScenarioStateManager | MTH | Both managers advance atomically |
| INT-005 | Agent Gateway, UI Pipeline | Agent analysis triggers UI actions through UIBridge | MTH | Agent analysis produces visible UI change |

## 2.7 Data Requirements

| ID | Entity | Description | Priority |
|----|--------|-------------|----------|
| DATA-001 | PhaseEvents | Data structure containing SIEM events, EDR detections, Intel IOCs per phase | MTH |
| DATA-002 | ScenarioState | Cumulative state structure with incidents, detections, IOCs, containment, tickets | MTH |
| DATA-003 | APT29Script | Complete event data: 14 SIEM incidents, 15 EDR detections, 7 IOCs across 8 phases | MTH |
| DATA-004 | AdditionalScripts | Event data for FIN7, Lazarus, REvil, SolarWinds, Insider Threat scenarios | NTH |
| DATA-005 | WSCommandFormat | WebSocket UI command message format (MCP tool_call and state_update protocols) | MTH |
| DATA-006 | MutationFormat | Agent mutation persistence format (comments, containment status, tickets, approvals) | MTH |
| DATA-007 | PhaseUIMapping | Phase-to-UI-Action mapping configuration for each scenario | MTH |

## 2.8 Full Traceability Matrix

| Req ID | Source | Description | Code | Tests | Verified |
|--------|--------|-------------|------|-------|----------|
| REQ-001-001-001 | US-001 | React hook connects to MCP WS Server on mount with auto-reconnect | [ ] | [ ] | [ ] |
| REQ-001-001-002 | US-001 | State updates from WS Server trigger UI navigation | [ ] | [ ] | [ ] |
| REQ-001-001-003 | US-001 | highlightedAssets state changes trigger node highlighting | [ ] | [ ] | [ ] |
| REQ-001-001-004 | US-001 | Charts array entries render as floating overlay | [ ] | [ ] | [ ] |
| REQ-001-001-005 | US-001 | Timeline state renders as sliding panel | [ ] | [ ] | [ ] |
| REQ-001-001-006 | US-001 | Graceful degradation if WS Server unavailable | [ ] | [ ] | [ ] |
| REQ-001-002-001 | US-002 | UIBridge WebSocket client connects to WS Server | [ ] | [ ] | [ ] |
| REQ-001-002-002 | US-002 | REST endpoint POST /api/v1/ui/action | [ ] | [ ] | [ ] |
| REQ-001-002-003 | US-002 | Silent failure when WS Server unavailable | [ ] | [ ] | [ ] |
| REQ-001-003-001 | US-003 | Phase-to-UI-Action mapping for APT29 | [ ] | [ ] | [ ] |
| REQ-001-003-002 | US-003 | UI actions trigger after agent analysis | [ ] | [ ] | [ ] |
| REQ-001-003-003 | US-003 | Presenter toggle for auto-UI-actions | [ ] | [ ] | [ ] |
| REQ-001-003-004 | BR-005 | Rate-limit agent UI actions (max 2/sec) | [ ] | [ ] | [ ] |
| REQ-001-003-005 | BR-008 | Queue UI actions during user interaction | [ ] | [ ] | [ ] |
| REQ-001-004-001 | US-004 | Charts render as floating overlays with animation | [ ] | [ ] | [ ] |
| REQ-001-004-002 | US-004 | Three highlight modes (pulse, glow, zoom) | [ ] | [ ] | [ ] |
| REQ-001-004-003 | US-004 | Timeline sliding panel with animation | [ ] | [ ] | [ ] |
| REQ-001-004-004 | US-004 | Dashboard KPI counting animation | [ ] | [ ] | [ ] |
| REQ-001-005-001 | US-005 | WS Server integrated startup with npm run dev | [ ] | [ ] | [ ] |
| REQ-002-001-001 | US-006 | ScenarioStateManager singleton with start/advance/reset | [ ] | [ ] | [ ] |
| REQ-002-001-002 | US-006 | Cumulative phase data application | [ ] | [ ] | [ ] |
| REQ-002-001-003 | US-006 | Agent mutation persistence in state | [ ] | [ ] | [ ] |
| REQ-002-001-004 | US-006 | Thread-safe state with asyncio Lock | [ ] | [ ] | [ ] |
| REQ-002-001-005 | BR-011 | Only one scenario active at a time | [ ] | [ ] | [ ] |
| REQ-002-002-001 | US-007 | APT29 phase 1-8 event definitions | [ ] | [ ] | [ ] |
| REQ-002-002-002 | US-007 | 14 cumulative SIEM incidents | [ ] | [ ] | [ ] |
| REQ-002-002-003 | US-007 | 15 cumulative EDR detections | [ ] | [ ] | [ ] |
| REQ-002-002-004 | US-007 | 7 cumulative Intel IOCs | [ ] | [ ] | [ ] |
| REQ-002-002-005 | US-007 | Cross-reference consistency | [ ] | [ ] | [ ] |
| REQ-002-003-001 | US-008 | FIN7 scenario script | [ ] | [ ] | [ ] |
| REQ-002-003-002 | US-008 | Lazarus scenario script | [ ] | [ ] | [ ] |
| REQ-002-003-003 | US-008 | REvil scenario script | [ ] | [ ] | [ ] |
| REQ-002-003-004 | US-008 | SolarWinds scenario script | [ ] | [ ] | [ ] |
| REQ-002-003-005 | US-008 | Insider Threat scenario script | [ ] | [ ] | [ ] |
| REQ-002-004-001 | US-009 | 25 tool handlers integrated with ScenarioStateManager | [ ] | [ ] | [ ] |
| REQ-002-004-002 | US-009 | Backward compatibility when no scenario active | [ ] | [ ] | [ ] |
| REQ-002-004-003 | US-009 | Mutations reflected immediately in queries | [ ] | [ ] | [ ] |
| REQ-002-004-004 | BR-013 | Tools must not reveal future-phase data | [ ] | [ ] | [ ] |
| REQ-002-005-001 | US-010 | Agent orchestration tools use scenario data | [ ] | [ ] | [ ] |
| REQ-002-005-002 | US-010 | Optional Vega gateway enrichment | [ ] | [ ] | [ ] |
| REQ-002-006-001 | US-011 | Phase sync between simulation and data engine | [ ] | [ ] | [ ] |
| REQ-002-006-002 | US-011 | Jump-to-phase applies cumulative events | [ ] | [ ] | [ ] |
| TECH-001 | US-001 | useMcpStateSync React hook | [ ] | [ ] | [ ] |
| TECH-002 | US-002 | UIBridge Python class | [ ] | [ ] | [ ] |
| TECH-003 | US-002 | REST endpoint POST /api/v1/ui/action | [ ] | [ ] | [ ] |
| TECH-004 | US-004 | Chart overlay component | [ ] | [ ] | [ ] |
| TECH-005 | US-004 | Asset highlight CSS animations | [ ] | [ ] | [ ] |
| TECH-006 | US-004 | Timeline sliding panel component | [ ] | [ ] | [ ] |
| TECH-007 | US-004 | KPI animation component | [ ] | [ ] | [ ] |
| TECH-008 | US-006 | ScenarioStateManager singleton | [ ] | [ ] | [ ] |
| TECH-009 | US-007 | Scenario script file structure | [ ] | [ ] | [ ] |
| TECH-010 | US-007 | PhaseEvents data structure | [ ] | [ ] | [ ] |
| TECH-011 | US-009 | 25 tool handler modifications | [ ] | [ ] | [ ] |
| TECH-012 | US-009 | Backward compatibility logic | [ ] | [ ] | [ ] |
| TECH-013 | US-003 | E2E tests for UI control flows | [ ] | [ ] | [ ] |
| INT-001 | Sec 2.6 | React and MCP WS Server WebSocket protocol | [ ] | [ ] | [ ] |
| INT-002 | Sec 2.6 | Backend UIBridge WebSocket client | [ ] | [ ] | [ ] |
| INT-003 | Sec 2.6 | Tool Handler to ScenarioStateManager interface | [ ] | [ ] | [ ] |
| INT-004 | Sec 2.6 | Simulation to Data Engine phase sync | [ ] | [ ] | [ ] |
| INT-005 | Sec 2.6 | Agent Gateway to UI action pipeline | [ ] | [ ] | [ ] |
| DATA-001 | Sec 2.7 | PhaseEvents data structure | [ ] | [ ] | [ ] |
| DATA-002 | Sec 2.7 | ScenarioStateManager cumulative state structure | [ ] | [ ] | [ ] |
| DATA-003 | Sec 2.7 | APT29 complete event data | [ ] | [ ] | [ ] |
| DATA-004 | Sec 2.7 | Additional scenario event data | [ ] | [ ] | [ ] |
| DATA-005 | Sec 2.7 | WebSocket UI command message format | [ ] | [ ] | [ ] |
| DATA-006 | Sec 2.7 | Agent mutation persistence format | [ ] | [ ] | [ ] |
| DATA-007 | Sec 2.7 | Phase-to-UI-Action mapping configuration | [ ] | [ ] | [ ] |
| NFR-001 | Sec 1.5 | UI state updates render within 100ms | [ ] | [ ] | [ ] |
| NFR-002 | Sec 1.5 | WS auto-reconnect with exponential backoff | [ ] | [ ] | [ ] |
| NFR-003 | Sec 1.5 | Graceful degradation if WS Server down | [ ] | [ ] | [ ] |
| NFR-004 | Sec 1.5 | No memory leaks from WS connections | [ ] | [ ] | [ ] |
| NFR-005 | Sec 1.5 | Maximum 50 concurrent React clients | [ ] | [ ] | [ ] |
| NFR-006 | Sec 1.5 | ScenarioStateManager query response under 10ms | [ ] | [ ] | [ ] |
| NFR-007 | Sec 1.5 | Memory usage for scenario data under 50MB | [ ] | [ ] | [ ] |
| NFR-008 | Sec 1.5 | New scenario requires only new script file | [ ] | [ ] | [ ] |
| NFR-009 | Sec 1.5 | Backward compatible with existing tests | [ ] | [ ] | [ ] |

---

## Verification Section

### Part 1 to Part 2 Traceability

| Part 1 Section | Covered in Part 2 | Requirements |
|----------------|-------------------|--------------|
| 1.4.1 Agent-to-UI Control | Covered | EPIC-001, FEAT-001-001 through FEAT-001-005, REQ-001-* |
| 1.4.2 Dynamic Data Engine | Covered | EPIC-002, FEAT-002-001 through FEAT-002-006, REQ-002-* |
| 1.5 Non-Functional | Covered | NFR-001 through NFR-009 |
| 1.6 Dependencies | Covered | TECH-001 through TECH-013 |
| 1.7 Constraints | Covered | INT-001 through INT-005 |

### Summary Statistics

| Category | MTH | NTH | Total |
|----------|-----|-----|-------|
| Epics | 2 | 0 | 2 |
| Features | 8 | 3 | 11 |
| Requirements | 34 | 8 | 42 |
| Technical | 13 | 0 | 13 |
| Integration | 5 | 0 | 5 |
| Data | 6 | 1 | 7 |
| Non-Functional | 9 | 0 | 9 |

*Document generated by SoftwareBuilderX v20.0.0*
