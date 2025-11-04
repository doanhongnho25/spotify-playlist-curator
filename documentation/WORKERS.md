# Workers & Scheduling

The workers package (`backend/app/workers/`) is prepared for Celery + Redis. Core jobs:

## Ingest Pipeline
- **`ingest_albums_from_sources`** – Fetch queued album URLs, call Spotify APIs to retrieve tracks, persist albums/tracks, and enqueue audio feature lookups.
- **`fetch_audio_features`** – Batch audio feature requests (≤100 IDs per call) and update `tracks.audio_features`.

## Playlist Operations
- **`build_playlist_snapshot`** – Use the sampler service to produce the 50-track selection for a playlist or policy, respecting cooldown/artist caps.
- **`ensure_playlist_for_account`** – Create or update a Spotify playlist, apply naming/description templates, and log history entries.
- **`reshuffle_due_playlists`** – Daily job that locates playlists where `next_reshuffle_at <= now()` and triggers `ensure_playlist_for_account`.

## Account Maintenance
- **`refresh_tokens`** – Refresh Spotify access tokens for accounts expiring within five minutes.
- **`scale_playlists_daily`** – Placeholder for capacity planning logic (compute target playlist counts, create/retire playlists, and rebalance across accounts).

## Metrics & Observability
- **`metrics_snapshot`** – Capture counts (accounts, playlists, tracks, reshuffles) into `metric_snapshots` for dashboard trends.
- **`job_history` logging** – Store recent job runs with status/duration for the Automation tab.

## Scheduler Cadence (UTC)

| Time | Job |
|------|-----|
| 02:00 | `scale_playlists_daily` |
| 02:30 (every 30 min) | `refresh_tokens` |
| 03:00 | `ingest_albums_from_sources` |
| 03:30 | `fetch_audio_features` |
| 04:00 | `build_playlist_snapshot` (all playlists) |
| 04:10 | `ensure_playlist_for_account` (sync all) |
| hourly | `metrics_snapshot` |

The Automation tab reads scheduler status via `/api/v1/jobs/list` and lets operators toggle jobs with `/api/v1/jobs/update` for debugging.

## Rate Limiting & Reliability

- Retry Spotify `429`/`5xx` responses with exponential backoff (≤6 attempts) and jitter.
- Apply per-account throttling (token bucket in Redis) to avoid exceeding Spotify quotas.
- Track account health (OK, degraded, quarantined) for prioritised sync waves.
- Record playlist and account actions in structured logs for observability.
