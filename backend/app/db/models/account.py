from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class SpotifyAccount(Base):
    __tablename__ = "spotify_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    display_name = Column(String, nullable=False)
    spotify_user_id = Column(String, nullable=False, unique=True)
    prefix = Column(String, nullable=False, default="Vibe Collection")
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    playlists_count = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    playlists = relationship("Playlist", back_populates="account", cascade="all, delete-orphan")
