import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          50: "#f4f6f8",
          100: "#e4e9ef",
          200: "#c5d0db",
          300: "#9aabbc",
          400: "#6b8299",
          500: "#4f667d",
          600: "#3d5165",
          700: "#334353",
          800: "#2c3947",
          900: "#1a222c",
          950: "#0d1218",
        },
        accent: {
          DEFAULT: "#7c5cfc",
          soft: "#a78bfa",
          dim: "#5b3fd4",
        },
        pass: "#22c55e",
        fail: "#ef4444",
      },
      fontFamily: {
        sans: ["var(--font-geist)", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
