from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Album(Base):
    __tablename__ = "albums"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    spotify_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    track_count = Column(Integer, nullable=False, default=0)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tracks = relationship("Track", back_populates="album", cascade="all, delete-orphan")
