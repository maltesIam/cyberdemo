/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        /* Legacy SOC colors (preserved for backward compatibility) */
        "soc-red": "#ef4444",
        "soc-orange": "#f97316",
        "soc-yellow": "#eab308",
        "soc-green": "#22c55e",

        /* Medicum clinical colors */
        medical: {
          primary: "#0066CC",
          secondary: "#4A90D9",
          success: "#28A745",
          warning: "#FFC107",
          danger: "#DC3545",
          info: "#17A2B8",
          light: "#F8F9FA",
          dark: "#343A40",
        },
        severity: {
          high: "#DC3545",
          medium: "#FD7E14",
          low: "#FFC107",
        },

        /* AgentFlow Design Token References */
        primary: {
          DEFAULT: "var(--primary)",
          hover: "var(--primary-hover)",
          500: "var(--primary-500)",
          600: "var(--primary-600)",
          700: "var(--primary-700)",
        },
        accent: "var(--accent)",

        /* Semantic Colors */
        success: "var(--color-success)",
        warning: "var(--color-warning)",
        error: "var(--color-error)",
        info: "var(--color-info)",
      },
      backgroundColor: {
        primary: "var(--bg-primary)",
        secondary: "var(--bg-secondary)",
        tertiary: "var(--bg-tertiary)",
        card: "var(--bg-card)",
        elevated: "var(--bg-elevated)",
        hover: "var(--bg-hover)",
        input: "var(--bg-input)",
      },
      textColor: {
        primary: "var(--text-primary)",
        secondary: "var(--text-secondary)",
        tertiary: "var(--text-tertiary)",
        inverse: "var(--text-inverse)",
        link: "var(--text-link)",
      },
      borderColor: {
        primary: "var(--border-primary)",
        secondary: "var(--border-secondary)",
        focus: "var(--border-focus)",
      },
      fontFamily: {
        sans: ["'Inter'", "ui-sans-serif", "system-ui", "-apple-system", "sans-serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "'Cascadia Code'", "'Fira Code'", "monospace"],
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
        xl: "var(--radius-xl)",
        "2xl": "var(--radius-2xl)",
        full: "var(--radius-full)",
      },
      spacing: {
        "space-1": "var(--spacing-1)",
        "space-2": "var(--spacing-2)",
        "space-3": "var(--spacing-3)",
        "space-4": "var(--spacing-4)",
        "space-6": "var(--spacing-6)",
        "space-8": "var(--spacing-8)",
      },
      boxShadow: {
        sm: "var(--shadow-sm)",
        md: "var(--shadow-md)",
        lg: "var(--shadow-lg)",
        xl: "var(--shadow-xl)",
      },
      transitionDuration: {
        fast: "var(--transition-fast)",
        DEFAULT: "var(--transition-default)",
        slow: "var(--transition-slow)",
      },
    },
  },
  plugins: [],
};
