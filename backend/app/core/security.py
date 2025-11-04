from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, Response, status
from itsdangerous import BadSignature, TimestampSigner

from app.core.config import get_settings


@dataclass
class DashboardSession:
    session_id: str
    created_at: datetime
    active_account_id: Optional[str] = None


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, DashboardSession] = {}

    def create(self) -> DashboardSession:
        session_id = secrets.token_urlsafe(32)
        session = DashboardSession(session_id=session_id, created_at=datetime.utcnow())
        self._sessions[session_id] = session
        return session

    def get(self, session_id: str) -> Optional[DashboardSession]:
        session = self._sessions.get(session_id)
        if not session:
            return None
        settings = get_settings()
        ttl = timedelta(seconds=settings.session_ttl_seconds)
        if session.created_at + ttl < datetime.utcnow():
            self.delete(session_id)
            return None
        return session

    def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def set_active_account(self, session_id: str, account_id: Optional[str]) -> None:
        session = self._sessions.get(session_id)
        if session:
            session.active_account_id = account_id


session_store = SessionStore()


def issue_dashboard_session(response: Response) -> DashboardSession:
    settings = get_settings()
    signer = TimestampSigner(settings.secret_key)
    session = session_store.create()
    signed = signer.sign(session.session_id)
    response.set_cookie(
        settings.cookie_name,
        signed.decode(),
        httponly=True,
        max_age=settings.session_ttl_seconds,
        samesite="lax",
    )
    return session


def destroy_dashboard_session(response: Response, signed_session: str | None) -> None:
    settings = get_settings()
    if not signed_session:
        return
    signer = TimestampSigner(settings.secret_key)
    try:
        raw = signer.unsign(signed_session).decode()
    except BadSignature:
        return
    session_store.delete(raw)
    response.delete_cookie(settings.cookie_name)


_cookie_name = get_settings().cookie_name


def require_dashboard_session(
    dashboard_session: str | None = Cookie(default=None, alias=_cookie_name)
) -> DashboardSession:
    settings = get_settings()
    if not dashboard_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    signer = TimestampSigner(settings.secret_key)
    try:
        raw = signer.unsign(dashboard_session, max_age=settings.session_ttl_seconds).decode()
    except BadSignature as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session") from exc

    session = session_store.get(raw)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    return session


def get_active_account_id(
    session: DashboardSession = Depends(require_dashboard_session),
) -> Optional[str]:
    return session.active_account_id
