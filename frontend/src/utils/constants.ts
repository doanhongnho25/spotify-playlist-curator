export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export const APP_TITLE =
  import.meta.env.VITE_APP_TITLE ?? "Vibe Engine Dashboard";

export const DEFAULT_DESCRIPTIONS = [
  "A curated blend of sounds from our archive.",
  "Fresh picks from our vault, handpicked for today.",
  "For late nights and clear minds.",
  "A smooth mix made for golden hours.",
  "Atmospheric cuts for focused flow."
];

export const STATUS_BADGES = {
  healthy: {
    label: "Stable",
    icon: "🟢"
  },
  syncing: {
    label: "Syncing",
    icon: "🔄"
  },
  warning: {
    label: "Rate-Limited",
    icon: "⚠️"
  }
} as const;
