from typing import List

import starlette.websockets

from db import websockets
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket, user):
        await websocket.accept()
        self.active_connections.append({'username': user, 'websocket': websocket})
        print(self.active_connections)

    def disconnect(self, user):
        for item in self.active_connections.copy():
            if item.get('username') == user:
                self.active_connections.remove(item)

        print(self.active_connections)
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()
