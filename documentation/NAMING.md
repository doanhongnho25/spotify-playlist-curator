# Naming Conventions

## Playlists
* Format: `Vibe • {ThemeTag} • #{GlobalIndex:000} • {YYYY-MM-DD}`.
* `ThemeTag` derives from `playlists.theme_tag` (fallback `Mixed`).
* `GlobalIndex` increments system-wide across logical playlists.
* Description template: `Curated by Vibe Bot — daily rotation (50 tracks). Policy: {policy_name}. Updated: {YYYY-MM-DD}. #vibe #autoplaylist`.

## Policies & Plans
* Policy names should be short and descriptive (e.g., `High Energy Mix`).
* Manager plan identifiers are stored as UUID primary keys; reference them when logging operational actions.

## Accounts
* Spotify account display names should follow `Vibe Publisher {Ordinal}` when onboarding multiple accounts.
* Status values: `active`, `inactive`, `degraded`, `quarantined`.

## Album Sources
* URLs normalized by trimming whitespace and converting to HTTPS when possible.
* Owner tags use `team/initiative` slash notation (`editorial/core`, `community/promo`).

## Tasks
* Celery task names map to spec-provided verbs (`ingest_albums_from_sources`, `scale_playlists_daily`, etc.) for observability.
