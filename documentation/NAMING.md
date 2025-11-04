# Naming & Copy Guidelines

## Playlist Titles
- Format: `{Prefix} • {Index:000}`
  - Prefix order: operator-defined account prefix → fallback `DEFAULT_PREFIX`.
  - Index is sequential per account (zero-padded to three digits).
- Prohibited words: `random`, `rotation`, `auto`, `autoplaylist`, hashtags referencing automation.
- Keep tone human and curation-focused (e.g., `Vibe Collection • 021`, `Midnight Flow • 044`).

## Playlist Descriptions
- Rotate through curated copy, e.g.:
  - “A curated blend of sounds from our archive.”
  - “Fresh picks from our vault, handpicked for today.”
  - “For late nights and clear minds.”
- Avoid technical jargon. Mention policy/size only when useful (e.g., `Curated by Vibe Engine — 50 tracks refreshed weekly.`).

## Accounts
- Prefix defaults to “Vibe Collection” but operators can edit per account (`/api/v1/accounts/prefix`).
- Maintain meaningful Spotify display names; avoid duplicate prefixes when juggling many accounts.

## Albums & Tracks
- Store album URLs exactly as submitted (Spotify canonical form) for traceability.
- Artist names follow Spotify-provided formatting (no additional casing adjustments).

## Tasks & Jobs
- Celery task names mirror worker functions (`ingest_albums_from_sources`, `ensure_playlist_for_account`).
- Job scheduler entries appear verbatim in the Automation tab; use descriptive, lowercase-with-underscores labels.
