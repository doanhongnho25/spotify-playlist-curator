from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Track(Base):
    __tablename__ = "tracks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    spotify_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    popularity = Column(Integer, nullable=True)
    album_id = Column(UUID(as_uuid=True), ForeignKey("albums.id"), nullable=False)
    audio_features = Column(JSON, nullable=True)
    is_usable = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    album = relationship("Album", back_populates="tracks")
    history_entries = relationship(
        "PlaylistEntryHistory",
        back_populates="track",
        cascade="all, delete-orphan",
    )
