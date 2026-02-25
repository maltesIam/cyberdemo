# Functional Specification: AgentFlow Design System

| Attribute | Value |
|-----------|-------|
| Version | 1.0.0 |
| Date | 2026-02-25 |
| Build ID | sbx-20260225-123259 |
| Status | Draft |
| Project | medicum |
| Template Version | SBX v23.0.0 |

---

# PART 1: FUNCTIONAL DESCRIPTION
*For business stakeholders and non-technical readers*

## 1.1 Executive Summary

This specification defines the complete visual and interaction overhaul of the CyberDemo Frontend application under the **AgentFlow Design System v2.0**. The goal is to implement a unified design token system, dual-theme support (Dark + Light + System preference), font size accessibility controls, and a professional enterprise-grade component library inspired by Linear, Vercel, Stripe, and other top-tier B2B platforms.

The project scope covers:
- Implementation of a complete CSS custom property design token system
- Three-mode theme toggle (Dark, Light, System) with localStorage persistence
- Cyclic font size accessibility button (Normal → Medium → Large)
- Systematic migration of all 18+ pages from hardcoded Tailwind classes to design token references
- Component standardization across buttons, cards, forms, tables, badges, navigation, modals, and domain-specific components
- WCAG 2.2 AA accessibility compliance
- Responsive layout adaptation

## 1.2 System Overview

### 1.2.1 Purpose

Transform the CyberDemo Frontend from a dark-mode-only application with hardcoded colors into a theme-aware, accessible, enterprise-grade UI built on a systematic design token architecture. This enables:
- User preference for light or dark themes
- Accessibility through scalable font sizes
- Consistent component appearance across all pages
- Maintainable styling through centralized design tokens

### 1.2.2 Scope

**In Scope:**
- CyberDemo Frontend application (`cyberdemo/frontend/`)
- All 18+ pages and routes
- Design token CSS custom properties system
- Theme toggle component and context
- Font size accessibility button
- Component migration to design tokens
- Responsive design improvements
- WCAG 2.2 AA compliance

**Out of Scope:**
- Backend API changes
- Medicum Demo application (separate project)
- Files Manager application (separate project)
- New feature development (no new pages or functionality)
- Database schema changes
- Third-party service integrations

### 1.2.3 Context Diagram

```
User Browser  <--->  CyberDemo Frontend (React + Tailwind)
                              :                    :
                              :                    :
                    Design Tokens CSS      Theme/Font Context
                              :
                              :
                    AgentFlow Style Guide v2.0
```

## 1.3 User Roles and Personas

| Role ID | Role Name | Description | Primary Goals |
|---------|-----------|-------------|---------------|
| USR-001 | SOC Analyst | Security Operations Center analyst using the platform daily | Quick access to dashboards, comfortable reading in preferred theme |
| USR-002 | Security Engineer | Technical user configuring attack simulations and reviewing graphs | Clear visualization in both themes, readable code blocks |
| USR-003 | Manager | Reviews dashboards and postmortems for reporting | Accessible font sizes, professional appearance for screen sharing |
| USR-004 | Accessibility User | User with visual impairments or preferences | Font size scaling, high contrast themes, keyboard navigation |

## 1.4 Functional Areas

### 1.4.1 Design Token System

**Description**: A centralized CSS custom property system that defines all visual values (colors, typography, spacing, shadows, transitions) as reusable tokens. All UI elements reference these tokens instead of hardcoded values.

**User Stories**:
- US-001: As a developer, I want all visual values defined as CSS custom properties so that I can change the entire application theme by updating token values
- US-002: As a developer, I want theme-aware semantic tokens (`--bg-primary`, `--text-primary`) so that components automatically adapt when the theme changes

**Business Rules**:
- BR-001: All color values MUST be defined as CSS custom properties, never hardcoded in component styles
- BR-002: Semantic tokens (e.g., `--bg-primary`) MUST reference the base color scale tokens (e.g., `neutral-950`)
- BR-003: The token naming convention MUST follow the pattern `--category-variant` (e.g., `--bg-primary`, `--text-secondary`)

### 1.4.2 Theme System

**Description**: A three-mode theme system (Dark, Light, System) that allows users to choose their preferred color scheme. The theme persists across page reloads via localStorage.

**User Stories**:
- US-003: As a user, I want to switch between Dark and Light themes so that I can use the application comfortably in any lighting condition
- US-004: As a user, I want a System mode that automatically matches my OS preference so that the app follows my system-wide setting
- US-005: As a user, I want my theme preference to persist across page reloads so that I don't have to set it every time

**Business Rules**:
- BR-004: The theme toggle MUST be visible in the top-right corner of every page header
- BR-005: Theme preference MUST be stored in localStorage under key `theme-preference`
- BR-006: On page load, the system MUST check localStorage first; if "system", apply `prefers-color-scheme` media query detection
- BR-007: Theme switching MUST NOT cause a flash of unstyled content (FOUC)
- BR-008: All theme transitions MUST use 300ms duration with ease-default easing

**Workflows**:
1. User clicks theme toggle button
2. System cycles through: Dark → Light → System → Dark
3. `[data-theme]` attribute on `<html>` is updated
4. All CSS custom properties automatically resolve to the new theme values
5. Preference is saved to localStorage

### 1.4.3 Font Size Accessibility

**Description**: A cyclic button that increases the base font size in 2px increments, allowing users to scale all text in the application proportionally using the rem-based sizing system.

**User Stories**:
- US-006: As a user with visual impairments, I want to increase the font size so that I can read text comfortably
- US-007: As a user, I want the font size setting to persist across page reloads so that I don't have to adjust it every time

**Business Rules**:
- BR-009: The font size button MUST be immediately to the LEFT of the theme toggle in the header
- BR-010: The button cycles through 3 states: Normal (16px), Medium (18px), Large (20px)
- BR-011: Font size step MUST be stored in localStorage under key `font-size-step`
- BR-012: Font size changes MUST affect the `html { font-size }` property, scaling all rem-based values proportionally

### 1.4.4 Component Library

**Description**: A standardized set of UI components (buttons, cards, forms, tables, badges, navigation, modals, etc.) built on the design token system. Each component has defined variants, sizes, and states.

**User Stories**:
- US-008: As a developer, I want standardized button variants (Primary, Secondary, Ghost, Destructive, Accent) so that I can use consistent button styles across all pages
- US-009: As a developer, I want card components with defined hover states and variants so that interactive elements behave consistently
- US-010: As a developer, I want form input components with proper focus, error, and disabled states so that forms are accessible and consistent

**Business Rules**:
- BR-013: All buttons MUST use the defined size system: Small (32px), Medium (36px), Large (44px)
- BR-014: All interactive cards MUST show `translateY(-2px)` on hover with border color change
- BR-015: All form inputs MUST show a blue focus ring (3px) when focused
- BR-016: All tables MUST use the design token table pattern with sticky header and hover rows

### 1.4.5 Page Migration

**Description**: Systematic migration of all 18+ pages from hardcoded Tailwind color classes and custom CSS to design token references. Each page must render correctly in both Dark and Light themes.

**User Stories**:
- US-011: As a user, I want all pages to look correct in both Dark and Light modes so that I can use my preferred theme everywhere
- US-012: As a developer, I want no hardcoded color values remaining in the codebase so that theme changes are automatic

**Business Rules**:
- BR-017: All `bg-gray-*`, `text-gray-*`, `border-gray-*` Tailwind classes MUST be replaced with design token references
- BR-018: All pages MUST be visually verified in both Dark and Light themes
- BR-019: No hardcoded color hex values (#xxx) may remain in component files after migration

### 1.4.6 Domain-Specific Components

**Description**: Specialized UI components for the cybersecurity domain: workflow canvas with nodes, agent status indicators, execution timelines, log viewers, and metrics dashboards.

**User Stories**:
- US-013: As a SOC analyst, I want workflow nodes with colored status indicators so that I can see agent states at a glance
- US-014: As a user, I want execution timeline components that clearly show step progress with color-coded status dots

**Business Rules**:
- BR-020: Agent status colors MUST follow the defined palette: idle (slate), running (blue), success (green), error (red), waiting (amber), queued (cyan)
- BR-021: Running and error status dots MUST have a pulsing animation
- BR-022: Workflow canvas MUST have a dot grid background pattern with 24px spacing

### 1.4.7 Responsive Design

**Description**: Desktop-first responsive layout that adapts the sidebar, content area, and panels at defined breakpoints.

**User Stories**:
- US-015: As a user on a tablet, I want the sidebar to collapse to an icon-only mode so that I have more content space
- US-016: As a user on a small screen, I want navigation accessible via a hamburger menu drawer

**Business Rules**:
- BR-023: At >1280px: Full sidebar (280px) visible
- BR-024: At 1024-1280px: Icon-only sidebar (56px)
- BR-025: At <1024px: Sidebar becomes a drawer toggled by hamburger icon

## 1.5 Non-Functional Requirements (Summary)

| Category | Requirement |
|----------|-------------|
| Performance | Theme switching must complete within 300ms with no visible flicker. All CSS transitions must use GPU-accelerated properties (transform, opacity). |
| Availability | The application must function fully offline after initial load (design tokens are bundled, not fetched). No external font service dependency for core functionality. |
| Security | Theme and font size preferences stored only in localStorage (no server-side storage). No PII in client-side storage. |
| Scalability | Design token system must support addition of new themes without modifying component code. Token architecture must scale to 50+ components. |
| Usability | WCAG 2.2 AA compliance minimum. All interactive elements must have visible focus indicators. Keyboard navigation must work for all interactive elements. Color contrast ratios must meet 4.5:1 for normal text, 3:1 for large text. |

## 1.6 Assumptions and Dependencies

### Assumptions
- The existing React 18 + Vite + Tailwind CSS stack will be maintained
- Inter and JetBrains Mono fonts will be loaded from Google Fonts
- The existing page routing structure will not change
- The backend API responses do not need to change
- Existing component logic (data fetching, state management) will be preserved

### Dependencies
- Google Fonts API for Inter and JetBrains Mono font loading
- Tailwind CSS 3.x for utility classes that reference CSS custom properties
- Lucide React for iconography
- React context API for theme and font size state management

## 1.7 Constraints

- No changes to the backend API
- Must maintain backward compatibility with existing functionality
- Font loading must use a fallback font stack to avoid FOUT
- All changes must be incremental — the application must remain functional throughout migration
- Tailwind configuration must support CSS variable references via `var()` syntax

## 1.8 Project Context (Existing Codebase)

The CyberDemo Frontend is an existing React application with:
- **18+ pages** across security operations, vulnerability management, threat intel, and collaboration features
- **Existing `design-tokens.css`** file with partial AgentFlow token implementation
- **Existing `ThemeToggle.tsx`** component for dark/light theme switching
- **Existing `FontSizeButton.tsx`** component for font size control
- **Current styling**: Mix of Tailwind utility classes with hardcoded colors and custom CSS animations
- **Current theme**: Primarily dark mode with `gray-900` backgrounds and `cyan-500` accents
- **Pages directory**: `frontend/src/pages/` with individual page components
- **Components directory**: `frontend/src/components/` with shared components
- **Styles directory**: `frontend/src/styles/` with `design-tokens.css` and `highlightStyles.ts`

---

# PART 2: TECHNICAL REQUIREMENTS
*Traceable requirements for development*

## 2.1 Requirements Traceability Matrix

Summary of all requirements categorized by type and priority.

| Category | Count | MTH | NTH |
|----------|-------|-----|-----|
| Functional (REQ) | 48 | 40 | 8 |
| Technical (TECH) | 8 | 6 | 2 |
| Integration (INT) | 2 | 2 | 0 |
| Data (DATA) | 2 | 2 | 0 |
| Non-Functional (NFR) | 5 | 4 | 1 |
| **Total** | **65** | **54** | **11** |

## 2.2 Requirements Numbering Convention

```
EPIC-XXX           : Epic level
FEAT-XXX-YYY       : Feature under Epic XXX
REQ-XXX-YYY-ZZZ    : Requirement under Feature YYY
TECH-XXX           : Technical requirement
INT-XXX            : Integration requirement
DATA-XXX           : Data requirement
NFR-XXX            : Non-functional requirement
```

## 2.3 Priority Classification

| Priority | Code | Description |
|----------|------|-------------|
| Must-To-Have | MTH | Required for minimum viable delivery |
| Nice-To-Have | NTH | Enhances quality but not blocking |

## 2.4 Epics, Features, and Requirements

---

### EPIC-001: Design Token System

**Description**: Implement the complete CSS custom property design token system as the single source of truth for all visual values.

#### FEAT-001-001: Base Design Tokens

##### REQ-001-001-001: Color Scale Tokens [MTH]
**Description**: Define all color scale tokens (Primary blue, Secondary cyan, Accent amber, Neutral slate, Semantic colors, Agent status colors) as CSS custom properties in `:root`.
**Source**: US-001
**Acceptance Criteria**:
- AC-001: All Primary color tokens (50-950) are defined as CSS custom properties
- AC-002: All Secondary color tokens (50-950) are defined
- AC-003: All Accent color tokens (50-900) are defined
- AC-004: All Neutral color tokens (0-950) are defined
- AC-005: All Semantic color tokens (success, warning, error, info with light/dark variants) are defined
- AC-006: All Agent status color tokens (idle, running, success, error, waiting, queued) are defined
**Files**: `frontend/src/styles/design-tokens.css`

##### REQ-001-001-002: Typography Tokens [MTH]
**Description**: Define typography tokens: font families (Inter, JetBrains Mono), font sizes (xs through 5xl), font weights (light through extrabold), and line heights.
**Source**: US-001
**Acceptance Criteria**:
- AC-001: Font family tokens defined for sans and mono
- AC-002: Font size tokens from xs (0.75rem) to 5xl (3rem) defined
- AC-003: Font weight tokens from light (300) to extrabold (800) defined
- AC-004: Line height tokens (tight, snug, normal, relaxed) defined
- AC-005: Inter and JetBrains Mono fonts loaded via @import
**Files**: `frontend/src/styles/design-tokens.css`

##### REQ-001-001-003: Spacing and Layout Tokens [MTH]
**Description**: Define spacing scale (4px base grid), border radius, container widths, and sidebar dimensions as CSS custom properties.
**Source**: US-001
**Acceptance Criteria**:
- AC-001: Spacing tokens from space-0 to space-24 defined on 4px grid
- AC-002: Border radius tokens from sm (4px) to full (9999px) defined
- AC-003: Container max-width (1280px) and sidebar width (280px) defined
**Files**: `frontend/src/styles/design-tokens.css`

##### REQ-001-001-004: Shadow and Elevation Tokens [MTH]
**Description**: Define shadow tokens from xs to xl plus glow variants for active elements.
**Source**: US-001
**Acceptance Criteria**:
- AC-001: Shadow tokens (xs, sm, md, lg, xl) defined
- AC-002: Glow variants (primary, secondary) defined for active workflow elements
**Files**: `frontend/src/styles/design-tokens.css`

##### REQ-001-001-005: Transition and Motion Tokens [MTH]
**Description**: Define transition duration tokens (fast, normal, slow, slower) and easing functions (default, in, out, spring).
**Source**: US-001
**Acceptance Criteria**:
- AC-001: Duration tokens (100ms, 200ms, 300ms, 500ms) defined
- AC-002: Easing function tokens (ease-default, ease-in, ease-out, ease-spring) defined
**Files**: `frontend/src/styles/design-tokens.css`

#### FEAT-001-002: Theme Tokens

##### REQ-001-002-001: Dark Theme Tokens [MTH]
**Description**: Define all semantic theme tokens (backgrounds, text colors, borders, shadows) for the dark theme under `[data-theme="dark"]`.
**Source**: US-003
**Acceptance Criteria**:
- AC-001: Background tokens (primary, secondary, tertiary, elevated, hover, active, input, card) defined for dark
- AC-002: Text tokens (primary, secondary, tertiary, inverse, link) defined for dark
- AC-003: Border tokens (primary, secondary, focus) defined for dark
- AC-004: Shadow card token defined for dark
- AC-005: `color-scheme: dark` is set
**Files**: `frontend/src/styles/design-tokens.css`

##### REQ-001-002-002: Light Theme Tokens [MTH]
**Description**: Define all semantic theme tokens for the light theme under `[data-theme="light"]`.
**Source**: US-003
**Acceptance Criteria**:
- AC-001: All background tokens defined with light values (white, neutral-50, neutral-100)
- AC-002: All text tokens defined with dark values (neutral-900, neutral-600, neutral-500)
- AC-003: All border tokens defined with light values (neutral-200, neutral-100)
- AC-004: Shadow card token defined for light (lower opacity than dark)
- AC-005: `color-scheme: light` is set
**Files**: `frontend/src/styles/design-tokens.css`

##### REQ-001-002-003: Z-Index Scale [MTH]
**Description**: Define z-index tokens for layered UI elements (base, dropdown, sticky, overlay, modal, popover, tooltip, toast).
**Source**: US-001
**Acceptance Criteria**:
- AC-001: Z-index tokens from base (0) to toast (700) defined
**Files**: `frontend/src/styles/design-tokens.css`

---

### EPIC-002: Theme System

**Description**: Implement the three-mode theme toggle with persistence and transition behavior.

#### FEAT-002-001: Theme Context and Hook

##### REQ-002-001-001: useTheme Hook [MTH]
**Description**: Create a React hook/context that manages theme state (dark/light/system), reads/writes localStorage, and applies `[data-theme]` attribute on `<html>`.
**Source**: US-003, US-004, US-005
**Acceptance Criteria**:
- AC-001: Hook provides `theme` state (dark, light, system)
- AC-002: Hook provides `setTheme()` function
- AC-003: On mount, reads from localStorage key `theme-preference`
- AC-004: On theme change, writes to localStorage and updates `<html>` data-theme attribute
- AC-005: System mode detects OS preference via `prefers-color-scheme` media query
- AC-006: System mode responds to OS preference changes in real-time
**Files**: `frontend/src/utils/theme.ts` or `frontend/src/hooks/useTheme.ts`

##### REQ-002-001-002: FOUC Prevention [MTH]
**Description**: Apply theme from localStorage before first paint to prevent flash of unstyled content.
**Source**: BR-007
**Acceptance Criteria**:
- AC-001: Theme is applied in `<head>` script or as early as possible in the render cycle
- AC-002: No visible flash when loading in light mode on a dark-default app (or vice versa)
**Files**: `frontend/index.html` or `frontend/src/main.tsx`

#### FEAT-002-002: Theme Toggle Component

##### REQ-002-002-001: ThemeToggle UI Component [MTH]
**Description**: Build a pill-shaped toggle with three buttons (Dark/Light/System) using moon, sun, and monitor icons.
**Source**: US-003, BR-004
**Acceptance Criteria**:
- AC-001: Three-button pill-shaped container with radius-full
- AC-002: Active button has primary-600 background, white text
- AC-003: Inactive buttons have transparent background, text-secondary
- AC-004: Transition between states uses duration-normal (200ms)
- AC-005: ARIA labels present: `aria-label="Theme selector"`, each button `aria-pressed`
**Files**: `frontend/src/components/ThemeToggle.tsx`

##### REQ-002-002-002: Theme Toggle Placement [MTH]
**Description**: Place the ThemeToggle in the top-right corner of every page header/toolbar.
**Source**: BR-004
**Acceptance Criteria**:
- AC-001: Toggle is visible on every page via the Layout component header
- AC-002: Toggle is in the top-right area of the header
**Files**: `frontend/src/components/Layout.tsx`

---

### EPIC-003: Font Size Accessibility

**Description**: Implement the cyclic font size button for proportional text scaling.

#### FEAT-003-001: Font Size Hook

##### REQ-003-001-001: useFontSize Hook [MTH]
**Description**: Create a React hook that manages font size state (step 0/1/2), reads/writes localStorage, and modifies `html { font-size }`.
**Source**: US-006, US-007
**Acceptance Criteria**:
- AC-001: Hook provides `fontSizeStep` state (0, 1, 2)
- AC-002: Hook provides `cycleFontSize()` function
- AC-003: Step 0 = 16px, Step 1 = 18px, Step 2 = 20px
- AC-004: On mount, reads from localStorage key `font-size-step`
- AC-005: On change, writes to localStorage and updates `html { font-size }`
**Files**: `frontend/src/hooks/useFontSize.ts`

#### FEAT-003-002: Font Size Button Component

##### REQ-003-002-001: FontSizeButton UI Component [MTH]
**Description**: Build a button that cycles through font size steps with visual feedback indicating current level.
**Source**: US-006, BR-009
**Acceptance Criteria**:
- AC-001: Button shows typography icon (e.g., "Aa")
- AC-002: Visual indicator changes per step (e.g., text label changes)
- AC-003: Tooltip shows current level: "Font size: Normal / Medium / Large"
- AC-004: ARIA label: `aria-label="Adjust font size"`, announces current level
- AC-005: Placed immediately to the LEFT of the theme toggle in the header
**Files**: `frontend/src/components/FontSizeButton.tsx`

---

### EPIC-004: Component Library

**Description**: Standardize all UI components to use design tokens with proper variants, sizes, and states.

#### FEAT-004-001: Button Components

##### REQ-004-001-001: Button Variants [MTH]
**Description**: Implement 5 button variants (Primary, Secondary, Ghost, Destructive, Accent) using design tokens.
**Source**: US-008
**Acceptance Criteria**:
- AC-001: Primary button uses primary-600 background, white text, primary-700 hover
- AC-002: Secondary button uses transparent background, border highlight on hover
- AC-003: Ghost button uses transparent background, text-secondary, bg-hover on hover
- AC-004: Destructive button uses error color background
- AC-005: Accent button uses secondary-600 background with secondary glow
- AC-006: All buttons show translateY(-1px) on hover
**Files**: `frontend/src/components/ui/Button.tsx` or equivalent

##### REQ-004-001-002: Button Sizes [MTH]
**Description**: Implement 3 button sizes: Small (32px), Medium (36px), Large (44px).
**Source**: BR-013
**Acceptance Criteria**:
- AC-001: btn-sm: text-xs, 6px 12px padding, 32px height
- AC-002: btn-md: text-sm, 8px 16px padding, 36px height
- AC-003: btn-lg: text-base, 10px 20px padding, 44px height
**Files**: `frontend/src/components/ui/Button.tsx`

#### FEAT-004-002: Form Components

##### REQ-004-002-001: Text Input Styling [MTH]
**Description**: Style text inputs with design tokens: bg-input background, border-primary border, radius-lg, focus ring.
**Source**: US-010
**Acceptance Criteria**:
- AC-001: Background uses bg-input token
- AC-002: Border uses border-primary, 1px
- AC-003: Focus state shows border-focus + blue ring (3px)
- AC-004: Error state shows red border + red ring
- AC-005: Placeholder uses text-tertiary color
**Files**: `frontend/src/styles/design-tokens.css` (global input styles)

##### REQ-004-002-002: Toggle Switch [NTH]
**Description**: Implement a toggle switch component: 44x24px pill, white knob, neutral-600 off, primary-600 on, spring easing.
**Source**: US-010
**Acceptance Criteria**:
- AC-001: 44x24px pill shape with smooth transition
- AC-002: Off state: neutral-600, On state: primary-600
- AC-003: Spring easing for toggle animation
**Files**: `frontend/src/components/ui/Toggle.tsx`

#### FEAT-004-003: Card Components

##### REQ-004-003-001: Base Card Styling [MTH]
**Description**: Style cards with bg-card background, border-secondary border, radius-xl, space-6 padding.
**Source**: US-009
**Acceptance Criteria**:
- AC-001: Background uses bg-card token
- AC-002: Border uses border-secondary, 1px
- AC-003: Border radius uses radius-xl
- AC-004: Interactive cards show border-primary + shadow + translateY(-2px) on hover
**Files**: `frontend/src/styles/design-tokens.css`, component files

##### REQ-004-003-002: Metric Card Component [MTH]
**Description**: Implement metric card with label (uppercase, tertiary), value (3xl, bold), and change indicator.
**Source**: US-013
**Acceptance Criteria**:
- AC-001: Label is text-xs, uppercase, tertiary color, weight-medium, letter-spacing 0.05em
- AC-002: Value is text-3xl, weight-bold, letter-spacing -0.02em
- AC-003: Change indicator shows green (up) or red (down) with arrow
**Files**: Dashboard page components

#### FEAT-004-004: Navigation Components

##### REQ-004-004-001: Sidebar Navigation Styling [MTH]
**Description**: Style sidebar with design tokens: fixed left, 280px width, bg-secondary, nav groups with uppercase titles.
**Source**: US-009, BR-015
**Acceptance Criteria**:
- AC-001: Sidebar uses bg-secondary background
- AC-002: Logo uses gradient text (primary-400 to secondary-400)
- AC-003: Nav group titles are text-xs, uppercase, weight-semibold, text-tertiary
- AC-004: Nav links are text-sm, text-secondary, radius-md, hover shows bg-hover
- AC-005: Active link shows primary tint background
**Files**: `frontend/src/components/Sidebar.tsx`

##### REQ-004-004-002: Tabs Component Styling [MTH]
**Description**: Style horizontal tabs with design tokens: text-sm, weight-medium, 2px bottom border, active state with primary-400.
**Source**: US-009, BR-015
**Acceptance Criteria**:
- AC-001: Tab text is text-sm, weight-medium
- AC-002: Active tab shows primary-400 text + colored bottom border
- AC-003: Inactive tabs show text-secondary
**Files**: Various page components using tabs

#### FEAT-004-005: Table Components

##### REQ-004-005-001: Table Styling [MTH]
**Description**: Style data tables with design tokens: container border, sticky header, hover rows, pagination footer.
**Source**: BR-016
**Acceptance Criteria**:
- AC-001: Container has border-secondary, radius-xl, overflow-x auto
- AC-002: Header has bg-tertiary, text-xs uppercase, weight-medium, letter-spacing 0.05em
- AC-003: Rows have text-sm, text-primary, border-secondary bottom
- AC-004: Hover state uses bg-hover
- AC-005: Pagination footer uses text-xs, text-tertiary
**Files**: Table components across all pages

#### FEAT-004-006: Badge and Alert Components

##### REQ-004-006-001: Badge Variants [MTH]
**Description**: Implement badge variants (Default, Primary, Secondary, Success, Warning, Error) with semi-transparent backgrounds.
**Source**: US-013, BR-020
**Acceptance Criteria**:
- AC-001: Pill shape with radius-full
- AC-002: text-xs, weight-medium, 2px 8px padding
- AC-003: Each variant has correct background opacity and text color
**Files**: Badge components

##### REQ-004-006-002: Inline Alert Styling [NTH]
**Description**: Style inline alerts with icon, colored left border, and semi-transparent backgrounds for info/success/warning/error.
**Source**: BR-017
**Acceptance Criteria**:
- AC-001: Flex row with icon + content (title + description)
- AC-002: Colored left border indicator
- AC-003: Semi-transparent colored backgrounds per severity
**Files**: Alert components

#### FEAT-004-007: Modal and Dialog Components

##### REQ-004-007-001: Modal Overlay and Container [MTH]
**Description**: Style modals with design tokens: backdrop blur overlay, elevated background, radius-xl, shadow-xl.
**Source**: BR-016
**Acceptance Criteria**:
- AC-001: Overlay uses rgba(0,0,0,0.6) + backdrop blur 4px
- AC-002: Modal uses bg-elevated, border-primary, radius-xl, shadow-xl
- AC-003: Max-width 480px
- AC-004: Header has text-lg, weight-semibold title
- AC-005: Footer has flex end, space-3 gap between buttons
- AC-006: Focus trap within modal when open
**Files**: Modal components

---

### EPIC-005: Page Migration

**Description**: Migrate all 18+ pages from hardcoded Tailwind classes to design token references.

#### FEAT-005-001: Core Layout Migration

##### REQ-005-001-001: Layout.tsx Migration [MTH]
**Description**: Migrate the main Layout component to use design tokens for backgrounds, borders, and header styling.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: Layout background uses bg-primary token
- AC-002: Header uses sticky positioning with backdrop blur
- AC-003: Header contains theme toggle and font size button
**Files**: `frontend/src/components/Layout.tsx`

##### REQ-005-001-002: Sidebar.tsx Migration [MTH]
**Description**: Migrate sidebar to use design tokens for all colors, borders, and hover states.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: Sidebar background uses bg-secondary
- AC-002: All nav link colors use text-secondary/text-primary tokens
- AC-003: Hover and active states use bg-hover/bg-active tokens
**Files**: `frontend/src/components/Sidebar.tsx`

#### FEAT-005-002: Dashboard Pages Migration

##### REQ-005-002-001: DashboardPage Migration [MTH]
**Description**: Migrate the main dashboard page to design tokens.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: All card backgrounds use bg-card token
- AC-002: All text colors use text-primary/text-secondary tokens
- AC-003: All metric values use correct typography tokens
- AC-004: Page renders correctly in both Dark and Light themes
**Files**: `frontend/src/pages/DashboardPage.tsx`

##### REQ-005-002-002: SurfacePage Migration [MTH]
**Description**: Migrate the Command Center (Surface) page to design tokens.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: All backgrounds, text, and border colors use design tokens
- AC-002: Page renders correctly in both themes
**Files**: `frontend/src/pages/SurfacePage.tsx`

##### REQ-005-002-003: GenerationPage Migration [MTH]
**Description**: Migrate the Generation page (default/home) to design tokens.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: All backgrounds, text, and border colors use design tokens
- AC-002: Page renders correctly in both themes
**Files**: `frontend/src/pages/GenerationPage.tsx`

#### FEAT-005-003: Security Operations Pages Migration

##### REQ-005-003-001: IncidentsPage Migration [MTH]
**Description**: Migrate incidents tracking page to design tokens.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: All table, card, and badge colors use design tokens
- AC-002: Page renders correctly in both themes
**Files**: `frontend/src/pages/IncidentsPage.tsx`

##### REQ-005-003-002: DetectionsPage Migration [MTH]
**Description**: Migrate detection alerts page to design tokens.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: All alert-related colors use semantic tokens
- AC-002: Page renders correctly in both themes
**Files**: `frontend/src/pages/DetectionsPage.tsx`

##### REQ-005-003-003: TimelinePage Migration [MTH]
**Description**: Migrate incident timeline page to design tokens.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: Timeline components use correct status colors
- AC-002: Page renders correctly in both themes
**Files**: `frontend/src/pages/TimelinePage.tsx`

##### REQ-005-003-004: PostmortemsPage Migration [MTH]
**Description**: Migrate postmortems page to design tokens.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: All backgrounds, text, and borders use design tokens
- AC-002: Page renders correctly in both themes
**Files**: `frontend/src/pages/PostmortemsPage.tsx`

#### FEAT-005-004: Vulnerability Pages Migration

##### REQ-005-004-001: VulnerabilityDashboard Migration [MTH]
**Description**: Migrate vulnerability dashboard and sub-pages to design tokens.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: Severity color badges use semantic tokens (error, warning, accent)
- AC-002: CVE detail pages render correctly in both themes
- AC-003: SSVC dashboard renders correctly in both themes
**Files**: `frontend/src/pages/VulnerabilityDashboard.tsx`, `frontend/src/pages/vuln-pages/`

##### REQ-005-004-002: CTEMPage Migration [MTH]
**Description**: Migrate Continuous Threat Exposure Management page to design tokens.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: All backgrounds, text, and borders use design tokens
- AC-002: Page renders correctly in both themes
**Files**: `frontend/src/pages/CTEMPage.tsx`

#### FEAT-005-005: Analysis and Collaboration Pages Migration

##### REQ-005-005-001: GraphPage Migration [MTH]
**Description**: Migrate the Attack Graph Visualization page to design tokens.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: Canvas background uses bg-secondary with dot grid pattern
- AC-002: Node colors use agent status tokens
- AC-003: Page renders correctly in both themes
**Files**: `frontend/src/pages/GraphPage.tsx`

##### REQ-005-005-002: SimulationPage Migration [MTH]
**Description**: Migrate attack simulation page to design tokens.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: All simulation controls and outputs use design tokens
- AC-002: Page renders correctly in both themes
**Files**: `frontend/src/pages/SimulationPage.tsx`

##### REQ-005-005-003: CollabPage Migration [NTH]
**Description**: Migrate collaboration page to design tokens.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: All backgrounds, text, and borders use design tokens
- AC-002: Page renders correctly in both themes
**Files**: `frontend/src/pages/CollabPage.tsx`

#### FEAT-005-006: Administration Pages Migration

##### REQ-005-006-001: ConfigPage Migration [NTH]
**Description**: Migrate system configuration page to design tokens.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: All form inputs and settings panels use design tokens
- AC-002: Page renders correctly in both themes
**Files**: `frontend/src/pages/ConfigPage.tsx`

##### REQ-005-006-002: AuditPage Migration [NTH]
**Description**: Migrate audit log page to design tokens.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: Log viewer uses correct mono font and dark background tokens
- AC-002: Page renders correctly in both themes
**Files**: `frontend/src/pages/AuditPage.tsx`

##### REQ-005-006-003: AssetsPage Migration [MTH]
**Description**: Migrate asset management page to design tokens.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: Asset tables and cards use design tokens
- AC-002: Page renders correctly in both themes
**Files**: `frontend/src/pages/AssetsPage.tsx`

##### REQ-005-006-004: TicketsPage Migration [NTH]
**Description**: Migrate ticket management page to design tokens.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: Ticket cards and status badges use design tokens
- AC-002: Page renders correctly in both themes
**Files**: `frontend/src/pages/TicketsPage.tsx`

#### FEAT-005-007: Special Pages Migration

##### REQ-005-007-001: ThreatEnrichmentPage Migration [MTH]
**Description**: Migrate threat enrichment page to design tokens.
**Source**: US-011
**Acceptance Criteria**:
- AC-001: Enrichment indicators and data displays use design tokens
- AC-002: Page renders correctly in both themes
**Files**: `frontend/src/pages/ThreatEnrichmentPage.tsx`

---

### EPIC-006: Domain-Specific Components

**Description**: Implement specialized cybersecurity domain UI components using design tokens.

#### FEAT-006-001: Agent Status Components

##### REQ-006-001-001: Agent Status Badges [MTH]
**Description**: Implement agent status badges with animated pulsing dots for running/error states.
**Source**: US-013, BR-020, BR-021
**Acceptance Criteria**:
- AC-001: Six status variants: idle (slate), running (blue), success (green), error (red), waiting (amber), queued (cyan)
- AC-002: Running and error dots have pulse animation (2s infinite)
- AC-003: Badge uses correct agent status color tokens
**Files**: Agent-related components

#### FEAT-006-002: Workflow Canvas

##### REQ-006-002-001: Canvas Background and Nodes [NTH]
**Description**: Implement workflow canvas with dot grid background and draggable nodes using design tokens.
**Source**: BR-022
**Acceptance Criteria**:
- AC-001: Canvas background uses bg-secondary with dot grid (border-secondary, 24px spacing)
- AC-002: Nodes use bg-elevated, border-primary, radius-xl
- AC-003: Node hover shows primary-500 border + glow
- AC-004: Connection lines use primary-500 stroke, 2px width
**Files**: `frontend/src/components/Graph/` or workflow components

#### FEAT-006-003: Execution Timeline

##### REQ-006-003-001: Timeline Component [NTH]
**Description**: Implement vertical execution timeline with colored step dots and connecting lines.
**Source**: US-014
**Acceptance Criteria**:
- AC-001: Step dots are 24px circles colored by status
- AC-002: Connecting line is 2px vertical border-secondary
- AC-003: Step info shows name (text-sm, weight-medium) + meta (text-xs, text-tertiary)
**Files**: Timeline-related components

---

## 2.5 Technical Requirements

### TECH-001: Tailwind Configuration for CSS Variables [MTH]
**Description**: Configure `tailwind.config.js` to reference CSS custom properties, enabling utility classes like `bg-[var(--bg-primary)]`.
**Acceptance Criteria**:
- AC-001: Tailwind config extends theme with CSS variable references
- AC-002: Utility classes resolve to design token values
**Files**: `frontend/tailwind.config.js`

### TECH-002: CSS File Organization [MTH]
**Description**: Organize `design-tokens.css` with clear sections: base tokens, dark theme, light theme, component defaults.
**Acceptance Criteria**:
- AC-001: File structure follows the Section 4 token organization
- AC-002: Comments clearly delimit each section
**Files**: `frontend/src/styles/design-tokens.css`

### TECH-003: React Context Provider [MTH]
**Description**: Create a ThemeProvider context that wraps the application and provides theme + font size state.
**Acceptance Criteria**:
- AC-001: ThemeProvider wraps entire App component
- AC-002: Provides useTheme and useFontSize hooks to all children
**Files**: `frontend/src/context/ThemeContext.tsx` or equivalent

### TECH-004: Hardcoded Color Cleanup [MTH]
**Description**: Remove all hardcoded color hex values and Tailwind color classes (bg-gray-*, text-gray-*) from component files.
**Acceptance Criteria**:
- AC-001: No hardcoded hex colors (#xxx) in component .tsx files
- AC-002: No bg-gray-*, text-gray-*, border-gray-* Tailwind classes in component .tsx files (replaced with design token references)
**Files**: All files in `frontend/src/`

### TECH-005: Font Loading Strategy [MTH]
**Description**: Implement font loading with fallback stack to prevent FOUT and ensure fonts load efficiently.
**Acceptance Criteria**:
- AC-001: Inter and JetBrains Mono loaded via Google Fonts with `display=swap`
- AC-002: Fallback font stack defined in CSS variables
**Files**: `frontend/src/styles/design-tokens.css`

### TECH-006: CSS Animation Definitions [MTH]
**Description**: Define standardized CSS animations (fadeIn, scaleUp, slideUp, bounce, pulse, shimmer, flowDash) using design token durations.
**Acceptance Criteria**:
- AC-001: All animation keyframes defined in design-tokens.css or a separate animations file
- AC-002: Animations use token duration and easing values
**Files**: `frontend/src/styles/design-tokens.css`

### TECH-007: Breakpoint System [NTH]
**Description**: Implement responsive breakpoint system matching the defined breakpoints (sm: 640px, md: 768px, lg: 1024px, xl: 1280px, 2xl: 1536px).
**Acceptance Criteria**:
- AC-001: Tailwind breakpoints match defined values
- AC-002: Layout components adapt correctly at each breakpoint
**Files**: `frontend/tailwind.config.js`

### TECH-008: Code Block Syntax Highlighting [NTH]
**Description**: Style code blocks with mono font, dark background, and syntax highlighting colors from design tokens.
**Acceptance Criteria**:
- AC-001: Code blocks use font-mono, text-sm, leading-relaxed
- AC-002: Syntax highlighting uses primary-400 (keywords), success (strings), secondary-400 (functions), accent-400 (numbers)
**Files**: `frontend/src/styles/highlightStyles.ts`

## 2.6 Integration Requirements

### INT-001: Google Fonts Integration [MTH]
**Description**: Load Inter and JetBrains Mono fonts from Google Fonts CDN.
**Acceptance Criteria**:
- AC-001: Fonts load successfully from Google Fonts
- AC-002: Application renders with fallback fonts while custom fonts load
**Files**: `frontend/src/styles/design-tokens.css`

### INT-002: Lucide Icons Integration [MTH]
**Description**: Use Lucide React for all icons with consistent sizing and stroke width.
**Acceptance Criteria**:
- AC-001: All icons use Lucide React library
- AC-002: Default size 24px, stroke width 1.5
- AC-003: Icons inherit currentColor for theme compatibility
**Files**: Various component files

## 2.7 Data Requirements

### DATA-001: LocalStorage Theme Preference [MTH]
**Description**: Store theme preference in localStorage under key `theme-preference` with values "dark", "light", or "system".
**Acceptance Criteria**:
- AC-001: Key `theme-preference` stores selected theme
- AC-002: Valid values: "dark", "light", "system"
- AC-003: Default if no stored value: "dark"

### DATA-002: LocalStorage Font Size Preference [MTH]
**Description**: Store font size step in localStorage under key `font-size-step` with values 0, 1, or 2.
**Acceptance Criteria**:
- AC-001: Key `font-size-step` stores current step
- AC-002: Valid values: 0, 1, 2
- AC-003: Default if no stored value: 0

## 2.8 Full Traceability Matrix

| Req ID | Source | Description | Priority | Code | Tests | Verified |
|--------|--------|-------------|----------|------|-------|----------|
| REQ-001-001-001 | US-001 | Color scale tokens | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-002 | US-001 | Typography tokens | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-003 | US-001 | Spacing and layout tokens | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-004 | US-001 | Shadow and elevation tokens | MTH | [ ] | [ ] | [ ] |
| REQ-001-001-005 | US-001 | Transition and motion tokens | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-001 | US-003 | Dark theme tokens | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-002 | US-003 | Light theme tokens | MTH | [ ] | [ ] | [ ] |
| REQ-001-002-003 | US-001 | Z-index scale | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-001 | US-003,US-004,US-005 | useTheme hook | MTH | [ ] | [ ] | [ ] |
| REQ-002-001-002 | BR-007 | FOUC prevention | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-001 | US-003, BR-004 | ThemeToggle UI component | MTH | [ ] | [ ] | [ ] |
| REQ-002-002-002 | BR-004 | Theme toggle placement | MTH | [ ] | [ ] | [ ] |
| REQ-003-001-001 | US-006, US-007 | useFontSize hook | MTH | [ ] | [ ] | [ ] |
| REQ-003-002-001 | US-006, BR-009 | FontSizeButton UI component | MTH | [ ] | [ ] | [ ] |
| REQ-004-001-001 | US-008 | Button variants | MTH | [ ] | [ ] | [ ] |
| REQ-004-001-002 | BR-013 | Button sizes | MTH | [ ] | [ ] | [ ] |
| REQ-004-002-001 | US-010 | Text input styling | MTH | [ ] | [ ] | [ ] |
| REQ-004-002-002 | US-010 | Toggle switch | NTH | [ ] | [ ] | [ ] |
| REQ-004-003-001 | US-009 | Base card styling | MTH | [ ] | [ ] | [ ] |
| REQ-004-003-002 | US-013 | Metric card component | MTH | [ ] | [ ] | [ ] |
| REQ-004-004-001 | US-009, BR-015 | Sidebar navigation styling | MTH | [ ] | [ ] | [ ] |
| REQ-004-004-002 | US-009, BR-015 | Tabs component styling | MTH | [ ] | [ ] | [ ] |
| REQ-004-005-001 | BR-016 | Table styling | MTH | [ ] | [ ] | [ ] |
| REQ-004-006-001 | US-013, BR-020 | Badge variants | MTH | [ ] | [ ] | [ ] |
| REQ-004-006-002 | BR-017 | Inline alert styling | NTH | [ ] | [ ] | [ ] |
| REQ-004-007-001 | BR-016 | Modal overlay and container | MTH | [ ] | [ ] | [ ] |
| REQ-005-001-001 | US-011 | Layout.tsx migration | MTH | [ ] | [ ] | [ ] |
| REQ-005-001-002 | US-011 | Sidebar.tsx migration | MTH | [ ] | [ ] | [ ] |
| REQ-005-002-001 | US-011 | DashboardPage migration | MTH | [ ] | [ ] | [ ] |
| REQ-005-002-002 | US-011 | SurfacePage migration | MTH | [ ] | [ ] | [ ] |
| REQ-005-002-003 | US-011 | GenerationPage migration | MTH | [ ] | [ ] | [ ] |
| REQ-005-003-001 | US-011 | IncidentsPage migration | MTH | [ ] | [ ] | [ ] |
| REQ-005-003-002 | US-011 | DetectionsPage migration | MTH | [ ] | [ ] | [ ] |
| REQ-005-003-003 | US-011 | TimelinePage migration | MTH | [ ] | [ ] | [ ] |
| REQ-005-003-004 | US-011 | PostmortemsPage migration | MTH | [ ] | [ ] | [ ] |
| REQ-005-004-001 | US-011 | VulnerabilityDashboard migration | MTH | [ ] | [ ] | [ ] |
| REQ-005-004-002 | US-011 | CTEMPage migration | MTH | [ ] | [ ] | [ ] |
| REQ-005-005-001 | US-011 | GraphPage migration | MTH | [ ] | [ ] | [ ] |
| REQ-005-005-002 | US-011 | SimulationPage migration | MTH | [ ] | [ ] | [ ] |
| REQ-005-005-003 | US-011 | CollabPage migration | NTH | [ ] | [ ] | [ ] |
| REQ-005-006-001 | US-011 | ConfigPage migration | NTH | [ ] | [ ] | [ ] |
| REQ-005-006-002 | US-011 | AuditPage migration | NTH | [ ] | [ ] | [ ] |
| REQ-005-006-003 | US-011 | AssetsPage migration | MTH | [ ] | [ ] | [ ] |
| REQ-005-006-004 | US-011 | TicketsPage migration | NTH | [ ] | [ ] | [ ] |
| REQ-005-007-001 | US-011 | ThreatEnrichmentPage migration | MTH | [ ] | [ ] | [ ] |
| REQ-006-001-001 | US-013, BR-020, BR-021 | Agent status badges | MTH | [ ] | [ ] | [ ] |
| REQ-006-002-001 | BR-022 | Canvas background and nodes | NTH | [ ] | [ ] | [ ] |
| REQ-006-003-001 | US-014 | Timeline component | NTH | [ ] | [ ] | [ ] |
| TECH-001 | BR-001, BR-002 | Tailwind config for CSS variables | MTH | [ ] | [ ] | [ ] |
| TECH-002 | BR-001 | CSS file organization | MTH | [ ] | [ ] | [ ] |
| TECH-003 | US-003, US-006 | React context provider | MTH | [ ] | [ ] | [ ] |
| TECH-004 | US-012 | Hardcoded color cleanup | MTH | [ ] | [ ] | [ ] |
| TECH-005 | US-001 | Font loading strategy | MTH | [ ] | [ ] | [ ] |
| TECH-006 | BR-008 | CSS animation definitions | MTH | [ ] | [ ] | [ ] |
| TECH-007 | US-015, US-016 | Breakpoint system | NTH | [ ] | [ ] | [ ] |
| TECH-008 | US-002 | Code block syntax highlighting | NTH | [ ] | [ ] | [ ] |
| INT-001 | US-001 | Google Fonts integration | MTH | [ ] | [ ] | [ ] |
| INT-002 | US-008 | Lucide Icons integration | MTH | [ ] | [ ] | [ ] |
| DATA-001 | BR-005 | LocalStorage theme preference | MTH | [ ] | [ ] | [ ] |
| DATA-002 | BR-011 | LocalStorage font size preference | MTH | [ ] | [ ] | [ ] |
| NFR-001 | NFR-Performance | Theme switch < 300ms | MTH | [ ] | [ ] | [ ] |
| NFR-002 | NFR-Accessibility | WCAG 2.2 AA color contrast | MTH | [ ] | [ ] | [ ] |
| NFR-003 | NFR-Accessibility | Keyboard navigation all elements | MTH | [ ] | [ ] | [ ] |
| NFR-004 | NFR-Accessibility | Visible focus indicators | MTH | [ ] | [ ] | [ ] |
| NFR-005 | BR-023, BR-024, BR-025 | Responsive layout at all breakpoints | NTH | [ ] | [ ] | [ ] |

## 2.9 Non-Functional Requirements Detail

### NFR-001: Theme Performance [MTH]
**Description**: Theme switching must complete within 300ms with no visible flicker.
**Acceptance Criteria**:
- AC-001: Theme transition completes within 300ms
- AC-002: No FOUC on page load
- AC-003: CSS transitions use GPU-accelerated properties

### NFR-002: Color Contrast Compliance [MTH]
**Description**: All text/background combinations must meet WCAG 2.2 AA contrast ratios.
**Acceptance Criteria**:
- AC-001: Normal text: 4.5:1 minimum contrast ratio
- AC-002: Large text: 3:1 minimum
- AC-003: UI components: 3:1 minimum

### NFR-003: Keyboard Navigation [MTH]
**Description**: All interactive elements must be navigable via keyboard.
**Acceptance Criteria**:
- AC-001: Tab navigates between elements
- AC-002: Enter/Space activates buttons and links
- AC-003: Escape closes modals and popovers
- AC-004: All interactive elements have visible focus indicators

### NFR-004: Focus Indicators [MTH]
**Description**: All interactive elements must show visible focus indicators matching design tokens.
**Acceptance Criteria**:
- AC-001: Focus indicator uses border-focus + 2px outline
- AC-002: Focus is visible in both Dark and Light themes

### NFR-005: Responsive Layout [NTH]
**Description**: Application layout adapts correctly at all defined breakpoints.
**Acceptance Criteria**:
- AC-001: >1280px: Full sidebar visible
- AC-002: 1024-1280px: Icon-only sidebar
- AC-003: <1024px: Drawer-based sidebar

---

## Verification Section

### Part 1 to Part 2 Traceability

| Part 1 Area | User Stories | Part 2 Epics/Requirements |
|-------------|-------------|---------------------------|
| 1.4.1 Design Token System | US-001, US-002 | EPIC-001 (REQ-001-001-001 through REQ-001-002-003) |
| 1.4.2 Theme System | US-003, US-004, US-005 | EPIC-002 (REQ-002-001-001 through REQ-002-002-002) |
| 1.4.3 Font Size Accessibility | US-006, US-007 | EPIC-003 (REQ-003-001-001, REQ-003-002-001) |
| 1.4.4 Component Library | US-008, US-009, US-010 | EPIC-004 (REQ-004-001-001 through REQ-004-007-001) |
| 1.4.5 Page Migration | US-011, US-012 | EPIC-005 (REQ-005-001-001 through REQ-005-007-001) |
| 1.4.6 Domain-Specific Components | US-013, US-014 | EPIC-006 (REQ-006-001-001 through REQ-006-003-001) |
| 1.4.7 Responsive Design | US-015, US-016 | NFR-005, TECH-007 |

### Summary Statistics

| Metric | Value |
|--------|-------|
| Total Epics | 6 |
| Total Features | 23 |
| Total Functional Requirements (REQ) | 48 |
| Total Technical Requirements (TECH) | 8 |
| Total Integration Requirements (INT) | 2 |
| Total Data Requirements (DATA) | 2 |
| Total Non-Functional Requirements (NFR) | 5 |
| **Grand Total** | **65** |
| MTH Requirements | 54 |
| NTH Requirements | 11 |
| User Stories | 16 |
| Business Rules | 25 |

---

_Document generated by SoftwareBuilderX v23.0.0_
