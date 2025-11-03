from fastapi import Depends, Header, HTTPException, status

from app.core.config import get_settings


def verify_admin_api_key(x_admin_api_key: str = Header(..., alias="X-ADMIN-API-KEY")) -> None:
    settings = get_settings()
    if x_admin_api_key != settings.admin_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin API key")


def admin_auth_dependency(_: None = Depends(verify_admin_api_key)) -> None:
    return None
