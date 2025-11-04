from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.api.deps import require_session
from app.api.v1.schemas.auth import (
    DevLoginRequest,
    DevLoginResponse,
    DevLogoutResponse,
    DevStatusResponse,
)
from app.core.config import get_settings
from app.core.security import DashboardSession, destroy_dashboard_session, issue_dashboard_session

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/dev-login", response_model=DevLoginResponse)
async def dev_login(payload: DevLoginRequest, response: Response) -> DevLoginResponse:
    settings = get_settings()
    if (
        payload.username != settings.dashboard_username
        or payload.password != settings.dashboard_password
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    issue_dashboard_session(response)
    return DevLoginResponse(message="logged_in")


@router.get("/dev-status", response_model=DevStatusResponse)
async def dev_status(_: DashboardSession = Depends(require_session)) -> DevStatusResponse:
    return DevStatusResponse(authenticated=True)


@router.post("/dev-logout", response_model=DevLogoutResponse)
async def dev_logout(request: Request, response: Response) -> DevLogoutResponse:
    settings = get_settings()
    cookie_value = request.cookies.get(settings.cookie_name)
    destroy_dashboard_session(response, cookie_value)
    return DevLogoutResponse(message="logged_out")
