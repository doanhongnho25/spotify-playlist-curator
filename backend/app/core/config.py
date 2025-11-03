from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field, AnyHttpUrl, field_validator


class Settings(BaseSettings):
    app_name: str = Field(default="Vibe API")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(..., env="REDIS_URL")
    spotify_client_id: str = Field(..., env="SPOTIFY_CLIENT_ID")
    spotify_client_secret: str = Field(..., env="SPOTIFY_CLIENT_SECRET")
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    admin_api_key: str = Field(..., env="ADMIN_API_KEY")
    spotify_token_key: str = Field(..., env="SPOTIFY_TOKEN_KEY")
    allowed_origins: List[AnyHttpUrl] = Field(default_factory=list, env="ALLOWED_ORIGINS")
    public_base_url: AnyHttpUrl = Field(..., env="PUBLIC_BASE_URL")

    tracks_per_playlist: int = Field(default=50, env="TRACKS_PER_PLAYLIST")
    min_repeat_gap_days: int = Field(default=10, env="MIN_REPEAT_GAP_DAYS")
    max_playlists_per_account: int = Field(default=50, env="MAX_PLAYLISTS_PER_ACCOUNT")
    target_accounts: int = Field(default=8, env="TARGET_ACCOUNTS")
    floor_total_playlists: int = Field(default=40, env="FLOOR_TOTAL_PLAYLISTS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, list):
            return value
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
