# Deployment Guide

## Local Development

1. Install Docker Engine and Docker Compose.
2. Duplicate `.env.example` → `.env` and populate Spotify + database credentials.
3. Launch the stack:
   ```bash
   make up
   ```
   This starts the FastAPI backend (`:8000`), Vite dashboard (`:3000`), PostgreSQL (`:5432`), Redis (`:6379`), and worker placeholders.
4. Apply database migrations:
   ```bash
   make migrate
   ```
5. Visit http://127.0.0.1:3000, log in with the dev credentials, and begin onboarding accounts / ingesting albums.

Useful commands:

| Command | Description |
|---------|-------------|
| `make up` | Build + start all services |
| `make down` | Stop and remove containers |
| `make migrate` | Run Alembic migrations |
| `make seed` | Optional seed routine |

## Frontend-Only Iteration

For UI work, the dashboard can run standalone:

```bash
cd frontend
npm install
npm run dev
```

Ensure `VITE_API_BASE_URL` points to the running backend (default `http://127.0.0.1:8000`).

## VPS Deployment (Ubuntu/Debian)

1. Provision a VM with Docker + Docker Compose.
2. Clone the repository and copy `.env` with production credentials (update `SPOTIFY_REDIRECT_URI` to the public hostname, e.g. `https://vibe.example.com/api/v1/oauth/spotify/callback`).
3. Configure a reverse proxy (Nginx/Traefik) to forward HTTPS traffic to the backend (`127.0.0.1:8000`) and frontend (`127.0.0.1:3000`).
4. Run `docker compose up -d --build` to start the services in detached mode.
5. Apply migrations inside the backend container:
   ```bash
   docker compose exec backend alembic upgrade head
   ```
6. Secure the host:
   - Enable UFW firewall (allow 22/80/443).
   - Issue TLS certificates via Certbot.
   - Configure `restart: unless-stopped` or `always` policies (already set in compose).
   - Mount volumes for PostgreSQL/Redis data persistence.
7. Schedule backups (pg_dump) and log rotation.
8. Monitor uptime (Uptime Kuma, Healthchecks) and extend metrics via `/api/v1/metrics/overview`.

## Spotify OAuth Checklist

- Register a Spotify application with redirect URI pointing to the backend callback.
- Allowlist `https://127.0.0.1` or the production domain as necessary.
- When running locally, access the dashboard via `http://127.0.0.1` (Spotify rejects `localhost`).

## Troubleshooting

| Symptom | Resolution |
|---------|------------|
| `401 Not authenticated` | Ensure the dev login succeeded and the browser sends the `dashboard_session` cookie. |
| `Invalid state` on OAuth callback | Session expired or tab open too long – re-trigger `/accounts/connect`. |
| Playlist creation fails | Verify Spotify quota, refresh tokens via `/api/v1/accounts/refresh/{id}`, and check backend logs. |
| Ingest stalls | Confirm the active account is set and has sufficient scopes (`playlist-modify-public`, `playlist-modify-private`). |
