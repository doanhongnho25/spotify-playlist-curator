# Project Vibe API Reference

Base URL: `http://127.0.0.1:8000`

Unless noted otherwise, endpoints that mutate state require an authenticated dashboard session (`dashboard_session` cookie issued by `/api/v1/auth/dev-login`). Public endpoints are explicitly labeled.

## Health

### `GET /`
Returns `{ "status": "ok", "environment": "development" }` when the gateway is reachable.

## Dashboard Authentication

### `POST /api/v1/auth/dev-login`
Authenticate with the dashboard credentials (configured via `DASHBOARD_USERNAME` / `DASHBOARD_PASSWORD`).

**Body**
```json
{
  "username": "admin",
  "password": "admin"
}
```

**Response**
```json
{ "authenticated": true }
```

Sets an HTTP-only cookie `dashboard_session` valid for 12 hours.

### `GET /api/v1/auth/dev-status`
Returns authentication status and the session's active Spotify account (if any).

```json
{ "authenticated": true, "active_account_id": "6a8c..." }
```

### `POST /api/v1/auth/dev-logout`
Invalidates the session and clears the `dashboard_session` cookie.

## Spotify OAuth & Accounts

### `GET /api/v1/oauth/spotify/connect`
Initiate OAuth onboarding for a new Spotify service account. Returns the authorization URL and state token.

```json
{
  "authorize_url": "https://accounts.spotify.com/authorize?...",
  "state": "abc123",
  "redirect_uri": "http://127.0.0.1:3000/api/v1/oauth/spotify/callback"
}
```

### `GET /api/v1/oauth/spotify/callback`
Spotify redirects here after consent. The API exchanges tokens, encrypts them, persists the account, and redirects back to `PUBLIC_BASE_URL`.

### `GET /api/v1/accounts/list`
List onboarded Spotify service accounts and identify the active account for the current session.

**Response**
```json
{
  "accounts": [
    {
      "id": "8f826cbe-...",
      "spotify_user_id": "service_account",
      "display_name": "Vibe Publisher",
      "status": "active",
      "expires_at": "2024-07-11T12:00:00+00:00",
      "created_at": "2024-07-01T01:02:03+00:00",
      "updated_at": "2024-07-01T01:02:03+00:00"
    }
  ],
  "active_account_id": "8f826cbe-..."
}
```

### `POST /api/v1/accounts/remove`
Soft-deactivate an account (status becomes `inactive`).

**Body**
```json
{ "account_id": "8f826cbe-..." }
```

### `GET /api/v1/accounts/active/get`
Retrieve the active Spotify account for the current dashboard session.

```json
{ "active_account_id": "8f826cbe-..." }
```

### `POST /api/v1/accounts/active/set`
Update the active Spotify account for the session. Passing `null` clears the selection.

**Body**
```json
{ "account_id": "8f826cbe-..." }
```

**Response**
```json
{ "active_account_id": "8f826cbe-..." }
```

## Ingest – Album Sources

### `POST /api/v1/ingest/albums/validate`
Validate a list of album URLs (deduplicated, whitespace trimmed). Returns the normalized URLs that would be queued.

### `POST /api/v1/ingest/albums/submit`
Batch submission of album URLs. Creates/updates `album_sources` records and marks them `queued` for workers. Requires dashboard session.

### `POST /api/v1/ingest/albums/submit-one`
**Public** endpoint for end users to recommend a single album URL.

### `GET /api/v1/ingest/status`
Returns the most recent 100 album sources with status metadata (queued/ingested/failed, timestamps, failure reasons).

## Playlists & Curation

### `POST /api/v1/playlists/templates`
Create a logical playlist tied to an existing `curation_policy` (supply `name`, optional `description`, and `policy_id`). Response includes the playlist ID and marks the action as `created`.

### `POST /api/v1/playlists/sync`
Queue a full synchronization for all playlists (placeholder response `status: "queued"`).

### `POST /api/v1/playlists/{id}/sync`
Trigger synchronization for a single playlist. Updates `last_synced_at` immediately for bookkeeping and returns the timestamp.

### `GET /api/v1/public/playlists`
**Public** directory of logical playlists. Each entry includes playlist metadata plus an array of account link objects `{ "account_id", "url", "status" }` for Spotify external URLs that are currently published.

### `GET /api/v1/public/playlists/{id}`
**Public** – retrieve one playlist listing by ID.

## Manager – Scaling

### `GET /api/v1/manager/plan`
Fetch the most recent scaling plan (`manager_plans` entry). If no plan exists, a default stub is generated.

### `POST /api/v1/manager/execute`
Persist an execution record with timestamp metadata. Intended to represent applying the scaling plan (detailed logic handled by workers).

## Error Handling

* `401 Unauthorized` – missing or expired dashboard session.
* `404 Not Found` – referenced resource is absent (e.g., playlist ID not found).
* `400 Bad Request` – malformed request payload (e.g., submitting multiple URLs to `/submit-one`).
* `500 Internal Server Error` – upstream HTTP failures when contacting Spotify.

All errors follow FastAPI's `{ "detail": "message" }` shape unless otherwise noted.
