# Test Plan: AgentFlow Design System Unification

| Attribute | Value |
|-----------|-------|
| Build ID | sbx-20260225-111316 |
| Created | 2026-02-25 |
| Template Version | SBX v21.0.0 |

---

## Test Strategy

| Type | Framework | Coverage Target |
|------|-----------|-----------------|
| Unit Tests | Vitest (React) / Web Test Runner (Lit) | All REQ-xxx, TECH-xxx, DATA-xxx, NFR-xxx |
| Integration Tests | Vitest + JSDOM | All INT-xxx, cross-component interactions |
| E2E Tests | Playwright | All FEAT-xxx visual verification |

---

## Unit Tests

| Test ID | Requirement | Description | File | Status |
|---------|-------------|-------------|------|--------|
| UT-001 | REQ-001-001-001 | Verify design-tokens.css contains all required CSS custom properties | tests/unit/design-tokens.test.ts | Pending |
| UT-002 | REQ-001-001-002 | Verify :root block contains all base/shared tokens | tests/unit/design-tokens.test.ts | Pending |
| UT-003 | REQ-001-001-003 | Verify [data-theme="dark"] block contains dark semantic tokens | tests/unit/design-tokens.test.ts | Pending |
| UT-004 | REQ-001-001-004 | Verify [data-theme="light"] block contains light semantic tokens | tests/unit/design-tokens.test.ts | Pending |
| UT-005 | REQ-001-001-005 | Verify token values match style guide v2.0 specifications | tests/unit/design-tokens.test.ts | Pending |
| UT-006 | REQ-001-002-001 | Verify CyberDemo tailwind.config.js references CSS custom properties | tests/unit/tailwind-config.test.ts | Pending |
| UT-007 | REQ-001-002-002 | Verify Medicum tailwind.config.js references CSS custom properties | tests/unit/tailwind-config.test.ts | Pending |
| UT-008 | REQ-001-002-003 | Verify Tailwind font families configured for Inter + JetBrains Mono | tests/unit/tailwind-config.test.ts | Pending |
| UT-009 | REQ-001-003-001 | Verify Inter font loaded with correct weights | tests/unit/font-loading.test.ts | Pending |
| UT-010 | REQ-001-003-002 | Verify JetBrains Mono font loaded with correct weights | tests/unit/font-loading.test.ts | Pending |
| UT-011 | REQ-001-003-003 | Verify Files Manager has Inter + JetBrains Mono fonts | tests/unit/font-loading.test.ts | Pending |
| UT-012 | REQ-002-001-001 | ThemeToggle renders pill shape with 3 buttons | tests/unit/theme-toggle.test.tsx | Pending |
| UT-013 | REQ-002-001-002 | ThemeToggle active button has primary-600 bg, inactive has text-secondary | tests/unit/theme-toggle.test.tsx | Pending |
| UT-014 | REQ-002-001-003 | ThemeToggle uses correct Lucide icons per mode | tests/unit/theme-toggle.test.tsx | Pending |
| UT-015 | REQ-002-001-004 | ThemeToggle click sets data-theme on html element | tests/unit/theme-toggle.test.tsx | Pending |
| UT-016 | REQ-002-001-005 | ThemeToggle System option reads prefers-color-scheme | tests/unit/theme-toggle.test.tsx | Pending |
| UT-017 | REQ-002-001-006 | ThemeToggle transition uses 200ms ease-default | tests/unit/theme-toggle.test.tsx | Pending |
| UT-018 | REQ-002-002-001 | theme-toggle Lit component renders correctly | tests/unit/theme-toggle-lit.test.ts | Pending |
| UT-019 | REQ-002-002-002 | theme-toggle Lit sets data-theme on documentElement | tests/unit/theme-toggle-lit.test.ts | Pending |
| UT-020 | REQ-002-002-003 | theme-toggle placed in Files Manager toolbar | tests/unit/theme-toggle-lit.test.ts | Pending |
| UT-021 | REQ-002-003-001 | Theme saved to localStorage key theme-preference | tests/unit/theme-persistence.test.ts | Pending |
| UT-022 | REQ-002-003-002 | Theme applied from localStorage before first paint | tests/unit/theme-persistence.test.ts | Pending |
| UT-023 | REQ-002-003-003 | System mode detects OS preference on load | tests/unit/theme-persistence.test.ts | Pending |
| UT-024 | REQ-002-003-004 | Default to dark if localStorage empty | tests/unit/theme-persistence.test.ts | Pending |
| UT-025 | REQ-002-003-005 | Body transition 300ms ease-default on theme switch | tests/unit/theme-persistence.test.ts | Pending |
| UT-026 | REQ-003-001-001 | FontSizeButton renders with Lucide icon | tests/unit/font-size-button.test.tsx | Pending |
| UT-027 | REQ-003-001-002 | FontSizeButton cycles 16px -> 18px -> 20px -> 16px | tests/unit/font-size-button.test.tsx | Pending |
| UT-028 | REQ-003-001-003 | FontSizeButton modifies documentElement fontSize | tests/unit/font-size-button.test.tsx | Pending |
| UT-029 | REQ-003-001-004 | FontSizeButton visually indicates current state | tests/unit/font-size-button.test.tsx | Pending |
| UT-030 | REQ-003-001-006 | FontSizeButton placed LEFT of ThemeToggle | tests/unit/font-size-button.test.tsx | Pending |
| UT-031 | REQ-003-002-001 | font-size-button Lit component works correctly | tests/unit/font-size-button-lit.test.ts | Pending |
| UT-032 | REQ-003-002-002 | font-size-button placed next to theme-toggle in FM | tests/unit/font-size-button-lit.test.ts | Pending |
| UT-033 | REQ-003-003-001 | Font size step saved to localStorage | tests/unit/font-size-persistence.test.ts | Pending |
| UT-034 | REQ-003-003-002 | Font size restored from localStorage before first paint | tests/unit/font-size-persistence.test.ts | Pending |
| UT-035 | REQ-003-003-003 | Default to step 0 (16px) if localStorage unavailable | tests/unit/font-size-persistence.test.ts | Pending |
| UT-036 | REQ-004-001-001 | CyberDemo sidebar uses design tokens | tests/unit/cyberdemo-layout.test.tsx | Pending |
| UT-037 | REQ-004-001-002 | CyberDemo header uses design tokens | tests/unit/cyberdemo-layout.test.tsx | Pending |
| UT-038 | REQ-004-001-003 | DemoControlBar uses design tokens | tests/unit/cyberdemo-layout.test.tsx | Pending |
| UT-039 | REQ-004-001-004 | CyberDemo imports design-tokens.css | tests/unit/cyberdemo-layout.test.tsx | Pending |
| UT-040 | REQ-004-002-001 | /dashboard page uses design tokens | tests/unit/cyberdemo-pages.test.tsx | Pending |
| UT-041 | REQ-004-002-002 | /generation page uses design tokens | tests/unit/cyberdemo-pages.test.tsx | Pending |
| UT-042 | REQ-004-002-003 | /surface page uses design tokens | tests/unit/cyberdemo-pages.test.tsx | Pending |
| UT-043 | REQ-004-003-001 | Vulnerability pages use design tokens | tests/unit/cyberdemo-pages.test.tsx | Pending |
| UT-044 | REQ-004-003-002 | /threats page uses design tokens | tests/unit/cyberdemo-pages.test.tsx | Pending |
| UT-045 | REQ-004-003-003 | /incidents page uses design tokens | tests/unit/cyberdemo-pages.test.tsx | Pending |
| UT-046 | REQ-004-003-004 | /detections page uses design tokens | tests/unit/cyberdemo-pages.test.tsx | Pending |
| UT-047 | REQ-004-003-005 | /ctem page uses design tokens | tests/unit/cyberdemo-pages.test.tsx | Pending |
| UT-048 | REQ-004-003-006 | /vulnerabilities/ssvc page uses design tokens | tests/unit/cyberdemo-pages.test.tsx | Pending |
| UT-049 | REQ-004-004-001 | Workflow canvas uses design tokens | tests/unit/cyberdemo-orchestration.test.tsx | Pending |
| UT-050 | REQ-004-004-002 | Agent status badges use design tokens | tests/unit/cyberdemo-orchestration.test.tsx | Pending |
| UT-051 | REQ-004-004-003 | Execution timeline uses design tokens | tests/unit/cyberdemo-orchestration.test.tsx | Pending |
| UT-052 | REQ-004-004-004 | Log viewer uses design tokens | tests/unit/cyberdemo-orchestration.test.tsx | Pending |
| UT-053 | REQ-004-004-005 | Metric cards use design tokens | tests/unit/cyberdemo-orchestration.test.tsx | Pending |
| UT-054 | REQ-004-005-001 | /timeline page uses design tokens | tests/unit/cyberdemo-remaining.test.tsx | Pending |
| UT-055 | REQ-004-005-002 | /postmortems page uses design tokens | tests/unit/cyberdemo-remaining.test.tsx | Pending |
| UT-056 | REQ-004-005-003 | /tickets page uses design tokens | tests/unit/cyberdemo-remaining.test.tsx | Pending |
| UT-057 | REQ-004-005-004 | /graph pages use design tokens | tests/unit/cyberdemo-remaining.test.tsx | Pending |
| UT-058 | REQ-004-005-005 | /collab page uses design tokens | tests/unit/cyberdemo-remaining.test.tsx | Pending |
| UT-059 | REQ-004-005-006 | /config page uses design tokens | tests/unit/cyberdemo-remaining.test.tsx | Pending |
| UT-060 | REQ-004-005-007 | /audit page uses design tokens | tests/unit/cyberdemo-remaining.test.tsx | Pending |
| UT-061 | REQ-004-005-008 | /simulation page uses design tokens | tests/unit/cyberdemo-remaining.test.tsx | Pending |
| UT-062 | REQ-004-005-009 | /assets page uses design tokens | tests/unit/cyberdemo-remaining.test.tsx | Pending |
| UT-063 | REQ-005-001-001 | Medicum App.tsx uses var(--bg-primary) | tests/unit/medicum-layout.test.tsx | Pending |
| UT-064 | REQ-005-001-002 | PatientHeader uses design tokens | tests/unit/medicum-layout.test.tsx | Pending |
| UT-065 | REQ-005-001-003 | Allergy badges use semantic tokens | tests/unit/medicum-layout.test.tsx | Pending |
| UT-066 | REQ-005-001-004 | Connection status dots use AgentFlow colors | tests/unit/medicum-layout.test.tsx | Pending |
| UT-067 | REQ-005-001-005 | ThemeToggle + FontSizeButton in PatientHeader | tests/unit/medicum-layout.test.tsx | Pending |
| UT-068 | REQ-005-001-006 | TabBar uses design tokens | tests/unit/medicum-layout.test.tsx | Pending |
| UT-069 | REQ-005-001-007 | Medicum imports design-tokens.css + fonts | tests/unit/medicum-layout.test.tsx | Pending |
| UT-070 | REQ-005-002-001 | Consulta transcription panel uses tokens | tests/unit/medicum-consulta.test.tsx | Pending |
| UT-071 | REQ-005-002-002 | Chat bubbles use tokens | tests/unit/medicum-consulta.test.tsx | Pending |
| UT-072 | REQ-005-002-003 | SOAP note panel uses tokens | tests/unit/medicum-consulta.test.tsx | Pending |
| UT-073 | REQ-005-002-004 | Whisper status badges use tokens | tests/unit/medicum-consulta.test.tsx | Pending |
| UT-074 | REQ-005-002-005 | Speaker toggle and buttons use tokens | tests/unit/medicum-consulta.test.tsx | Pending |
| UT-075 | REQ-005-003-001 | Historia accordion uses tokens | tests/unit/medicum-historia.test.tsx | Pending |
| UT-076 | REQ-005-003-002 | Lab results table uses tokens | tests/unit/medicum-historia.test.tsx | Pending |
| UT-077 | REQ-005-003-003 | Episode cards use tokens | tests/unit/medicum-historia.test.tsx | Pending |
| UT-078 | REQ-005-004-001 | Codificacion AI panel uses tokens | tests/unit/medicum-codificacion.test.tsx | Pending |
| UT-079 | REQ-005-004-002 | CIE-10 codes use font-mono with theme-aware color | tests/unit/medicum-codificacion.test.tsx | Pending |
| UT-080 | REQ-005-004-003 | Confidence badges use semantic tokens | tests/unit/medicum-codificacion.test.tsx | Pending |
| UT-081 | REQ-005-004-004 | Search input and results use tokens | tests/unit/medicum-codificacion.test.tsx | Pending |
| UT-082 | REQ-005-004-005 | Assigned codes panel uses tokens | tests/unit/medicum-codificacion.test.tsx | Pending |
| UT-083 | REQ-005-005-001 | Visor toolbar uses tokens | tests/unit/medicum-visor.test.tsx | Pending |
| UT-084 | REQ-005-005-002 | Visor image area stays dark in both themes | tests/unit/medicum-visor.test.tsx | Pending |
| UT-085 | REQ-005-005-003 | Visor AI analysis panel uses tokens | tests/unit/medicum-visor.test.tsx | Pending |
| UT-086 | REQ-005-005-004 | Visor finding cards use tokens | tests/unit/medicum-visor.test.tsx | Pending |
| UT-087 | REQ-005-005-005 | Visor radiological report uses tokens | tests/unit/medicum-visor.test.tsx | Pending |
| UT-088 | REQ-006-001-001 | Files Manager --bg-primary token correct | tests/unit/files-manager-tokens.test.ts | Pending |
| UT-089 | REQ-006-001-002 | Files Manager --bg-secondary token correct | tests/unit/files-manager-tokens.test.ts | Pending |
| UT-090 | REQ-006-001-003 | Files Manager --bg-tertiary token correct | tests/unit/files-manager-tokens.test.ts | Pending |
| UT-091 | REQ-006-001-004 | Files Manager --text-* tokens correct | tests/unit/files-manager-tokens.test.ts | Pending |
| UT-092 | REQ-006-001-005 | Files Manager --border-* tokens correct | tests/unit/files-manager-tokens.test.ts | Pending |
| UT-093 | REQ-006-001-006 | Files Manager light theme values correct | tests/unit/files-manager-tokens.test.ts | Pending |
| UT-094 | REQ-006-001-007 | Files Manager has shadow, radius, spacing tokens | tests/unit/files-manager-tokens.test.ts | Pending |
| UT-095 | REQ-006-002-001 | theme-toggle integrated in FM toolbar | tests/unit/files-manager-integration.test.ts | Pending |
| UT-096 | REQ-006-002-002 | font-size-button integrated in FM toolbar | tests/unit/files-manager-integration.test.ts | Pending |
| UT-097 | REQ-006-003-001 | No hardcoded colors in FM index.html | tests/unit/files-manager-hardcoded.test.ts | Pending |
| UT-098 | REQ-006-003-002 | No hardcoded colors in files-epic002.ts | tests/unit/files-manager-hardcoded.test.ts | Pending |
| UT-099 | REQ-007-001-001 | Primary buttons match spec | tests/unit/component-standards.test.tsx | Pending |
| UT-100 | REQ-007-001-002 | Destructive buttons match spec | tests/unit/component-standards.test.tsx | Pending |
| UT-101 | REQ-007-001-003 | Button sizes match spec | tests/unit/component-standards.test.tsx | Pending |
| UT-102 | REQ-007-001-004 | Focus ring matches spec | tests/unit/component-standards.test.tsx | Pending |
| UT-103 | REQ-007-001-005 | Disabled state matches spec | tests/unit/component-standards.test.tsx | Pending |
| UT-104 | REQ-007-002-001 | Card components match spec | tests/unit/component-standards.test.tsx | Pending |
| UT-105 | REQ-007-002-002 | Interactive card hover matches spec | tests/unit/component-standards.test.tsx | Pending |
| UT-106 | REQ-007-003-001 | Input components match spec | tests/unit/component-standards.test.tsx | Pending |
| UT-107 | REQ-007-003-002 | Input focus state matches spec | tests/unit/component-standards.test.tsx | Pending |
| UT-108 | REQ-007-003-003 | Input error state matches spec | tests/unit/component-standards.test.tsx | Pending |
| UT-109 | REQ-007-003-004 | Placeholder color matches spec | tests/unit/component-standards.test.tsx | Pending |
| UT-110 | REQ-007-004-001 | Table headers match spec | tests/unit/component-standards.test.tsx | Pending |
| UT-111 | REQ-007-004-002 | Table rows match spec | tests/unit/component-standards.test.tsx | Pending |
| UT-112 | REQ-007-005-001 | Badges match spec | tests/unit/component-standards.test.tsx | Pending |
| UT-113 | REQ-007-005-002 | Toasts match spec | tests/unit/component-standards.test.tsx | Pending |
| UT-114 | REQ-007-006-001 | Modals match spec | tests/unit/component-standards.test.tsx | Pending |
| UT-115 | REQ-007-006-002 | Modal footer matches spec | tests/unit/component-standards.test.tsx | Pending |
| UT-116 | REQ-008-001-001 | Dark theme contrast ratios >= 4.5:1 | tests/unit/accessibility.test.ts | Pending |
| UT-117 | REQ-008-001-002 | Light theme contrast ratios >= 4.5:1 | tests/unit/accessibility.test.ts | Pending |
| UT-118 | REQ-008-001-003 | UI component contrast >= 3:1 | tests/unit/accessibility.test.ts | Pending |
| UT-119 | REQ-008-002-001 | Focus indicators visible on all interactive elements | tests/unit/accessibility.test.ts | Pending |
| UT-120 | REQ-008-002-002 | Theme toggle ARIA attributes correct | tests/unit/accessibility.test.ts | Pending |
| UT-121 | REQ-008-002-003 | Font size button ARIA attributes correct | tests/unit/accessibility.test.ts | Pending |
| UT-122 | REQ-008-002-004 | Modal focus trap implemented | tests/unit/accessibility.test.ts | Pending |
| UT-123 | REQ-008-002-005 | Toast has role="status" | tests/unit/accessibility.test.ts | Pending |
| UT-124 | REQ-003-001-005 | FontSizeButton tooltip shows current level | tests/unit/font-size-button.test.tsx | Pending |
| UT-125 | REQ-006-004-001 | Emoji buttons replaced with Lucide SVG | tests/unit/files-manager-icons.test.ts | Pending |
| UT-126 | REQ-006-004-002 | Lucide dependency available in Lit | tests/unit/files-manager-icons.test.ts | Pending |
| UT-127 | REQ-007-007-001 | Empty states match spec | tests/unit/component-standards.test.tsx | Pending |
| UT-128 | REQ-009-001-001 | Sidebar collapses to icons at 1024-1280px | tests/unit/responsive.test.tsx | Pending |
| UT-129 | REQ-009-001-002 | Sidebar becomes hamburger below 1024px | tests/unit/responsive.test.tsx | Pending |
| UT-130 | REQ-009-001-003 | Tables hide secondary columns at 1024-1280px | tests/unit/responsive.test.tsx | Pending |
| UT-131 | REQ-009-001-004 | Tables horizontal scroll at 768-1024px | tests/unit/responsive.test.tsx | Pending |
| UT-132 | TECH-001 | CSS custom properties used (no SASS/LESS) | tests/unit/tech-requirements.test.ts | Pending |
| UT-133 | TECH-002 | Tokens importable in React and Lit | tests/unit/tech-requirements.test.ts | Pending |
| UT-134 | TECH-003 | Theme script runs synchronously in head | tests/unit/tech-requirements.test.ts | Pending |
| UT-135 | TECH-004 | Font size targets documentElement.style.fontSize | tests/unit/tech-requirements.test.ts | Pending |
| UT-136 | TECH-005 | Tailwind var(--token) references work | tests/unit/tech-requirements.test.ts | Pending |
| UT-137 | TECH-006 | Shadow DOM components inject tokens | tests/unit/tech-requirements.test.ts | Pending |
| UT-138 | TECH-007 | CyberDemo animations preserved | tests/unit/tech-requirements.test.ts | Pending |
| UT-139 | TECH-008 | Build size increase < 50KB | tests/unit/tech-requirements.test.ts | Pending |
| UT-140 | TECH-009 | font-display: swap configured | tests/unit/tech-requirements.test.ts | Pending |
| UT-141 | TECH-010 | No hardcoded hex colors in source | tests/unit/tech-requirements.test.ts | Pending |
| UT-142 | DATA-001 | localStorage theme-preference stores correct values | tests/unit/data-requirements.test.ts | Pending |
| UT-143 | DATA-002 | localStorage font-size-step stores correct values | tests/unit/data-requirements.test.ts | Pending |
| UT-144 | DATA-003 | Per-origin localStorage scoping works | tests/unit/data-requirements.test.ts | Pending |
| UT-145 | DATA-004 | No sensitive data in localStorage | tests/unit/data-requirements.test.ts | Pending |
| UT-146 | NFR-001 | Theme switch latency < 300ms | tests/unit/nfr-performance.test.ts | Pending |
| UT-147 | NFR-002 | Font size change latency < 100ms | tests/unit/nfr-performance.test.ts | Pending |
| UT-148 | NFR-003 | No FOUC on page load | tests/unit/nfr-performance.test.ts | Pending |
| UT-149 | NFR-004 | Feature parity across themes | tests/unit/nfr-quality.test.ts | Pending |
| UT-150 | NFR-005 | Graceful localStorage fallback | tests/unit/nfr-quality.test.ts | Pending |
| UT-151 | NFR-006 | No sensitive data stored | tests/unit/nfr-security.test.ts | Pending |
| UT-152 | NFR-007 | No XSS vectors | tests/unit/nfr-security.test.ts | Pending |
| UT-153 | NFR-008 | Token system extensible | tests/unit/nfr-quality.test.ts | Pending |
| UT-154 | NFR-009 | Framework-agnostic CSS | tests/unit/nfr-quality.test.ts | Pending |
| UT-155 | NFR-010 | WCAG 2.2 AA contrast compliance | tests/unit/nfr-accessibility.test.ts | Pending |
| UT-156 | NFR-011 | Consistent keyboard navigation | tests/unit/nfr-accessibility.test.ts | Pending |
| UT-157 | NFR-012 | Per-project preference persistence | tests/unit/nfr-quality.test.ts | Pending |

---

## Integration Tests

| Test ID | Requirements | Description | File | Status |
|---------|--------------|-------------|------|--------|
| IT-001 | INT-001, REQ-001-001-001 | Design tokens shared between CyberDemo and Medicum | tests/integration/token-sharing.test.ts | Pending |
| IT-002 | INT-002, REQ-001-002-001, REQ-001-002-002 | Tailwind config references same tokens across projects | tests/integration/tailwind-integration.test.ts | Pending |
| IT-003 | INT-004, REQ-001-003-001, REQ-001-003-002 | Font loading consistent across all apps | tests/integration/font-consistency.test.ts | Pending |
| IT-004 | INT-003, REQ-002-001-004, REQ-002-001-005 | Theme toggle sets data-theme correctly | tests/integration/theme-system.test.ts | Pending |
| IT-005 | REQ-002-003-001, REQ-002-003-002 | Theme persistence across page reloads | tests/integration/theme-persistence.test.ts | Pending |
| IT-006 | REQ-003-003-001, REQ-003-003-002 | Font size persistence across page reloads | tests/integration/font-size-persistence.test.ts | Pending |
| IT-007 | TECH-003, NFR-003 | Synchronous theme detection prevents FOUC | tests/integration/fouc-prevention.test.ts | Pending |
| IT-008 | TECH-006 | Shadow DOM components receive token injection | tests/integration/shadow-dom-tokens.test.ts | Pending |
| IT-009 | INT-005 | Lucide icons available in all three apps | tests/integration/icon-availability.test.ts | Pending |

---

## E2E Tests (Playwright)

| Test ID | Feature | Description | File | Status |
|---------|---------|-------------|------|--------|
| E2E-001 | FEAT-002-001 | ThemeToggle in CyberDemo: dark/light/system switch works visually | tests/e2e/theme-toggle-cyberdemo.spec.ts | Pending |
| E2E-002 | FEAT-003-001 | FontSizeButton in CyberDemo: cycles 16/18/20px | tests/e2e/font-size-cyberdemo.spec.ts | Pending |
| E2E-003 | FEAT-004-001 | CyberDemo pages load with correct tokens in both themes | tests/e2e/cyberdemo-migration.spec.ts | Pending |
| E2E-004 | FEAT-005-001 | Medicum pages load with correct tokens in both themes | tests/e2e/medicum-migration.spec.ts | Pending |
| E2E-005 | FEAT-006-001 | Files Manager loads with correct tokens, theme toggle works | tests/e2e/files-manager-migration.spec.ts | Pending |
| E2E-006 | FEAT-003-002 | FontSizeButton in Files Manager: cycles work | tests/e2e/font-size-files-manager.spec.ts | Pending |
| E2E-007 | FEAT-007-001 | Buttons across all apps match visual spec | tests/e2e/component-buttons.spec.ts | Pending |
| E2E-008 | FEAT-007-002 | Cards across all apps match visual spec | tests/e2e/component-cards.spec.ts | Pending |
| E2E-009 | FEAT-007-003 | Inputs across all apps match visual spec | tests/e2e/component-inputs.spec.ts | Pending |
| E2E-010 | FEAT-007-004 | Tables across all apps match visual spec | tests/e2e/component-tables.spec.ts | Pending |
| E2E-011 | FEAT-007-005 | Badges and toasts match visual spec | tests/e2e/component-badges-toasts.spec.ts | Pending |
| E2E-012 | FEAT-007-006 | Modals match visual spec | tests/e2e/component-modals.spec.ts | Pending |
| E2E-013 | FEAT-008-002 | Accessibility: focus indicators, ARIA, keyboard nav | tests/e2e/accessibility.spec.ts | Pending |

---

## Coverage Verification Matrix

| Req ID | UT IDs | IT IDs | E2E IDs | Coverage |
|--------|--------|--------|---------|----------|
| REQ-001-001-001 | UT-001 | IT-001 | - | [ ] Complete |
| REQ-001-001-002 | UT-002 | - | - | [ ] Complete |
| REQ-001-001-003 | UT-003 | - | - | [ ] Complete |
| REQ-001-001-004 | UT-004 | - | - | [ ] Complete |
| REQ-001-001-005 | UT-005 | - | - | [ ] Complete |
| REQ-002-001-001 | UT-012 | - | E2E-001 | [ ] Complete |
| REQ-003-001-001 | UT-026 | - | E2E-002 | [ ] Complete |
| REQ-004-001-001 | UT-036 | - | E2E-003 | [ ] Complete |
| REQ-005-001-001 | UT-063 | - | E2E-004 | [ ] Complete |
| REQ-006-001-001 | UT-088 | - | E2E-005 | [ ] Complete |
| TECH-001 | UT-132 | - | - | [ ] Complete |
| TECH-003 | UT-134 | IT-007 | - | [ ] Complete |
| TECH-006 | UT-137 | IT-008 | - | [ ] Complete |
| INT-001 | - | IT-001 | - | [ ] Complete |
| INT-002 | - | IT-002 | - | [ ] Complete |
| INT-003 | - | IT-004 | - | [ ] Complete |
| INT-004 | - | IT-003 | - | [ ] Complete |
| INT-005 | - | IT-009 | - | [ ] Complete |
| DATA-001 | UT-142 | - | - | [ ] Complete |
| NFR-001 | UT-146 | - | - | [ ] Complete |
| NFR-003 | UT-148 | IT-007 | - | [ ] Complete |
| NFR-010 | UT-155 | - | E2E-013 | [ ] Complete |

---
_Document generated by SoftwareBuilderX v21.0.0_
