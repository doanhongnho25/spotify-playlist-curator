from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, BaseSettings, Field, validator


class Settings(BaseSettings):
    app_name: str = Field("Vibe Engine API", env="APP_NAME")
    environment: str = Field("development", env="ENVIRONMENT")
    secret_key: str = Field(..., env="SECRET_KEY")

    dashboard_username: str = Field("admin", env="DASHBOARD_USERNAME")
    dashboard_password: str = Field("admin", env="DASHBOARD_PASSWORD")

    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(..., env="REDIS_URL")

    spotify_client_id: str = Field(..., env="SPOTIFY_CLIENT_ID")
    spotify_client_secret: str = Field(..., env="SPOTIFY_CLIENT_SECRET")
    spotify_redirect_uri: AnyHttpUrl = Field(
        "http://127.0.0.1:8000/api/v1/oauth/spotify/callback",
        env="SPOTIFY_REDIRECT_URI",
    )

    default_prefix: str = Field("Vibe Collection", env="DEFAULT_PREFIX")
    playlist_size: int = Field(50, env="TRACKS_PER_PLAYLIST")
    reshuffle_interval_days: int = Field(5, env="RESHUFFLE_INTERVAL_DAYS")
    cooldown_days: int = Field(5, env="MIN_REPEAT_GAP_DAYS")
    max_playlists_per_account: int = Field(200, env="MAX_PLAYLISTS_PER_ACCOUNT")
    artist_cap: int = Field(2, env="ARTIST_CAP")

    allowed_origins: List[AnyHttpUrl] | str | None = Field(
        "http://127.0.0.1:3000",
        env="ALLOWED_ORIGINS",
    )

    cookie_name: str = Field("dashboard_session", env="COOKIE_NAME")
    session_ttl_seconds: int = Field(60 * 60 * 12, env="SESSION_TTL_SECONDS")

    class Config:
        env_file = ".env"
        case_sensitive = True

    @validator("allowed_origins", pre=True)
    def split_origins(
        cls, value: List[AnyHttpUrl] | str | None
    ) -> Optional[List[AnyHttpUrl]]:
        if not value:
            return None
        if isinstance(value, list):
            return value
        return [origin.strip() for origin in value.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
