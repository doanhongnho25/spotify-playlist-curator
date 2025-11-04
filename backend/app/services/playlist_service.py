from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Playlist, PlaylistEntryHistory, SpotifyAccount
from app.services.sampler_service import sampler_service
from app.services.spotify_service import spotify_service
from app.utils.naming_utils import build_playlist_name, pick_description, sanitize_prefix
from app.utils.time_utils import add_days, utc_now


class PlaylistCapacityError(Exception):
    pass


class PlaylistService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _ensure_capacity(self, account: SpotifyAccount, count: int) -> None:
        if account.playlists_count + count > self.settings.max_playlists_per_account:
            raise PlaylistCapacityError("Max playlists per account exceeded")

    def _next_index(self, db: Session, account: SpotifyAccount) -> int:
        existing = (
            db.query(func.count(Playlist.id))
            .filter(Playlist.account_id == account.id)
            .scalar()
        )
        return existing or 0

    async def create_playlists(
        self,
        db: Session,
        account: SpotifyAccount,
        count: int,
        prefix: str | None,
        size: int,
        interval_days: int,
        cooldown_days: int,
        artist_cap: int,
    ) -> List[Playlist]:
        self._ensure_capacity(account, count)
        effective_prefix = sanitize_prefix(prefix or account.prefix or self.settings.default_prefix)
        created: List[Playlist] = []
        start_index = self._next_index(db, account)
        now = utc_now()
        for idx in range(count):
            display_index = start_index + idx + 1
            name = build_playlist_name(effective_prefix, display_index)
            description = pick_description(display_index)
            playlist = Playlist(
                name=name,
                prefix=effective_prefix,
                account_id=account.id,
                size=size,
                last_reshuffled_at=now,
                next_reshuffle_at=add_days(now, interval_days),
            )
            db.add(playlist)
            db.flush()

            tracks = sampler_service.select_tracks(db, playlist, size, cooldown_days, artist_cap)
            track_uris = [f"spotify:track:{track.spotify_id}" for track in tracks]
            spotify_payload = await spotify_service.create_playlist(
                account.access_token, account.spotify_user_id, name, description
            )
            playlist.spotify_playlist_id = spotify_payload.get("id")
            playlist.external_url = spotify_payload.get("external_urls", {}).get("spotify")

            if playlist.spotify_playlist_id and track_uris:
                await spotify_service.replace_playlist_items(
                    account.access_token, playlist.spotify_playlist_id, track_uris
                )

            for track in tracks:
                history = PlaylistEntryHistory(
                    playlist_id=playlist.id,
                    track_id=track.id,
                    batch_tag=now.strftime("%Y-%m-%d"),
                    added_at=datetime.utcnow(),
                )
                db.add(history)

            created.append(playlist)

        account.playlists_count += len(created)
        db.commit()
        for playlist in created:
            db.refresh(playlist)
        return created

    async def reshuffle_playlist(
        self,
        db: Session,
        playlist: Playlist,
        account: SpotifyAccount,
        size: int,
        cooldown_days: int,
        artist_cap: int,
        interval_days: int,
    ) -> Playlist:
        tracks = sampler_service.select_tracks(db, playlist, size, cooldown_days, artist_cap)
        track_uris = [f"spotify:track:{track.spotify_id}" for track in tracks]
        if playlist.spotify_playlist_id:
            if track_uris:
                await spotify_service.replace_playlist_items(
                    account.access_token, playlist.spotify_playlist_id, track_uris
                )
            await spotify_service.update_playlist_details(
                account.access_token,
                playlist.spotify_playlist_id,
                playlist.name,
                pick_description(utc_now().day),
            )
        now = utc_now()
        playlist.last_reshuffled_at = now
        playlist.next_reshuffle_at = add_days(now, interval_days)
        for track in tracks:
            db.add(
                PlaylistEntryHistory(
                    playlist_id=playlist.id,
                    track_id=track.id,
                    batch_tag=now.strftime("%Y-%m-%d"),
                    added_at=datetime.utcnow(),
                )
            )
        db.add(playlist)
        db.commit()
        db.refresh(playlist)
        return playlist


playlist_service = PlaylistService()
