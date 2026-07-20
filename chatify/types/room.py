from .core import *
from .channel import *
class Room:
    def __init__(self, id: RoomID) -> None:
        self.id: RoomID = id
        self.channels: list[ChannelMetadata]
        self._cache: dict[ChannelMetadata, Channel] = {}


    def _get_metadata_by_id(self, channelID: ChannelID) -> ChannelMetadata | None:
        return next(
            (c for c in self.channels if c.id == channelID),
            None
        )
    def get_channel(self, channelID: ChannelID) -> Channel:
        #TODO: Make this actually lazy-load
        metadata = self._get_metadata_by_id(channelID)
        if not metadata:
            raise NotImplementedError("idk")

        return self._cache[metadata]