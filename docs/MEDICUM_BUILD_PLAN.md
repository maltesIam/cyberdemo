# Build Plan: Medicum (CyberDemo Frontend Design System)

| Attribute | Value |
|-----------|-------|
| Build ID | sbx-20260225-132308 |
| Created | 2026-02-25 |
| Functional Spec | docs/MEDICUM_FUNCTIONAL_SPEC.md |
| Template Version | SBX v23.0.0 |

---

## Build Phases

### Cycle 1: MTH (Must-To-Have)

| Phase | Description | Tasks | Status |
|-------|-------------|-------|--------|
| P1 | Design Token Foundation | 14 tasks | Pending |
| P2 | Theme & Font Size Systems | 8 tasks | Pending |
| P3 | UI Component Library | 14 tasks | Pending |
| P4 | Page Migration - Core | 15 tasks | Pending |
| P5 | Specialized Components & NFRs | 3 tasks | Pending |

### Cycle 2: NTH (Nice-To-Have)

| Phase | Description | Tasks | Status |
|-------|-------------|-------|--------|
| P6 | NTH Features & Pages | 11 tasks | Pending |

---

## Task Assignments

### Build Agent Distribution

| Agent | Focus Area | Task Count |
|-------|------------|------------|
| Agent 1 | Design Tokens (EPIC-001) | 8 |
| Agent 2 | Theme System (EPIC-002) + Font Size (EPIC-003) | 6 |
| Agent 3 | UI Components - Buttons, Inputs, Cards (EPIC-004 part 1) | 7 |
| Agent 4 | UI Components - Nav, Tables, Badges, Modals (EPIC-004 part 2) | 7 |
| Agent 5 | Page Migration - Layout + Dashboard area (EPIC-005 part 1) | 7 |
| Agent 6 | Page Migration - Security area (EPIC-005 part 2) | 7 |
| Agent 7 | Page Migration - Advanced area (EPIC-005 part 3) | 7 |
| Agent 8 | Specialized Components (EPIC-006) + Integration | 5 |
| Agent 9 | TDD Verification Agent | - |
| Agent 10 | Review Agent | - |

---

## Detailed Task List

### Phase P1: Design Token Foundation

| Task ID | Requirement | Description | Agent | Priority | Status |
|---------|-------------|-------------|-------|----------|--------|
| T-TECH-001 | TECH-001 | Tailwind config for CSS variables | 1 | MTH | Pending |
| T-TECH-002 | TECH-002 | CSS file organization | 1 | MTH | Pending |
| T-001-001 | REQ-001-001-001 | Color scale tokens | 1 | MTH | Pending |
| T-001-002 | REQ-001-001-002 | Typography tokens | 1 | MTH | Pending |
| T-001-003 | REQ-001-001-003 | Spacing and layout tokens | 1 | MTH | Pending |
| T-001-004 | REQ-001-001-004 | Shadow and elevation tokens | 1 | MTH | Pending |
| T-001-005 | REQ-001-001-005 | Transition and motion tokens | 1 | MTH | Pending |
| T-TECH-005 | TECH-005 | Font loading strategy | 1 | MTH | Pending |
| T-TECH-006 | TECH-006 | CSS animation definitions | 1 | MTH | Pending |
| T-INT-001 | INT-001 | Google Fonts integration | 1 | MTH | Pending |
| T-001-006 | REQ-001-002-001 | Dark theme tokens | 2 | MTH | Pending |
| T-001-007 | REQ-001-002-002 | Light theme tokens | 2 | MTH | Pending |
| T-001-008 | REQ-001-002-003 | Z-index scale | 2 | MTH | Pending |
| T-INT-002 | INT-002 | Lucide Icons integration | 2 | MTH | Pending |

### Phase P2: Theme & Font Size Systems

| Task ID | Requirement | Description | Agent | Priority | Status |
|---------|-------------|-------------|-------|----------|--------|
| T-TECH-003 | TECH-003 | React context provider (ThemeProvider + FontSizeProvider) | 2 | MTH | Pending |
| T-002-001 | REQ-002-001-001 | useTheme hook | 2 | MTH | Pending |
| T-002-002 | REQ-002-001-002 | FOUC prevention | 2 | MTH | Pending |
| T-DATA-001 | DATA-001 | LocalStorage theme preference | 2 | MTH | Pending |
| T-002-003 | REQ-002-002-001 | ThemeToggle UI component | 3 | MTH | Pending |
| T-002-004 | REQ-002-002-002 | Theme toggle placement | 3 | MTH | Pending |
| T-003-001 | REQ-003-001-001 | useFontSize hook | 3 | MTH | Pending |
| T-DATA-002 | DATA-002 | LocalStorage font size preference | 3 | MTH | Pending |

### Phase P3: UI Component Library

| Task ID | Requirement | Description | Agent | Priority | Status |
|---------|-------------|-------------|-------|----------|--------|
| T-003-002 | REQ-003-002-001 | FontSizeButton UI component | 3 | MTH | Pending |
| T-004-001 | REQ-004-001-001 | Button variants | 3 | MTH | Pending |
| T-004-002 | REQ-004-001-002 | Button sizes | 3 | MTH | Pending |
| T-004-003 | REQ-004-002-001 | Text input styling | 3 | MTH | Pending |
| T-004-004 | REQ-004-003-001 | Base card styling | 4 | MTH | Pending |
| T-004-005 | REQ-004-003-002 | Metric card component | 4 | MTH | Pending |
| T-004-006 | REQ-004-004-001 | Sidebar navigation styling | 4 | MTH | Pending |
| T-004-007 | REQ-004-004-002 | Tabs component styling | 4 | MTH | Pending |
| T-004-008 | REQ-004-005-001 | Table styling | 4 | MTH | Pending |
| T-004-009 | REQ-004-006-001 | Badge variants | 4 | MTH | Pending |
| T-004-010 | REQ-004-007-001 | Modal overlay and container | 4 | MTH | Pending |
| T-TECH-004 | TECH-004 | Hardcoded color cleanup | 4 | MTH | Pending |
| T-NFR-002 | NFR-002 | WCAG 2.2 AA color contrast | 3 | MTH | Pending |
| T-NFR-003 | NFR-003 | Keyboard navigation all elements | 3 | MTH | Pending |

### Phase P4: Page Migration - Core

| Task ID | Requirement | Description | Agent | Priority | Status |
|---------|-------------|-------------|-------|----------|--------|
| T-005-001 | REQ-005-001-001 | Layout.tsx migration | 5 | MTH | Pending |
| T-005-002 | REQ-005-001-002 | Sidebar.tsx migration | 5 | MTH | Pending |
| T-005-003 | REQ-005-002-001 | DashboardPage migration | 5 | MTH | Pending |
| T-005-004 | REQ-005-002-002 | SurfacePage migration | 5 | MTH | Pending |
| T-005-005 | REQ-005-002-003 | GenerationPage migration | 5 | MTH | Pending |
| T-005-006 | REQ-005-003-001 | IncidentsPage migration | 6 | MTH | Pending |
| T-005-007 | REQ-005-003-002 | DetectionsPage migration | 6 | MTH | Pending |
| T-005-008 | REQ-005-003-003 | TimelinePage migration | 6 | MTH | Pending |
| T-005-009 | REQ-005-003-004 | PostmortemsPage migration | 6 | MTH | Pending |
| T-005-010 | REQ-005-004-001 | VulnerabilityDashboard migration | 6 | MTH | Pending |
| T-005-011 | REQ-005-004-002 | CTEMPage migration | 6 | MTH | Pending |
| T-005-012 | REQ-005-005-001 | GraphPage migration | 7 | MTH | Pending |
| T-005-013 | REQ-005-005-002 | SimulationPage migration | 7 | MTH | Pending |
| T-005-014 | REQ-005-006-003 | AssetsPage migration | 7 | MTH | Pending |
| T-005-015 | REQ-005-007-001 | ThreatEnrichmentPage migration | 7 | MTH | Pending |

### Phase P5: Specialized Components & NFRs

| Task ID | Requirement | Description | Agent | Priority | Status |
|---------|-------------|-------------|-------|----------|--------|
| T-006-001 | REQ-006-001-001 | Agent status badges | 8 | MTH | Pending |
| T-NFR-001 | NFR-001 | Theme switch < 300ms | 8 | MTH | Pending |
| T-NFR-004 | NFR-004 | Visible focus indicators | 8 | MTH | Pending |

### Phase P6: NTH Features & Pages

| Task ID | Requirement | Description | Agent | Priority | Status |
|---------|-------------|-------------|-------|----------|--------|
| T-004-011 | REQ-004-002-002 | Toggle switch | 5 | NTH | Pending |
| T-004-012 | REQ-004-006-002 | Inline alert styling | 5 | NTH | Pending |
| T-005-016 | REQ-005-005-003 | CollabPage migration | 7 | NTH | Pending |
| T-005-017 | REQ-005-006-001 | ConfigPage migration | 7 | NTH | Pending |
| T-005-018 | REQ-005-006-002 | AuditPage migration | 7 | NTH | Pending |
| T-005-019 | REQ-005-006-004 | TicketsPage migration | 7 | NTH | Pending |
| T-TECH-007 | TECH-007 | Breakpoint system | 8 | NTH | Pending |
| T-TECH-008 | TECH-008 | Code block syntax highlighting | 8 | NTH | Pending |
| T-006-002 | REQ-006-002-001 | Canvas background and nodes | 8 | NTH | Pending |
| T-006-003 | REQ-006-003-001 | Timeline component | 8 | NTH | Pending |
| T-NFR-005 | NFR-005 | Responsive layout at all breakpoints | 8 | NTH | Pending |

---

## Requirements Coverage Matrix

| Requirement ID | Task ID | Test IDs | Status |
|----------------|---------|----------|--------|
| REQ-001-001-001 | T-001-001 | UT-001-001, IT-001 | [ ] |
| REQ-001-001-002 | T-001-002 | UT-001-002, IT-001 | [ ] |
| REQ-001-001-003 | T-001-003 | UT-001-003, IT-001 | [ ] |
| REQ-001-001-004 | T-001-004 | UT-001-004, IT-001 | [ ] |
| REQ-001-001-005 | T-001-005 | UT-001-005, IT-001 | [ ] |
| REQ-001-002-001 | T-001-006 | UT-001-006, IT-002 | [ ] |
| REQ-001-002-002 | T-001-007 | UT-001-007, IT-002 | [ ] |
| REQ-001-002-003 | T-001-008 | UT-001-008 | [ ] |
| REQ-002-001-001 | T-002-001 | UT-002-001, IT-003, E2E-001 | [ ] |
| REQ-002-001-002 | T-002-002 | UT-002-002, IT-003 | [ ] |
| REQ-002-002-001 | T-002-003 | UT-002-003, IT-003, E2E-001 | [ ] |
| REQ-002-002-002 | T-002-004 | UT-002-004, E2E-001 | [ ] |
| REQ-003-001-001 | T-003-001 | UT-003-001, IT-004, E2E-002 | [ ] |
| REQ-003-002-001 | T-003-002 | UT-003-002, E2E-002 | [ ] |
| REQ-004-001-001 | T-004-001 | UT-004-001, IT-005 | [ ] |
| REQ-004-001-002 | T-004-002 | UT-004-002, IT-005 | [ ] |
| REQ-004-002-001 | T-004-003 | UT-004-003, IT-005 | [ ] |
| REQ-004-002-002 | T-004-011 | UT-004-011, IT-005 | [ ] |
| REQ-004-003-001 | T-004-004 | UT-004-004, IT-005 | [ ] |
| REQ-004-003-002 | T-004-005 | UT-004-005, IT-005 | [ ] |
| REQ-004-004-001 | T-004-006 | UT-004-006, IT-006, E2E-003 | [ ] |
| REQ-004-004-002 | T-004-007 | UT-004-007, IT-006 | [ ] |
| REQ-004-005-001 | T-004-008 | UT-004-008, IT-006 | [ ] |
| REQ-004-006-001 | T-004-009 | UT-004-009, IT-005 | [ ] |
| REQ-004-006-002 | T-004-012 | UT-004-012, IT-005 | [ ] |
| REQ-004-007-001 | T-004-010 | UT-004-010, IT-006 | [ ] |
| REQ-005-001-001 | T-005-001 | UT-005-001, IT-007, E2E-003 | [ ] |
| REQ-005-001-002 | T-005-002 | UT-005-002, IT-007, E2E-003 | [ ] |
| REQ-005-002-001 | T-005-003 | UT-005-003, E2E-004 | [ ] |
| REQ-005-002-002 | T-005-004 | UT-005-004, E2E-004 | [ ] |
| REQ-005-002-003 | T-005-005 | UT-005-005, E2E-004 | [ ] |
| REQ-005-003-001 | T-005-006 | UT-005-006, E2E-005 | [ ] |
| REQ-005-003-002 | T-005-007 | UT-005-007, E2E-005 | [ ] |
| REQ-005-003-003 | T-005-008 | UT-005-008, E2E-005 | [ ] |
| REQ-005-003-004 | T-005-009 | UT-005-009, E2E-005 | [ ] |
| REQ-005-004-001 | T-005-010 | UT-005-010, E2E-006 | [ ] |
| REQ-005-004-002 | T-005-011 | UT-005-011, E2E-006 | [ ] |
| REQ-005-005-001 | T-005-012 | UT-005-012, E2E-007 | [ ] |
| REQ-005-005-002 | T-005-013 | UT-005-013, E2E-007 | [ ] |
| REQ-005-005-003 | T-005-016 | UT-005-016, E2E-007 | [ ] |
| REQ-005-006-001 | T-005-017 | UT-005-017, E2E-008 | [ ] |
| REQ-005-006-002 | T-005-018 | UT-005-018, E2E-008 | [ ] |
| REQ-005-006-003 | T-005-014 | UT-005-014, E2E-008 | [ ] |
| REQ-005-006-004 | T-005-019 | UT-005-019, E2E-008 | [ ] |
| REQ-005-007-001 | T-005-015 | UT-005-015, E2E-009 | [ ] |
| REQ-006-001-001 | T-006-001 | UT-006-001, IT-008 | [ ] |
| REQ-006-002-001 | T-006-002 | UT-006-002, IT-008 | [ ] |
| REQ-006-003-001 | T-006-003 | UT-006-003, IT-008 | [ ] |
| TECH-001 | T-TECH-001 | UT-TECH-001 | [ ] |
| TECH-002 | T-TECH-002 | UT-TECH-002 | [ ] |
| TECH-003 | T-TECH-003 | UT-TECH-003, IT-003 | [ ] |
| TECH-004 | T-TECH-004 | UT-TECH-004 | [ ] |
| TECH-005 | T-TECH-005 | UT-TECH-005 | [ ] |
| TECH-006 | T-TECH-006 | UT-TECH-006 | [ ] |
| TECH-007 | T-TECH-007 | UT-TECH-007 | [ ] |
| TECH-008 | T-TECH-008 | UT-TECH-008 | [ ] |
| INT-001 | T-INT-001 | UT-INT-001, IT-001 | [ ] |
| INT-002 | T-INT-002 | UT-INT-002, IT-005 | [ ] |
| DATA-001 | T-DATA-001 | UT-DATA-001, IT-003 | [ ] |
| DATA-002 | T-DATA-002 | UT-DATA-002, IT-004 | [ ] |
| NFR-001 | T-NFR-001 | UT-NFR-001, E2E-001 | [ ] |
| NFR-002 | T-NFR-002 | UT-NFR-002 | [ ] |
| NFR-003 | T-NFR-003 | UT-NFR-003, E2E-010 | [ ] |
| NFR-004 | T-NFR-004 | UT-NFR-004, E2E-010 | [ ] |
| NFR-005 | T-NFR-005 | UT-NFR-005, E2E-011 | [ ] |

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 65 |
| MTH Tasks | 54 |
| NTH Tasks | 11 |
| Build Agents | 8 (+ TDD Verifier + Review Agent = 10 total) |
| Phases | 6 (5 MTH + 1 NTH) |
| Unit Tests | 65 |
| Integration Tests | 8 |
| E2E Tests | 11 |

---
_Document generated by SoftwareBuilderX v23.0.0_
