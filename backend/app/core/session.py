from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional

SESSION_TTL_SECONDS = 60 * 60 * 12  # 12 hours


@dataclass
class DashboardSession:
    session_id: str
    username: str
    created_at: datetime
    last_seen: datetime = field(default_factory=datetime.utcnow)
    active_account_id: Optional[str] = None

    def touch(self) -> None:
        self.last_seen = datetime.utcnow()


class DashboardSessionStore:
    def __init__(self) -> None:
        self._sessions: Dict[str, DashboardSession] = {}

    def _is_expired(self, session: DashboardSession) -> bool:
        return datetime.utcnow() - session.last_seen > timedelta(seconds=SESSION_TTL_SECONDS)

    def _cleanup(self) -> None:
        expired = [key for key, value in self._sessions.items() if self._is_expired(value)]
        for key in expired:
            self._sessions.pop(key, None)

    def create(self, username: str) -> DashboardSession:
        self._cleanup()
        session_id = secrets.token_urlsafe(32)
        session = DashboardSession(session_id=session_id, username=username, created_at=datetime.utcnow())
        self._sessions[session_id] = session
        return session

    def get(self, session_id: str) -> Optional[DashboardSession]:
        self._cleanup()
        session = self._sessions.get(session_id)
        if session is None:
            return None
        if self._is_expired(session):
            self._sessions.pop(session_id, None)
            return None
        session.touch()
        return session

    def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def set_active_account(self, session_id: str, account_id: Optional[str]) -> Optional[DashboardSession]:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        session.active_account_id = account_id
        session.touch()
        return session

    def clear_active_for_account(self, account_id: str) -> None:
        for session in self._sessions.values():
            if session.active_account_id == account_id:
                session.active_account_id = None


dashboard_sessions = DashboardSessionStore()
