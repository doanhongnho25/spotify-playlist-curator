# API Reference

All endpoints live under the `/api/v1` prefix and require an authenticated dashboard session cookie unless noted. Responses use JSON.

## Authentication

### `POST /api/v1/auth/dev-login`
Request body:
```json
{ "username": "admin", "password": "admin" }
```
Sets an HTTP-only `dashboard_session` cookie. Returns `{ "message": "logged_in" }`.

### `GET /api/v1/auth/dev-status`
Returns `{ "authenticated": true }` when the cookie is valid.

### `POST /api/v1/auth/dev-logout`
Clears the session cookie and returns `{ "message": "logged_out" }`.

## Spotify OAuth

### `GET /api/v1/accounts/connect`
Returns `{ "authorization_url": "https://accounts.spotify.com/authorize?..." }`.

### `GET /api/v1/oauth/spotify/callback`
Parameters: `code`, `state` (from Spotify). Exchanges the code, upserts the Spotify account, and marks it active for the current session. Response `{ "status": "connected" }`.

## Accounts

### `GET /api/v1/accounts/list`
Returns
```json
{
  "accounts": [
    {
      "id": "...",
      "display_name": "Vibe Bot",
      "spotify_user_id": "user123",
      "prefix": "Vibe Collection",
      "expires_at": "2024-05-01T12:00:00Z",
      "playlists_count": 40,
      "status": "active"
    }
  ],
  "active_account_id": "..."
}
```

### `POST /api/v1/accounts/active/set`
Body `{ "account_id": "<uuid or null>" }`. Stores the active account for the current session. Returns the same payload as `/list`.

### `POST /api/v1/accounts/prefix`
Body `{ "account_id": "<uuid>", "prefix": "Midnight Flow" }`. Updates the naming prefix and returns `{ "id": "...", "prefix": "Midnight Flow" }`.

### `POST /api/v1/accounts/refresh/{id}`
Refreshes Spotify tokens. Response mirrors an `AccountRead` object.

### `DELETE /api/v1/accounts/{id}`
Marks the account inactive and clears it as active for the session.

## Library

### `POST /api/v1/library/ingest`
Body:
```json
{
  "album_urls": ["https://open.spotify.com/album/..."]
}
```
Uses the active account token to fetch album metadata + tracks, storing results in the database. Returns `{ "queued": <count> }`.

## Playlists

### `GET /api/v1/playlists/list`
Returns `{ "playlists": [ { ...PlaylistRead } ] }`.

### `POST /api/v1/playlists/create`
Body:
```json
{
  "account_id": "<uuid>",
  "count": 25,
  "prefix": "Aurora",
  "size": 50,
  "interval_days": 5
}
```
Creates the requested number of playlists for the account, sampling tracks according to cooldown + artist cap settings. Response `{ "created_playlist_ids": ["..."] }`.

### `POST /api/v1/playlists/{id}/reshuffle`
Replaces the playlist tracks with a fresh 50-track snapshot and logs history. Returns `{ "id": "...", "status": "reshuffled" }`.

### `POST /api/v1/playlists/reshuffle-bulk`
Body example:
```json
{ "mode": "account", "account_id": "<uuid>" }
```
Mode options: `all`, `account`, `selected`. Returns `{ "created_playlist_ids": ["..."] }` representing reshuffled playlists.

## Settings

### `GET /api/v1/settings`
Returns current runtime configuration, e.g.
```json
{
  "playlist_size": 50,
  "reshuffle_interval_days": 5,
  "cooldown_days": 5,
  "max_playlists_per_account": 200,
  "artist_cap": 2,
  "default_prefix": "Vibe Collection"
}
```

### `POST /api/v1/settings`
Accepts the same shape to persist overrides in the `settings` table.

## Metrics

### `GET /api/v1/metrics/overview`
Returns counts for accounts, playlists, tracks, reshuffles scheduled today, next reshuffle ETA, and a `system_health` summary.

### `GET /api/v1/metrics/history`
Returns `{ "history": [ { "timestamp": "...", "playlists": 120, "reshuffles": 35 } ] }`.

## Jobs

### `GET /api/v1/jobs/list`
Returns scheduler metadata for core jobs (reshuffle, refresh tokens, metrics snapshot).

### `POST /api/v1/jobs/update`
Body `{ "name": "reshuffle_due_playlists", "enabled": true }`. Toggles the job and returns the updated job list.

## Health

### `GET /`
Open healthcheck returning `{ "status": "ok", "environment": "development" }`.
