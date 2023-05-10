import json
from typing import List
import starlette.websockets
from fastapi import WebSocket

from db import insert_message
from utils.auth import decode_token
from utils.chat import chat_users, encrypt_message, decrypt_message
from notify import notify_dao, MessagePayload, UserDevicePayload


class ConnectionManager:
    def __init__(self):
        self.connections = []
        self.authorized_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        for item in self.authorized_connections:
            if item.get("websocket") == websocket:
                self.authorized_connections.remove(item)
        manager.connections.remove(websocket)

    async def send_personal_message(self, data: dict, websocket: WebSocket):
        if not any(d["websocket"] == websocket for d in manager.authorized_connections):
            await websocket.send_json(
                {
                    "event": "receive_message",
                    "status": 0,
                    "data": "websocket not authorized",
                }
            )
        else:
            receiver, sender, message = (
                data["data"]["to"],
                data["data"]["from"],
                data["data"]["message"],
            )
            message = encrypt_message(message)
            data = await insert_message(receiver, sender, message)
            message_to_notify = MessagePayload(
                username=receiver,
                message=receiver,
                notify={"title": sender, "body": message},
            )
            await notify_dao.send(message_to_notify)
            data["message"] = decrypt_message(data["message"])
            websocket_receiver = None
            for item in self.authorized_connections:
                if item.get("username") == receiver:
                    websocket_receiver = item.get("websocket")
                    break
            result = {"event": "receive_message", "data": data}
            await websocket.send_json(result)
            if websocket_receiver is not None:
                await websocket_receiver.send_json(result)

    async def authorize(self, data: dict, websocket: WebSocket):
        if not "token" in data["data"].keys():
            await websocket.send_json(
                {"event": "auth", "status": 0, "data": 'missing key "token"'}
            )
        else:
            user = await decode_token(data["data"]["token"])
            if not "token_device" in data["data"].keys():
                await websocket.send_json(
                    {"event": "auth", "status": 0, "data": 'missing key "token_device"'}
                )
            else:
                token_device = data["data"]["token_device"]
                user_device = UserDevicePayload(username=user, token=token_device)
                await notify_dao.save_device_token(user_device)
                if not user:
                    await websocket.send_json(
                        {"event": "auth", "status": 0, "data": "invalid token"}
                    )
                else:
                    manager.authorized_connections.append(
                        {"username": user, "websocket": websocket}
                    )
                    chats = await chat_users(user)
                    await websocket.send_json({"event": "auth", "status": 1, "data": chats})

    async def broadcast(self, message: str):
        pass


manager = ConnectionManager()
