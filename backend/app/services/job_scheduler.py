from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

from app.api.v1.schemas.jobs import JobInfo


class JobScheduler:
    def __init__(self) -> None:
        self._jobs: Dict[str, Dict[str, object]] = {
            "reshuffle_due_playlists": {
                "enabled": True,
                "last_run": None,
                "next_run": datetime.utcnow() + timedelta(hours=1),
                "duration_ms": None,
            },
            "refresh_spotify_tokens": {
                "enabled": True,
                "last_run": None,
                "next_run": datetime.utcnow() + timedelta(hours=6),
                "duration_ms": None,
            },
            "metrics_snapshot": {
                "enabled": True,
                "last_run": None,
                "next_run": datetime.utcnow() + timedelta(hours=1),
                "duration_ms": None,
            },
        }

    def list_jobs(self) -> List[JobInfo]:
        return [
            JobInfo(
                name=name,
                status="enabled" if meta["enabled"] else "disabled",
                last_run=meta["last_run"],
                next_run=meta["next_run"],
                duration_ms=meta["duration_ms"],
            )
            for name, meta in self._jobs.items()
        ]

    def update_job(self, name: str, enabled: bool) -> None:
        if name not in self._jobs:
            raise ValueError(f"Unknown job {name}")
        self._jobs[name]["enabled"] = enabled

    def mark_run(self, name: str, duration_ms: int) -> None:
        if name not in self._jobs:
            return
        meta = self._jobs[name]
        meta["last_run"] = datetime.utcnow()
        meta["duration_ms"] = duration_ms
        meta["next_run"] = datetime.utcnow() + timedelta(hours=1)


job_scheduler = JobScheduler()
