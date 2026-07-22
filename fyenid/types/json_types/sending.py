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

    reply: MessageID | None = Field(
        description="The message ID to respond to, if any.",
        default=None
    )

class EditRequest(BaseModel):
    content: str = Field(
        description="The content to send in the message.",
        examples=["Hello, world!"],
        max_length=2048
    )
