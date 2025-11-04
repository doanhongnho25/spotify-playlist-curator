from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Dict
from urllib.parse import urlencode, urlparse, urlunparse

import httpx

from app.core.config import get_settings
from app.models.tables import Account, AccountStatus
from app.utils.crypto import cipher

STATE_TTL_SECONDS = 900
_state_store: Dict[str, datetime] = {}


def _cleanup_state() -> None:
    now = datetime.utcnow()
    expired = [key for key, value in _state_store.items() if (now - value).total_seconds() > STATE_TTL_SECONDS]
    for key in expired:
        _state_store.pop(key, None)


def _api_base_url() -> str:
    settings = get_settings()
    parsed = urlparse(str(settings.public_base_url))
    scheme = parsed.scheme or "http"
    host = parsed.hostname or "127.0.0.1"
    netloc = f"{host}:8000"
    return urlunparse((scheme, netloc, "", "", "", ""))


def build_redirect_uri() -> str:
    return f"{_api_base_url().rstrip('/')}/api/v1/oauth/spotify/callback"


def generate_state() -> str:
    _cleanup_state()
    state = secrets.token_urlsafe(16)
    _state_store[state] = datetime.utcnow()
    return state


def validate_state(state: str) -> bool:
    _cleanup_state()
    return state in _state_store


def revoke_state(state: str) -> None:
    _state_store.pop(state, None)


async def get_authorize_url() -> tuple[str, str]:
    settings = get_settings()
    redirect_uri = build_redirect_uri()
    params = {
        "client_id": settings.spotify_client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "playlist-modify-public playlist-modify-private",
        "state": generate_state(),
        "show_dialog": "false",
    }
    state = params["state"]
    return "https://accounts.spotify.com/authorize?" + urlencode(params), state


async def exchange_code_for_tokens(code: str, redirect_uri: str) -> dict:
    settings = get_settings()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": settings.spotify_client_id,
                "client_secret": settings.spotify_client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json()


async def get_spotify_profile(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.spotify.com/v1/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()


def persist_account_from_tokens(db, profile: dict, tokens: dict) -> Account:
    account: Account | None = db.query(Account).filter(Account.spotify_user_id == profile["id"]).one_or_none()
    expires_in = tokens.get("expires_in")
    expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in or 3600))
    encrypted_access = cipher.encrypt(tokens["access_token"])
    encrypted_refresh = cipher.encrypt(tokens.get("refresh_token"))

    if account is None:
        account = Account(
            spotify_user_id=profile["id"],
            display_name=profile.get("display_name"),
            access_token_encrypted=encrypted_access,
            refresh_token_encrypted=encrypted_refresh,
            expires_at=expires_at,
            status=AccountStatus.active,
        )
        db.add(account)
    else:
        account.display_name = profile.get("display_name")
        account.access_token_encrypted = encrypted_access
        account.refresh_token_encrypted = encrypted_refresh
        account.expires_at = expires_at
        account.status = AccountStatus.active

    db.commit()
    db.refresh(account)
    return account
