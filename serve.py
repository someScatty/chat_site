import asyncio

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from pathlib import Path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import uvicorn
from fyenid.app import ChatApp
from fyenid.types.channel import ChannelMetadata
from fyenid.types.json_types.auth import LoginRequest, LoginReturn
from fyenid.types.json_types.channels import FoundChannels, NewChannel, NewChannelReturn
from fyenid.types.json_types.reading import ReadRequestReturn
from fyenid.types.json_types.sending import EditRequest, SendRequest
from fyenid.types.json_types.user import UserObject
from fyenid.types.user import Token, User

chat = ChatApp(Path(__file__).parent / "config", debug=True)
app = FastAPI(
    title="chatify",
    description="Some chat app idk lmao",
    version=chat.config.version,
    lifespan=chat.run
)
chat.config.debug = True
security = HTTPBearer()

@app.get("/{page}")
async def root(page: str):
    '''Loads a page from /templates'''
    return chat.files.return_template(page)


@app.get("/css/{css}")
async def css(css: str):
    return chat.files.find("css", css, "text/css")

@app.get("/scripts/{scripts}")
async def scripts(scripts: str):
    return chat.files.find("scripts", scripts, "application/javascript")

@app.exception_handler(404)
async def not_found(request: Request, exc):
    return chat.files.return_status(404)

@app.exception_handler(500)
async def server_error(request: Request, exc):
    return chat.files.return_status(500)

@app.post("/api/login")
async def on_login(request: LoginRequest) -> LoginReturn:
    username = request.username
    password = request.password
    output = chat.users.login(username, password)
    if output is None:
        return LoginReturn(success=False, session_token="", id=-1, error="Unknown login")
    user, token = output
    return LoginReturn(
        success=True,
        session_token=token.value,
        id=user.id,
        error=""
    )

@app.post("/api/signUp")
async def on_signup(request: LoginRequest) -> LoginReturn:
    username = request.username
    password = request.password
    output = chat.users.create_user(username, password)
    
    session=Token.generate(1800) # 30min
    output.session_tokens.append(session)

    return LoginReturn(
        success=True,
        session_token=session.value,
        id=output.id,
        error=""
    )
    

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    user = chat.users.verify(credentials.credentials)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return user

@app.get("/users/{user_id}")
async def get_user_info(user_id: int, user: User = Depends(get_current_user)) -> UserObject:
    usr = chat.users.get_user(id=user_id)

    if usr is None:
        raise HTTPException(403)

    return UserObject(
        username=usr.username
    )


@app.delete("/messages/{message_id}/delete")
async def delete(message_id: int,  user: User = Depends(get_current_user)):
    msg = await chat.messages.get_message(message_id)
    if msg.author != user.id:
        return Response(status_code=403)
    await chat.messages.delete_message(msg)
    return Response(status_code=200)
    
@app.patch("/messages/{message_id}/edit")
async def edit(edit: EditRequest, message_id: int,  user: User = Depends(get_current_user)):
    msg = await chat.messages.get_message(message_id)
    if msg.author != user.id:
        return Response(status_code=403)
    await chat.messages.edit_message(msg, edit.content)
    return Response(status_code=200)

@app.get("/channels/{channel_num}/read")
async def read(channel_num: int, user: User = Depends(get_current_user), limit: int=50, before: int = -1, after: int = -1) -> ReadRequestReturn:
    msgs = await chat.channels.load_channel(channel_num)

    if not msgs:
        raise HTTPException(500)
    

    if before > 0:
        _, ind = chat.messages._get_message_info_from_id(before)
        messages = msgs.messages[max(0, ind - limit):ind]
    elif after > 0:
        _, ind = chat.messages._get_message_info_from_id(after)
        messages = msgs.messages[ind+1:ind+1+limit]
    else:
        messages = msgs.messages[:limit]
    return ReadRequestReturn(
        messages=await asyncio.gather(
            *[
                chat.messages.export_message(msg)
                for msg in messages
            ]
        )
    )
@app.post("/channels/{channel_num}/send")
async def on_send(request: SendRequest, 
                  channel_num: int,
                  user: User = Depends(get_current_user)):
    '''Sends a message to a channel number'''

    
    msg_contents = request.content
    channel_info = await chat.channels.load_channel(channel_num)
    if channel_info:
        await chat.messages.send_message(
            msg_contents,
            user.id,
            channel_num,
            request.reply
        )
            


@app.get("/channels/get")
async def get_channels(limit: int = 50) -> FoundChannels:
    '''Gets the channels.'''
    channels = chat.channels.channel_ids[0:limit]
    print("FOUND:", channels)
    return FoundChannels(channels=channels)

@app.post("/channels/new")
async def on_new_channel(request: NewChannel, user: HTTPAuthorizationCredentials = Depends(get_current_user)) -> NewChannelReturn:
    chl = await chat.channels.new_channel(ChannelMetadata(name=request.name, description=request.description))
    if chl:
        return NewChannelReturn(
            success=True,
            error="",
            id=chl.id
        )
    return NewChannelReturn(
        success=False,
        error="Could not make channel",
        id=-1
    )

if __name__ == "__main__":

    chat.users.create_user("moakdoge", "1234")
    uvicorn.run(
        app=app,
        host=chat.config.host,
        port=chat.config.port
    )