from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import accounts, auth, jobs, library, metrics, oauth, playlists, settings

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(oauth.router)
api_router.include_router(accounts.router)
api_router.include_router(playlists.router)
api_router.include_router(library.router)
api_router.include_router(settings.router)
api_router.include_router(metrics.router)
api_router.include_router(jobs.router)
