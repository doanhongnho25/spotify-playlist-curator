from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel


class MetricOverview(BaseModel):
    accounts: int
    playlists: int
    tracks: int
    reshuffles_scheduled_today: int
    next_reshuffle_at: datetime | None
    system_health: str


class MetricsHistoryPoint(BaseModel):
    timestamp: datetime
    playlists: int
    reshuffles: int


class MetricsHistoryResponse(BaseModel):
    history: List[MetricsHistoryPoint]
