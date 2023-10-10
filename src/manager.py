from schemas import Client, DnDStatus, Room


class ClientManager:
    def __init__(self):
        self.active_connections: dict[str, Room] = dict()

    async def connect(self, client: Client, room_name: str):
        room = self._get_or_create_room(room_name)
        if room.dnd_status is not None:
            await client.websocket.send_text(room.dnd_status.model_dump_json())
        client.room = room
        room.clients.append(client)

    async def disconnect(self, client: Client):
        if client.room:
            client.room.clients.remove(client)
        if client.websocket:
            await client.websocket.close()

    async def broadcast(self, status: DnDStatus, client: Client):
        if client.room is None:
            await self.disconnect(client)
            return
        print(status)
        client.room.dnd_status = status
        for room_client in client.room.clients:
            if not room_client.websocket:
                continue
            await room_client.websocket.send_text(status.model_dump_json())

    def _get_or_create_room(self, room_name: str) -> Room:
        if room_name not in self.active_connections:
            self.active_connections[room_name] = Room(
                name=room_name,
                clients=[],
                dnd_status=None,
            )
        return self.active_connections[room_name]


manager = ClientManager()
