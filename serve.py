from fastapi import Depends, FastAPI, Request
from pathlib import Path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import uvicorn
from chatify.app import ChatApp
from chatify.types.json_types.sending import SendRequest
app = FastAPI(
    title="chatify",
    description="Some chat app idk lmao",
    version="0.0.1a"
)
chat = ChatApp(Path(__file__).parent / "config")
chat.config.debug = True
security = HTTPBearer()

@app.get("/{page}")
async def root(page: str):
    '''Loads a page from /templates'''
    return chat.files.return_template(page)

@app.exception_handler(404)
async def not_found(request: Request, exc):
    return chat.files.return_status(404)

@app.exception_handler(500)
async def server_error(request: Request, exc):
    return chat.files.return_status(500)

@app.post("/channels/{channel_num}/send")
async def on_send(request: SendRequest, 
                  channel_num: int,
                  credentials: HTTPAuthorizationCredentials = Depends(security)):
    '''Sends a message to a channel number'''

    msg_contents = request.content
    channel_info = await chat.channels.load_channel(channel_num)
    if channel_info:
        await chat.channels.register_message(
            channel_num,
            await chat.messages.send_message(
                msg_contents,
                0,
                channel_num,
                None
            )
            
        )

if __name__ == "__main__":
    login = chat.users.login("moakdoge", "1234")
    print(login)
    chat.users.save_all()
    uvicorn.run(
        app=app,
        host=chat.config.host,
        port=chat.config.port
    )