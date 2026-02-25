# AgentFlow Design System Unification — Functional Specification

**Build ID:** sbx-20260225-102928
**Version:** 1.0.0
**Date:** February 2026
**Status:** Draft
**Template:** SBX v21.0.0

---

# PART 1: Functional Description

## 1.1 Executive Summary

This project unifies the visual design, UX, UI, and component system across three web applications in the SoulInTheBot ecosystem under the **AgentFlow Design System v2.0**. The scope includes migrating all pages and components to a shared CSS custom properties system, implementing a three-mode theme toggle (Dark/Light/System), and adding a cyclic font size accessibility control. The target is enterprise-grade visual consistency inspired by Linear, Vercel, Stripe, n8n, and other top-tier B2B platforms.

**Key Deliverables:**
- Shared design token system (CSS custom properties) adopted by all 3 projects
- Dark/Light/System theme toggle in every page header
- 3-step cyclic font size button (16px → 18px → 20px → 16px)
- All hardcoded colors replaced with semantic token references
- WCAG 2.2 AA compliance in both themes
- Inter + JetBrains Mono typography across all projects

**Target Applications:**
1. **CyberDemo Frontend** — React 18 + Tailwind CSS (18 routes, dark-only → dual theme)
2. **Medicum Demo** — React 18 + Tailwind + Zustand (4 tabs, light-only → dual theme)
3. **Files Manager** — Lit 3.1 Web Components + CSS Custom Properties (single-page, dark-first → dual theme with toggle)

## 1.2 System Overview

### 1.2.1 Purpose

Provide a unified, theme-aware, accessible visual layer for all SoulInTheBot web applications. Users moving between applications should experience zero visual friction — same colors, same typography, same component patterns, same theme preference.

### 1.2.2 Scope

- **In scope:** Visual redesign of all existing pages/views in all 3 target applications; shared design tokens; theme system; font size control; accessibility compliance; responsive layouts
- **Out of scope:** Backend logic changes; new features or pages; API changes; data model changes; business logic modifications

### 1.2.3 Context

The three applications currently have independent, inconsistent visual systems:
- CyberDemo: Dark-only, Tailwind gray-900/cyan-500, no tokens, custom animations
- Medicum: Light-only, custom medical-primary (#0066CC), system fonts, no CSS variables
- Files Manager: Dark-first with light overrides defined (no toggle), --files-* CSS variables, Inter + JetBrains Mono already

The AgentFlow Design System v2.0 (defined in `style-guide-v2.html` and `style-guide-light-v2.html`) provides the target specification for all visual values.

## 1.3 User Roles and Personas

| Persona ID | User Role | Description | Primary Actions |
|------------|-----------|-------------|-----------------|
| P-001 | **Security Analyst** | Uses CyberDemo for threat monitoring, incident response, vulnerability management | Browses dashboards, views attack graphs, manages incidents, reviews audit logs |
| P-002 | **Clinician** | Uses Medicum for patient consultations, medical coding, image analysis | Transcribes consultations, reviews history, assigns CIE-10 codes, analyzes medical images |
| P-003 | **System Administrator** | Uses Files Manager for file operations on the SoulInTheBot platform | Browses directories, uploads/downloads files, manages folders |
| P-004 | **Developer** | Maintains all three applications | Updates components, adds features, ensures consistency |
| P-005 | **Accessibility User** | Any user with visual or motor accessibility needs | Adjusts font size, uses keyboard navigation, relies on screen readers |

## 1.4 Functional Areas

### FA-001: Design Token System

**US-001:** As a developer, I want a single CSS custom properties file defining all visual values so that all three applications share identical design tokens.

**US-002:** As a developer, I want Tailwind CSS configured to reference design tokens so that I can use utility classes that automatically adapt to the active theme.

**BR-001:** All visual values (colors, spacing, typography, shadows, radii, z-index, transitions) MUST be defined as CSS custom properties in a single `design-tokens.css` file.

**BR-002:** No hardcoded color values, font sizes, or spacing values shall remain in any component after migration. All values must reference CSS custom properties.

**BR-003:** The design token file must define tokens for both `[data-theme="dark"]` and `[data-theme="light"]` selectors.

### FA-002: Theme System

**US-003:** As a user, I want to switch between Dark, Light, and System themes so that I can use my preferred visual mode.

**US-004:** As a user, I want my theme preference to persist across page reloads so that I do not have to re-select it each time.

**US-005:** As a user, I want the theme to switch smoothly without a flash of unstyled content.

**BR-004:** Theme switching is implemented by setting `data-theme` attribute on the `<html>` element.

**BR-005:** "System" mode detects OS preference via `prefers-color-scheme` media query and applies the corresponding theme.

**BR-006:** Theme preference is stored in `localStorage` under key `theme-preference` with values: `"dark"`, `"light"`, `"system"`.

**BR-007:** On page load, theme is applied from `localStorage` before first paint to prevent FOUC.

**BR-008:** Theme transition uses 300ms ease for background and color properties.

### FA-003: Font Size Accessibility Control

**US-006:** As a user with visual accessibility needs, I want to increase the font size with a single click so that I can read content more comfortably.

**US-007:** As a user, I want my font size preference to persist across sessions.

**BR-009:** Font size button cycles through 3 states: Normal (16px) → Medium (18px) → Large (20px) → Normal (16px).

**BR-010:** Font size scaling modifies `html { font-size }` since all sizes use `rem` units, causing proportional scaling of all text.

**BR-011:** Font size step is stored in `localStorage` under key `font-size-step` with values: `0`, `1`, `2`.

**BR-012:** The font size button is located immediately to the LEFT of the theme toggle in the page header.

### FA-004: CyberDemo Frontend Migration

**US-008:** As a security analyst, I want CyberDemo to support both dark and light themes while maintaining all existing functionality.

**US-009:** As a security analyst, I want a consistent, professional appearance across all 18 CyberDemo pages.

**BR-013:** All 18 routes in CyberDemo must render correctly in both Dark and Light themes.

**BR-014:** The sidebar, header, layout, DemoControlBar, NarrationFooter, and DemoFloatingWidget must use design tokens.

**BR-015:** Domain-specific components (workflow canvas, agent cards, execution timeline, log viewer, metric cards) must use design tokens.

**BR-016:** Current dark-only gray-900 backgrounds migrate to AgentFlow neutral-950 (#020617) in dark mode.

**BR-017:** Current cyan-500 accent color is preserved as the secondary color; primary becomes blue-600 (#2563eb).

### FA-005: Medicum Demo Migration

**US-010:** As a clinician, I want Medicum to support dark mode in addition to the current light mode.

**US-011:** As a clinician, I want medical-specific UI elements (confidence badges, CIE-10 codes, severity indicators) to remain clearly readable in both themes.

**BR-018:** Medicum's custom color palette maps to AgentFlow tokens: medical-primary (#0066CC) → primary-600 (#2563eb), severity-high → color-error, severity-medium → accent-500, severity-low → color-warning.

**BR-019:** System font stack is replaced with Inter (UI) + JetBrains Mono (code/ICD codes).

**BR-020:** All 4 tabs (Consulta, Historia, Codificación, Visor) must render correctly in both themes.

**BR-021:** The Visor tab image display area maintains a dark background (`--bg-primary` in dark, dedicated dark canvas in light) for proper medical image viewing.

**BR-022:** CIE-10 code text uses `font-mono` with theme-aware primary color for readability.

**BR-023:** Confidence badges retain their semantic color coding (green ≥90%, yellow ≥70%, gray below) using AgentFlow success/warning/neutral tokens.

### FA-006: Files Manager Migration

**US-012:** As a system administrator, I want a visible theme toggle in the Files Manager toolbar so I can switch themes.

**US-013:** As a system administrator, I want the Files Manager's visual design to match the other SoulInTheBot applications.

**BR-024:** The `--files-*` CSS variable namespace is remapped to AgentFlow standard `--bg-*`, `--text-*`, `--border-*`, `--color-*` tokens.

**BR-025:** Dark theme values update from `#1a1a2e/#16213e/#0f3460` to AgentFlow `#020617/#0f172a/#1e293b`.

**BR-026:** Light theme values update from `#ffffff/#f5f5f5/#ebebeb` to AgentFlow `#ffffff/#f8fafc/#f1f5f9`.

**BR-027:** Hardcoded colors in `index.html` (loading spinner, error banner) and `files-epic002.ts` (modal inline styles) are replaced with CSS variable references.

**BR-028:** Emoji action buttons (✂📋⬇🗑) are replaced with Lucide icons for visual consistency across all projects.

**BR-029:** Fonts (Inter + JetBrains Mono) are already present — no change needed.

### FA-007: Component Standardization

**US-014:** As a user, I want buttons, cards, inputs, tables, and other UI components to look and behave identically across all three applications.

**BR-030:** Button variants (Primary, Secondary, Ghost, Destructive, Accent) must follow the style guide spec in all projects.

**BR-031:** Cards use `bg-card` background, `border-secondary` border, `radius-xl`, `space-6` padding.

**BR-032:** Form inputs use `bg-input`, `border-primary`, `radius-lg`, with focus ring using `border-focus` + blue ring.

**BR-033:** Tables use `bg-tertiary` headers, `text-xs` uppercase, `border-secondary` row separators, `bg-hover` row hover.

**BR-034:** Badges use pill shape (`radius-full`), semantic color backgrounds at 15% opacity.

**BR-035:** Modals use `rgba(0,0,0,0.6)` overlay with backdrop blur, `bg-elevated` body, `radius-xl`, `shadow-xl`.

**BR-036:** Toast notifications use `bg-elevated`, `border-primary`, `shadow-lg`, max-width 380px.

**BR-037:** Empty states use centered layout, 48px icon at 50% opacity, `text-lg` title, `text-sm` description.

### FA-008: Accessibility

**US-015:** As a user with accessibility needs, I want all interactive elements to be navigable via keyboard.

**US-016:** As a screen reader user, I want proper ARIA labels on all interactive elements.

**BR-038:** WCAG 2.2 AA color contrast minimums: normal text 4.5:1, large text 3:1, UI components 3:1.

**BR-039:** All interactive elements have visible focus indicators using `border-focus` + 2px outline.

**BR-040:** Theme toggle has `aria-label="Theme selector"` with each button having `aria-pressed`.

**BR-041:** Font size button has `aria-label="Adjust font size"` and announces current level.

**BR-042:** Modal dialogs implement focus trap.

**BR-043:** Toast notifications use `role="status"`.

### FA-009: Responsive Design

**US-017:** As a user on a smaller screen, I want the layout to adapt gracefully so I can still use the application.

**BR-044:** Desktop-first approach with breakpoints at 640px, 768px, 1024px, 1280px, 1536px.

**BR-045:** Sidebar collapses to icon-only (56px) at 1024-1280px and to hamburger drawer below 1024px.

**BR-046:** Tables hide secondary columns at 1024-1280px and use horizontal scroll at 768-1024px.

## 1.5 Non-Functional Requirements Summary

| Category | ID | Requirement | Target |
|----------|----|-------------|--------|
| Performance | NFR-001 | Theme switch latency | Less than 300ms perceived transition |
| Performance | NFR-002 | Font size change latency | Less than 100ms reflow |
| Performance | NFR-003 | No FOUC on page load | Theme applied before first paint |
| Availability | NFR-004 | All three apps functional in both themes | 100% feature parity across themes |
| Availability | NFR-005 | Graceful degradation if localStorage unavailable | Falls back to dark theme |
| Security | NFR-006 | No sensitive data in localStorage | Only theme-preference and font-size-step |
| Security | NFR-007 | No XSS vectors in theme/font size handling | Strict value validation |
| Scalability | NFR-008 | Design tokens extensible for future projects | Modular CSS custom property architecture |
| Scalability | NFR-009 | Component patterns reusable across frameworks | Framework-agnostic CSS token system |
| Usability | NFR-010 | WCAG 2.2 AA compliance in both themes | All contrast ratios meet minimums |
| Usability | NFR-011 | Consistent keyboard navigation patterns | Tab, Enter/Space, Esc across all apps |
| Usability | NFR-012 | Theme and font preferences persist per-project | localStorage per application |

## 1.6 Assumptions and Dependencies

### Assumptions
- A-001: All three applications will continue to be served from their current tech stacks (React+Tailwind and Lit+CSS)
- A-002: The AgentFlow Design System v2.0 style guides (`style-guide-v2.html`, `style-guide-light-v2.html`) are the final, authoritative design reference
- A-003: Inter and JetBrains Mono fonts can be loaded via CDN or local files in all projects
- A-004: All users have modern browsers supporting CSS custom properties and `prefers-color-scheme`
- A-005: The existing functionality of all three applications remains unchanged — only visual presentation changes

### Dependencies
- D-001: `style-guide-v2.html` — Dark theme design reference
- D-002: `style-guide-light-v2.html` — Light theme design reference
- D-003: Lucide Icons library (already used in CyberDemo and Medicum)
- D-004: Inter font family (Google Fonts or local)
- D-005: JetBrains Mono font family (Google Fonts or local)
- D-006: Tailwind CSS 3.x (CyberDemo and Medicum)
- D-007: Lit 3.x (Files Manager)

## 1.7 Constraints

- C-001: No backend changes are permitted — this is a pure frontend visual migration
- C-002: All existing features must continue to work identically after migration
- C-003: No new npm dependencies beyond fonts and Lucide (if not already present)
- C-004: CyberDemo's custom CSS animations in `index.css` must be preserved and adapted to use design tokens
- C-005: Files Manager's Shadow DOM encapsulation must be respected — global CSS does not penetrate shadow roots
- C-006: Medicum's Zustand stores are unaffected — only view layer changes
- C-007: The image viewer dark background in Medicum Visor tab must remain dark even in light theme for proper medical image viewing

## 1.8 Project Context (Existing Codebase)

### CyberDemo Frontend
- **Location:** `cyberdemo/frontend/`
- **Stack:** React 18, Vite 5, Tailwind 3.4, TypeScript
- **Current state:** 18 routes, dark-only, Tailwind utility classes, custom CSS animations
- **Layout:** Sidebar + Header + Content area with DemoControlBar, NarrationFooter, DemoFloatingWidget
- **Key files:** `src/App.tsx`, `src/index.css`, `tailwind.config.js`, `src/components/Layout.tsx`

### Medicum Demo
- **Location:** `SoulInTheBot/AIPerson/person.ai/medicum-demo/`
- **Stack:** React 18, Vite 4, Tailwind 3.3, Zustand 4.4, TypeScript
- **Current state:** 4 tabs (Consulta, Historia, Codificacion, Visor), light-only, system fonts
- **Layout:** PatientHeader (sticky) + TabBar + Tab Content
- **Key files:** `src/App.tsx`, `src/index.css`, `tailwind.config.js`, `src/components/PatientHeader.tsx`, `src/components/TabBar.tsx`, `src/components/tabs/*.tsx`

### Files Manager
- **Location:** `SoulInTheBot/AIPerson/ui/`
- **Stack:** Lit 3.1, Vite 5.4, TypeScript
- **Current state:** Single-page, dark-first, CSS custom properties (`--files-*`), light overrides defined but no toggle
- **Layout:** Two-panel (sidebar + file list) with toolbar, modals, toasts
- **Key files:** `index.html`, `src/styles/files.css`, `src/ui/views/files.ts`, `src/ui/views/files-epic002.ts`
- **Components:** `<files-view>`, `<upload-progress-bar>`, `<delete-confirmation-modal>`, `<file-actions-buttons>`

---

# PART 2: Technical Requirements

## 2.1 Requirements Traceability Matrix (Brief)

| Source Type | Count | Traced To |
|-------------|-------|-----------|
| User Stories (US) | 17 | Requirements (REQ) |
| Business Rules (BR) | 46 | Requirements (REQ), Technical (TECH) |
| Non-Functional (NFR) | 12 | Technical (TECH), Integration (INT) |

## 2.2 Requirements Numbering Convention

| Type | Pattern | Example |
|------|---------|---------|
| Epic | `EPIC-XXX` | EPIC-001 |
| Feature | `FEAT-XXX-YYY` | FEAT-001-001 |
| Requirement | `REQ-XXX-YYY-ZZZ` | REQ-001-001-001 |
| Technical | `TECH-XXX` | TECH-001 |
| Integration | `INT-XXX` | INT-001 |
| Data | `DATA-XXX` | DATA-001 |
| Non-Functional | `NFR-XXX` | NFR-001 |

## 2.3 Priority Classification

| Priority | Label | Description |
|----------|-------|-------------|
| **MTH** | Must To Have | Required for minimum viable delivery. Without these, the system does not fulfill its purpose. |
| **NTH** | Nice To Have | Enhances quality/polish but not blocking. Can be deferred if needed. |

---

## 2.4 Epics, Features, and REQ Definitions

### EPIC-001: Design Token Foundation (MTH)
*Create the shared CSS custom properties system that all three applications will consume.*

#### FEAT-001-001: Design Tokens CSS File (MTH)
*Source: US-001, BR-001, BR-002, BR-003*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-001-001 | Create `design-tokens.css` file containing all CSS custom properties from the AgentFlow Design System v2.0 | MTH | File contains all color, spacing, typography, shadow, radius, z-index, transition, and breakpoint tokens |
| REQ-001-001-002 | Define `:root` block with all base/shared tokens (color scales, spacing, typography, etc.) | MTH | All 11 color primary shades, 11 secondary, 10 accent, 13 neutral, 12 semantic, 6 agent status tokens present |
| REQ-001-001-003 | Define `[data-theme="dark"]` block with dark-specific semantic tokens (bg, text, border, shadow) | MTH | All 8 bg-*, 5 text-*, 3 border-*, 1 shadow-card, 1 color-scheme tokens present |
| REQ-001-001-004 | Define `[data-theme="light"]` block with light-specific semantic tokens | MTH | All 8 bg-*, 5 text-*, 3 border-*, 1 shadow-card, 1 color-scheme tokens present |
| REQ-001-001-005 | Token values match exactly the style guide v2.0 specifications | MTH | Every token value matches the authoritative style guide documents |

#### FEAT-001-002: Tailwind Configuration (MTH)
*Source: US-002, BR-001*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-002-001 | Extend CyberDemo `tailwind.config.js` to reference CSS custom properties for colors | MTH | Tailwind classes like `bg-primary`, `text-primary` resolve to `var(--bg-primary)` etc. |
| REQ-001-002-002 | Extend Medicum `tailwind.config.js` to reference CSS custom properties, replacing medical/severity palette | MTH | `medical.*` and `severity.*` colors map to AgentFlow tokens |
| REQ-001-002-003 | Configure Tailwind font families to use Inter and JetBrains Mono | MTH | `font-sans` resolves to Inter, `font-mono` resolves to JetBrains Mono in both projects |

#### FEAT-001-003: Font Loading (MTH)
*Source: BR-019, BR-029*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-001-003-001 | Load Inter font (weights: 300, 400, 500, 600, 700, 800) in CyberDemo and Medicum | MTH | Inter renders correctly in all weights |
| REQ-001-003-002 | Load JetBrains Mono font (weights: 400, 600) in CyberDemo and Medicum | MTH | JetBrains Mono renders correctly for code/data elements |
| REQ-001-003-003 | Verify Inter and JetBrains Mono are already loaded in Files Manager | MTH | Fonts render correctly — no changes needed if already present |

---

### EPIC-002: Theme System (MTH)
*Implement the three-mode theme toggle across all applications.*

#### FEAT-002-001: Theme Toggle Component — React (MTH)
*Source: US-003, BR-004, BR-005*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-002-001-001 | Create `ThemeToggle` React component with pill-shaped container, 3 buttons (Dark/Light/System) | MTH | Pill shape with `radius-full`, `bg-tertiary`, 1px `border-primary` |
| REQ-002-001-002 | Active button shows `primary-600` background with white text; inactive buttons show `text-secondary` | MTH | Visual distinction between active and inactive states |
| REQ-002-001-003 | Dark button uses Moon icon, Light uses Sun icon, System uses Monitor icon (Lucide) | MTH | Correct icons render for each option |
| REQ-002-001-004 | Clicking a button sets `data-theme` attribute on `<html>` element | MTH | Document element reflects selected theme |
| REQ-002-001-005 | System option reads `prefers-color-scheme` media query and applies matching theme | MTH | System option mirrors OS preference |
| REQ-002-001-006 | Transition between states uses `duration-normal` (200ms) with `ease-default` | MTH | Smooth visual transition on button click |

#### FEAT-002-002: Theme Toggle Component — Lit (MTH)
*Source: US-012, BR-004, BR-005*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-002-002-001 | Create `<theme-toggle>` LitElement web component with identical visual spec as React version | MTH | Same pill shape, icons, colors, transitions |
| REQ-002-002-002 | Component sets `data-theme` on `document.documentElement` (outside Shadow DOM) | MTH | Theme attribute is on `<html>`, not inside shadow root |
| REQ-002-002-003 | Place `<theme-toggle>` in the Files Manager toolbar area | MTH | Toggle visible and functional in toolbar |

#### FEAT-002-003: Theme Persistence and FOUC Prevention (MTH)
*Source: US-004, US-005, BR-006, BR-007, BR-008*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-002-003-001 | Save theme preference to `localStorage` key `theme-preference` on every change | MTH | Value persists after page reload |
| REQ-002-003-002 | On page load, read `localStorage` and apply theme BEFORE first paint (inline script in `<head>`) | MTH | No flash of wrong theme on page load |
| REQ-002-003-003 | If `localStorage` value is "system", detect OS preference and apply corresponding theme | MTH | System preference correctly detected on load |
| REQ-002-003-004 | If `localStorage` is empty or unavailable, default to "dark" theme | MTH | Graceful fallback behavior |
| REQ-002-003-005 | Theme transition on `<body>` uses `duration-slow` (300ms) + `ease-default` for background and color | MTH | Smooth visual transition when switching |

---

### EPIC-003: Font Size Accessibility Control (MTH)
*Implement the cyclic font size button across all applications.*

#### FEAT-003-001: Font Size Button Component — React (MTH)
*Source: US-006, BR-009, BR-010, BR-012*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-003-001-001 | Create `FontSizeButton` React component with typography icon (Lucide "Type" or "ALargeSmall") | MTH | Icon button renders correctly |
| REQ-003-001-002 | Click cycles through 3 states: step 0 (16px) → step 1 (18px) → step 2 (20px) → step 0 (16px) | MTH | Font size changes on each click in cyclic order |
| REQ-003-001-003 | Modify `document.documentElement.style.fontSize` to set the new base size | MTH | All rem-based sizes scale proportionally |
| REQ-003-001-004 | Button visually indicates current state (e.g., small/medium/large "A" text, or dot indicators) | MTH | User can see which size level is active |
| REQ-003-001-005 | Tooltip on hover shows "Font size: Normal / Medium / Large" corresponding to current state | NTH | Tooltip provides context |
| REQ-003-001-006 | Place button to the LEFT of ThemeToggle in page header | MTH | Correct positioning |

#### FEAT-003-002: Font Size Button Component — Lit (MTH)
*Source: US-006, BR-009, BR-010*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-003-002-001 | Create `<font-size-button>` LitElement web component with identical behavior as React version | MTH | Same cycling, same visual feedback |
| REQ-003-002-002 | Place next to `<theme-toggle>` in Files Manager toolbar | MTH | Button visible and functional in toolbar |

#### FEAT-003-003: Font Size Persistence (MTH)
*Source: US-007, BR-011*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-003-003-001 | Save font size step to `localStorage` key `font-size-step` (values: "0", "1", "2") | MTH | Value persists after page reload |
| REQ-003-003-002 | On page load, restore font size from `localStorage` before first paint | MTH | Correct font size on load, no reflow flash |
| REQ-003-003-003 | If `localStorage` is empty or unavailable, default to step 0 (16px) | MTH | Graceful fallback |

---

### EPIC-004: CyberDemo Frontend Migration (MTH)
*Migrate all CyberDemo pages and components to the AgentFlow Design System.*

#### FEAT-004-001: CyberDemo Layout and Navigation (MTH)
*Source: US-008, US-009, BR-013, BR-014*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-004-001-001 | Update sidebar navigation to use design tokens (bg-secondary, text-secondary, hover: bg-hover, active: primary tint) | MTH | Sidebar renders correctly in both themes |
| REQ-004-001-002 | Update sticky header to use tokens (bg-primary at 0.8 opacity, backdrop blur) with ThemeToggle and FontSizeButton | MTH | Header renders correctly, controls functional |
| REQ-004-001-003 | Update DemoControlBar, NarrationFooter, and DemoFloatingWidget to use design tokens | MTH | All layout widgets render correctly in both themes |
| REQ-004-001-004 | Import `design-tokens.css` in the application entry point | MTH | Tokens available globally |

#### FEAT-004-002: CyberDemo Dashboard and Main Pages (MTH)
*Source: BR-013, BR-016, BR-017*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-004-002-001 | Migrate `/dashboard` page: metric cards, charts, activity feed to design tokens | MTH | Dashboard renders correctly in both themes |
| REQ-004-002-002 | Migrate `/generation` (home) page to design tokens | MTH | Page renders correctly in both themes |
| REQ-004-002-003 | Migrate `/surface` (Command Center) page to design tokens | MTH | Page renders correctly in both themes |

#### FEAT-004-003: CyberDemo Security Pages (MTH)
*Source: BR-013*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-004-003-001 | Migrate `/vulnerabilities`, CVE detail, CVE assets, CVE exploits pages to design tokens | MTH | All vulnerability pages render correctly in both themes |
| REQ-004-003-002 | Migrate `/threats` page to design tokens | MTH | Page renders correctly in both themes |
| REQ-004-003-003 | Migrate `/incidents` page to design tokens | MTH | Page renders correctly in both themes |
| REQ-004-003-004 | Migrate `/detections` page to design tokens | MTH | Page renders correctly in both themes |
| REQ-004-003-005 | Migrate `/ctem` page to design tokens | MTH | Page renders correctly in both themes |
| REQ-004-003-006 | Migrate `/vulnerabilities/ssvc` page to design tokens | MTH | Page renders correctly in both themes |

#### FEAT-004-004: CyberDemo Domain Components (MTH)
*Source: BR-015*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-004-004-001 | Migrate workflow canvas (dot grid, nodes, connections, ports) to design tokens | MTH | Canvas renders correctly in both themes |
| REQ-004-004-002 | Migrate agent status badges (running, idle, success, error, waiting, queued) to design tokens | MTH | Status badges display correct colors and animations |
| REQ-004-004-003 | Migrate execution timeline to design tokens | MTH | Timeline renders correctly in both themes |
| REQ-004-004-004 | Migrate log viewer to design tokens | MTH | Log viewer renders correctly in both themes |
| REQ-004-004-005 | Migrate metric cards to design tokens | MTH | Metric cards render correctly in both themes |

#### FEAT-004-005: CyberDemo Utility Pages (MTH)
*Source: BR-013*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-004-005-001 | Migrate `/timeline` page to design tokens | MTH | Page renders correctly in both themes |
| REQ-004-005-002 | Migrate `/postmortems` page to design tokens | MTH | Page renders correctly in both themes |
| REQ-004-005-003 | Migrate `/tickets` page to design tokens | MTH | Page renders correctly in both themes |
| REQ-004-005-004 | Migrate `/graph` and `/graph/:incidentId` pages to design tokens | MTH | Attack graph renders correctly in both themes |
| REQ-004-005-005 | Migrate `/collab` page to design tokens | MTH | Page renders correctly in both themes |
| REQ-004-005-006 | Migrate `/config` page to design tokens | MTH | Page renders correctly in both themes |
| REQ-004-005-007 | Migrate `/audit` page to design tokens | MTH | Page renders correctly in both themes |
| REQ-004-005-008 | Migrate `/simulation` page to design tokens | MTH | Page renders correctly in both themes |
| REQ-004-005-009 | Migrate `/assets` page to design tokens | MTH | Page renders correctly in both themes |

---

### EPIC-005: Medicum Demo Migration (MTH)
*Migrate all Medicum tabs and components to the AgentFlow Design System.*

#### FEAT-005-001: Medicum Base Layout and Header (MTH)
*Source: US-010, BR-018, BR-019*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-005-001-001 | Update `App.tsx` body background from `bg-gray-100` to `var(--bg-primary)` | MTH | Body background adapts to theme |
| REQ-005-001-002 | Update `PatientHeader` from `bg-white` to `var(--bg-elevated)`, text/border to tokens | MTH | Header renders correctly in both themes |
| REQ-005-001-003 | Update allergy badges to use AgentFlow semantic tokens (error/warning/accent) | MTH | Badges readable in both themes |
| REQ-005-001-004 | Update connection status dots to use AgentFlow success/warning/error colors | MTH | Status correctly colored in both themes |
| REQ-005-001-005 | Place ThemeToggle and FontSizeButton in PatientHeader top-right | MTH | Controls visible and functional |
| REQ-005-001-006 | Update `TabBar` from `bg-white` to `var(--bg-elevated)`, active tab to primary token | MTH | Tab bar renders correctly in both themes |
| REQ-005-001-007 | Import `design-tokens.css` and Inter + JetBrains Mono fonts | MTH | Tokens and fonts available |

#### FEAT-005-002: Medicum Consulta Tab (MTH)
*Source: BR-020*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-005-002-001 | Update transcription panel from `bg-white` cards to token-based backgrounds | MTH | Panel renders correctly in both themes |
| REQ-005-002-002 | Update chat bubbles: doctor (primary) and patient (secondary/tertiary) to tokens | MTH | Bubbles readable in both themes |
| REQ-005-002-003 | Update SOAP note panel to token-based backgrounds and text colors | MTH | SOAP sections readable in both themes |
| REQ-005-002-004 | Update Whisper status badges to semantic tokens | MTH | Status badges correctly colored |
| REQ-005-002-005 | Update speaker toggle and listen/demo buttons to design token colors | MTH | Buttons render correctly in both themes |

#### FEAT-005-003: Medicum Historia Tab (MTH)
*Source: BR-020*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-005-003-001 | Update accordion sections from `bg-gray-50`/`bg-white` to token-based backgrounds | MTH | Accordions render correctly in both themes |
| REQ-005-003-002 | Update lab results table to use table design token pattern | MTH | Table readable in both themes with correct value coloring |
| REQ-005-003-003 | Update episode cards to token-based backgrounds | MTH | Cards render correctly in both themes |

#### FEAT-005-004: Medicum Codificacion Tab (MTH)
*Source: BR-020, BR-022, BR-023*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-005-004-001 | Update AI suggestions panel to token-based backgrounds | MTH | Panel renders correctly in both themes |
| REQ-005-004-002 | Update CIE-10 code display: `font-mono` with `var(--color-primary-600)` in light / `var(--color-primary-400)` in dark | MTH | ICD codes clearly readable in both themes |
| REQ-005-004-003 | Update confidence badges: green (>=90% success), yellow (>=70% warning), gray (below neutral) using semantic tokens | MTH | Badges semantically correct and readable |
| REQ-005-004-004 | Update search input and results dropdown to design token pattern | MTH | Search UI renders correctly in both themes |
| REQ-005-004-005 | Update assigned codes panel (primary/secondary distinction) to tokens | MTH | Code cards render correctly in both themes |

#### FEAT-005-005: Medicum Visor Tab (MTH)
*Source: BR-020, BR-021*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-005-005-001 | Update image viewer toolbar to token-based backgrounds | MTH | Toolbar renders correctly in both themes |
| REQ-005-005-002 | Keep image display area dark (`bg-gray-900` to `--color-neutral-900`) in BOTH themes for medical image viewing | MTH | Image area always dark for proper viewing |
| REQ-005-005-003 | Update AI analysis panel to token-based backgrounds | MTH | Panel renders correctly in both themes |
| REQ-005-005-004 | Update finding cards and confidence badges to semantic tokens | MTH | Findings readable in both themes |
| REQ-005-005-005 | Update radiological report block to token-based background | MTH | Report block readable in both themes |

---

### EPIC-006: Files Manager Migration (MTH)
*Migrate Files Manager to the AgentFlow Design System.*

#### FEAT-006-001: Files Manager CSS Variable Remapping (MTH)
*Source: US-013, BR-024, BR-025, BR-026*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-006-001-001 | Replace `--files-bg-primary` (#1a1a2e) with `--bg-primary` (#020617) in dark theme | MTH | Background matches AgentFlow spec |
| REQ-006-001-002 | Replace `--files-bg-secondary` (#16213e) with `--bg-secondary` (#0f172a) in dark theme | MTH | Background matches AgentFlow spec |
| REQ-006-001-003 | Replace `--files-bg-tertiary` (#0f3460) with `--bg-tertiary` (#1e293b) in dark theme | MTH | Background matches AgentFlow spec |
| REQ-006-001-004 | Replace `--files-text-*` variables with `--text-primary/secondary/tertiary` AgentFlow tokens | MTH | Text colors match AgentFlow spec |
| REQ-006-001-005 | Replace `--files-border`/`--files-border-subtle` with `--border-primary`/`--border-secondary` tokens | MTH | Border colors match AgentFlow spec |
| REQ-006-001-006 | Update `[data-theme="light"]` override values to match AgentFlow light tokens | MTH | Light theme matches AgentFlow spec |
| REQ-006-001-007 | Add missing AgentFlow tokens (shadows, radii, spacing, z-index, transitions) to the CSS variable system | MTH | All required tokens available |

#### FEAT-006-002: Files Manager Theme Toggle and Font Size (MTH)
*Source: US-012, BR-024*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-006-002-001 | Integrate `<theme-toggle>` component in toolbar | MTH | Toggle visible and functional |
| REQ-006-002-002 | Integrate `<font-size-button>` component in toolbar, to the left of theme toggle | MTH | Button visible and functional |

#### FEAT-006-003: Files Manager Hardcoded Color Fixes (MTH)
*Source: BR-027*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-006-003-001 | Replace hardcoded colors in `index.html` (body bg #1a1a2e, text #e0e0e0, spinner #4a9eff, error banner #ff4444) with CSS variable references | MTH | No hardcoded colors in index.html |
| REQ-006-003-002 | Replace hardcoded colors in `files-epic002.ts` inline styles (modal backdrop rgba, box-shadow values) with CSS variable references | MTH | No hardcoded colors in component inline styles |

#### FEAT-006-004: Files Manager Icon Standardization (NTH)
*Source: BR-028*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-006-004-001 | Replace emoji action buttons with Lucide SVG icons (Scissors, Copy, Download, Trash2) | NTH | Icons render consistently, matching other projects |
| REQ-006-004-002 | Add Lucide icon dependency or inline SVGs in the Lit component | NTH | Icons available without breaking build |

---

### EPIC-007: Component Standardization (MTH)
*Ensure all UI components follow the AgentFlow Design System patterns across all projects.*

#### FEAT-007-001: Button Standardization (MTH)
*Source: US-014, BR-030*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-007-001-001 | All primary buttons across all 3 apps use `primary-600` bg, white text, hover `primary-700` + translateY(-1px) | MTH | Primary buttons visually consistent |
| REQ-007-001-002 | All destructive buttons use `color-error` bg, white text, hover `error-dark` | MTH | Destructive buttons visually consistent |
| REQ-007-001-003 | Button sizes follow spec: sm (32px), md (36px), lg (44px) with corresponding padding and font size | MTH | Button sizes consistent |
| REQ-007-001-004 | All buttons have focus ring: 2px outline `primary-500` | MTH | Focus indicators visible |
| REQ-007-001-005 | Disabled buttons use opacity 0.5 and cursor-not-allowed | MTH | Disabled state consistent |

#### FEAT-007-002: Card Standardization (MTH)
*Source: BR-031*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-007-002-001 | All card components use `bg-card`, `border-secondary`, `radius-xl`, `space-6` padding | MTH | Cards visually consistent |
| REQ-007-002-002 | Interactive cards have hover: `border-primary` + `shadow-card` + translateY(-2px) | MTH | Hover effect consistent |

#### FEAT-007-003: Form Input Standardization (MTH)
*Source: BR-032*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-007-003-001 | All text inputs use `bg-input`, `border-primary`, `radius-lg`, 36px height | MTH | Inputs visually consistent |
| REQ-007-003-002 | Focus state: `border-focus` + 3px blue ring | MTH | Focus ring visible and consistent |
| REQ-007-003-003 | Error state: red border + red ring | MTH | Error state visible |
| REQ-007-003-004 | Placeholder text uses `text-tertiary` | MTH | Placeholder color consistent |

#### FEAT-007-004: Table Standardization (MTH)
*Source: BR-033*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-007-004-001 | Table headers use `bg-tertiary`, `text-xs`, uppercase, `weight-medium`, letter-spacing 0.05em | MTH | Table headers consistent |
| REQ-007-004-002 | Table rows use `text-sm`, `text-primary`, `border-secondary` bottom, hover `bg-hover` | MTH | Table rows consistent |

#### FEAT-007-005: Badge and Toast Standardization (MTH)
*Source: BR-034, BR-036*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-007-005-001 | All badges use pill shape, `text-xs`, semantic color bg at 15% opacity | MTH | Badges visually consistent |
| REQ-007-005-002 | Toast notifications use `bg-elevated`, `border-primary`, `shadow-lg`, max-width 380px | MTH | Toasts visually consistent |

#### FEAT-007-006: Modal Standardization (MTH)
*Source: BR-035*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-007-006-001 | All modals use `rgba(0,0,0,0.6)` overlay + backdrop blur, `bg-elevated`, `radius-xl`, `shadow-xl` | MTH | Modals visually consistent |
| REQ-007-006-002 | Modal footer buttons right-aligned with `space-3` gap | MTH | Footer layout consistent |

#### FEAT-007-007: Empty State Standardization (NTH)
*Source: BR-037*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-007-007-001 | All empty states use centered layout, 48px icon at 50% opacity, `text-lg` title, `text-sm` description | NTH | Empty states visually consistent |

---

### EPIC-008: Accessibility Compliance (MTH)
*Ensure WCAG 2.2 AA compliance across all applications.*

#### FEAT-008-001: Color Contrast Compliance (MTH)
*Source: US-015, BR-038*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-008-001-001 | All text/background combinations meet 4.5:1 contrast ratio in dark theme | MTH | Contrast audit passes |
| REQ-008-001-002 | All text/background combinations meet 4.5:1 contrast ratio in light theme | MTH | Contrast audit passes |
| REQ-008-001-003 | All UI components (borders, icons, indicators) meet 3:1 contrast ratio | MTH | Component contrast audit passes |

#### FEAT-008-002: Keyboard Navigation and ARIA (MTH)
*Source: US-015, US-016, BR-039, BR-040, BR-041, BR-042, BR-043*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-008-002-001 | All interactive elements have visible focus indicators | MTH | Tab navigation shows focus ring on every element |
| REQ-008-002-002 | Theme toggle has `aria-label="Theme selector"` and each button has `aria-pressed` | MTH | Screen reader announces correctly |
| REQ-008-002-003 | Font size button has `aria-label="Adjust font size"` and announces current level | MTH | Screen reader announces correctly |
| REQ-008-002-004 | Modal dialogs implement focus trap | MTH | Tab key cycles within modal only |
| REQ-008-002-005 | Toast notifications use `role="status"` | MTH | Screen reader announces toasts |

---

### EPIC-009: Responsive Design (NTH)
*Implement responsive layout patterns across all applications.*

#### FEAT-009-001: Responsive Layout Adaptation (NTH)
*Source: US-017, BR-044, BR-045, BR-046*

| Req ID | Description | Priority | Acceptance Criteria |
|--------|-------------|----------|---------------------|
| REQ-009-001-001 | Sidebar collapses to 56px icon-only at 1024-1280px breakpoint | NTH | Layout adapts at breakpoint |
| REQ-009-001-002 | Sidebar becomes hamburger drawer below 1024px | NTH | Drawer toggles correctly |
| REQ-009-001-003 | Tables hide secondary columns at 1024-1280px | NTH | Tables remain usable |
| REQ-009-001-004 | Tables use horizontal scroll at 768-1024px | NTH | Tables scrollable |

---

## 2.5 Technical Requirements

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| TECH-001 | Use CSS custom properties (not SASS/LESS variables) as the token system for cross-framework compatibility | MTH | BR-001, C-005 |
| TECH-002 | Design tokens file must be importable in both React (CSS import) and Lit (adoptedStyleSheets or link injection) | MTH | BR-001, C-005 |
| TECH-003 | Theme detection script must execute synchronously in `<head>` before body renders to prevent FOUC | MTH | BR-007, NFR-003 |
| TECH-004 | Font size modification targets `document.documentElement.style.fontSize` for global rem scaling | MTH | BR-010 |
| TECH-005 | All Tailwind config extensions must use `var(--token-name)` syntax to reference CSS custom properties | MTH | BR-001 |
| TECH-006 | Files Manager Shadow DOM components that need theme tokens must inject the design-tokens.css into their shadow root | MTH | C-005 |
| TECH-007 | CyberDemo custom CSS animations in `index.css` must be preserved, with color references updated to tokens | MTH | C-004 |
| TECH-008 | Build output size should not increase more than 50KB from font loading and token file | NTH | NFR-001 |
| TECH-009 | Use `font-display: swap` for web font loading to prevent invisible text | MTH | NFR-001 |
| TECH-010 | Validate that no hardcoded hex color values remain in any component source file after migration | MTH | BR-002 |

## 2.6 Integration Requirements

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| INT-001 | CyberDemo and Medicum must share the same `design-tokens.css` file (copy or symlink) to ensure token parity | MTH | BR-001, US-001 |
| INT-002 | Files Manager must consume the same token values, adapted for its CSS variable system | MTH | BR-024 |
| INT-003 | All three applications must respond identically to `data-theme` attribute changes on `<html>` | MTH | BR-004 |
| INT-004 | Font loading (Inter, JetBrains Mono) must be consistent across all three applications | MTH | BR-019, BR-029 |
| INT-005 | Lucide icons must be available in all three applications (npm package for React, SVG inlines or CDN for Lit) | MTH | BR-028, D-003 |

## 2.7 Data Requirements

| Req ID | Description | Priority | Source |
|--------|-------------|----------|--------|
| DATA-001 | `localStorage` key `theme-preference` stores string values: `"dark"`, `"light"`, `"system"` | MTH | BR-006 |
| DATA-002 | `localStorage` key `font-size-step` stores string values: `"0"`, `"1"`, `"2"` | MTH | BR-011 |
| DATA-003 | Both localStorage keys are scoped per-origin (natural browser behavior — each app has its own domain/port) | MTH | BR-006 |
| DATA-004 | No sensitive data stored in localStorage — only UI preference values | MTH | NFR-006 |

## 2.7b Non-Functional Requirements (Detailed)

### Performance

| Req ID | Description | Priority | Target | Source |
|--------|-------------|----------|--------|--------|
| NFR-001 | Theme switch perceived latency must be under 300ms | MTH | Less than 300ms | BR-008 |
| NFR-002 | Font size change reflow must complete under 100ms | MTH | Less than 100ms | BR-010 |
| NFR-003 | No FOUC on page load — theme applied before first paint via inline head script | MTH | Zero visible flash | BR-007, TECH-003 |

### Availability

| Req ID | Description | Priority | Target | Source |
|--------|-------------|----------|--------|--------|
| NFR-004 | All features in all three apps must be fully functional in both themes | MTH | 100% feature parity | BR-013, BR-020 |
| NFR-005 | If localStorage is unavailable, fall back to dark theme gracefully | MTH | No crash or broken UI | BR-006 |

### Security

| Req ID | Description | Priority | Target | Source |
|--------|-------------|----------|--------|--------|
| NFR-006 | Only non-sensitive UI preferences stored in localStorage (theme-preference, font-size-step) | MTH | No PII or secrets | DATA-004 |
| NFR-007 | Theme and font size handling must not introduce XSS vectors — strict value validation on localStorage reads | MTH | Zero injection risk | BR-004, BR-010 |

### Scalability

| Req ID | Description | Priority | Target | Source |
|--------|-------------|----------|--------|--------|
| NFR-008 | Design token architecture must be extensible for future projects without breaking existing apps | NTH | Modular CSS custom properties | BR-001 |
| NFR-009 | Component patterns must be reusable across React and Lit frameworks via framework-agnostic CSS tokens | NTH | Same tokens work in both | TECH-001, TECH-002 |

### Usability

| Req ID | Description | Priority | Target | Source |
|--------|-------------|----------|--------|--------|
| NFR-010 | All text/background combinations meet WCAG 2.2 AA contrast ratios in both themes | MTH | 4.5:1 text, 3:1 UI | BR-038 |
| NFR-011 | Keyboard navigation patterns (Tab, Enter/Space, Esc) must be consistent across all three applications | MTH | Full keyboard access | BR-039 |
| NFR-012 | Theme and font size preferences persist per-project via localStorage | MTH | Survives page reload | BR-006, BR-011 |

## 2.8 Full Traceability Matrix

| Req ID | Source | Description | Priority | Code | Tests | Verified |
|--------|--------|-------------|----------|------|-------|----------|
| REQ-001-001-001 | US-001, BR-001 | Create design-tokens.css with all AgentFlow CSS custom properties | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-002 | US-001, BR-001 | Define :root block with all base/shared tokens | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-003 | BR-003 | Define [data-theme="dark"] block with dark semantic tokens | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-004 | BR-003 | Define [data-theme="light"] block with light semantic tokens | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-005 | BR-001 | Token values match style guide v2.0 exactly | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-001 | US-002, BR-001 | Extend CyberDemo tailwind.config.js to reference CSS custom properties | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-002 | US-002, BR-001 | Extend Medicum tailwind.config.js replacing medical/severity palette | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-003 | BR-019 | Configure Tailwind font families to Inter + JetBrains Mono | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-001 | BR-019 | Load Inter font weights 300-800 in CyberDemo and Medicum | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-002 | BR-019 | Load JetBrains Mono font weights 400, 600 in CyberDemo and Medicum | MTH | [ ] | [ ] | [ ] |
| REQ-001-003-003 | BR-029 | Verify Inter + JetBrains Mono already loaded in Files Manager | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-001 | US-003, BR-004 | Create ThemeToggle React component with pill shape, 3 buttons | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-002 | US-003 | Active button primary-600 bg, inactive text-secondary | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-003 | US-003 | Dark=Moon, Light=Sun, System=Monitor Lucide icons | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-004 | BR-004 | Click sets data-theme on html element | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-005 | BR-005 | System reads prefers-color-scheme media query | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-006 | BR-008 | Transition 200ms ease-default | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-001 | US-012, BR-004 | Create theme-toggle LitElement component | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-002 | BR-004 | Lit component sets data-theme on document.documentElement | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-003 | US-012 | Place theme-toggle in Files Manager toolbar | MTH | [ ] | [ ] | [ ] |
| REQ-002-003-001 | US-004, BR-006 | Save theme to localStorage key theme-preference | MTH | [ ] | [ ] | [ ] |
| REQ-002-003-002 | US-005, BR-007 | Apply theme from localStorage before first paint | MTH | [ ] | [ ] | [ ] |
| REQ-002-003-003 | BR-005 | System mode detects OS preference on load | MTH | [ ] | [ ] | [ ] |
| REQ-002-003-004 | NFR-005 | Default to dark if localStorage empty/unavailable | MTH | [ ] | [ ] | [ ] |
| REQ-002-003-005 | BR-008 | Body transition 300ms ease-default on theme switch | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-001 | US-006, BR-009 | Create FontSizeButton React component with Lucide icon | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-002 | BR-009, BR-010 | Click cycles: 16px to 18px to 20px to 16px | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-003 | BR-010 | Modifies document.documentElement.style.fontSize | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-004 | BR-009 | Button visually indicates current size state | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-005 | BR-009 | Tooltip shows current font size level name | NTH | [ ] | [ ] | [ ] |
| REQ-003-001-006 | BR-012 | Button placed LEFT of ThemeToggle in header | MTH | [ ] | [ ] | [ ] |
| REQ-003-002-001 | US-006, BR-009 | Create font-size-button LitElement component | MTH | [ ] | [ ] | [ ] |
| REQ-003-002-002 | BR-012 | Place next to theme-toggle in Files Manager toolbar | MTH | [ ] | [ ] | [ ] |
| REQ-003-003-001 | US-007, BR-011 | Save font-size-step to localStorage | MTH | [ ] | [ ] | [ ] |
| REQ-003-003-002 | BR-011 | Restore font size from localStorage before first paint | MTH | [ ] | [ ] | [ ] |
| REQ-003-003-003 | NFR-005 | Default to step 0 (16px) if localStorage unavailable | MTH | [ ] | [ ] | [ ] |
| REQ-004-001-001 | US-009, BR-014 | Update CyberDemo sidebar to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-001-002 | BR-014 | Update CyberDemo header with tokens, ThemeToggle, FontSizeButton | MTH | [ ] | [ ] | [ ] |
| REQ-004-001-003 | BR-014 | Update DemoControlBar, NarrationFooter, DemoFloatingWidget | MTH | [ ] | [ ] | [ ] |
| REQ-004-001-004 | BR-001 | Import design-tokens.css in CyberDemo entry point | MTH | [ ] | [ ] | [ ] |
| REQ-004-002-001 | BR-013 | Migrate /dashboard to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-002-002 | BR-013 | Migrate /generation to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-002-003 | BR-013 | Migrate /surface to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-003-001 | BR-013 | Migrate vulnerability pages (4 routes) to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-003-002 | BR-013 | Migrate /threats to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-003-003 | BR-013 | Migrate /incidents to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-003-004 | BR-013 | Migrate /detections to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-003-005 | BR-013 | Migrate /ctem to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-003-006 | BR-013 | Migrate /vulnerabilities/ssvc to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-004-001 | BR-015 | Migrate workflow canvas to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-004-002 | BR-015 | Migrate agent status badges to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-004-003 | BR-015 | Migrate execution timeline to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-004-004 | BR-015 | Migrate log viewer to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-004-005 | BR-015 | Migrate metric cards to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-005-001 | BR-013 | Migrate /timeline to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-005-002 | BR-013 | Migrate /postmortems to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-005-003 | BR-013 | Migrate /tickets to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-005-004 | BR-013 | Migrate /graph pages to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-005-005 | BR-013 | Migrate /collab to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-005-006 | BR-013 | Migrate /config to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-005-007 | BR-013 | Migrate /audit to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-005-008 | BR-013 | Migrate /simulation to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-004-005-009 | BR-013 | Migrate /assets to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-001-001 | US-010, BR-018 | Update App.tsx body to var(--bg-primary) | MTH | [ ] | [ ] | [ ] |
| REQ-005-001-002 | BR-018 | Update PatientHeader to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-001-003 | BR-018 | Update allergy badges to semantic tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-001-004 | BR-018 | Update connection status dots to AgentFlow colors | MTH | [ ] | [ ] | [ ] |
| REQ-005-001-005 | BR-012 | Place ThemeToggle + FontSizeButton in PatientHeader | MTH | [ ] | [ ] | [ ] |
| REQ-005-001-006 | BR-018 | Update TabBar to design tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-001-007 | BR-001 | Import design-tokens.css + fonts in Medicum | MTH | [ ] | [ ] | [ ] |
| REQ-005-002-001 | BR-020 | Update Consulta transcription panel to tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-002-002 | BR-020 | Update chat bubbles to tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-002-003 | BR-020 | Update SOAP note panel to tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-002-004 | BR-020 | Update Whisper status badges to tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-002-005 | BR-020 | Update speaker toggle and buttons to tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-003-001 | BR-020 | Update Historia accordion sections to tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-003-002 | BR-020 | Update lab results table to token pattern | MTH | [ ] | [ ] | [ ] |
| REQ-005-003-003 | BR-020 | Update episode cards to tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-004-001 | BR-020 | Update Codificacion AI suggestions panel to tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-004-002 | BR-022 | CIE-10 codes font-mono with theme-aware primary color | MTH | [ ] | [ ] | [ ] |
| REQ-005-004-003 | BR-023 | Confidence badges with semantic tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-004-004 | BR-020 | Update search input and results to tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-004-005 | BR-020 | Update assigned codes panel to tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-005-001 | BR-020 | Update Visor toolbar to tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-005-002 | BR-021 | Visor image area stays dark in both themes | MTH | [ ] | [ ] | [ ] |
| REQ-005-005-003 | BR-020 | Update AI analysis panel to tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-005-004 | BR-023 | Update Visor finding cards and badges to tokens | MTH | [ ] | [ ] | [ ] |
| REQ-005-005-005 | BR-020 | Update radiological report block to tokens | MTH | [ ] | [ ] | [ ] |
| REQ-006-001-001 | BR-025 | Replace --files-bg-primary with --bg-primary dark | MTH | [ ] | [ ] | [ ] |
| REQ-006-001-002 | BR-025 | Replace --files-bg-secondary with --bg-secondary dark | MTH | [ ] | [ ] | [ ] |
| REQ-006-001-003 | BR-025 | Replace --files-bg-tertiary with --bg-tertiary dark | MTH | [ ] | [ ] | [ ] |
| REQ-006-001-004 | BR-024 | Replace --files-text-* with --text-* tokens | MTH | [ ] | [ ] | [ ] |
| REQ-006-001-005 | BR-024 | Replace --files-border with --border-* tokens | MTH | [ ] | [ ] | [ ] |
| REQ-006-001-006 | BR-026 | Update light theme values to AgentFlow spec | MTH | [ ] | [ ] | [ ] |
| REQ-006-001-007 | BR-024 | Add missing shadow, radius, spacing tokens | MTH | [ ] | [ ] | [ ] |
| REQ-006-002-001 | US-012 | Integrate theme-toggle in Files Manager toolbar | MTH | [ ] | [ ] | [ ] |
| REQ-006-002-002 | BR-012 | Integrate font-size-button in Files Manager toolbar | MTH | [ ] | [ ] | [ ] |
| REQ-006-003-001 | BR-027 | Fix hardcoded colors in index.html | MTH | [ ] | [ ] | [ ] |
| REQ-006-003-002 | BR-027 | Fix hardcoded colors in files-epic002.ts | MTH | [ ] | [ ] | [ ] |
| REQ-006-004-001 | BR-028 | Replace emoji action buttons with Lucide SVG icons | NTH | [ ] | [ ] | [ ] |
| REQ-006-004-002 | BR-028 | Add Lucide dependency or inline SVGs for Lit | NTH | [ ] | [ ] | [ ] |
| REQ-007-001-001 | BR-030 | Primary buttons: primary-600 bg, hover primary-700 + translateY | MTH | [ ] | [ ] | [ ] |
| REQ-007-001-002 | BR-030 | Destructive buttons: color-error bg, hover error-dark | MTH | [ ] | [ ] | [ ] |
| REQ-007-001-003 | BR-030 | Button sizes: sm 32px, md 36px, lg 44px | MTH | [ ] | [ ] | [ ] |
| REQ-007-001-004 | BR-039 | Focus ring: 2px outline primary-500 | MTH | [ ] | [ ] | [ ] |
| REQ-007-001-005 | BR-030 | Disabled: opacity 0.5, cursor-not-allowed | MTH | [ ] | [ ] | [ ] |
| REQ-007-002-001 | BR-031 | Cards: bg-card, border-secondary, radius-xl, space-6 | MTH | [ ] | [ ] | [ ] |
| REQ-007-002-002 | BR-031 | Interactive cards: hover border-primary + shadow + translateY | MTH | [ ] | [ ] | [ ] |
| REQ-007-003-001 | BR-032 | Inputs: bg-input, border-primary, radius-lg, 36px | MTH | [ ] | [ ] | [ ] |
| REQ-007-003-002 | BR-032 | Input focus: border-focus + blue ring | MTH | [ ] | [ ] | [ ] |
| REQ-007-003-003 | BR-032 | Input error: red border + red ring | MTH | [ ] | [ ] | [ ] |
| REQ-007-003-004 | BR-032 | Placeholder: text-tertiary | MTH | [ ] | [ ] | [ ] |
| REQ-007-004-001 | BR-033 | Table headers: bg-tertiary, text-xs, uppercase | MTH | [ ] | [ ] | [ ] |
| REQ-007-004-002 | BR-033 | Table rows: text-sm, border-secondary, hover bg-hover | MTH | [ ] | [ ] | [ ] |
| REQ-007-005-001 | BR-034 | Badges: pill, text-xs, semantic 15% opacity bg | MTH | [ ] | [ ] | [ ] |
| REQ-007-005-002 | BR-036 | Toasts: bg-elevated, border-primary, shadow-lg, 380px | MTH | [ ] | [ ] | [ ] |
| REQ-007-006-001 | BR-035 | Modals: overlay blur, bg-elevated, radius-xl | MTH | [ ] | [ ] | [ ] |
| REQ-007-006-002 | BR-035 | Modal footer: right-aligned, space-3 gap | MTH | [ ] | [ ] | [ ] |
| REQ-007-007-001 | BR-037 | Empty states: centered, 48px icon, text-lg title | NTH | [ ] | [ ] | [ ] |
| REQ-008-001-001 | BR-038 | Color contrast 4.5:1 for text in dark theme | MTH | [ ] | [ ] | [ ] |
| REQ-008-001-002 | BR-038 | Color contrast 4.5:1 for text in light theme | MTH | [ ] | [ ] | [ ] |
| REQ-008-001-003 | BR-038 | UI component contrast 3:1 | MTH | [ ] | [ ] | [ ] |
| REQ-008-002-001 | BR-039 | Visible focus indicators on all interactive elements | MTH | [ ] | [ ] | [ ] |
| REQ-008-002-002 | BR-040 | Theme toggle ARIA labels and aria-pressed | MTH | [ ] | [ ] | [ ] |
| REQ-008-002-003 | BR-041 | Font size button ARIA label and announcements | MTH | [ ] | [ ] | [ ] |
| REQ-008-002-004 | BR-042 | Modal focus trap | MTH | [ ] | [ ] | [ ] |
| REQ-008-002-005 | BR-043 | Toast role="status" | MTH | [ ] | [ ] | [ ] |
| REQ-009-001-001 | BR-045 | Sidebar icon-only at 1024-1280px | NTH | [ ] | [ ] | [ ] |
| REQ-009-001-002 | BR-045 | Sidebar hamburger drawer below 1024px | NTH | [ ] | [ ] | [ ] |
| REQ-009-001-003 | BR-046 | Tables hide secondary columns at 1024-1280px | NTH | [ ] | [ ] | [ ] |
| REQ-009-001-004 | BR-046 | Tables horizontal scroll at 768-1024px | NTH | [ ] | [ ] | [ ] |
| TECH-001 | BR-001, C-005 | CSS custom properties for cross-framework tokens | MTH | [ ] | [ ] | [ ] |
| TECH-002 | BR-001, C-005 | Design tokens importable in React and Lit | MTH | [ ] | [ ] | [ ] |
| TECH-003 | BR-007, NFR-003 | Synchronous theme detection in head | MTH | [ ] | [ ] | [ ] |
| TECH-004 | BR-010 | Font size modifies documentElement.style.fontSize | MTH | [ ] | [ ] | [ ] |
| TECH-005 | BR-001 | Tailwind uses var(--token) syntax | MTH | [ ] | [ ] | [ ] |
| TECH-006 | C-005 | Shadow DOM token injection for Lit components | MTH | [ ] | [ ] | [ ] |
| TECH-007 | C-004 | Preserve CyberDemo custom CSS animations | MTH | [ ] | [ ] | [ ] |
| TECH-008 | NFR-001 | Build size increase less than 50KB from tokens + fonts | NTH | [ ] | [ ] | [ ] |
| TECH-009 | NFR-001 | font-display: swap for web fonts | MTH | [ ] | [ ] | [ ] |
| TECH-010 | BR-002 | No hardcoded hex colors after migration | MTH | [ ] | [ ] | [ ] |
| INT-001 | BR-001, US-001 | Shared design-tokens.css between CyberDemo and Medicum | MTH | [ ] | [ ] | [ ] |
| INT-002 | BR-024 | Files Manager consumes same token values | MTH | [ ] | [ ] | [ ] |
| INT-003 | BR-004 | All apps respond to data-theme attribute | MTH | [ ] | [ ] | [ ] |
| INT-004 | BR-019 | Consistent font loading across apps | MTH | [ ] | [ ] | [ ] |
| INT-005 | BR-028 | Lucide icons available in all apps | MTH | [ ] | [ ] | [ ] |
| DATA-001 | BR-006 | localStorage theme-preference: dark/light/system | MTH | [ ] | [ ] | [ ] |
| DATA-002 | BR-011 | localStorage font-size-step: 0/1/2 | MTH | [ ] | [ ] | [ ] |
| DATA-003 | BR-006 | Per-origin localStorage scoping | MTH | [ ] | [ ] | [ ] |
| DATA-004 | NFR-006 | No sensitive data in localStorage | MTH | [ ] | [ ] | [ ] |
| NFR-001 | BR-008 | Theme switch latency less than 300ms | MTH | [ ] | [ ] | [ ] |
| NFR-002 | BR-010 | Font size change latency less than 100ms | MTH | [ ] | [ ] | [ ] |
| NFR-003 | BR-007, TECH-003 | No FOUC on page load | MTH | [ ] | [ ] | [ ] |
| NFR-004 | BR-013, BR-020 | 100% feature parity across themes | MTH | [ ] | [ ] | [ ] |
| NFR-005 | BR-006 | Graceful localStorage fallback | MTH | [ ] | [ ] | [ ] |
| NFR-006 | DATA-004 | No sensitive data in localStorage | MTH | [ ] | [ ] | [ ] |
| NFR-007 | BR-004, BR-010 | No XSS vectors in theme/font handling | MTH | [ ] | [ ] | [ ] |
| NFR-008 | BR-001 | Token system extensible for future projects | NTH | [ ] | [ ] | [ ] |
| NFR-009 | TECH-001, TECH-002 | Framework-agnostic CSS token architecture | NTH | [ ] | [ ] | [ ] |
| NFR-010 | BR-038 | WCAG 2.2 AA compliance both themes | MTH | [ ] | [ ] | [ ] |
| NFR-011 | BR-039 | Consistent keyboard navigation | MTH | [ ] | [ ] | [ ] |
| NFR-012 | BR-006, BR-011 | Per-project preference persistence | MTH | [ ] | [ ] | [ ] |

---

# VERIFICATION

## Part 1 to Part 2 Traceability

| Part 1 Source | Part 2 Coverage |
|---------------|-----------------|
| US-001 | REQ-001-001-001, REQ-001-001-002, INT-001 |
| US-002 | REQ-001-002-001, REQ-001-002-002, TECH-005 |
| US-003 | REQ-002-001-001 through REQ-002-001-006 |
| US-004 | REQ-002-003-001 |
| US-005 | REQ-002-003-002, REQ-002-003-005, TECH-003 |
| US-006 | REQ-003-001-001 through REQ-003-001-004, REQ-003-002-001 |
| US-007 | REQ-003-003-001, REQ-003-003-002 |
| US-008 | EPIC-004 (all REQ-004-*) |
| US-009 | REQ-004-001-001 through REQ-004-001-004 |
| US-010 | EPIC-005 (all REQ-005-*) |
| US-011 | REQ-005-004-002, REQ-005-004-003, REQ-005-005-002 |
| US-012 | REQ-002-002-001 through REQ-002-002-003, REQ-006-002-001 |
| US-013 | EPIC-006 (all REQ-006-*) |
| US-014 | EPIC-007 (all REQ-007-*) |
| US-015 | REQ-008-001-001 through REQ-008-001-003, REQ-008-002-001 |
| US-016 | REQ-008-002-002 through REQ-008-002-005 |
| US-017 | REQ-009-001-001 through REQ-009-001-004 |
| BR-001 through BR-046 | Covered by REQ, TECH, INT, DATA requirements |
| NFR-001 through NFR-012 | Covered by TECH-003, TECH-008, TECH-009, NFR-* requirements |

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Epics** | 9 |
| **Features** | 33 |
| **Functional Requirements (REQ)** | 131 |
| **Technical Requirements (TECH)** | 10 |
| **Integration Requirements (INT)** | 5 |
| **Data Requirements (DATA)** | 4 |
| **Non-Functional Requirements (NFR)** | 12 |
| **Total Requirements** | 162 |
| **MTH Requirements** | 151 |
| **NTH Requirements** | 11 |
| **User Stories** | 17 |
| **Business Rules** | 46 |
| **Personas** | 5 |

---

_Generated by SoftwareBuilderX v21.0.0_
