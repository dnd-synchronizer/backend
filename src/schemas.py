from dataclasses import dataclass

from fastapi import WebSocket
from pydantic import UUID4, BaseModel


class DnDStatus(BaseModel):
    room: str
    status: bool
    client: UUID4


class Auth(BaseModel):
    room: str
    client_id: UUID4


@dataclass
class Client:
    room: str
    client_id: UUID4
    websocket: WebSocket

    def __hash__(self):
        return hash(self.client_id)

    def __eq__(self, other):
        return self.client_id == other.client_id
