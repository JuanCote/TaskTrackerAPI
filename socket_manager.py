import json
from datetime import datetime
from typing import List
import starlette.websockets
from fastapi import WebSocket

from db import insert_message
from model.message_model import Message
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
            date_now = int(datetime.now().timestamp() * 1000)
            message = Message(
                sender=data["data"]["from"],
                receiver=data["data"]["to"],
                message=data["data"]["message"],
                date=date_now,
                id=date_now
            )
            websocket_receiver = None
            for item in self.authorized_connections:
                if item.get("username") == message.receiver:
                    websocket_receiver = item.get("websocket")
                    break
            result = {"event": "receive_message", "data": dict(message)}
            await websocket.send_json(result)
            if websocket_receiver is not None:
                await websocket_receiver.send_json(result)

            message_to_notify = MessagePayload(
                username=message.receiver,
                message=message.receiver,
                notify={"title": message.sender, "body": message.message},
            )
            await notify_dao.send(message_to_notify)
            await insert_message(message)

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
                    for item in chats:
                        item["last_message"]["message"] = decrypt_message(
                            item["last_message"]["message"]
                        )
                        for message in item["messages"]:
                            message["message"] = decrypt_message(message["message"])
                    await websocket.send_json(
                        {"event": "auth", "status": 1, "data": chats}
                    )

    async def broadcast(self, message: str):
        pass


manager = ConnectionManager()
