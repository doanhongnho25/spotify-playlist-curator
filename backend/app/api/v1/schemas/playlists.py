from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PlaylistRead(BaseModel):
    id: UUID
    name: str
    account_id: UUID
    prefix: str
    size: int
    last_reshuffled_at: Optional[datetime]
    next_reshuffle_at: Optional[datetime]
    external_url: Optional[str]

    class Config:
        orm_mode = True


class PlaylistListResponse(BaseModel):
    playlists: List[PlaylistRead]


class PlaylistCreateRequest(BaseModel):
    account_id: UUID
    count: int = Field(..., gt=0, le=500)
    prefix: Optional[str]
    size: Optional[int]
    interval_days: Optional[int]


class PlaylistCreateResponse(BaseModel):
    created_playlist_ids: List[UUID]


class PlaylistReshuffleResponse(BaseModel):
    id: UUID
    status: str


class PlaylistBulkReshuffleRequest(BaseModel):
    mode: str = Field(..., regex="^(all|account|selected)$")
    account_id: Optional[UUID]
    playlist_ids: Optional[List[UUID]]
