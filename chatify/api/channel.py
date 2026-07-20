import asyncio
import secrets


from chatify.types.core import ChannelID
from chatify.types.channel import *
from chatify.types.message import Message
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from chatify.app import ChatApp

class ChannelSubsystem:
    #TODO: Make this not dogshit
    def __init__(self, parent: "ChatApp") -> None:
        self.CACHE: dict[ChannelID, Channel] = {} 
        self.parent = parent

    async def load_channel(self, channelID: ChannelID) -> Channel | None:
        return self.CACHE.get(channelID, None)
    
    async def register_message(self,channelID: ChannelID, message: Message):
        chan = await self.load_channel(channelID)
        if chan is None:
            raise
        chan.messages.append(message)

    async def generate_channel_snowflake(self) -> int:
        return secrets.randbits(40)

    async def new_channel(
        self,
        metadata: ChannelMetadata
    ):
        #TODO: implement channel manager over this bs
        new_id = await self.generate_channel_snowflake()
        self.CACHE[new_id] = Channel(
            metadata,
            [],
            new_id
        )


