from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.tables import Playlist, PlaylistEntriesHistory, Track

settings = get_settings()


class InsufficientTracksError(RuntimeError):
    """Raised when the track pool cannot satisfy the requested sample size."""


def _recent_track_ids(session: Session, playlist_id: UUID, cooldown_days: int) -> set[UUID]:
    cutoff = datetime.utcnow() - timedelta(days=cooldown_days)
    stmt = select(PlaylistEntriesHistory.track_id).where(
        PlaylistEntriesHistory.playlist_id == playlist_id,
        PlaylistEntriesHistory.added_at >= cutoff,
    )
    return {row[0] for row in session.execute(stmt).all()}


def _usable_tracks(session: Session, exclude_ids: set[UUID]) -> list[Track]:
    stmt = select(Track).where(Track.is_usable.is_(True))
    if exclude_ids:
        stmt = stmt.where(Track.id.notin_(list(exclude_ids)))
    return list(session.scalars(stmt))


def select_tracks_for_playlist(
    playlist_id: UUID,
    *,
    session: Optional[Session] = None,
    seed: Optional[str] = None,
) -> list[Track]:
    owns_session = session is None
    db = session or SessionLocal()
    try:
        playlist = db.get(Playlist, playlist_id)
        if playlist is None:
            raise ValueError("Playlist not found")

        cooldown_days = playlist.cooldown_days or settings.min_repeat_gap_days
        target_size = playlist.target_size or settings.tracks_per_playlist
        recent_ids = _recent_track_ids(db, playlist_id, cooldown_days)
        candidates = _usable_tracks(db, recent_ids)

        rng = random.Random()
        if seed:
            rng.seed(seed)

        if len(candidates) < target_size:
            # Relax cooldown if needed
            relaxed_stmt = select(Track).where(Track.is_usable.is_(True))
            candidates = list(db.scalars(relaxed_stmt))
            if len(candidates) < target_size:
                raise InsufficientTracksError("Not enough usable tracks to satisfy playlist size")

        selected = rng.sample(candidates, target_size)

        batch_tag = datetime.utcnow().strftime("%Y-%m-%d")
        for index, track in enumerate(selected):
            history = PlaylistEntriesHistory(
                playlist_id=playlist_id,
                track_id=track.id,
                batch_tag=batch_tag,
                seed=seed,
                order_index=index,
            )
            db.add(history)
            track.last_used_at = datetime.utcnow()
            db.add(track)

        playlist.last_synced_at = datetime.utcnow()
        playlist.last_reshuffled_at = playlist.last_synced_at
        playlist.next_reshuffle_at = playlist.last_synced_at + timedelta(days=playlist.reshuffle_interval_days)
        db.add(playlist)
        db.commit()
        db.refresh(playlist)

        return selected
    finally:
        if owns_session:
            db.close()
