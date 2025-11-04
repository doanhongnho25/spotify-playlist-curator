from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import get_settings
from app.core.security import require_dashboard_session
from app.db.session import get_db
from app.models.tables import ManagerPlan
from app.schemas.manager import ManagerExecuteResponse, ManagerPlanResponse

router = APIRouter(prefix="/api/v1/manager", tags=["manager"])


@router.get("/plan", response_model=ManagerPlanResponse)
def get_plan(
    _: Annotated[None, Depends(require_dashboard_session)],
    db=Depends(get_db),
):
    latest_plan: ManagerPlan | None = (
        db.query(ManagerPlan)
        .order_by(ManagerPlan.created_at.desc())
        .first()
    )
    if latest_plan is None:
        stats = {
            "message": "No plans generated yet",
            "tracks_per_playlist": get_settings().tracks_per_playlist,
        }
        actions = {"tasks": []}
        latest_plan = ManagerPlan(stats=stats, actions=actions, executed=False)
        db.add(latest_plan)
        db.commit()
        db.refresh(latest_plan)
    return ManagerPlanResponse(
        created_at=latest_plan.created_at,
        stats=latest_plan.stats,
        actions=latest_plan.actions,
        executed=latest_plan.executed,
    )


@router.post("/execute", response_model=ManagerExecuteResponse)
def execute_plan(
    _: Annotated[None, Depends(require_dashboard_session)],
    db=Depends(get_db),
):
    plan = ManagerPlan(stats={"executed_at": datetime.utcnow().isoformat()}, actions={"applied": True}, executed=True)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return ManagerExecuteResponse(acknowledged=True, plan_id=str(plan.id))
