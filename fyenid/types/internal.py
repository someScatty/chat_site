import asyncio
from dataclasses import dataclass
from typing import Any, Callable

@dataclass(slots=True)
class AsyncTask:
    fn: Callable
    repeat: int = -1
    args: tuple[Any, ...] = ()
    active_task: asyncio.Task | None = None
    last_ran: int = 0