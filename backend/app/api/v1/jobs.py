from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_session
from app.api.v1.schemas.jobs import JobListResponse, JobUpdateRequest
from app.core.security import DashboardSession
from app.services.job_scheduler import job_scheduler

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.get("/list", response_model=JobListResponse)
async def list_jobs(_: DashboardSession = Depends(require_session)) -> JobListResponse:
    return JobListResponse(jobs=job_scheduler.list_jobs())


@router.post("/update", response_model=JobListResponse)
async def update_job(
    payload: JobUpdateRequest,
    _: DashboardSession = Depends(require_session),
) -> JobListResponse:
    try:
        job_scheduler.update_job(payload.name, payload.enabled)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return JobListResponse(jobs=job_scheduler.list_jobs())
