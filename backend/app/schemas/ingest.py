from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, HttpUrl

from app.models.tables import AlbumSourceStatus


class AlbumSourceBase(BaseModel):
    url: HttpUrl
    owner_tag: Optional[str] = None


class AlbumSourceSubmitRequest(BaseModel):
    urls: list[HttpUrl]
    owner_tag: Optional[str] = None


class AlbumSourceValidateRequest(BaseModel):
    urls: list[HttpUrl]


class AlbumSourceStatusResponse(BaseModel):
    id: UUID
    url: HttpUrl
    status: AlbumSourceStatus
    owner_tag: Optional[str] = None
    queued_at: Optional[datetime] = None
    ingested_at: Optional[datetime] = None
    failure_reason: Optional[str] = None


class AlbumSourceStatusList(BaseModel):
    sources: list[AlbumSourceStatusResponse]
