from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class AccountStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    degraded = "degraded"
    quarantined = "quarantined"


class AlbumSourceStatus(str, enum.Enum):
    queued = "queued"
    ingested = "ingested"
    failed = "failed"


class PlaylistAccountStatus(str, enum.Enum):
    pending = "pending"
    syncing = "syncing"
    synced = "synced"
    error = "error"
    archived = "archived"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spotify_user_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255))
    access_token_encrypted: Mapped[Optional[str]] = mapped_column(Text)
    refresh_token_encrypted: Mapped[Optional[str]] = mapped_column(Text)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[AccountStatus] = mapped_column(Enum(AccountStatus), default=AccountStatus.active)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    playlists: Mapped[list["PlaylistAccountMap"]] = relationship(back_populates="account", cascade="all, delete-orphan")


class AlbumSource(Base):
    __tablename__ = "album_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True)
    owner_tag: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[AlbumSourceStatus] = mapped_column(Enum(AlbumSourceStatus), default=AlbumSourceStatus.queued)
    queued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ingested_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    failure_reason: Mapped[Optional[str]] = mapped_column(Text)

    albums: Mapped[list["Album"]] = relationship(back_populates="source")


class Album(Base):
    __tablename__ = "albums"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("album_sources.id", ondelete="SET NULL"))
    spotify_album_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    artist: Mapped[str] = mapped_column(String(512), nullable=False)
    release_date: Mapped[Optional[str]] = mapped_column(String(64))
    total_tracks: Mapped[int] = mapped_column(Integer, default=0)
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSON)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    source: Mapped[Optional[AlbumSource]] = relationship(back_populates="albums")
    tracks: Mapped[list["Track"]] = relationship(back_populates="album")


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    album_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("albums.id", ondelete="SET NULL"))
    spotify_track_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    artist: Mapped[str] = mapped_column(String(512), nullable=False)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    popularity: Mapped[Optional[int]] = mapped_column(Integer)
    energy: Mapped[Optional[float]] = mapped_column(Float)
    danceability: Mapped[Optional[float]] = mapped_column(Float)
    audio_features: Mapped[Optional[dict]] = mapped_column(JSON)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    album: Mapped[Optional[Album]] = relationship(back_populates="tracks")
    history_entries: Mapped[list["PlaylistEntriesHistory"]] = relationship(back_populates="track")

    __table_args__ = (
        Index("ix_tracks_artist", "artist"),
        Index("ix_tracks_popularity", "popularity"),
    )


class AlbumTrackMap(Base):
    __tablename__ = "album_track_map"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    album_source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("album_sources.id", ondelete="CASCADE"))
    track_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tracks.id", ondelete="CASCADE"))

    __table_args__ = (
        UniqueConstraint("album_source_id", "track_id", name="uq_album_track"),
    )


class CurationPolicy(Base):
    __tablename__ = "curation_policies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    policy_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    playlists: Mapped[list["Playlist"]] = relationship(back_populates="policy")


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    policy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("curation_policies.id", ondelete="CASCADE"))
    theme_tag: Mapped[Optional[str]] = mapped_column(String(64))
    global_index: Mapped[int] = mapped_column(Integer)
    replication_factor: Mapped[int] = mapped_column(Integer, default=1)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    policy: Mapped[CurationPolicy] = relationship(back_populates="playlists")
    account_maps: Mapped[list["PlaylistAccountMap"]] = relationship(back_populates="playlist")
    history_entries: Mapped[list["PlaylistEntriesHistory"]] = relationship(back_populates="playlist")


class PlaylistAccountMap(Base):
    __tablename__ = "playlist_account_map"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    playlist_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("playlists.id", ondelete="CASCADE"))
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"))
    spotify_playlist_id: Mapped[Optional[str]] = mapped_column(String(128))
    spotify_external_url: Mapped[Optional[str]] = mapped_column(String(2048))
    status: Mapped[PlaylistAccountStatus] = mapped_column(Enum(PlaylistAccountStatus), default=PlaylistAccountStatus.pending)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    playlist: Mapped[Playlist] = relationship(back_populates="account_maps")
    account: Mapped[Account] = relationship(back_populates="playlists")

    __table_args__ = (
        UniqueConstraint("playlist_id", "account_id", name="uq_playlist_account"),
    )


class PlaylistEntriesHistory(Base):
    __tablename__ = "playlist_entries_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    playlist_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("playlists.id", ondelete="CASCADE"))
    track_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tracks.id", ondelete="CASCADE"))
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    batch_tag: Mapped[str] = mapped_column(String(64))

    playlist: Mapped[Playlist] = relationship(back_populates="history_entries")
    track: Mapped[Track] = relationship(back_populates="history_entries")

    __table_args__ = (
        Index("ix_playlist_history_playlist_added", "playlist_id", "added_at"),
    )


class ManagerPlan(Base):
    __tablename__ = "manager_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    stats: Mapped[dict] = mapped_column(JSON)
    actions: Mapped[dict] = mapped_column(JSON)
    executed: Mapped[bool] = mapped_column(Boolean, default=False)


class RecentUsageView(Base):
    __tablename__ = "recent_usage"
    __table_args__ = {"info": {"is_view": True}}

    track_spotify_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    last_used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
