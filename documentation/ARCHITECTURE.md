# Project Vibe – Architecture

## Overview

Project Vibe now follows a three-tier model consisting of a FastAPI gateway, a Celery-based worker plane, and dedicated datastores (PostgreSQL + Redis). The system ingests large batches of album sources, enriches tracks, applies rule-driven curation, and synchronizes 50-track playlists across multiple Spotify accounts while still exposing the original Gemini-powered vibe generator for end users.

## Logical Components

### API Layer (FastAPI)
* Hosts admin, ingest, manager, playlist, and public endpoints under `/api/v1`.
* Manages Spotify service-account onboarding via an OAuth callback that encrypts access/refresh tokens with a Fernet key.
* Exposes orchestration endpoints used by workers (e.g., playlist sync triggers, ingest submissions).
* Maintains the end-user `POST /api/v1/playlist/generate` Gemini integration.

### Worker Layer (Celery)
* `workers.tasks` registers jobs such as `ingest_albums_from_sources`, `build_playlist_snapshot`, `ensure_playlist_for_account`, and `scale_playlists_daily`.
* Celery beat is configured with the required UTC cadence:
  * 02:00 – scaling planner (`scale_playlists_daily`).
  * 02:30 and every 30 minutes – `refresh_tokens`.
  * 03:00/03:30/04:00/04:10 windows for ingest → enrich → curate → sync.
* Workers communicate with Redis queues and reuse the shared SQLAlchemy models for persistence.

### Datastore Layer
* **PostgreSQL 16** – authoritative store for accounts, album sources, albums, tracks, playlist mappings, historical entries, and manager plans. Alembic migrations define schema, indexes, and the `recent_usage` view for avoiding repeat tracks.
* **Redis 7** – Celery broker/backend and placeholder for rate limiting / circuit-breaking primitives.

## Data Model

Alembic migration `0001_initial` provisions the following tables:

| Table | Purpose |
|-------|---------|
| `accounts` | Spotify service accounts with encrypted tokens and status.
| `album_sources` | Queue of album URLs with ingest status and failure reason.
| `albums` / `tracks` | Normalized catalog data sourced from Spotify.
| `album_track_map` | Relationship between ingest sources and tracks.
| `curation_policies` | Rule definitions (JSON payloads) powering playlist templates.
| `playlists` | Logical playlists (name, policy, theme tag, replication factor).
| `playlist_account_map` | Physical playlist instances per Spotify account, including external URLs and sync status.
| `playlist_entries_history` | Daily 50-track snapshots with `batch_tag` for rotation history.
| `manager_plans` | Audit trail capturing scaling stats and actions.

Indices exist on track artist/popularity and playlist history `(playlist_id, added_at DESC)`. View `recent_usage` surfaces last usage timestamps by Spotify track ID.

## Data Flows

1. **Album Intake**
   * Admin submits a batch of URLs → entries land in `album_sources` with status `queued`.
   * Worker `ingest_albums_from_sources` fetches metadata, creates `albums` and `tracks`, and maps them back to the sources.
   * `fetch_audio_features` enriches tracks with energy/danceability metrics.

2. **Curation & Rotation**
   * `build_playlist_snapshot` filters tracks based on policy JSON, avoids repeats leveraging `recent_usage`, and respects balancing limits (per-artist/per-album).
   * Output snapshot is written to `playlist_entries_history` with a `batch_tag` (typically `YYYY-MM-DD`).

3. **Synchronization**
   * `ensure_playlist_for_account` provisions or replaces playlists on Spotify, enforcing the naming convention `Vibe • {ThemeTag} • #{GlobalIndex:000} • {YYYY-MM-DD}` and public descriptions.
   * `playlist_account_map` records Spotify playlist IDs, external URLs, statuses, and errors.
   * Public endpoints aggregate these mappings so consumers can browse playlists per account.

4. **Scaling Manager**
   * `scale_playlists_daily` calculates `P* = ceil(T / (K * R))` where `T` is usable track count, `K` is 50 tracks per playlist, and `R` is the minimum repeat gap (days).
   * Capacity checks respect active accounts × `max_playlists_per_account` and `floor_total_playlists` guardrails.
   * Manager plans (stats, actions) persist to `manager_plans` for auditability; rebalancing uses consistent hashing guidance when accounts change.

## Scheduling & Rate Limits

* Retries for 429/5xx responses should implement exponential backoff with jitter (six attempts max) and a 10-minute circuit breaker.
* Per-account throttling (token bucket) is delegated to Redis-backed helpers (to be implemented in worker services).
* Flower (http://127.0.0.1:5555) provides observability into task queues.

## Security

* Spotify tokens encrypted via Fernet key `SPOTIFY_TOKEN_KEY`.
* Admin routes guard with `X-ADMIN-API-KEY` header.
* CORS configured from `ALLOWED_ORIGINS`.
* All user-facing cookies remain HTTP-only; admin flows rely solely on headers.

## Frontend Touchpoints

The React frontend now consumes both admin and public APIs:
* Admin dashboards call accounts, ingest, playlists, and manager endpoints.
* End users still interact with the vibe generator and single album submission endpoint.

This architecture enables high-volume ingest (10k+ albums), daily playlist rotations, and automated scaling across multiple Spotify accounts while keeping the original MVP experience intact.
