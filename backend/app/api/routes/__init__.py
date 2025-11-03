from fastapi import APIRouter

from . import admin_accounts, auth, ingest, manager, playlists, vibe


api_router = APIRouter()
api_router.include_router(admin_accounts.router)
api_router.include_router(auth.router)
api_router.include_router(ingest.router)
api_router.include_router(manager.router)
api_router.include_router(playlists.router)
api_router.include_router(vibe.router)
