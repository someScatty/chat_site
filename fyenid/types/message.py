from typing import NamedTuple
from .core import *

class Message(NamedTuple):
    content: str
    author: UserID
    timestamp: UnixTime

    #Essential
    id: MessageID

    #optional / nice to have
    attachments: tuple[AttachmentID, ...]
    reply: MessageID | None = None
    edited: bool = False
    deleted: bool = False