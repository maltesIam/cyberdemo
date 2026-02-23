# Test Plan: CyberDemo Agent Integration Enhancement
Version: 1.0.0 | Build Plan: docs/BUILD_PLAN.md | Build ID: sbx-20260222-012823

---

## TEST CONFIGURATION

| Parameter | Value |
|-----------|-------|
| Backend Test Framework | pytest 8.x |
| Frontend Test Framework | vitest 2.x |
| E2E Framework | Playwright 1.48+ |
| Coverage Target | 80% |
| CI Integration | GitHub Actions |

---

## UNIT TESTS

### EPIC-001: Agent Orchestration MCP (MTH)

| Test ID | Requirement | Description | File | Created | Passed |
|---------|-------------|-------------|------|---------|--------|
| UT-001 | REQ-001-001-001 | Test webhook configuration endpoint creates config | tests/unit/test_webhooks.py | [ ] | [ ] |
| UT-002 | REQ-001-001-002 | Test webhook dispatcher sends events correctly | tests/unit/test_webhooks.py | [ ] | [ ] |
| UT-003 | REQ-001-001-003 | Test retry logic with exponential backoff | tests/unit/test_webhooks.py | [ ] | [ ] |
| UT-004 | REQ-001-001-004 | Test configurable timeout handling | tests/unit/test_webhooks.py | [ ] | [ ] |
| UT-005 | REQ-001-001-005 | Test response validation for agent replies | tests/unit/test_webhooks.py | [ ] | [ ] |
| UT-006 | REQ-001-002-001 | Test queue analysis endpoint accepts jobs | tests/unit/test_analysis_queue.py | [ ] | [ ] |
| UT-007 | REQ-001-002-002 | Test job status endpoint returns correct status | tests/unit/test_analysis_queue.py | [ ] | [ ] |
| UT-008 | REQ-001-002-003 | Test job result endpoint returns analysis | tests/unit/test_analysis_queue.py | [ ] | [ ] |
| UT-009 | REQ-001-002-004 | Test WebSocket notifications for job updates | tests/unit/test_analysis_queue.py | [ ] | [ ] |
| UT-010 | REQ-001-002-005 | Test job persistence in PostgreSQL | tests/unit/test_analysis_queue.py | [ ] | [ ] |
| UT-011 | REQ-001-002-006 | Test job cleanup scheduler removes old jobs | tests/unit/test_analysis_queue.py | [ ] | [ ] |
| UT-012 | REQ-001-003-001 | Test agent_analyze_alert tool invocation | tests/unit/test_agent_tools.py | [ ] | [ ] |
| UT-013 | REQ-001-003-002 | Test agent_investigate_ioc tool invocation | tests/unit/test_agent_tools.py | [ ] | [ ] |
| UT-014 | REQ-001-003-003 | Test agent_recommend_action tool invocation | tests/unit/test_agent_tools.py | [ ] | [ ] |
| UT-015 | REQ-001-003-004 | Test agent_generate_report tool invocation | tests/unit/test_agent_tools.py | [ ] | [ ] |
| UT-016 | REQ-001-003-005 | Test agent_explain_decision tool invocation | tests/unit/test_agent_tools.py | [ ] | [ ] |
| UT-017 | REQ-001-003-006 | Test agent_correlate_events tool invocation | tests/unit/test_agent_tools.py | [ ] | [ ] |

### EPIC-002: Attack Simulation System (MTH)

| Test ID | Requirement | Description | File | Created | Passed |
|---------|-------------|-------------|------|---------|--------|
| UT-018 | REQ-002-001-001 | Test APT29 scenario generates correct events | tests/unit/test_attack_scenarios.py | [ ] | [ ] |
| UT-019 | REQ-002-001-002 | Test FIN7 scenario generates correct events | tests/unit/test_attack_scenarios.py | [ ] | [ ] |
| UT-020 | REQ-002-001-003 | Test Lazarus scenario generates correct events | tests/unit/test_attack_scenarios.py | [ ] | [ ] |
| UT-021 | REQ-002-001-004 | Test REvil scenario generates correct events | tests/unit/test_attack_scenarios.py | [ ] | [ ] |
| UT-022 | REQ-002-001-005 | Test SolarWinds scenario generates correct events | tests/unit/test_attack_scenarios.py | [ ] | [ ] |
| UT-023 | REQ-002-001-006 | Test Insider Threat scenario generates events | tests/unit/test_attack_scenarios.py | [ ] | [ ] |
| UT-024 | REQ-002-002-001 | Test attack_start_scenario tool starts simulation | tests/unit/test_simulation_control.py | [ ] | [ ] |
| UT-025 | REQ-002-002-002 | Test attack_pause and attack_resume tools | tests/unit/test_simulation_control.py | [ ] | [ ] |
| UT-026 | REQ-002-002-003 | Test attack_speed tool changes simulation speed | tests/unit/test_simulation_control.py | [ ] | [ ] |
| UT-027 | REQ-002-002-004 | Test attack_jump_to_stage tool navigates stages | tests/unit/test_simulation_control.py | [ ] | [ ] |
| UT-028 | REQ-002-002-005 | Test attack_inject_event tool injects events | tests/unit/test_simulation_control.py | [ ] | [ ] |
| UT-029 | REQ-002-002-006 | Test simulation state persistence in memory | tests/unit/test_simulation_control.py | [ ] | [ ] |
| UT-030 | REQ-002-003-001 | Test MITRE IDs present in scenario events | tests/unit/test_mitre_integration.py | [ ] | [ ] |
| UT-031 | REQ-002-003-002 | Test list tactics endpoint returns all tactics | tests/unit/test_mitre_integration.py | [ ] | [ ] |
| UT-032 | REQ-002-003-003 | Test get techniques endpoint by tactic | tests/unit/test_mitre_integration.py | [ ] | [ ] |
| UT-071 | REQ-002-003-004 | Test attack chain visualization component | frontend/src/__tests__/AttackChainVisualization.test.tsx | [ ] | [ ] |

### EPIC-003: Real-Time Narration (NTH)

| Test ID | Requirement | Description | File | Created | Passed |
|---------|-------------|-------------|------|---------|--------|
| UT-033 | REQ-003-001-001 | Test NarrationPanel component renders collapsed | frontend/src/__tests__/NarrationPanel.test.tsx | [ ] | [ ] |
| UT-034 | REQ-003-001-002 | Test message types (thinking/finding/decision) render | frontend/src/__tests__/NarrationPanel.test.tsx | [ ] | [ ] |
| UT-035 | REQ-003-001-003 | Test confidence indicator colors | frontend/src/__tests__/NarrationPanel.test.tsx | [ ] | [ ] |
| UT-036 | REQ-003-001-004 | Test auto-scroll on new messages | frontend/src/__tests__/NarrationPanel.test.tsx | [ ] | [ ] |
| UT-037 | REQ-003-001-005 | Test narration toggle functionality | frontend/src/__tests__/NarrationPanel.test.tsx | [ ] | [ ] |
| UT-038 | REQ-003-002-001 | Test WebSocket narration streaming | tests/unit/test_narration.py | [ ] | [ ] |
| UT-039 | REQ-003-002-002 | Test narration message format validation | tests/unit/test_narration.py | [ ] | [ ] |
| UT-040 | REQ-003-002-003 | Test 100-message buffer limit | tests/unit/test_narration.py | [ ] | [ ] |
| UT-041 | REQ-003-002-004 | Test narration history endpoint | tests/unit/test_narration.py | [ ] | [ ] |

### EPIC-004: Copilot Mode (NTH)

| Test ID | Requirement | Description | File | Created | Passed |
|---------|-------------|-------------|------|---------|--------|
| UT-042 | REQ-004-001-001 | Test action capture React hooks | frontend/src/__tests__/useCopilotActions.test.tsx | [ ] | [ ] |
| UT-043 | REQ-004-001-002 | Test event throttling max 10/sec | frontend/src/__tests__/useCopilotActions.test.tsx | [ ] | [ ] |
| UT-044 | REQ-004-001-003 | Test action context schema validation | tests/unit/test_copilot.py | [ ] | [ ] |
| UT-045 | REQ-004-001-004 | Test copilot WebSocket connection | tests/unit/test_copilot.py | [ ] | [ ] |
| UT-046 | REQ-004-002-001 | Test copilot_get_suggestion tool | tests/unit/test_copilot_tools.py | [ ] | [ ] |
| UT-047 | REQ-004-002-002 | Test copilot_explain_why tool | tests/unit/test_copilot_tools.py | [ ] | [ ] |
| UT-048 | REQ-004-002-003 | Test copilot_auto_complete tool | tests/unit/test_copilot_tools.py | [ ] | [ ] |
| UT-049 | REQ-004-002-004 | Test CopilotWidget component renders | frontend/src/__tests__/CopilotWidget.test.tsx | [ ] | [ ] |
| UT-050 | REQ-004-002-005 | Test acceptance/rejection tracking | tests/unit/test_copilot_tools.py | [ ] | [ ] |

### EPIC-005: Automated Playbooks (NTH)

| Test ID | Requirement | Description | File | Created | Passed |
|---------|-------------|-------------|------|---------|--------|
| UT-051 | REQ-005-001-001 | Test playbook execute endpoint | tests/unit/test_playbooks.py | [ ] | [ ] |
| UT-052 | REQ-005-001-002 | Test playbook pause endpoint | tests/unit/test_playbooks.py | [ ] | [ ] |
| UT-053 | REQ-005-001-003 | Test playbook resume endpoint | tests/unit/test_playbooks.py | [ ] | [ ] |
| UT-054 | REQ-005-001-004 | Test playbook rollback endpoint | tests/unit/test_playbooks.py | [ ] | [ ] |
| UT-055 | REQ-005-001-005 | Test playbook status endpoint | tests/unit/test_playbooks.py | [ ] | [ ] |
| UT-056 | REQ-005-001-006 | Test playbook state persistence | tests/unit/test_playbooks.py | [ ] | [ ] |
| UT-057 | REQ-005-002-001 | Test Ransomware Response playbook | tests/unit/test_playbook_definitions.py | [ ] | [ ] |
| UT-058 | REQ-005-002-002 | Test Phishing Investigation playbook | tests/unit/test_playbook_definitions.py | [ ] | [ ] |
| UT-059 | REQ-005-002-003 | Test Lateral Movement Detection playbook | tests/unit/test_playbook_definitions.py | [ ] | [ ] |
| UT-060 | REQ-005-002-004 | Test Data Exfiltration Response playbook | tests/unit/test_playbook_definitions.py | [ ] | [ ] |
| UT-061 | REQ-005-002-005 | Test Insider Threat Investigation playbook | tests/unit/test_playbook_definitions.py | [ ] | [ ] |
| UT-062 | REQ-005-002-006 | Test Cloud Compromise Response playbook | tests/unit/test_playbook_definitions.py | [ ] | [ ] |

### EPIC-006: Demo Control Panel (NTH)

| Test ID | Requirement | Description | File | Created | Passed |
|---------|-------------|-------------|------|---------|--------|
| UT-063 | REQ-006-001-001 | Test Play/Pause/Stop buttons render and work | frontend/src/__tests__/DemoControlPanel.test.tsx | [ ] | [ ] |
| UT-064 | REQ-006-001-002 | Test speed slider 0.5x-4x range | frontend/src/__tests__/DemoControlPanel.test.tsx | [ ] | [ ] |
| UT-065 | REQ-006-001-003 | Test scenario dropdown selection | frontend/src/__tests__/DemoControlPanel.test.tsx | [ ] | [ ] |
| UT-066 | REQ-006-001-004 | Test MITRE progress bar updates | frontend/src/__tests__/DemoControlPanel.test.tsx | [ ] | [ ] |
| UT-067 | REQ-006-001-005 | Test keyboard shortcuts (Space, +/-) | frontend/src/__tests__/DemoControlPanel.test.tsx | [ ] | [ ] |
| UT-068 | REQ-006-002-001 | Test DemoContext provides global state | frontend/src/__tests__/DemoContext.test.tsx | [ ] | [ ] |
| UT-069 | REQ-006-002-002 | Test localStorage persistence on reload | frontend/src/__tests__/DemoContext.test.tsx | [ ] | [ ] |
| UT-070 | REQ-006-002-003 | Test MCP Frontend Server sync | frontend/src/__tests__/DemoContext.test.tsx | [ ] | [ ] |

---

## INTEGRATION TESTS

### Webhook System Integration (FEAT-001-001)

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| IT-001 | Register webhook with valid URL and verify persistence | tests/integration/test_webhook_integration.py | [ ] | [ ] |
| IT-002 | Register webhook with invalid URL returns error | tests/integration/test_webhook_integration.py | [ ] | [ ] |
| IT-003 | Dispatch event to webhook endpoint and receive acknowledgment | tests/integration/test_webhook_integration.py | [ ] | [ ] |
| IT-004 | Webhook retry with exponential backoff on failure | tests/integration/test_webhook_integration.py | [ ] | [ ] |
| IT-005 | Webhook timeout handling after 30 seconds | tests/integration/test_webhook_integration.py | [ ] | [ ] |
| IT-006 | Multiple webhooks triggered simultaneously | tests/integration/test_webhook_integration.py | [ ] | [ ] |
| IT-007 | HMAC signature validation for webhook security | tests/integration/test_webhook_integration.py | [ ] | [ ] |
| IT-008 | Delete webhook and verify removal | tests/integration/test_webhook_integration.py | [ ] | [ ] |

### Analysis Queue Integration (FEAT-001-002)

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| IT-009 | Queue analysis job and receive job_id | tests/integration/test_analysis_queue_integration.py | [ ] | [ ] |
| IT-010 | Check job status transitions: pending → processing → completed | tests/integration/test_analysis_queue_integration.py | [ ] | [ ] |
| IT-011 | Get job result after completion | tests/integration/test_analysis_queue_integration.py | [ ] | [ ] |
| IT-012 | WebSocket notification on job status change | tests/integration/test_analysis_queue_integration.py | [ ] | [ ] |
| IT-013 | Job persistence survives server restart | tests/integration/test_analysis_queue_integration.py | [ ] | [ ] |
| IT-014 | Job cleanup removes jobs older than 24h | tests/integration/test_analysis_queue_integration.py | [ ] | [ ] |
| IT-015 | Rate limiting returns 429 after 100 req/min | tests/integration/test_analysis_queue_integration.py | [ ] | [ ] |
| IT-016 | Concurrent job processing (up to 10 jobs) | tests/integration/test_analysis_queue_integration.py | [ ] | [ ] |

### Agent Orchestration Tools Integration (FEAT-001-003)

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| IT-017 | agent_analyze_alert with valid alert returns analysis | tests/integration/test_agent_tools_integration.py | [ ] | [ ] |
| IT-018 | agent_analyze_alert with invalid alert returns error | tests/integration/test_agent_tools_integration.py | [ ] | [ ] |
| IT-019 | agent_investigate_ioc with IP address | tests/integration/test_agent_tools_integration.py | [ ] | [ ] |
| IT-020 | agent_investigate_ioc with domain | tests/integration/test_agent_tools_integration.py | [ ] | [ ] |
| IT-021 | agent_investigate_ioc with hash | tests/integration/test_agent_tools_integration.py | [ ] | [ ] |
| IT-022 | agent_recommend_action returns actionable recommendations | tests/integration/test_agent_tools_integration.py | [ ] | [ ] |
| IT-023 | agent_generate_report creates PDF format | tests/integration/test_agent_tools_integration.py | [ ] | [ ] |
| IT-024 | agent_generate_report creates JSON format | tests/integration/test_agent_tools_integration.py | [ ] | [ ] |
| IT-025 | agent_explain_decision returns reasoning chain | tests/integration/test_agent_tools_integration.py | [ ] | [ ] |
| IT-026 | agent_correlate_events with multiple event IDs | tests/integration/test_agent_tools_integration.py | [ ] | [ ] |
| IT-027 | All 6 tools audit logging verified | tests/integration/test_agent_tools_integration.py | [ ] | [ ] |

### Attack Scenarios Integration (FEAT-002-001)

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| IT-028 | APT29 scenario generates all expected event types | tests/integration/test_attack_scenarios_integration.py | [ ] | [ ] |
| IT-029 | FIN7 scenario follows MITRE ATT&CK chain | tests/integration/test_attack_scenarios_integration.py | [ ] | [ ] |
| IT-030 | Lazarus scenario events indexed in OpenSearch | tests/integration/test_attack_scenarios_integration.py | [ ] | [ ] |
| IT-031 | REvil scenario generates ransomware indicators | tests/integration/test_attack_scenarios_integration.py | [ ] | [ ] |
| IT-032 | SolarWinds scenario simulates supply chain attack | tests/integration/test_attack_scenarios_integration.py | [ ] | [ ] |
| IT-033 | Insider Threat scenario simulates data exfiltration | tests/integration/test_attack_scenarios_integration.py | [ ] | [ ] |
| IT-034 | Scenario reproducibility with same seed | tests/integration/test_attack_scenarios_integration.py | [ ] | [ ] |
| IT-035 | Events contain valid MITRE tactic_id and technique_id | tests/integration/test_attack_scenarios_integration.py | [ ] | [ ] |

### Simulation Control Integration (FEAT-002-002)

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| IT-036 | attack_start_scenario initiates event generation | tests/integration/test_simulation_integration.py | [ ] | [ ] |
| IT-037 | attack_pause stops event generation | tests/integration/test_simulation_integration.py | [ ] | [ ] |
| IT-038 | attack_resume continues from paused state | tests/integration/test_simulation_integration.py | [ ] | [ ] |
| IT-039 | attack_speed at 0.5x slows event rate by half | tests/integration/test_simulation_integration.py | [ ] | [ ] |
| IT-040 | attack_speed at 4x accelerates event rate | tests/integration/test_simulation_integration.py | [ ] | [ ] |
| IT-041 | attack_jump_to_stage skips to specified MITRE stage | tests/integration/test_simulation_integration.py | [ ] | [ ] |
| IT-042 | attack_inject_event adds custom event to simulation | tests/integration/test_simulation_integration.py | [ ] | [ ] |
| IT-043 | Simulation state persists across API calls | tests/integration/test_simulation_integration.py | [ ] | [ ] |

### MITRE ATT&CK Integration (FEAT-002-003)

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| IT-044 | GET /api/v1/mitre/tactics returns all 14 tactics | tests/integration/test_mitre_integration.py | [ ] | [ ] |
| IT-045 | GET /api/v1/mitre/techniques/{tactic_id} returns techniques | tests/integration/test_mitre_integration.py | [ ] | [ ] |
| IT-046 | Attack chain visualization data matches scenario events | tests/integration/test_mitre_integration.py | [ ] | [ ] |
| IT-047 | MITRE data cached and refreshed appropriately | tests/integration/test_mitre_integration.py | [ ] | [ ] |

### Narration System Integration (EPIC-003)

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| IT-048 | WebSocket /ws/narration establishes connection | tests/integration/test_narration_integration.py | [ ] | [ ] |
| IT-049 | Narration messages stream during agent analysis | tests/integration/test_narration_integration.py | [ ] | [ ] |
| IT-050 | Message types (thinking/finding/decision) correctly categorized | tests/integration/test_narration_integration.py | [ ] | [ ] |
| IT-051 | Confidence levels (high/medium/low) included in messages | tests/integration/test_narration_integration.py | [ ] | [ ] |
| IT-052 | 100-message buffer maintains latest messages only | tests/integration/test_narration_integration.py | [ ] | [ ] |
| IT-053 | GET /api/v1/narration/history returns session history | tests/integration/test_narration_integration.py | [ ] | [ ] |
| IT-054 | Narration messages persisted in OpenSearch index | tests/integration/test_narration_integration.py | [ ] | [ ] |

### Copilot System Integration (EPIC-004)

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| IT-055 | WebSocket /ws/copilot/actions receives user actions | tests/integration/test_copilot_integration.py | [ ] | [ ] |
| IT-056 | Action throttling limits to 10 events/second | tests/integration/test_copilot_integration.py | [ ] | [ ] |
| IT-057 | copilot_get_suggestion returns contextual suggestions | tests/integration/test_copilot_integration.py | [ ] | [ ] |
| IT-058 | copilot_explain_why provides reasoning for suggestion | tests/integration/test_copilot_integration.py | [ ] | [ ] |
| IT-059 | copilot_auto_complete suggests completion actions | tests/integration/test_copilot_integration.py | [ ] | [ ] |
| IT-060 | Suggestion acceptance tracking persists per session | tests/integration/test_copilot_integration.py | [ ] | [ ] |
| IT-061 | Suggestion latency under 2 seconds | tests/integration/test_copilot_integration.py | [ ] | [ ] |

### Playbook Engine Integration (EPIC-005)

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| IT-062 | POST /api/v1/playbooks/execute starts playbook | tests/integration/test_playbook_integration.py | [ ] | [ ] |
| IT-063 | Playbook pauses at approval points | tests/integration/test_playbook_integration.py | [ ] | [ ] |
| IT-064 | POST /api/v1/playbooks/{id}/resume continues execution | tests/integration/test_playbook_integration.py | [ ] | [ ] |
| IT-065 | POST /api/v1/playbooks/{id}/rollback reverts actions | tests/integration/test_playbook_integration.py | [ ] | [ ] |
| IT-066 | GET /api/v1/playbooks/{id}/status returns current step | tests/integration/test_playbook_integration.py | [ ] | [ ] |
| IT-067 | Playbook state persists in PostgreSQL | tests/integration/test_playbook_integration.py | [ ] | [ ] |
| IT-068 | Ransomware Response playbook executes all steps | tests/integration/test_playbook_integration.py | [ ] | [ ] |
| IT-069 | Phishing Investigation playbook with agent interaction | tests/integration/test_playbook_integration.py | [ ] | [ ] |
| IT-070 | Playbook audit trail complete in logs | tests/integration/test_playbook_integration.py | [ ] | [ ] |

### Demo Control Panel Integration (EPIC-006)

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| IT-071 | DemoContext state syncs with MCP Frontend Server | tests/integration/test_demo_control_integration.py | [ ] | [ ] |
| IT-072 | Play/Pause state changes reflected in simulation | tests/integration/test_demo_control_integration.py | [ ] | [ ] |
| IT-073 | Speed changes propagate to event generation | tests/integration/test_demo_control_integration.py | [ ] | [ ] |
| IT-074 | Scenario selection loads correct attack pattern | tests/integration/test_demo_control_integration.py | [ ] | [ ] |
| IT-075 | MITRE progress bar updates match simulation stage | tests/integration/test_demo_control_integration.py | [ ] | [ ] |
| IT-076 | State persists in localStorage across page reload | tests/integration/test_demo_control_integration.py | [ ] | [ ] |

### Cross-System Integration

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| IT-077 | Attack scenario triggers webhook to agent | tests/integration/test_cross_system_integration.py | [ ] | [ ] |
| IT-078 | Agent analysis generates narration messages | tests/integration/test_cross_system_integration.py | [ ] | [ ] |
| IT-079 | Copilot suggestions based on attack events | tests/integration/test_cross_system_integration.py | [ ] | [ ] |
| IT-080 | Playbook triggered by attack detection | tests/integration/test_cross_system_integration.py | [ ] | [ ] |
| IT-081 | Full flow: attack → detection → agent → playbook | tests/integration/test_cross_system_integration.py | [ ] | [ ] |
| IT-082 | Database transactions maintain consistency | tests/integration/test_cross_system_integration.py | [ ] | [ ] |
| IT-083 | OpenSearch indices properly populated by all systems | tests/integration/test_cross_system_integration.py | [ ] | [ ] |
| IT-084 | WebSocket connections handle concurrent users (10+) | tests/integration/test_cross_system_integration.py | [ ] | [ ] |

---

## E2E TESTS

### Agent Invocation E2E (EPIC-001)

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| E2E-001 | Full flow: alert → webhook → agent analysis → result display | tests/e2e/test_agent_invocation_flow.py | [ ] | [ ] |
| E2E-002 | Queue analysis, wait for completion, verify result | tests/e2e/test_agent_invocation_flow.py | [ ] | [ ] |
| E2E-003 | Multiple concurrent analyses complete successfully | tests/e2e/test_agent_invocation_flow.py | [ ] | [ ] |
| E2E-004 | Webhook failure handling and retry visible in UI | tests/e2e/test_agent_invocation_flow.py | [ ] | [ ] |

### Attack Simulation E2E (EPIC-002)

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| E2E-005 | Select APT29, start, observe events in dashboard | tests/e2e/test_attack_simulation_flow.py | [ ] | [ ] |
| E2E-006 | Pause mid-attack, verify event generation stops | tests/e2e/test_attack_simulation_flow.py | [ ] | [ ] |
| E2E-007 | Change speed to 4x, verify accelerated events | tests/e2e/test_attack_simulation_flow.py | [ ] | [ ] |
| E2E-008 | Jump to exfiltration stage, verify stage change | tests/e2e/test_attack_simulation_flow.py | [ ] | [ ] |
| E2E-009 | Full attack scenario completion with all stages | tests/e2e/test_attack_simulation_flow.py | [ ] | [ ] |
| E2E-010 | Attack chain visualization shows MITRE progress | tests/e2e/test_attack_simulation_flow.py | [ ] | [ ] |

### Combined Attack + Agent E2E

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| E2E-011 | Attack event triggers automatic agent analysis | tests/e2e/test_combined_attack_agent.py | [ ] | [ ] |
| E2E-012 | Agent recommends containment during attack | tests/e2e/test_combined_attack_agent.py | [ ] | [ ] |
| E2E-013 | Correlation of multiple attack events by agent | tests/e2e/test_combined_attack_agent.py | [ ] | [ ] |

### Narration E2E (EPIC-003)

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| E2E-014 | Narration panel shows messages during analysis | tests/e2e/test_narration_flow.py | [ ] | [ ] |
| E2E-015 | Toggle narration on/off preserves history | tests/e2e/test_narration_flow.py | [ ] | [ ] |
| E2E-016 | Confidence colors display correctly (green/yellow/red) | tests/e2e/test_narration_flow.py | [ ] | [ ] |
| E2E-017 | Auto-scroll to latest narration message | tests/e2e/test_narration_flow.py | [ ] | [ ] |

### Copilot E2E (EPIC-004)

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| E2E-018 | User action generates copilot suggestion | tests/e2e/test_copilot_flow.py | [ ] | [ ] |
| E2E-019 | Accept suggestion, verify action executed | tests/e2e/test_copilot_flow.py | [ ] | [ ] |
| E2E-020 | Reject suggestion, verify tracking updated | tests/e2e/test_copilot_flow.py | [ ] | [ ] |
| E2E-021 | Explain button shows reasoning for suggestion | tests/e2e/test_copilot_flow.py | [ ] | [ ] |

### Playbook E2E (EPIC-005)

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| E2E-022 | Execute Ransomware Response playbook end-to-end | tests/e2e/test_playbook_flow.py | [ ] | [ ] |
| E2E-023 | Playbook pauses at approval point, user approves | tests/e2e/test_playbook_flow.py | [ ] | [ ] |
| E2E-024 | Playbook rollback reverts visible changes | tests/e2e/test_playbook_flow.py | [ ] | [ ] |
| E2E-025 | Playbook status visible throughout execution | tests/e2e/test_playbook_flow.py | [ ] | [ ] |

### Demo Control E2E (EPIC-006)

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| E2E-026 | Play/Pause controls affect simulation in real-time | tests/e2e/test_demo_control_flow.py | [ ] | [ ] |
| E2E-027 | Speed slider changes visible in event rate | tests/e2e/test_demo_control_flow.py | [ ] | [ ] |
| E2E-028 | Keyboard shortcuts (Space, +/-) work correctly | tests/e2e/test_demo_control_flow.py | [ ] | [ ] |
| E2E-029 | Progress bar reflects current attack stage | tests/e2e/test_demo_control_flow.py | [ ] | [ ] |

### Full System E2E

| Test ID | Description | File | Created | Passed |
|---------|-------------|------|---------|--------|
| E2E-030 | MTH cycle: all core features working together | tests/e2e/test_mth_complete.py | [ ] | [ ] |
| E2E-031 | NTH cycle: all enhanced features working | tests/e2e/test_nth_complete.py | [ ] | [ ] |
| E2E-032 | Full demo: presenter controls attack, agent assists | tests/e2e/test_full_demo.py | [ ] | [ ] |
| E2E-033 | 10 concurrent users simulating SOC activity | tests/e2e/test_full_demo.py | [ ] | [ ] |
| E2E-034 | Session persistence across browser refresh | tests/e2e/test_full_demo.py | [ ] | [ ] |
| E2E-035 | Error recovery: server restart during simulation | tests/e2e/test_full_demo.py | [ ] | [ ] |

---

## PLAYWRIGHT E2E TESTS

### Webhook Configuration UI (EPIC-001)

| Test ID | User Flow | Description | File | Created | Passed |
|---------|-----------|-------------|------|---------|--------|
| PW-001 | Webhook Config | Open webhook config page, page loads correctly | frontend/e2e/webhook-config.spec.ts | [ ] | [ ] |
| PW-002 | Webhook Config | Add new webhook with valid URL | frontend/e2e/webhook-config.spec.ts | [ ] | [ ] |
| PW-003 | Webhook Config | Edit existing webhook URL | frontend/e2e/webhook-config.spec.ts | [ ] | [ ] |
| PW-004 | Webhook Config | Delete webhook with confirmation dialog | frontend/e2e/webhook-config.spec.ts | [ ] | [ ] |
| PW-005 | Webhook Config | Test webhook button triggers test event | frontend/e2e/webhook-config.spec.ts | [ ] | [ ] |
| PW-006 | Webhook Config | Validation error on invalid URL | frontend/e2e/webhook-config.spec.ts | [ ] | [ ] |

### Analysis Queue UI (EPIC-001)

| Test ID | User Flow | Description | File | Created | Passed |
|---------|-----------|-------------|------|---------|--------|
| PW-007 | Analysis Queue | View pending analysis jobs list | frontend/e2e/analysis-queue.spec.ts | [ ] | [ ] |
| PW-008 | Analysis Queue | Queue new analysis from alert detail | frontend/e2e/analysis-queue.spec.ts | [ ] | [ ] |
| PW-009 | Analysis Queue | Job status updates in real-time | frontend/e2e/analysis-queue.spec.ts | [ ] | [ ] |
| PW-010 | Analysis Queue | View completed analysis result | frontend/e2e/analysis-queue.spec.ts | [ ] | [ ] |
| PW-011 | Analysis Queue | Cancel pending analysis job | frontend/e2e/analysis-queue.spec.ts | [ ] | [ ] |

### Attack Scenario UI (EPIC-002)

| Test ID | User Flow | Description | File | Created | Passed |
|---------|-----------|-------------|------|---------|--------|
| PW-012 | Attack Scenario | Scenario selection dropdown shows all 6 scenarios | frontend/e2e/attack-scenario.spec.ts | [ ] | [ ] |
| PW-013 | Attack Scenario | Select APT29 scenario, verify description shown | frontend/e2e/attack-scenario.spec.ts | [ ] | [ ] |
| PW-014 | Attack Scenario | Start scenario button initiates simulation | frontend/e2e/attack-scenario.spec.ts | [ ] | [ ] |
| PW-015 | Attack Scenario | Events appear in dashboard after start | frontend/e2e/attack-scenario.spec.ts | [ ] | [ ] |
| PW-016 | Attack Scenario | MITRE ATT&CK chain visualization updates | frontend/e2e/attack-scenario.spec.ts | [ ] | [ ] |
| PW-017 | Attack Scenario | Scenario info panel shows attack details | frontend/e2e/attack-scenario.spec.ts | [ ] | [ ] |

### Simulation Control UI (EPIC-002)

| Test ID | User Flow | Description | File | Created | Passed |
|---------|-----------|-------------|------|---------|--------|
| PW-018 | Simulation Control | Play button starts paused simulation | frontend/e2e/simulation-control.spec.ts | [ ] | [ ] |
| PW-019 | Simulation Control | Pause button stops event generation | frontend/e2e/simulation-control.spec.ts | [ ] | [ ] |
| PW-020 | Simulation Control | Stop button ends simulation completely | frontend/e2e/simulation-control.spec.ts | [ ] | [ ] |
| PW-021 | Simulation Control | Speed slider at 0.5x slows events | frontend/e2e/simulation-control.spec.ts | [ ] | [ ] |
| PW-022 | Simulation Control | Speed slider at 4x accelerates events | frontend/e2e/simulation-control.spec.ts | [ ] | [ ] |
| PW-023 | Simulation Control | Stage jump dropdown navigates MITRE stages | frontend/e2e/simulation-control.spec.ts | [ ] | [ ] |
| PW-024 | Simulation Control | Inject event modal allows custom event | frontend/e2e/simulation-control.spec.ts | [ ] | [ ] |

### Narration Panel UI (EPIC-003)

| Test ID | User Flow | Description | File | Created | Passed |
|---------|-----------|-------------|------|---------|--------|
| PW-025 | Narration Panel | Panel opens from sidebar toggle | frontend/e2e/narration-panel.spec.ts | [ ] | [ ] |
| PW-026 | Narration Panel | Panel collapses/expands correctly | frontend/e2e/narration-panel.spec.ts | [ ] | [ ] |
| PW-027 | Narration Panel | Messages stream in during analysis | frontend/e2e/narration-panel.spec.ts | [ ] | [ ] |
| PW-028 | Narration Panel | Thinking messages show brain icon | frontend/e2e/narration-panel.spec.ts | [ ] | [ ] |
| PW-029 | Narration Panel | Finding messages show magnifier icon | frontend/e2e/narration-panel.spec.ts | [ ] | [ ] |
| PW-030 | Narration Panel | Decision messages show checkmark icon | frontend/e2e/narration-panel.spec.ts | [ ] | [ ] |
| PW-031 | Narration Panel | High confidence shows green indicator | frontend/e2e/narration-panel.spec.ts | [ ] | [ ] |
| PW-032 | Narration Panel | Low confidence shows red indicator | frontend/e2e/narration-panel.spec.ts | [ ] | [ ] |
| PW-033 | Narration Panel | Auto-scroll keeps latest message visible | frontend/e2e/narration-panel.spec.ts | [ ] | [ ] |
| PW-034 | Narration Panel | Toggle off hides narration, preserves state | frontend/e2e/narration-panel.spec.ts | [ ] | [ ] |

### Copilot Widget UI (EPIC-004)

| Test ID | User Flow | Description | File | Created | Passed |
|---------|-----------|-------------|------|---------|--------|
| PW-035 | Copilot Widget | Widget appears in corner of dashboard | frontend/e2e/copilot-widget.spec.ts | [ ] | [ ] |
| PW-036 | Copilot Widget | Suggestion appears after user action | frontend/e2e/copilot-widget.spec.ts | [ ] | [ ] |
| PW-037 | Copilot Widget | Accept button executes suggestion | frontend/e2e/copilot-widget.spec.ts | [ ] | [ ] |
| PW-038 | Copilot Widget | Dismiss button hides suggestion | frontend/e2e/copilot-widget.spec.ts | [ ] | [ ] |
| PW-039 | Copilot Widget | "Why?" link shows explanation modal | frontend/e2e/copilot-widget.spec.ts | [ ] | [ ] |
| PW-040 | Copilot Widget | Suggestion timeout auto-dismisses | frontend/e2e/copilot-widget.spec.ts | [ ] | [ ] |
| PW-041 | Copilot Widget | Acceptance rate shown in stats | frontend/e2e/copilot-widget.spec.ts | [ ] | [ ] |

### Playbook Execution UI (EPIC-005)

| Test ID | User Flow | Description | File | Created | Passed |
|---------|-----------|-------------|------|---------|--------|
| PW-042 | Playbook | Playbook list shows all 6 playbooks | frontend/e2e/playbook.spec.ts | [ ] | [ ] |
| PW-043 | Playbook | Click playbook shows description and steps | frontend/e2e/playbook.spec.ts | [ ] | [ ] |
| PW-044 | Playbook | Execute button starts playbook | frontend/e2e/playbook.spec.ts | [ ] | [ ] |
| PW-045 | Playbook | Step progress indicator updates | frontend/e2e/playbook.spec.ts | [ ] | [ ] |
| PW-046 | Playbook | Approval modal appears at pause point | frontend/e2e/playbook.spec.ts | [ ] | [ ] |
| PW-047 | Playbook | Approve button continues execution | frontend/e2e/playbook.spec.ts | [ ] | [ ] |
| PW-048 | Playbook | Reject button pauses playbook | frontend/e2e/playbook.spec.ts | [ ] | [ ] |
| PW-049 | Playbook | Rollback button appears after completion | frontend/e2e/playbook.spec.ts | [ ] | [ ] |
| PW-050 | Playbook | Rollback reverts visible changes | frontend/e2e/playbook.spec.ts | [ ] | [ ] |

### Demo Control Panel UI (EPIC-006)

| Test ID | User Flow | Description | File | Created | Passed |
|---------|-----------|-------------|------|---------|--------|
| PW-051 | Demo Control | Control panel visible in demo mode | frontend/e2e/demo-control.spec.ts | [ ] | [ ] |
| PW-052 | Demo Control | Play button starts simulation | frontend/e2e/demo-control.spec.ts | [ ] | [ ] |
| PW-053 | Demo Control | Pause button stops simulation | frontend/e2e/demo-control.spec.ts | [ ] | [ ] |
| PW-054 | Demo Control | Space key toggles play/pause | frontend/e2e/demo-control.spec.ts | [ ] | [ ] |
| PW-055 | Demo Control | + key increases speed | frontend/e2e/demo-control.spec.ts | [ ] | [ ] |
| PW-056 | Demo Control | - key decreases speed | frontend/e2e/demo-control.spec.ts | [ ] | [ ] |
| PW-057 | Demo Control | Speed slider shows current value | frontend/e2e/demo-control.spec.ts | [ ] | [ ] |
| PW-058 | Demo Control | Scenario dropdown changes scenario | frontend/e2e/demo-control.spec.ts | [ ] | [ ] |
| PW-059 | Demo Control | MITRE progress bar shows stages | frontend/e2e/demo-control.spec.ts | [ ] | [ ] |
| PW-060 | Demo Control | Current stage highlighted in progress | frontend/e2e/demo-control.spec.ts | [ ] | [ ] |

### Dashboard Integration (Cross-Feature)

| Test ID | User Flow | Description | File | Created | Passed |
|---------|-----------|-------------|------|---------|--------|
| PW-061 | Dashboard | Dashboard loads with all widgets | frontend/e2e/dashboard.spec.ts | [ ] | [ ] |
| PW-062 | Dashboard | Events table updates during simulation | frontend/e2e/dashboard.spec.ts | [ ] | [ ] |
| PW-063 | Dashboard | Alert count increases with new alerts | frontend/e2e/dashboard.spec.ts | [ ] | [ ] |
| PW-064 | Dashboard | Click alert opens detail modal | frontend/e2e/dashboard.spec.ts | [ ] | [ ] |
| PW-065 | Dashboard | Analyze button triggers agent analysis | frontend/e2e/dashboard.spec.ts | [ ] | [ ] |
| PW-066 | Dashboard | MITRE attack chain shows active techniques | frontend/e2e/dashboard.spec.ts | [ ] | [ ] |

### Graph Visualization (Cross-Feature)

| Test ID | User Flow | Description | File | Created | Passed |
|---------|-----------|-------------|------|---------|--------|
| PW-067 | Graph | Graph page loads with nodes | frontend/e2e/graph.spec.ts | [ ] | [ ] |
| PW-068 | Graph | Nodes update during attack simulation | frontend/e2e/graph.spec.ts | [ ] | [ ] |
| PW-069 | Graph | Click node shows entity details | frontend/e2e/graph.spec.ts | [ ] | [ ] |
| PW-070 | Graph | Zoom controls work correctly | frontend/e2e/graph.spec.ts | [ ] | [ ] |
| PW-071 | Graph | Filter by entity type works | frontend/e2e/graph.spec.ts | [ ] | [ ] |

### Responsive Design

| Test ID | User Flow | Description | File | Created | Passed |
|---------|-----------|-------------|------|---------|--------|
| PW-072 | Responsive | Dashboard renders on mobile (375px) | frontend/e2e/responsive.spec.ts | [ ] | [ ] |
| PW-073 | Responsive | Dashboard renders on tablet (768px) | frontend/e2e/responsive.spec.ts | [ ] | [ ] |
| PW-074 | Responsive | Demo controls accessible on tablet | frontend/e2e/responsive.spec.ts | [ ] | [ ] |
| PW-075 | Responsive | Narration panel mobile-friendly | frontend/e2e/responsive.spec.ts | [ ] | [ ] |

### WebSocket Connections

| Test ID | User Flow | Description | File | Created | Passed |
|---------|-----------|-------------|------|---------|--------|
| PW-076 | WebSocket | Connection indicator shows connected | frontend/e2e/websocket.spec.ts | [ ] | [ ] |
| PW-077 | WebSocket | Reconnect after disconnect | frontend/e2e/websocket.spec.ts | [ ] | [ ] |
| PW-078 | WebSocket | Real-time events appear without refresh | frontend/e2e/websocket.spec.ts | [ ] | [ ] |
| PW-079 | WebSocket | Multiple tabs share connection state | frontend/e2e/websocket.spec.ts | [ ] | [ ] |

### State Persistence

| Test ID | User Flow | Description | File | Created | Passed |
|---------|-----------|-------------|------|---------|--------|
| PW-080 | Persistence | Demo state persists on page refresh | frontend/e2e/persistence.spec.ts | [ ] | [ ] |
| PW-081 | Persistence | Narration history preserved on refresh | frontend/e2e/persistence.spec.ts | [ ] | [ ] |
| PW-082 | Persistence | Copilot stats persist per session | frontend/e2e/persistence.spec.ts | [ ] | [ ] |
| PW-083 | Persistence | User preferences saved in localStorage | frontend/e2e/persistence.spec.ts | [ ] | [ ] |

### Error Handling

| Test ID | User Flow | Description | File | Created | Passed |
|---------|-----------|-------------|------|---------|--------|
| PW-084 | Errors | API error shows user-friendly message | frontend/e2e/errors.spec.ts | [ ] | [ ] |
| PW-085 | Errors | Network error shows reconnecting state | frontend/e2e/errors.spec.ts | [ ] | [ ] |
| PW-086 | Errors | Invalid route redirects to 404 page | frontend/e2e/errors.spec.ts | [ ] | [ ] |
| PW-087 | Errors | Form validation errors display inline | frontend/e2e/errors.spec.ts | [ ] | [ ] |

### Accessibility

| Test ID | User Flow | Description | File | Created | Passed |
|---------|-----------|-------------|------|---------|--------|
| PW-088 | A11y | All interactive elements keyboard accessible | frontend/e2e/accessibility.spec.ts | [ ] | [ ] |
| PW-089 | A11y | Focus indicators visible | frontend/e2e/accessibility.spec.ts | [ ] | [ ] |
| PW-090 | A11y | Screen reader announces state changes | frontend/e2e/accessibility.spec.ts | [ ] | [ ] |

---

## COVERAGE VERIFICATION

### Requirements to Tests Mapping

| Requirement | UT | IT | E2E | PW | Complete |
|-------------|----|----|-----|----| ---------|
| REQ-001-001-001 | UT-001 | IT-001 | E2E-001 | PW-001 | [ ] |
| REQ-001-001-002 | UT-002 | IT-001 | E2E-001 | - | [ ] |
| REQ-001-001-003 | UT-003 | IT-001 | E2E-001 | - | [ ] |
| REQ-001-001-004 | UT-004 | IT-001 | E2E-001 | - | [ ] |
| REQ-001-001-005 | UT-005 | IT-001 | E2E-001 | - | [ ] |
| REQ-001-002-001 | UT-006 | IT-002 | E2E-001 | - | [ ] |
| REQ-001-002-002 | UT-007 | IT-002 | E2E-001 | - | [ ] |
| REQ-001-002-003 | UT-008 | IT-002 | E2E-001 | - | [ ] |
| REQ-001-002-004 | UT-009 | IT-002 | E2E-001 | - | [ ] |
| REQ-001-002-005 | UT-010 | IT-002 | E2E-001 | - | [ ] |
| REQ-001-002-006 | UT-011 | IT-002 | E2E-001 | - | [ ] |
| REQ-001-003-001 | UT-012 | IT-003 | E2E-001 | - | [ ] |
| REQ-001-003-002 | UT-013 | IT-003 | E2E-001 | - | [ ] |
| REQ-001-003-003 | UT-014 | IT-003 | E2E-001 | - | [ ] |
| REQ-001-003-004 | UT-015 | IT-003 | E2E-001 | - | [ ] |
| REQ-001-003-005 | UT-016 | IT-003 | E2E-001 | - | [ ] |
| REQ-001-003-006 | UT-017 | IT-003 | E2E-001 | - | [ ] |
| REQ-002-001-001 | UT-018 | IT-004 | E2E-002 | PW-002 | [ ] |
| REQ-002-001-002 | UT-019 | IT-004 | E2E-002 | PW-002 | [ ] |
| REQ-002-001-003 | UT-020 | IT-004 | E2E-002 | PW-002 | [ ] |
| REQ-002-001-004 | UT-021 | IT-004 | E2E-002 | PW-002 | [ ] |
| REQ-002-001-005 | UT-022 | IT-004 | E2E-002 | PW-002 | [ ] |
| REQ-002-001-006 | UT-023 | IT-004 | E2E-002 | PW-002 | [ ] |
| REQ-002-002-001 | UT-024 | IT-005 | E2E-002 | PW-002 | [ ] |
| REQ-002-002-002 | UT-025 | IT-005 | E2E-002 | PW-002 | [ ] |
| REQ-002-002-003 | UT-026 | IT-005 | E2E-002 | PW-002 | [ ] |
| REQ-002-002-004 | UT-027 | IT-005 | E2E-002 | PW-002 | [ ] |
| REQ-002-002-005 | UT-028 | IT-005 | E2E-002 | PW-002 | [ ] |
| REQ-002-002-006 | UT-029 | IT-005 | E2E-002 | - | [ ] |
| REQ-002-003-001 | UT-030 | IT-004 | E2E-002 | - | [ ] |
| REQ-002-003-002 | UT-031 | IT-004 | E2E-002 | - | [ ] |
| REQ-002-003-003 | UT-032 | IT-004 | E2E-002 | - | [ ] |
| REQ-002-003-004 | UT-071 | IT-004 | E2E-002 | PW-002 | [ ] |
| REQ-003-001-001 | UT-033 | IT-006 | E2E-004 | PW-003 | [ ] |
| REQ-003-001-002 | UT-034 | IT-006 | E2E-004 | PW-003 | [ ] |
| REQ-003-001-003 | UT-035 | IT-006 | E2E-004 | PW-003 | [ ] |
| REQ-003-001-004 | UT-036 | IT-006 | E2E-004 | PW-003 | [ ] |
| REQ-003-001-005 | UT-037 | IT-006 | E2E-004 | PW-003 | [ ] |
| REQ-003-002-001 | UT-038 | IT-006 | E2E-004 | - | [ ] |
| REQ-003-002-002 | UT-039 | IT-006 | E2E-004 | - | [ ] |
| REQ-003-002-003 | UT-040 | IT-006 | E2E-004 | - | [ ] |
| REQ-003-002-004 | UT-041 | IT-006 | E2E-004 | - | [ ] |
| REQ-004-001-001 | UT-042 | IT-007 | E2E-005 | PW-004 | [ ] |
| REQ-004-001-002 | UT-043 | IT-007 | E2E-005 | - | [ ] |
| REQ-004-001-003 | UT-044 | IT-007 | E2E-005 | - | [ ] |
| REQ-004-001-004 | UT-045 | IT-007 | E2E-005 | - | [ ] |
| REQ-004-002-001 | UT-046 | IT-007 | E2E-005 | PW-004 | [ ] |
| REQ-004-002-002 | UT-047 | IT-007 | E2E-005 | PW-004 | [ ] |
| REQ-004-002-003 | UT-048 | IT-007 | E2E-005 | PW-004 | [ ] |
| REQ-004-002-004 | UT-049 | IT-007 | E2E-005 | PW-004 | [ ] |
| REQ-004-002-005 | UT-050 | IT-007 | E2E-005 | PW-004 | [ ] |
| REQ-005-001-001 | UT-051 | IT-008 | E2E-006 | - | [ ] |
| REQ-005-001-002 | UT-052 | IT-008 | E2E-006 | - | [ ] |
| REQ-005-001-003 | UT-053 | IT-008 | E2E-006 | - | [ ] |
| REQ-005-001-004 | UT-054 | IT-008 | E2E-006 | - | [ ] |
| REQ-005-001-005 | UT-055 | IT-008 | E2E-006 | - | [ ] |
| REQ-005-001-006 | UT-056 | IT-008 | E2E-006 | - | [ ] |
| REQ-005-002-001 | UT-057 | IT-008 | E2E-006 | - | [ ] |
| REQ-005-002-002 | UT-058 | IT-008 | E2E-006 | - | [ ] |
| REQ-005-002-003 | UT-059 | IT-008 | E2E-006 | - | [ ] |
| REQ-005-002-004 | UT-060 | IT-008 | E2E-006 | - | [ ] |
| REQ-005-002-005 | UT-061 | IT-008 | E2E-006 | - | [ ] |
| REQ-005-002-006 | UT-062 | IT-008 | E2E-006 | - | [ ] |
| REQ-006-001-001 | UT-063 | IT-009 | E2E-007 | PW-005 | [ ] |
| REQ-006-001-002 | UT-064 | IT-009 | E2E-007 | PW-005 | [ ] |
| REQ-006-001-003 | UT-065 | IT-009 | E2E-007 | PW-005 | [ ] |
| REQ-006-001-004 | UT-066 | IT-009 | E2E-007 | PW-005 | [ ] |
| REQ-006-001-005 | UT-067 | IT-009 | E2E-007 | PW-005 | [ ] |
| REQ-006-002-001 | UT-068 | IT-009 | E2E-007 | - | [ ] |
| REQ-006-002-002 | UT-069 | IT-009 | E2E-007 | - | [ ] |
| REQ-006-002-003 | UT-070 | IT-009 | E2E-007 | - | [ ] |

---

## TEST SUMMARY

| Type | Total | MTH | NTH |
|------|-------|-----|-----|
| Unit Tests | 71 | 33 | 38 |
| Integration Tests | 84 | 51 | 33 |
| E2E Tests | 35 | 16 | 19 |
| Playwright Tests | 90 | 40 | 50 |
| **Total** | **280** | **140** | **140** |

---

## TEST EXECUTION COMMANDS

### Backend Tests (pytest)
```bash
# Unit tests
cd backend && pytest tests/unit/ -v --cov=src

# Integration tests
cd backend && pytest tests/integration/ -v

# E2E tests
cd backend && pytest tests/e2e/ -v
```

### Frontend Tests (vitest)
```bash
# Unit tests
cd frontend && npm run test

# Watch mode
cd frontend && npm run test:watch
```

### Playwright E2E Tests
```bash
# All Playwright tests
cd frontend && npx playwright test

# Specific test file
cd frontend && npx playwright test e2e/demo-control.spec.ts

# With UI
cd frontend && npx playwright test --ui
```

---

*Document generated by SoftwareBuilderX v15.0.0*
*Build ID: sbx-20260222-012823*
*Phase: Planning*
