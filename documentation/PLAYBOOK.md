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
curl -X POST http://localhost:8000/api/v1/playlists/sync \
  -H "X-ADMIN-API-KEY: $ADMIN_API_KEY"
```

### Add Spotify Account
1. `GET /api/v1/admin/connect` (header `X-ADMIN-API-KEY`).
2. Follow `authorize_url` in a browser, grant access.
3. `GET /api/v1/admin/callback?code=...&state=...` automatically persists the account.

### Emergency Token Refresh
```
curl -X POST http://localhost:8000/celery/refresh \
  -H "X-ADMIN-API-KEY: $ADMIN_API_KEY"
```
*(placeholder – actual trigger uses Celery beat; manual invocation should call the task via `celery_app.send_task("refresh_tokens")`)*

## Monitoring & Alerts
* **Flower** at `http://localhost:5555` for task queues.
* Metrics to wire into Prometheus/Grafana:
  * `tracks_ingested_total`
  * `playlists_synced_total`
  * `429_count`
  * `account_health{status}`

## Incident Response Checklist
1. Identify failing accounts (`GET /api/v1/admin/accounts`).
2. Quarantine by setting status to `inactive`.
3. Re-run `scale_playlists_daily` to redistribute load.
4. Inspect Redis throttles before re-enabling.
5. Record actions in an operational log referencing `manager_plans` entry.
