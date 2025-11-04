from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import require_dashboard_session
from app.core.session import dashboard_sessions
from app.db.session import get_db
from app.models.tables import Account, AccountStatus
from app.schemas.accounts import (
    AccountListResponse,
    AccountRead,
    AccountRemoveRequest,
    AccountRemoveResponse,
    ActiveAccountResponse,
    ActiveAccountSetRequest,
)

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])


@router.get("/list", response_model=AccountListResponse)
def list_accounts(
    session=Depends(require_dashboard_session),
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

    active_id = session.active_account_id
    return AccountListResponse(
        accounts=items,
        active_account_id=UUID(active_id) if active_id else None,
    )


@router.post("/remove", response_model=AccountRemoveResponse)
def remove_account(
    payload: AccountRemoveRequest,
    session=Depends(require_dashboard_session),
    db=Depends(get_db),
):
    account: Account | None = db.query(Account).filter(Account.id == payload.account_id).one_or_none()
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    account.status = AccountStatus.inactive
    db.add(account)
    db.commit()
    db.refresh(account)

    dashboard_sessions.clear_active_for_account(str(account.id))
    if session.active_account_id == str(account.id):
        dashboard_sessions.set_active_account(session.session_id, None)

    return AccountRemoveResponse(id=account.id, status=account.status)


@router.get("/active/get", response_model=ActiveAccountResponse)
def get_active_account(session=Depends(require_dashboard_session)):
    active_id = session.active_account_id
    return ActiveAccountResponse(active_account_id=UUID(active_id) if active_id else None)


@router.post("/active/set", response_model=ActiveAccountResponse)
def set_active_account(
    payload: ActiveAccountSetRequest,
    session=Depends(require_dashboard_session),
    db=Depends(get_db),
):
    if payload.account_id is None:
        dashboard_sessions.set_active_account(session.session_id, None)
        return ActiveAccountResponse(active_account_id=None)

    account: Account | None = db.query(Account).filter(Account.id == payload.account_id).one_or_none()
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    if account.status != AccountStatus.active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account inactive")

    dashboard_sessions.set_active_account(session.session_id, str(account.id))
    return ActiveAccountResponse(active_account_id=account.id)
