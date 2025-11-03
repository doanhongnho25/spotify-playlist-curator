from __future__ import annotations

from pydantic import BaseModel


class VibeRequest(BaseModel):
    vibe: str


class VibeSong(BaseModel):
    title: str
    artist: str


class VibeResponse(BaseModel):
    songs: list[VibeSong]
