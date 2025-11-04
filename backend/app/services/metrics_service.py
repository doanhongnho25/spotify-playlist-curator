from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.v1.schemas.metrics import MetricOverview, MetricsHistoryPoint
from app.db.models import MetricSnapshot, Playlist, PlaylistEntryHistory, SpotifyAccount, Track
from app.utils.time_utils import utc_now


class MetricsService:
    def get_overview(self, db: Session) -> MetricOverview:
        accounts = db.query(func.count(SpotifyAccount.id)).scalar() or 0
        playlists = db.query(func.count(Playlist.id)).scalar() or 0
        tracks = db.query(func.count(Track.id)).scalar() or 0
        today = utc_now().date()
        tomorrow = today + timedelta(days=1)
        reshuffles_today = (
            db.query(func.count(PlaylistEntryHistory.id))
            .filter(PlaylistEntryHistory.added_at >= datetime.combine(today, datetime.min.time()))
            .filter(PlaylistEntryHistory.added_at < datetime.combine(tomorrow, datetime.min.time()))
            .scalar()
            or 0
        )
        next_reshuffle = (
            db.query(func.min(Playlist.next_reshuffle_at))
            .filter(Playlist.next_reshuffle_at.isnot(None))
            .scalar()
        )
        health = "stable" if reshuffles_today >= 0 else "unknown"
        return MetricOverview(
            accounts=accounts,
            playlists=playlists,
            tracks=tracks,
            reshuffles_scheduled_today=reshuffles_today,
            next_reshuffle_at=next_reshuffle,
            system_health=health,
        )

    def get_history(self, db: Session, days: int = 7) -> List[MetricsHistoryPoint]:
        cutoff = utc_now() - timedelta(days=days)
        snapshots = (
            db.query(MetricSnapshot)
            .filter(MetricSnapshot.created_at >= cutoff)
            .order_by(MetricSnapshot.created_at.asc())
            .all()
        )
        return [
            MetricsHistoryPoint(
                timestamp=snapshot.created_at,
                playlists=snapshot.playlists_count,
                reshuffles=snapshot.reshuffles_last_24h,
            )
            for snapshot in snapshots
        ]


metrics_service = MetricsService()
