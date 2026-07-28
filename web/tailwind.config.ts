import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        void: "var(--sh-void)",
        ink: "var(--sh-ink)",
        panel: "var(--sh-panel)",
        line: "var(--sh-line)",
        fog: "var(--sh-fog)",
        mute: "var(--sh-mute)",
        signal: "var(--sh-signal)",
        valid: "var(--sh-valid)",
        warn: "var(--sh-warn)",
        fault: "var(--sh-fault)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
        display: ["var(--font-display)", "var(--font-sans)", "sans-serif"],
      },
      boxShadow: {
        signal: "0 0 0 1px var(--sh-line), 0 12px 40px rgba(0,0,0,.35)",
        glow: "0 0 24px color-mix(in oklab, var(--sh-signal) 35%, transparent)",
      },
      backgroundImage: {
        grid: "linear-gradient(to right, color-mix(in oklab, var(--sh-line) 55%, transparent) 1px, transparent 1px), linear-gradient(to bottom, color-mix(in oklab, var(--sh-line) 55%, transparent) 1px, transparent 1px)",
        aurora:
          "radial-gradient(1200px 500px at 10% -10%, color-mix(in oklab, var(--sh-signal) 22%, transparent), transparent 60%), radial-gradient(900px 400px at 90% 0%, color-mix(in oklab, var(--sh-valid) 12%, transparent), transparent 55%)",
      },
      backgroundSize: {
        grid: "48px 48px",
      },
      keyframes: {
        packet: {
          "0%": { transform: "translateX(0%)", opacity: "0" },
          "8%": { opacity: "1" },
          "92%": { opacity: "1" },
          "100%": { transform: "translateX(100%)", opacity: "0" },
        },
      },
      animation: {
        packet: "packet 7s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
