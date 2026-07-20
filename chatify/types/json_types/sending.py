from pydantic import BaseModel, Field
from ..core import *
class SendRequest(BaseModel):
    content: str = Field(
        description="The content to send in the message.",
        examples=["Hello, world!"],
        max_length=2048
    )

    author: UserID = Field(
        description="The user ID of the sender; Is validated.",
    )