from typing import Annotated
from uuid import uuid4

from fastapi import Cookie, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from manager import manager
from ws import router

app = FastAPI()
app.include_router(router)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request, room_name: Annotated[str | None, Cookie()] = None):
    if room_name:
        return RedirectResponse(url=f"/rooms/{room_name}", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/rooms/create_random_room", response_class=HTMLResponse)
async def create_random_room(request: Request):
    room_name = str(uuid4()).split("-")[0]
    manager.active_connections[room_name]
    response = RedirectResponse(url=f"/rooms/{room_name}", status_code=303)
    response.set_cookie("room_name", room_name)
    return response


@app.get("/rooms/{room_name}", response_class=HTMLResponse)
async def room(request: Request, room_name: str):
    room = manager.active_connections[room_name]
    return templates.TemplateResponse(
        "room.html",
        {"request": request, "room_name": room_name, "room": room},
    )
