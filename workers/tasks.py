from __future__ import annotations

from datetime import datetime
from typing import Any

from celery.schedules import crontab

from workers import celery_app


@celery_app.task(name="ingest_albums_from_sources")
def ingest_albums_from_sources() -> str:
    return "ingest_albums_from_sources queued"


@celery_app.task(name="ingest_album_by_url")
def ingest_album_by_url(url: str) -> str:
    return f"ingest_album_by_url:{url}"


@celery_app.task(name="fetch_audio_features")
def fetch_audio_features(batch: list[str]) -> dict[str, Any]:
    return {"processed": len(batch)}


@celery_app.task(name="build_playlist_snapshot")
def build_playlist_snapshot(policy_id: str | None = None, playlist_id: str | None = None) -> dict[str, Any]:
    return {"policy_id": policy_id, "playlist_id": playlist_id}


@celery_app.task(name="ensure_playlist_for_account")
def ensure_playlist_for_account(playlist_id: str, account_id: str) -> dict[str, str]:
    return {"playlist_id": playlist_id, "account_id": account_id}


@celery_app.task(name="refresh_tokens")
def refresh_tokens() -> str:
    return "refresh_tokens"


@celery_app.task(name="scale_playlists_daily")
def scale_playlists_daily() -> dict[str, Any]:
    return {"scaled_at": datetime.utcnow().isoformat()}


celery_app.conf.beat_schedule = {
    "scale-daily": {
        "task": "scale_playlists_daily",
        "schedule": crontab(hour=2, minute=0),
    },
    "refresh-tokens": {
        "task": "refresh_tokens",
        "schedule": crontab(minute="*/30"),
    },
    "ingest-morning": {
        "task": "ingest_albums_from_sources",
        "schedule": crontab(hour=3, minute=0),
    },
}
