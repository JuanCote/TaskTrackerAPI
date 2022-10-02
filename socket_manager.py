import asyncio
import json
from datetime import datetime

from db import websockets

from fastapi import WebSocket


async def add_socket_to_list(websocket: WebSocket):
    with open('sockets.json', 'r') as file:
        data = json.load(file)

    data.update({int(datetime.now().timestamp()): str(websocket)})

    with open('sockets.json', 'w') as file:
        json.dump(data, file)

    return data


def delete_socket_to_list(websocket: WebSocket):
    with open('sockets.json', 'r') as file:
        data = json.load(file)

    with open('sockets.json', 'w') as file:
        json.dump(data, file)

    return data


class ConnectionManager:
    async def connect(self, websocket: WebSocket):
        await websocket.accept()

        task = asyncio.create_task(add_socket_to_list(websocket))
        await task

        if task:
            task.cancel()

    def disconnect(self, websocket: WebSocket):
        delete_socket_to_list(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        pass


manager = ConnectionManager()
