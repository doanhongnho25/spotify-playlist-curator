from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_session
from app.api.v1.accounts import pop_state
from app.core.config import get_settings
from app.core.security import DashboardSession, session_store
from app.db.models import SpotifyAccount
from app.services.spotify_service import spotify_service

router = APIRouter(prefix="/api/v1/oauth", tags=["oauth"])


@router.get("/spotify/callback")
async def spotify_callback(
    code: str = Query(...),
    state: str = Query(...),
    session: DashboardSession = Depends(require_session),
    db: Session = Depends(get_db_session),
) -> dict[str, str]:
    if not pop_state(state):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state")
    token_payload = await spotify_service.exchange_code(code)
    access_token = token_payload.get("access_token")
    refresh_token = token_payload.get("refresh_token")
    expires_at = token_payload.get("expires_at")
    if not access_token or not refresh_token or not expires_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token payload")
    me = await spotify_service.get_current_user(access_token)
    spotify_user_id = me.get("id")
    display_name = me.get("display_name") or me.get("id")
    if not spotify_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Spotify user id")

    account = db.query(SpotifyAccount).filter(SpotifyAccount.spotify_user_id == spotify_user_id).one_or_none()
    if account:
        account.access_token = access_token
        account.refresh_token = refresh_token
        account.expires_at = expires_at
        account.status = "active"
        account.display_name = display_name
    else:
        account = SpotifyAccount(
            spotify_user_id=spotify_user_id,
            display_name=display_name,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            prefix=get_settings().default_prefix,
        )
        db.add(account)
    db.commit()
    db.refresh(account)
    session_store.set_active_account(session.session_id, str(account.id))
    return {"status": "connected"}
