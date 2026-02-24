# Test Plan: CyberDemo Interactive Frontend

| Attribute | Value |
|-----------|-------|
| Build ID | sbx-20260224-021825 |
| Created | 2026-02-24 |
| Template Version | SBX v21.0.0 |

---

## Test Strategy

| Type | Framework | Coverage Target |
|------|-----------|-----------------|
| Unit Tests | Vitest + React Testing Library | All REQ-xxx, TECH-xxx, DATA-xxx |
| Integration Tests | Vitest + MSW (Mock Service Worker) | All INT-xxx, cross-component flows |
| E2E Tests | Playwright | All FEAT-xxx user flows |

---

## Unit Tests

### TECH Requirements

| Test ID | Requirement | Description | File | Status |
|---------|-------------|-------------|------|--------|
| UT-TECH-001 | TECH-001 | Test DemoContext provider initializes with default state and exposes actions | tests/unit/contexts/DemoContext.test.tsx | Pending |
| UT-TECH-002 | TECH-002 | Test useSimulation hook calls correct API endpoints for start, pause, resume, speed | tests/unit/hooks/useSimulation.test.ts | Pending |
| UT-TECH-003 | TECH-003 | Test useNarration hook connects WebSocket, buffers messages, handles reconnection | tests/unit/hooks/useNarration.test.ts | Pending |
| UT-TECH-004 | TECH-004 | Test useAipAssist hook connects WebSocket, manages suggestions, tracks read state | tests/unit/hooks/useAipAssist.test.ts | Pending |
| UT-TECH-005 | TECH-005 | Test Cytoscape graph adapter creates nodes, edges, and updates layout | tests/unit/adapters/graphAdapter.test.ts | Pending |
| UT-TECH-006 | TECH-006 | Test keyboard shortcut handler registers Space and Esc bindings correctly | tests/unit/hooks/useKeyboardShortcuts.test.ts | Pending |

### DATA Requirements

| Test ID | Requirement | Description | File | Status |
|---------|-------------|-------------|------|--------|
| UT-DATA-001 | DATA-001 | Test simulation state schema stores scenario, phase, speed, running correctly | tests/unit/contexts/DemoContext.test.tsx | Pending |
| UT-DATA-002 | DATA-002 | Test narration message schema enforces timestamp, type, content; caps at 1000 entries | tests/unit/hooks/useNarration.test.ts | Pending |
| UT-DATA-003 | DATA-003 | Test AI suggestions schema tracks id, content, status, actions, read/unread | tests/unit/hooks/useAipAssist.test.ts | Pending |
| UT-DATA-004 | DATA-004 | Test analysis results schema stores id, decision, timestamp per incident | tests/unit/hooks/useAnalysis.test.ts | Pending |

### REQ Requirements - Demo Control Bar

| Test ID | Requirement | Description | File | Status |
|---------|-------------|-------------|------|--------|
| UT-001 | REQ-001-001-001 | Test DemoControlBar renders in header with all child controls | tests/unit/components/DemoControlBar.test.tsx | Pending |
| UT-002 | REQ-001-001-002 | Test ScenarioDropdown renders 6 options and fires onChange | tests/unit/components/DemoControlBar.test.tsx | Pending |
| UT-003 | REQ-001-001-003 | Test Play/Pause/Stop buttons render correct state and fire actions | tests/unit/components/DemoControlBar.test.tsx | Pending |
| UT-004 | REQ-001-001-004 | Test SpeedSlider renders range 0.5x-4x and fires onChange | tests/unit/components/DemoControlBar.test.tsx | Pending |
| UT-005 | REQ-001-001-005 | Test MitreProgress renders colored circles per phase | tests/unit/components/MitreProgress.test.tsx | Pending |
| UT-006 | REQ-001-001-006 | Test collapse/expand toggle hides and shows control bar content | tests/unit/components/DemoControlBar.test.tsx | Pending |

### REQ Requirements - aIP Assist Widget

| Test ID | Requirement | Description | File | Status |
|---------|-------------|-------------|------|--------|
| UT-007 | REQ-001-002-001 | Test AipAssistWidget renders as fixed position bottom-right | tests/unit/components/AipAssistWidget.test.tsx | Pending |
| UT-008 | REQ-001-002-002 | Test collapsed state renders circular button with badge count | tests/unit/components/AipAssistWidget.test.tsx | Pending |
| UT-009 | REQ-001-002-003 | Test expanded state renders suggestion list panel | tests/unit/components/AipAssistWidget.test.tsx | Pending |
| UT-010 | REQ-001-002-004 | Test each suggestion renders Analyze, Ignore, Details buttons | tests/unit/components/AipAssistWidget.test.tsx | Pending |
| UT-011 | REQ-001-002-005 | Test thinking indicator displays when isProcessing is true | tests/unit/components/AipAssistWidget.test.tsx | Pending |
| UT-012 | REQ-001-002-006 | Test badge count updates when unread suggestions change | tests/unit/components/AipAssistWidget.test.tsx | Pending |

### REQ Requirements - Narration Footer

| Test ID | Requirement | Description | File | Status |
|---------|-------------|-------------|------|--------|
| UT-013 | REQ-001-003-001 | Test NarrationFooter renders in layout footer area | tests/unit/components/NarrationFooter.test.tsx | Pending |
| UT-014 | REQ-001-003-002 | Test messages display with timestamps in terminal format | tests/unit/components/NarrationFooter.test.tsx | Pending |
| UT-015 | REQ-001-003-003 | Test color coding: info=white, warning=yellow, error=red, success=green | tests/unit/components/NarrationFooter.test.tsx | Pending |
| UT-016 | REQ-001-003-004 | Test expand/collapse toggle changes panel visibility | tests/unit/components/NarrationFooter.test.tsx | Pending |
| UT-017 | REQ-001-003-005 | Test auto-scroll triggers when new message added | tests/unit/components/NarrationFooter.test.tsx | Pending |
| UT-018 | REQ-001-003-006 | Test filter dropdown filters messages by type | tests/unit/components/NarrationFooter.test.tsx | Pending |

### REQ Requirements - Demo Cases Panel

| Test ID | Requirement | Description | File | Status |
|---------|-------------|-------------|------|--------|
| UT-019 | REQ-002-001-001 | Test DemoCasesPanel renders on Dashboard | tests/unit/components/DemoCasesPanel.test.tsx | Pending |
| UT-020 | REQ-002-001-002 | Test 3 case cards render name, host, type, expected result | tests/unit/components/DemoCasesPanel.test.tsx | Pending |
| UT-021 | REQ-002-001-003 | Test card click invokes agent handler | tests/unit/components/DemoCasesPanel.test.tsx | Pending |
| UT-022 | REQ-002-001-004 | Test loading state shows spinner during execution | tests/unit/components/DemoCasesPanel.test.tsx | Pending |
| UT-023 | REQ-002-001-005 | Test result display matches expected outcome | tests/unit/components/DemoCasesPanel.test.tsx | Pending |
| UT-024 | REQ-002-001-006 | Test approval card renders for Case 2 with approve/reject | tests/unit/components/ApprovalCard.test.tsx | Pending |

### REQ Requirements - Incident AI Analysis

| Test ID | Requirement | Description | File | Status |
|---------|-------------|-------------|------|--------|
| UT-025 | REQ-002-002-001 | Test AnalyzeButton renders in table row | tests/unit/components/AnalyzeButton.test.tsx | Pending |
| UT-026 | REQ-002-002-002 | Test 3 button states: initial, processing, completed with icon | tests/unit/components/AnalyzeButton.test.tsx | Pending |
| UT-027 | REQ-002-002-003 | Test click dispatches narration expand action | tests/unit/components/AnalyzeButton.test.tsx | Pending |
| UT-028 | REQ-002-002-004 | Test async analysis call queues request | tests/unit/components/AnalyzeButton.test.tsx | Pending |
| UT-029 | REQ-002-002-005 | Test result persists to incident state on completion | tests/unit/components/AnalyzeButton.test.tsx | Pending |
| UT-030 | REQ-002-002-006 | Test multiple parallel analyses run independently | tests/unit/components/AnalyzeButton.test.tsx | Pending |

### REQ Requirements - Simulation Page

| Test ID | Requirement | Description | File | Status |
|---------|-------------|-------------|------|--------|
| UT-031 | REQ-003-001-001 | Test SimulationPage route renders at /simulation | tests/unit/pages/SimulationPage.test.tsx | Pending |
| UT-032 | REQ-003-001-002 | Test 3-column layout renders MITRE, Graph, aIP panels | tests/unit/pages/SimulationPage.test.tsx | Pending |
| UT-033 | REQ-003-001-003 | Test MitrePhasesList renders vertical phases with status | tests/unit/components/MitrePhasesList.test.tsx | Pending |
| UT-034 | REQ-003-001-004 | Test AttackGraph renders Cytoscape canvas with nodes/edges | tests/unit/components/AttackGraph.test.tsx | Pending |
| UT-035 | REQ-003-001-005 | Test integrated aIP panel renders in right column (not floating) | tests/unit/pages/SimulationPage.test.tsx | Pending |
| UT-036 | REQ-003-001-006 | Test narration footer is always visible (not collapsible) | tests/unit/pages/SimulationPage.test.tsx | Pending |
| UT-037 | REQ-003-001-007 | Test scenario selector renders and fires selection change | tests/unit/pages/SimulationPage.test.tsx | Pending |
| UT-038 | REQ-003-001-008 | Test visualization updates when receiving WebSocket events | tests/unit/components/AttackGraph.test.tsx | Pending |

---

## Integration Tests

| Test ID | Requirements | Description | File | Status |
|---------|--------------|-------------|------|--------|
| IT-001 | REQ-001-001-001 to REQ-001-001-005 | Test DemoControlBar interacts with DemoContext for simulation control | tests/integration/DemoControlBar.integration.test.tsx | Pending |
| IT-002 | REQ-001-002-001 to REQ-001-002-006 | Test AipAssistWidget receives suggestions via WebSocket and renders actions | tests/integration/AipAssistWidget.integration.test.tsx | Pending |
| IT-003 | REQ-001-003-001 to REQ-001-003-005 | Test NarrationFooter receives messages via WebSocket and renders stream | tests/integration/NarrationFooter.integration.test.tsx | Pending |
| IT-004 | REQ-002-001-001 to REQ-002-001-006 | Test DemoCasesPanel invokes agent, shows loading, displays result | tests/integration/DemoCasesPanel.integration.test.tsx | Pending |
| IT-005 | REQ-002-002-001 to REQ-002-002-005 | Test AnalyzeButton queues analysis, shows progress, persists result | tests/integration/AnalyzeButton.integration.test.tsx | Pending |
| IT-006 | REQ-003-001-001 to REQ-003-001-008 | Test SimulationPage loads, connects WebSocket, updates visualization | tests/integration/SimulationPage.integration.test.tsx | Pending |
| IT-INT-001 | INT-001 | Test POST /api/v1/simulation/start integration with MSW mock | tests/integration/api/simulation.integration.test.ts | Pending |
| IT-INT-002 | INT-002 | Test POST /api/v1/simulation/pause integration with MSW mock | tests/integration/api/simulation.integration.test.ts | Pending |
| IT-INT-003 | INT-003 | Test POST /api/v1/simulation/resume integration with MSW mock | tests/integration/api/simulation.integration.test.ts | Pending |
| IT-INT-004 | INT-004 | Test POST /api/v1/simulation/speed integration with MSW mock | tests/integration/api/simulation.integration.test.ts | Pending |
| IT-INT-005 | INT-005 | Test WebSocket /api/v1/simulation/ws connection and event handling | tests/integration/ws/simulation.integration.test.ts | Pending |
| IT-INT-006 | INT-006 | Test POST /api/v1/analysis/queue integration with MSW mock | tests/integration/api/analysis.integration.test.ts | Pending |
| IT-INT-007 | INT-007 | Test WebSocket /api/v1/narration/ws/{session} connection and streaming | tests/integration/ws/narration.integration.test.ts | Pending |
| IT-INT-008 | INT-008 | Test WebSocket /api/v1/aip-assist/ws/{session} connection and suggestions | tests/integration/ws/aipAssist.integration.test.ts | Pending |

---

## E2E Tests (Playwright)

| Test ID | Feature | Description | File | Status |
|---------|---------|-------------|------|--------|
| E2E-001 | FEAT-001-001 | Full demo control bar flow: select scenario, play, adjust speed, view MITRE progress, pause, stop | tests/e2e/demoControlBar.spec.ts | Pending |
| E2E-002 | FEAT-001-002 | Full aIP Assist flow: receive suggestion, expand widget, click Analyze, see result | tests/e2e/aipAssistWidget.spec.ts | Pending |
| E2E-003 | FEAT-001-003 | Full narration flow: start simulation, see streaming messages, color coding, auto-scroll | tests/e2e/narrationFooter.spec.ts | Pending |
| E2E-004 | FEAT-002-001 | Full demo cases flow: click Case 1 (auto-contain), Case 2 (approval), Case 3 (false positive) | tests/e2e/demoCasesPanel.spec.ts | Pending |
| E2E-005 | FEAT-002-002 | Full AI analysis flow: click Analyze on incident, see processing, view result in narration | tests/e2e/analyzeWithAI.spec.ts | Pending |
| E2E-006 | FEAT-003-001 | Full simulation page flow: navigate, select scenario, start, see graph updates, view phases | tests/e2e/simulationPage.spec.ts | Pending |

---

## Coverage Verification Matrix

| Req ID | UT IDs | IT IDs | E2E IDs | Coverage |
|--------|--------|--------|---------|----------|
| REQ-001-001-001 | UT-001 | IT-001 | E2E-001 | [ ] Complete |
| REQ-001-001-002 | UT-002 | IT-001 | E2E-001 | [ ] Complete |
| REQ-001-001-003 | UT-003 | IT-001 | E2E-001 | [ ] Complete |
| REQ-001-001-004 | UT-004 | IT-001 | E2E-001 | [ ] Complete |
| REQ-001-001-005 | UT-005 | IT-001 | E2E-001 | [ ] Complete |
| REQ-001-001-006 | UT-006 | - | E2E-001 | [ ] Complete |
| REQ-001-002-001 | UT-007 | IT-002 | E2E-002 | [ ] Complete |
| REQ-001-002-002 | UT-008 | IT-002 | E2E-002 | [ ] Complete |
| REQ-001-002-003 | UT-009 | IT-002 | E2E-002 | [ ] Complete |
| REQ-001-002-004 | UT-010 | IT-002 | E2E-002 | [ ] Complete |
| REQ-001-002-005 | UT-011 | IT-002 | E2E-002 | [ ] Complete |
| REQ-001-002-006 | UT-012 | IT-002 | E2E-002 | [ ] Complete |
| REQ-001-003-001 | UT-013 | IT-003 | E2E-003 | [ ] Complete |
| REQ-001-003-002 | UT-014 | IT-003 | E2E-003 | [ ] Complete |
| REQ-001-003-003 | UT-015 | IT-003 | E2E-003 | [ ] Complete |
| REQ-001-003-004 | UT-016 | IT-003 | E2E-003 | [ ] Complete |
| REQ-001-003-005 | UT-017 | IT-003 | E2E-003 | [ ] Complete |
| REQ-001-003-006 | UT-018 | - | E2E-003 | [ ] Complete |
| REQ-002-001-001 | UT-019 | IT-004 | E2E-004 | [ ] Complete |
| REQ-002-001-002 | UT-020 | IT-004 | E2E-004 | [ ] Complete |
| REQ-002-001-003 | UT-021 | IT-004 | E2E-004 | [ ] Complete |
| REQ-002-001-004 | UT-022 | IT-004 | E2E-004 | [ ] Complete |
| REQ-002-001-005 | UT-023 | IT-004 | E2E-004 | [ ] Complete |
| REQ-002-001-006 | UT-024 | IT-004 | E2E-004 | [ ] Complete |
| REQ-002-002-001 | UT-025 | IT-005 | E2E-005 | [ ] Complete |
| REQ-002-002-002 | UT-026 | IT-005 | E2E-005 | [ ] Complete |
| REQ-002-002-003 | UT-027 | IT-005 | E2E-005 | [ ] Complete |
| REQ-002-002-004 | UT-028 | IT-005 | E2E-005 | [ ] Complete |
| REQ-002-002-005 | UT-029 | IT-005 | E2E-005 | [ ] Complete |
| REQ-002-002-006 | UT-030 | - | E2E-005 | [ ] Complete |
| REQ-003-001-001 | UT-031 | IT-006 | E2E-006 | [ ] Complete |
| REQ-003-001-002 | UT-032 | IT-006 | E2E-006 | [ ] Complete |
| REQ-003-001-003 | UT-033 | IT-006 | E2E-006 | [ ] Complete |
| REQ-003-001-004 | UT-034 | IT-006 | E2E-006 | [ ] Complete |
| REQ-003-001-005 | UT-035 | IT-006 | E2E-006 | [ ] Complete |
| REQ-003-001-006 | UT-036 | IT-006 | E2E-006 | [ ] Complete |
| REQ-003-001-007 | UT-037 | IT-006 | E2E-006 | [ ] Complete |
| REQ-003-001-008 | UT-038 | IT-006 | E2E-006 | [ ] Complete |
| TECH-001 | UT-TECH-001 | - | - | [ ] Complete |
| TECH-002 | UT-TECH-002 | - | - | [ ] Complete |
| TECH-003 | UT-TECH-003 | - | - | [ ] Complete |
| TECH-004 | UT-TECH-004 | - | - | [ ] Complete |
| TECH-005 | UT-TECH-005 | - | - | [ ] Complete |
| TECH-006 | UT-TECH-006 | - | - | [ ] Complete |
| INT-001 | - | IT-INT-001 | - | [ ] Complete |
| INT-002 | - | IT-INT-002 | - | [ ] Complete |
| INT-003 | - | IT-INT-003 | - | [ ] Complete |
| INT-004 | - | IT-INT-004 | - | [ ] Complete |
| INT-005 | - | IT-INT-005 | - | [ ] Complete |
| INT-006 | - | IT-INT-006 | - | [ ] Complete |
| INT-007 | - | IT-INT-007 | - | [ ] Complete |
| INT-008 | - | IT-INT-008 | - | [ ] Complete |
| DATA-001 | UT-DATA-001 | - | - | [ ] Complete |
| DATA-002 | UT-DATA-002 | - | - | [ ] Complete |
| DATA-003 | UT-DATA-003 | - | - | [ ] Complete |
| DATA-004 | UT-DATA-004 | - | - | [ ] Complete |
| NFR-001 | N/A | N/A | N/A | Not implementable this phase |
| NFR-002 | N/A | N/A | N/A | Not implementable this phase |
| NFR-003 | N/A | N/A | N/A | Not implementable this phase |
| NFR-004 | N/A | N/A | N/A | Not implementable this phase |
| NFR-005 | N/A | N/A | N/A | Not implementable this phase |

---
_Document generated by SoftwareBuilderX v21.0.0_
