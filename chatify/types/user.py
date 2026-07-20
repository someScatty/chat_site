from dataclasses import dataclass
import math
import secrets, time
from .core import UserID

@dataclass(slots=True, frozen=True)
class Token:
    expiration_time: int
    value: str

    @classmethod
    def generate(cls, session_length: int) -> "Token":
        '''Generates a session token'''
        exp_time = math.ceil(session_length + time.time())
        value = secrets.token_urlsafe(64)

        return cls(
            value=value,
            expiration_time=exp_time
        )


@dataclass(slots=True)
class User:
    username: str
    token: str
    session_tokens: list[Token]
    id: UserID