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
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("spotify_user_id", sa.String(length=255), nullable=False, unique=True),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("access_token_encrypted", sa.Text(), nullable=True),
        sa.Column("refresh_token_encrypted", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.Enum("active", "inactive", "degraded", "quarantined", name="accountstatus"), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "album_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("url", sa.String(length=2048), nullable=False, unique=True),
        sa.Column("owner_tag", sa.String(length=255), nullable=True),
        sa.Column("status", sa.Enum("queued", "ingested", "failed", name="albumsourcestatus"), nullable=False, server_default="queued"),
        sa.Column("queued_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
    )

    op.create_table(
        "albums",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("album_sources.id", ondelete="SET NULL")),
        sa.Column("spotify_album_id", sa.String(length=128), nullable=False, unique=True),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("artist", sa.String(length=512), nullable=False),
        sa.Column("release_date", sa.String(length=64), nullable=True),
        sa.Column("total_tracks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "curation_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("policy_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "playlists",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curation_policies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("theme_tag", sa.String(length=64), nullable=True),
        sa.Column("global_index", sa.Integer(), nullable=False),
        sa.Column("replication_factor", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "tracks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("album_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("albums.id", ondelete="SET NULL")),
        sa.Column("spotify_track_id", sa.String(length=128), nullable=False, unique=True),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("artist", sa.String(length=512), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("popularity", sa.Integer(), nullable=True),
        sa.Column("energy", sa.Float(), nullable=True),
        sa.Column("danceability", sa.Float(), nullable=True),
        sa.Column("audio_features", sa.JSON(), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_tracks_artist", "tracks", ["artist"])
    op.create_index("ix_tracks_popularity", "tracks", ["popularity"])

    op.create_table(
        "album_track_map",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("album_source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("album_sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("track_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("album_source_id", "track_id", name="uq_album_track"),
    )

    op.create_table(
        "playlist_account_map",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("playlist_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("spotify_playlist_id", sa.String(length=128), nullable=True),
        sa.Column("spotify_external_url", sa.String(length=2048), nullable=True),
        sa.Column("status", sa.Enum("pending", "syncing", "synced", "error", "archived", name="playlistaccountstatus"), nullable=False, server_default="pending"),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.UniqueConstraint("playlist_id", "account_id", name="uq_playlist_account"),
    )

    op.create_table(
        "playlist_entries_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("playlist_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False),
        sa.Column("track_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("batch_tag", sa.String(length=64), nullable=False),
    )
    op.create_index("ix_playlist_history_playlist_added", "playlist_entries_history", ["playlist_id", "added_at"])

    op.create_table(
        "manager_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("stats", sa.JSON(), nullable=False),
        sa.Column("actions", sa.JSON(), nullable=False),
        sa.Column("executed", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


    op.execute(
        "CREATE VIEW recent_usage AS "
        "SELECT spotify_track_id, MAX(added_at) AS last_used_at FROM playlist_entries_history peh "
        "JOIN tracks t ON peh.track_id = t.id GROUP BY spotify_track_id"
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS recent_usage")
    op.drop_table("manager_plans")
    op.drop_index("ix_playlist_history_playlist_added", table_name="playlist_entries_history")
    op.drop_table("playlist_entries_history")
    op.drop_table("playlist_account_map")
    op.drop_table("album_track_map")
    op.drop_index("ix_tracks_popularity", table_name="tracks")
    op.drop_index("ix_tracks_artist", table_name="tracks")
    op.drop_table("tracks")
    op.drop_table("playlists")
    op.drop_table("curation_policies")
    op.drop_table("albums")
    op.drop_table("album_sources")
    op.drop_table("accounts")
    op.execute("DROP TYPE IF EXISTS accountstatus")
    op.execute("DROP TYPE IF EXISTS albumsourcestatus")
    op.execute("DROP TYPE IF EXISTS playlistaccountstatus")
