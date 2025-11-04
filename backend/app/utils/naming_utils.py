from __future__ import annotations

import re
from typing import Iterable

DEFAULT_DESCRIPTIONS = [
    "A curated blend of sounds from our archive.",
    "Fresh picks from our vault, handpicked for today.",
    "For late nights and clear minds.",
    "An easy mix for your everyday soundtrack.",
    "Handpicked selections from the Vibe Engine library.",
]


def sanitize_prefix(prefix: str) -> str:
    cleaned = prefix.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    banned = {"random", "rotation", "auto", "autoplaylist"}
    parts = [word for word in cleaned.split(" ") if word.lower() not in banned]
    return " ".join(parts) or "Vibe Collection"


def build_playlist_name(prefix: str, index: int) -> str:
    return f"{prefix.strip()} • {index:03d}"


def pick_description(seed: int | None = None) -> str:
    if seed is not None:
        idx = seed % len(DEFAULT_DESCRIPTIONS)
        return DEFAULT_DESCRIPTIONS[idx]
    from random import choice

    return choice(DEFAULT_DESCRIPTIONS)
