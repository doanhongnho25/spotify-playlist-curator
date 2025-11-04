from fastapi import APIRouter

from . import accounts, auth, ingest, manager, oauth, playlists


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(oauth.router)
api_router.include_router(accounts.router)
api_router.include_router(ingest.router)
api_router.include_router(manager.router)
api_router.include_router(playlists.router)
