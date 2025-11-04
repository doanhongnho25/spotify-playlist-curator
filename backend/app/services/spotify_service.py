from __future__ import annotations

import base64
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List

import httpx

from app.core.config import get_settings


class SpotifyAuthError(Exception):
    pass


class SpotifyService:
    API_BASE = "https://api.spotify.com/v1"
    AUTH_BASE = "https://accounts.spotify.com"

    def __init__(self) -> None:
        self.settings = get_settings()

    def _client_credentials(self) -> str:
        raw = f"{self.settings.spotify_client_id}:{self.settings.spotify_client_secret}"
        return base64.b64encode(raw.encode()).decode()

    async def generate_authorize_url(self, state: str) -> str:
        scope = "playlist-modify-public playlist-modify-private user-read-email"
        params = {
            "client_id": self.settings.spotify_client_id,
            "response_type": "code",
            "redirect_uri": str(self.settings.spotify_redirect_uri),
            "scope": scope,
            "state": state,
            "show_dialog": "true",
        }
        query = httpx.QueryParams(params)
        return f"{self.AUTH_BASE}/authorize?{query}"

    async def exchange_code(self, code: str) -> Dict[str, Any]:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": str(self.settings.spotify_redirect_uri),
        }
        headers = {"Authorization": f"Basic {self._client_credentials()}"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.AUTH_BASE}/api/token", data=data, headers=headers, timeout=30.0)
        resp.raise_for_status()
        payload = resp.json()
        payload["expires_at"] = datetime.utcnow() + timedelta(seconds=payload.get("expires_in", 3600))
        return payload

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        headers = {"Authorization": f"Basic {self._client_credentials()}"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.AUTH_BASE}/api/token", data=data, headers=headers, timeout=30.0)
        resp.raise_for_status()
        payload = resp.json()
        payload["expires_at"] = datetime.utcnow() + timedelta(seconds=payload.get("expires_in", 3600))
        payload.setdefault("refresh_token", refresh_token)
        return payload

    async def get_current_user(self, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.API_BASE}/me", headers=headers, timeout=30.0)
        resp.raise_for_status()
        return resp.json()

    async def create_playlist(
        self, access_token: str, user_id: str, name: str, description: str
    ) -> Dict[str, Any]:
        payload = {"name": name, "description": description, "public": True}
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.API_BASE}/users/{user_id}/playlists", json=payload, headers=headers, timeout=30.0
            )
        resp.raise_for_status()
        return resp.json()

    async def update_playlist_details(
        self, access_token: str, playlist_id: str, name: str, description: str
    ) -> None:
        payload = {"name": name, "description": description, "public": True}
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{self.API_BASE}/playlists/{playlist_id}", json=payload, headers=headers, timeout=30.0
            )
        resp.raise_for_status()

    async def replace_playlist_items(self, access_token: str, playlist_id: str, track_uris: List[str]) -> None:
        headers = {"Authorization": f"Bearer {access_token}"}
        chunks = [track_uris[i : i + 100] for i in range(0, len(track_uris), 100)]
        if not chunks:
            return
        async with httpx.AsyncClient() as client:
            first = chunks[0]
            resp = await client.put(
                f"{self.API_BASE}/playlists/{playlist_id}/tracks",
                json={"uris": first},
                headers=headers,
                timeout=30.0,
            )
            resp.raise_for_status()
            for chunk in chunks[1:]:
                resp = await client.post(
                    f"{self.API_BASE}/playlists/{playlist_id}/tracks",
                    json={"uris": chunk},
                    headers=headers,
                    timeout=30.0,
                )
                resp.raise_for_status()

    async def get_album_tracks(self, access_token: str, album_id: str) -> List[Dict[str, Any]]:
        headers = {"Authorization": f"Bearer {access_token}"}
        tracks: List[Dict[str, Any]] = []
        params = {"limit": 50}
        async with httpx.AsyncClient() as client:
            url = f"{self.API_BASE}/albums/{album_id}/tracks"
            while url:
                resp = await client.get(url, params=params, headers=headers, timeout=30.0)
                resp.raise_for_status()
                data = resp.json()
                tracks.extend(data.get("items", []))
                url = data.get("next")
                params = None
        return tracks

    async def get_audio_features(self, access_token: str, track_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        headers = {"Authorization": f"Bearer {access_token}"}
        results: Dict[str, Dict[str, Any]] = {}
        async with httpx.AsyncClient() as client:
            for chunk in [track_ids[i : i + 100] for i in range(0, len(track_ids), 100)]:
                if not chunk:
                    continue
                params = {"ids": ",".join(chunk)}
                resp = await client.get(
                    f"{self.API_BASE}/audio-features", params=params, headers=headers, timeout=30.0
                )
                resp.raise_for_status()
                for feature in resp.json().get("audio_features", []):
                    if feature:
                        results[feature["id"]] = feature
        return results

    @staticmethod
    def build_state() -> str:
        return secrets.token_urlsafe(16)


spotify_service = SpotifyService()
