from collections import defaultdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()
ws_clients = defaultdict(list)


@app.websocket("/ws/rooms/{room_id}/")
async def get_room(websocket: WebSocket, room_id: str):
    await websocket.accept()
    ws_clients[room_id].append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for client in ws_clients[room_id]:
                if client == websocket:
                    continue
                await client.send_text(data)
    except WebSocketDisconnect:
        ws_clients[room_id].remove(websocket)
        await websocket.close()
