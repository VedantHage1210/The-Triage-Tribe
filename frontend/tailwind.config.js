/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Section 16 — Visual Design Theme color system
        clinical: {
          teal: "#0F766E",
          blue: "#1D4ED8",
        },
        severity: {
          emergency: "#DC2626",
          urgent: "#EA580C",
          routine: "#CA8A04",
          selfcare: "#16A34A",
        },
        bg: {
          soft: "#F8FAFC",
          // Cool, clinical off-white — deliberately not the warm-cream
          // (#F4F1EA-ish) default. Used for the result-card surface.
          paper: "#F4F7F6",
        },
        ink: {
          DEFAULT: "#1E293B",
          // Near-black used for the result card's structural chrome —
          // warmer/darker than slate-900 so it doesn't read as a stock
          // Tailwind default.
          deep: "#12201F",
        },
      },
      fontFamily: {
        sans: ["Inter", "IBM Plex Sans", "system-ui", "sans-serif"],
        // Reserved for data figures only (confidence %, session refs) —
        // a vitals-readout cue, not a decorative label font.
        mono: ["IBM Plex Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
    },
  },
  plugins: [],
};
