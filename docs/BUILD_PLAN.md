# Build Plan: CyberDemo Agent Integration Enhancement
Version: 1.0.0 | Date: 2026-02-22 | Functional Spec: docs/FUNCTIONAL_SPEC.md

---

## BUILD CONFIGURATION

| Parameter | Value |
|-----------|-------|
| Build ID | sbx-20260222-012823 |
| Parallel Agents | 4 construction + 1 TDD + 1 review |
| TDD Mode | Strict |
| Test Framework | pytest (backend) / vitest (frontend) |
| E2E Framework | Playwright |
| Backend Stack | Python 3.12 / FastAPI / SQLAlchemy |
| Frontend Stack | React 18 / TypeScript / TailwindCSS |

---

## CYCLE 1: MUST-TO-HAVE (MTH)

### Phase 1.1: Foundation & Infrastructure

| Task ID | Description | Requirements | Agent | Status |
|---------|-------------|--------------|-------|--------|
| T-1.1.001 | Create database schema for analysis_jobs table | TECH-004 | build-1 | pending |
| T-1.1.002 | Create database schema for webhook_configs table | TECH-005 | build-1 | pending |
| T-1.1.003 | Create Alembic migration for new tables | TECH-004, TECH-005 | build-1 | pending |
| T-1.1.004 | Create Pydantic models for webhook and job entities | TECH-001 | build-2 | pending |
| T-1.1.005 | Create OpenSearch index template for attack_simulations | INT-003 | build-2 | pending |

### Phase 1.2: Agent Orchestration MCP (EPIC-001)

| Task ID | Description | Requirements | Agent | Status |
|---------|-------------|--------------|-------|--------|
| T-1.2.001 | Implement webhook configuration API endpoint | REQ-001-001-001 | build-1 | pending |
| T-1.2.002 | Implement webhook dispatcher with retry logic | REQ-001-001-002, REQ-001-001-003 | build-1 | pending |
| T-1.2.003 | Implement webhook timeout handling | REQ-001-001-004 | build-1 | pending |
| T-1.2.004 | Implement webhook response validation | REQ-001-001-005 | build-1 | pending |
| T-1.2.005 | Implement POST /api/v1/analysis/queue endpoint | REQ-001-002-001 | build-2 | pending |
| T-1.2.006 | Implement GET /api/v1/analysis/status/{job_id} | REQ-001-002-002 | build-2 | pending |
| T-1.2.007 | Implement GET /api/v1/analysis/result/{job_id} | REQ-001-002-003 | build-2 | pending |
| T-1.2.008 | Implement WebSocket /ws/analysis for notifications | REQ-001-002-004 | build-3 | pending |
| T-1.2.009 | Implement job persistence in PostgreSQL | REQ-001-002-005 | build-2 | pending |
| T-1.2.010 | Implement job cleanup scheduler (>24h) | REQ-001-002-006 | build-2 | pending |
| T-1.2.011 | Implement MCP tool: agent_analyze_alert | REQ-001-003-001 | build-3 | pending |
| T-1.2.012 | Implement MCP tool: agent_investigate_ioc | REQ-001-003-002 | build-3 | pending |
| T-1.2.013 | Implement MCP tool: agent_recommend_action | REQ-001-003-003 | build-3 | pending |
| T-1.2.014 | Implement MCP tool: agent_generate_report | REQ-001-003-004 | build-3 | pending |
| T-1.2.015 | Implement MCP tool: agent_explain_decision | REQ-001-003-005 | build-4 | pending |
| T-1.2.016 | Implement MCP tool: agent_correlate_events | REQ-001-003-006 | build-4 | pending |
| T-1.2.017 | Register all agent orchestration tools in MCP server | TECH-001 | build-4 | pending |
| T-1.2.018 | Implement rate limiting (100 req/min) | TECH-008 | build-4 | pending |
| T-1.2.019 | Implement HMAC signature validation for webhooks | TECH-009 | build-4 | pending |
| T-1.2.020 | Implement audit logging for all invocations | REQ-014 | build-4 | pending |

### Phase 1.3: Attack Simulation System (EPIC-002)

| Task ID | Description | Requirements | Agent | Status |
|---------|-------------|--------------|-------|--------|
| T-1.3.001 | Create attack scenario base class and interface | TECH-001 | build-1 | pending |
| T-1.3.002 | Implement APT29 (Cozy Bear) scenario | REQ-002-001-001 | build-1 | pending |
| T-1.3.003 | Implement FIN7 scenario | REQ-002-001-002 | build-1 | pending |
| T-1.3.004 | Implement Lazarus Group scenario | REQ-002-001-003 | build-2 | pending |
| T-1.3.005 | Implement REvil ransomware scenario | REQ-002-001-004 | build-2 | pending |
| T-1.3.006 | Implement SolarWinds-style supply chain scenario | REQ-002-001-005 | build-3 | pending |
| T-1.3.007 | Implement Insider Threat scenario | REQ-002-001-006 | build-3 | pending |
| T-1.3.008 | Implement MCP tool: attack_start_scenario | REQ-002-002-001 | build-4 | pending |
| T-1.3.009 | Implement MCP tools: attack_pause/resume | REQ-002-002-002 | build-4 | pending |
| T-1.3.010 | Implement MCP tool: attack_speed | REQ-002-002-003 | build-4 | pending |
| T-1.3.011 | Implement MCP tool: attack_jump_to_stage | REQ-002-002-004 | build-4 | pending |
| T-1.3.012 | Implement MCP tool: attack_inject_event | REQ-002-002-005 | build-4 | pending |
| T-1.3.013 | Implement simulation state persistence | REQ-002-002-006, REQ-013 | build-3 | pending |
| T-1.3.014 | Implement GET /api/v1/mitre/tactics | REQ-002-003-002 | build-1 | pending |
| T-1.3.015 | Implement GET /api/v1/mitre/techniques/{tactic_id} | REQ-002-003-003 | build-1 | pending |
| T-1.3.016 | Add MITRE tactic/technique IDs to all scenario events | REQ-002-003-001 | build-2 | pending |
| T-1.3.017 | Implement attack chain visualization component in UI | REQ-002-003-004 | build-3 | pending |

### Phase 1.4: Integration & MTH Testing

| Task ID | Description | Requirements | Agent | Status |
|---------|-------------|--------------|-------|--------|
| T-1.4.001 | Integration tests for webhook system | FEAT-001-001 | build-1 | pending |
| T-1.4.002 | Integration tests for analysis queue | FEAT-001-002 | build-2 | pending |
| T-1.4.003 | Integration tests for agent orchestration tools | FEAT-001-003 | build-3 | pending |
| T-1.4.004 | Integration tests for attack scenarios | FEAT-002-001 | build-4 | pending |
| T-1.4.005 | Integration tests for simulation control | FEAT-002-002 | build-4 | pending |
| T-1.4.006 | E2E tests for full agent invocation flow | EPIC-001 | build-1 | pending |
| T-1.4.007 | E2E tests for attack simulation flow | EPIC-002 | build-2 | pending |
| T-1.4.008 | Playwright E2E: Webhook configuration UI | EPIC-001 | build-3 | pending |
| T-1.4.009 | Playwright E2E: Attack scenario selection UI | EPIC-002 | build-4 | pending |

---

## CYCLE 2: NICE-TO-HAVE (NTH)

### Phase 2.1: Real-Time Narration (EPIC-003)

| Task ID | Description | Requirements | Agent | Status |
|---------|-------------|--------------|-------|--------|
| T-2.1.001 | Create database schema for narration_messages | TECH-007 | build-1 | pending |
| T-2.1.002 | Create OpenSearch index for narration_logs | INT-004 | build-1 | pending |
| T-2.1.003 | Implement React NarrationPanel component (collapsable) | REQ-003-001-001 | build-2 | pending |
| T-2.1.004 | Implement message types (thinking/finding/decision) | REQ-003-001-002 | build-2 | pending |
| T-2.1.005 | Implement confidence indicator with colors | REQ-003-001-003 | build-2 | pending |
| T-2.1.006 | Implement auto-scroll for new messages | REQ-003-001-004 | build-2 | pending |
| T-2.1.007 | Implement narration toggle | REQ-003-001-005 | build-2 | pending |
| T-2.1.008 | Implement WebSocket /ws/narration streaming | REQ-003-002-001 | build-3 | pending |
| T-2.1.009 | Implement narration message format | REQ-003-002-002 | build-3 | pending |
| T-2.1.010 | Implement 100-message buffer | REQ-003-002-003 | build-3 | pending |
| T-2.1.011 | Implement GET /api/v1/narration/history/{session_id} | REQ-003-002-004 | build-3 | pending |

### Phase 2.2: Copilot Mode (EPIC-004)

| Task ID | Description | Requirements | Agent | Status |
|---------|-------------|--------------|-------|--------|
| T-2.2.001 | Implement React hooks for action capture | REQ-004-001-001 | build-1 | pending |
| T-2.2.002 | Implement event throttling (max 10/sec) | REQ-004-001-002 | build-1 | pending |
| T-2.2.003 | Define action context schema | REQ-004-001-003 | build-1 | pending |
| T-2.2.004 | Implement WebSocket /ws/copilot/actions | REQ-004-001-004 | build-2 | pending |
| T-2.2.005 | Implement MCP tool: copilot_get_suggestion | REQ-004-002-001 | build-3 | pending |
| T-2.2.006 | Implement MCP tool: copilot_explain_why | REQ-004-002-002 | build-3 | pending |
| T-2.2.007 | Implement MCP tool: copilot_auto_complete | REQ-004-002-003 | build-3 | pending |
| T-2.2.008 | Implement CopilotWidget React component | REQ-004-002-004, TECH-012 | build-4 | pending |
| T-2.2.009 | Implement suggestion acceptance/rejection tracking | REQ-004-002-005 | build-4 | pending |

### Phase 2.3: Automated Playbooks (EPIC-005)

| Task ID | Description | Requirements | Agent | Status |
|---------|-------------|--------------|-------|--------|
| T-2.3.001 | Create database schema for playbook_executions | TECH-006 | build-1 | pending |
| T-2.3.002 | Implement POST /api/v1/playbooks/execute/{id} | REQ-005-001-001 | build-1 | pending |
| T-2.3.003 | Implement POST /api/v1/playbooks/{id}/pause | REQ-005-001-002 | build-1 | pending |
| T-2.3.004 | Implement POST /api/v1/playbooks/{id}/resume | REQ-005-001-003 | build-2 | pending |
| T-2.3.005 | Implement POST /api/v1/playbooks/{id}/rollback | REQ-005-001-004 | build-2 | pending |
| T-2.3.006 | Implement GET /api/v1/playbooks/{id}/status | REQ-005-001-005 | build-2 | pending |
| T-2.3.007 | Implement playbook state persistence | REQ-005-001-006 | build-2 | pending |
| T-2.3.008 | Implement Ransomware Response playbook | REQ-005-002-001 | build-3 | pending |
| T-2.3.009 | Implement Phishing Investigation playbook | REQ-005-002-002 | build-3 | pending |
| T-2.3.010 | Implement Lateral Movement Detection playbook | REQ-005-002-003 | build-3 | pending |
| T-2.3.011 | Implement Data Exfiltration Response playbook | REQ-005-002-004 | build-4 | pending |
| T-2.3.012 | Implement Insider Threat Investigation playbook | REQ-005-002-005 | build-4 | pending |
| T-2.3.013 | Implement Cloud Compromise Response playbook | REQ-005-002-006 | build-4 | pending |

### Phase 2.4: Demo Control Panel (EPIC-006)

| Task ID | Description | Requirements | Agent | Status |
|---------|-------------|--------------|-------|--------|
| T-2.4.001 | Implement DemoControlPanel React component | TECH-011 | build-1 | pending |
| T-2.4.002 | Implement Play/Pause/Stop buttons | REQ-006-001-001 | build-1 | pending |
| T-2.4.003 | Implement speed slider (0.5x-4x) | REQ-006-001-002 | build-1 | pending |
| T-2.4.004 | Implement scenario selection dropdown | REQ-006-001-003 | build-2 | pending |
| T-2.4.005 | Implement MITRE stage progress bar | REQ-006-001-004 | build-2 | pending |
| T-2.4.006 | Implement keyboard shortcuts | REQ-006-001-005 | build-2 | pending |
| T-2.4.007 | Implement DemoContext for global state | REQ-006-002-001 | build-3 | pending |
| T-2.4.008 | Implement localStorage persistence | REQ-006-002-002 | build-3 | pending |
| T-2.4.009 | Implement MCP Frontend Server sync | REQ-006-002-003 | build-3 | pending |

### Phase 2.5: NTH Integration & Testing

| Task ID | Description | Requirements | Agent | Status |
|---------|-------------|--------------|-------|--------|
| T-2.5.001 | Integration tests for narration system | EPIC-003 | build-1 | pending |
| T-2.5.002 | Integration tests for copilot system | EPIC-004 | build-2 | pending |
| T-2.5.003 | Integration tests for playbook engine | EPIC-005 | build-3 | pending |
| T-2.5.004 | Integration tests for demo control panel | EPIC-006 | build-4 | pending |
| T-2.5.005 | E2E tests for narration streaming | EPIC-003 | build-1 | pending |
| T-2.5.006 | E2E tests for copilot suggestions | EPIC-004 | build-2 | pending |
| T-2.5.007 | E2E tests for playbook execution | EPIC-005 | build-3 | pending |
| T-2.5.008 | Playwright E2E: Narration panel UI | EPIC-003 | build-4 | pending |
| T-2.5.009 | Playwright E2E: Copilot widget UI | EPIC-004 | build-4 | pending |
| T-2.5.010 | Playwright E2E: Demo control panel UI | EPIC-006 | build-4 | pending |

---

## REQUIREMENTS COVERAGE MATRIX

### EPIC-001: Agent Orchestration MCP (MTH)

| Requirement ID | Summary | Build Task | Test ID | Status |
|----------------|---------|------------|---------|--------|
| REQ-001-001-001 | Webhook configure endpoint | T-1.2.001 | UT-001, IT-001 | [ ] |
| REQ-001-001-002 | Webhook dispatcher | T-1.2.002 | UT-002, IT-001 | [ ] |
| REQ-001-001-003 | Retry logic with backoff | T-1.2.002 | UT-003, IT-001 | [ ] |
| REQ-001-001-004 | Configurable timeout | T-1.2.003 | UT-004, IT-001 | [ ] |
| REQ-001-001-005 | Response validation | T-1.2.004 | UT-005, IT-001 | [ ] |
| REQ-001-002-001 | Queue analysis endpoint | T-1.2.005 | UT-006, IT-002 | [ ] |
| REQ-001-002-002 | Job status endpoint | T-1.2.006 | UT-007, IT-002 | [ ] |
| REQ-001-002-003 | Job result endpoint | T-1.2.007 | UT-008, IT-002 | [ ] |
| REQ-001-002-004 | WebSocket notifications | T-1.2.008 | UT-009, IT-002 | [ ] |
| REQ-001-002-005 | Job persistence | T-1.2.009 | UT-010, IT-002 | [ ] |
| REQ-001-002-006 | Job cleanup | T-1.2.010 | UT-011, IT-002 | [ ] |
| REQ-001-003-001 | agent_analyze_alert tool | T-1.2.011 | UT-012, IT-003 | [ ] |
| REQ-001-003-002 | agent_investigate_ioc tool | T-1.2.012 | UT-013, IT-003 | [ ] |
| REQ-001-003-003 | agent_recommend_action tool | T-1.2.013 | UT-014, IT-003 | [ ] |
| REQ-001-003-004 | agent_generate_report tool | T-1.2.014 | UT-015, IT-003 | [ ] |
| REQ-001-003-005 | agent_explain_decision tool | T-1.2.015 | UT-016, IT-003 | [ ] |
| REQ-001-003-006 | agent_correlate_events tool | T-1.2.016 | UT-017, IT-003 | [ ] |

### EPIC-002: Attack Simulation System (MTH)

| Requirement ID | Summary | Build Task | Test ID | Status |
|----------------|---------|------------|---------|--------|
| REQ-002-001-001 | APT29 scenario | T-1.3.002 | UT-018, IT-004 | [ ] |
| REQ-002-001-002 | FIN7 scenario | T-1.3.003 | UT-019, IT-004 | [ ] |
| REQ-002-001-003 | Lazarus scenario | T-1.3.004 | UT-020, IT-004 | [ ] |
| REQ-002-001-004 | REvil scenario | T-1.3.005 | UT-021, IT-004 | [ ] |
| REQ-002-001-005 | SolarWinds scenario | T-1.3.006 | UT-022, IT-004 | [ ] |
| REQ-002-001-006 | Insider Threat scenario | T-1.3.007 | UT-023, IT-004 | [ ] |
| REQ-002-002-001 | attack_start_scenario tool | T-1.3.008 | UT-024, IT-005 | [ ] |
| REQ-002-002-002 | attack_pause/resume tools | T-1.3.009 | UT-025, IT-005 | [ ] |
| REQ-002-002-003 | attack_speed tool | T-1.3.010 | UT-026, IT-005 | [ ] |
| REQ-002-002-004 | attack_jump_to_stage tool | T-1.3.011 | UT-027, IT-005 | [ ] |
| REQ-002-002-005 | attack_inject_event tool | T-1.3.012 | UT-028, IT-005 | [ ] |
| REQ-002-002-006 | Simulation state persistence | T-1.3.013 | UT-029, IT-005 | [ ] |
| REQ-002-003-001 | MITRE IDs in events | T-1.3.016 | UT-030, IT-004 | [ ] |
| REQ-002-003-002 | List tactics endpoint | T-1.3.014 | UT-031, IT-004 | [ ] |
| REQ-002-003-003 | Get techniques endpoint | T-1.3.015 | UT-032, IT-004 | [ ] |
| REQ-002-003-004 | Attack chain visualization | T-1.3.017 | UT-071, IT-004 | [ ] |

### EPIC-003: Real-Time Narration (NTH)

| Requirement ID | Summary | Build Task | Test ID | Status |
|----------------|---------|------------|---------|--------|
| REQ-003-001-001 | Collapsable panel | T-2.1.003 | UT-033, IT-006 | [ ] |
| REQ-003-001-002 | Message types | T-2.1.004 | UT-034, IT-006 | [ ] |
| REQ-003-001-003 | Confidence indicator | T-2.1.005 | UT-035, IT-006 | [ ] |
| REQ-003-001-004 | Auto-scroll | T-2.1.006 | UT-036, IT-006 | [ ] |
| REQ-003-001-005 | Toggle narration | T-2.1.007 | UT-037, IT-006 | [ ] |
| REQ-003-002-001 | WebSocket streaming | T-2.1.008 | UT-038, IT-006 | [ ] |
| REQ-003-002-002 | Message format | T-2.1.009 | UT-039, IT-006 | [ ] |
| REQ-003-002-003 | Message buffer | T-2.1.010 | UT-040, IT-006 | [ ] |
| REQ-003-002-004 | History endpoint | T-2.1.011 | UT-041, IT-006 | [ ] |

### EPIC-004: Copilot Mode (NTH)

| Requirement ID | Summary | Build Task | Test ID | Status |
|----------------|---------|------------|---------|--------|
| REQ-004-001-001 | Action capture hooks | T-2.2.001 | UT-042, IT-007 | [ ] |
| REQ-004-001-002 | Event throttling | T-2.2.002 | UT-043, IT-007 | [ ] |
| REQ-004-001-003 | Context schema | T-2.2.003 | UT-044, IT-007 | [ ] |
| REQ-004-001-004 | Copilot WebSocket | T-2.2.004 | UT-045, IT-007 | [ ] |
| REQ-004-002-001 | copilot_get_suggestion tool | T-2.2.005 | UT-046, IT-007 | [ ] |
| REQ-004-002-002 | copilot_explain_why tool | T-2.2.006 | UT-047, IT-007 | [ ] |
| REQ-004-002-003 | copilot_auto_complete tool | T-2.2.007 | UT-048, IT-007 | [ ] |
| REQ-004-002-004 | CopilotWidget component | T-2.2.008 | UT-049, IT-007 | [ ] |
| REQ-004-002-005 | Acceptance tracking | T-2.2.009 | UT-050, IT-007 | [ ] |

### EPIC-005: Automated Playbooks (NTH)

| Requirement ID | Summary | Build Task | Test ID | Status |
|----------------|---------|------------|---------|--------|
| REQ-005-001-001 | Execute endpoint | T-2.3.002 | UT-051, IT-008 | [ ] |
| REQ-005-001-002 | Pause endpoint | T-2.3.003 | UT-052, IT-008 | [ ] |
| REQ-005-001-003 | Resume endpoint | T-2.3.004 | UT-053, IT-008 | [ ] |
| REQ-005-001-004 | Rollback endpoint | T-2.3.005 | UT-054, IT-008 | [ ] |
| REQ-005-001-005 | Status endpoint | T-2.3.006 | UT-055, IT-008 | [ ] |
| REQ-005-001-006 | State persistence | T-2.3.007 | UT-056, IT-008 | [ ] |
| REQ-005-002-001 | Ransomware playbook | T-2.3.008 | UT-057, IT-008 | [ ] |
| REQ-005-002-002 | Phishing playbook | T-2.3.009 | UT-058, IT-008 | [ ] |
| REQ-005-002-003 | Lateral Movement playbook | T-2.3.010 | UT-059, IT-008 | [ ] |
| REQ-005-002-004 | Data Exfiltration playbook | T-2.3.011 | UT-060, IT-008 | [ ] |
| REQ-005-002-005 | Insider Threat playbook | T-2.3.012 | UT-061, IT-008 | [ ] |
| REQ-005-002-006 | Cloud Compromise playbook | T-2.3.013 | UT-062, IT-008 | [ ] |

### EPIC-006: Demo Control Panel (NTH)

| Requirement ID | Summary | Build Task | Test ID | Status |
|----------------|---------|------------|---------|--------|
| REQ-006-001-001 | Play/Pause/Stop buttons | T-2.4.002 | UT-063, IT-009 | [ ] |
| REQ-006-001-002 | Speed slider | T-2.4.003 | UT-064, IT-009 | [ ] |
| REQ-006-001-003 | Scenario dropdown | T-2.4.004 | UT-065, IT-009 | [ ] |
| REQ-006-001-004 | Progress bar | T-2.4.005 | UT-066, IT-009 | [ ] |
| REQ-006-001-005 | Keyboard shortcuts | T-2.4.006 | UT-067, IT-009 | [ ] |
| REQ-006-002-001 | DemoContext | T-2.4.007 | UT-068, IT-009 | [ ] |
| REQ-006-002-002 | localStorage persistence | T-2.4.008 | UT-069, IT-009 | [ ] |
| REQ-006-002-003 | MCP sync | T-2.4.009 | UT-070, IT-009 | [ ] |

---

## AGENT ASSIGNMENTS

### Cycle 1 (MTH) - Phase Distribution

| Agent | Phase 1.1 | Phase 1.2 | Phase 1.3 | Phase 1.4 | Total Tasks |
|-------|-----------|-----------|-----------|-----------|-------------|
| build-1 | 3 | 4 | 5 | 2 | 14 |
| build-2 | 2 | 6 | 4 | 2 | 14 |
| build-3 | 0 | 5 | 3 | 2 | 10 |
| build-4 | 0 | 5 | 4 | 2 | 11 |

### Cycle 2 (NTH) - Phase Distribution

| Agent | Phase 2.1 | Phase 2.2 | Phase 2.3 | Phase 2.4 | Phase 2.5 | Total Tasks |
|-------|-----------|-----------|-----------|-----------|-----------|-------------|
| build-1 | 2 | 3 | 2 | 2 | 2 | 11 |
| build-2 | 5 | 1 | 3 | 3 | 2 | 14 |
| build-3 | 4 | 3 | 3 | 3 | 2 | 15 |
| build-4 | 0 | 2 | 4 | 0 | 4 | 10 |

---

## TEST PLAN REFERENCE

See: [docs/SBX_TEST_PLAN.md](SBX_TEST_PLAN.md)

---

## SUMMARY

| Metric | Cycle 1 (MTH) | Cycle 2 (NTH) | Total |
|--------|---------------|---------------|-------|
| Phases | 4 | 5 | 9 |
| Tasks | 46 | 55 | 101 |
| Unit Tests | 33 | 38 | 71 |
| Integration Tests | 51 | 33 | 84 |
| E2E Tests | 16 | 19 | 35 |
| Playwright Tests | 40 | 50 | 90 |

---

*Document generated by SoftwareBuilderX v15.0.0*
*Build ID: sbx-20260222-012823*
*Phase: Planning*
