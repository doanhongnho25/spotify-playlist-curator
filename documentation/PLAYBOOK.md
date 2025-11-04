# Operations Playbook

## Daily Cadence (UTC)

| Time  | Job                           | Notes |
|-------|-------------------------------|-------|
| 02:00 | `scale_playlists_daily`       | Compute target playlist counts per account |
| 02:30 | `refresh_tokens` (every 30m)  | Refresh Spotify tokens expiring within 5 minutes |
| 03:00 | `ingest_albums_from_sources`  | Pull queued album URLs |
| 03:30 | `fetch_audio_features`        | Hydrate track audio features |
| 04:00 | `build_playlist_snapshot`     | Sample 50 tracks per playlist |
| 04:10 | `ensure_playlist_for_account` | Sync playlists to Spotify |
| hourly | `metrics_snapshot`           | Capture counts for dashboard charts |

Use `/api/v1/jobs/list` to verify schedule state and `/api/v1/jobs/update` to toggle jobs when testing locally.

## Manual Procedures

### Rolling Ingest Restart
```bash
make down
make up
```
Validate worker queues (Flower or Celery logs) before resuming ingest submissions.

### Trigger Playlist Creation
```bash
curl -X POST http://127.0.0.1:8000/api/v1/playlists/create \
  -H 'Content-Type: application/json' \
  --cookie "dashboard_session=<value>" \
  -d '{"account_id": "<uuid>", "count": 5}'
```

### Force Reshuffle for an Account
```bash
curl -X POST http://127.0.0.1:8000/api/v1/playlists/reshuffle-bulk \
  -H 'Content-Type: application/json' \
  --cookie "dashboard_session=<value>" \
  -d '{"mode": "account", "account_id": "<uuid>"}'
```

### Emergency Token Refresh
```bash
curl -X POST http://127.0.0.1:8000/api/v1/accounts/refresh/<uuid> \
  --cookie "dashboard_session=<value>"
```

## Monitoring & Alerts
- Observe worker queues via Flower (default `http://127.0.0.1:5555`) or Celery logs.
- Track key metrics (export via custom Prometheus collector if needed):
  - playlists_created_total
  - reshuffles_total
  - retry_count (429/5xx)
  - account_health{status}

## Incident Response Checklist
1. Inspect `/api/v1/accounts/list` for degraded accounts (token expiry, errors).
2. Temporarily deactivate problematic accounts via `DELETE /api/v1/accounts/{id}`.
3. Re-run scaling (`scale_playlists_daily`) to redistribute playlists.
4. Verify Redis rate limiter state before re-enabling.
5. Document actions (timestamp, affected accounts/playlists) in operational logs.
