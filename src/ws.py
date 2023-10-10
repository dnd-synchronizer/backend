from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from manager import manager
from schemas import Auth, Client, DnDStatus

router = APIRouter()


@router.websocket("/ws/rooms/{room_name}/")
async def connect_room(websocket: WebSocket, room_name: str):
    await websocket.accept()
    auth_data = await websocket.receive_json()
    try:
        auth = Auth(**auth_data)
        client = Client(**auth.model_dump(), websocket=websocket)
    except ValidationError as e:
        await websocket.send_text(e.json())
        await websocket.close()
        return
    await manager.connect(client, room_name)
    try:
        while True:
            text = await websocket.receive_text()
            try:
                status = DnDStatus.model_validate_json(text)
                await manager.broadcast(status, client)
                continue
            except ValidationError:
                pass
            await websocket.send_text(text)
    except WebSocketDisconnect:
        await manager.disconnect(client)
