from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_session
from app.api.v1.schemas.settings import SettingsPayload, SettingsResponse
from app.core.config import get_settings
from app.core.security import DashboardSession
from app.db.models import Setting

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])

SETTINGS_KEYS = {
    "playlist_size": "playlist_size",
    "reshuffle_interval_days": "reshuffle_interval_days",
    "cooldown_days": "cooldown_days",
    "max_playlists_per_account": "max_playlists_per_account",
    "artist_cap": "artist_cap",
    "default_prefix": "default_prefix",
}


def _load_settings(db: Session) -> SettingsResponse:
    stored = {setting.key: setting.value for setting in db.query(Setting).all()}
    defaults = get_settings()
    payload = {
        "playlist_size": int(stored.get("playlist_size", defaults.playlist_size)),
        "reshuffle_interval_days": int(stored.get("reshuffle_interval_days", defaults.reshuffle_interval_days)),
        "cooldown_days": int(stored.get("cooldown_days", defaults.cooldown_days)),
        "max_playlists_per_account": int(
            stored.get("max_playlists_per_account", defaults.max_playlists_per_account)
        ),
        "artist_cap": int(stored.get("artist_cap", defaults.artist_cap)),
        "default_prefix": stored.get("default_prefix", defaults.default_prefix),
    }
    return SettingsResponse(**payload)


@router.get("", response_model=SettingsResponse)
async def get_settings_endpoint(
    _: DashboardSession = Depends(require_session),
    db: Session = Depends(get_db_session),
) -> SettingsResponse:
    return _load_settings(db)


@router.post("", response_model=SettingsResponse)
async def update_settings(
    payload: SettingsPayload,
    _: DashboardSession = Depends(require_session),
    db: Session = Depends(get_db_session),
) -> SettingsResponse:
    for field, key in SETTINGS_KEYS.items():
        value = getattr(payload, field)
        setting = db.query(Setting).filter(Setting.key == key).one_or_none()
        if setting:
            setting.value = str(value)
        else:
            setting = Setting(key=key, value=str(value))
            db.add(setting)
    db.commit()
    return _load_settings(db)
