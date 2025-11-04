from __future__ import annotations

from typing import List

from pydantic import BaseModel, HttpUrl


class LibraryIngestRequest(BaseModel):
    album_urls: List[HttpUrl]


class LibraryIngestResponse(BaseModel):
    queued: int
