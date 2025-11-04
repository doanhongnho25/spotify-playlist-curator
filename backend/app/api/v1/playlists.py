from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_session
from app.api.v1.schemas.playlists import (
    PlaylistBulkReshuffleRequest,
    PlaylistCreateRequest,
    PlaylistCreateResponse,
    PlaylistListResponse,
    PlaylistRead,
    PlaylistReshuffleResponse,
)
from app.core.config import get_settings
from app.core.security import DashboardSession
from app.db.models import Playlist, SpotifyAccount
from app.services.playlist_service import PlaylistCapacityError, playlist_service

router = APIRouter(prefix="/api/v1/playlists", tags=["playlists"])


@router.get("/list", response_model=PlaylistListResponse)
async def list_playlists(
    _: DashboardSession = Depends(require_session),
    db: Session = Depends(get_db_session),
) -> PlaylistListResponse:
    playlists = db.query(Playlist).order_by(Playlist.created_at.desc()).all()
    return PlaylistListResponse(playlists=[PlaylistRead.from_orm(playlist) for playlist in playlists])


@router.post("/create", response_model=PlaylistCreateResponse)
async def create_playlists(
    payload: PlaylistCreateRequest,
    session: DashboardSession = Depends(require_session),
    db: Session = Depends(get_db_session),
) -> PlaylistCreateResponse:
    account = db.query(SpotifyAccount).filter(SpotifyAccount.id == payload.account_id).one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    settings = get_settings()
    try:
        created = await playlist_service.create_playlists(
            db,
            account,
            payload.count,
            payload.prefix,
            payload.size or settings.playlist_size,
            payload.interval_days or settings.reshuffle_interval_days,
            settings.cooldown_days,
            settings.artist_cap,
        )
    except PlaylistCapacityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return PlaylistCreateResponse(created_playlist_ids=[playlist.id for playlist in created])


@router.post("/{playlist_id}/reshuffle", response_model=PlaylistReshuffleResponse)
async def reshuffle_playlist(
    playlist_id: UUID,
    session: DashboardSession = Depends(require_session),
    db: Session = Depends(get_db_session),
) -> PlaylistReshuffleResponse:
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).one_or_none()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")
    account = db.query(SpotifyAccount).filter(SpotifyAccount.id == playlist.account_id).one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account missing")
    settings = get_settings()
    await playlist_service.reshuffle_playlist(
        db,
        playlist,
        account,
        playlist.size or settings.playlist_size,
        settings.cooldown_days,
        settings.artist_cap,
        settings.reshuffle_interval_days,
    )
    return PlaylistReshuffleResponse(id=playlist.id, status="reshuffled")


@router.post("/reshuffle-bulk", response_model=PlaylistCreateResponse)
async def reshuffle_bulk(
    payload: PlaylistBulkReshuffleRequest,
    session: DashboardSession = Depends(require_session),
    db: Session = Depends(get_db_session),
) -> PlaylistCreateResponse:
    settings = get_settings()
    playlists: List[Playlist]
    if payload.mode == "all":
        playlists = db.query(Playlist).all()
    elif payload.mode == "account":
        if not payload.account_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="account_id required")
        playlists = db.query(Playlist).filter(Playlist.account_id == payload.account_id).all()
    else:
        ids = payload.playlist_ids or []
        playlists = db.query(Playlist).filter(Playlist.id.in_(ids)).all()

    reshuffled_ids: List[UUID] = []
    for playlist in playlists:
        account = db.query(SpotifyAccount).filter(SpotifyAccount.id == playlist.account_id).one_or_none()
        if not account:
            continue
        await playlist_service.reshuffle_playlist(
            db,
            playlist,
            account,
            playlist.size or settings.playlist_size,
            settings.cooldown_days,
            settings.artist_cap,
            settings.reshuffle_interval_days,
        )
        reshuffled_ids.append(playlist.id)
    return PlaylistCreateResponse(created_playlist_ids=reshuffled_ids)
