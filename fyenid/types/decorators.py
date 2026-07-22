from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar, cast


P = ParamSpec("P")
T = TypeVar("T")


SyncFunc = Callable[P, T]
AsyncFunc = Callable[P, Awaitable[T]]


def on_exit(
    func: SyncFunc[P, T] | AsyncFunc[P, T],
) -> SyncFunc[P, T] | AsyncFunc[P, T]:
    setattr(func, "__on_exit__", True)
    return func


def on_interval(seconds: float):
    def decorator(
        func: AsyncFunc[P, T],
    ) -> AsyncFunc[P, T]:
        setattr(func, "__interval__", seconds)
        return func

    return decorator