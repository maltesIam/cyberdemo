# Build Plan: AgentFlow Design System Unification

| Attribute | Value |
|-----------|-------|
| Build ID | sbx-20260225-111316 |
| Created | 2026-02-25 |
| Functional Spec | docs/FUNCTIONAL_SPEC.md |
| Template Version | SBX v21.0.0 |

---

## Build CYCLE Phases

### Cycle 1: MTH (Must-To-Have)

| Phase | Description | Tasks | Status |
|-------|-------------|-------|--------|
| P1 | Design Token Foundation + Theme System + Font Size | 35 tasks | Pending |
| P2 | CyberDemo Migration | 27 tasks | Pending |
| P3 | Medicum Migration | 25 tasks | Pending |
| P4 | Files Manager Migration | 11 tasks | Pending |
| P5 | Component Standardization + Accessibility | 25 tasks | Pending |
| P6 | Technical, Integration, Data, NFR Requirements | 28 tasks | Pending |

### Cycle 2: NTH (Nice-To-Have)

| Phase | Description | Tasks | Status |
|-------|-------------|-------|--------|
| P7 | NTH Enhancements | 11 tasks | Pending |

---

## Task Assignments

### Build Agent Distribution

| Agent | Focus Area | Task Count |
|-------|------------|------------|
| Agent 1 | Tokens, Theme System, Font Size (P1) + TECH/INT/DATA/NFR (P6) | 63 |
| Agent 2 | CyberDemo Migration (P2) | 27 |
| Agent 3 | Medicum Migration (P3) | 25 |
| Agent 4 | Files Manager (P4) + Component Standards (P5) + NTH (P7) | 47 |

---

## Detailed Task List

### Phase P1: Design Token Foundation + Theme System + Font Size (MTH)

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-001 | REQ-001-001-001 | Create design-tokens.css with all AgentFlow CSS custom properties | 1 | Pending |
| T-002 | REQ-001-001-002 | Define :root block with all base/shared tokens | 1 | Pending |
| T-003 | REQ-001-001-003 | Define [data-theme="dark"] block with dark semantic tokens | 1 | Pending |
| T-004 | REQ-001-001-004 | Define [data-theme="light"] block with light semantic tokens | 1 | Pending |
| T-005 | REQ-001-001-005 | Validate token values match style guide v2.0 exactly | 1 | Pending |
| T-006 | REQ-001-002-001 | Extend CyberDemo tailwind.config.js to reference CSS custom properties | 1 | Pending |
| T-007 | REQ-001-002-002 | Extend Medicum tailwind.config.js replacing medical/severity palette | 1 | Pending |
| T-008 | REQ-001-002-003 | Configure Tailwind font families to Inter + JetBrains Mono | 1 | Pending |
| T-009 | REQ-001-003-001 | Load Inter font weights 300-800 in CyberDemo and Medicum | 1 | Pending |
| T-010 | REQ-001-003-002 | Load JetBrains Mono font weights 400, 600 in CyberDemo and Medicum | 1 | Pending |
| T-011 | REQ-001-003-003 | Verify Inter + JetBrains Mono already loaded in Files Manager | 1 | Pending |
| T-012 | REQ-002-001-001 | Create ThemeToggle React component with pill shape, 3 buttons | 1 | Pending |
| T-013 | REQ-002-001-002 | Active button primary-600 bg, inactive text-secondary | 1 | Pending |
| T-014 | REQ-002-001-003 | Dark=Moon, Light=Sun, System=Monitor Lucide icons | 1 | Pending |
| T-015 | REQ-002-001-004 | Click sets data-theme on html element | 1 | Pending |
| T-016 | REQ-002-001-005 | System reads prefers-color-scheme media query | 1 | Pending |
| T-017 | REQ-002-001-006 | Transition 200ms ease-default between states | 1 | Pending |
| T-018 | REQ-002-002-001 | Create theme-toggle LitElement web component | 1 | Pending |
| T-019 | REQ-002-002-002 | Lit component sets data-theme on document.documentElement | 1 | Pending |
| T-020 | REQ-002-002-003 | Place theme-toggle in Files Manager toolbar | 1 | Pending |
| T-021 | REQ-002-003-001 | Save theme to localStorage key theme-preference | 1 | Pending |
| T-022 | REQ-002-003-002 | Apply theme from localStorage before first paint | 1 | Pending |
| T-023 | REQ-002-003-003 | System mode detects OS preference on load | 1 | Pending |
| T-024 | REQ-002-003-004 | Default to dark if localStorage empty/unavailable | 1 | Pending |
| T-025 | REQ-002-003-005 | Body transition 300ms ease-default on theme switch | 1 | Pending |
| T-026 | REQ-003-001-001 | Create FontSizeButton React component with Lucide icon | 1 | Pending |
| T-027 | REQ-003-001-002 | Click cycles: 16px -> 18px -> 20px -> 16px | 1 | Pending |
| T-028 | REQ-003-001-003 | Modifies document.documentElement.style.fontSize | 1 | Pending |
| T-029 | REQ-003-001-004 | Button visually indicates current size state | 1 | Pending |
| T-030 | REQ-003-001-006 | Button placed LEFT of ThemeToggle in header | 1 | Pending |
| T-031 | REQ-003-002-001 | Create font-size-button LitElement component | 1 | Pending |
| T-032 | REQ-003-002-002 | Place next to theme-toggle in Files Manager toolbar | 1 | Pending |
| T-033 | REQ-003-003-001 | Save font-size-step to localStorage | 1 | Pending |
| T-034 | REQ-003-003-002 | Restore font size from localStorage before first paint | 1 | Pending |
| T-035 | REQ-003-003-003 | Default to step 0 (16px) if localStorage unavailable | 1 | Pending |

### Phase P2: CyberDemo Migration (MTH)

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-036 | REQ-004-001-001 | Update CyberDemo sidebar to design tokens | 2 | Pending |
| T-037 | REQ-004-001-002 | Update CyberDemo header with tokens, ThemeToggle, FontSizeButton | 2 | Pending |
| T-038 | REQ-004-001-003 | Update DemoControlBar, NarrationFooter, DemoFloatingWidget | 2 | Pending |
| T-039 | REQ-004-001-004 | Import design-tokens.css in CyberDemo entry point | 2 | Pending |
| T-040 | REQ-004-002-001 | Migrate /dashboard to design tokens | 2 | Pending |
| T-041 | REQ-004-002-002 | Migrate /generation to design tokens | 2 | Pending |
| T-042 | REQ-004-002-003 | Migrate /surface (Command Center) to design tokens | 2 | Pending |
| T-043 | REQ-004-003-001 | Migrate vulnerability pages (4 routes) to design tokens | 2 | Pending |
| T-044 | REQ-004-003-002 | Migrate /threats to design tokens | 2 | Pending |
| T-045 | REQ-004-003-003 | Migrate /incidents to design tokens | 2 | Pending |
| T-046 | REQ-004-003-004 | Migrate /detections to design tokens | 2 | Pending |
| T-047 | REQ-004-003-005 | Migrate /ctem to design tokens | 2 | Pending |
| T-048 | REQ-004-003-006 | Migrate /vulnerabilities/ssvc to design tokens | 2 | Pending |
| T-049 | REQ-004-004-001 | Migrate workflow canvas to design tokens | 2 | Pending |
| T-050 | REQ-004-004-002 | Migrate agent status badges to design tokens | 2 | Pending |
| T-051 | REQ-004-004-003 | Migrate execution timeline to design tokens | 2 | Pending |
| T-052 | REQ-004-004-004 | Migrate log viewer to design tokens | 2 | Pending |
| T-053 | REQ-004-004-005 | Migrate metric cards to design tokens | 2 | Pending |
| T-054 | REQ-004-005-001 | Migrate /timeline to design tokens | 2 | Pending |
| T-055 | REQ-004-005-002 | Migrate /postmortems to design tokens | 2 | Pending |
| T-056 | REQ-004-005-003 | Migrate /tickets to design tokens | 2 | Pending |
| T-057 | REQ-004-005-004 | Migrate /graph pages to design tokens | 2 | Pending |
| T-058 | REQ-004-005-005 | Migrate /collab to design tokens | 2 | Pending |
| T-059 | REQ-004-005-006 | Migrate /config to design tokens | 2 | Pending |
| T-060 | REQ-004-005-007 | Migrate /audit to design tokens | 2 | Pending |
| T-061 | REQ-004-005-008 | Migrate /simulation to design tokens | 2 | Pending |
| T-062 | REQ-004-005-009 | Migrate /assets to design tokens | 2 | Pending |

### Phase P3: Medicum Migration (MTH)

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-063 | REQ-005-001-001 | Update App.tsx body to var(--bg-primary) | 3 | Pending |
| T-064 | REQ-005-001-002 | Update PatientHeader to design tokens | 3 | Pending |
| T-065 | REQ-005-001-003 | Update allergy badges to semantic tokens | 3 | Pending |
| T-066 | REQ-005-001-004 | Update connection status dots to AgentFlow colors | 3 | Pending |
| T-067 | REQ-005-001-005 | Place ThemeToggle + FontSizeButton in PatientHeader | 3 | Pending |
| T-068 | REQ-005-001-006 | Update TabBar to design tokens | 3 | Pending |
| T-069 | REQ-005-001-007 | Import design-tokens.css + fonts in Medicum | 3 | Pending |
| T-070 | REQ-005-002-001 | Update Consulta transcription panel to tokens | 3 | Pending |
| T-071 | REQ-005-002-002 | Update chat bubbles to tokens | 3 | Pending |
| T-072 | REQ-005-002-003 | Update SOAP note panel to tokens | 3 | Pending |
| T-073 | REQ-005-002-004 | Update Whisper status badges to tokens | 3 | Pending |
| T-074 | REQ-005-002-005 | Update speaker toggle and buttons to tokens | 3 | Pending |
| T-075 | REQ-005-003-001 | Update Historia accordion sections to tokens | 3 | Pending |
| T-076 | REQ-005-003-002 | Update lab results table to token pattern | 3 | Pending |
| T-077 | REQ-005-003-003 | Update episode cards to tokens | 3 | Pending |
| T-078 | REQ-005-004-001 | Update Codificacion AI suggestions panel to tokens | 3 | Pending |
| T-079 | REQ-005-004-002 | CIE-10 codes font-mono with theme-aware primary color | 3 | Pending |
| T-080 | REQ-005-004-003 | Confidence badges with semantic tokens | 3 | Pending |
| T-081 | REQ-005-004-004 | Update search input and results to tokens | 3 | Pending |
| T-082 | REQ-005-004-005 | Update assigned codes panel to tokens | 3 | Pending |
| T-083 | REQ-005-005-001 | Update Visor toolbar to tokens | 3 | Pending |
| T-084 | REQ-005-005-002 | Visor image area stays dark in both themes | 3 | Pending |
| T-085 | REQ-005-005-003 | Update AI analysis panel to tokens | 3 | Pending |
| T-086 | REQ-005-005-004 | Update Visor finding cards and badges to tokens | 3 | Pending |
| T-087 | REQ-005-005-005 | Update radiological report block to tokens | 3 | Pending |

### Phase P4: Files Manager Migration (MTH)

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-088 | REQ-006-001-001 | Replace --files-bg-primary with --bg-primary dark | 4 | Pending |
| T-089 | REQ-006-001-002 | Replace --files-bg-secondary with --bg-secondary dark | 4 | Pending |
| T-090 | REQ-006-001-003 | Replace --files-bg-tertiary with --bg-tertiary dark | 4 | Pending |
| T-091 | REQ-006-001-004 | Replace --files-text-* with --text-* tokens | 4 | Pending |
| T-092 | REQ-006-001-005 | Replace --files-border with --border-* tokens | 4 | Pending |
| T-093 | REQ-006-001-006 | Update light theme values to AgentFlow spec | 4 | Pending |
| T-094 | REQ-006-001-007 | Add missing shadow, radius, spacing tokens | 4 | Pending |
| T-095 | REQ-006-002-001 | Integrate theme-toggle in Files Manager toolbar | 4 | Pending |
| T-096 | REQ-006-002-002 | Integrate font-size-button in Files Manager toolbar | 4 | Pending |
| T-097 | REQ-006-003-001 | Fix hardcoded colors in index.html | 4 | Pending |
| T-098 | REQ-006-003-002 | Fix hardcoded colors in files-epic002.ts | 4 | Pending |

### Phase P5: Component Standardization + Accessibility (MTH)

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-099 | REQ-007-001-001 | Primary buttons: primary-600 bg, hover primary-700 + translateY | 4 | Pending |
| T-100 | REQ-007-001-002 | Destructive buttons: color-error bg, hover error-dark | 4 | Pending |
| T-101 | REQ-007-001-003 | Button sizes: sm 32px, md 36px, lg 44px | 4 | Pending |
| T-102 | REQ-007-001-004 | Focus ring: 2px outline primary-500 | 4 | Pending |
| T-103 | REQ-007-001-005 | Disabled: opacity 0.5, cursor-not-allowed | 4 | Pending |
| T-104 | REQ-007-002-001 | Cards: bg-card, border-secondary, radius-xl, space-6 | 4 | Pending |
| T-105 | REQ-007-002-002 | Interactive cards: hover border-primary + shadow + translateY | 4 | Pending |
| T-106 | REQ-007-003-001 | Inputs: bg-input, border-primary, radius-lg, 36px | 4 | Pending |
| T-107 | REQ-007-003-002 | Input focus: border-focus + blue ring | 4 | Pending |
| T-108 | REQ-007-003-003 | Input error: red border + red ring | 4 | Pending |
| T-109 | REQ-007-003-004 | Placeholder: text-tertiary | 4 | Pending |
| T-110 | REQ-007-004-001 | Table headers: bg-tertiary, text-xs, uppercase | 4 | Pending |
| T-111 | REQ-007-004-002 | Table rows: text-sm, border-secondary, hover bg-hover | 4 | Pending |
| T-112 | REQ-007-005-001 | Badges: pill, text-xs, semantic 15% opacity bg | 4 | Pending |
| T-113 | REQ-007-005-002 | Toasts: bg-elevated, border-primary, shadow-lg, 380px | 4 | Pending |
| T-114 | REQ-007-006-001 | Modals: overlay blur, bg-elevated, radius-xl | 4 | Pending |
| T-115 | REQ-007-006-002 | Modal footer: right-aligned, space-3 gap | 4 | Pending |
| T-116 | REQ-008-001-001 | Color contrast 4.5:1 for text in dark theme | 4 | Pending |
| T-117 | REQ-008-001-002 | Color contrast 4.5:1 for text in light theme | 4 | Pending |
| T-118 | REQ-008-001-003 | UI component contrast 3:1 | 4 | Pending |
| T-119 | REQ-008-002-001 | Visible focus indicators on all interactive elements | 4 | Pending |
| T-120 | REQ-008-002-002 | Theme toggle ARIA labels and aria-pressed | 4 | Pending |
| T-121 | REQ-008-002-003 | Font size button ARIA label and announcements | 4 | Pending |
| T-122 | REQ-008-002-004 | Modal focus trap | 4 | Pending |
| T-123 | REQ-008-002-005 | Toast role="status" | 4 | Pending |

### Phase P6: Technical, Integration, Data, NFR Requirements (MTH)

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-132 | TECH-001 | CSS custom properties for cross-framework tokens | 1 | Pending |
| T-133 | TECH-002 | Design tokens importable in React and Lit | 1 | Pending |
| T-134 | TECH-003 | Synchronous theme detection in head | 1 | Pending |
| T-135 | TECH-004 | Font size modifies documentElement.style.fontSize | 1 | Pending |
| T-136 | TECH-005 | Tailwind uses var(--token) syntax | 1 | Pending |
| T-137 | TECH-006 | Shadow DOM token injection for Lit components | 1 | Pending |
| T-138 | TECH-007 | Preserve CyberDemo custom CSS animations | 1 | Pending |
| T-140 | TECH-009 | font-display: swap for web fonts | 1 | Pending |
| T-141 | TECH-010 | No hardcoded hex colors after migration | 1 | Pending |
| T-142 | INT-001 | Shared design-tokens.css between CyberDemo and Medicum | 1 | Pending |
| T-143 | INT-002 | Files Manager consumes same token values | 1 | Pending |
| T-144 | INT-003 | All apps respond to data-theme attribute | 1 | Pending |
| T-145 | INT-004 | Consistent font loading across apps | 1 | Pending |
| T-146 | INT-005 | Lucide icons available in all apps | 1 | Pending |
| T-147 | DATA-001 | localStorage theme-preference: dark/light/system | 1 | Pending |
| T-148 | DATA-002 | localStorage font-size-step: 0/1/2 | 1 | Pending |
| T-149 | DATA-003 | Per-origin localStorage scoping | 1 | Pending |
| T-150 | DATA-004 | No sensitive data in localStorage | 1 | Pending |
| T-151 | NFR-001 | Theme switch latency less than 300ms | 1 | Pending |
| T-152 | NFR-002 | Font size change latency less than 100ms | 1 | Pending |
| T-153 | NFR-003 | No FOUC on page load | 1 | Pending |
| T-154 | NFR-004 | 100% feature parity across themes | 1 | Pending |
| T-155 | NFR-005 | Graceful localStorage fallback | 1 | Pending |
| T-156 | NFR-006 | No sensitive data in localStorage | 1 | Pending |
| T-157 | NFR-007 | No XSS vectors in theme/font handling | 1 | Pending |
| T-160 | NFR-010 | WCAG 2.2 AA compliance both themes | 1 | Pending |
| T-161 | NFR-011 | Consistent keyboard navigation | 1 | Pending |
| T-162 | NFR-012 | Per-project preference persistence | 1 | Pending |

### Phase P7: NTH Enhancements

| Task ID | Requirement | Description | Agent | Status |
|---------|-------------|-------------|-------|--------|
| T-124 | REQ-003-001-005 | Tooltip shows current font size level name | 4 | Pending |
| T-125 | REQ-006-004-001 | Replace emoji action buttons with Lucide SVG icons | 4 | Pending |
| T-126 | REQ-006-004-002 | Add Lucide dependency or inline SVGs for Lit | 4 | Pending |
| T-127 | REQ-007-007-001 | Empty states: centered, 48px icon, text-lg title | 4 | Pending |
| T-128 | REQ-009-001-001 | Sidebar icon-only at 1024-1280px | 4 | Pending |
| T-129 | REQ-009-001-002 | Sidebar hamburger drawer below 1024px | 4 | Pending |
| T-130 | REQ-009-001-003 | Tables hide secondary columns at 1024-1280px | 4 | Pending |
| T-131 | REQ-009-001-004 | Tables horizontal scroll at 768-1024px | 4 | Pending |
| T-139 | TECH-008 | Build size increase less than 50KB from tokens + fonts | 4 | Pending |
| T-158 | NFR-008 | Token system extensible for future projects | 4 | Pending |
| T-159 | NFR-009 | Framework-agnostic CSS token architecture | 4 | Pending |

---

## REQUIREMENTS Coverage Matrix

| Requirement ID | Task ID | Test IDs | Status |
|----------------|---------|----------|--------|
| REQ-001-001-001 | T-001 | UT-001, IT-001 | [ ] |
| REQ-001-001-002 | T-002 | UT-002 | [ ] |
| REQ-001-001-003 | T-003 | UT-003 | [ ] |
| REQ-001-001-004 | T-004 | UT-004 | [ ] |
| REQ-001-001-005 | T-005 | UT-005 | [ ] |
| REQ-001-002-001 | T-006 | UT-006, IT-002 | [ ] |
| REQ-001-002-002 | T-007 | UT-007, IT-002 | [ ] |
| REQ-001-002-003 | T-008 | UT-008 | [ ] |
| REQ-001-003-001 | T-009 | UT-009, IT-003 | [ ] |
| REQ-001-003-002 | T-010 | UT-010, IT-003 | [ ] |
| REQ-001-003-003 | T-011 | UT-011 | [ ] |
| REQ-002-001-001 | T-012 | UT-012, E2E-001 | [ ] |
| REQ-002-001-002 | T-013 | UT-013 | [ ] |
| REQ-002-001-003 | T-014 | UT-014 | [ ] |
| REQ-002-001-004 | T-015 | UT-015, IT-004 | [ ] |
| REQ-002-001-005 | T-016 | UT-016, IT-004 | [ ] |
| REQ-002-001-006 | T-017 | UT-017 | [ ] |
| REQ-002-002-001 | T-018 | UT-018, E2E-005 | [ ] |
| REQ-002-002-002 | T-019 | UT-019 | [ ] |
| REQ-002-002-003 | T-020 | UT-020 | [ ] |
| REQ-002-003-001 | T-021 | UT-021, IT-005 | [ ] |
| REQ-002-003-002 | T-022 | UT-022, IT-005 | [ ] |
| REQ-002-003-003 | T-023 | UT-023 | [ ] |
| REQ-002-003-004 | T-024 | UT-024 | [ ] |
| REQ-002-003-005 | T-025 | UT-025 | [ ] |
| REQ-003-001-001 | T-026 | UT-026, E2E-002 | [ ] |
| REQ-003-001-002 | T-027 | UT-027 | [ ] |
| REQ-003-001-003 | T-028 | UT-028 | [ ] |
| REQ-003-001-004 | T-029 | UT-029 | [ ] |
| REQ-003-001-005 | T-124 | UT-124 | [ ] |
| REQ-003-001-006 | T-030 | UT-030 | [ ] |
| REQ-003-002-001 | T-031 | UT-031, E2E-006 | [ ] |
| REQ-003-002-002 | T-032 | UT-032 | [ ] |
| REQ-003-003-001 | T-033 | UT-033, IT-006 | [ ] |
| REQ-003-003-002 | T-034 | UT-034, IT-006 | [ ] |
| REQ-003-003-003 | T-035 | UT-035 | [ ] |
| REQ-004-001-001 | T-036 | UT-036, E2E-003 | [ ] |
| REQ-004-001-002 | T-037 | UT-037 | [ ] |
| REQ-004-001-003 | T-038 | UT-038 | [ ] |
| REQ-004-001-004 | T-039 | UT-039 | [ ] |
| REQ-004-002-001 | T-040 | UT-040, E2E-003 | [ ] |
| REQ-004-002-002 | T-041 | UT-041 | [ ] |
| REQ-004-002-003 | T-042 | UT-042 | [ ] |
| REQ-004-003-001 | T-043 | UT-043 | [ ] |
| REQ-004-003-002 | T-044 | UT-044 | [ ] |
| REQ-004-003-003 | T-045 | UT-045 | [ ] |
| REQ-004-003-004 | T-046 | UT-046 | [ ] |
| REQ-004-003-005 | T-047 | UT-047 | [ ] |
| REQ-004-003-006 | T-048 | UT-048 | [ ] |
| REQ-004-004-001 | T-049 | UT-049, E2E-003 | [ ] |
| REQ-004-004-002 | T-050 | UT-050 | [ ] |
| REQ-004-004-003 | T-051 | UT-051 | [ ] |
| REQ-004-004-004 | T-052 | UT-052 | [ ] |
| REQ-004-004-005 | T-053 | UT-053 | [ ] |
| REQ-004-005-001 | T-054 | UT-054 | [ ] |
| REQ-004-005-002 | T-055 | UT-055 | [ ] |
| REQ-004-005-003 | T-056 | UT-056 | [ ] |
| REQ-004-005-004 | T-057 | UT-057 | [ ] |
| REQ-004-005-005 | T-058 | UT-058 | [ ] |
| REQ-004-005-006 | T-059 | UT-059 | [ ] |
| REQ-004-005-007 | T-060 | UT-060 | [ ] |
| REQ-004-005-008 | T-061 | UT-061 | [ ] |
| REQ-004-005-009 | T-062 | UT-062 | [ ] |
| REQ-005-001-001 | T-063 | UT-063, E2E-004 | [ ] |
| REQ-005-001-002 | T-064 | UT-064 | [ ] |
| REQ-005-001-003 | T-065 | UT-065 | [ ] |
| REQ-005-001-004 | T-066 | UT-066 | [ ] |
| REQ-005-001-005 | T-067 | UT-067 | [ ] |
| REQ-005-001-006 | T-068 | UT-068 | [ ] |
| REQ-005-001-007 | T-069 | UT-069 | [ ] |
| REQ-005-002-001 | T-070 | UT-070, E2E-004 | [ ] |
| REQ-005-002-002 | T-071 | UT-071 | [ ] |
| REQ-005-002-003 | T-072 | UT-072 | [ ] |
| REQ-005-002-004 | T-073 | UT-073 | [ ] |
| REQ-005-002-005 | T-074 | UT-074 | [ ] |
| REQ-005-003-001 | T-075 | UT-075 | [ ] |
| REQ-005-003-002 | T-076 | UT-076 | [ ] |
| REQ-005-003-003 | T-077 | UT-077 | [ ] |
| REQ-005-004-001 | T-078 | UT-078 | [ ] |
| REQ-005-004-002 | T-079 | UT-079 | [ ] |
| REQ-005-004-003 | T-080 | UT-080 | [ ] |
| REQ-005-004-004 | T-081 | UT-081 | [ ] |
| REQ-005-004-005 | T-082 | UT-082 | [ ] |
| REQ-005-005-001 | T-083 | UT-083 | [ ] |
| REQ-005-005-002 | T-084 | UT-084 | [ ] |
| REQ-005-005-003 | T-085 | UT-085 | [ ] |
| REQ-005-005-004 | T-086 | UT-086 | [ ] |
| REQ-005-005-005 | T-087 | UT-087 | [ ] |
| REQ-006-001-001 | T-088 | UT-088, E2E-005 | [ ] |
| REQ-006-001-002 | T-089 | UT-089 | [ ] |
| REQ-006-001-003 | T-090 | UT-090 | [ ] |
| REQ-006-001-004 | T-091 | UT-091 | [ ] |
| REQ-006-001-005 | T-092 | UT-092 | [ ] |
| REQ-006-001-006 | T-093 | UT-093 | [ ] |
| REQ-006-001-007 | T-094 | UT-094 | [ ] |
| REQ-006-002-001 | T-095 | UT-095 | [ ] |
| REQ-006-002-002 | T-096 | UT-096 | [ ] |
| REQ-006-003-001 | T-097 | UT-097 | [ ] |
| REQ-006-003-002 | T-098 | UT-098 | [ ] |
| REQ-006-004-001 | T-125 | UT-125 | [ ] |
| REQ-006-004-002 | T-126 | UT-126 | [ ] |
| REQ-007-001-001 | T-099 | UT-099, E2E-007 | [ ] |
| REQ-007-001-002 | T-100 | UT-100 | [ ] |
| REQ-007-001-003 | T-101 | UT-101 | [ ] |
| REQ-007-001-004 | T-102 | UT-102 | [ ] |
| REQ-007-001-005 | T-103 | UT-103 | [ ] |
| REQ-007-002-001 | T-104 | UT-104, E2E-008 | [ ] |
| REQ-007-002-002 | T-105 | UT-105 | [ ] |
| REQ-007-003-001 | T-106 | UT-106, E2E-009 | [ ] |
| REQ-007-003-002 | T-107 | UT-107 | [ ] |
| REQ-007-003-003 | T-108 | UT-108 | [ ] |
| REQ-007-003-004 | T-109 | UT-109 | [ ] |
| REQ-007-004-001 | T-110 | UT-110, E2E-010 | [ ] |
| REQ-007-004-002 | T-111 | UT-111 | [ ] |
| REQ-007-005-001 | T-112 | UT-112, E2E-011 | [ ] |
| REQ-007-005-002 | T-113 | UT-113 | [ ] |
| REQ-007-006-001 | T-114 | UT-114, E2E-012 | [ ] |
| REQ-007-006-002 | T-115 | UT-115 | [ ] |
| REQ-007-007-001 | T-127 | UT-127 | [ ] |
| REQ-008-001-001 | T-116 | UT-116 | [ ] |
| REQ-008-001-002 | T-117 | UT-117 | [ ] |
| REQ-008-001-003 | T-118 | UT-118 | [ ] |
| REQ-008-002-001 | T-119 | UT-119, E2E-013 | [ ] |
| REQ-008-002-002 | T-120 | UT-120 | [ ] |
| REQ-008-002-003 | T-121 | UT-121 | [ ] |
| REQ-008-002-004 | T-122 | UT-122 | [ ] |
| REQ-008-002-005 | T-123 | UT-123 | [ ] |
| REQ-009-001-001 | T-128 | UT-128 | [ ] |
| REQ-009-001-002 | T-129 | UT-129 | [ ] |
| REQ-009-001-003 | T-130 | UT-130 | [ ] |
| REQ-009-001-004 | T-131 | UT-131 | [ ] |
| TECH-001 | T-132 | UT-132 | [ ] |
| TECH-002 | T-133 | UT-133 | [ ] |
| TECH-003 | T-134 | UT-134, IT-007 | [ ] |
| TECH-004 | T-135 | UT-135 | [ ] |
| TECH-005 | T-136 | UT-136 | [ ] |
| TECH-006 | T-137 | UT-137, IT-008 | [ ] |
| TECH-007 | T-138 | UT-138 | [ ] |
| TECH-008 | T-139 | UT-139 | [ ] |
| TECH-009 | T-140 | UT-140 | [ ] |
| TECH-010 | T-141 | UT-141 | [ ] |
| INT-001 | T-142 | IT-001 | [ ] |
| INT-002 | T-143 | IT-002 | [ ] |
| INT-003 | T-144 | IT-004 | [ ] |
| INT-004 | T-145 | IT-003 | [ ] |
| INT-005 | T-146 | IT-009 | [ ] |
| DATA-001 | T-147 | UT-142 | [ ] |
| DATA-002 | T-148 | UT-143 | [ ] |
| DATA-003 | T-149 | UT-144 | [ ] |
| DATA-004 | T-150 | UT-145 | [ ] |
| NFR-001 | T-151 | UT-146 | [ ] |
| NFR-002 | T-152 | UT-147 | [ ] |
| NFR-003 | T-153 | UT-148, IT-007 | [ ] |
| NFR-004 | T-154 | UT-149 | [ ] |
| NFR-005 | T-155 | UT-150 | [ ] |
| NFR-006 | T-156 | UT-151 | [ ] |
| NFR-007 | T-157 | UT-152 | [ ] |
| NFR-008 | T-158 | UT-153 | [ ] |
| NFR-009 | T-159 | UT-154 | [ ] |
| NFR-010 | T-160 | UT-155 | [ ] |
| NFR-011 | T-161 | UT-156 | [ ] |
| NFR-012 | T-162 | UT-157 | [ ] |

---
_Document generated by SoftwareBuilderX v21.0.0_
