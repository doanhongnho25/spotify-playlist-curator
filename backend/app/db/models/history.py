from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class PlaylistEntryHistory(Base):
    __tablename__ = "playlist_entries_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    playlist_id = Column(UUID(as_uuid=True), ForeignKey("playlists.id"), nullable=False)
    track_id = Column(UUID(as_uuid=True), ForeignKey("tracks.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    batch_tag = Column(String, nullable=False)

    playlist = relationship("Playlist", back_populates="entries")
    track = relationship("Track", back_populates="history_entries")
