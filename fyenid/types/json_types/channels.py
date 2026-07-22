from pydantic import BaseModel, Field
from ..core import *
class NewChannel(BaseModel):
    name: str
    description: str

class NewChannelReturn(BaseModel):
    success: bool
    error: str
    id: int

class FoundChannels(BaseModel):
    channels: list[int]