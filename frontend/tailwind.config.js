/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "soc-red": "#ef4444",
        "soc-orange": "#f97316",
        "soc-yellow": "#eab308",
        "soc-green": "#22c55e",
      },
    },
  },
  plugins: [],
};
