from typing import NamedTuple
from .core import *

class Message(NamedTuple):
    content: str
    author: UserID
    timestamp: UnixTime

    #Essential
    id: MessageID
    room: RoomID
    channel: ChannelID

    #optional / nice to have
    attachments: tuple[AttachmentID, ...]
    reply: MessageID | None = None