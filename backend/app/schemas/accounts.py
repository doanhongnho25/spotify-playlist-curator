from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.tables import AccountStatus


class AccountBase(BaseModel):
    spotify_user_id: str
    display_name: Optional[str] = None
    status: AccountStatus


class AccountRead(AccountBase):
    id: UUID
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class AccountDeactivateResponse(BaseModel):
    id: UUID
    status: AccountStatus


class AccountListResponse(BaseModel):
    accounts: list[AccountRead]
