# Test Plan: CyberDemo Agent-to-UI Enhancement

| Attribute | Value |
|-----------|-------|
| Build ID | sbx-20260224-155636 |
| Created | 2026-02-24 |
| Template Version | SBX v20.0.0 |

---

## Test Strategy

| Type | Framework | Coverage Target |
|------|-----------|-----------------|
| Unit Tests | Vitest (frontend), pytest (backend) | All REQ-xxx, TECH-xxx, DATA-xxx, NFR-xxx |
| Integration Tests | Vitest + pytest | All INT-xxx, cross-component flows |
| E2E Tests | Playwright | All FEAT-xxx user-facing flows |

---

## Unit Tests

| Test ID | Requirement | Description | File | Status |
|---------|-------------|-------------|------|--------|
| UT-001 | REQ-001-001-001 | useMcpStateSync hook connects to WS Server and auto-reconnects | tests/unit/frontend/useMcpStateSync.test.ts | Pending |
| UT-002 | REQ-001-001-002 | State updates trigger UI navigation with toast notification | tests/unit/frontend/wsNavigation.test.ts | Pending |
| UT-003 | REQ-001-001-003 | highlightedAssets state triggers node highlighting | tests/unit/frontend/assetHighlight.test.ts | Pending |
| UT-004 | REQ-001-001-004 | Charts array entries render as floating overlay | tests/unit/frontend/chartOverlay.test.ts | Pending |
| UT-005 | REQ-001-001-005 | Timeline state renders as sliding panel | tests/unit/frontend/timelinePanel.test.ts | Pending |
| UT-006 | REQ-001-001-006 | Graceful degradation if WS Server unavailable | tests/unit/frontend/wsGracefulDegradation.test.ts | Pending |
| UT-007 | REQ-001-002-001 | UIBridge WebSocket client connects and sends commands | tests/unit/backend/test_ui_bridge.py | Pending |
| UT-008 | REQ-001-002-002 | REST endpoint /api/v1/ui/action forwards commands | tests/unit/backend/test_ui_action_endpoint.py | Pending |
| UT-009 | REQ-001-002-003 | UIBridge silent failure when WS Server unavailable | tests/unit/backend/test_ui_bridge_failure.py | Pending |
| UT-010 | REQ-001-003-001 | Phase-to-UI-Action mapping for APT29 (8 phases) | tests/unit/backend/test_phase_ui_mapping.py | Pending |
| UT-011 | REQ-001-003-002 | UI actions trigger after agent analysis with delay | tests/unit/frontend/agentUIActions.test.ts | Pending |
| UT-012 | REQ-001-003-003 | Presenter toggle enables/disables auto-UI-actions | tests/unit/frontend/presenterToggle.test.ts | Pending |
| UT-013 | REQ-001-003-004 | Rate limiter for agent UI actions (max 2/sec) | tests/unit/frontend/rateLimiter.test.ts | Pending |
| UT-014 | REQ-001-003-005 | Queue UI actions during user interaction | tests/unit/frontend/actionQueue.test.ts | Pending |
| UT-015 | REQ-001-004-001 | Chart overlay smooth animation and auto-dismiss | tests/unit/frontend/chartOverlayAnimation.test.ts | Pending |
| UT-016 | REQ-001-004-002 | Three highlight modes (pulse, glow, zoom) | tests/unit/frontend/highlightModes.test.ts | Pending |
| UT-017 | REQ-001-004-003 | Timeline panel sliding animation and staggered entries | tests/unit/frontend/timelinePanelAnimation.test.ts | Pending |
| UT-018 | REQ-001-004-004 | Dashboard KPI counting number animation | tests/unit/frontend/kpiAnimation.test.ts | Pending |
| UT-019 | REQ-001-005-001 | npm run dev starts both React and WS Server | tests/unit/frontend/devStartup.test.ts | Pending |
| UT-020 | REQ-002-001-001 | ScenarioStateManager singleton with start/advance/reset | tests/unit/backend/test_scenario_state_manager.py | Pending |
| UT-021 | REQ-002-001-002 | Cumulative phase data (phase N includes 1..N) | tests/unit/backend/test_cumulative_phases.py | Pending |
| UT-022 | REQ-002-001-003 | Agent mutations persist in state | tests/unit/backend/test_agent_mutations.py | Pending |
| UT-023 | REQ-002-001-004 | Thread-safe state with asyncio Lock | tests/unit/backend/test_thread_safety.py | Pending |
| UT-024 | REQ-002-001-005 | Only one scenario active at a time | tests/unit/backend/test_exclusive_scenario.py | Pending |
| UT-025 | REQ-002-002-001 | APT29 phase 1-8 event definitions | tests/unit/backend/test_apt29_phases.py | Pending |
| UT-026 | REQ-002-002-002 | APT29 14 cumulative SIEM incidents | tests/unit/backend/test_apt29_siem.py | Pending |
| UT-027 | REQ-002-002-003 | APT29 15 cumulative EDR detections | tests/unit/backend/test_apt29_edr.py | Pending |
| UT-028 | REQ-002-002-004 | APT29 7 cumulative Intel IOCs | tests/unit/backend/test_apt29_iocs.py | Pending |
| UT-029 | REQ-002-002-005 | APT29 cross-reference consistency | tests/unit/backend/test_apt29_consistency.py | Pending |
| UT-030 | REQ-002-003-001 | FIN7 scenario script structure | tests/unit/backend/test_fin7_scenario.py | Pending |
| UT-031 | REQ-002-003-002 | Lazarus scenario script structure | tests/unit/backend/test_lazarus_scenario.py | Pending |
| UT-032 | REQ-002-003-003 | REvil scenario script structure | tests/unit/backend/test_revil_scenario.py | Pending |
| UT-033 | REQ-002-003-004 | SolarWinds scenario script structure | tests/unit/backend/test_solarwinds_scenario.py | Pending |
| UT-034 | REQ-002-003-005 | Insider Threat scenario script structure | tests/unit/backend/test_insider_scenario.py | Pending |
| UT-035 | REQ-002-004-001 | 25 tool handlers query ScenarioStateManager | tests/unit/backend/test_tool_handler_integration.py | Pending |
| UT-036 | REQ-002-004-002 | Backward compatibility (static data fallback) | tests/unit/backend/test_backward_compatibility.py | Pending |
| UT-037 | REQ-002-004-003 | Mutations reflected immediately in queries | tests/unit/backend/test_mutation_queries.py | Pending |
| UT-038 | REQ-002-004-004 | No future-phase data leakage | tests/unit/backend/test_phase_isolation.py | Pending |
| UT-039 | REQ-002-005-001 | Orchestration tools use scenario data | tests/unit/backend/test_orchestration_scenario.py | Pending |
| UT-040 | REQ-002-005-002 | Vega gateway enrichment integration | tests/unit/backend/test_vega_enrichment.py | Pending |
| UT-041 | REQ-002-006-001 | Phase sync between simulation and data engine | tests/unit/backend/test_phase_sync.py | Pending |
| UT-042 | REQ-002-006-002 | Jump-to-phase applies cumulative events | tests/unit/backend/test_jump_to_phase.py | Pending |

### Technical Requirement Unit Tests

| Test ID | Requirement | Description | File | Status |
|---------|-------------|-------------|------|--------|
| UT-TECH-001 | TECH-001 | useMcpStateSync hook implementation | tests/unit/frontend/useMcpStateSync.test.ts | Pending |
| UT-TECH-002 | TECH-002 | UIBridge Python class | tests/unit/backend/test_ui_bridge.py | Pending |
| UT-TECH-003 | TECH-003 | REST endpoint implementation | tests/unit/backend/test_ui_action_endpoint.py | Pending |
| UT-TECH-004 | TECH-004 | Chart overlay component | tests/unit/frontend/chartOverlay.test.ts | Pending |
| UT-TECH-005 | TECH-005 | Asset highlight CSS animations | tests/unit/frontend/highlightModes.test.ts | Pending |
| UT-TECH-006 | TECH-006 | Timeline panel component | tests/unit/frontend/timelinePanel.test.ts | Pending |
| UT-TECH-007 | TECH-007 | KPI animation component | tests/unit/frontend/kpiAnimation.test.ts | Pending |
| UT-TECH-008 | TECH-008 | ScenarioStateManager singleton | tests/unit/backend/test_scenario_state_manager.py | Pending |
| UT-TECH-009 | TECH-009 | Scenario script file structure | tests/unit/backend/test_apt29_phases.py | Pending |
| UT-TECH-010 | TECH-010 | PhaseEvents data structure | tests/unit/backend/test_scenario_state_manager.py | Pending |
| UT-TECH-011 | TECH-011 | Tool handler modifications | tests/unit/backend/test_tool_handler_integration.py | Pending |
| UT-TECH-012 | TECH-012 | Backward compatibility logic | tests/unit/backend/test_backward_compatibility.py | Pending |
| UT-TECH-013 | TECH-013 | E2E tests for UI control | tests/e2e/agentUIControl.spec.ts | Pending |

### NFR Unit Tests

| Test ID | Requirement | Description | File | Status |
|---------|-------------|-------------|------|--------|
| UT-NFR-001 | NFR-001 | UI state update render performance (<100ms) | tests/unit/frontend/useMcpStateSync.test.ts | Pending |
| UT-NFR-002 | NFR-002 | WS auto-reconnect with exponential backoff | tests/unit/frontend/useMcpStateSync.test.ts | Pending |
| UT-NFR-003 | NFR-003 | Graceful degradation if WS down | tests/unit/frontend/wsGracefulDegradation.test.ts | Pending |
| UT-NFR-004 | NFR-004 | No memory leaks from WS connections | tests/unit/frontend/useMcpStateSync.test.ts | Pending |
| UT-NFR-005 | NFR-005 | Max 50 concurrent clients | tests/unit/frontend/useMcpStateSync.test.ts | Pending |
| UT-NFR-006 | NFR-006 | ScenarioStateManager query <10ms | tests/unit/backend/test_scenario_state_manager.py | Pending |
| UT-NFR-007 | NFR-007 | Memory under 50MB for scenario data | tests/unit/backend/test_scenario_state_manager.py | Pending |
| UT-NFR-008 | NFR-008 | New scenario = new script file only | tests/unit/backend/test_apt29_phases.py | Pending |
| UT-NFR-009 | NFR-009 | Backward compatible with existing tests | tests/unit/backend/test_backward_compatibility.py | Pending |

### Data Requirement Unit Tests

| Test ID | Requirement | Description | File | Status |
|---------|-------------|-------------|------|--------|
| UT-DATA-001 | DATA-001 | PhaseEvents data structure | tests/unit/backend/test_scenario_state_manager.py | Pending |
| UT-DATA-002 | DATA-002 | ScenarioState cumulative structure | tests/unit/backend/test_scenario_state_manager.py | Pending |
| UT-DATA-003 | DATA-003 | APT29 event data completeness | tests/unit/backend/test_apt29_phases.py | Pending |
| UT-DATA-004 | DATA-004 | Additional scenario data | tests/unit/backend/test_fin7_scenario.py | Pending |
| UT-DATA-005 | DATA-005 | WS UI command format | tests/unit/frontend/useMcpStateSync.test.ts | Pending |
| UT-DATA-006 | DATA-006 | Agent mutation format | tests/unit/backend/test_agent_mutations.py | Pending |
| UT-DATA-007 | DATA-007 | Phase-to-UI-Action mapping | tests/unit/backend/test_phase_ui_mapping.py | Pending |

---

## Integration Tests

| Test ID | Requirements | Description | File | Status |
|---------|--------------|-------------|------|--------|
| IT-001 | REQ-001-001-001, INT-001 | React to MCP WS Server full WebSocket flow | tests/integration/frontend/wsConnection.integration.test.ts | Pending |
| IT-002 | REQ-001-002-001, INT-002 | UIBridge to MCP WS Server command forwarding | tests/integration/backend/test_ui_bridge_integration.py | Pending |
| IT-003 | REQ-001-003-001, INT-005 | Agent analysis triggers UI actions through pipeline | tests/integration/backend/test_agent_ui_pipeline.py | Pending |
| IT-004 | REQ-002-001-001, INT-003 | ScenarioStateManager with tool handler queries | tests/integration/backend/test_scenario_tool_flow.py | Pending |
| IT-005 | REQ-002-004-001, INT-003 | 25 tool handlers with ScenarioStateManager integration | tests/integration/backend/test_tool_integration.py | Pending |
| IT-006 | REQ-002-006-001, INT-004 | Simulation phase advance syncs both managers | tests/integration/backend/test_phase_sync_integration.py | Pending |
| IT-007 | REQ-001-003-004, REQ-001-003-005 | Rate limiting and user interaction queuing across WS pipeline | tests/integration/frontend/rateLimitQueue.integration.test.ts | Pending |

### Integration Requirement Tests

| Test ID | Requirement | Description | File | Status |
|---------|-------------|-------------|------|--------|
| IT-INT-001 | INT-001 | WebSocket protocol React to WS Server | tests/integration/frontend/wsConnection.integration.test.ts | Pending |
| IT-INT-002 | INT-002 | UIBridge to WS Server | tests/integration/backend/test_ui_bridge_integration.py | Pending |
| IT-INT-003 | INT-003 | Tool Handler to ScenarioStateManager | tests/integration/backend/test_tool_integration.py | Pending |
| IT-INT-004 | INT-004 | Simulation to Data Engine sync | tests/integration/backend/test_phase_sync_integration.py | Pending |
| IT-INT-005 | INT-005 | Agent to UI pipeline | tests/integration/backend/test_agent_ui_pipeline.py | Pending |

---

## E2E Tests (Playwright)

| Test ID | Feature | Description | File | Status |
|---------|---------|-------------|------|--------|
| E2E-001 | FEAT-001-001, FEAT-001-004 | WS state sync triggers UI components (charts, highlights, timeline) | tests/e2e/agentUIControl.spec.ts | Pending |
| E2E-002 | FEAT-001-003 | Agent analysis triggers UI actions with presenter controls | tests/e2e/agentUIActions.spec.ts | Pending |
| E2E-003 | FEAT-002-002 | APT29 scenario loads and phases advance with data | tests/e2e/apt29Scenario.spec.ts | Pending |
| E2E-004 | FEAT-002-004 | Tool handlers return scenario-aware data | tests/e2e/scenarioToolData.spec.ts | Pending |
| E2E-005 | FEAT-002-006 | Simulation phase sync with data engine | tests/e2e/phaseSync.spec.ts | Pending |
| E2E-006 | FEAT-001-001 | Graceful degradation when WS Server is down | tests/e2e/gracefulDegradation.spec.ts | Pending |

---

## Coverage Verification Matrix

| Req ID | UT IDs | IT IDs | E2E IDs | Coverage |
|--------|--------|--------|---------|----------|
| REQ-001-001-001 | UT-001 | IT-001 | E2E-001 | [ ] Complete |
| REQ-001-001-002 | UT-002 | IT-001 | E2E-001 | [ ] Complete |
| REQ-001-001-003 | UT-003 | IT-001 | E2E-001 | [ ] Complete |
| REQ-001-001-004 | UT-004 | IT-001 | E2E-001 | [ ] Complete |
| REQ-001-001-005 | UT-005 | IT-001 | E2E-001 | [ ] Complete |
| REQ-001-001-006 | UT-006 | IT-001 | E2E-006 | [ ] Complete |
| REQ-001-002-001 | UT-007 | IT-002 | - | [ ] Complete |
| REQ-001-002-002 | UT-008 | IT-002 | - | [ ] Complete |
| REQ-001-002-003 | UT-009 | IT-002 | - | [ ] Complete |
| REQ-001-003-001 | UT-010 | IT-003 | - | [ ] Complete |
| REQ-001-003-002 | UT-011 | IT-003 | E2E-002 | [ ] Complete |
| REQ-001-003-003 | UT-012 | - | E2E-002 | [ ] Complete |
| REQ-001-003-004 | UT-013 | IT-007 | - | [ ] Complete |
| REQ-001-003-005 | UT-014 | IT-007 | - | [ ] Complete |
| REQ-001-004-001 | UT-015 | - | E2E-001 | [ ] Complete |
| REQ-001-004-002 | UT-016 | - | E2E-001 | [ ] Complete |
| REQ-001-004-003 | UT-017 | - | E2E-001 | [ ] Complete |
| REQ-001-004-004 | UT-018 | - | - | [ ] Complete |
| REQ-001-005-001 | UT-019 | - | - | [ ] Complete |
| REQ-002-001-001 | UT-020 | IT-004 | - | [ ] Complete |
| REQ-002-001-002 | UT-021 | IT-004 | - | [ ] Complete |
| REQ-002-001-003 | UT-022 | IT-004 | - | [ ] Complete |
| REQ-002-001-004 | UT-023 | - | - | [ ] Complete |
| REQ-002-001-005 | UT-024 | - | - | [ ] Complete |
| REQ-002-002-001 | UT-025 | - | E2E-003 | [ ] Complete |
| REQ-002-002-002 | UT-026 | - | E2E-003 | [ ] Complete |
| REQ-002-002-003 | UT-027 | - | E2E-003 | [ ] Complete |
| REQ-002-002-004 | UT-028 | - | E2E-003 | [ ] Complete |
| REQ-002-002-005 | UT-029 | IT-004 | - | [ ] Complete |
| REQ-002-003-001 | UT-030 | - | - | [ ] Complete |
| REQ-002-003-002 | UT-031 | - | - | [ ] Complete |
| REQ-002-003-003 | UT-032 | - | - | [ ] Complete |
| REQ-002-003-004 | UT-033 | - | - | [ ] Complete |
| REQ-002-003-005 | UT-034 | - | - | [ ] Complete |
| REQ-002-004-001 | UT-035 | IT-005 | E2E-004 | [ ] Complete |
| REQ-002-004-002 | UT-036 | IT-005 | - | [ ] Complete |
| REQ-002-004-003 | UT-037 | IT-005 | - | [ ] Complete |
| REQ-002-004-004 | UT-038 | IT-005 | - | [ ] Complete |
| REQ-002-005-001 | UT-039 | - | - | [ ] Complete |
| REQ-002-005-002 | UT-040 | - | - | [ ] Complete |
| REQ-002-006-001 | UT-041 | IT-006 | E2E-005 | [ ] Complete |
| REQ-002-006-002 | UT-042 | IT-006 | - | [ ] Complete |
| TECH-001 | UT-TECH-001 | - | - | [ ] Complete |
| TECH-002 | UT-TECH-002 | - | - | [ ] Complete |
| TECH-003 | UT-TECH-003 | - | - | [ ] Complete |
| TECH-004 | UT-TECH-004 | - | - | [ ] Complete |
| TECH-005 | UT-TECH-005 | - | - | [ ] Complete |
| TECH-006 | UT-TECH-006 | - | - | [ ] Complete |
| TECH-007 | UT-TECH-007 | - | - | [ ] Complete |
| TECH-008 | UT-TECH-008 | - | - | [ ] Complete |
| TECH-009 | UT-TECH-009 | - | - | [ ] Complete |
| TECH-010 | UT-TECH-010 | - | - | [ ] Complete |
| TECH-011 | UT-TECH-011 | - | - | [ ] Complete |
| TECH-012 | UT-TECH-012 | - | - | [ ] Complete |
| TECH-013 | UT-TECH-013 | - | E2E-001 | [ ] Complete |
| INT-001 | - | IT-INT-001 | - | [ ] Complete |
| INT-002 | - | IT-INT-002 | - | [ ] Complete |
| INT-003 | - | IT-INT-003 | - | [ ] Complete |
| INT-004 | - | IT-INT-004 | - | [ ] Complete |
| INT-005 | - | IT-INT-005 | - | [ ] Complete |
| DATA-001 | UT-DATA-001 | - | - | [ ] Complete |
| DATA-002 | UT-DATA-002 | - | - | [ ] Complete |
| DATA-003 | UT-DATA-003 | - | - | [ ] Complete |
| DATA-004 | UT-DATA-004 | - | - | [ ] Complete |
| DATA-005 | UT-DATA-005 | - | - | [ ] Complete |
| DATA-006 | UT-DATA-006 | - | - | [ ] Complete |
| DATA-007 | UT-DATA-007 | - | - | [ ] Complete |
| NFR-001 | UT-NFR-001 | - | - | [ ] Complete |
| NFR-002 | UT-NFR-002 | - | - | [ ] Complete |
| NFR-003 | UT-NFR-003 | - | - | [ ] Complete |
| NFR-004 | UT-NFR-004 | - | - | [ ] Complete |
| NFR-005 | UT-NFR-005 | - | - | [ ] Complete |
| NFR-006 | UT-NFR-006 | - | - | [ ] Complete |
| NFR-007 | UT-NFR-007 | - | - | [ ] Complete |
| NFR-008 | UT-NFR-008 | - | - | [ ] Complete |
| NFR-009 | UT-NFR-009 | - | - | [ ] Complete |

---
_Document generated by SoftwareBuilderX v20.0.0_
