from dataclasses import dataclass, field
from typing import Literal

from fastapi import WebSocket
from pydantic import UUID4, BaseModel


class DnDStatus(BaseModel):
    room: str
    status: bool
    client: UUID4


class Auth(BaseModel):
    room: str
    client_id: UUID4
    platform: Literal["macos", "android"]


@dataclass
class Client:
    room: str
    client_id: UUID4
    websocket: WebSocket
    platform: Literal["macos", "android"]

    def __hash__(self):
        return hash(self.client_id)

    def __eq__(self, other):
        return self.client_id == other.client_id


@dataclass
class Room:
    clients: list[Client] = field(default_factory=list)
    status: DnDStatus | None = None
