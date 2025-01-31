import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from config import REDIS_PUBSUB_CHANNEL
import uvicorn


app = FastAPI()

origins = [
    "http://localhost:2105",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


redis = Redis(host="localhost", port=6379, decode_responses=True)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        pubsub = redis.pubsub()
        await pubsub.subscribe(REDIS_PUBSUB_CHANNEL)

        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message:
                await manager.send_message(message['data'], websocket)
            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        await pubsub.unsubscribe(REDIS_PUBSUB_CHANNEL)
        await pubsub.close()


@app.on_event("shutdown")
async def shutdown():
    await redis.close()


if __name__ == '__main__':
    uvicorn.run('appsocket:app', port=8001, reload=True)
