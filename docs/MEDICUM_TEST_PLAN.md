# Test Plan: Medicum (CyberDemo Frontend Design System)

| Attribute | Value |
|-----------|-------|
| Build ID | sbx-20260225-132308 |
| Created | 2026-02-25 |
| Template Version | SBX v23.0.0 |

---

## Test Strategy

| Type | Framework | Coverage Target |
|------|-----------|-----------------|
| Unit Tests | Vitest + React Testing Library | All REQ-xxx, TECH-xxx, DATA-xxx, NFR-xxx |
| Integration Tests | Vitest + React Testing Library | All INT-xxx, cross-component flows |
| E2E Tests | Playwright | All FEAT-xxx user flows |

---

## Unit Tests

| Test ID | Requirement | Description | File | Status |
|---------|-------------|-------------|------|--------|
| UT-001 | REQ-001-001-001 | Color scale tokens defined in CSS variables | tests/unit/design-tokens/color-tokens.test.ts | Pending |
| UT-002 | REQ-001-001-002 | Typography tokens (font-family, size, weight, line-height) | tests/unit/design-tokens/typography-tokens.test.ts | Pending |
| UT-003 | REQ-001-001-003 | Spacing tokens (4px base unit scale) | tests/unit/design-tokens/spacing-tokens.test.ts | Pending |
| UT-004 | REQ-001-001-004 | Shadow tokens (sm, md, lg, xl) | tests/unit/design-tokens/shadow-tokens.test.ts | Pending |
| UT-005 | REQ-001-001-005 | Transition tokens (duration, easing) | tests/unit/design-tokens/transition-tokens.test.ts | Pending |
| UT-006 | REQ-001-002-001 | Dark theme color mappings correct | tests/unit/design-tokens/dark-theme.test.ts | Pending |
| UT-007 | REQ-001-002-002 | Light theme color mappings correct | tests/unit/design-tokens/light-theme.test.ts | Pending |
| UT-008 | REQ-001-002-003 | Z-index scale values correct | tests/unit/design-tokens/z-index.test.ts | Pending |
| UT-009 | REQ-002-001-001 | useTheme hook returns theme and toggleTheme | tests/unit/hooks/useTheme.test.ts | Pending |
| UT-010 | REQ-002-001-002 | FOUC prevention script injects correct class | tests/unit/hooks/fouc-prevention.test.ts | Pending |
| UT-011 | REQ-002-002-001 | ThemeToggle renders Sun/Moon icons based on theme | tests/unit/components/ThemeToggle.test.tsx | Pending |
| UT-012 | REQ-002-002-002 | ThemeToggle placed in sidebar footer | tests/unit/components/ThemeTogglePlacement.test.tsx | Pending |
| UT-013 | REQ-003-001-001 | useFontSize hook returns size and cycle function | tests/unit/hooks/useFontSize.test.ts | Pending |
| UT-014 | REQ-003-002-001 | FontSizeButton renders with A icon and cycles sizes | tests/unit/components/FontSizeButton.test.tsx | Pending |
| UT-015 | REQ-004-001-001 | Button variants (primary, secondary, ghost, danger) | tests/unit/components/Button.test.tsx | Pending |
| UT-016 | REQ-004-001-002 | Button sizes (sm, md, lg) | tests/unit/components/ButtonSizes.test.tsx | Pending |
| UT-017 | REQ-004-002-001 | Text input styling with focus ring | tests/unit/components/TextInput.test.tsx | Pending |
| UT-018 | REQ-004-003-001 | Card base styling (rounded, shadow, padding) | tests/unit/components/Card.test.tsx | Pending |
| UT-019 | REQ-004-003-002 | MetricCard shows label, value, trend indicator | tests/unit/components/MetricCard.test.tsx | Pending |
| UT-020 | REQ-004-004-001 | Sidebar nav items with active/hover states | tests/unit/components/SidebarNav.test.tsx | Pending |
| UT-021 | REQ-004-004-002 | Tabs component with active indicator | tests/unit/components/Tabs.test.tsx | Pending |
| UT-022 | REQ-004-005-001 | Table styling with striped rows and hover | tests/unit/components/Table.test.tsx | Pending |
| UT-023 | REQ-004-006-001 | Badge variants (success, warning, danger, info) | tests/unit/components/Badge.test.tsx | Pending |
| UT-024 | REQ-004-007-001 | Modal overlay with backdrop blur | tests/unit/components/Modal.test.tsx | Pending |
| UT-025 | REQ-004-002-002 | Toggle switch with checked/unchecked states | tests/unit/components/ToggleSwitch.test.tsx | Pending |
| UT-026 | REQ-004-006-002 | Inline alert with icon and message | tests/unit/components/InlineAlert.test.tsx | Pending |
| UT-027 | REQ-005-001-001 | Layout.tsx uses design tokens for grid | tests/unit/pages/Layout.test.tsx | Pending |
| UT-028 | REQ-005-001-002 | Sidebar.tsx uses token-based styling | tests/unit/pages/Sidebar.test.tsx | Pending |
| UT-029 | REQ-005-002-001 | DashboardPage uses MetricCard and token colors | tests/unit/pages/DashboardPage.test.tsx | Pending |
| UT-030 | REQ-005-002-002 | SurfacePage uses card and table tokens | tests/unit/pages/SurfacePage.test.tsx | Pending |
| UT-031 | REQ-005-002-003 | GenerationPage uses token-based styling | tests/unit/pages/GenerationPage.test.tsx | Pending |
| UT-032 | REQ-005-003-001 | IncidentsPage uses badge and table tokens | tests/unit/pages/IncidentsPage.test.tsx | Pending |
| UT-033 | REQ-005-003-002 | DetectionsPage uses token-based styling | tests/unit/pages/DetectionsPage.test.tsx | Pending |
| UT-034 | REQ-005-003-003 | TimelinePage uses token colors for events | tests/unit/pages/TimelinePage.test.tsx | Pending |
| UT-035 | REQ-005-003-004 | PostmortemsPage uses card and table tokens | tests/unit/pages/PostmortemsPage.test.tsx | Pending |
| UT-036 | REQ-005-004-001 | VulnerabilityDashboard uses MetricCard tokens | tests/unit/pages/VulnerabilityDashboard.test.tsx | Pending |
| UT-037 | REQ-005-004-002 | CTEMPage uses token-based styling | tests/unit/pages/CTEMPage.test.tsx | Pending |
| UT-038 | REQ-005-005-001 | GraphPage uses token colors for nodes | tests/unit/pages/GraphPage.test.tsx | Pending |
| UT-039 | REQ-005-005-002 | SimulationPage uses token-based styling | tests/unit/pages/SimulationPage.test.tsx | Pending |
| UT-040 | REQ-005-006-003 | AssetsPage uses card and table tokens | tests/unit/pages/AssetsPage.test.tsx | Pending |
| UT-041 | REQ-005-007-001 | ThreatEnrichmentPage uses token styling | tests/unit/pages/ThreatEnrichmentPage.test.tsx | Pending |
| UT-042 | REQ-005-005-003 | CollabPage uses token-based styling | tests/unit/pages/CollabPage.test.tsx | Pending |
| UT-043 | REQ-005-006-001 | ConfigPage uses form token styling | tests/unit/pages/ConfigPage.test.tsx | Pending |
| UT-044 | REQ-005-006-002 | AuditPage uses table token styling | tests/unit/pages/AuditPage.test.tsx | Pending |
| UT-045 | REQ-005-006-004 | TicketsPage uses card token styling | tests/unit/pages/TicketsPage.test.tsx | Pending |
| UT-046 | REQ-006-001-001 | Agent status badges use correct colors | tests/unit/components/AgentStatusBadge.test.tsx | Pending |
| UT-047 | REQ-006-002-001 | Canvas background uses token gradient | tests/unit/components/CanvasBackground.test.tsx | Pending |
| UT-048 | REQ-006-003-001 | Timeline uses token colors for events | tests/unit/components/Timeline.test.tsx | Pending |
| UT-049 | TECH-001 | Tailwind config extends with CSS variables | tests/unit/config/tailwind-config.test.ts | Pending |
| UT-050 | TECH-002 | CSS files organized in correct structure | tests/unit/config/css-organization.test.ts | Pending |
| UT-051 | TECH-003 | ThemeProvider and FontSizeProvider context works | tests/unit/providers/DesignProvider.test.tsx | Pending |
| UT-052 | TECH-004 | No hardcoded hex colors in components | tests/unit/config/no-hardcoded-colors.test.ts | Pending |
| UT-053 | TECH-005 | Font loading with display=swap | tests/unit/config/font-loading.test.ts | Pending |
| UT-054 | TECH-006 | CSS animations use token durations | tests/unit/config/animations.test.ts | Pending |
| UT-055 | TECH-007 | Breakpoints match spec values | tests/unit/config/breakpoints.test.ts | Pending |
| UT-056 | TECH-008 | Code block syntax highlighting tokens | tests/unit/config/syntax-highlight.test.ts | Pending |
| UT-057 | INT-001 | Google Fonts loads Inter and JetBrains Mono | tests/unit/integrations/google-fonts.test.ts | Pending |
| UT-058 | INT-002 | Lucide icons with consistent sizing | tests/unit/integrations/lucide-icons.test.tsx | Pending |
| UT-059 | DATA-001 | LocalStorage theme persistence | tests/unit/data/theme-storage.test.ts | Pending |
| UT-060 | DATA-002 | LocalStorage font size persistence | tests/unit/data/fontsize-storage.test.ts | Pending |
| UT-061 | NFR-001 | Theme switch completes under 300ms | tests/unit/nfr/theme-performance.test.ts | Pending |
| UT-062 | NFR-002 | Color contrast ratios meet WCAG 2.2 AA | tests/unit/nfr/color-contrast.test.ts | Pending |
| UT-063 | NFR-003 | All interactive elements keyboard accessible | tests/unit/nfr/keyboard-navigation.test.ts | Pending |
| UT-064 | NFR-004 | Focus indicators visible on all elements | tests/unit/nfr/focus-indicators.test.ts | Pending |
| UT-065 | NFR-005 | Layout adapts at breakpoints | tests/unit/nfr/responsive-layout.test.ts | Pending |

---

## Integration Tests

| Test ID | Requirements | Description | File | Status |
|---------|--------------|-------------|------|--------|
| IT-001 | REQ-001-001-001, REQ-001-001-002, REQ-001-001-003, INT-001 | Design tokens load and apply to rendered components | tests/integration/design-tokens.test.tsx | Pending |
| IT-002 | REQ-001-002-001, REQ-001-002-002 | Theme tokens switch between dark and light correctly | tests/integration/theme-tokens.test.tsx | Pending |
| IT-003 | TECH-003, REQ-002-001-001, DATA-001 | ThemeProvider + useTheme + localStorage integration | tests/integration/theme-system.test.tsx | Pending |
| IT-004 | REQ-003-001-001, DATA-002 | FontSizeProvider + useFontSize + localStorage integration | tests/integration/fontsize-system.test.tsx | Pending |
| IT-005 | REQ-004-001-001, REQ-004-001-002, REQ-004-002-001, INT-002 | UI components render correctly with token styles | tests/integration/ui-components.test.tsx | Pending |
| IT-006 | REQ-004-004-001, REQ-004-005-001, REQ-004-007-001 | Navigation, table, modal components in layout context | tests/integration/layout-components.test.tsx | Pending |
| IT-007 | REQ-005-001-001, REQ-005-001-002 | Layout and Sidebar integrate with theme and font size | tests/integration/layout-integration.test.tsx | Pending |
| IT-008 | REQ-006-001-001, REQ-006-002-001 | Specialized components with design token integration | tests/integration/specialized-components.test.tsx | Pending |

---

## E2E Tests (Playwright)

| Test ID | Feature | Description | File | Status |
|---------|---------|-------------|------|--------|
| E2E-001 | FEAT-002-001, FEAT-002-002 | Theme toggle: click toggle, verify theme changes, persists on reload | tests/e2e/theme-toggle.spec.ts | Pending |
| E2E-002 | FEAT-003-001, FEAT-003-002 | Font size: click button, verify size cycles, persists on reload | tests/e2e/font-size.spec.ts | Pending |
| E2E-003 | FEAT-005-001 | Layout: sidebar navigation, theme and font size controls visible | tests/e2e/layout-navigation.spec.ts | Pending |
| E2E-004 | FEAT-005-002 | Dashboard pages: load correctly with design tokens applied | tests/e2e/dashboard-pages.spec.ts | Pending |
| E2E-005 | FEAT-005-003 | Security pages: incidents, detections, timeline render correctly | tests/e2e/security-pages.spec.ts | Pending |
| E2E-006 | FEAT-005-004 | Vulnerability pages: dashboard and CTEM render correctly | tests/e2e/vulnerability-pages.spec.ts | Pending |
| E2E-007 | FEAT-005-005 | Advanced pages: graph, simulation render with tokens | tests/e2e/advanced-pages.spec.ts | Pending |
| E2E-008 | FEAT-005-006 | Settings pages: config, audit, assets render correctly | tests/e2e/settings-pages.spec.ts | Pending |
| E2E-009 | FEAT-005-007 | ThreatEnrichment page renders with design tokens | tests/e2e/threat-enrichment.spec.ts | Pending |
| E2E-010 | NFR-003, NFR-004 | Keyboard navigation: tab through all interactive elements | tests/e2e/keyboard-navigation.spec.ts | Pending |
| E2E-011 | NFR-005 | Responsive: layout adapts at each breakpoint | tests/e2e/responsive-layout.spec.ts | Pending |

---

## Coverage Verification Matrix

| Req ID | UT IDs | IT IDs | E2E IDs | Coverage |
|--------|--------|--------|---------|----------|
| REQ-001-001-001 | UT-001 | IT-001 | - | [ ] Complete |
| REQ-001-001-002 | UT-002 | IT-001 | - | [ ] Complete |
| REQ-001-001-003 | UT-003 | IT-001 | - | [ ] Complete |
| REQ-001-001-004 | UT-004 | IT-001 | - | [ ] Complete |
| REQ-001-001-005 | UT-005 | IT-001 | - | [ ] Complete |
| REQ-001-002-001 | UT-006 | IT-002 | - | [ ] Complete |
| REQ-001-002-002 | UT-007 | IT-002 | - | [ ] Complete |
| REQ-001-002-003 | UT-008 | - | - | [ ] Complete |
| REQ-002-001-001 | UT-009 | IT-003 | E2E-001 | [ ] Complete |
| REQ-002-001-002 | UT-010 | IT-003 | - | [ ] Complete |
| REQ-002-002-001 | UT-011 | IT-003 | E2E-001 | [ ] Complete |
| REQ-002-002-002 | UT-012 | - | E2E-001 | [ ] Complete |
| REQ-003-001-001 | UT-013 | IT-004 | E2E-002 | [ ] Complete |
| REQ-003-002-001 | UT-014 | - | E2E-002 | [ ] Complete |
| REQ-004-001-001 | UT-015 | IT-005 | - | [ ] Complete |
| REQ-004-001-002 | UT-016 | IT-005 | - | [ ] Complete |
| REQ-004-002-001 | UT-017 | IT-005 | - | [ ] Complete |
| REQ-004-002-002 | UT-025 | IT-005 | - | [ ] Complete |
| REQ-004-003-001 | UT-018 | IT-005 | - | [ ] Complete |
| REQ-004-003-002 | UT-019 | IT-005 | - | [ ] Complete |
| REQ-004-004-001 | UT-020 | IT-006 | E2E-003 | [ ] Complete |
| REQ-004-004-002 | UT-021 | IT-006 | - | [ ] Complete |
| REQ-004-005-001 | UT-022 | IT-006 | - | [ ] Complete |
| REQ-004-006-001 | UT-023 | IT-005 | - | [ ] Complete |
| REQ-004-006-002 | UT-026 | IT-005 | - | [ ] Complete |
| REQ-004-007-001 | UT-024 | IT-006 | - | [ ] Complete |
| REQ-005-001-001 | UT-027 | IT-007 | E2E-003 | [ ] Complete |
| REQ-005-001-002 | UT-028 | IT-007 | E2E-003 | [ ] Complete |
| REQ-005-002-001 | UT-029 | - | E2E-004 | [ ] Complete |
| REQ-005-002-002 | UT-030 | - | E2E-004 | [ ] Complete |
| REQ-005-002-003 | UT-031 | - | E2E-004 | [ ] Complete |
| REQ-005-003-001 | UT-032 | - | E2E-005 | [ ] Complete |
| REQ-005-003-002 | UT-033 | - | E2E-005 | [ ] Complete |
| REQ-005-003-003 | UT-034 | - | E2E-005 | [ ] Complete |
| REQ-005-003-004 | UT-035 | - | E2E-005 | [ ] Complete |
| REQ-005-004-001 | UT-036 | - | E2E-006 | [ ] Complete |
| REQ-005-004-002 | UT-037 | - | E2E-006 | [ ] Complete |
| REQ-005-005-001 | UT-038 | - | E2E-007 | [ ] Complete |
| REQ-005-005-002 | UT-039 | - | E2E-007 | [ ] Complete |
| REQ-005-005-003 | UT-042 | - | E2E-007 | [ ] Complete |
| REQ-005-006-001 | UT-043 | - | E2E-008 | [ ] Complete |
| REQ-005-006-002 | UT-044 | - | E2E-008 | [ ] Complete |
| REQ-005-006-003 | UT-040 | - | E2E-008 | [ ] Complete |
| REQ-005-006-004 | UT-045 | - | E2E-008 | [ ] Complete |
| REQ-005-007-001 | UT-041 | - | E2E-009 | [ ] Complete |
| REQ-006-001-001 | UT-046 | IT-008 | - | [ ] Complete |
| REQ-006-002-001 | UT-047 | IT-008 | - | [ ] Complete |
| REQ-006-003-001 | UT-048 | IT-008 | - | [ ] Complete |
| TECH-001 | UT-049 | - | - | [ ] Complete |
| TECH-002 | UT-050 | - | - | [ ] Complete |
| TECH-003 | UT-051 | IT-003 | - | [ ] Complete |
| TECH-004 | UT-052 | - | - | [ ] Complete |
| TECH-005 | UT-053 | - | - | [ ] Complete |
| TECH-006 | UT-054 | - | - | [ ] Complete |
| TECH-007 | UT-055 | - | - | [ ] Complete |
| TECH-008 | UT-056 | - | - | [ ] Complete |
| INT-001 | UT-057 | IT-001 | - | [ ] Complete |
| INT-002 | UT-058 | IT-005 | - | [ ] Complete |
| DATA-001 | UT-059 | IT-003 | - | [ ] Complete |
| DATA-002 | UT-060 | IT-004 | - | [ ] Complete |
| NFR-001 | UT-061 | - | E2E-001 | [ ] Complete |
| NFR-002 | UT-062 | - | - | [ ] Complete |
| NFR-003 | UT-063 | - | E2E-010 | [ ] Complete |
| NFR-004 | UT-064 | - | E2E-010 | [ ] Complete |
| NFR-005 | UT-065 | - | E2E-011 | [ ] Complete |

---
_Document generated by SoftwareBuilderX v23.0.0_
