/**
 * Files Manager Design Tokens - AgentFlow v2.0
 *
 * Replaces legacy --files-* CSS custom properties with standard AgentFlow tokens.
 * This module exports the CSS string for FM token integration.
 *
 * Token mapping:
 *   --files-bg-primary   -> --bg-primary
 *   --files-bg-secondary -> --bg-secondary
 *   --files-bg-tertiary  -> --bg-tertiary
 *   --files-text-*       -> --text-*
 *   --files-border       -> --border-*
 */

export function getFilesManagerTokensCSS(): string {
  return `
/* AgentFlow Design Tokens for Files Manager */
/* Replaces legacy --files-* namespace with standard tokens */

:root {
  /* Base/shared tokens */
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;
  --color-secondary-500: #06b6d4;
  --color-secondary-600: #0891b2;
  --color-error: #ef4444;
  --color-error-dark: #b91c1c;
  --color-success: #22c55e;
  --color-warning: #eab308;

  /* Spacing (4px base grid) */
  --space-0: 0;
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;

  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-2xl: 1rem;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-xs: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1);

  /* Typography */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;

  /* Transitions */
  --duration-fast: 100ms;
  --duration-normal: 200ms;
  --duration-slow: 300ms;
  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);
}

/* Dark Theme (default for Files Manager) */
[data-theme="dark"] {
  --bg-primary: #020617;
  --bg-secondary: #0f172a;
  --bg-tertiary: #1e293b;
  --bg-elevated: #1e293b;
  --bg-hover: rgba(148,163,184,0.08);
  --bg-active: rgba(148,163,184,0.12);
  --bg-input: #0f172a;
  --bg-card: rgba(30,41,59,0.5);

  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-tertiary: #64748b;
  --text-inverse: #020617;
  --text-link: #60a5fa;

  --border-primary: #334155;
  --border-secondary: #1e293b;
  --border-focus: #3b82f6;

  --shadow-card: 0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2);

  color-scheme: dark;
}

/* Light Theme */
[data-theme="light"] {
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
  --bg-elevated: #ffffff;
  --bg-hover: rgba(15,23,42,0.04);
  --bg-active: rgba(15,23,42,0.08);
  --bg-input: #ffffff;
  --bg-card: #ffffff;

  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-tertiary: #64748b;
  --text-inverse: #ffffff;
  --text-link: #2563eb;

  --border-primary: #e2e8f0;
  --border-secondary: #f1f5f9;
  --border-focus: #3b82f6;

  --shadow-card: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);

  color-scheme: light;
}
`;
}
