from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status

from app.core.session import DashboardSession, dashboard_sessions


def get_optional_dashboard_session(
    dashboard_session: Optional[str] = Cookie(None),
) -> Optional[DashboardSession]:
    if not dashboard_session:
        return None
    return dashboard_sessions.get(dashboard_session)


def require_dashboard_session(
    session: Optional[DashboardSession] = Depends(get_optional_dashboard_session),
) -> DashboardSession:
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Dashboard authentication required",
        )
    return session
