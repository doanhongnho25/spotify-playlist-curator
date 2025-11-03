from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

import google.generativeai as genai

from app.core.config import get_settings
from app.schemas.generation import VibeRequest, VibeResponse, VibeSong

router = APIRouter(prefix="/api/v1", tags=["vibe"])

settings = get_settings()
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)


@router.post("/playlist/generate", response_model=VibeResponse)
async def generate_playlist(request: VibeRequest) -> VibeResponse:
    if not settings.gemini_api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")

    prompt = f"""Generate a playlist of exactly 10 songs that match this vibe: \"{request.vibe}\"\n\nReturn ONLY a JSON array with this exact format, no other text:\n[\n  {{\"title\": \"Song Name\", \"artist\": \"Artist Name\"}},\n  ...\n]\n\nMake sure the songs are real, popular songs that match the vibe. Be creative and diverse in your selections."""

    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    response = model.generate_content(prompt)
    response_text = response.text.strip()

    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]

    try:
        songs_raw = json.loads(response_text)
    except json.JSONDecodeError as exc:  # pragma: no cover - external response variability
        raise HTTPException(status_code=500, detail="Failed to parse Gemini response") from exc

    songs = [VibeSong(**song) for song in songs_raw]
    return VibeResponse(songs=songs)
