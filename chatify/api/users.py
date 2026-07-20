import json
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

    def get_user(self, id: UserID) -> User:
        '''Gets a user by a user ID'''
        user = self.users.get(id, None)

        if user is None:
            raise Exception("I have no idea how the fuck to handle this")
        
        return user
    

    @property
    def _save_location(self):
        return self.parent.config._folder / "users.json"
    

    def _dump_token(self, tkn: Token) -> dict:
        '''Gets JSON data for a token'''
        return {
            "expiration_date": tkn.expiration_time,
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
            expiration_time=data["expiration_time"],
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
        
        with open(self._save_location, "w") as f:
            f.write(json.dumps(fixed_users))        

    def load_all(self):
        '''Loads all saved users'''
        data = {}
        if not self._save_location.exists():
            return
        
        with open(self._save_location, "r") as f:
            data = json.loads(f.read())
    
        for id, raw_usr in data.items():
            self.users[id] = self._load_user(raw_usr)
