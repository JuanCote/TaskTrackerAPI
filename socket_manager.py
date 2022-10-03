from typing import List

import starlette.websockets

from db import websockets
from fastapi import WebSocket

active_connections: List[WebSocket] = []


class ConnectionManager:
    def __init__(self):
        print('init')

        print('*'*50, id(active_connections))

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        active_connections.append(websocket)
        print(id(self))
        print(id(active_connections))

    def disconnect(self, websocket: WebSocket):
        active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in active_connections:
            await connection.send_text(message)


manager = ConnectionManager()
