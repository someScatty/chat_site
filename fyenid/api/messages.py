from fyenid.types.core import *
from fyenid.types.message import *
import time, math, secrets

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from fyenid.app import ChatApp

class MessageLib:
    def __init__(self, parent: "ChatApp") -> None:
        self.parent: "ChatApp" = parent

    def _get_message_info_from_id(self, id: MessageID) -> tuple[int, int]:
        '''Returns the channel ID and index of a message'''
        channel_id = id >> 24
        index = id & ((1 << 24) - 1)
        return channel_id, index
    
    async def get_message(self, id: MessageID) -> Message:
        '''Gets a message by an ID.'''
        channel, index = self._get_message_info_from_id(id)
        _channel = await self.parent.channels.load_channel(channel)
        if _channel is None:
            self.parent.console.error("Could not find", channel, "from message", id)
            raise
        msg = _channel.messages[index]
        if msg.id == id:
            return msg
        raise

    async def delete_message(self, message: MessageID | Message):
        if isinstance(message, int):
            message = await self.get_message(message)
        channel_id, index = self._get_message_info_from_id(message.id)
        channel = await self.parent.channels.load_channel(channel_id)

        if not channel:
            raise
            

        newinst = message._asdict()
        newinst["deleted"]=True
        newinst["content"]='[message deleted]'
        msg=await self.import_message(newinst)
        channel.messages[index] = msg
        await self.parent.channels.journal(msg, channel)

    async def edit_message(self, message: MessageID | Message, content: str):
        if isinstance(message, int):
            message = await self.get_message(message)
        channel_id, index = self._get_message_info_from_id(message.id)
        channel = await self.parent.channels.load_channel(channel_id)

        if not channel:
            raise
        
        newinst = message._asdict()
        newinst["edited"]=True
        newinst["content"]=content
        msg=await self.import_message(newinst)
        channel.messages[index] = msg
        await self.parent.channels.journal(msg, channel)   

    async def generate_snowflake(self,channel: ChannelID):
        part1 = await self.parent.channels.load_channel(channel)
        if part1 is None:
            raise NotImplementedError("dk")

        number = (
            (part1.id << 24) | # 40 bit metadata id lmao
            len(part1.messages)
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

        user = self.parent.users.get_user(id=author)
        if user is None:
            self.parent.console.error(f"User ID of {author} was not found! Failed to send message")
            return
    
        messageOBJ = Message(
            content=content,
            author=author,
            id=id,
            timestamp=timestamp,
            attachments=()
        )
        self.parent.console.debug(f"Message send in #{channel} (@",user.username,")", seperator="") # type: ignore
        await self.parent.channels.register_message(channel, messageOBJ)
        return messageOBJ
        