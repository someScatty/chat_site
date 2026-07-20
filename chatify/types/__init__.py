from typing import TYPE_CHECKING, NamedTuple
from .core import *
from dataclasses import dataclass
    
class ChannelMetadata(NamedTuple):
    name: str
    description: str
    parent: RoomID

@dataclass(slots=True)
class Channel:
    metadata: ChannelMetadata
    messages: list[MessageID]