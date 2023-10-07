from collections import defaultdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import UUID4, ValidationError

from schemas import Auth, Client, DnDStatus

app = FastAPI()


class ClientManager:
    def __init__(self):
        self.active_connections: dict[str, list[Client]] = defaultdict(list)

    async def connect(self, client: Client):
        self.active_connections[client.room].append(client)

    async def disconnect(self, client: Client):
        self.active_connections[client.room].remove(client)
        if client.websocket:
            await client.websocket.close()

    async def broadcast(self, data: str, room_id: str):
        for client in self.active_connections[room_id]:
            if not client.websocket:
                continue
            await client.websocket.send_text(data)


manager = ClientManager()


@app.websocket("/ws/rooms/")
async def connect_room(websocket: WebSocket):
    await websocket.accept()
    auth_data = await websocket.receive_json()
    try:
        auth = Auth(**auth_data)
        client = Client(**auth.model_dump(), websocket=websocket)
    except ValidationError as e:
        await websocket.send_text(e.json())
        await websocket.close()
        return
    await manager.connect(client)
    try:
        while True:
            await websocket.receive_text()
            await websocket.send_text("ping")
    except WebSocketDisconnect:
        await manager.disconnect(client)


@app.post("/rooms/change_status/")
async def change_dnd_status(status: DnDStatus) -> DnDStatus:
    await manager.broadcast(status.model_dump_json(), status.room)
    return status


@app.get("/rooms/client_list/")
async def room_list(auth: Auth) -> list[UUID4]:
    return [client.client_id for client in manager.active_connections[auth.room]]
