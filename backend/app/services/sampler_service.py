from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from app.db.models import Playlist, PlaylistEntryHistory, Track
from app.utils.random_utils import pick_many, shuffle


class SamplerService:
    def select_tracks(
        self,
        db: Session,
        playlist: Playlist,
        size: int,
        cooldown_days: int,
        artist_cap: int,
    ) -> List[Track]:
        candidates = (
            db.query(Track)
            .filter(Track.is_usable.is_(True))
            .order_by(Track.popularity.desc().nulls_last())
            .all()
        )
        if not candidates:
            return []

        cutoff = datetime.utcnow() - timedelta(days=cooldown_days)
        recent_ids = {
            entry.track_id
            for entry in db.query(PlaylistEntryHistory)
            .filter(PlaylistEntryHistory.playlist_id == playlist.id)
            .filter(PlaylistEntryHistory.added_at >= cutoff)
        }
        filtered = [track for track in candidates if track.id not in recent_ids]
        if len(filtered) < size:
            filtered = candidates

        grouped = defaultdict(list)
        for track in filtered:
            grouped[track.artist].append(track)

        selected: List[Track] = []
        artist_counts: dict[str, int] = defaultdict(int)
        artist_cycle = shuffle(grouped.keys())
        idx = 0
        while len(selected) < size and artist_cycle:
            artist = artist_cycle[idx % len(artist_cycle)]
            pool = grouped[artist]
            if not pool:
                idx += 1
                if idx > len(artist_cycle) * 5:
                    break
                continue
            if artist_counts[artist] >= artist_cap:
                idx += 1
                continue
            choice = pick_many(pool, 1)[0]
            selected.append(choice)
            artist_counts[artist] += 1
            pool.remove(choice)
            idx += 1
            if idx > len(artist_cycle) * 5:
                break

        if len(selected) < size:
            remaining = [track for track in filtered if track not in selected]
            selected.extend(pick_many(remaining, size - len(selected)))
        return selected[:size]


sampler_service = SamplerService()
