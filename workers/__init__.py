from __future__ import annotations

from celery import Celery

from app.core.config import get_settings

settings = get_settings()
celery_app = Celery(
    "vibe_workers",
    broker=settings.redis_url,
    backend=settings.redis_url,
)
celery_app.conf.update(
    timezone="UTC",
    beat_schedule={
        "scale-daily": {
            "task": "scale_playlists_daily",
            "schedule": 60 * 60 * 24,
        },
        "refresh-tokens": {
            "task": "refresh_tokens",
            "schedule": 60 * 30,
        },
        "metrics-hourly": {
            "task": "metrics_snapshot",
            "schedule": 60 * 60,
        },
    },
)
