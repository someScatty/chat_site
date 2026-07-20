import os, json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chatify.app import ChatApp

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
    
    def save_custom(
            self, 
            file: str | Path,
            data: dict):
        '''Saves a custom file'''

        with open(self._folder / file, "w") as f:
            dumped = json.dumps(data, indent=2 if self.debug else 0)
            f.write(dumped)        

    def load_custom(
            self, 
            file: str | Path,
            ) -> dict:
        '''Loads a custom file'''
        if not (self._folder / file).exists():
            return {}
        with open(self._folder / file, "r") as f:
            return json.load(f)
                 
    def __init__(self, base: Path, parent: "ChatApp", debug: bool = False) -> None:
        self._folder = base
        self._folder.mkdir(exist_ok=True, parents=True)
        self._parent = parent
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.debug: bool = debug #os.getenv("DEBUG", "false").lower() == "true"
        self.base_404_message = '''
<!DOCTYPE html>
<h1>Error loading normal 404 page; if you see this as a non-developer, something has gone seriously wrong!</h1><nl>
<h2>If you are the site developer, please put a file named 404.html into your templates folder!</h2>
        '''

        self._load()
        self._save()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self._save()
