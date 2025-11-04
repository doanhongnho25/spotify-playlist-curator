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


class AccountListResponse(BaseModel):
    accounts: list[AccountRead]
    active_account_id: Optional[UUID] = None


class AccountRemoveRequest(BaseModel):
    account_id: UUID


class AccountRemoveResponse(BaseModel):
    id: UUID
    status: AccountStatus


class ActiveAccountResponse(BaseModel):
    active_account_id: Optional[UUID]


class ActiveAccountSetRequest(BaseModel):
    account_id: Optional[UUID]
