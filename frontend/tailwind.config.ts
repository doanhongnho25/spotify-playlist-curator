import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#121212",
        foreground: "#EDEDED",
        accent: {
          DEFAULT: "#6A5AE0",
          soft: "#A85CF9"
        }
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"]
      },
      borderRadius: {
        xl: "12px"
      },
      boxShadow: {
        glow: "0 0 25px rgba(168, 92, 249, 0.25)"
      }
    }
  },
  plugins: []
};

export default config;
