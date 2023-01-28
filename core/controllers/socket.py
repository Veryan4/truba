from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from fastapi_utils.tasks import repeat_every
from typing import List

from services.story import story
from services.user import auth

router = APIRouter()


class ConnectionManager:

  def __init__(self):
    self.active_connections: List[WebSocket] = []

  async def connect(self, websocket: WebSocket):
    await websocket.accept()
    self.active_connections.append(websocket)

  def disconnect(self, websocket: WebSocket):
    self.active_connections.remove(websocket)

  async def send_personal_message(self, message: str, websocket: WebSocket):
    await websocket.send_text(message)

  async def broadcast(self, message: str):
    for connection in self.active_connections:
      await connection.send_text(message)

  @repeat_every(seconds=60 * 60)
  async def broadcastNews(self):
    news = jsonable_encoder(story.get_public_stories("en"))
    for connection in self.active_connections:
      try:
        await connection.send_text(news)
      except WebSocketDisconnect:
        self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,
                             user_id: str = Depends(auth.get_websocket_token)):
  await manager.connect(websocket)
  try:
    while True:
      data = await websocket.receive_text()
      await manager.send_personal_message(f"You wrote: {data}", websocket)
  except WebSocketDisconnect:
    manager.disconnect(websocket)
