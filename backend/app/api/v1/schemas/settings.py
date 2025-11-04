from __future__ import annotations

from pydantic import BaseModel, Field


class SettingsPayload(BaseModel):
    playlist_size: int = Field(..., gt=0, le=200)
    reshuffle_interval_days: int = Field(..., gt=0, le=30)
    cooldown_days: int = Field(..., ge=0, le=30)
    max_playlists_per_account: int = Field(..., gt=0, le=1000)
    artist_cap: int = Field(..., gt=0, le=10)
    default_prefix: str = Field(..., min_length=1, max_length=64)


class SettingsResponse(SettingsPayload):
    pass
