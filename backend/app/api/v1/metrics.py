from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_session
from app.api.v1.schemas.metrics import MetricOverview, MetricsHistoryResponse
from app.core.security import DashboardSession
from app.services.metrics_service import metrics_service

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])


@router.get("/overview", response_model=MetricOverview)
async def metrics_overview(
    _: DashboardSession = Depends(require_session),
    db: Session = Depends(get_db_session),
) -> MetricOverview:
    return metrics_service.get_overview(db)


@router.get("/history", response_model=MetricsHistoryResponse)
async def metrics_history(
    _: DashboardSession = Depends(require_session),
    db: Session = Depends(get_db_session),
) -> MetricsHistoryResponse:
    return MetricsHistoryResponse(history=metrics_service.get_history(db))
