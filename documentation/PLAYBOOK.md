# Operations Playbook

## Daily Cadence (UTC)
| Time  | Job                           |
|-------|-------------------------------|
| 02:00 | `scale_playlists_daily`       |
| 02:30 | `refresh_tokens` (every 30m)  |
| 03:00 | `ingest_albums_from_sources`  |
| 03:30 | `fetch_audio_features`        |
| 04:00 | `build_playlist_snapshot`     |
| 04:10 | `ensure_playlist_for_account` |

## Manual Procedures

### Rolling Ingest Restart
1. `make down`
2. `make up`
3. Check Flower for stalled tasks.

### Trigger Full Sync
```
curl -X POST http://127.0.0.1:8000/api/v1/playlists/sync \
  --cookie "dashboard_session=<value>"
```

### Add Spotify Account
1. Authenticate via `/api/v1/auth/dev-login` (dashboard or API) to obtain `dashboard_session`.
2. Call `GET /api/v1/oauth/spotify/connect` with the session cookie to receive `authorize_url`.
3. Follow the URL, approve the scopes, and allow the backend callback to persist the account.

### Emergency Token Refresh
```
docker compose exec worker celery -A workers.tasks call refresh_tokens
```
*(production relies on Celery beat; use the manual command only for emergencies)*

## Monitoring & Alerts
* **Flower** at `http://127.0.0.1:5555` for task queues.
* Metrics to wire into Prometheus/Grafana:
  * `tracks_ingested_total`
  * `playlists_synced_total`
  * `429_count`
  * `account_health{status}`

## Incident Response Checklist
1. Identify failing accounts (`GET /api/v1/accounts/list`).
2. Quarantine by setting status to `inactive` via `POST /api/v1/accounts/remove`.
3. Re-run `scale_playlists_daily` to redistribute load.
4. Inspect Redis throttles before re-enabling.
5. Record actions in an operational log referencing `manager_plans` entry.
