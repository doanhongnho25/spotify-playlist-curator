# Vibe Control Center

Vibe Control Center orchestrates Spotify playlist curation across multiple managed accounts. The stack is split into a React dashboard, a FastAPI gateway, and a Celery worker tier backed by PostgreSQL and Redis. Operators authenticate with a development login, onboard Spotify accounts via OAuth, ingest album sources, define curation policies, and coordinate daily playlist rotation at scale.

## Architecture at a Glance

```
┌────────────┐     ┌────────────┐     ┌────────────┐
│  Frontend  │◄──►│    API     │◄──►│  PostgreSQL │
│  (React)   │     │ (FastAPI)  │     │   Redis    │
└────────────┘     └────┬───────┘     └────┬───────┘
                         │                │
                         │                └─ Celery workers + beat
                         │
                         ├─ OAuth for Spotify service accounts
                         ├─ Album ingest + enrichment orchestration
                         └─ Playlist curation, sync, scaling, and public listing
```

### Frontend (React)
- Development login (`admin` / `admin`) sets an HTTP-only `dashboard_session` cookie.
- Unified dashboard with tabs for Accounts, Albums, Policies & Playlists, Manager, and Metrics.
- Account switcher persists the active Spotify account per session for manual sync flows.

### API (FastAPI)
- Exposes `/api/v1/auth/dev-login` for dashboard authentication (no admin API key).
- Handles Spotify OAuth (`/api/v1/oauth/spotify/connect|callback`) and account management endpoints.
- Provides ingest, policy, playlist, manager, and public listing APIs.
- Persists encrypted Spotify tokens, album metadata, curation policies, playlist mappings, and rotation history.

### Workers (Celery)
- Queue album ingestion, audio feature enrichment, playlist snapshot builds, multi-account sync, scaling, rebalance, and token refresh jobs.
- Scheduler mirrors the daily cadence: scale at 02:00 UTC, refresh tokens every 30 minutes, ingest/enrich/curate/sync waves through the morning.

### Datastores
- **PostgreSQL 16**: accounts, albums, tracks, policies, playlist history, manager plans, and automation audit trails.
- **Redis 7**: Celery broker, rate limiting, throttling, and token bucket counters.

## Environment

Copy `.env.example` to `.env` and update secrets:

```bash
cp .env.example .env
```

| Variable | Purpose |
|----------|---------|
| `DASHBOARD_USERNAME`, `DASHBOARD_PASSWORD` | Development dashboard credentials |
| `DATABASE_URL`, `REDIS_URL` | Database and cache connection strings |
| `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` | Spotify application credentials |
| `SPOTIFY_TOKEN_KEY` | Base64-encoded Fernet key for token encryption |
| `ALLOWED_ORIGINS`, `PUBLIC_BASE_URL` | Frontend origins and callback base URL (use `http://127.0.0.1`) |
| `TRACKS_PER_PLAYLIST`, `MIN_REPEAT_GAP_DAYS`, `MAX_PLAYLISTS_PER_ACCOUNT`, `FLOOR_TOTAL_PLAYLISTS`, `REBALANCE_MOVE_LIMIT_PER_ACCOUNT` | Playlist manager knobs |
| `REACT_APP_API_BASE` | Frontend API root (defaults to `http://127.0.0.1:8000`) |

Generate a Fernet key when provisioning a new environment:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Local Development

Spin up the stack with Docker Compose:

```bash
make up
```

Services are available at:
- API – http://127.0.0.1:8000
- Dashboard – http://127.0.0.1:3000
- Flower – http://127.0.0.1:5555
- PostgreSQL – port 5432
- Redis – port 6379

Apply migrations and optional seed data:

```bash
make migrate
make seed
```

Stop services and remove containers:

```bash
make down
```

## Core Flows

1. **Dashboard Login** – Visit http://127.0.0.1:3000, sign in with `admin` / `admin` (configurable via `.env`).
2. **Connect Spotify Accounts** – Launch OAuth from the Accounts tab; tokens are encrypted and stored in PostgreSQL. The active account can be switched per session.
3. **Ingest Albums** – Paste album URLs for validation and submission. Workers ingest sources, enrich audio features, and populate albums/tracks tables.
4. **Define Policies & Templates** – Store JSON rules (filters, balancing, diversity) and attach them to logical playlists.
5. **Daily Automation** – Workers generate 50-track snapshots per playlist, enforce avoid-repeat windows, and sync playlists across allocated accounts.
6. **Scaling & Rebalance** – Compute target playlist counts (`P* = ceil(T / (TRACKS_PER_PLAYLIST * MIN_REPEAT_GAP_DAYS))`), create/retire playlists, and rebalance via consistent hashing with move limits per account.
7. **Public Listing** – `/api/v1/public/playlists` exposes curated playlist names, account links, and last sync timestamps.

## Documentation
- [Architecture](documentation/ARCHITECTURE.md)
- [API Reference](documentation/API.md)
- [Playbook](documentation/PLAYBOOK.md)
- [Naming Conventions](documentation/NAMING.md)

These documents outline the ingest-to-sync pipeline, multi-account distribution, scheduling matrix, and naming/description standards for Spotify playlists.
