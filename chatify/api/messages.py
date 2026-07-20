from chatify.types.core import *
from chatify.types.message import *
import time, math, secrets

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from chatify.app import ChatApp

class MessageLib:
    def __init__(self, parent: "ChatApp") -> None:
        self.parent: "ChatApp" = parent

    async def generate_snowflake(self,channel: ChannelID):
        part1 = await self.parent.channels.load_channel(channel)
        if part1 is None:
            raise NotImplementedError("dk")

        number = (
            (part1.id << 24) | # 40 bit metadata id lmao
            secrets.randbits(24)
        )

        return number

    async def export_message(self, message: Message):
        '''Exports a message to save to JSON'''
        #parts = dir(message)
        return message._asdict()
    
    async def import_message(self, data: dict):
        '''Imports a message from json'''
        return Message(**data)
    async def send_message(
        self,
        content: str,
        author: UserID,
        channel: ChannelID,
        timestamp: int | None = None
    ):
        #TODO: implement
        id = await self.generate_snowflake(
            channel
        )
        if timestamp is None:
            timestamp = time.time_ns() // 1_000

        messageOBJ = Message(
            content=content,
            author=author,
            id=id,
            timestamp=timestamp,
            attachments=()
        )

        await self.parent.channels.register_message(channel, messageOBJ)
        return messageOBJ
        