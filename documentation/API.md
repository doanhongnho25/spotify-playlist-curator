# Project Vibe API Reference

Base URL: `http://127.0.0.1:8000`

All admin endpoints require the header `X-ADMIN-API-KEY` matching the configured `ADMIN_API_KEY` value. Public endpoints do not require authentication.

## Health

### `GET /`
Returns `{ "status": "ok", "environment": "development" }` when the gateway is reachable.

## Admin – Spotify Accounts

### `GET /api/v1/admin/accounts`
List onboarded Spotify service accounts.

**Headers:**
```
X-ADMIN-API-KEY: <secret>
```

**Response:**
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
  ]
}
```

### `GET /api/v1/admin/connect`
Start OAuth onboarding for a new account. Returns the Spotify authorization URL, generated `state`, and redirect URI. The frontend should redirect the administrator to the provided `authorize_url`.

### `GET /api/v1/admin/callback`
Spotify redirects here after the admin completes OAuth. Tokens are exchanged, encrypted, and persisted. Response payload contains the created/updated account ID.

### `POST /api/v1/admin/accounts/{id}/deactivate`
Soft-deactivate an account (status becomes `inactive`).

## Ingest – Album Sources

### `POST /api/v1/ingest/albums/validate`
Validate a list of album URLs (deduplicated, whitespace trimmed). Returns the normalized URLs that would be queued.

### `POST /api/v1/ingest/albums/submit`
Admin-only batch submission of album URLs. Creates/updates `album_sources` records.

### `POST /api/v1/ingest/albums/submit-one`
Public endpoint for end users to recommend a single album URL.

### `GET /api/v1/ingest/status`
Returns the most recent 100 album sources with status metadata.

## Playlists & Curation

### `POST /api/v1/playlists/templates`
Create a logical playlist tied to an existing `curation_policy` (supply `name`, optional `description`, and `policy_id`). Response includes the playlist ID and marks the action as `created`.

### `POST /api/v1/playlists/sync`
Queue a full synchronization for all playlists (returns status `queued`).

### `POST /api/v1/playlists/{id}/sync`
Trigger synchronization for a single playlist. Updates `last_synced_at` immediately for bookkeeping and returns the timestamp.

### `GET /api/v1/public/playlists`
Public directory of logical playlists. Each entry includes playlist metadata plus an array of account link objects `{ "account_id", "url", "status" }` for Spotify external URLs that are currently published.

### `GET /api/v1/public/playlists/{id}`
Retrieve one playlist listing by ID.

## Manager – Scaling

### `GET /api/v1/manager/plan`
Fetch the most recent scaling plan (`manager_plans` entry). If no plan exists, a default stub is generated.

### `POST /api/v1/manager/execute`
Persist an execution record with timestamp metadata. Intended to represent applying the scaling plan (detailed logic handled by workers).

## Legacy Gemini Endpoint

### `POST /api/v1/playlist/generate`
Request body `{ "vibe": "upbeat summer" }`. Returns 10 `{ "title", "artist" }` pairs produced by the Gemini Flash model. Requires a valid `GEMINI_API_KEY` configuration.

## Error Handling
* `401 Unauthorized` – missing/invalid admin API key.
* `404 Not Found` – referenced resource is absent (e.g., playlist ID not found).
* `400 Bad Request` – malformed request payload (e.g., submitting multiple URLs to `/submit-one`).
* `500 Internal Server Error` – Gemini parsing errors or upstream HTTP failures.

All errors follow FastAPI's `{ "detail": "message" }` shape unless otherwise noted.

## End-User Session (legacy)

### `GET /api/v1/auth/login`
Initiate OAuth for an end user who wants to save a one-off playlist. Sets an HTTP-only `spotify_session` cookie.

### `GET /api/v1/auth/status`
Returns `{ "authenticated": true|false }` depending on the in-memory session.

### `POST /api/v1/auth/logout`
Clears the cookie and removes the server-side session entry.
