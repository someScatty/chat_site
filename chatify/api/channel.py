import asyncio
from io import TextIOWrapper
import json
import os
from pathlib import Path
import secrets

import time
from chatify.types.core import ChannelID
from chatify.types.channel import *
from chatify.types.decorators import *
from chatify.types.message import Message
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from chatify.app import ChatApp

class ChannelSubsystem:
    #TODO: Make this not dogshit
    def __init__(self, parent: "ChatApp") -> None:
        self.CACHE: dict[ChannelID, Channel] = {} 
        self.parent = parent
        self.channel_ids: list[int] = []
        self._journal_cache: dict[ChannelID, TextIOWrapper] = {}

        self.load_all() 


    async def journal(self, message: Message, channel: Channel):
        '''Creates a journal file'''
        _json = json.dumps(await self.parent.messages.export_message(message))
        metadata, messages = self._get_save_files(channelID=channel.id)
        tmpjournal = metadata.parent / ".tmpjournal"
        if channel.id not in self._journal_cache:
            if not tmpjournal.exists(): # hack to make a journal file
                tmpjournal.write_text("")
            self._journal_cache[channel.id] = open(tmpjournal, "a")

        file = self._journal_cache[channel.id]
        file.write(_json + "\n")
        file.flush()
        os.fsync(file.fileno())

    @on_exit
    async def _on_exit(self):
        for id, chl in self.CACHE.copy().items():
            self.parent.console.debug(f"Unloading: {chl} ({id})")
            await self._unload(chl)

    def load_all(self):
        for file in (self.parent.config._folder / "channels").glob("*"):
            if file.is_dir():
                self.channel_ids.append(int(file.stem))

    async def load_channel(self, channelID: ChannelID) -> Channel | None:
        channel = self.CACHE.get(channelID, None)

        if channel is None:
            channel = await self.load(channelID)

        if channel:
            channel.last_loaded = int(time.time())
            return channel
    
    async def register_message(self,channelID: ChannelID, message: Message):
        chan = await self.load_channel(channelID)
        if chan is None:
            raise
        chan.messages.append(message)
        await self.journal(message, chan)

    async def export_metadata(self, metadata: ChannelMetadata) -> dict:
        '''exports channel metadata or smth idk im tired as shit just work'''
        return {
            "name": metadata.name,
            "description": metadata.description
        }
    async def export_channel(self, channel: Channel) -> dict:
        '''Exports a channel to a JSON format'''
        return {
            "metadata": await self.export_metadata(channel.metadata),
            "messages": [await self.parent.messages.export_message(m) for m in channel.messages],       
        }
    

    def _get_save_files(self, channelID: ChannelID) -> tuple[Path, Path]:
        '''Gets metadata and messages save folder'''
        config = self.parent.config
        _folder = config._folder / "channels" / str(channelID)
        metadata = _folder / "metadata.json"
        messages = _folder / "messages.json"

        return (metadata, messages)
    async def save(self, channel: Channel):
        config = self.parent.config
        metadata, messages = self._get_save_files(channel.id)
        data = await self.export_channel(channel)
        config.save_custom(metadata, data["metadata"])
        config.save_custom(messages, data["messages"])


    async def load(self, channelID: ChannelID) -> Channel:
        self.parent.console.debug(f"Loading channel #{channelID}")
        metadata, messages = self._get_save_files(channelID)
        config = self.parent.config
        metadata_contents = config.load_custom(metadata)
        message_contents = config.load_custom(messages)
        tmpjournal = metadata.parent / ".tmpjournal"

        if tmpjournal.exists():
            self.parent.console.warn(f".tmpjournal is found; loading off it")
            _messages = []
            with open(tmpjournal, "r") as f:
                _lines = f.read().splitlines()
                for i, line in enumerate(_lines):
                    try:
                        _messages.append(json.loads(line))
                    except json.JSONDecodeError:
                        self.parent.console.error("Failed to load message",i,"(corrupted)")
            message_contents.extend(_messages) # type: ignore
            os.remove(tmpjournal)
        
        data = {
            "messages": message_contents,
            "metadata": metadata_contents,
            "id": channelID
        }
        if data["metadata"] == {}:
            raise Exception("Channel does not exist!")
        


        self.CACHE[data["id"]] = Channel(
            metadata=ChannelMetadata(**data["metadata"]),
            messages=[await self.parent.messages.import_message(m) for m in data["messages"]],
            id=data["id"],
            last_loaded=round(time.time())
        )

        await self.save(self.CACHE[data["id"]])
        return self.CACHE[data["id"]] 

    async def get_metadata(self, channelID: ChannelID) -> ChannelMetadata:
        '''Gets the metadata for a channel'''
        if channelID in self.CACHE:
            return self.CACHE[channelID].metadata
        
        metadata_file, _  = self._get_save_files(channelID)
        if metadata_file.exists():
            md = self.parent.config.load_custom(metadata_file)
            return ChannelMetadata(*md)
        
        self.parent.console.error(f"Could not poll metadata for channel #{channelID}")
        raise

    async def _unload(self, channel: Channel):
        self.parent.console.debug(f"Unloading channel #{channel.id}")
        await self.save(channel)
        del self.CACHE[channel.id]
        #Make sure to delete the journaling file if any
        if channel.id in self._journal_cache:
            io_obj = self._journal_cache[channel.id]
            io_obj.flush()
            io_obj.close()
            os.remove(Path(io_obj.name).resolve())
            del self._journal_cache[channel.id]

    @on_interval(seconds=5)
    async def _load_loop(self):
        for _, channel in self.CACHE.copy().items():
            if time.time() - channel.last_loaded > self.parent.config.lazy_load_time:
                await self._unload(channel)

        
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
        self.channel_ids.append(new_id)
        await self.save(self.CACHE[new_id])
        return self.CACHE[new_id]
    


