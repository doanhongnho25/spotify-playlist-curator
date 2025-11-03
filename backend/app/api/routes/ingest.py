from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import admin_auth_dependency
from app.db.session import get_db
from app.models.tables import AlbumSource, AlbumSourceStatus
from app.schemas.ingest import (
    AlbumSourceStatusList,
    AlbumSourceStatusResponse,
    AlbumSourceSubmitRequest,
    AlbumSourceValidateRequest,
)

router = APIRouter(prefix="/api/v1/ingest", tags=["ingest"])


def _normalize_url(url: str) -> str:
    return url.strip()


@router.post("/albums/validate", response_model=AlbumSourceStatusList)
def validate_albums(payload: AlbumSourceValidateRequest):
    seen = set()
    valid_urls: list[AlbumSourceStatusResponse] = []
    for url in payload.urls:
        normalized = _normalize_url(str(url))
        if normalized in seen:
            continue
        seen.add(normalized)
        valid_urls.append(
            AlbumSourceStatusResponse(
                id=uuid4(),
                url=normalized,
                status=AlbumSourceStatus.queued,
                owner_tag=None,
                queued_at=None,  # type: ignore[arg-type]
            )
        )
    return AlbumSourceStatusList(sources=valid_urls)


@router.post("/albums/submit", response_model=AlbumSourceStatusList)
def submit_albums_admin(
    payload: AlbumSourceSubmitRequest,
    _: Annotated[None, Depends(admin_auth_dependency)],
    db=Depends(get_db),
):
    if not payload.urls:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No URLs provided")

    records: list[AlbumSource] = []
    for url in payload.urls:
        normalized = _normalize_url(str(url))
        record = db.query(AlbumSource).filter(AlbumSource.url == normalized).one_or_none()
        if record is None:
            record = AlbumSource(url=normalized, owner_tag=payload.owner_tag)
            db.add(record)
        records.append(record)

    db.commit()
    for record in records:
        db.refresh(record)

    return AlbumSourceStatusList(
        sources=[
            AlbumSourceStatusResponse(
                id=record.id,
                url=record.url,
                status=record.status,
                owner_tag=record.owner_tag,
                queued_at=record.queued_at,
                ingested_at=record.ingested_at,
                failure_reason=record.failure_reason,
            )
            for record in records
        ]
    )


@router.post("/albums/submit-one", response_model=AlbumSourceStatusResponse)
def submit_album_public(payload: AlbumSourceValidateRequest, db=Depends(get_db)):
    if len(payload.urls) != 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Exactly one URL required")
    url = _normalize_url(str(payload.urls[0]))
    record = db.query(AlbumSource).filter(AlbumSource.url == url).one_or_none()
    if record is None:
        record = AlbumSource(url=url)
        db.add(record)
        db.commit()
        db.refresh(record)

    return AlbumSourceStatusResponse(
        id=record.id,
        url=record.url,
        status=record.status,
        owner_tag=record.owner_tag,
        queued_at=record.queued_at,
        ingested_at=record.ingested_at,
        failure_reason=record.failure_reason,
    )


@router.get("/status", response_model=AlbumSourceStatusList)
def ingest_status(db=Depends(get_db)):
    records = db.query(AlbumSource).order_by(AlbumSource.queued_at.desc()).limit(100).all()
    return AlbumSourceStatusList(
        sources=[
            AlbumSourceStatusResponse(
                id=record.id,
                url=record.url,
                status=record.status,
                owner_tag=record.owner_tag,
                queued_at=record.queued_at,
                ingested_at=record.ingested_at,
                failure_reason=record.failure_reason,
            )
            for record in records
        ]
    )
