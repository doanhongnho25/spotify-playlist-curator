# Project Vibe

Project Vibe is a multi-account Spotify playlist curator that combines FastAPI, Celery workers, and PostgreSQL to ingest albums, enrich metadata, rotate 50-track playlists, and publish them across managed Spotify accounts. A lightweight React frontend provides both admin tooling and the original end-user "generate 10 songs" experience powered by Google Gemini.

## Service Topology

```
┌────────────┐     ┌────────────┐     ┌────────────┐
│  Frontend  │◄──►│    API     │◄──►│  PostgreSQL │
│  (React)   │     │ (FastAPI)  │     │   Redis    │
└────────────┘     └────┬───────┘     └────┬───────┘
                         │                │
                         │                └─ Celery beat / worker queues
                         │
                         ├─ Admin + public REST endpoints
                         └─ Gemini + Spotify orchestration
```

### API (FastAPI)
* Acts as gateway for admin, ingest, curation, and public listing endpoints.
* Stores OAuth-managed Spotify accounts with encrypted tokens.
* Exposes the legacy `/api/v1/playlist/generate` endpoint for 10-song end-user playlists.

### Workers (Celery)
* Task skeletons cover ingest, enrichment, playlist curation, synchronization, scaling, and token refresh flows.
* Beat scheduler mirrors the required UTC cadence (scale at 02:00, refresh tokens every 30 minutes, etc.).

### Datastores
* **PostgreSQL 16** for relational data (albums, tracks, playlists, history, manager plans).
* **Redis 7** for queues, rate limiting, and scheduling primitives.

## Getting Started

### 1. Environment
Copy `.env.example` to `.env` and populate the credentials:

```
cp .env.example .env
```

Key variables:
* `DATABASE_URL`, `REDIS_URL`
* `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_TOKEN_KEY`
* `GEMINI_API_KEY`, `ADMIN_API_KEY`
* Playlist manager tuning knobs (`TRACKS_PER_PLAYLIST`, `MIN_REPEAT_GAP_DAYS`, etc.).

Generate a Fernet key for `SPOTIFY_TOKEN_KEY`:

```
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 2. Containers

Spin everything up:

```
make up
```

Services exposed locally (use explicit IPv4 to satisfy Spotify OAuth callbacks):
* API – http://127.0.0.1:8000
* Frontend – http://127.0.0.1:3000
* Flower (task monitoring) – http://127.0.0.1:5555
* PostgreSQL – port 5432
* Redis – port 6379

Apply database migrations:

```
make migrate
```

Optional seed data for a default curation policy:

```
make seed
```

### 3. Spotify Admin Onboarding

Use the admin API to onboard service accounts:
1. Call `GET /api/v1/admin/connect` with `X-ADMIN-API-KEY` to receive an authorization URL.
2. Complete the Spotify OAuth flow at `/api/v1/admin/callback`; the API persists encrypted tokens tied to the account.
3. Manage account status (`/api/v1/admin/accounts`, `/api/v1/admin/accounts/{id}/deactivate`).

### 4. Album Ingest & Public Submission
* Admins can validate and queue batch album URLs via `/api/v1/ingest/albums/validate` and `/api/v1/ingest/albums/submit`.
* End users may suggest a single album through `/api/v1/ingest/albums/submit-one`.
* Progress is available at `/api/v1/ingest/status`.

### 5. Playlist Operations
* Create playlist templates tied to curation policies (`POST /api/v1/playlists/templates`).
* Trigger full or single playlist syncs (`POST /api/v1/playlists/sync`, `POST /api/v1/playlists/{id}/sync`).
* Public directory (`GET /api/v1/public/playlists`) lists names, per-account links, and last sync timestamps.

### 6. Manager Controls
* Retrieve the latest scaling plan: `GET /api/v1/manager/plan`.
* Execute a reconciliation run: `POST /api/v1/manager/execute`.

### 7. Legacy Gemini Flow
The end-user React experience still calls `POST /api/v1/playlist/generate`, which uses the Gemini Flash model to return 10 curated songs for a given vibe.

## Tooling & Scripts

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `make up`    | Build and start all services via Docker Compose|
| `make down`  | Stop services and remove volumes               |
| `make migrate` | Apply Alembic migrations to PostgreSQL      |
| `make seed`  | Load baseline curation policy example          |
| `make fmt`   | Run automatic formatting (FastAPI container)  |

## Documentation
* [Architecture](documentation/ARCHITECTURE.md)
* [API Reference](documentation/API.md)
* [Playbook](documentation/PLAYBOOK.md)
* [Naming Conventions](documentation/NAMING.md)

Each document has been updated to reflect the API/Worker/Datastore split, scheduling expectations, and multi-account playlist replication.
