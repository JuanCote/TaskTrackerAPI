import json
from typing import List
import starlette.websockets
from fastapi import WebSocket

from db import insert_message
from deps import decode_token
from model.chat import chat_users


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

    async def send_personal_message(self, data: dict, websocket: WebSocket):
        if not any(d['websocket'] == websocket for d in manager.authorized_connections):
            await websocket.send_json({'event': 'receive_message', 'status': 0, 'data': 'websocket not authorized'})
        else:
            receiver, sender, message = data['data']['to'], data['data']['from'], data['data']['message']
            data = insert_message(receiver, sender, message)
            for item in self.authorized_connections:
                if item.get('username') == receiver:
                    websocket_receiver = item.get('websocket')
                    break
            result = {'event': 'receive_message', 'data': data}
            await websocket_receiver.send_json(result)
            if websocket is not None:
                await websocket.send_json(result)

    async def authorize(self, data: dict, websocket: WebSocket):
        if not 'token' in data['data'].keys():
            await websocket.send_json({'event': 'auth', 'status': 0, 'data': 'missing key "token"'})
        else:
            user = await decode_token(data['data']['token'])
            if not user:
                await websocket.send_json({'event': 'auth', 'status': 0, 'data': 'invalid token'})
            else:
                manager.authorized_connections.append({'username': user, 'websocket': websocket})
                chats = await chat_users(user)
                await websocket.send_json({'event': 'auth', 'status': 1, 'data': chats})

    async def broadcast(self, message: str):
        pass


manager = ConnectionManager()
