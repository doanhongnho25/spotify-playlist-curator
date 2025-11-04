from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.security import get_optional_dashboard_session
from app.core.session import DashboardSession, dashboard_sessions
from app.schemas.auth import DevAuthResponse, DevLoginRequest, DevStatusResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/dev-login", response_model=DevAuthResponse)
def dev_login(payload: DevLoginRequest) -> JSONResponse:
    settings = get_settings()
    if payload.username != settings.dashboard_username or payload.password != settings.dashboard_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    session = dashboard_sessions.create(username=payload.username)
    response = JSONResponse(DevAuthResponse(authenticated=True).model_dump())
    response.set_cookie(
        key="dashboard_session",
        value=session.session_id,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=12 * 60 * 60,
    )
    return response


@router.get("/dev-status", response_model=DevStatusResponse)
def dev_status(session=Depends(get_optional_dashboard_session)) -> DevStatusResponse:
    if session is None:
        return DevStatusResponse(authenticated=False, active_account_id=None)

    active_id = session.active_account_id
    return DevStatusResponse(
        authenticated=True,
        active_account_id=UUID(active_id) if active_id else None,
    )


@router.post("/dev-logout", response_model=DevAuthResponse)
def dev_logout(
    session: Annotated[DashboardSession | None, Depends(get_optional_dashboard_session)],
) -> JSONResponse:
    if session is not None:
        dashboard_sessions.delete(session.session_id)
    response = JSONResponse(DevAuthResponse(authenticated=False).model_dump())
    response.delete_cookie("dashboard_session")
    return response
