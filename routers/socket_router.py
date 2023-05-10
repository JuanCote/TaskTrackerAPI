from fastapi import APIRouter
from starlette.websockets import WebSocketDisconnect, WebSocket

from socket_manager import manager

router = APIRouter()

@router.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if 'event' in data.keys() and data['event'] == 'auth':
                await manager.authorize(data, websocket)
            elif 'event' in data.keys() and data['event'] == 'send_message':
                await manager.send_personal_message(data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)