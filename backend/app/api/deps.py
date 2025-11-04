from __future__ import annotations

from typing import Generator

from sqlalchemy.orm import Session

from app.core.security import DashboardSession, require_dashboard_session
from app.db.session import get_db


def get_db_session() -> Generator[Session, None, None]:
    with get_db() as session:
        yield session


def require_session() -> DashboardSession:
    return require_dashboard_session()
