from pathlib import Path
from typing import Callable

import chatify.api.channel
import chatify.api.messages
import chatify.api.files
import chatify.api.config
import chatify.api.users
import chatify.api.security
import atexit
class ChatApp:
    def __init__(self, base: Path) -> None:
        self._on_shutdown: list[Callable] = []


        self.channels = chatify.api.channel.ChannelSubsystem(self)
        self.messages = chatify.api.messages.MessageLib(self)
        self.files = chatify.api.files.FileManager(self)
        self.config = chatify.api.config.Config(base, self)
        self.users = chatify.api.users.UserManager(self)
        self.security = chatify.api.security.SecurityLib(self)


        #internals
        atexit.register(self._exit)

    def on_exit(self, fn: Callable):
        self._on_shutdown.append(fn)

    
    def _exit(self):
        for fn in self._on_shutdown:
            print(f"Shutting down: {fn.__module__} ({fn.__name__})")
            fn()