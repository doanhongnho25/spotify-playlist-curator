from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    accounts_count = Column(Integer, nullable=False, default=0)
    playlists_count = Column(Integer, nullable=False, default=0)
    tracks_count = Column(Integer, nullable=False, default=0)
    reshuffles_last_24h = Column(Integer, nullable=False, default=0)
    avg_tracks_per_playlist = Column(Integer, nullable=False, default=0)
