from typing import TYPE_CHECKING, Literal

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import zlib, hashlib, secrets

if TYPE_CHECKING:
    from fyenid.app import ChatApp
class SecurityLib:
    def __init__(self, parent: "ChatApp") -> None:
        self.parent = parent
        self.ph = PasswordHasher()

    def secure_hash(self, password: str):
        '''Generates a secure hash'''
        return self.ph.hash(password)
    
    def secure_usertoken(self) -> int:
        '''Generates a user token'''
        return secrets.randbits(64)
    
    def validate_password(self, hash: str, password: str) -> bool:
        '''Validates a password with its respective hash'''
        try:
            verified = self.ph.verify(hash, password)
        except VerifyMismatchError:
            return False
        return verified
    
    def hash(self, 
             data: bytes | str,
             hash_type: Literal["sha1", "sha256", "md5", "crc32"] = "sha256"
        ) -> str:
        
        '''Hashes some data.'''
        if isinstance(data, str):
            data = data.encode(encoding="utf-8")

        match hash_type:
            case "sha256":
                return hashlib.sha256(data).hexdigest()
            case "md5":
                return hashlib.md5(data).hexdigest()
            case "sha1":    
                return hashlib.sha1(data).hexdigest()
            case "crc32":
                return str(zlib.crc32(data))
            case _:
                raise TypeError(f"Unknown hash type: {hash_type}")