#chat.users.get_user(id=user_id).username
from pydantic import BaseModel, Field
from ..core import *
class UserObject(BaseModel):
    username: str