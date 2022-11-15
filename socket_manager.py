import json
from typing import List
import starlette.websockets
from fastapi import WebSocket

from db import insert_message


class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket, user):
        await websocket.accept()
        self.active_connections.append({'username': user, 'websocket': websocket})

    def disconnect(self, user):
        for item in self.active_connections.copy():
            if item.get('username') == user:
                self.active_connections.remove(item)

    async def send_personal_message(self, receiver: str, sender: str, message: str):
        insert_message(receiver, sender, message)
        websocket = None
        for item in self.active_connections:
            if item.get('username') == receiver:
                websocket = item.get('websocket')
                break

        if websocket is not None:
            data = {'sender': sender, 'message': message}
            await websocket.send_json(data)

    async def broadcast(self, message: str):
        pass


manager = ConnectionManager()
