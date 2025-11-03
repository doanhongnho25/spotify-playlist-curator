from __future__ import annotations

import secrets
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Cookie, HTTPException, Response
from fastapi.responses import JSONResponse, RedirectResponse

from app.core.config import get_settings

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

settings = get_settings()

_state_store: dict[str, bool] = {}
_session_tokens: dict[str, dict[str, str | int | None]] = {}


@router.get("/login")
async def login() -> RedirectResponse:
    state = secrets.token_urlsafe(16)
    _state_store[state] = True
    redirect_uri = f"{settings.public_base_url.rstrip('/')}/api/v1/auth/callback"
    params = {
        "client_id": settings.spotify_client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "playlist-modify-public playlist-modify-private",
        "state": state,
        "show_dialog": "false",
    }
    return RedirectResponse(url=f"https://accounts.spotify.com/authorize?{urlencode(params)}")


@router.get("/callback")
async def callback(code: str, state: str) -> Response:
    if state not in _state_store:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    _state_store.pop(state, None)

    redirect_uri = f"{settings.public_base_url.rstrip('/')}/api/v1/auth/callback"
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
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
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        tokens = token_response.json()

    session_id = secrets.token_urlsafe(32)
    _session_tokens[session_id] = {
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "expires_in": tokens.get("expires_in"),
    }

    response = RedirectResponse(url=settings.public_base_url)
    response.set_cookie(
        key="spotify_session",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=3600,
    )
    return response


@router.get("/status")
async def auth_status(spotify_session: Optional[str] = Cookie(None)) -> dict[str, bool]:
    authenticated = bool(spotify_session and spotify_session in _session_tokens)
    return {"authenticated": authenticated}


@router.post("/logout")
async def logout(response: Response, spotify_session: Optional[str] = Cookie(None)) -> JSONResponse:
    if spotify_session and spotify_session in _session_tokens:
        _session_tokens.pop(spotify_session, None)
    response.delete_cookie("spotify_session")
    return JSONResponse({"status": "logged out"})
