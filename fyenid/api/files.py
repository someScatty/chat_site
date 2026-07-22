from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import Response
from fastapi.responses import HTMLResponse


if TYPE_CHECKING:
    from fyenid.app import ChatApp
class FileManager:
    def __init__(self, parent: "ChatApp") -> None:
        self.parent = parent

    @property
    def template_folder(self) -> Path:
        name = self.parent.config._folder / "templates"
        name.mkdir(exist_ok=True, parents=True)
        return name
    

    def find(self, namespace: str, value: str, media_type: str) -> Response | None:
        '''Looks inside a namespace for a file.'''
        for file in (self.parent.config._folder / namespace).glob("*"):
            if file.name == value:
                return Response(
                    content = file.read_text(),
                    media_type=media_type
                )
            
    def load_template(self, name: str) -> str | None:
        '''Loads an HTML file from /templates. Use .return_template if passed directly into a return call for FastAPI.'''
        for file in self.template_folder.glob("*.html"):
            if file.suffix != ".html":
                continue
            root_name = file.stem
            if root_name == name:
                text = file.read_text()
                return text
    
        return None
    
    def return_template(self, name: str) -> HTMLResponse:
        template_data = self.load_template(name)
        
        if template_data:
            return HTMLResponse(
                content=template_data
            )
        
        return self.return_status(404)
    
    def return_status(self, status_code: int) -> HTMLResponse:
        '''Attempts to load a status code error page; if it fails, returns a barebones 404'''
        template = self.load_template(str(status_code))
        if template:
            return self.return_template(str(status_code))
        
        _404template = self.load_template("404")
        if not _404template:
            return HTMLResponse(
                content=self.parent.config.base_404_message,
                status_code=404
            )
        
        return self.return_template("404")