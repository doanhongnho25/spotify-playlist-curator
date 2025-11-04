# Architecture

Vibe Engine splits the playlist automation platform into three cooperative layers:

1. **Frontend (Vite + React)** – The “Vibe Engine Dashboard” that exposes login, account onboarding, playlist management, library exploration, automation controls, and observability widgets.
2. **API (FastAPI)** – Handles development authentication, Spotify OAuth, account lifecycle, album ingest, playlist creation/reshuffle, settings, metrics, and scheduler management. SQLAlchemy models persist state in PostgreSQL.
3. **Workers (Celery-ready)** – Background tasks for ingest, audio feature enrichment, cooldown-aware sampling, playlist sync, token refresh, and metrics snapshots. Redis serves as the message broker / rate-limiter foundation.

## Component Diagram

```
        ┌─────────────────────┐
        │  Vite React UI      │
        │  - React Query      │
        │  - Tailwind + shadcn│
        └─────────┬──────────┘
                  │ HTTP (cookie auth)
                  ▼
        ┌─────────────────────┐
        │ FastAPI Gateway     │
        │  /api/v1            │
        │   ├ auth/dev-login  │
        │   ├ oauth/spotify   │
        │   ├ accounts        │
        │   ├ library         │
        │   ├ playlists       │
        │   ├ settings        │
        │   ├ metrics         │
        │   └ jobs            │
        └──────┬───────┬──────┘
               │       │
        SQLAlchemy   Celery tasks
        │            │
        ▼            ▼
┌─────────────┐  ┌────────────┐
│ PostgreSQL  │  │ Redis      │
│ - accounts  │  │ - broker   │
│ - albums    │  │ - rate cap │
│ - tracks    │  └────────────┘
│ - playlists │
│ - history   │
│ - settings  │
│ - metrics   │
└─────────────┘
```

## Data Model Summary

| Table | Purpose |
|-------|---------|
| `spotify_accounts` | OAuth’d Spotify service accounts (tokens, prefix, expiry, status, playlist count) |
| `albums` | Seeded Spotify albums derived from submitted URLs |
| `tracks` | Tracks linked to albums, with popularity and cached audio features |
| `playlists` | Logical playlists assigned to accounts with size, next reshuffle, and Spotify IDs |
| `playlist_entries_history` | Append-only log of track snapshots per playlist (batch tag = date) |
| `settings` | Key/value runtime configuration overrides |
| `metric_snapshots` | Aggregated daily metrics captured by workers |

Indexes ensure quick artist/popularity filtering and descending history queries. Alembic migrations live in `backend/alembic/`.

## Request Flow

1. Operator logs in via `/api/v1/auth/dev-login`; FastAPI mints a signed `dashboard_session` cookie.
2. Accounts tab initiates `/api/v1/accounts/connect` → Spotify OAuth. Callback upserts into `spotify_accounts` and marks the session’s active account.
3. Library tab submits album URLs to `/api/v1/library/ingest`. The backend pulls album/track metadata and audio features, deduplicating on Spotify IDs.
4. Playlists tab calls `/api/v1/playlists/create`, leveraging the sampler to select 50 tracks (respecting cooldown + artist cap) before creating the playlist on Spotify and persisting history.
5. Reshuffle requests (manual or scheduled) hit `/api/v1/playlists/{id}/reshuffle` or `/api/v1/playlists/reshuffle-bulk`, replacing tracks and logging new history entries.
6. Settings endpoints expose runtime configuration stored in the `settings` table, while `/api/v1/metrics/*` returns system counts and trend history for dashboard visualizations.
7. `/api/v1/jobs/*` reflects scheduler state – a lightweight facade for Celery beat configuration during development.

## Background Jobs

Workers (defined in `backend/app/workers/`) orchestrate:

- Album ingest batches, including audio feature lookups.
- Cooldown-aware sampling with the sampler service.
- Playlist snapshot syncs to Spotify (create/update + description refresh).
- Token refresh waves (refresh tokens 5 minutes prior to expiry).
- Metrics snapshot captures (daily/hourly aggregates).

Docker Compose provisions worker and beat containers; production deployments can attach additional consumers as needed.

## Session & Security

- Dashboard sessions rely on a signed cookie (`SECRET_KEY`).
- All operator endpoints require a valid `dashboard_session` cookie; OAuth callback also checks stored state tokens.
- Spotify tokens are stored as-is for brevity; integrate envelope encryption (e.g., KMS) when hardening for production.

## Scaling Considerations

- `MAX_PLAYLISTS_PER_ACCOUNT` protects service accounts from exceeding Spotify limits.
- Reshuffle cadence is configurable via settings/environment variables.
- Redis is ready to host rate limiter buckets and Celery queues; horizontal worker scaling is supported by design.
- Metric snapshots power observability dashboards; extend with Prometheus exporters for deeper insights.
