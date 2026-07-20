from dataclasses import dataclass
from .core import *
from typing import NamedTuple

class ChannelMetadata(NamedTuple):
    name: str
    description: str
    id: ChannelID

@dataclass(slots=True)
class Channel:
    metadata: ChannelMetadata
    messages: list[MessageID]