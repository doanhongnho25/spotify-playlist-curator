from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


class TokenCipher:
    def __init__(self) -> None:
        settings = get_settings()
        key = settings.spotify_token_key
        if isinstance(key, str):
            key = key.encode("utf-8")
        self._fernet = Fernet(key)

    def encrypt(self, value: str | None) -> str | None:
        if value is None:
            return None
        token = value.encode("utf-8")
        return self._fernet.encrypt(token).decode("utf-8")

    def decrypt(self, value: str | None) -> str | None:
        if value is None:
            return None
        try:
            token = self._fernet.decrypt(value.encode("utf-8"))
        except InvalidToken as exc:  # pragma: no cover - indicates misconfiguration
            raise ValueError("Invalid encrypted token") from exc
        return token.decode("utf-8")


cipher = TokenCipher()
