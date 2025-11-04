from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DevLoginRequest(BaseModel):
    username: str
    password: str


class DevAuthResponse(BaseModel):
    authenticated: bool


class DevStatusResponse(BaseModel):
    authenticated: bool
    active_account_id: Optional[UUID] = None
