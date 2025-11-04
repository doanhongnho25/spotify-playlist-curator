from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    spotify_playlist_id = Column(String, nullable=True)
    name = Column(String, nullable=False)
    prefix = Column(String, nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("spotify_accounts.id"), nullable=False)
    size = Column(Integer, nullable=False, default=50)
    last_reshuffled_at = Column(DateTime, nullable=True)
    next_reshuffle_at = Column(DateTime, nullable=True)
    external_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    account = relationship("SpotifyAccount", back_populates="playlists")
    entries = relationship("PlaylistEntryHistory", back_populates="playlist", cascade="all, delete-orphan")
