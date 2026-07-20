import secrets

from chatify.types.core import ChannelID
from chatify.types.channel import *
from chatify.types.message import Message

#TODO: Make this not dogshit
CACHE: dict[ChannelID, Channel] = {} 

async def load_channel(channelID: ChannelID) -> Channel | None:
    return CACHE.get(channelID, None)

async def register_message(channelID: ChannelID, message: Message):
    chan = await load_channel(channelID)
    if chan is None:
        raise
    chan.messages.append(message)

async def generate_channel_snowflake() -> int:
    return secrets.randbits(40)

async def new_channel(
    metadata: ChannelMetadata
):
    #TODO: implement channel manager over this bs
    
    new_id = await generate_channel_snowflake()
    CACHE[new_id] = Channel(
        metadata,
        [],
        new_id
    )