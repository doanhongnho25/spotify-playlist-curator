from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AccountRead(BaseModel):
    id: UUID
    display_name: str
    spotify_user_id: str
    prefix: str
    expires_at: datetime
    playlists_count: int
    status: str

    class Config:
        orm_mode = True


class AccountListResponse(BaseModel):
    accounts: List[AccountRead]
    active_account_id: Optional[UUID]


class AccountPrefixUpdateRequest(BaseModel):
    account_id: UUID
    prefix: str = Field(..., min_length=1, max_length=64)


class AccountPrefixUpdateResponse(BaseModel):
    id: UUID
    prefix: str


class AccountSetActiveRequest(BaseModel):
    account_id: Optional[UUID]


class AccountRemoveResponse(BaseModel):
    id: UUID
    status: str


class AccountConnectResponse(BaseModel):
    authorization_url: str
