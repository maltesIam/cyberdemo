# Build Plan: CyberDemo Agent-to-UI Enhancement

| Attribute | Value |
|-----------|-------|
| Build ID | sbx-20260224-155636 |
| Created | 2026-02-24 |
| Functional Spec | docs/FUNCTIONAL_SPEC.md |
| Template Version | SBX v20.0.0 |

---

## Build Phases

### Cycle 1: MTH (Must-To-Have)

| Phase | Description | Tasks | Status |
|-------|-------------|-------|--------|
| P1 | Core Infrastructure (WS Hook, UIBridge, ScenarioStateManager) | 8 tasks | Pending |
| P2 | Frontend UI Components (Charts, Highlights, Timeline, KPI) | 5 tasks | Pending |
| P3 | Scenario Data & Tool Integration | 7 tasks | Pending |
| P4 | Integration, Sync & Testing | 7 tasks | Pending |

### Cycle 2: NTH (Nice-To-Have)

| Phase | Description | Tasks | Status |
|-------|-------------|-------|--------|
| P5 | Additional Scenarios & Orchestration | 8 tasks | Pending |
| P6 | Developer Experience | 1 task | Pending |

---

## Task Assignments

### Build Agent Distribution

| Agent | Focus Area | Task Count |
|-------|------------|------------|
| Agent 1 | Frontend (React hooks, WS, UI components) | 10 tasks |
| Agent 2 | Backend Core (UIBridge, ScenarioStateManager, data structures) | 8 tasks |
| Agent 3 | Scenario Scripts & Tool Handler Integration | 14 tasks |
| Agent 4 | Integration, Sync, Testing & NTH Features | 10 tasks |

### Detailed Task List

#### Phase P1: Core Infrastructure

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-001 | REQ-001-001-001 | Create useMcpStateSync React hook with WS connection to port 3001 and auto-reconnect | 1 | Pending |
| T-002 | REQ-001-001-006 | Implement graceful degradation when WS Server is unavailable | 1 | Pending |
| T-003 | REQ-001-002-001 | Create UIBridge Python class with async WS client (lazy connection) | 2 | Pending |
| T-004 | REQ-001-002-002 | Add REST endpoint POST /api/v1/ui/action forwarding commands to WS Server | 2 | Pending |
| T-005 | REQ-001-002-003 | Implement silent failure in UIBridge when WS Server unavailable | 2 | Pending |
| T-006 | REQ-002-001-001 | Create ScenarioStateManager singleton with start_scenario, advance_to_phase, reset | 2 | Pending |
| T-007 | REQ-002-001-002 | Implement cumulative phase data logic (phase N includes phases 1..N) | 2 | Pending |
| T-008 | REQ-002-001-004 | Add asyncio Lock for thread-safe state access | 2 | Pending |

#### Phase P2: Frontend UI Components

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-009 | REQ-001-001-002 | State updates from WS trigger UI navigation with toast notification | 1 | Pending |
| T-010 | REQ-001-001-003 | highlightedAssets state triggers node highlighting on graph page | 1 | Pending |
| T-011 | REQ-001-001-004 | Charts array entries render as floating overlay components | 1 | Pending |
| T-012 | REQ-001-001-005 | Timeline state renders as sliding panel from right | 1 | Pending |
| T-013 | REQ-001-004-001 | Chart overlays with smooth animation and auto-dismiss timer | 1 | Pending |

#### Phase P3: Scenario Data & Tool Integration

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-014 | REQ-001-004-002 | Asset highlight effects: pulse, glow, zoom CSS animations | 1 | Pending |
| T-015 | REQ-001-004-003 | Timeline panel with sliding animation and staggered entries | 1 | Pending |
| T-016 | REQ-001-004-004 | Dashboard KPI counting number animation effect | 1 | Pending |
| T-017 | REQ-002-002-001 | APT29 scenario script: 8 phase event definitions with SIEM incidents | 3 | Pending |
| T-018 | REQ-002-002-002 | APT29: 14 cumulative SIEM incidents across 8 phases | 3 | Pending |
| T-019 | REQ-002-002-003 | APT29: 15 cumulative EDR detections across 8 phases | 3 | Pending |
| T-020 | REQ-002-002-004 | APT29: 7 cumulative Intel IOCs across 8 phases | 3 | Pending |

#### Phase P4: Integration, Sync & Testing

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-021 | REQ-002-002-005 | APT29: Cross-reference consistency between incidents, detections, IOCs | 3 | Pending |
| T-022 | REQ-002-001-003 | Agent mutations (contain, close, comment) persist in ScenarioState | 2 | Pending |
| T-023 | REQ-002-001-005 | Only one scenario active at a time (exclusive lock) | 2 | Pending |
| T-024 | REQ-002-004-001 | Integrate 25 SOC tool handlers with ScenarioStateManager | 3 | Pending |
| T-025 | REQ-002-004-002 | Backward compatibility: return static data when no scenario active | 3 | Pending |
| T-026 | REQ-002-004-003 | Agent mutations reflected immediately in all tool queries | 3 | Pending |
| T-027 | REQ-002-004-004 | Tools must not reveal future-phase data (data isolation) | 3 | Pending |

#### Phase P4b: Agent UI Actions & Simulation Sync

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-028 | REQ-001-003-001 | Phase-to-UI-Action mapping configuration for APT29 (8 phases) | 4 | Pending |
| T-029 | REQ-001-003-002 | UI actions trigger 1-2s after agent analysis text appears | 4 | Pending |
| T-030 | REQ-001-003-003 | Presenter toggle to enable/disable auto-UI-actions | 4 | Pending |
| T-031 | REQ-001-003-004 | Rate limiter for agent UI actions (max 2/sec) | 4 | Pending |
| T-032 | REQ-001-003-005 | Queue UI actions during user interaction (no interruption) | 4 | Pending |
| T-033 | REQ-002-006-001 | Phase sync: attack_start_scenario initializes both managers | 4 | Pending |
| T-034 | REQ-002-006-002 | Phase advance and jump-to-stage sync cumulative events | 4 | Pending |

#### Phase P5: NTH - Additional Scenarios & Orchestration

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-035 | REQ-002-003-001 | FIN7 scenario script (6 phases, financial targeting) | 3 | Pending |
| T-036 | REQ-002-003-002 | Lazarus scenario script (5 phases, destructive wiper) | 3 | Pending |
| T-037 | REQ-002-003-003 | REvil scenario script (5 phases, ransomware) | 3 | Pending |
| T-038 | REQ-002-003-004 | SolarWinds scenario script (6 phases, supply chain) | 3 | Pending |
| T-039 | REQ-002-003-005 | Insider Threat scenario script (3 phases, credential abuse) | 3 | Pending |
| T-040 | REQ-002-005-001 | Agent orchestration tools query ScenarioStateManager | 4 | Pending |
| T-041 | REQ-002-005-002 | Optional Vega gateway enrichment for analysis text | 4 | Pending |

#### Phase P6: NTH - Developer Experience

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-042 | REQ-001-005-001 | npm run dev starts both React and MCP WS Server | 4 | Pending |

---

## Technical Requirements Tasks

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-TECH-001 | TECH-001 | useMcpStateSync React hook (part of T-001) | 1 | Pending |
| T-TECH-002 | TECH-002 | UIBridge Python class (part of T-003) | 2 | Pending |
| T-TECH-003 | TECH-003 | REST endpoint /api/v1/ui/action (part of T-004) | 2 | Pending |
| T-TECH-004 | TECH-004 | Chart overlay component (part of T-011, T-013) | 1 | Pending |
| T-TECH-005 | TECH-005 | Asset highlight CSS animations (part of T-014) | 1 | Pending |
| T-TECH-006 | TECH-006 | Timeline panel component (part of T-012, T-015) | 1 | Pending |
| T-TECH-007 | TECH-007 | KPI animation component (part of T-016) | 1 | Pending |
| T-TECH-008 | TECH-008 | ScenarioStateManager singleton (part of T-006) | 2 | Pending |
| T-TECH-009 | TECH-009 | Scenario script files structure (part of T-017) | 3 | Pending |
| T-TECH-010 | TECH-010 | PhaseEvents data structure (part of T-006) | 2 | Pending |
| T-TECH-011 | TECH-011 | 25 tool handler modifications (part of T-024) | 3 | Pending |
| T-TECH-012 | TECH-012 | Backward compatibility logic (part of T-025) | 3 | Pending |
| T-TECH-013 | TECH-013 | E2E tests for UI control flows (part of T-029) | 4 | Pending |

## Integration Requirements Tasks

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-INT-001 | INT-001 | WebSocket protocol for React to MCP WS Server (part of T-001) | 1 | Pending |
| T-INT-002 | INT-002 | UIBridge WS client to MCP WS Server (part of T-003) | 2 | Pending |
| T-INT-003 | INT-003 | Tool Handler to ScenarioStateManager query interface (part of T-024) | 3 | Pending |
| T-INT-004 | INT-004 | SimulationStateManager and ScenarioStateManager sync (part of T-033) | 4 | Pending |
| T-INT-005 | INT-005 | Agent Gateway to UI pipeline (part of T-029) | 4 | Pending |

## Data Requirements Tasks

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-DATA-001 | DATA-001 | PhaseEvents data structure (part of T-006) | 2 | Pending |
| T-DATA-002 | DATA-002 | ScenarioState cumulative structure (part of T-006) | 2 | Pending |
| T-DATA-003 | DATA-003 | APT29 complete event data (part of T-017-T-021) | 3 | Pending |
| T-DATA-004 | DATA-004 | Additional scenario event data (part of T-035-T-039) | 3 | Pending |
| T-DATA-005 | DATA-005 | WebSocket UI command format (part of T-001, T-003) | 1 | Pending |
| T-DATA-006 | DATA-006 | Agent mutation format (part of T-022) | 2 | Pending |
| T-DATA-007 | DATA-007 | Phase-to-UI-Action mapping config (part of T-028) | 4 | Pending |

## NFR Tasks

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-NFR-001 | NFR-001 | UI state updates render within 100ms (part of T-001) | 1 | Pending |
| T-NFR-002 | NFR-002 | WS auto-reconnect with exponential backoff (part of T-001) | 1 | Pending |
| T-NFR-003 | NFR-003 | Graceful degradation if WS down (part of T-002) | 1 | Pending |
| T-NFR-004 | NFR-004 | No memory leaks from WS connections (part of T-001) | 1 | Pending |
| T-NFR-005 | NFR-005 | Max 50 concurrent React clients (part of T-001) | 1 | Pending |
| T-NFR-006 | NFR-006 | ScenarioStateManager query response under 10ms (part of T-006) | 2 | Pending |
| T-NFR-007 | NFR-007 | Memory usage for scenario data under 50MB (part of T-006) | 2 | Pending |
| T-NFR-008 | NFR-008 | New scenario requires only new script file (part of T-017) | 3 | Pending |
| T-NFR-009 | NFR-009 | Backward compatible with existing tests (part of T-025) | 3 | Pending |

---

## Requirements Coverage Matrix

| Requirement ID | Task ID | Test IDs | Status |
|----------------|---------|----------|--------|
| REQ-001-001-001 | T-001 | UT-001, IT-001, E2E-001 | [ ] |
| REQ-001-001-002 | T-009 | UT-002, IT-001, E2E-001 | [ ] |
| REQ-001-001-003 | T-010 | UT-003, IT-001 | [ ] |
| REQ-001-001-004 | T-011 | UT-004, IT-001 | [ ] |
| REQ-001-001-005 | T-012 | UT-005, IT-001 | [ ] |
| REQ-001-001-006 | T-002 | UT-006, IT-001 | [ ] |
| REQ-001-002-001 | T-003 | UT-007, IT-002 | [ ] |
| REQ-001-002-002 | T-004 | UT-008, IT-002 | [ ] |
| REQ-001-002-003 | T-005 | UT-009, IT-002 | [ ] |
| REQ-001-003-001 | T-028 | UT-010, IT-003 | [ ] |
| REQ-001-003-002 | T-029 | UT-011, IT-003, E2E-002 | [ ] |
| REQ-001-003-003 | T-030 | UT-012, E2E-002 | [ ] |
| REQ-001-003-004 | T-031 | UT-013, IT-007 | [ ] |
| REQ-001-003-005 | T-032 | UT-014, IT-007 | [ ] |
| REQ-001-004-001 | T-013 | UT-015, E2E-001 | [ ] |
| REQ-001-004-002 | T-014 | UT-016, E2E-001 | [ ] |
| REQ-001-004-003 | T-015 | UT-017, E2E-001 | [ ] |
| REQ-001-004-004 | T-016 | UT-018 | [ ] |
| REQ-001-005-001 | T-042 | UT-019 | [ ] |
| REQ-002-001-001 | T-006 | UT-020, IT-004 | [ ] |
| REQ-002-001-002 | T-007 | UT-021, IT-004 | [ ] |
| REQ-002-001-003 | T-022 | UT-022, IT-004 | [ ] |
| REQ-002-001-004 | T-008 | UT-023 | [ ] |
| REQ-002-001-005 | T-023 | UT-024 | [ ] |
| REQ-002-002-001 | T-017 | UT-025 | [ ] |
| REQ-002-002-002 | T-018 | UT-026 | [ ] |
| REQ-002-002-003 | T-019 | UT-027 | [ ] |
| REQ-002-002-004 | T-020 | UT-028 | [ ] |
| REQ-002-002-005 | T-021 | UT-029, IT-004 | [ ] |
| REQ-002-003-001 | T-035 | UT-030 | [ ] |
| REQ-002-003-002 | T-036 | UT-031 | [ ] |
| REQ-002-003-003 | T-037 | UT-032 | [ ] |
| REQ-002-003-004 | T-038 | UT-033 | [ ] |
| REQ-002-003-005 | T-039 | UT-034 | [ ] |
| REQ-002-004-001 | T-024 | UT-035, IT-005 | [ ] |
| REQ-002-004-002 | T-025 | UT-036, IT-005 | [ ] |
| REQ-002-004-003 | T-026 | UT-037, IT-005 | [ ] |
| REQ-002-004-004 | T-027 | UT-038, IT-005 | [ ] |
| REQ-002-005-001 | T-040 | UT-039 | [ ] |
| REQ-002-005-002 | T-041 | UT-040 | [ ] |
| REQ-002-006-001 | T-033 | UT-041, IT-006 | [ ] |
| REQ-002-006-002 | T-034 | UT-042, IT-006 | [ ] |
| TECH-001 | T-TECH-001 | UT-001 | [ ] |
| TECH-002 | T-TECH-002 | UT-007 | [ ] |
| TECH-003 | T-TECH-003 | UT-008 | [ ] |
| TECH-004 | T-TECH-004 | UT-015 | [ ] |
| TECH-005 | T-TECH-005 | UT-016 | [ ] |
| TECH-006 | T-TECH-006 | UT-017 | [ ] |
| TECH-007 | T-TECH-007 | UT-018 | [ ] |
| TECH-008 | T-TECH-008 | UT-020 | [ ] |
| TECH-009 | T-TECH-009 | UT-025 | [ ] |
| TECH-010 | T-TECH-010 | UT-020 | [ ] |
| TECH-011 | T-TECH-011 | UT-035 | [ ] |
| TECH-012 | T-TECH-012 | UT-036 | [ ] |
| TECH-013 | T-TECH-013 | E2E-001 | [ ] |
| INT-001 | T-INT-001 | IT-001 | [ ] |
| INT-002 | T-INT-002 | IT-002 | [ ] |
| INT-003 | T-INT-003 | IT-005 | [ ] |
| INT-004 | T-INT-004 | IT-006 | [ ] |
| INT-005 | T-INT-005 | IT-003 | [ ] |
| DATA-001 | T-DATA-001 | UT-020 | [ ] |
| DATA-002 | T-DATA-002 | UT-020 | [ ] |
| DATA-003 | T-DATA-003 | UT-025 | [ ] |
| DATA-004 | T-DATA-004 | UT-030 | [ ] |
| DATA-005 | T-DATA-005 | UT-001 | [ ] |
| DATA-006 | T-DATA-006 | UT-022 | [ ] |
| DATA-007 | T-DATA-007 | UT-010 | [ ] |
| NFR-001 | T-NFR-001 | UT-001 | [ ] |
| NFR-002 | T-NFR-002 | UT-001 | [ ] |
| NFR-003 | T-NFR-003 | UT-006 | [ ] |
| NFR-004 | T-NFR-004 | UT-001 | [ ] |
| NFR-005 | T-NFR-005 | UT-001 | [ ] |
| NFR-006 | T-NFR-006 | UT-020 | [ ] |
| NFR-007 | T-NFR-007 | UT-020 | [ ] |
| NFR-008 | T-NFR-008 | UT-025 | [ ] |
| NFR-009 | T-NFR-009 | UT-036 | [ ] |

---
_Document generated by SoftwareBuilderX v20.0.0_
