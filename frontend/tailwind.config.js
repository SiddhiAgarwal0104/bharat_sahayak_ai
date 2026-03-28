/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",   // scans ALL src files for class names
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#1B4F9B",
          light:   "#2563C4",
          dark:    "#163D7A",
        },
        accent:  { DEFAULT: "#F47B20", light: "#F9A05A" },
        success: { DEFAULT: "#138808", light: "#E8F5E9" },
        danger:  { DEFAULT: "#E53935", light: "#FFEBEE" },
        neutral: {
          50:  "#F5F7FA",
          100: "#E8ECF0",
          200: "#D1D9E0",
          700: "#4A5568",
          900: "#1A1A2E",
        },
      },
      fontFamily: {
        sans: ["Noto Sans", "system-ui", "sans-serif"],
      },
      minHeight: {
        touch: "48px",
      },
      borderRadius: {
        xl:  "12px",
        "2xl": "16px",
      },
    },
  },
  plugins: [],
}