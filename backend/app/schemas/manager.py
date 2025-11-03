from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ManagerPlanResponse(BaseModel):
    created_at: datetime
    stats: dict[str, Any]
    actions: dict[str, Any]
    executed: bool


class ManagerExecuteResponse(BaseModel):
    acknowledged: bool
    plan_id: str
