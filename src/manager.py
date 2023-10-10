from collections import defaultdict

from schemas import Client, DnDStatus, Room


class ClientManager:
    def __init__(self):
        self.active_connections: dict[str, Room] = defaultdict(Room)

    async def connect(self, client: Client):
        if status := self.active_connections[client.room].status:
            await client.websocket.send_text(status.model_dump_json())
        self.active_connections[client.room].clients.append(client)

    async def disconnect(self, client: Client):
        self.active_connections[client.room].clients.remove(client)
        if client.websocket:
            await client.websocket.close()

    async def broadcast(self, status: DnDStatus):
        self.active_connections[status.room].status = status
        for client in self.active_connections[status.room].clients:
            if not client.websocket:
                continue
            await client.websocket.send_text(status.model_dump_json())


manager = ClientManager()
