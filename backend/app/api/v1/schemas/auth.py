from __future__ import annotations

from pydantic import BaseModel


class DevLoginRequest(BaseModel):
    username: str
    password: str


class DevLoginResponse(BaseModel):
    message: str


class DevStatusResponse(BaseModel):
    authenticated: bool


class DevLogoutResponse(BaseModel):
    message: str
