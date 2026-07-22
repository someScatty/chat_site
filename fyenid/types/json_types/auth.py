from pydantic import BaseModel, Field
from ..core import *
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginReturn(BaseModel):
    success: bool
    session_token: str
    id: int
    error: str