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
        },
        ink: {
          DEFAULT: "#1E293B",
        },
      },
      fontFamily: {
        sans: ["Inter", "IBM Plex Sans", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
