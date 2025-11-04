from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PlaylistTemplateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    policy_id: UUID


class PlaylistSyncResponse(BaseModel):
    playlist_id: UUID
    status: str
    synced_at: datetime


class PlaylistPublicListing(BaseModel):
    playlist_id: UUID
    name: str
    theme_tag: Optional[str]
    last_synced_at: Optional[datetime]
    links: list[dict]


class PlaylistPublicListingResponse(BaseModel):
    playlists: list[PlaylistPublicListing]
