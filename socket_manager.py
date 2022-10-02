from fastapi import WebSocket


active_connections = {}


class ConnectionManager:
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        active_connections.update({websocket: '2'})
        print(active_connections)

    def disconnect(self, websocket: WebSocket):
        active_connections.pop(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for key, connection in active_connections.items():
            await key.send_text(message)


manager = ConnectionManager()
