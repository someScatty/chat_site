import os, json
from dataclasses import dataclass
from pathlib import Path
import sys
import uuid
from typing import TYPE_CHECKING

from fyenid.types.decorators import on_exit

if TYPE_CHECKING:
    from fyenid.app import ChatApp

class Config:
    _folder: Path

    @property
    def _save_location(self) -> Path:
        return self._folder / "config.json"

    def _save(self):
        with open(self._save_location, "w") as file:
            file.write(json.dumps(self.serialize(), indent=2 if self.debug else 0))

    def _load(self):
        if not self._save_location.exists():
            self._save()
        else:
            with open(self._save_location, "r") as file:
                data = json.loads(file.read())
                self.__dict__.update(data)

    
    def serialize(self):
        ALLOWED_TYPES = (str, int, list, dict, bool)
        new = {}
        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue
            if isinstance(value, ALLOWED_TYPES):
                new[key] = value
        return new
    
    def make_temp_file(self, file: Path) -> Path:
        '''Generates a temp file'''
        name = file.name + "-" + str(self._parent.security.hash(data=file.name, hash_type='crc32')) + ".tmp"
        return Path(file.parent / name).resolve()

    def save_custom(
            self, 
            file: str | Path,
            data: dict):
        '''Saves a custom file'''

        fi = (self._folder / file)
        fi.parent.mkdir(exist_ok=True, parents=True)

        #making it atomic
        tempfile = self.make_temp_file(fi)
        self._parent.console.debug("Saving", fi.relative_to(self._folder), "atomically with", tempfile.relative_to(self._folder))
        with open(tempfile, "w") as f:
            contents = json.dumps(data, indent=2 if self.debug else 0)
            f.write(contents)
            f.flush()
            os.fsync(f.fileno())

        os.replace(tempfile, fi)
        self._parent.console.debug(f"Successfully saved file {fi.relative_to(self._folder)}")

    def _load_contents(self, data: bytes) -> dict:
        '''Loads contents'''
        txt = data.decode(encoding="utf-8")
        return json.loads(txt)

    def load_custom(
            self, 
            file: str | Path,
            ) -> dict:
        '''Loads a custom file'''

        fixed_file = (self._folder / file).resolve()
        tmp_file = self.make_temp_file(fixed_file)

        self._parent.console.debug(f"Loading file {fixed_file.relative_to(self._folder)}")

        if not (self._folder / file).exists():
            if tmp_file.exists():
                self._parent.console.warn(f"Loading off {tmp_file} for file {fixed_file.relative_to(self._folder)}")
                contents = tmp_file.read_bytes()
                os.replace(tmp_file, fixed_file)
                return self._load_contents(contents)
            return {}
        
        
        with open(self._folder / file, "rb") as f:
            return self._load_contents(f.read())


    @property
    def _lockfile(self) -> Path:
        return self._folder / "app.lock"
    
    def _is_locked(self) -> bool:
        return self._lockfile.exists() 
         
    def _lock_pid(self) -> int | None:
        if not self._is_locked():
            return None
        return int(self._lockfile.read_text())

    def _lock(self):
        self._lockfile.write_text(str(os.getpid()))

    def _unlock(self):
        os.remove(self._lockfile)

    def __init__(self, base: Path, parent: "ChatApp", debug: bool = False) -> None:
        self._folder = base
        self._folder.mkdir(exist_ok=True, parents=True)
        self._parent = parent
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.lazy_load_time = 3 #TESTING; should be closer to 30 or 60. in seconds.
        self.timeout = 30 * 60 #The amount of time for a session to be valid. In seconds.
        self.port: int = int(os.getenv("PORT", "8000"))
        self.debug: bool = debug #os.getenv("DEBUG", "false").lower() == "true"
        self.product_name: str = "fyenid"
        self.base_404_message = '''
<!DOCTYPE html>
<h1>Error loading normal 404 page; if you see this as a non-developer, something has gone seriously wrong!</h1><nl>
<h2>If you are the site developer, please put a file named 404.html into your templates folder!</h2>
        '''
        self.version = "0.0.1b"
        self._load()
        self._save()



    @on_exit
    def _on_exit(self):
        self._save()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self._save()
