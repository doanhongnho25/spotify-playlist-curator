from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_session
from app.api.v1.schemas.accounts import (
    AccountConnectResponse,
    AccountListResponse,
    AccountPrefixUpdateRequest,
    AccountPrefixUpdateResponse,
    AccountRead,
    AccountRemoveResponse,
    AccountSetActiveRequest,
)
from app.core.security import DashboardSession, session_store
from app.db.models import SpotifyAccount
from app.services.spotify_service import spotify_service
from app.utils.naming_utils import sanitize_prefix

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])

_state_cache: Dict[str, datetime] = {}


def _active_uuid(session: DashboardSession) -> Optional[UUID]:
    if not session.active_account_id:
        return None
    try:
        return UUID(session.active_account_id)
    except ValueError:
        return None


def _serialize_accounts(accounts: List[SpotifyAccount], session: DashboardSession) -> AccountListResponse:
    return AccountListResponse(
        accounts=[AccountRead.from_orm(account) for account in accounts],
        active_account_id=_active_uuid(session),
    )


@router.get("/list", response_model=AccountListResponse)
async def list_accounts(
    session: DashboardSession = Depends(require_session),
    db: Session = Depends(get_db_session),
) -> AccountListResponse:
    accounts = db.query(SpotifyAccount).order_by(SpotifyAccount.created_at.desc()).all()
    return _serialize_accounts(accounts, session)


@router.post("/active/set", response_model=AccountListResponse)
async def set_active_account(
    payload: AccountSetActiveRequest,
    session: DashboardSession = Depends(require_session),
    db: Session = Depends(get_db_session),
) -> AccountListResponse:
    if payload.account_id is None:
        session_store.set_active_account(session.session_id, None)
    else:
        account = db.query(SpotifyAccount).filter(SpotifyAccount.id == payload.account_id).one_or_none()
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        session_store.set_active_account(session.session_id, str(account.id))
    accounts = db.query(SpotifyAccount).order_by(SpotifyAccount.created_at.desc()).all()
    return _serialize_accounts(accounts, session)


@router.post("/prefix", response_model=AccountPrefixUpdateResponse)
async def update_prefix(
    payload: AccountPrefixUpdateRequest,
    _: DashboardSession = Depends(require_session),
    db: Session = Depends(get_db_session),
) -> AccountPrefixUpdateResponse:
    account = db.query(SpotifyAccount).filter(SpotifyAccount.id == payload.account_id).one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    account.prefix = sanitize_prefix(payload.prefix)
    db.add(account)
    db.commit()
    db.refresh(account)
    return AccountPrefixUpdateResponse(id=account.id, prefix=account.prefix)


@router.delete("/{account_id}", response_model=AccountRemoveResponse)
async def remove_account(
    account_id: UUID,
    session: DashboardSession = Depends(require_session),
    db: Session = Depends(get_db_session),
) -> AccountRemoveResponse:
    account = db.query(SpotifyAccount).filter(SpotifyAccount.id == account_id).one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    account.status = "inactive"
    db.add(account)
    db.commit()
    if session.active_account_id == str(account.id):
        session_store.set_active_account(session.session_id, None)
    return AccountRemoveResponse(id=account.id, status=account.status)


@router.post("/refresh/{account_id}", response_model=AccountRead)
async def refresh_account(
    account_id: UUID,
    _: DashboardSession = Depends(require_session),
    db: Session = Depends(get_db_session),
) -> AccountRead:
    account = db.query(SpotifyAccount).filter(SpotifyAccount.id == account_id).one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    refreshed = await spotify_service.refresh_token(account.refresh_token)
    account.access_token = refreshed.get("access_token", account.access_token)
    account.refresh_token = refreshed.get("refresh_token", account.refresh_token)
    account.expires_at = refreshed.get("expires_at", account.expires_at)
    db.add(account)
    db.commit()
    db.refresh(account)
    return AccountRead.from_orm(account)


@router.get("/connect", response_model=AccountConnectResponse)
async def connect_account(_: DashboardSession = Depends(require_session)) -> AccountConnectResponse:
    state = spotify_service.build_state()
    _state_cache[state] = datetime.utcnow()
    url = await spotify_service.generate_authorize_url(state)
    return AccountConnectResponse(authorization_url=url)


def pop_state(state: str) -> bool:
    timestamp = _state_cache.pop(state, None)
    if not timestamp:
        return False
    return (datetime.utcnow() - timestamp).total_seconds() < 600
