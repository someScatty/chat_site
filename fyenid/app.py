import asyncio
import inspect
import os
from pathlib import Path
import sys
from typing import Any, Callable

from fastapi import FastAPI
import fyenid.api.channel
import fyenid.api.messages
import fyenid.api.files
import fyenid.api.config
import fyenid.api.users
import fyenid.api.security
import fyenid.api.logger
import atexit, time, psutil
from contextlib import asynccontextmanager

from fyenid.types.internal import AsyncTask
class ChatApp:
    def __init__(self, base: Path, *, debug: bool = False) -> None:
        self._on_shutdown: list[Callable] = []
        self._registered_tasks: list[AsyncTask] = []
        self._track_setattrs = True
        self._mods_loaded = 0
        
        _start = time.time_ns()

        self.console = fyenid.api.logger.Logger(self)
        self.security = fyenid.api.security.SecurityLib(self)
        self.config = fyenid.api.config.Config(base, self) # type: ignore
        self.config.debug = debug

        if self.config._is_locked():
            if psutil.pid_exists(self.config._lock_pid() or 999999):
                self.console.error(f"Lockfile was found! (PID: {self.config._lock_pid()})")
                sys.exit(1)
            else:
                self.config._unlock()
                self.console.warn(f"Lockfile for non-existant process found, unlocking manually...")
        self.config._lock()

        self.channels = fyenid.api.channel.ChannelSubsystem(self)
        self.messages = fyenid.api.messages.MessageLib(self)
        self.files = fyenid.api.files.FileManager(self)
        self.users = fyenid.api.users.UserManager(self)


        

        _end = time.time_ns()
        _duration = (_end - _start) / 1_000_000

        self.console.success(f"Loaded {self._mods_loaded} modules in {_duration:.2f}ms")
        self.console.success(f"Welcome to {self.config.product_name} {self.config.version}!")
        self.console.bar()
        self.console.newline()
        self._track_setattrs = False


    def _apply_decorators(self, obj):
        for name in dir(obj):
            method = getattr(obj, name)

            if getattr(method, "__on_exit__", False):
                self.on_exit(method)

            if hasattr(method, "__interval__"):
                self.schedule_task(method, getattr(method, "__interval__"))

    def __setattr__(self, name: str, value: Any):
        object.__setattr__(self, name, value)
        if name.startswith("_"):
            return
        if hasattr(self, "console") and self._track_setattrs:
            self._apply_decorators(getattr(self, name))
            self.console.info(f"Loaded: {value.__module__}")
            self._mods_loaded += 1


    def on_exit(self, fn: Callable):
        self._on_shutdown.append(fn)

    
    async def _exit(self):
        for fn in self._on_shutdown:
            _async = inspect.iscoroutinefunction(fn)
            self.console.info(f"Shutting down: {fn.__module__} ({"async" if _async else "sync"} {fn.__name__})")
            if _async:
                await fn()
            else:
                fn()
        self.config._unlock() 

    def schedule_task(self, tsk: Callable, repeat_interval: int = 99999999, *args):
        self._registered_tasks.append(
            AsyncTask(tsk,repeat_interval,args)
        )

    async def tick_tasks(self):
        await asyncio.sleep(0)
        while True:
            if not self._registered_tasks:
                await asyncio.sleep(1)
                continue
            now = time.monotonic()
            minimum_time = min(_.repeat - (now - _.last_ran) for _ in self._registered_tasks)
            for task in self._registered_tasks:
                if (
                    task.active_task is None
                    and now - task.last_ran >= task.repeat
                ):
                    task.active_task = asyncio.create_task(
                        task.fn(*task.args)
                    )

                if task.active_task is not None and task.active_task.done():
                    task.active_task = None

            await asyncio.sleep(minimum_time)


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