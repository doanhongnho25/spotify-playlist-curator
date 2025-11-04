from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func

from app.core.security import require_dashboard_session
from app.db.session import get_db
from app.models.tables import CurationPolicy, Playlist
from app.schemas.playlists import (
    PlaylistPublicListing,
    PlaylistPublicListingResponse,
    PlaylistSyncResponse,
    PlaylistTemplateRequest,
)

router = APIRouter(tags=["playlists"])


def _next_global_index(db) -> int:
    current_max = db.query(func.max(Playlist.global_index)).scalar()
    return (current_max or 0) + 1


@router.post("/api/v1/playlists/templates", response_model=PlaylistSyncResponse)
def create_playlist_template(
    payload: PlaylistTemplateRequest,
    _: Annotated[None, Depends(require_dashboard_session)],
    db=Depends(get_db),
):
    policy: CurationPolicy | None = db.query(CurationPolicy).filter(CurationPolicy.id == payload.policy_id).one_or_none()
    if policy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")

    playlist = Playlist(
        name=payload.name,
        description=payload.description,
        policy_id=policy.id,
        theme_tag=policy.name,
        global_index=_next_global_index(db),
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)

    return PlaylistSyncResponse(playlist_id=playlist.id, status="created", synced_at=datetime.utcnow())


@router.post("/api/v1/playlists/sync", response_model=PlaylistSyncResponse)
def sync_all_playlists(
    _: Annotated[None, Depends(require_dashboard_session)],
):
    return PlaylistSyncResponse(playlist_id=UUID(int=0), status="queued", synced_at=datetime.utcnow())


@router.post("/api/v1/playlists/{playlist_id}/sync", response_model=PlaylistSyncResponse)
def sync_single_playlist(
    playlist_id: UUID,
    _: Annotated[None, Depends(require_dashboard_session)],
    db=Depends(get_db),
):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).one_or_none()
    if playlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")

    playlist.last_synced_at = datetime.utcnow()
    db.add(playlist)
    db.commit()
    return PlaylistSyncResponse(playlist_id=playlist.id, status="synced", synced_at=playlist.last_synced_at)


@router.get("/api/v1/public/playlists", response_model=PlaylistPublicListingResponse)
def list_public_playlists(db=Depends(get_db)):
    playlists = (
        db.query(Playlist)
        .order_by(Playlist.global_index.asc())
        .all()
    )

    result: list[PlaylistPublicListing] = []
    for playlist in playlists:
        links = [
            {
                "account_id": str(mapping.account_id),
                "url": mapping.spotify_external_url,
                "status": mapping.status.value,
            }
            for mapping in playlist.account_maps
            if mapping.spotify_external_url
        ]
        result.append(
            PlaylistPublicListing(
                playlist_id=playlist.id,
                name=playlist.name,
                theme_tag=playlist.theme_tag,
                last_synced_at=playlist.last_synced_at,
                links=links,
            )
        )

    return PlaylistPublicListingResponse(playlists=result)


@router.get("/api/v1/public/playlists/{playlist_id}", response_model=PlaylistPublicListing)
def get_public_playlist(playlist_id: UUID, db=Depends(get_db)):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).one_or_none()
    if playlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")

    links = [
        {
            "account_id": str(mapping.account_id),
            "url": mapping.spotify_external_url,
            "status": mapping.status.value,
        }
        for mapping in playlist.account_maps
        if mapping.spotify_external_url
    ]
    return PlaylistPublicListing(
        playlist_id=playlist.id,
        name=playlist.name,
        theme_tag=playlist.theme_tag,
        last_synced_at=playlist.last_synced_at,
        links=links,
    )
