from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import models as db_models
from app.db.session import SessionLocal
from app.services.metrics_service import metrics_service
from app.services.sampler_service import sampler_service
from workers import celery_app


@celery_app.task(name="ingest_albums_from_sources")
def ingest_albums_from_sources() -> str:
    # Placeholder; ingestion is triggered via API for now.
    return "ingest_albums_from_sources queued"


@celery_app.task(name="fetch_audio_features")
def fetch_audio_features(batch: list[str]) -> dict[str, Any]:
    return {"processed": len(batch)}


@celery_app.task(name="build_playlist_snapshot")
def build_playlist_snapshot(playlist_id: str | None = None) -> dict[str, Any]:
    if not playlist_id:
        return {"status": "skipped", "reason": "no playlist"}
    session: Session = SessionLocal()
    try:
        playlist = session.get(db_models.Playlist, playlist_id)
        if not playlist:
            return {"status": "missing", "playlist_id": playlist_id}
        sampler_service.select_tracks(
            session,
            playlist,
            playlist.size,
            get_settings().cooldown_days,
            get_settings().artist_cap,
        )
        return {"status": "sampled", "playlist_id": playlist_id}
    finally:
        session.close()


@celery_app.task(name="refresh_tokens")
def refresh_tokens() -> str:
    return "refresh_tokens queued"


@celery_app.task(name="scale_playlists_daily")
def scale_playlists_daily() -> dict[str, Any]:
    return {"scaled_at": datetime.utcnow().isoformat()}


@celery_app.task(name="metrics_snapshot")
def metrics_snapshot() -> dict[str, Any]:
    session: Session = SessionLocal()
    try:
        overview = metrics_service.get_overview(session)
        return overview.dict()
    finally:
        session.close()
