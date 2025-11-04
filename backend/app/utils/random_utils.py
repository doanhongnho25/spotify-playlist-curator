from __future__ import annotations

import random
from typing import Iterable, Sequence, TypeVar

T = TypeVar("T")


def pick_many(items: Sequence[T], k: int) -> list[T]:
    if k <= 0:
        return []
    if len(items) <= k:
        return list(items)
    return random.sample(list(items), k)


def shuffle(items: Iterable[T]) -> list[T]:
    pool = list(items)
    random.shuffle(pool)
    return pool
