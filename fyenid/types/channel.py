from dataclasses import dataclass
from .core import *
from .message import Message
from typing import NamedTuple

class ChannelMetadata(NamedTuple):
    name: str
    description: str

@dataclass(slots=True)
class Channel:
    metadata: ChannelMetadata
    messages: list[Message]
    id: ChannelID
    last_loaded: int = 0