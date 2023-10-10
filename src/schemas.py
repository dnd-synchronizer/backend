from dataclasses import dataclass, field
from typing import Literal, Optional

from fastapi import WebSocket
from pydantic import UUID4, BaseModel


class DnDStatus(BaseModel):
    status: bool
    id: UUID4

    def __bool__(self):
        return self.status


class Auth(BaseModel):
    id: UUID4
    platform: Literal["macos", "android"]


@dataclass
class Client:
    id: UUID4
    websocket: WebSocket
    platform: Literal["macos", "android"]
    room: Optional["Room"] = None


@dataclass
class Room:
    name: str
    clients: list[Client] = field(default_factory=list)
    dnd_status: DnDStatus | None = None
