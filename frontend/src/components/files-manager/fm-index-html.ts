/**
 * Files Manager index.html template - Hardcoded color fix
 *
 * T-097: Replaces hardcoded hex colors (#4a9eff loading spinner, #ff4444 error)
 * with CSS custom property references.
 */

export function getFilesManagerIndexHTML(): string {
  return `<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Files Manager</title>
  <script>
    // Synchronous theme detection before first paint
    (function() {
      var saved = localStorage.getItem('theme-preference');
      if (saved === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
      } else if (saved === 'system') {
        var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
      } else {
        document.documentElement.setAttribute('data-theme', 'dark');
      }
    })();
  </script>
  <style>
    /* Loading spinner uses CSS custom properties */
    .loading-spinner {
      border: 3px solid var(--border-primary, #334155);
      border-top: 3px solid var(--color-primary-500, #3b82f6);
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    /* Error banner uses CSS custom properties */
    .error-banner {
      background: rgba(239, 68, 68, 0.15);
      color: var(--color-error, #ef4444);
      border: 1px solid var(--color-error, #ef4444);
      border-radius: var(--radius-md, 6px);
      padding: var(--space-3, 12px) var(--space-4, 16px);
      font-family: var(--font-sans, 'Inter', sans-serif);
    }

    body {
      margin: 0;
      background: var(--bg-primary);
      color: var(--text-primary);
      font-family: var(--font-sans);
      transition: background var(--duration-slow) var(--ease-default),
                  color var(--duration-slow) var(--ease-default);
    }
  </style>
</head>
<body>
  <div id="app">
    <div class="loading-spinner"></div>
  </div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>`;
}
