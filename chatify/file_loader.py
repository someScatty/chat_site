from functools import cache
from pathlib import Path

from fastapi.responses import HTMLResponse
from . import config
class FileManager:
    def __init__(self) -> None:
        pass

    @property
    def template_folder(self) -> Path:
        name = config.get()._folder / "templates"
        name.mkdir(exist_ok=True, parents=True)
        return name
    
    def load_template(self, name: str) -> str | None:
        '''Loads an HTML file from /templates. Use .return_template if passed directly into a return call for FastAPI.'''
        for file in self.template_folder.glob("*.html"):
            if file.suffix != ".html":
                continue
            root_name = file.stem
            if root_name == name:
                return file.read_text()
    
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
                content=config.get().base_404_message,
                status_code=404
            )
        
        return self.return_template("404")