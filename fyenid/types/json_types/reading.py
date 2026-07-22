from pydantic import BaseModel, Field

from fyenid.types.message import Message
from ..core import *

class ReadRequestReturn(BaseModel):
    messages: list[dict] = Field(description="The returned messages.")