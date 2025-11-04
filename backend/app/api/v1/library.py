from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_session
from app.api.v1.accounts import _active_uuid
from app.api.v1.schemas.library import LibraryIngestRequest, LibraryIngestResponse
from app.core.security import DashboardSession
from app.db.models import Album, SpotifyAccount, Track
from app.services.spotify_service import spotify_service

router = APIRouter(prefix="/api/v1/library", tags=["library"])


def _album_id_from_url(url: str) -> str | None:
    if "spotify.com/album/" not in url:
        return None
    segment = url.split("spotify.com/album/")[-1]
    return segment.split("?")[0]


@router.post("/ingest", response_model=LibraryIngestResponse)
async def ingest_albums(
    payload: LibraryIngestRequest,
    session: DashboardSession = Depends(require_session),
    db: Session = Depends(get_db_session),
) -> LibraryIngestResponse:
    account_id = _active_uuid(session)
    if not account_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Select an active account")
    account = db.query(SpotifyAccount).filter(SpotifyAccount.id == account_id).one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active account missing")

    queued = 0
    for url in payload.album_urls:
        album_id = _album_id_from_url(str(url))
        if not album_id:
            continue
        existing = db.query(Album).filter(Album.spotify_id == album_id).one_or_none()
        if existing:
            continue
        tracks = await spotify_service.get_album_tracks(account.access_token, album_id)
        if not tracks:
            continue
        album = Album(
            spotify_id=album_id,
            name=tracks[0].get("album", {}).get("name", "Unknown Album"),
            artist=", ".join(
                artist.get("name") for artist in tracks[0].get("artists", []) if artist.get("name")
            ),
            track_count=len(tracks),
        )
        db.add(album)
        db.flush()
        track_ids: List[str] = []
        for track in tracks:
            track_id = track.get("id")
            if not track_id:
                continue
            track_ids.append(track_id)
            db.add(
                Track(
                    spotify_id=track_id,
                    name=track.get("name", ""),
                    artist=", ".join(artist.get("name") for artist in track.get("artists", []) if artist.get("name")),
                    popularity=track.get("popularity"),
                    album_id=album.id,
                )
            )
        audio_features = await spotify_service.get_audio_features(account.access_token, track_ids)
        for track in db.query(Track).filter(Track.album_id == album.id).all():
            if track.spotify_id in audio_features:
                track.audio_features = audio_features[track.spotify_id]
        queued += 1
    db.commit()
    return LibraryIngestResponse(queued=queued)
