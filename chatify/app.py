import asyncio
import inspect
from pathlib import Path
from typing import Callable

from fastapi import FastAPI
import chatify.api.channel
import chatify.api.messages
import chatify.api.files
import chatify.api.config
import chatify.api.users
import chatify.api.security
import atexit, time
from contextlib import asynccontextmanager

from chatify.types.internal import AsyncTask
class ChatApp:
    def __init__(self, base: Path) -> None:
        self._on_shutdown: list[Callable] = []
        self._registered_tasks: list[AsyncTask] = []

        self.security = chatify.api.security.SecurityLib(self)
        self.config = chatify.api.config.Config(base, self) # type: ignore
        self.channels = chatify.api.channel.ChannelSubsystem(self)
        self.messages = chatify.api.messages.MessageLib(self)
        self.files = chatify.api.files.FileManager(self)
        self.users = chatify.api.users.UserManager(self)




    def on_exit(self, fn: Callable):
        self._on_shutdown.append(fn)

    
    async def _exit(self):
        for fn in self._on_shutdown:
            _async = inspect.iscoroutinefunction(fn)
            print(f"Shutting down: {fn.__module__} ({"async" if _async else "sync"} {fn.__name__})")
            if _async:
                await fn()
            else:
                fn() 

    def schedule_task(self, tsk: Callable, repeat_interval: int = 99999999, *args):
        self._registered_tasks.append(
            AsyncTask(tsk,repeat_interval,args)
        )

    async def tick_tasks(self):
        await asyncio.sleep(0)

        while True:
            for task in self._registered_tasks:
                if (
                    task.active_task is None
                    and time.time() - task.last_ran >= task.repeat
                ):
                    task.active_task = asyncio.create_task(
                        task.fn(*task.args)
                    )

                if task.active_task is not None and task.active_task.done():
                    task.active_task = None

            await asyncio.sleep(1)


    @asynccontextmanager
    async def run(self, app):
        task =  asyncio.create_task(self.tick_tasks())
        yield

        await self._exit()
        for task in self._registered_tasks:
            if task.active_task is None:
                continue

            if task.active_task.done():
                continue

            task.active_task.cancel()