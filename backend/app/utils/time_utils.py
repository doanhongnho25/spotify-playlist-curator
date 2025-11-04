from __future__ import annotations

from datetime import datetime, timedelta, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def add_days(value: datetime, days: int) -> datetime:
    return value + timedelta(days=days)
