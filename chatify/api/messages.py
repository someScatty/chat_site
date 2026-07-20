from chatify.types.core import *
from chatify.types.message import *
import time, math, secrets
from . import channel as channelAPI
async def generate_snowflake(channel: ChannelID):
    part1 = await channelAPI.load_channel(channel)
    if part1 is None:
        raise NotImplementedError("dk")

    number = (
        (part1.id << 24) | # 40 bit metadata id lmao
        secrets.randbits(24)
    )

    return number

async def send_message(
    content: str,
    author: UserID,
    channel: ChannelID,
    timestamp: int | None = None
):
    #TODO: implement
    id = await generate_snowflake(
        channel
    )
    if timestamp is None:
        timestamp = time.time_ns() // 1_000

    messageOBJ = Message(
        content=content,
        author=author,
        channel=channel,
        id=id,
        timestamp=timestamp,
        attachments=()
    )

    await channelAPI.register_message(channel, messageOBJ)
    return messageOBJ
    