import asyncio
from functools import lru_cache
import json
import time
from typing import TYPE_CHECKING

from chatify.types.user import User, Token
from chatify.types.core import UserID
if TYPE_CHECKING:
    from chatify.app import ChatApp

class UserManager:
    def __init__(self, parent: "ChatApp") -> None:
        self.parent = parent
        self.users: dict[UserID, User] = {}
        self.load_all()

        self.parent.on_exit(self._on_exit)
        self.parent.schedule_task(self._asession_purge, repeat_interval=1)

    def get_user(self, *, id: UserID | None = None, username: str | None = None) -> User | None:
        '''Gets a user by a user ID or username'''

        if id is not None:
            user = self.users.get(id, None)

            if user is None:
               return None
               # raise Exception("I have no idea how the fuck to handle this")
            
            return user


        if username is not None:
            found = [usr for usr in self.users.values() if usr.username == username]

            if len(found) == 0:
                return None
            return found[0]
        raise Exception("please provide id or username")
    
    @property
    def _save_location(self):
        return "users.json"
    

    def _dump_token(self, tkn: Token) -> dict:
        '''Gets JSON data for a token'''
        return {
            "expires": tkn.expiration_time,
            "value": tkn.value
        }
    
    def _dump_user(self, usr: User) -> dict:
        '''Gets JSON data for a user'''
        session_tokens = [self._dump_token(tk) for tk in usr.session_tokens]
        return {
            "username": usr.username,
            "token": usr.token,
            "session_tokens": session_tokens,
            "id": usr.id
        }
        

    def _load_token(self, data: dict) -> Token:
        '''Loads a session token based off the data dict'''
        return Token(
            expiration_time=data["expires"],
            value=data["value"]
        )
    def _load_user(self, data: dict) -> User:
        '''Loads a user off its respective data dict'''
        session_tokens: list[Token] = [self._load_token(_) for _ in data["session_tokens"]]
        return User(
            data["username"],
            data["token"],
            session_tokens,
            data["id"]
        )
    
    def save_all(self):
        '''Saves all users to a file.'''
        fixed_users: dict[UserID, dict] = {}
        
        for id, usr in self.users.items():
            fixed_users[id] = self._dump_user(usr)

        self.parent.config.save_custom(self._save_location, fixed_users) 

    def load_all(self):
        '''Loads all saved users'''
        data = self.parent.config.load_custom(self._save_location)
        for id, raw_usr in data.items():
            self.users[int(id)] = self._load_user(raw_usr)


    def exists(self, username: str) -> bool:
        '''Checks if a user exists'''
        usr = self.get_user(username=username)

        return (usr is not None)

    def create_user(
        self,
        username: str,
        password: str
    ) -> User:
        '''Generates a new user'''
        if self.exists(username):
            return self.get_user(username=username) # type: ignore
        
        token = self.parent.security.secure_hash(password)

        new_user = User(
            username=username,
            token=token,
            session_tokens=[],
            id=self.parent.security.secure_usertoken()
        )

        self.users[new_user.id] = new_user

        # cant believe this was forgotten -scatty
        self.save_all()
        return new_user
    
    def generate_session_token(self, user: UserID, duration: int = 1800) -> Token:
        '''Generates a valid session token. Duration is in SECONDS before it expires.'''
        usr = self.get_user(id=user)
        tkn = Token.generate(duration)

        if not usr:
            raise

        usr.session_tokens.append(tkn)
        self.save_all()

        return tkn
    
    def login(self, username: str, password: str) -> tuple[User, Token] | None:
        '''
        Atempts to log in a user; returns None if password is wrong or user is not found
        Also will generate a valid session token
        '''
        usr = self.get_user(username=username)

        if usr is None:
            return None
        
        verified = self.parent.security.validate_password(usr.token, password)

        if not verified:
            return None
        
        token = Token.generate(1800) #30 min
        usr.session_tokens.append(token)

        # cant believe this was forgotten -scatty
        self.save_all()
        return usr, token
    


    async def _asession_purge(self):
        for id, usr in self.users.items():
            usr.session_tokens = [_ for _ in usr.session_tokens if not _.expired]


    @lru_cache()
    def get_id_from_session(self, session: str) -> UserID | None:
        '''Gets a user ID from a session'''
       
        for id, user in self.users.items():
            for ses in user.session_tokens:
                if ses.value == session:
                    return id
        return None
    
    def verify(self, session: str, user: UserID | None = None) -> User:
        '''Checks if a session token is valid. Returns the user if valid'''

        if user is None:
            user = self.get_id_from_session(session)
        usr = self.get_user(id=user)

        if usr is None:
            raise #idk lmao

        found = [s for s in usr.session_tokens if s.value == session]
        valid = len(found) > 0
        if valid:
            if found[0].expired:
                raise
            return usr
        raise

    def _on_exit(self):
        self.save_all()