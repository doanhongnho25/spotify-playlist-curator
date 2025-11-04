from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "spotify_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("spotify_user_id", sa.String(length=255), nullable=False, unique=True),
        sa.Column("prefix", sa.String(length=255), nullable=False, server_default="Vibe Collection"),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("playlists_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "albums",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("spotify_id", sa.String(length=255), nullable=False, unique=True),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("artist", sa.String(length=512), nullable=False),
        sa.Column("track_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "tracks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("spotify_id", sa.String(length=255), nullable=False, unique=True),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("artist", sa.String(length=512), nullable=False),
        sa.Column("popularity", sa.Integer(), nullable=True),
        sa.Column("album_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("albums.id", ondelete="CASCADE"), nullable=False),
        sa.Column("audio_features", sa.JSON(), nullable=True),
        sa.Column("is_usable", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_tracks_artist", "tracks", ["artist"])
    op.create_index("ix_tracks_popularity", "tracks", ["popularity"])

    op.create_table(
        "playlists",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("spotify_playlist_id", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("prefix", sa.String(length=255), nullable=False),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("spotify_accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("size", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("last_reshuffled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_reshuffle_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("external_url", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "playlist_entries_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("playlist_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False),
        sa.Column("track_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("batch_tag", sa.String(length=64), nullable=False),
    )
    op.create_index(
        "ix_playlist_entries_history_playlist_added",
        "playlist_entries_history",
        ["playlist_id", "added_at"],
    )

    op.create_table(
        "settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(length=255), nullable=False, unique=True),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "metric_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("accounts_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("playlists_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tracks_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reshuffles_last_24h", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_tracks_per_playlist", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("metric_snapshots")
    op.drop_table("settings")
    op.drop_index("ix_playlist_entries_history_playlist_added", table_name="playlist_entries_history")
    op.drop_table("playlist_entries_history")
    op.drop_table("playlists")
    op.drop_index("ix_tracks_popularity", table_name="tracks")
    op.drop_index("ix_tracks_artist", table_name="tracks")
    op.drop_table("tracks")
    op.drop_table("albums")
    op.drop_table("spotify_accounts")
