from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import admin_auth_dependency
from app.db.session import get_db
from app.models.tables import Account, AccountStatus
import httpx

from app.schemas.accounts import AccountDeactivateResponse, AccountListResponse, AccountRead
from app.services import spotify

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/accounts", response_model=AccountListResponse)
def list_accounts(
    _: Annotated[None, Depends(admin_auth_dependency)],
    db=Depends(get_db),
):
    accounts = db.query(Account).order_by(Account.created_at.desc()).all()
    items = [
        AccountRead(
            id=account.id,
            spotify_user_id=account.spotify_user_id,
            display_name=account.display_name,
            status=account.status,
            expires_at=account.expires_at,
            created_at=account.created_at,
            updated_at=account.updated_at,
        )
        for account in accounts
    ]
    return AccountListResponse(accounts=items)


@router.get("/connect")
async def initiate_account_connect(
    _: Annotated[None, Depends(admin_auth_dependency)],
):
    authorize_url, state = await spotify.get_admin_authorize_url()
    return {"authorize_url": authorize_url, "state": state, "redirect_uri": spotify.build_admin_redirect_uri()}


@router.post("/accounts/{account_id}/deactivate", response_model=AccountDeactivateResponse)
def deactivate_account(
    account_id: str,
    _: Annotated[None, Depends(admin_auth_dependency)],
    db=Depends(get_db),
):
    account: Account | None = db.query(Account).filter(Account.id == account_id).one_or_none()
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    account.status = AccountStatus.inactive
    account.updated_at = datetime.utcnow()
    db.add(account)
    db.commit()
    db.refresh(account)
    return AccountDeactivateResponse(id=account.id, status=account.status)

@router.get("/callback")
async def admin_callback(code: str, state: str, db=Depends(get_db)):
    if not spotify.validate_state(state):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state")

    redirect_uri = spotify.build_admin_redirect_uri()
    try:
        tokens = await spotify.exchange_code_for_tokens(code=code, redirect_uri=redirect_uri)
    except httpx.HTTPStatusError as exc:  # pragma: no cover - network failure
        spotify.revoke_state(state)
        raise HTTPException(status_code=exc.response.status_code, detail="Failed to exchange code") from exc

    spotify.revoke_state(state)
    profile = await spotify.get_spotify_profile(tokens["access_token"])
    account = spotify.persist_account_from_tokens(db, profile, tokens)
    return {"account_id": str(account.id), "spotify_user_id": account.spotify_user_id}
