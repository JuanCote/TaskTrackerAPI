import json
from typing import List
import starlette.websockets
from fastapi import WebSocket

from db import insert_message


class ConnectionManager:
    def __init__(self):
        self.connections = []
        self.authorized_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        for item in self.authorized_connections:
            if item.get('websocket') == websocket:
                self.authorized_connections.remove(item)
        manager.connections.remove(websocket)

    async def send_personal_message(self, receiver: str, sender: str, message: str):
        data = insert_message(receiver, sender, message)
        websocket = None
        for item in self.authorized_connections:
            if item.get('username') == receiver:
                websocket = item.get('websocket')
                break

        if websocket is not None:
            await websocket.send_json(data)

    async def broadcast(self, message: str):
        pass


manager = ConnectionManager()
