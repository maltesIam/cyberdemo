# AgentFlow Design System - Functional Description

## Unification of Visual Design, UX, UI, and Component System

**Version:** 1.1.0
**Date:** February 2026
**Scope:** All web applications in the SoulInTheBot ecosystem
**Reference Documents:**
- `style-guide-v2.html` (Dark theme — primary reference)
- `style-guide-light-v2.html` (Light theme — complementary reference)

**Target Projects:**
- CyberDemo Frontend (`cyberdemo/frontend/`) — React + Tailwind
- Medicum Demo (`SoulInTheBot/AIPerson/person.ai/medicum-demo/`) — React + Tailwind + Zustand
- Files Manager (`SoulInTheBot/AIPerson/ui/`) — Lit Web Components + CSS Custom Properties

---

## 1. Purpose and Objective

This functional description defines the complete visual and interaction overhaul of all web applications in the SoulInTheBot ecosystem. The goal is to unify every page, component, and interaction pattern under the **AgentFlow Design System v2.0**, ensuring:

- **Visual consistency** across all projects (same colors, typography, spacing, components)
- **Dual-theme support** (Dark + Light + System preference detection)
- **Accessibility controls** (font size scaling via header button)
- **Professional enterprise-grade appearance** inspired by Linear, Vercel, Stripe, n8n, and other top-tier B2B platforms

---

## 2. Target Applications

### 2.1 CyberDemo Frontend
- **Technology:** React 18 + Vite + Tailwind CSS
- **Location:** `cyberdemo/frontend/`
- **Pages (18 routes):**
  - `/surface` - Command Center
  - `/generation` - Generation (default/home)
  - `/dashboard` - Main Dashboard
  - `/assets` - Asset Management
  - `/incidents` - Incident Tracking
  - `/detections` - Detection Alerts
  - `/ctem` - Continuous Threat Exposure Management
  - `/vulnerabilities` - Vulnerability Dashboard
  - `/vulnerabilities/cves/:cveId` - CVE Detail
  - `/vulnerabilities/cves/:cveId/assets` - CVE Assets
  - `/vulnerabilities/cves/:cveId/exploits` - CVE Exploits
  - `/vulnerabilities/ssvc` - SSVC Dashboard
  - `/threats` - Threat Intel
  - `/timeline` - Incident Timeline
  - `/postmortems` - Postmortems
  - `/tickets` - Ticket Management
  - `/graph` and `/graph/:incidentId` - Attack Graph Visualization
  - `/collab` - Collaboration
  - `/config` - System Configuration
  - `/audit` - Audit Log
  - `/simulation` - Attack Simulation
- **Current styling:** Tailwind CSS utility classes + custom CSS animations in `index.css`
- **Current theme:** Dark only (gray-900 backgrounds, cyan-500 accents)

### 2.2 Medicum Demo (Historia Clínica Electrónica)
- **Technology:** React 18 + Vite + TypeScript + Tailwind CSS 3.3 + Zustand 4.4
- **Location:** `SoulInTheBot/AIPerson/person.ai/medicum-demo/`
- **Pages (4 tabs, single-page app):**
  - **Consulta** — Transcription with Whisper + SOAP note generation (two-panel: transcription left, SOAP right)
  - **Historia** — Patient history with accordion sections (antecedentes, cirugías, laboratorio, episodios)
  - **Codificación** — CIE-10 (ICD-10) coding interface with AI suggestions, search, assigned codes panel
  - **Visor** — Medical image viewer with zoom controls, AI analysis, findings with confidence scores, radiological reports
- **Current styling:** Tailwind utility classes + custom `medical.*` and `severity.*` color palette in `tailwind.config.js`
- **Current theme:** Light mode only (`bg-gray-100` body, `bg-white` cards, `text-gray-900` text)
- **Current fonts:** System font stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, ...`)
- **Current color palette:**
  - Primary: `#0066CC` (medical-primary)
  - Secondary: `#4A90D9` (medical-secondary)
  - Success: `#28A745`, Warning: `#FFC107`, Danger: `#DC3545`, Info: `#17A2B8`
  - Severity: High `#DC3545`, Medium `#FD7E14`, Low `#FFC107`
- **Key UI patterns:**
  - White cards: `bg-white rounded-lg shadow-sm border border-gray-200`
  - Primary buttons: `bg-medical-primary text-white hover:bg-blue-700`
  - Right sidebar: fixed `w-96` in all tabs
  - Focus rings: `focus:ring-2 focus:ring-medical-primary`
  - Confidence badges: color-coded by threshold (green ≥90%, yellow ≥70%, gray below)
  - ICD codes: `font-mono text-sm font-medium text-medical-primary`
- **Icons:** Lucide React (Stethoscope, FileText, Code, Image, ZoomIn, ZoomOut, Scan, etc.)

### 2.3 Files Manager (Gestor de Archivos)
- **Technology:** Lit 3.1 Web Components + CSS Custom Properties + Vite 5.4 + TypeScript
- **Location:** `SoulInTheBot/AIPerson/ui/`
- **Views:** Single-page Nautilus-style file manager
  - **Sidebar** — Directory tree navigation (resizable 200-400px, default 250px)
  - **Toolbar** — Search input + clipboard badge + paste/create folder buttons
  - **File list** — Sortable grid (name, size, modified, actions) with row selection
  - **Modals** — Delete confirmation, create directory, rename directory
  - **Upload progress bar** — Inline progress with percentage
  - **Toast notifications** — Error, success, warning, info variants
  - **Breadcrumb** — Path navigation with clickable segments
- **Current styling:** CSS custom properties (`--files-*` namespace) in single `files.css` (1080 lines)
- **Current theme:** Dark-first (`#1a1a2e` bg) with `[data-theme="light"]` overrides defined but **no UI toggle connected**
- **Current fonts:** Inter + JetBrains Mono (already matching AgentFlow target)
- **Current color palette:**
  - Primary: `#3b82f6` (blue — matches AgentFlow primary-500)
  - Secondary: `#06b6d4` (cyan — matches AgentFlow secondary-500)
  - Error: `#ef4444`, Success: `#10b981`, Warning: `#f59e0b`
  - Dark backgrounds: `#1a1a2e`, `#16213e`, `#0f3460`
  - Light backgrounds: `#ffffff`, `#f5f5f5`, `#ebebeb`
  - Borders: `#2d3a4f` (dark), `#d0d0d0` (light)
- **Key UI patterns:**
  - Two-panel layout: sidebar + main content
  - Action buttons per row: cut (✂), copy (📋), download (⬇), delete (🗑)
  - Custom scrollbars (webkit)
  - Resize handle between sidebar and main content
  - Clipboard badge with cut/copy state
- **Components (LitElement):** `<files-view>`, `<upload-progress-bar>`, `<delete-confirmation-modal>`, `<file-actions-buttons>`

---

## 3. Reference Design System: AgentFlow v2.0

The definitive source of truth for all design decisions is the pair of style guide documents:

### 3.1 Design Principles (from the guides)

| Principle | Description |
|-----------|-------------|
| **Clarity Over Complexity** | Every element must earn its place on screen. When in doubt, simplify. |
| **Progressive Disclosure** | Show what's needed, when it's needed. Surface essential info first, drill into details on demand. |
| **Trust Through Transparency** | Users must always understand what's happening and why. Show the work. |
| **Speed & Responsiveness** | Inspired by Linear. Every interaction should feel instant. Optimistic UI. |
| **Accessible Intelligence** | WCAG 2.2 AA compliance as the floor. Keyboard nav, screen reader support. |
| **Consistent Patterns** | Once a user learns an interaction, it should work everywhere. |
| **Flow-First Design** | Visual connections, smooth transitions, directional movement. |
| **Restrained Elegance** | No gratuitous decoration. Every shadow, color, animation serves a purpose. |

### 3.2 Reference Applications Analyzed

The design system is built on analysis of 10 leading B2B platforms:

| Application | What We Adopt |
|-------------|---------------|
| **Linear** | Performance-first mindset, dark mode default, command palette |
| **Notion** | Modular component architecture, content-first typography |
| **Vercel** | Design tokens, monochrome base + strategic color, font choices |
| **Stripe** | Data visualization patterns, consistent component API |
| **Figma** | Panel-based workspace, contextual actions, collaborative patterns |
| **n8n** | Canvas patterns, node design, execution feedback, visual flow |
| **Retool** | Component composition, data table patterns, form layouts |
| **Dify** | AI config panels, prompt editing UX, model selection patterns |
| **CrewAI** | Agent cards, team management, execution monitoring |
| **Langflow** | Flow visualization, config panels, integration marketplace |

---

## 4. Design Tokens (CSS Custom Properties)

All applications MUST use these exact CSS custom properties. This is the single source of truth for every visual value.

### 4.1 Color System

#### Primary Colors - Blue (AI / Intelligence)
```
--color-primary-50:  #eff6ff
--color-primary-100: #dbeafe
--color-primary-200: #bfdbfe
--color-primary-300: #93c5fd
--color-primary-400: #60a5fa
--color-primary-500: #3b82f6
--color-primary-600: #2563eb   ← Main brand color
--color-primary-700: #1d4ed8
--color-primary-800: #1e40af
--color-primary-900: #1e3a8a
--color-primary-950: #172554
```

#### Secondary Colors - Cyan (Automation / Flow)
```
--color-secondary-50:  #ecfeff
--color-secondary-100: #cffafe
--color-secondary-200: #a5f3fc
--color-secondary-300: #67e8f9
--color-secondary-400: #22d3ee
--color-secondary-500: #06b6d4
--color-secondary-600: #0891b2
--color-secondary-700: #0e7490
--color-secondary-800: #155e75
--color-secondary-900: #164e63
--color-secondary-950: #083344
```

#### Accent Colors - Amber (Highlights / Attention)
```
--color-accent-50:  #fffbeb
--color-accent-100: #fef3c7
--color-accent-200: #fde68a
--color-accent-300: #fcd34d
--color-accent-400: #fbbf24
--color-accent-500: #f59e0b
--color-accent-600: #d97706
--color-accent-700: #b45309
--color-accent-800: #92400e
--color-accent-900: #78350f
```

#### Neutral Colors - Slate
```
--color-neutral-0:   #ffffff
--color-neutral-50:  #f8fafc
--color-neutral-100: #f1f5f9
--color-neutral-200: #e2e8f0
--color-neutral-300: #cbd5e1
--color-neutral-400: #94a3b8
--color-neutral-500: #64748b
--color-neutral-600: #475569
--color-neutral-700: #334155
--color-neutral-800: #1e293b
--color-neutral-900: #0f172a
--color-neutral-950: #020617
```

#### Semantic Colors
```
--color-success-light: #dcfce7    --color-success: #22c55e    --color-success-dark: #15803d
--color-warning-light: #fef9c3    --color-warning: #eab308    --color-warning-dark: #a16207
--color-error-light:   #fee2e2    --color-error:   #ef4444    --color-error-dark:   #b91c1c
--color-info-light:    #dbeafe    --color-info:    #3b82f6    --color-info-dark:    #1d4ed8
```

#### Agent Status Colors
```
--color-agent-idle:    #94a3b8
--color-agent-running: #3b82f6
--color-agent-success: #22c55e
--color-agent-error:   #ef4444
--color-agent-waiting: #f59e0b
--color-agent-queued:  #06b6d4
```

### 4.2 Theme Tokens

#### Dark Theme (`[data-theme="dark"]`)
```
--bg-primary:    #020617 (neutral-950)
--bg-secondary:  #0f172a (neutral-900)
--bg-tertiary:   #1e293b (neutral-800)
--bg-elevated:   #1e293b (neutral-800)
--bg-hover:      rgba(148,163,184,0.08)
--bg-active:     rgba(148,163,184,0.12)
--bg-input:      #0f172a (neutral-900)
--bg-card:       rgba(30,41,59,0.5)

--text-primary:   #f8fafc (neutral-50)
--text-secondary: #94a3b8 (neutral-400)
--text-tertiary:  #64748b (neutral-500)
--text-inverse:   #020617 (neutral-950)
--text-link:      #60a5fa (primary-400)

--border-primary:   #334155 (neutral-700)
--border-secondary: #1e293b (neutral-800)
--border-focus:     #3b82f6 (primary-500)

--shadow-card: 0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2)

color-scheme: dark
```

#### Light Theme (`[data-theme="light"]`)
```
--bg-primary:    #ffffff (neutral-0)
--bg-secondary:  #f8fafc (neutral-50)
--bg-tertiary:   #f1f5f9 (neutral-100)
--bg-elevated:   #ffffff (neutral-0)
--bg-hover:      rgba(15,23,42,0.04)
--bg-active:     rgba(15,23,42,0.08)
--bg-input:      #ffffff (neutral-0)
--bg-card:       #ffffff (neutral-0)

--text-primary:   #0f172a (neutral-900)
--text-secondary: #475569 (neutral-600)
--text-tertiary:  #64748b (neutral-500)
--text-inverse:   #ffffff (neutral-0)
--text-link:      #2563eb (primary-600)

--border-primary:   #e2e8f0 (neutral-200)
--border-secondary: #f1f5f9 (neutral-100)
--border-focus:     #3b82f6 (primary-500)

--shadow-card: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04)

color-scheme: light
```

### 4.3 Typography

#### Font Families
```
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
--font-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace
```

#### Type Scale
| Token | Size | Weight | Use |
|-------|------|--------|-----|
| `--text-5xl` | 3rem (48px) | 800 extrabold | Display headings, hero text |
| `--text-4xl` | 2.25rem (36px) | 700 bold | Page titles |
| `--text-3xl` | 1.875rem (30px) | 700 bold | Section headings |
| `--text-2xl` | 1.5rem (24px) | 600 semibold | Subsection headings |
| `--text-xl` | 1.25rem (20px) | 600 semibold | Card titles |
| `--text-lg` | 1.125rem (18px) | 400 regular | Large body text, introductions |
| `--text-base` | 1rem (16px) | 400 regular | Default body text |
| `--text-sm` | 0.875rem (14px) | 400 regular | Secondary text, UI labels |
| `--text-xs` | 0.75rem (12px) | 500 medium | Captions, metadata, timestamps |

#### Font Weights
```
--weight-light:     300   (Decorative, large headings only)
--weight-regular:   400   (Body text default)
--weight-medium:    500   (UI labels, buttons, navigation)
--weight-semibold:  600   (Subheadings, emphasis)
--weight-bold:      700   (Section titles, headings)
--weight-extrabold: 800   (Display headings, hero text)
```

#### Line Heights
```
--leading-tight:    1.25
--leading-snug:     1.375
--leading-normal:   1.5
--leading-relaxed:  1.625
```

#### Monospace (Code & Data)
- Code Regular: 14px (`--text-sm`)
- Code Small: 12px (`--text-xs`)
- Code Bold: 14px / 600 semibold

### 4.4 Spacing System (4px base grid)
```
--space-0:  0
--space-1:  0.25rem  (4px)
--space-2:  0.5rem   (8px)
--space-3:  0.75rem  (12px)
--space-4:  1rem     (16px)
--space-5:  1.25rem  (20px)
--space-6:  1.5rem   (24px)
--space-8:  2rem     (32px)
--space-10: 2.5rem   (40px)
--space-12: 3rem     (48px)
--space-16: 4rem     (64px)
--space-20: 5rem     (80px)
--space-24: 6rem     (96px)
```

### 4.5 Border Radius
```
--radius-sm:   0.25rem  (4px)   - Checkboxes, small tags
--radius-md:   0.375rem (6px)   - Inputs, nav links, dropdowns
--radius-lg:   0.5rem   (8px)   - Buttons, cards inner elements
--radius-xl:   0.75rem  (12px)  - Cards, panels, modals
--radius-2xl:  1rem     (16px)  - Large containers
--radius-full: 9999px            - Badges, avatars, pills
```

### 4.6 Shadows & Elevation
```
--shadow-xs:           0 1px 2px rgba(0,0,0,0.05)                              — Subtle element separation
--shadow-sm:           0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)  — Cards, inputs
--shadow-md:           0 4px 6px -1px rgba(0,0,0,0.1), ...                     — Dropdowns, popovers
--shadow-lg:           0 10px 15px -3px rgba(0,0,0,0.1), ...                   — Modals, side panels
--shadow-xl:           0 20px 25px -5px rgba(0,0,0,0.1), ...                   — Command palette, top overlays
--shadow-glow-primary: 0 0 20px rgba(59,130,246,0.3)                           — Active/focused workflow nodes
--shadow-glow-secondary: 0 0 20px rgba(6,182,212,0.3)                          — Secondary glow effects
```

### 4.7 Transitions & Motion
```
--duration-fast:   100ms   — Hover states, toggle, small UI feedback
--duration-normal: 200ms   — Button clicks, input focus, card interactions
--duration-slow:   300ms   — Panel open/close, theme switch, page transitions
--duration-slower: 500ms   — Complex animations, workflow node movement

--ease-default: cubic-bezier(0.4, 0, 0.2, 1)    — General-purpose easing
--ease-in:      cubic-bezier(0.4, 0, 1, 1)       — Exit animations
--ease-out:     cubic-bezier(0, 0, 0.2, 1)        — Enter animations
--ease-spring:  cubic-bezier(0.34, 1.56, 0.64, 1) — Playful bounce for toggles, badges
```

### 4.8 Z-Index Scale
```
--z-base:     0
--z-dropdown: 100
--z-sticky:   200
--z-overlay:  300
--z-modal:    400
--z-popover:  500
--z-tooltip:  600
--z-toast:    700
```

### 4.9 Breakpoints
```
--bp-sm:  640px   — Mobile landscape, large phones
--bp-md:  768px   — Tablets
--bp-lg:  1024px  — Small laptops, tablets landscape
--bp-xl:  1280px  — Desktops (primary target)
--bp-2xl: 1536px  — Large displays
```

### 4.10 Container & Layout
```
--container-max: 1280px
--sidebar-width: 280px
```

---

## 5. Component Catalog

All projects MUST use these component patterns. Every component uses the design tokens defined above.

### 5.1 Buttons

**Variants:**
| Variant | Background | Text | Hover Effect |
|---------|-----------|------|-------------|
| **Primary** | `primary-600` | white | `primary-700` + translateY(-1px) + glow |
| **Secondary** | transparent | `text-primary` | `bg-hover` + border highlight |
| **Ghost** | transparent | `text-secondary` | `bg-hover` + text primary |
| **Destructive** | `color-error` | white | `error-dark` |
| **Accent** | `secondary-600` | white | `secondary-700` + secondary glow |

**Sizes:**
| Size | Font | Padding | Height |
|------|------|---------|--------|
| Small (`btn-sm`) | `text-xs` | 6px 12px | 32px |
| Medium (`btn-md`) | `text-sm` | 8px 16px | 36px |
| Large (`btn-lg`) | `text-base` | 10px 20px | 44px |

**States:** Default, Hover (translateY -1px, glow), Focus (2px outline, primary-500), Disabled (opacity 0.5), Loading (spinner animation)

**Icon Button:** `btn-icon` - Square button (width = height of current size), centered icon

### 5.2 Form Inputs

**Text Input:**
- Font: `font-sans`, `text-sm`
- Background: `bg-input`
- Border: 1px `border-primary`, radius `radius-lg`
- Height: 36px default, 32px small, 44px large
- Focus: `border-focus` + blue ring (3px rgba(59,130,246,0.15))
- Error: red border + red ring
- Placeholder: `text-tertiary`

**Textarea:** Same styling, auto height, min-height 80px, vertical resize

**Select:** Same as input + custom arrow SVG

**Toggle Switch:** 44x24px pill, white circle knob, `neutral-600` off, `primary-600` on, spring easing

**Checkbox:** 18x18px, `radius-sm`, `border-primary`, checked = `primary-600` + white checkmark

**Radio:** 18x18px, circle, checked = `primary-600` border + filled inner circle

**Input Group:** Label (`text-sm` medium) + Input + Hint (`text-xs` tertiary) or Error message (`text-xs` red)

### 5.3 Cards

**Base Card:**
- Background: `bg-card`
- Border: 1px `border-secondary`, radius `radius-xl`
- Padding: `space-6`
- Interactive variant: hover = `border-primary` + `shadow-card` + translateY(-2px)

**Agent Card:**
- Layout: Flex row, avatar (40x40, gradient, radius-lg) + info column + status badge
- Hover: `primary-500` border + primary glow

**Metric Card:**
- Label: `text-xs`, uppercase, tertiary, `weight-medium`, letter-spacing 0.05em
- Value: `text-3xl`, `weight-bold`, letter-spacing -0.02em
- Change indicator: `text-xs`, green (up) or red (down) with arrow

**Integration Card:** Interactive card with icon (40x40) + title/description + status badge

### 5.4 Badges & Tags

**Badges:** Pill shape (`radius-full`), `text-xs`, `weight-medium`, 2px 8px padding
| Variant | Background | Text Color |
|---------|-----------|-----------|
| Default | `bg-tertiary` | `text-secondary` |
| Primary | `rgba(59,130,246,0.15)` | `primary-400` |
| Secondary | `rgba(6,182,212,0.15)` | `secondary-400` |
| Success | `rgba(34,197,94,0.15)` | `color-success` |
| Warning | `rgba(245,158,11,0.15)` | `accent-400` |
| Error | `rgba(239,68,68,0.15)` | `color-error` |

**Tags:** `radius-md`, 1px `border-primary`, `bg-tertiary`, `text-secondary`, 4px 10px padding

### 5.5 Alerts & Toasts

**Inline Alerts:** Flex row, icon + content (title + description), colored left hint, semi-transparent colored backgrounds
- Info: blue
- Success: green
- Warning: amber
- Error: red

**Toast Notifications:** Floating cards, `bg-elevated`, `border-primary`, `shadow-lg`, max-width 380px, close button

### 5.6 Tables

- Container: `border-secondary`, `radius-xl`, overflow-x auto
- Header: `bg-tertiary`, `text-xs`, uppercase, `weight-medium`, letter-spacing 0.05em
- Rows: `text-sm`, `text-primary`, `border-secondary` bottom
- Hover: `bg-hover`
- Pagination footer: `text-xs`, `text-tertiary`

### 5.7 Navigation Components

**Tabs:** Horizontal flex, `text-sm`, `weight-medium`, 2px bottom border, active = `primary-400` + colored border

**Breadcrumbs:** Flex row, `text-sm`, separator "›", current item = `text-primary` + `weight-medium`

**Sidebar Navigation:**
- Fixed left, `sidebar-width` (280px), `bg-secondary`
- Logo: gradient text (`primary-400` to `secondary-400`)
- Nav groups with uppercase titles (`text-xs`, `weight-semibold`, `text-tertiary`)
- Nav links: `text-sm`, `text-secondary`, `radius-md`, hover = `bg-hover`, active = primary tint

**Command Palette:** Modal overlay with search input, suggestion list, keyboard shortcut hints

### 5.8 Modals & Dialogs

- Overlay: `rgba(0,0,0,0.6)` + backdrop blur 4px
- Modal: `bg-elevated`, `border-primary`, `radius-xl`, `shadow-xl`, max-width 480px
- Header: title (`text-lg`, `weight-semibold`) + optional description
- Footer: flex end, `space-3` gap between buttons

### 5.9 Tooltips

- Background: `neutral-800`, text: `neutral-100`
- `text-xs`, `radius-md`, padding 6px 10px
- Arrow pointing down
- Position: above element by default

### 5.10 Progress & Loading

**Progress Bar:** 6px height, `bg-tertiary`, fill = gradient (`primary-600` to `secondary-500`)

**Skeleton Loading:** Shimmer animation (gradient sweep), `radius-md`

**Spinner:** 16px circle, 2px border, `spin` animation 0.6s linear infinite

### 5.11 Code Blocks

- Background: `neutral-900` (dark) / `neutral-50` (light)
- Header: filename + copy button
- Pre: `font-mono`, `text-sm`, `leading-relaxed`
- Syntax highlighting: keywords (`primary-400`), strings (`success`), functions (`secondary-400`), numbers (`accent-400`), comments (`text-tertiary`)

### 5.12 Empty States

- Centered, `space-16` top/bottom padding
- Large icon (48px, opacity 0.5)
- Title: `text-lg`, `weight-semibold`
- Description: `text-sm`, `text-secondary`, max-width 360px
- CTA button below

---

## 6. Domain-Specific Components

### 6.1 Workflow Canvas

- Background: `bg-secondary` with dot grid pattern (`border-secondary`, 24px spacing)
- **Workflow Nodes:** `bg-elevated`, 2px `border-primary`, `radius-xl`, `shadow-md`, draggable
  - Hover: `primary-500` border + glow
  - Active: same as hover
  - Node icon types: Trigger (amber gradient), Agent (blue gradient), Tool (cyan gradient), Output (green gradient)
  - Ports: 12px circles on edges, scale 1.3 on hover

- **Connection Lines:** SVG paths, `primary-500` stroke, 2px width, 0.6 opacity
  - Animated variant: dashed with flow animation

### 6.2 Agent Status Components

Agent status badges with animated pulsing dot:
- Running: blue background + pulsing blue dot
- Idle: slate background + static slate dot
- Success: green background + static green dot
- Error: red background + pulsing red dot
- Waiting: amber background + pulsing amber dot
- Queued: cyan background + pulsing cyan dot

### 6.3 Execution Timeline

Vertical timeline with connected steps:
- Step dots: 24px circles, colored by status (success/running/error/pending)
- Connecting line: 2px vertical `border-secondary`
- Step info: name (`text-sm`, `weight-medium`) + meta (`text-xs`, `text-tertiary`)

### 6.4 Log Viewer

- Dark background (`neutral-950` dark / `neutral-900` light)
- `font-mono`, `text-xs`
- Filter tabs in header
- Log lines: timestamp (tertiary) + level badge (colored) + message
- Max-height 200px with scroll

### 6.5 Metrics Dashboard

Grid of metric cards (4 columns on desktop) with:
- Label (uppercase, tertiary)
- Value (3xl, bold)
- Change indicator (colored arrow + percentage)

---

## 7. Theme System

### 7.1 Three-Mode Theme Toggle

**Location:** Top-right corner of every page header/toolbar

**Behavior:**
- **Dark mode:** Forces `[data-theme="dark"]` on `<html>`
- **Light mode:** Forces `[data-theme="light"]` on `<html>`
- **System mode:** Uses `prefers-color-scheme` media query to detect OS preference and applies accordingly

**Toggle UI Component:**
- Pill-shaped container (`radius-full`), `bg-tertiary`, 1px `border-primary`
- Three buttons inside: icons/labels for Dark (moon icon), Light (sun icon), System (monitor icon)
- Active button: `primary-600` background, white text
- Inactive buttons: `text-secondary`, transparent background
- Transition: `duration-normal` with `ease-default`

**Persistence:**
- User choice saved to `localStorage` under key `theme-preference`
- On page load, check localStorage first; if "system", apply media query detection
- Theme preference is per-project (each app manages its own)

**Implementation requirement:** All visual values MUST use the theme-aware semantic tokens (`--bg-primary`, `--text-primary`, etc.) NOT the raw color tokens directly. This ensures automatic theme switching.

### 7.2 Theme Transition

When switching themes:
- `background` and `color` on `<body>` transition with `duration-slow` (300ms) + `ease-default`
- All other elements that use theme tokens automatically transition through CSS inheritance
- No flash of unstyled content (FOUC) — apply theme from localStorage before first paint

---

## 8. Font Size Accessibility Control

### 8.1 Cyclic Font Size Button

**Location:** Top-right corner of the header, immediately to the LEFT of the theme toggle

**Icon:** Typography/text size icon (e.g., "Aa" or a font-size icon from Lucide)

**Behavior (3 states, cyclic):**
1. **Normal (default):** Base font size = 16px (1rem). Button shows normal state.
2. **First click → Medium:** Base font size increases by 2px → 18px. Button shows visual indicator (e.g., one dot or "A+").
3. **Second click → Large:** Base font size increases by 2 more px → 20px. Button shows stronger indicator (e.g., two dots or "A++").
4. **Third click → Back to Normal:** Resets to 16px. Cycle restarts.

**Implementation:**
- Modify `html { font-size: Xpx }` dynamically since all sizes use `rem`
- This means ALL text in the application scales proportionally
- Store current step in `localStorage` under key `font-size-step` (values: 0, 1, 2)
- On page load, restore from localStorage

**Visual feedback:**
- The button itself should visually indicate the current size level
- Tooltip on hover: "Font size: Normal / Medium / Large"
- Smooth transition on font size change

---

## 9. Layout Patterns

### 9.1 Dashboard Layout
- Icon sidebar (56px) OR full sidebar (280px)
- Top bar (sticky, backdrop blur, `bg-primary` at 0.8 opacity)
- Dashboard grid: metric cards (4 columns) + chart area (3/4) + activity feed (1/4)

### 9.2 Workflow Editor Layout
- Icon sidebar (56px)
- Component panel (220px left)
- Canvas (flexible center) with floating toolbar
- Config panel (280px right)

### 9.3 Standard Page Layout
- Full sidebar (280px) with navigation groups
- Sticky header with page title + actions + theme/font controls
- Content area (max-width 960px centered or full-width for dashboards)

### 9.4 Grid System
- 12-column flexible grid
- Common patterns:
  - Sidebar (3 cols) + Main content (9 cols)
  - Three equal panels (4 + 4 + 4)
  - Two equal panels (6 + 6)

---

## 10. Responsive Design

Desktop-first approach (B2B productivity tool). All applications must adapt:

| Breakpoint | Sidebar | Canvas/Content | Config Panel | Tables |
|------------|---------|---------------|-------------|--------|
| >1280px | Full sidebar visible | Full canvas with toolbar | Side panel (280px) | Full columns |
| 1024-1280px | Icon-only sidebar (56px) | Full canvas | Overlay panel | Hide secondary columns |
| 768-1024px | Drawer (hamburger toggle) | Simplified canvas | Bottom sheet | Horizontal scroll |
| <768px | Drawer (hamburger toggle) | Read-only view | Full-screen modal | Card-based list |

---

## 11. Accessibility Requirements

### 11.1 WCAG 2.2 AA Compliance (minimum)

**Color Contrast:**
- Normal text: 4.5:1 minimum
- Large text: 3:1 minimum
- UI components: 3:1 minimum
- Critical text: target 7:1 (AAA)

**Keyboard Navigation:**
- `Tab` — Navigate between elements
- `Enter` / `Space` — Activate buttons/links
- `Esc` — Close modals/popovers
- `Cmd+K` — Open command palette
- All interactive elements must have visible focus indicators (`border-focus` + 2px outline)

**ARIA Requirements:**
- All interactive elements: proper ARIA labels
- Workflow canvas: `aria-live` regions for execution updates
- Modal dialogs: focus trap
- Toast notifications: `role="status"`
- Theme toggle: `aria-label="Theme selector"`, each button `aria-pressed`
- Font size button: `aria-label="Adjust font size"`, announce current level

**Screen Reader:**
- Meaningful alt text for all icons and images
- Live regions for dynamic content updates
- Logical heading hierarchy (h1 → h2 → h3)

---

## 12. Iconography

**Library:** Lucide Icons (consistent, clean, open-source)

**Default size:** 24px
**Stroke width:** 1.5 (for 24px+), 2 (for 16-20px)
**Available sizes:** 16px, 20px, 24px, 32px
**Color:** Inherits from `currentColor` (follows text color)

---

## 13. Animation Guidelines

### 13.1 Standard Animations
| Animation | Duration | Easing | Use |
|-----------|----------|--------|-----|
| Fade In | 300ms | `ease-default` | Page elements appearing |
| Scale Up | 300ms | `ease-default` | Modal opening, card expanding |
| Slide Up | 300ms | `ease-default` | Toast appearing, panel sliding in |
| Bounce | 500ms | `ease-spring` | Toggle confirmation, badge highlight |

### 13.2 Data Flow Animations
- Dashed stroke with `flowDash` animation for connection lines
- Pulse animation (2s infinite) for running agent dots
- Shimmer animation (1.5s infinite) for skeleton loading

### 13.3 Theme Switch Animation
- Background and text: `duration-slow` (300ms)
- All other properties: inherit transition naturally

---

## 14. Implementation Strategy

### 14.1 CyberDemo Frontend (React + Tailwind)

**Approach:**
1. Create a shared `design-tokens.css` file with all CSS custom properties from Section 4
2. Configure Tailwind to reference the CSS custom properties (extend theme in `tailwind.config.js`)
3. Add `[data-theme]` attribute toggling on `<html>` element
4. Create React context/hook for theme management (`useTheme`)
5. Create React context/hook for font size management (`useFontSize`)
6. Build `ThemeToggle` and `FontSizeButton` React components
7. Place both controls in the `Layout.tsx` header
8. Systematically replace all hardcoded colors/spacing with design token references across all 18 pages and all components

### 14.2 Medicum Demo (React + Tailwind)

**Approach:**
1. Create a shared `design-tokens.css` file with all CSS custom properties from Section 4 (or import the same one from CyberDemo)
2. Replace the `medical.*` and `severity.*` color palette in `tailwind.config.js` with AgentFlow design token references
3. Map existing semantic colors: `medical-primary → primary-600`, `medical-secondary → primary-400`, `severity-high → color-error`, `severity-medium → accent-500`, `severity-low → color-warning`
4. Add `[data-theme]` attribute toggling on `<html>` element (currently light-only)
5. Replace system font stack with Inter + JetBrains Mono
6. Create or reuse the same `useTheme` and `useFontSize` React hooks from CyberDemo
7. Build `ThemeToggle` and `FontSizeButton` components (or share from CyberDemo if monorepo structure allows)
8. Place both controls in the `PatientHeader` component (top-right area, next to connection status)
9. Systematically replace all hardcoded Tailwind color classes:
   - `bg-white` → `bg-[var(--bg-elevated)]` or equivalent
   - `bg-gray-100` → `bg-[var(--bg-primary)]`
   - `bg-gray-50` → `bg-[var(--bg-secondary)]`
   - `text-gray-900` → `text-[var(--text-primary)]`
   - `text-gray-600` → `text-[var(--text-secondary)]`
   - `border-gray-200` → `border-[var(--border-primary)]`
   - `bg-medical-primary` → `bg-[var(--color-primary-600)]`
   - etc. for all 4 tabs and all components
10. Special attention for the Visor tab: `bg-gray-900` image area should use `--bg-primary` in dark mode (already dark) and a dedicated dark canvas background in light mode
11. Special attention for CIE-10 tab: confidence badges and ICD codes must remain readable in both themes
12. Update the SOAP note colors, transcription bubbles, and allergy badges to use semantic tokens

### 14.3 Files Manager (Lit Web Components)

**Approach:**
1. The Files Manager **already uses CSS custom properties** with a `--files-*` namespace — this is the closest to the target architecture
2. Rename/remap `--files-*` variables to AgentFlow `--bg-*`, `--text-*`, `--border-*`, `--color-*` tokens (or create a mapping layer)
3. Update dark theme values: `#1a1a2e → #020617 (neutral-950)`, `#16213e → #0f172a (neutral-900)`, `#0f3460 → #1e293b (neutral-800)`
4. The light theme overrides already exist in `[data-theme="light"]` — update values to match AgentFlow light tokens
5. Fonts already match (Inter + JetBrains Mono) — no change needed
6. Accent colors `#3b82f6` and `#06b6d4` already match AgentFlow primary-500 and secondary-500 — minimal adjustment needed
7. **Build a theme toggle UI**: Currently no toggle exists — create a `<theme-toggle>` LitElement web component and place it in the toolbar area
8. **Build a font size button**: Create a `<font-size-button>` LitElement web component, place next to theme toggle
9. Fix hardcoded colors in `index.html` (loading spinner `#4a9eff`, error banner `#ff4444`) to use CSS variables
10. Fix hardcoded colors in `files-epic002.ts` component inline styles (modal backdrop, shadows)
11. Ensure toast notifications, modals, and progress bars all use the AgentFlow semantic tokens
12. Add the missing shadow and radius tokens to the CSS variable system

---

## 15. What Changes From Current State

### 15.1 CyberDemo — Key Changes
| Current | New |
|---------|-----|
| Dark mode only | Dark + Light + System toggle |
| Tailwind gray-900 backgrounds | AgentFlow neutral-950 (`#020617`) dark |
| Cyan-500 (`#06b6d4`) accent | Blue primary-600 (`#2563eb`) + cyan secondary |
| No font size control | 3-step cyclic font size button |
| Custom glow/pulse CSS | Standardized animation tokens |
| Ad-hoc component styles | Unified component library matching style guide |
| No Inter/JetBrains Mono fonts | Inter for UI + JetBrains Mono for code |

### 15.2 Medicum Demo — Key Changes
| Current | New |
|---------|-----|
| Light mode only | Dark + Light + System toggle |
| System font stack (`-apple-system, ...`) | Inter for UI + JetBrains Mono for code |
| Custom `medical-primary` (`#0066CC`) | AgentFlow primary-600 (`#2563eb`) |
| Custom `medical-secondary` (`#4A90D9`) | AgentFlow primary-400 (`#60a5fa`) |
| Custom `severity.high/medium/low` colors | AgentFlow semantic `color-error`, `color-warning`, `accent-500` |
| Hardcoded Tailwind classes (`bg-white`, `text-gray-900`) | CSS variable references via Tailwind (`bg-[var(--bg-elevated)]`) |
| No design token system | Full AgentFlow CSS custom properties |
| No font size control | 3-step cyclic font size button |
| `bg-gray-100` body background | `--bg-primary` (adapts to theme) |
| White cards with `border-gray-200` | `--bg-card` background with `--border-secondary` |
| Green/yellow/red confidence badges | Same semantic concept but with AgentFlow success/warning/error tokens |
| CIE-10 codes in `text-medical-primary` | CIE-10 codes in `--color-primary-600` / `--color-primary-400` (theme-aware) |

### 15.3 Files Manager — Key Changes
| Current | New |
|---------|-----|
| Dark backgrounds (`#1a1a2e`, `#16213e`, `#0f3460`) | AgentFlow dark (`#020617`, `#0f172a`, `#1e293b`) |
| Light backgrounds (`#ffffff`, `#f5f5f5`, `#ebebeb`) | AgentFlow light (`#ffffff`, `#f8fafc`, `#f1f5f9`) |
| Text `#e0e0e0` / `#a0a0a0` / `#606060` | AgentFlow `neutral-50` / `neutral-400` / `neutral-500` |
| `--files-*` variable namespace | AgentFlow `--bg-*`, `--text-*`, `--border-*` standard namespace |
| Borders `#2d3a4f` / `#252a3d` | AgentFlow `neutral-700` / `neutral-800` |
| No theme toggle UI (mechanism exists, no button) | Pill-shaped theme toggle (Dark/Light/System) in toolbar |
| No font size control | 3-step cyclic font size button |
| Emoji action buttons (✂📋⬇🗑) | Lucide icons for consistency across all projects |
| Hardcoded colors in `index.html` | CSS variable references |
| Hardcoded colors in `files-epic002.ts` inline styles | CSS variable references |
| Inter + JetBrains Mono already | No change (already matches target) |
| Primary `#3b82f6` (blue) | Minimal change — already matches primary-500 |
| Secondary `#06b6d4` (cyan) | No change — already matches secondary-500 |

---

## 16. Validation Criteria

The implementation is considered complete when:

1. All pages in all projects render correctly in **Dark**, **Light**, and **System** modes
2. Theme toggle button is visible and functional in the top-right of every page
3. Font size button is visible, functional, and cycles through Normal → +2px → +4px → Normal
4. Both user preferences (theme + font size) persist across page reloads via localStorage
5. All colors, typography, spacing, shadows, and radii match the design tokens exactly
6. All components (buttons, cards, inputs, tables, badges, alerts, etc.) match the style guide specifications
7. WCAG 2.2 AA color contrast is met for both themes
8. Keyboard navigation works across all interactive elements
9. Responsive layout adapts correctly at all breakpoints
10. No hardcoded color values remain — all visual values reference CSS custom properties
