from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel


class JobInfo(BaseModel):
    name: str
    status: str
    last_run: datetime | None
    next_run: datetime | None
    duration_ms: int | None


class JobListResponse(BaseModel):
    jobs: List[JobInfo]


class JobUpdateRequest(BaseModel):
    name: str
    enabled: bool
