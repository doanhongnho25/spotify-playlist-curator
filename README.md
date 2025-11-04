# Vibe Engine

Vibe Engine orchestrates Spotify playlist curation across multiple managed accounts. The stack pairs a Vite + React dashboard with a FastAPI backend backed by PostgreSQL and Redis. Operators authenticate with a development login, onboard Spotify accounts via OAuth, ingest album sources, and create or reshuffle public playlists that pull 50 tracks at a time from the library.

## Architecture Overview

```
┌────────────┐     ┌────────────┐     ┌────────────┐
│  Frontend  │◄──►│    API     │◄──►│  PostgreSQL │
│  (React)   │     │ (FastAPI)  │     │   Redis    │
└────────────┘     └────┬───────┘     └────┬───────┘
                         │                │
                         │                └─ background workers (Celery ready)
                         │
                         ├─ Spotify OAuth + dev login session cookies
                         ├─ Album ingest + audio feature enrichment
                         └─ Playlist creation, reshuffle, metrics, and settings
```

### Frontend
- Vite + React 18 with Tailwind, shadcn/ui, React Query, and Recharts.
- Development login (`admin` / `admin`) sets an HTTP-only `dashboard_session` cookie.
- Navigation covers Dashboard, Accounts, Playlists, Library, Settings, Automation, and optional Assistant pages.
- Account switcher stores the active Spotify account per browser session.

### Backend
- FastAPI v1 namespace with modules for auth, Spotify OAuth, accounts, playlists, library ingest, settings, metrics, and job control.
- SQLAlchemy ORM models capture Spotify accounts, albums, tracks, playlists, playlist history, runtime settings, and metric snapshots.
- Sampler service enforces a 5-day cooldown, per-artist cap, and 50-track snapshots for each playlist.
- Spotify integration (httpx) handles OAuth, playlist CRUD, album lookups, audio features, and token refresh.
- Session management signs cookies via `itsdangerous` and keeps active account pointers in memory.

### Datastores & Jobs
- **PostgreSQL** stores accounts, music library, playlists, history, settings, and metric snapshots.
- **Redis** is reserved for Celery broker/rate limiting (workers scheduled via docker-compose).
- Job scheduler facade exposes enable/disable/run metadata for reshuffle, refresh, and metrics jobs.

## Getting Started

1. Copy the example environment file and edit credentials:

```bash
cp .env.example .env
```

Key variables:

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Signing key for dashboard sessions |
| `DASHBOARD_USERNAME`, `DASHBOARD_PASSWORD` | Development login credentials |
| `DATABASE_URL`, `REDIS_URL` | Postgres and Redis connection strings |
| `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REDIRECT_URI` | Spotify application settings |
| `TRACKS_PER_PLAYLIST`, `RESHUFFLE_INTERVAL_DAYS`, `MIN_REPEAT_GAP_DAYS`, `MAX_PLAYLISTS_PER_ACCOUNT`, `ARTIST_CAP`, `DEFAULT_PREFIX` | Playlist tuning knobs |
| `ALLOWED_ORIGINS`, `PUBLIC_BASE_URL` | Frontend base URLs (use `http://127.0.0.1`) |

2. Start the stack with Docker Compose:

```bash
make up
```

Services default to:
- API – http://127.0.0.1:8000
- Dashboard – http://127.0.0.1:3000
- PostgreSQL – port 5432
- Redis – port 6379

Run migrations and optional seed routines:

```bash
make migrate
make seed
```

Stop services:

```bash
make down
```

## Core Flows

1. **Login** – visit http://127.0.0.1:3000 and sign in with the dev credentials.
2. **Connect Spotify Accounts** – start the OAuth handshake; access/refresh tokens are persisted per account. Prefixes can be edited inline and sessions track an “active” account for manual workflows.
3. **Ingest Albums** – paste Spotify album URLs; the backend fetches tracks, stores album + track metadata, and enriches audio features.
4. **Create Playlists** – request dozens of playlists per account; naming follows `<prefix> • <index>` and descriptions rotate between natural templates. Capacity limits guard `MAX_PLAYLISTS_PER_ACCOUNT`.
5. **Reshuffle** – replace playlist contents while respecting cooldown/artist caps. Bulk reshuffle supports all, per account, or selected subsets.
6. **Settings & Metrics** – adjust playlist size/interval/cooldown and observe system counts & health via `/api/v1/metrics` endpoints.
7. **Jobs** – toggle scheduler jobs (reshuffle, refresh tokens, metrics snapshot) with `/api/v1/jobs` for local testing.

## Documentation

- [Architecture](documentation/ARCHITECTURE.md)
- [API Reference](documentation/API.md)
- [Deployment Guide](documentation/DEPLOYMENT.md)
- [Database Overview](documentation/DATABASE.md)
- [Workers](documentation/WORKERS.md)
- [Naming Guide](documentation/NAMING.md)

These guides cover the ingest-to-playlist pipeline, schema reference, deployment steps for local/VPS environments, worker cadence, and playlist naming/description conventions.
