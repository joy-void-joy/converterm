import typing
from dataclasses import dataclass

import pexpect, pexpect.exceptions

import socketio

from environs import Env


env = Env()
env.read_env()
env.read_env(".env.local", override=True)

@dataclass
class App:
    @dataclass
    class User:
        pipe: pexpect.spawn | None = None
        

    users: dict[str, User]

app = App(users={})

sio = socketio.AsyncServer(
    cors_allowed_origins=env.list("CORS_ALLOWED_ORIGINS", subcast=str),
    async_mode="asgi",
)

def on_startup():
    app.users = {}

async def wait_for(sid: str, func = None) -> App.User:
    while (result := app.users.get(sid)) is None or (func and not func(result)):
        await sio.sleep(env.float("BUFFER_TIMEOUT"))

    return result

async def spawn(command: str, sid: str):
    user = await wait_for(sid)
    user.pipe = pexpect.spawn(command, encoding="utf-8", cwd=env.str("WORKING_DIRECTORY") or None, echo=False)
    user.pipe.setwinsize(env.int("VITE_TERM_HEIGHT"), env.int("VITE_TERM_WIDTH"))

    if not env.bool("CONTINUOUS"):
        return user.pipe

    while user.pipe.isalive():
        await sio.sleep()

        try:
            result = user.pipe.read_nonblocking(size=env.int("BUFFER_SIZE"), timeout=env.float("BUFFER_TIMEOUT"))
        except (pexpect.exceptions.TIMEOUT, pexpect.exceptions.EOF):
            pass
        else:
            await sio.emit("answer_command", result, to=sid)



@sio.event
async def connect(sid, *_) -> None:
    app.users[sid] = App.User()

    if env.bool("CONTINUOUS"):
        async def spawn_command():
            await spawn(env.str("COMMAND"), sid)
        sio.start_background_task(spawn_command)

    if env.bool("DISPLAY_COMMAND"):
        await sio.emit("answer_settitle", {"commandname": env.str("COMMAND"), "continuous": env.bool("CONTINUOUS")}, to=sid)

        

@sio.event
async def ask_command(sid, data: str) -> None:
    if env.bool("CONTINUOUS"):
        user = await wait_for(sid, lambda user: user.pipe is not None)
        return user.pipe.sendline(data)

    proc = await spawn(f"{env.str('COMMAND')} {data}", sid)
    result = proc.read()

    if env.bool("CRASH_ON_ERROR") and proc.exitstatus:
        raise RuntimeError("Command failed", result)
        
    await sio.emit("answer_command", result, to=sid)
    await sio.emit("answer_flush", to=sid)


asgi = socketio.ASGIApp(sio, on_startup=on_startup)
