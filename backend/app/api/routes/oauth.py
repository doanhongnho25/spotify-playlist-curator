from __future__ import annotations

from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from app.core.config import get_settings
from app.core.security import get_optional_dashboard_session, require_dashboard_session
from app.core.session import DashboardSession, dashboard_sessions
from app.db.session import get_db
from app.models.tables import Account
from app.services import spotify

router = APIRouter(prefix="/api/v1/oauth/spotify", tags=["oauth"])


@router.get("/connect")
async def start_oauth(session=Depends(require_dashboard_session)):
    authorize_url, state = await spotify.get_authorize_url()
    return {"authorize_url": authorize_url, "state": state, "redirect_uri": spotify.build_redirect_uri()}


@router.get("/callback")
async def oauth_callback(
    code: str,
    state: str,
    session: Annotated[DashboardSession | None, Depends(get_optional_dashboard_session)],
    db=Depends(get_db),
):
    if not spotify.validate_state(state):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state")

    redirect_uri = spotify.build_redirect_uri()
    try:
        tokens = await spotify.exchange_code_for_tokens(code=code, redirect_uri=redirect_uri)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        spotify.revoke_state(state)
        raise HTTPException(status_code=exc.response.status_code, detail="Failed to exchange code") from exc

    spotify.revoke_state(state)
    profile = await spotify.get_spotify_profile(tokens["access_token"])
    account: Account = spotify.persist_account_from_tokens(db, profile, tokens)

    if session is not None:
        dashboard_sessions.set_active_account(session.session_id, str(account.id))

    settings = get_settings()
    return RedirectResponse(url=settings.public_base_url)
