# Database Overview

The FastAPI service uses SQLAlchemy models defined in `backend/app/db/models/`. Key tables:

## `spotify_accounts`
- `id` (UUID)
- `display_name`
- `spotify_user_id` (unique)
- `prefix` (naming prefix for playlists)
- `access_token`, `refresh_token`, `expires_at`
- `playlists_count` (tracks created playlists per account)
- `status` (`active`, `inactive`, etc.)
- `created_at`, `updated_at`

## `albums`
- `id` (UUID)
- `spotify_id` (unique)
- `name`, `artist`
- `track_count`
- `added_at`

## `tracks`
- `id` (UUID)
- `spotify_id` (unique)
- `name`, `artist`
- `popularity`
- `album_id` → `albums.id`
- `audio_features` (JSON blob)
- `is_usable` flag
- `created_at`

Indexes: `ix_tracks_artist`, `ix_tracks_popularity` support sampler filtering.

## `playlists`
- `id` (UUID)
- `spotify_playlist_id`
- `name`, `prefix`
- `account_id` → `spotify_accounts.id`
- `size`
- `last_reshuffled_at`, `next_reshuffle_at`
- `external_url`
- `created_at`, `updated_at`

## `playlist_entries_history`
- `id` (UUID)
- `playlist_id` → `playlists.id`
- `track_id` → `tracks.id`
- `added_at`
- `batch_tag` (e.g., `YYYY-MM-DD`)

Index: `ix_playlist_entries_history_playlist_added` (`playlist_id`, `added_at desc`).

## `settings`
- `id` (UUID)
- `key` (unique)
- `value`
- `updated_at`

Used to override runtime configuration (playlist size, cooldown, etc.).

## `metric_snapshots`
- `id` (UUID)
- `created_at`
- `accounts_count`, `playlists_count`, `tracks_count`
- `reshuffles_last_24h`
- `avg_tracks_per_playlist`

Populated by worker metrics job to power dashboard charts.

## Migration Strategy

Alembic migration `0001_initial` establishes the schema. Run `alembic upgrade head` (via `make migrate`) after cloning or during deployments. Subsequent schema changes should add new revisions under `backend/alembic/versions/`.
