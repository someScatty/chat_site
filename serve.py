from fastapi import FastAPI, Request
from pathlib import Path
import uvicorn
import chatify.config
import chatify.file_loader
app = FastAPI()
fileManager = chatify.file_loader.FileManager()


@app.get("/{page}")
async def root(page: str):
    return fileManager.return_template(page)

@app.exception_handler(404)
async def not_found(request: Request, exc):
    return fileManager.return_status(404)

@app.exception_handler(500)
async def server_error(request: Request, exc):
    return fileManager.return_status(500)

if __name__ == "__main__":
    chatify.config.load(Path(__file__).parent)

    uvicorn.run(
        app=app,
        host=chatify.config.get().host,
        port=chatify.config.get().port
    )